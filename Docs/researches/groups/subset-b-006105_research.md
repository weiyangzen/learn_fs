# Research Report: subset-b-006105

Work item `subset-b-006105` covers RAID-6 SIMD backends and tests, generic pseudo-random/rate-limit/tree/reference/hash/bitmap helpers, and the Reed-Solomon library under `sources/distributed-fs/ceph-client/lib`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/recov_ssse3.c -->
## sources/distributed-fs/ceph-client/lib/raid6/recov_ssse3.c

Purpose: implements SSSE3-accelerated RAID-6 recovery callbacks for x86, specifically dual data loss (`data2`) and data-plus-P recovery (`datap`) in the `raid6_recov_calls` table `raid6_recov_ssse3`. It is selected only when XMM, SSE2, and SSSE3 CPU features are available.

Important APIs/functions: `raid6_has_ssse3()` probes CPU features through `boot_cpu_has()`. `raid6_2data_recov_ssse3()` recovers two failed data disks. `raid6_datap_recov_ssse3()` recovers one data disk plus P parity. Both use common RAID-6 GF tables (`raid6_vgfmul`, `raid6_gfexp`, `raid6_gfinv`, `raid6_gfexi`) and delegate initial delta syndrome calculation to `raid6_call.gen_syndrome()`.

Control flow: recovery first saves original P/Q and failed page pointers, substitutes failed data with `raid6_get_zero_page()`, redirects P/Q slots to failed buffers to compute delta P/Q, restores the pointer table, then applies GF multiplication using SSSE3 `pshufb` nibble lookup tables. The 64-bit build processes 32 bytes per loop with extra XMM registers; 32-bit processes 16 bytes.

State and persistence: no persistent state is kept, but the caller-provided `ptrs` array and failed buffers are temporarily mutated. SIMD state is bracketed by `kernel_fpu_begin()` and `kernel_fpu_end()`.

Dependencies/integration: depends on `linux/raid/pq.h`, `x86.h`, current global `raid6_call`, and aligned buffers compatible with `movdqa`. It plugs into RAID-6 recovery algorithm selection with priority 1 and name `ssse3x2` or `ssse3x1`.

Risks/test signals: risks include alignment assumptions, byte-count multiple assumptions inherited from RAID-6 page processing, pointer-table restoration bugs, and subtle GF table index errors. The userspace RAID-6 test harness in `lib/raid6/test/test.c` exercises all algorithm combinations, including this recovery backend on SSSE3-capable x86.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/recov_ssse3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/rvv.c -->
## sources/distributed-fs/ceph-client/lib/raid6/rvv.c

Purpose: provides RISC-V Vector Extension RAID-6 syndrome generation and incremental xor-syndrome implementations. The file deliberately errors if compiled with compiler vector support enabled, because it emits vector instructions explicitly in inline assembly under `.option arch,+v`.

Important APIs/functions: real worker functions are `raid6_rvv{1,2,4,8}_gen_syndrome_real()` and `raid6_rvv{1,2,4,8}_xor_syndrome_real()`. `RAID6_RVV_WRAPPER(1/2/4/8)` from `rvv.h` registers `raid6_calls` objects named `rvvx1`, `rvvx2`, `rvvx4`, and `rvvx8`.

Control flow: each function obtains runtime vector length with `vsetvli e8,m1`, uses that as `nsize`, and loops over `bytes` in unroll factors of 1, 2, 4, or 8 vector chunks. Syndrome generation initializes P and Q from the highest data disk and walks lower data disks, applying GF multiply-by-two using sign-mask, left-shift, and XOR with `0x1d`, then XORing input data into P/Q. Xor-syndrome first computes the affected range, advances Q over unaffected lower disks, then XORs computed P/Q deltas into existing parity.

State and persistence: no heap/global state is maintained. All state is vector registers and caller buffers; writes land in parity buffers or update existing parity in place. Kernel vector state is handled by wrapper functions, not the `_real()` bodies.

Dependencies/integration: depends on `rvv.h`, `linux/raid/pq.h`, RISC-V vector availability, and assembler support for vector mnemonics. Integrated through the RAID-6 algorithm list when `CONFIG_RISCV_ISA_V`/userspace RVV detection is active.

Risks/test signals: repeated inline assembly blocks make register/address mistakes easy, especially in the x8 path. The loops assume `bytes` is compatible with the chosen vector chunking; RAID page-sized callers normally satisfy this. Test coverage comes from `raid6/test` on RISC-V vector-capable systems and algorithm self-selection benchmarks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/rvv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/rvv.h -->
## sources/distributed-fs/ceph-client/lib/raid6/rvv.h

Purpose: defines the RISC-V vector support glue for RAID-6 vector backends, including capability detection and the macro that wraps raw inline-assembly implementations in kernel vector-state management.

Important APIs/types: `rvv_has_vector()` returns `has_vector()`. In kernel builds it includes `<asm/vector.h>`; in userspace tests it stubs `kernel_vector_begin/end()` and implements `has_vector()` with `getauxval(AT_HWCAP) & COMPAT_HWCAP_ISA_V`. `RAID6_RVV_WRAPPER(_n)` generates public `raid6_calls const raid6_rvvx##_n` structures plus wrapper functions for `gen_syndrome` and `xor_syndrome`.

Control flow: generated wrappers enter vector context with `kernel_vector_begin()`, call the corresponding `_real()` implementation in `rvv.c`, then call `kernel_vector_end()`. The `valid` callback is `rvv_has_vector`, and the cache-hint priority field is zero.

State and persistence: the header creates no persistent mutable state. Its main side effect is defining exported algorithm descriptors at compile time wherever the macro is used.

Dependencies/integration: ties `rvv.c` to the generic RAID-6 selection ABI in `linux/raid/pq.h`. It also bridges kernel and userspace test environments by choosing different vector capability definitions.

Risks/test signals: correctness depends on wrapper prototypes matching `_real()` function names and signatures exactly. Userspace detection depends on platform headers exposing compatible HWCAP definitions. RAID-6 userspace tests validate that the wrappers call into vector code only on supported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/rvv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/sse1.c -->
## sources/distributed-fs/ceph-client/lib/raid6/sse1.c

Purpose: implements legacy 32-bit x86 SSE1/MMXEXT RAID-6 syndrome generation. The implementation is actually MMX-based but uses SSE/MMXEXT features such as prefetch and non-temporal stores.

Important APIs/functions: `raid6_have_sse1_or_mmxext()` checks MMX plus XMM or MMXEXT. `raid6_sse11_gen_syndrome()` processes one 64-bit MMX lane per loop, while `raid6_sse12_gen_syndrome()` is unrolled by two. Public descriptors are `raid6_sse1x1` and `raid6_sse1x2`; neither provides `xor_syndrome`.

Control flow: each function identifies highest data disk `z0`, P at `z0+1`, Q at `z0+2`, enters FPU/MMX context, initializes the GF reduction constant `0x1d`, and walks each byte range across data disks. Q is multiplied by two in GF(2^8) using compare-mask, byte add, mask with `0x1d`, and XOR; P is a simple XOR accumulator. Results are written with `movntq` and finalized with `sfence`.

State and persistence: no persistent state. The routines mutate only parity buffers and use MMX registers under `kernel_fpu_begin/end()`.

Dependencies/integration: compiled only under `CONFIG_X86_32`; depends on `raid6_mmx_constants` from `mmx.c`, `x86.h`, and generic RAID-6 algorithm selection.

Risks/test signals: risks include MMX/FPU state handling, non-temporal store ordering, and maintaining support for old 32-bit feature combinations. Validation is available through `raid6/test`, which includes `sse1.o` for i386 builds and compares recovery across algorithms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/sse1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/sse2.c -->
## sources/distributed-fs/ceph-client/lib/raid6/sse2.c

Purpose: provides SSE2 RAID-6 syndrome generation and xor-syndrome update implementations for x86. It registers plain, unrolled-by-2, and on x86_64 unrolled-by-4 algorithms.

Important APIs/functions: `raid6_have_sse2()` checks MMX, FXSR, XMM, and XMM2. Public `raid6_calls` are `raid6_sse2x1`, `raid6_sse2x2`, and `raid6_sse2x4` on 64-bit. Each variant provides both `gen_syndrome` and `xor_syndrome`.

Control flow: syndrome generation loops by 16, 32, or 64 bytes. It initializes P/Q accumulators and applies GF multiply-by-two with `pcmpgtb`, `paddb`, mask `0x1d`, and XOR. Xor-syndrome uses the `start`/`stop` range to update parity for read-modify-write flows: it XORs affected data into P, computes Q contribution through the affected range, advances Q over unaffected lower disks, then XORs with existing Q. Non-temporal stores are used where appropriate, with comments avoiding them for small read/write areas in some variants.

State and persistence: no persistent state; parity buffers are overwritten or updated in place. SIMD state is protected with `kernel_fpu_begin/end()`.

Dependencies/integration: depends on `linux/raid/pq.h`, `x86.h`, inline SSE2 assembly, and the generic RAID-6 algorithm registry. `raid6_sse_constants.x1d` is the aligned GF reduction constant.

Risks/test signals: the code is register-heavy and architecture-specific, so risks include clobber omissions, alignment assumptions, and parity update divergence between unroll variants. `raid6/test/test.c` stresses generation, recovery, and xor-syndrome read-modify-write simulations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/sse2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/test/Makefile -->
## sources/distributed-fs/ceph-client/lib/raid6/test/Makefile

Purpose: builds a standalone userspace RAID-6 test library and `raid6test` executable from the kernel RAID-6 sources.

Important targets/variables: `OBJS` starts with generic integer, recovery, algorithm, and table objects, then conditionally adds architecture-specific objects. `ARCH` is derived from `uname -m`; x86 adds MMX/SSE/AVX objects, ARM/AArch64 adds NEON, PowerPC probes Altivec, LoongArch probes LSX/LASX, and RISC-V adds RVV objects. Targets include `raid6.a`, `raid6test`, generated `int*.c`, `neon*.c`, `altivec*.c`, `vpermxor*.c`, `tables.c`, `clean`, and `spotless`.

Control flow: pattern rules copy `.c` and `.uc` files from the parent RAID-6 directory into the test directory, use `unroll.awk` to expand unrolled templates, build a static archive, then link `raid6test` with the test program. `mktables` generates `tables.c`.

State and persistence: generated source/object/archive/binary files are local build artifacts and removed by `clean`.

Dependencies/integration: depends on GCC, `ld`, `awk`, `ar`, `ranlib`, kernel headers under `../../../include` and architecture include directories. It mirrors kernel config macros to userspace CFLAGS so algorithm files compile outside the kernel.

Risks/test signals: feature probes are shell/compiler dependent and architecture detection is simple. The Makefile itself is a test signal: successful build/run validates many RAID-6 algorithm implementations in userspace without booting a kernel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/test/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/test/test.c -->
## sources/distributed-fs/ceph-client/lib/raid6/test/test.c

Purpose: standalone RAID-6 recovery correctness test. It exercises all available recovery algorithms against all available syndrome algorithms for a 16-disk stripe, including P and Q.

Important APIs/functions: `makedata()` fills data buffers and pointer table entries. `disk_type()` labels D/P/Q slots. `test_disks()` injects two failed disks, calls `raid6_dual_recov()`, and compares recovered buffers. `main()` iterates `raid6_recov_algos` and `raid6_algos`, then invokes `raid6_select_algo()` at the end.

Control flow: initial data is randomized. For each valid recovery backend, the program installs its `data2` and `datap` functions. For each valid syndrome backend, it regenerates P/Q, then tests every pair of failed disks. If the syndrome backend supports `xor_syndrome`, the test also simulates read-modify-write ranges by applying xor-syndrome before and after replacing a data range, then repeats failure-pair validation.

State and persistence: static aligned arrays hold original data, current pointer table, and recovery scratch pages. No persistent external state exists; output is printed to stdout and the process return code is nonzero on errors.

Dependencies/integration: depends on the userspace RAID-6 archive built by the Makefile and generic interfaces in `linux/raid/pq.h`.

Risks/test signals: the D+Q failure case is skipped because it is equivalent to RAID-5-style XOR plus Q recomputation and is not implemented as a direct scenario. Strong signal comes from exhaustive disk-pair checks across algorithm combinations and xor-syndrome RMW paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/test/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/unroll.awk -->
## sources/distributed-fs/ceph-client/lib/raid6/unroll.awk

Purpose: small source-generation filter used by RAID-6 tests and template-based SIMD/integer implementations to expand unrolled code templates.

Important behavior: it requires `-vN=n`, converts `N` to numeric `n`, and for each input line repeats lines containing `$$` exactly `n` times. In each repeated line it replaces `$$` with the current repeat index, `$#` with the unroll count, and `$*` with a literal dollar sign.

Control flow: the script initializes `n` in `BEGIN`, sets `rep` per line based on whether `$$` is present, loops `i` from 0 to `rep-1`, applies `gsub()` transformations, and prints the resulting line.

State and persistence: no persistent state beyond current input line and loop counters. Output is generated source on stdout.

Dependencies/integration: called from `raid6/test/Makefile` to expand `int.uc`, `neon.uc`, `altivec.uc`, and `vpermxor.uc` into unroll-specific `.c` files.

Risks/test signals: the filter is intentionally simple; malformed templates or missing `-vN` silently produce wrong or empty-style expansion. Build success and later RAID-6 test correctness are the practical signals that generated code is coherent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/unroll.awk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/x86.h -->
## sources/distributed-fs/ceph-client/lib/raid6/x86.h

Purpose: shared x86/x86_64 RAID-6 helper header. It abstracts FPU state handling and CPU feature probing for kernel and userspace test builds.

Important APIs/types: kernel builds include `<asm/fpu/api.h>` for `kernel_fpu_begin/end()`. Userspace builds define no-op `kernel_fpu_begin/end()`, `__aligned(x)`, x86 feature bit constants, and a `boot_cpu_has(int flag)` helper implemented with `cpuid`.

Control flow: `boot_cpu_has()` chooses CPUID leaf 7, extended leaf `0x80000001`, or leaf 1 based on encoded feature bits, executes `cpuid`, then extracts the target bit from EBX, ECX, or EDX.

State and persistence: no mutable persistent state. It only exposes inline helpers and macros.

Dependencies/integration: guarded to x86 and non-UML builds. Used by x86 RAID-6 algorithm files such as `sse1.c`, `sse2.c`, and `recov_ssse3.c`, enabling the same source to compile in kernel and userspace test contexts.

Risks/test signals: userspace `boot_cpu_has()` is only intended to be good enough for modern CPU testing; feature encoding must match all callers. If feature detection is wrong, algorithm selection may execute unsupported instructions. The standalone RAID-6 test build exercises this path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/x86.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/random32.c -->
## sources/distributed-fs/ceph-client/lib/random32.c

Purpose: implements the kernel pseudo-random `prandom` Tausworthe generator for non-cryptographic uses, plus optional self-tests under `CONFIG_RANDOM32_SELFTEST`.

Important APIs/functions: `prandom_u32_state()` advances a caller-provided `struct rnd_state` using four LFSR/Tausworthe components and returns their XOR. `prandom_bytes_state()` fills byte buffers from repeated 32-bit outputs. `prandom_seed_full_state()` seeds per-CPU states from `get_random_bytes()` and warms each state. Self-test helpers include `prandom_state_selftest_seed()` and `prandom_state_selftest()`.

Control flow: state transitions use the `TAUSWORTHE` macro with fixed masks/shifts and seed constraints documented in comments. Byte generation writes full unaligned 32-bit words, then any remaining bytes from a final value. Full-state seeding iterates possible CPUs, derives four constrained seeds with `__seed()`, and calls `prandom_warmup()` ten times.

State and persistence: state lives in caller-supplied `struct rnd_state` or per-CPU storage passed to seeding. The file itself keeps only static test vectors when self-test is enabled.

Dependencies/integration: exports `prandom_u32_state`, `prandom_bytes_state`, and `prandom_seed_full_state`. Depends on random seeding, percpu iteration, jiffies/scheduler infrastructure for tests, and unaligned stores.

Risks/test signals: not cryptographic; callers needing entropy must use `get_random_*`. Bad seeding can violate generator constraints. Built-in self-tests compare boundary and GSL-derived vectors and report pass/fail at init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/random32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ratelimit.c -->
## sources/distributed-fs/ceph-client/lib/ratelimit.c

Purpose: implements the shared `___ratelimit()` helper for limiting repeated callbacks or log messages using a caller-owned `struct ratelimit_state`.

Important API/function: `___ratelimit(struct ratelimit_state *rs, const char *func)` returns 1 when the caller should proceed and 0 when the callback should be suppressed. It is exported as a kernel symbol.

Control flow: the function reads interval and burst with `READ_ONCE()` so concurrent sysctl/proc updates do not create unsafe compiler assumptions. Zero interval disables limiting; nonpositive burst generally suppresses. The hot path tries `raw_spin_trylock_irqsave()`. If contended, it uses atomic `rs_n_left` as an approximate fast path. With the lock held, it initializes the window if needed, resets counts when `begin + interval` has passed, prints suppressed-count messages unless release-reporting is requested, then decrements the remaining burst.

State and persistence: mutable state is entirely in `ratelimit_state`: interval, burst, flags, window start, atomic remaining allowance, and missed count. Misses are incremented when suppressed.

Dependencies/integration: depends on jiffies time helpers, raw spinlocks, atomics, warning infrastructure, and deferred printk.

Risks/test signals: the contended lockless fallback can allow false positives near interval boundaries by design. Negative uninitialized values warn. Test signals are mostly indirect through printk/net ratelimit users and lock/concurrency behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ratelimit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/rbtree.c -->
## sources/distributed-fs/ceph-client/lib/rbtree.c

Purpose: core Linux red-black tree implementation, including non-augmented insert/erase, augmented callbacks, replacement helpers, inorder traversal, and postorder traversal.

Important APIs/functions: public exports include `rb_insert_color()`, `rb_erase()`, `__rb_insert_augmented()`, `__rb_erase_color()`, `rb_next()`, `rb_prev()`, `rb_replace_node()`, `rb_replace_node_rcu()`, `rb_next_postorder()`, and `rb_first_postorder()`. `rb_erase_linked()` additionally maintains a linked cached-leftmost wrapper.

Control flow: `__rb_insert()` repairs red-black properties after `rb_link_node()` using standard uncle-red color flips and rotations. `____rb_erase_color()` rebalances after deletion through sibling cases, handling symmetric left/right forms. Rotation helpers use `WRITE_ONCE()` for child-pointer changes to support lockless readers that may miss nodes but must not loop or observe invalid objects.

State and persistence: tree shape and node color/parent metadata are stored in caller-owned `rb_node` structures. Augmented callbacks allow users to maintain derived per-subtree state through propagation, copy, and rotate operations.

Dependencies/integration: depends on `linux/rbtree_augmented.h` and export macros. Many kernel subsystems embed `rb_node` in their own objects and provide search/link logic.

Risks/test signals: balancing code is case-heavy and pointer-order sensitive. RCU replacement requires publishing parent-child links last. `rbtree_test.c` provides invariant checks, postorder traversal checks, cached-tree comparisons, augmented propagation checks, and performance timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/rbtree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/rbtree_test.c -->
## sources/distributed-fs/ceph-client/lib/rbtree_test.c

Purpose: kernel module self-test and microbenchmark for regular, cached, and augmented rbtrees.

Important APIs/types: module parameters `nnodes`, `perf_loops`, `check_loops`, and `seed` control size and randomness. `struct test_node` embeds `struct rb_node` plus key/value/augmented fields. Functions cover insertion/erasure variants, invariant checking, postorder checking, augmented callback validation, and timing.

Control flow: module init allocates test nodes, seeds `rnd`, runs `basic_check()` and `augmented_check()`, frees nodes, then returns `-EAGAIN` so the test module unloads immediately. Basic testing measures insert/delete, cached insert/delete, inorder traversal, first-node fetch, then repeatedly inserts and erases while checking invariants at each step. Augmented testing repeats with `RB_DECLARE_CALLBACKS_MAX` and verifies each node's augmented maximum equals its subtree maximum.

State and persistence: static globals hold the cached root, node array, and pseudo-random state during the test only. No state persists after module unload.

Dependencies/integration: depends on module infrastructure, `rbtree_augmented.h`, `prandom`, slab allocation, and cycle counters.

Risks/test signals: duplicate keys are allowed on the right side, so checks validate nondecreasing order rather than strict uniqueness. The test warns with `WARN_ON_ONCE()` on invariant violations and logs timing, making it a direct signal for rbtree regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/rbtree_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/rcuref.c -->
## sources/distributed-fs/ceph-client/lib/rcuref.c

Purpose: implements slow paths for `rcuref`, a scalable reference count for RCU-managed objects. The design optimizes fast get/put paths with unconditional atomic add/subtract and uses value zones to detect valid, saturated, released, dead, and no-reference states.

Important APIs/functions: `rcuref_get_slowpath()` handles increments that land outside the valid reference zone. `rcuref_put_slowpath()` handles decrements that may drop the last reference, encounter imbalanced puts, or operate on saturated counts. Both are GPL exports.

Control flow: get slow path reads the counter; values in or beyond the released/dead zone are reset to `RCUREF_DEAD` and fail. Saturated values warn once, reset to `RCUREF_SATURATED`, and succeed so the object leaks rather than wraps. Put slow path marks `RCUREF_NOREF` as `RCUREF_DEAD` with release cmpxchg and acquire-after-control dependency; races simply return false. Imbalanced dead-zone puts warn and restore dead state; saturated puts restore saturation.

State and persistence: state is the atomic integer inside caller-owned `rcuref_t`. No global state is held.

Dependencies/integration: depends on `linux/rcuref.h`, atomics, warning macros, and RCU lifetime discipline. Callers must prevent grace-period completion across put slow paths, as described in the file comments.

Risks/test signals: misuse on non-RCU-managed objects can produce use-after-free. Saturation intentionally leaks. The code relies on large zones to absorb races and on exact memory-ordering contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/rcuref.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/reed_solomon/Makefile -->
## sources/distributed-fs/ceph-client/lib/reed_solomon/Makefile

Purpose: kernel build fragment for the Reed-Solomon library and its optional test module.

Important behavior: `obj-$(CONFIG_REED_SOLOMON) += reed_solomon.o` builds the library when configured. `obj-$(CONFIG_REED_SOLOMON_TEST) += test_rslib.o` builds the self-test module independently behind its test config.

Control flow: there is no procedural build logic beyond Kbuild object selection.

State and persistence: no runtime state. Build outputs are controlled by Kbuild.

Dependencies/integration: consumed by the kernel build system under the `lib/reed_solomon` directory. The main object includes the generic encoder/decoder bodies conditionally based on encoder/decoder width configs in `reed_solomon.c`.

Risks/test signals: configuration omissions can build the library without a desired width-specific encode/decode wrapper. Enabling `CONFIG_REED_SOLOMON_TEST` provides a direct randomized correctness signal through `test_rslib.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/reed_solomon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/reed_solomon/decode_rs.c -->
## sources/distributed-fs/ceph-client/lib/reed_solomon/decode_rs.c

Purpose: generic Reed-Solomon decoder body included by 8-bit and 16-bit wrappers in `reed_solomon.c`.

Important functions/data: it operates on `struct rs_control`, `struct rs_codec`, caller data/parity/syndrome/erasure arrays, and decoder scratch buffers embedded in `rs_control` (`lambda`, `syn`, `b`, `t`, `omega`, `root`, `reg`, `loc`).

Control flow: it validates padding, uses caller-provided syndromes if present, otherwise computes syndromes over data and parity, converts to index form, and returns early for zero syndrome. It initializes the erasure locator, runs Berlekamp-Massey to compute the error+erasure locator polynomial, performs Chien search for roots/locations, computes the evaluator polynomial omega, calculates correction values, verifies the correction syndrome against the received syndrome, then either fills `corr`/`eras_pos` or applies corrections in place to data/parity.

State and persistence: decoder scratch buffers are stored in `rs_control`, so callers must serialize decode calls per control object. The input codeword may be modified in place when no correction buffer is provided.

Dependencies/integration: included inside `decode_rs8()` and `decode_rs16()` wrappers. Uses GF lookup tables and `rs_modnn()`.

Risks/test signals: invalid erasure positions, excessive errors, deg/root mismatches, and syndrome verification failures return `-EBADMSG`. `test_rslib.c` tests correction-buffer, caller-syndrome, in-place, erasure, padding, and beyond-capacity behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/reed_solomon/decode_rs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/reed_solomon/encode_rs.c -->
## sources/distributed-fs/ceph-client/lib/reed_solomon/encode_rs.c

Purpose: generic Reed-Solomon encoder body included by the 8-bit and 16-bit encoder wrappers in `reed_solomon.c`.

Important behavior: it uses `struct rs_control` and its shared codec tables (`alpha_to`, `index_of`, `genpoly`) to update a caller-provided parity array. The body is type-generic because it is included inside wrappers whose `data` pointer type differs.

Control flow: the function validates `len` by computing `pad = nn - nroots - len`, rejecting out-of-range values with `-ERANGE`. For each input symbol, it computes feedback from the masked/inverted data byte and current first parity element. If feedback is nonzero, it XORs generator-polynomial contributions into parity positions. It then shifts the parity vector with `memmove()` and writes the final feedback contribution or zero.

State and persistence: the caller owns and initializes `par`; the encoder mutates it cumulatively. No file-local persistent state exists.

Dependencies/integration: included in `encode_rs8()` and `encode_rs16()`, which export the public kernel APIs. Depends on precomputed GF tables and `rs_modnn()`.

Risks/test signals: parity must be initialized by the caller, usually to zero. Incorrect `invmsk` or length/padding produces wrong codewords. `test_rslib.c` validates generated parity by round-trip decode and by re-encoding returned words in beyond-capacity tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/reed_solomon/encode_rs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/reed_solomon/reed_solomon.c -->
## sources/distributed-fs/ceph-client/lib/reed_solomon/reed_solomon.c

Purpose: runtime-configurable Reed-Solomon encoder/decoder library. It manages shared codec tables and per-user control structures, then exposes width-specific encode/decode wrappers depending on config.

Important APIs/types: `struct rs_codec` holds GF parameters, lookup tables, generator polynomial, and user count. `struct rs_control` points to a codec and contains decode scratch buffers. Public APIs include `init_rs_gfp()`, `init_rs_non_canonical()`, `free_rs()`, and conditional `encode_rs8/16()` and `decode_rs8/16()`.

Control flow: `codec_init()` allocates tables, builds `alpha_to`/`index_of`, verifies the primitive polynomial/function, computes `iprim`, and builds generator polynomial in index form. `init_rs_internal()` validates parameters, allocates the control plus decode buffers, reuses a matching codec from `codec_list` under `rslistlock`, or creates a new one. `free_rs()` decrements codec users and frees tables when the last control releases it.

State and persistence: global `codec_list` persists shared codecs under mutex protection. Each control owns decode buffers, so decode calls on a single control must be serialized.

Dependencies/integration: depends on `linux/rslib.h`, slab allocation, mutexes, and included generic encoder/decoder bodies. Intended for drivers/subsystems needing configurable RS codes.

Risks/test signals: parameter validation prevents impossible fields, but primitive polynomial correctness is only detected during table generation. Allocation can be expensive and should happen at init time. `test_rslib.c` provides randomized validation over many symbol sizes and padding levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/reed_solomon/reed_solomon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/reed_solomon/test_rslib.c -->
## sources/distributed-fs/ceph-client/lib/reed_solomon/test_rslib.c

Purpose: kernel module self-test for the generic Reed-Solomon library across multiple field sizes, generator polynomials, roots, padding amounts, correction modes, and beyond-capacity cases.

Important APIs/types: module parameters `v`, `ewsc`, and `bc` control verbosity, erasures-without-corruption, and beyond-capacity testing. `Tab[]` lists code configurations. `struct wspace` holds sent/received codewords, syndrome, correction buffer, and error location arrays.

Control flow: `run_exercise()` initializes an RS control, allocates workspace, and tests several padding levels. `get_rcw_we()` creates a random codeword, encodes parity, injects random errors and erasures, and records true locations. `exercise_rs()` tests correction-buffer, caller-syndrome, and in-place decode paths up to correction capacity. `exercise_rs_bc()` injects beyond-capacity patterns and checks that any successful decode still yields a valid codeword.

State and persistence: workspace and RS controls are allocated per test configuration and freed. The module returns `-EAGAIN` after running so it unloads directly.

Dependencies/integration: depends on `rslib`, random numbers, module params, and slab allocation. It exercises `encode_rs16()` and `decode_rs16()`.

Risks/test signals: randomized tests can be expensive for small fields with high trial counts. It reports wrong data, wrong return values, wrong error positions, and silent beyond-capacity failures, then logs overall pass/fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/reed_solomon/test_rslib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ref_tracker.c -->
## sources/distributed-fs/ceph-client/lib/ref_tracker.c

Purpose: debug helper for tracking reference allocations/frees, aggregating allocation stack traces, detecting leaks/double frees, and optionally exposing live reference users through debugfs.

Important APIs/types: private `struct ref_tracker` stores list node, dead flag, allocation stack handle, and free stack handle. Public APIs include `ref_tracker_alloc()`, `ref_tracker_free()`, `ref_tracker_dir_print[_locked]()`, `ref_tracker_dir_snprint()`, `ref_tracker_dir_exit()`, and debugfs helpers when enabled.

Control flow: allocation records a stack trace in stackdepot, allocates a tracker, and links it into `dir->list`; NULL tracker pointers increment `no_tracker`, and allocation failures increment `untracked`. Freeing records a free stack, detects double free via `tracker->dead`, moves the tracker into a quarantine list, and frees the oldest quarantined tracker when the quota is exhausted. Directory exit marks debugfs entries dead, frees quarantine, reports remaining live references, and warns on leaks/counter imbalance.

State and persistence: state lives in caller-owned `ref_tracker_dir` lists, spinlock, counters, quarantine availability, and debugfs xarrays. Stack traces are persisted in stackdepot.

Dependencies/integration: uses list sorting/stat aggregation, stacktrace/stackdepot, seq_file, slab, refcount, xarray, workqueue, and debugfs.

Risks/test signals: debugfs teardown is asynchronous to avoid blocking in arbitrary free contexts. Incorrect tracker ownership can cause false double-free/leak reports. Warnings and stack dumps are the main diagnostic signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ref_tracker.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/refcount.c -->
## sources/distributed-fs/ceph-client/lib/refcount.c

Purpose: out-of-line helpers for hardened `refcount_t` operations that cannot or should not be implemented only as inline atomic wrappers.

Important APIs/functions: `refcount_warn_saturate()` sets the counter to `REFCOUNT_SATURATED` and emits a warning based on saturation type. `refcount_dec_if_one()` performs a release-ordered 1-to-0 transition. `refcount_dec_not_one()` decrements unless the value is 1. `refcount_dec_and_mutex_lock()`, `refcount_dec_and_lock()`, and `refcount_dec_and_lock_irqsave()` acquire the supplied lock only when successfully dropping the last reference.

Control flow: decrement-and-lock helpers first try to decrement non-final references without taking the external lock. If the count is exactly one, they acquire the lock, call `refcount_dec_and_test()`, and release the lock if another reference appeared. Underflow and saturated states warn or behave as leak-preserving safety cases.

State and persistence: state is the caller-owned `refcount_t`; no globals. Saturation deliberately persists to prevent wraparound and likely leaks the object.

Dependencies/integration: depends on mutexes, spinlocks, atomics, and warning infrastructure. Used by kernel objects that need refcount hardening and final-release locking.

Risks/test signals: misuse after count zero reports use-after-free style warnings. Saturation warnings indicate a serious lifetime bug. Memory ordering is release plus control dependency for destruction sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/refcount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/rhashtable.c -->
## sources/distributed-fs/ceph-client/lib/rhashtable.c

Purpose: generic resizable, concurrent hash table implementation supporting RCU lookups, per-bucket locking, async resizing, nested bucket allocation fallback, rhlist duplicate-key mode, and walkers.

Important APIs/functions: public exports include `rhashtable_init_noprof()`, `rhltable_init_noprof()`, `rhashtable_insert_slow()`, walker APIs (`rhashtable_walk_enter/exit/start_check/next/peek/stop`), `rhashtable_free_and_destroy()`, `rhashtable_destroy()`, and nested bucket helpers. Internal resize functions include `rhashtable_rehash_alloc()`, `rhashtable_rehash_attach()`, `rhashtable_rehash_table()`, and deferred workers.

Control flow: initialization validates hash/key callbacks, chooses size, allocates a bucket table, seeds hash salt, and initializes work items. Insert scans the current or future table, locks a bucket, checks duplicates/elasticity, inserts with RCU pointer updates, increments element count, and schedules rehash when load grows. Resize attaches a future table, migrates chains bucket by bucket, publishes the new table with RCU, tracks walkers, and frees old tables after grace period. Iterators preserve table/slot/skip state and report `-EAGAIN` across resizes.

State and persistence: `struct rhashtable` owns table pointers, params, counters, lock/mutex, work/irq_work, and optional rhlist mode. Bucket tables hold random salts, bucket heads, future table links, walkers, and optional nested tables.

Dependencies/integration: uses RCU, atomics, jhash/random, workqueues, irq_work, vmalloc/slab, lockdep, and nulls lists.

Risks/test signals: resize concurrency, nested allocation, walker relinking, and teardown ordering are high-risk. Comments document lock-order and teardown fixes. Users usually validate through subsystem tests exercising insert/delete/lookup under RCU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/rhashtable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/sbitmap.c -->
## sources/distributed-fs/ceph-client/lib/sbitmap.c

Purpose: scalable bitmap and waitqueue-backed bitmap queue implementation used for efficient tag/resource allocation, especially where per-CPU hints and batched wakeups reduce contention.

Important APIs/functions: bitmap APIs include `sbitmap_init_node()`, `sbitmap_resize()`, `sbitmap_get()`, `sbitmap_any_bit_set()`, `sbitmap_weight()`, and seq display helpers. Queue APIs include `sbitmap_queue_init_node()`, `sbitmap_queue_resize()`, `__sbitmap_queue_get()`, `__sbitmap_queue_get_batch()`, `sbitmap_queue_get_shallow()`, `sbitmap_queue_clear[_batch]()`, wake helpers, and waitqueue add/prepare/finish helpers.

Control flow: initialization computes bits-per-word, allocates words and optional per-CPU hints, and initializes swap locks. Allocation reads a CPU hint, searches for a zero bit in the target word, moves deferred clears into the visible word if needed, and updates the hint. Shallow allocation scales per-word depth to enforce class limits. Queue clear operations publish deferred or direct clears with memory barriers, update CPU hints, and wake waiters in batches across rotating waitqueue buckets.

State and persistence: `struct sbitmap` owns depth, shift, map words, deferred-clear masks, locks, round-robin flag, and per-CPU hints. `struct sbitmap_queue` adds wait states, wake counters, wake batch, active waiter count, completion counters, and shallow-depth limits.

Dependencies/integration: depends on random hints, percpu allocation, atomics/bitops, raw spinlocks, waitqueues, memory barriers, and seq_file.

Risks/test signals: memory ordering around clear/reallocation and waitqueue wakeups is subtle. Batch allocation has assumptions about non-round-robin maps. Seq output (`sbitmap_show`, `sbitmap_queue_show`, bitmap dump) provides operational diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/sbitmap.c -->
