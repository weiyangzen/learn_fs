# subset-b-000852 Research

Grouped research for SPARC library, math emulation, and memory-management sources under `sources/distributed-fs/ceph-client/arch/sparc`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/memscan_64.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/memscan_64.S

Purpose: SPARC64 assembly implementation of `memscan`, with a zero-byte fast path exported as `__memscan_zero` and a byte-by-byte generic path exported as `__memscan_generic`. It is part of the kernel string/memory helper layer and is tuned for 64-bit SPARC load semantics.

Important APIs/functions: `__memscan_zero(buf, size)` scans for the first zero byte and returns the matching address or the end address when no zero is found. `memscan`/`__memscan_generic(addr, c, size)` scans for an arbitrary byte. `EXPORT_SYMBOL(__memscan_zero)` and `EXPORT_SYMBOL(__memscan_generic)` expose the optimized variants to other kernel code/modules.

Control flow: the zero scanner handles non-positive sizes, peels initial unaligned bytes, then uses 8-byte `ldxa [%o0] ASI_PL` loads. It builds `HI_MAGIC`/`LO_MAGIC` masks and detects zero bytes with the classic subtract/xor/high-bit test before falling into byte localization. The generic scanner computes an end pointer, walks from negative offset toward zero, compares loaded bytes against `%o1`, and returns either the found pointer or original address plus size.

State and persistence: no persistent state. It mutates only SPARC output/global registers and reads caller memory. The zero path depends on ASI primary little details for load behavior but does not write memory.

Dependencies/integration: includes `linux/export.h`; uses SPARC64 ASI constant `ASI_PL`. Linked into `arch/sparc/lib` as the architecture implementation behind common kernel memscan semantics. Callers depend on exact libc-style return behavior when no byte is found.

Risks: off-by-one errors around the unaligned peel and final `add %o0, %o1, %o0` end comparison would corrupt returned pointers. The 8-byte path can over-read if size handling regresses; the current logic decrements size before advancing and bounds the final candidate. ASI load ordering and endianness-sensitive byte extraction are hardware-specific.

Test signals: architecture string tests for `memscan` over zero length, one byte, unaligned starts, found-at-boundary, not-found, and all byte values. KUnit/lib string tests on SPARC64 or qemu/sparc64 should compare against generic C behavior. Fault-injection around unmapped tail pages would be valuable because optimized scanners are prone to speculative over-read mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/memscan_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/memset.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/memset.S

Purpose: optimized SPARC assembly implementation of `memset`, `__bzero`, and clear-user-style zeroing helpers. It supports normal kernel memset return semantics and exception-table fixups for user-memory clearing.

Important APIs/functions: `memset(dst, c, len)` returns the original destination. `__bzero(dst, len)` zeros a region and returns zero on success or remaining bytes on clear-user exceptions. Labels `__bzero_begin` and `__bzero_end` delimit the region for exception/fixup users. Macros `EX`, `STORE`, `STORE_LAST`, `ZERO_BIG_BLOCK`, and `ZERO_LAST_BLOCKS` generate fault-aware byte/word/doubleword stores and exception table records.

Control flow: `memset` saves original `%o0`, replicates the low byte of `%o1` into a 32-bit pattern, then shares the bzero body with `%g4` set so it returns the original pointer. The common body aligns to 4 and then 8 bytes, stores repeated 128-byte chunks via unrolled 64-byte blocks, handles remaining 8-byte groups through a computed jump into `ZERO_LAST_BLOCKS`, then finishes 4/2/1-byte tails. The `.fixup` path computes how many bytes remain after a fault and returns through label `30`.

State and persistence: writes caller-specified memory only. It writes exception table entries and fixup code at assembly time, not runtime. No global runtime state.

Dependencies/integration: includes `linux/export.h` and `asm/ptrace.h`; emits `__ex_table` entries used by the kernel exception-table search. `EXPORT_SYMBOL(__bzero)` and `EXPORT_SYMBOL(memset)` make this the SPARC implementation used broadly by core kernel and modules.

Risks: the generated fixup math is tightly coupled to the store macros; changing macro order or offsets can make clear-user remaining-byte results wrong. Alignment arithmetic must preserve `memset`'s original-pointer return while `__bzero` returns zero. Large unrolled stores increase the blast radius of a single exception-table bug.

Test signals: boot-time/string selftests for memset patterns, zero lengths, unaligned destinations, and every tail size 0-127. Usercopy/clear_user tests should verify exception fixup return counts across faults in byte, word, doubleword, and block stores. Disassembly review should confirm `.fixup` and `__ex_table` entries align with store sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/memset.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/muldi3.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/muldi3.S

Purpose: GCC runtime helper `__muldi3` for 64-bit integer multiplication on 32-bit SPARC-style register pairs. It is based on GNU CC support code and exported for kernel/module users that need compiler-emitted long-long multiplication support.

Important APIs/functions: `__muldi3` accepts high/low halves in the SPARC calling convention and returns a 64-bit product in `%i0/%i1` after `restore`. `EXPORT_SYMBOL(__muldi3)` exposes it.

Control flow: the routine uses `save`, writes one operand low word into `%y`, performs a 32-step `mulscc` multiply sequence to compute the low-half partial product, reads `%y`, computes cross terms with `umul`, adds them into the high result, then returns high/low halves.

State and persistence: no persistent state. It uses `%y`, local registers, integer condition codes, and the stack frame created by `save`.

Dependencies/integration: includes `linux/export.h`. Integrated as a libgcc replacement for builds where the compiler emits `__muldi3` instead of inline multiply sequences.

Risks: register-pair ABI must match compiler expectations exactly. The `%y` write/read delay and fixed `mulscc` sequence are SPARC-specific; scheduling or assembler rewrites can break arithmetic. Signedness assumptions matter because the helper name is used for two's-complement low 64-bit products.

Test signals: compiler runtime arithmetic tests for positive/negative operands, zero, all-ones, carry-heavy cross products, and randomized 64-bit multiplication compared with a reference. Build logs should show no unresolved libgcc multiply helper references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/muldi3.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/multi3.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/multi3.S

Purpose: SPARC64 assembly implementation of GCC runtime helper `__multi3`, producing a 128-bit product from two 64-bit operands. It supports compiler-generated `__int128` multiplication in kernel code.

Important APIs/functions: `ENTRY(__multi3)` with operands in `%o0/%o1` and `%o2/%o3`, returns high/low result through `%o0/%o1`. `ENDPROC(__multi3)` and `EXPORT_SYMBOL(__multi3)` integrate it with kernel symbol/linkage conventions.

Control flow: it decomposes operands into 32-bit halves, uses `mulx` for partial products, manages carries with `addcc`, `srlx`, and conditional moves, then adds cross terms and high-half products before returning in the delay slot.

State and persistence: no memory or global state. It is a leaf routine and only consumes caller registers.

Dependencies/integration: includes `linux/export.h` and `linux/linkage.h`. Used by compiler output and potentially modules requiring 128-bit arithmetic support on SPARC64.

Risks: carry propagation is dense and branchless; a single condition-code misuse changes high-word results only on boundary inputs. ABI correctness is critical because helper calls are compiler-generated and not manually audited at call sites.

Test signals: randomized 64x64-to-128 multiplication tests, edge cases such as `0xffffffffffffffff * 0xffffffffffffffff`, powers of two, and high-only/low-only operands. Cross-check with compiler-rt/libgcc reference on SPARC64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/multi3.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/strlen.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/strlen.S

Purpose: optimized SPARC assembly implementation of `strlen`, adapted from GNU libc and exported as the kernel string helper.

Important APIs/functions: `ENTRY(strlen)` returns the number of bytes before the first NUL. It uses magic constants `LO_MAGIC` and `HI_MAGIC`, linkage macros, and `EXPORT_SYMBOL(strlen)`.

Control flow: the routine saves the starting pointer, peels up to three bytes to align on a 4-byte boundary, then scans words with the subtract/high-bit zero-detection trick. On possible zero, it checks each byte in word order and subtracts the original pointer. Labels `11`, `12`, and `13` return immediate lengths for early unaligned hits.

State and persistence: no persistent state and no writes. It reads memory until a NUL terminator and uses only registers.

Dependencies/integration: includes `linux/export.h`, `linux/linkage.h`, and `asm/asm.h` for branch macros that abstract 32/64-bit conditional forms. Used throughout kernel and module code wherever `strlen` is referenced.

Risks: optimized word scanning assumes accessible bytes up to the terminator; like most strlen implementations, invalid unterminated strings can fault. Endianness and byte-order checks must match SPARC layout. Alignment peel labels are easy sources of off-by-one return errors.

Test signals: string tests for every alignment modulo 4, empty strings, terminator in each byte lane, long strings crossing cache lines/pages, and comparison against generic C `strlen`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/strlen.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/strncmp_32.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/strncmp_32.S

Purpose: hand-optimized SPARC32 assembly implementation of `strncmp`, derived from GCC output of the generic GNU libc routine.

Important APIs/functions: `ENTRY(strncmp)` compares `%o0` and `%o1` for at most `%o2` bytes and returns signed byte difference or zero. `EXPORT_SYMBOL(strncmp)` exports the implementation.

Control flow: for lengths greater than three, it processes four byte comparisons per loop iteration using repeated inline blocks, stops on NUL or mismatch, and then handles the final remainder bytes. For short counts, it jumps directly to the tail loop. Return paths subtract unsigned byte values to preserve C `strncmp` ordering.

State and persistence: no persistent state and no writes. It advances local copies of string pointers and count registers.

Dependencies/integration: includes `linux/export.h` and `linux/linkage.h`. Provides the architecture symbol used by common kernel string users on 32-bit SPARC.

Risks: length handling is subtle: the code preloads bytes and decrements block/remainder counters while also stopping on NUL. The final return path uses `%o3`/`%g2`, so short-count and zero-count paths must avoid stale values. It does not use exception fixups; invalid user pointers are not supported.

Test signals: compare against generic `strncmp` for counts 0-8, long equal prefixes, NUL before `n`, mismatch before/at/after 4-byte boundaries, signed high-bit byte values, and all source alignments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/strncmp_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/strncmp_64.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/strncmp_64.S

Purpose: compact SPARC64 assembly implementation of `strncmp`.

Important APIs/functions: `ENTRY(strncmp)` returns zero for non-positive length, otherwise compares bytes from `%o0` and `%o1`. It uses `lduba [%o0] (ASI_PNF)` for the initial source load and exports `strncmp`.

Control flow: after a `brlez` zero-length guard, it loads one byte, increments both pointers, exits on NUL or mismatch, decrements the count, and loops while bytes remain. The return value is `%o3 - %o4`; zero-count returns clear `%o0`.

State and persistence: no persistent state and no writes. It reads memory only.

Dependencies/integration: includes `linux/export.h`, `linux/linkage.h`, and `asm/asi.h`. It plugs into kernel string calls for SPARC64.

Risks: the first load uses a non-faulting primary ASI while later loads use regular `ldub`; this asymmetry should match intended kernel address behavior. Count is decremented after comparison, so boundary tests are important. It is byte-wise and simple but not exception-table protected.

Test signals: generic string selftests for `n <= 0`, exact-length equality, mismatch at last byte, NUL before count, high-bit byte ordering, and invalid/unmapped first pointer behavior if non-faulting ASI semantics are relied on.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/strncmp_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/udivdi3.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/udivdi3.S

Purpose: GNU CC runtime helper `__udivdi3` implementing unsigned 64-bit division on SPARC using 32-bit operations and hand-inlined long division primitives.

Important APIs/functions: `__udivdi3` accepts numerator/divisor halves by SPARC ABI and returns a 64-bit quotient. The file embeds repeated `udiv_qrnnd`-style loops and one `umul_ppmm` verification/correction sequence. It references `__clz_tab` for normalization shift calculation.

Control flow: the routine distinguishes divisor high word zero from nonzero. For single-word divisors it performs one or two 32-bit quotient/remainder divisions, including an intentional hardware divide-by-zero path when divisor is zero. For multiword divisors it normalizes using leading-zero count, divides the normalized high words, multiplies the tentative quotient by the divisor low word, and decrements the quotient when the product is too large. It returns quotient high/low via locals restored into outputs.

State and persistence: no persistent state. Uses `%y`, stack frame, condition codes, and local registers. It does not write memory.

Dependencies/integration: depends on `__clz_tab` supplied by the kernel/libgcc support set. Used when compiler-generated unsigned long-long division cannot be inlined.

Risks: division helpers are high-risk because rare boundary combinations trigger correction paths. Divide-by-zero behavior intentionally traps via `udiv`; replacing it with a silent branch would alter ABI semantics. Normalization assumes `__clz_tab` availability and correct byte selection.

Test signals: exhaustive-ish randomized unsigned 64-bit division against C reference; boundary divisors 0, 1, 2^32-1, 2^32, high-word-only divisors, numerator < divisor, numerator == divisor, and quotient correction cases. Link tests should confirm `__clz_tab` resolves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/udivdi3.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/math-emu/Makefile -->
# sources/distributed-fs/ceph-client/arch/sparc/math-emu/Makefile

Purpose: builds the SPARC floating-point emulation object for the selected word size.

Important APIs/functions: `ccflags-y := -w` suppresses warnings for the emulation source, and `obj-y := math_$(BITS).o` selects `math_32.o` or `math_64.o` according to the architecture build variable.

Control flow: Kbuild includes exactly one object based on `BITS`; there is no conditional list beyond that.

State and persistence: no runtime state. Build-time state is limited to compiler flags and object selection.

Dependencies/integration: depends on architecture Kbuild defining `BITS`. Integrates the math emulator into the SPARC kernel image when this directory is built.

Risks: global warning suppression can hide real regressions in the emulation code. Wrong `BITS` propagation would build the incompatible dispatcher and register layout.

Test signals: build both sparc32 and sparc64 configurations and verify the expected object appears in link maps. A warning-enabled local build is useful for catching latent type issues despite `-w`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/math-emu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/math-emu/math_32.c -->
# sources/distributed-fs/ceph-client/arch/sparc/math-emu/math_32.c

Purpose: SPARC32 software floating-point instruction emulator. It decodes trapped FPOP instructions, runs Linux soft-fp operations, updates task FPU state, and reports whether a SIGFPE-style trap is required.

Important APIs/functions: `do_mathemu(struct pt_regs *regs, struct task_struct *fpt)` is the entry point. `record_exception(unsigned long *pfsr, int eflag)` updates FSR CEXC/AEXC/TEM/trap-type fields. `do_one_mathemu(u32 insn, unsigned long *pfsr, unsigned long *fregs)` decodes one instruction and dispatches to soft-fp macros. Opcode constants cover V8 single, double, quad, conversion, move, sqrt, and compare instructions. `argp` overlays raw register storage as single/double/quad.

Control flow: `do_mathemu` records an emulation perf event, either fetches the precise instruction from `regs->pc` when the FP queue is empty or iterates queued instructions from `thread.fpqueue`. On success for a precise trap it advances `pc/npc`; for queued traps it clears queue flags and `fpqdepth`. `do_one_mathemu` classifies FPOP1/FPOP2 opcodes into a packed `type`, validates register alignment for double/quad operands, unpacks operands with soft-fp macros, executes the requested arithmetic/conversion/compare, packs results unless `FP_INHIBIT_RESULTS`, and records exceptions.

State and persistence: mutates `fpt->thread.fsr`, `fpt->thread.float_regs`, `fpt->thread.fpqdepth`, and possibly `regs->pc/npc`. No heap state. Exception state persists in FSR accrued/current exception bits.

Dependencies/integration: includes scheduler/MM/uaccess/perf headers, `sfp-util_32.h`, and the generic `math-emu/soft-fp`, `single`, `double`, and `quad` macro layers. Trap handling supplies the task owning the FPU, which may not be `current`.

Risks: FPU queue handling is architecturally delicate; a failed queued instruction stops further emulation but still clears queue metadata. Register alignment checks determine whether invalid_fp_register is simulated. Soft-fp exception prioritization must match SPARC hardware, especially compare-with-NaN and trap-enabled TEM cases. `get_user` fetch failures return failure without advancing PC.

Test signals: SPARC32 FP emulation tests for all decoded opcodes, invalid register numbers, precise and queued traps, all IEEE exception classes with TEM enabled/disabled, NaN compare cases, and PC/nPC advancement. Perf software emulation fault counters should increment. Running floating-point workloads on systems with disabled/missing FPU is the integration signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/math-emu/math_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/math-emu/math_64.c -->
# sources/distributed-fs/ceph-client/arch/sparc/math-emu/math_64.c

Purpose: SPARC64 software floating-point emulator for unfinished/unimplemented FPop traps and illegal-instruction cases on newer sun4v CPUs. It handles quad operations, subnormal single/double operations, conversions, comparisons, and conditional quad moves.

Important APIs/functions: `do_mathemu(struct pt_regs *regs, struct fpustate *f, bool illegal_insn_trap)` is the entry point. `record_exception(struct pt_regs *regs, int eflag)` updates `current_thread_info()->xfsr[0]` and advances `tpc/tnpc` when no trap is generated. Opcode constants include FPOP1 quad/subnormal operations, FPOP2 compares, and conditional `fmovq` forms. It uses FPRS flags `FPRS_DL`, `FPRS_DU`, and `FPRS_FEF` to manage lazy FPU register state.

Control flow: the entry rejects privileged unfinished FPop by dying in kernel mode, records a perf emulation fault, adjusts PC for 32-bit tasks, fetches the user instruction, and decodes FPOP1/FPOP2. Conditional quad moves evaluate floating condition codes, integer condition codes, or register-zero/less-than conditions; false conditions become a nop that clears CEXC and advances PC, true conditions are rewritten as plain `fmovq`. For decoded operations, the routine validates trap type unless invoked via illegal instruction, maps encoded register numbers into SPARC64 FP register storage, substitutes zero for unsaved halves, initializes FPRS state for destinations, executes soft-fp macros, writes results or condition codes, records exceptions, and advances `tpc/tnpc` on success.

State and persistence: mutates `current_thread_info()->xfsr[0]`, `fpsaved[0]`, `gsr[0]`, `regs->tpc/tnpc`, and the supplied `fpustate` register file. It may flush user register windows to read locals for register-conditional moves. Exception and lazy-FPU state persist in thread info.

Dependencies/integration: includes `asm/fpumacro.h`, `asm/cacheflush.h`, `linux/uaccess.h`, `sfp-util_64.h`, and soft-fp headers. Integrates with trap handlers for unfinished FPop, unimplemented FPop, and UltraSPARC-T2 illegal instruction behavior.

Risks: register renumbering for 64-bit FP regs (`((freg & 1) << 5) | (freg & 0x1e)`) is easy to break. Conditional move paths read user register windows and must handle 32-bit vs 64-bit stack windows correctly. Trap-type validation differs for illegal-instruction traps, so caller classification matters. Lazy FPRS initialization can zero half the FP register file if flags are wrong.

Test signals: SPARC64 FP emulation tests for quad arithmetic/move/compare, subnormal single/double operations, 32-bit task PCs, all conditional `fmovq` condition sources, invalid register encodings, FPRS lazy state, and T2 illegal-instruction trap paths. User FP workloads forcing subnormal/quad software paths are key integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/math-emu/math_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/math-emu/sfp-util_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/math-emu/sfp-util_32.h

Purpose: SPARC32 machine-dependent support macros for the generic Linux soft-fp package.

Important APIs/types/macros: `add_ssaaaa` and `sub_ddmmss` implement double-word add/subtract with carry/borrow. `umul_ppmm` expands to a `%y`/`mulscc` 32x32-to-64 multiply. `udiv_qrnnd` expands to a 32-iteration quotient/remainder division loop. `UDIV_NEEDS_NORMALIZATION` is `0`, `abort()` maps to `return 0`, and `__BYTE_ORDER` is set from kernel endian macros.

Control flow: all behavior is macro-expanded into soft-fp callers. Arithmetic macros use inline assembly and condition codes; `abort()` returns failure from the containing emulation function.

State and persistence: no standalone state. Expanded code uses `%g1`, `%g2`, `%y`, condition codes, and local C variables. It can alter control flow of callers through `return 0`.

Dependencies/integration: includes kernel/sched/types and `asm/byteorder.h`. Consumed by `math_32.c` and generic `math-emu` headers, especially multiplication/division-heavy soft-fp operations.

Risks: inline asm constraints and clobbers must match GCC expectations. `%y` scheduling comments are important on SPARC; moving delay instructions can break multiplication. `abort()` being a return macro couples this header to functions returning integer success/failure.

Test signals: compile soft-fp with multiple GCC versions and run FP emulation arithmetic that exercises add/sub/mul/div internals, especially quad division. Static build checks should catch asm constraint regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/math-emu/sfp-util_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/math-emu/sfp-util_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/math-emu/sfp-util_64.h

Purpose: SPARC64 machine-dependent soft-fp support macros optimized for 64-bit words.

Important APIs/types/macros: `add_ssaaaa` and `sub_ddmmss` implement 128-ish add/sub on paired `UDItype` words. `umul_ppmm` uses `mulx` and 32-bit decomposition to produce high/low product words. `udiv_qrnnd` implements normalized double-word division in C using high/low divisor halves. `UDIV_NEEDS_NORMALIZATION` is `1`; `abort()` returns `0`; byte order is derived from kernel endian macros.

Control flow: macro-expanded into soft-fp code. The multiply macro is inline assembly with temporaries and carry handling. The divide macro performs Knuth-style two-step quotient digit estimation and correction.

State and persistence: no runtime state outside callers. Uses condition codes in asm and caller variables for quotient/remainder.

Dependencies/integration: includes kernel/sched/types and `asm/byteorder.h`. Used by `math_64.c` and generic soft-fp headers for quad/single/double operations.

Risks: `UDIV_NEEDS_NORMALIZATION` must agree with the divide macro implementation; soft-fp callers normalize before invoking it. Carry handling in `umul_ppmm` is compact and architecture-specific. The C divide macro assumes nonzero normalized high divisor halves.

Test signals: FP emulation tests for quad multiply/divide/conversions, compiler checks for inline asm constraints, and randomized soft-fp operation comparison against hardware or IEEE reference where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/math-emu/sfp-util_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/Makefile -->
# sources/distributed-fs/ceph-client/arch/sparc/mm/Makefile

Purpose: Kbuild manifest for SPARC-specific memory-management objects.

Important APIs/functions: selects `fault_$(BITS).o` and `init_$(BITS).o` for all builds. Adds SPARC64 `ultra.o`, `tlb.o`, `tsb.o`; SPARC32 SRMMU/IOMMU/cache CPU support objects; `hugetlbpage.o` when huge pages are enabled; and `execmem.o` when executable memory allocation is configured.

Control flow: object inclusion is controlled by `CONFIG_SPARC64`, `CONFIG_SPARC32`, `CONFIG_HUGETLB_PAGE`, and `CONFIG_EXECMEM`.

State and persistence: build-time only.

Dependencies/integration: coordinates architecture MM initialization, fault handling, TLB/TSB management, platform-specific cache/TLB ops, and DMA/IOMMU support.

Risks: incorrect config gating can link incompatible 32/64-bit objects or omit platform cache/TLB operations. New MM features must be added under the correct architecture config.

Test signals: build matrix for SPARC32, SPARC64, hugepage enabled/disabled, execmem enabled/disabled, and SBUS/SRMMU platform configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/execmem.c -->
# sources/distributed-fs/ceph-client/arch/sparc/mm/execmem.c

Purpose: SPARC implementation of executable memory allocation range setup.

Important APIs/functions: `execmem_arch_setup()` initializes a static `struct execmem_info` with `EXECMEM_DEFAULT` range from `MODULES_VADDR` to `MODULES_END`, `PAGE_KERNEL` protection, and 1-byte alignment, then returns it.

Control flow: single init-time assignment to `execmem_info` using a compound literal.

State and persistence: `execmem_info` is static and `__ro_after_init`, so the configured executable allocation policy persists read-only after init.

Dependencies/integration: includes `linux/mm.h` and `linux/execmem.h`; depends on SPARC module address constants and `PAGE_KERNEL` initialized by architecture paging setup. Used by generic execmem/module/BPF-style executable allocation infrastructure.

Risks: `PAGE_KERNEL` must be initialized before use. Range mismatch with module mapping limits would allow allocation outside executable kernel virtual space or unnecessarily constrain callers.

Test signals: boot with `CONFIG_EXECMEM`, module load/unload, BPF/JIT or other execmem users if enabled, and verification that allocations land between `MODULES_VADDR` and `MODULES_END`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/execmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/fault_32.c -->
# sources/distributed-fs/ceph-client/arch/sparc/mm/fault_32.c

Purpose: SPARC32 page-fault and register-window fault handling.

Important APIs/functions: `do_sparc_fault(regs, text_fault, write, address)` is the main fault entry. Helpers include `unhandled_fault`, `show_signal_msg`, `compute_si_addr`, `do_fault_siginfo`, `force_user_fault`, `window_overflow_fault`, `window_underflow_fault`, and `window_ret_fault`. Global `show_unhandled_signals` gates segfault logging.

Control flow: the main handler normalizes text faults to `regs->pc`, routes kernel vmalloc addresses through `vmalloc_fault`, rejects faults in atomic/no-mm contexts, locks/fetches VMA with `lock_mm_and_find_vma`, validates access permissions, calls `handle_mm_fault`, handles retry/completed/error cases, and signals user mode or searches exception tables for kernel mode. `vmalloc_fault` copies missing top-level kernel mappings from `init_mm`. Window fault helpers fault in stack save/restore areas and enforce 8-byte stack alignment.

State and persistence: mutates process page tables through `handle_mm_fault`/vmalloc synchronization, updates `regs->pc/npc` for exception fixups, and sends signals. No private persistent data besides `show_unhandled_signals`.

Dependencies/integration: uses core mm fault APIs, exception tables, perf page-fault events, SPARC register/window address computation, `mm_32.h`, SRMMU page table structures, and signal delivery.

Risks: in the `no_context` kernel path the code assigns `entry->fixup` without a visible null check, so it relies on reaching that path only when an exception table entry exists or on architecture expectations not shown here. Accurate effective-address computation is needed for user `si_addr`. Stack window faults cross page boundaries and can recurse into page fault handling.

Test signals: user SIGSEGV/SIGBUS tests for read/write/exec faults, vmalloc fault synchronization, exception-table protected copy routines, register-window overflow/underflow/ret faults across page boundaries, OOM fault handling, and perf page-fault counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/fault_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/fault_64.c -->
# sources/distributed-fs/ceph-client/arch/sparc/mm/fault_64.c

Purpose: SPARC64 page-fault handler for ITLB/DTLB misses, write/access faults, kernel exception fixups, non-faulting loads, stack growth, TSB growth, and huge TSB setup.

Important APIs/functions: `do_sparc64_fault(struct pt_regs *regs)` is the main entry. Helpers include `get_user_insn`, `do_fault_siginfo`, `get_fault_insn`, `do_kernel_fault`, `bad_kernel_pc`, and `bogus_32bit_fault_tpc`. Global `show_unhandled_signals` controls signal logging.

Control flow: the handler enters exception context, reads thread fault code/address, lets kprobes consume faults, validates 32-bit task address widths and privileged PCs, rejects atomic/no-mm contexts, emits perf page-fault events, locks `mmap_lock` with trylock optimization for kernel faults, resolves VMA and stack growth, optionally decodes the faulting instruction to infer writes on pure DTLB misses, validates ITLB execute and write/read permissions, calls `handle_mm_fault`, handles retry/completed/error/OOM/SIGBUS cases, grows base and huge TSBs according to RSS counters, and exits exception context. Kernel faults search exception tables, handle non-faulting loads by clearing destination registers or special `ldf/stq`, or die.

State and persistence: mutates page tables through `handle_mm_fault`, grows per-mm TSBs, updates thread fault code for Spitfire executable write block-commit, advances `tpc/tnpc` for exception fixups/non-faulting loads, sends signals, and may log diagnostics.

Dependencies/integration: uses kprobes, context tracking, exception tables, SPARC ASIs, LSU/fault-code bits, TSB management (`tsb_grow`, `hugetlb_setup`), huge/THP counters, instruction decoding helpers, and core mm.

Risks: write inference from instruction bits is best-effort and must exclude prefetches. Non-faulting load handling relies on ASI decoding. Kernel PC validation must keep module/init ranges in sync. TSB growth after faults depends on RSS counters adjusted for THP. Faulting while `mmap_read_trylock` fails has a special kernel path to avoid sleeping without fixup.

Test signals: SPARC64 user read/write/exec faults, 32-bit compat faults above 4GB, kernel exception-table copy paths, non-faulting load faults, stack auto-growth vs non-faulting load no-growth, THP/hugetlb first faults that trigger huge TSB setup, kprobe page-fault tests, OOM/SIGBUS paths, and TSB growth counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/fault_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/hugetlbpage.c -->
# sources/distributed-fs/ceph-client/arch/sparc/mm/hugetlbpage.c

Purpose: SPARC64 huge TLB page support, converting Linux hugepage sizes to SPARC TTE encodings and implementing huge PTE allocation, lookup, set, and clear operations.

Important APIs/functions: `arch_make_huge_pte`, `pud_leaf_size`, `pmd_leaf_size`, `pte_leaf_size`, `huge_pte_alloc`, `huge_pte_offset`, `__set_huge_pte_at`, `set_huge_pte_at`, and `huge_ptep_get_and_clear`. Static helpers translate shifts to sun4u/sun4v TTE size bits and back.

Control flow: `arch_make_huge_pte` marks the entry huge, selects sun4u or sun4v encoding by `tlb_type`, and applies ADI MCD bit handling for `VM_SPARC_ADI`. Allocation walks PGD/P4D/PUD/PMD and returns a PUD/PMD leaf slot for large sizes or a huge PTE page for smaller huge pages. Set/clear compute the hardware-backed size, derive how many page-table slots are covered, update `mm->context.hugetlb_pte_count`, fill or zero consecutive entries, and enqueue TLB batch invalidations, including the second real 4MB half of an 8MB Linux HPAGE.

State and persistence: mutates page-table entries and `mm->context.hugetlb_pte_count`. No private persistent state.

Dependencies/integration: depends on SPARC page bits, `tlb_type`, `maybe_tlb_batch_add`, core hugetlb APIs, pgalloc, TLB/cache headers, and ADI flags.

Risks: size translation differs between sun4u and sun4v; unsupported shifts only warn and can fall back to default 4MB encoding. Count accounting must match the number of page-table slots populated. 8MB Linux HPAGE backed by two 4MB hardware pages requires duplicate TLB batching.

Test signals: hugetlb allocation/mapping/unmapping for 64K, 4MB/HPAGE, 256MB, 2GB, and 16GB where supported; ADI huge mappings; page-table count accounting; and TLB invalidation after clear/change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/hugetlbpage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/hypersparc.S -->
# sources/distributed-fs/ceph-client/arch/sparc/mm/hypersparc.S

Purpose: high-speed HyperSPARC-specific MMU, cache, TLB, page clear, and page copy routines for SPARC32 SRMMU systems.

Important APIs/functions: exports cache flush operations (`hypersparc_flush_cache_all/mm/range/page`, `hypersparc_flush_page_to_ram`, `hypersparc_flush_page_for_dma`, `hypersparc_flush_sig_insns`), TLB flush operations (`hypersparc_flush_tlb_all/mm/range/page`), and `hypersparc_setup_blockops`. Init-only routines `hypersparc_bzero_1page` and `hypersparc_copy_1page` are copied over generic page clear/copy implementations.

Control flow: cache routines flush register windows, read global VAC line/cache size variables, choose whole-user-space flushing for large ranges or page-by-page flushing for smaller ranges, temporarily switch SRMMU context registers, probe mappings, issue ASI_M flush stores, and restore context. TLB routines write SRMMU flush probe addresses at all/mm/range/page granularity. Blockops use HyperSPARC block fill/copy ASIs and `hypersparc_setup_blockops` patches generic routines then flushes the whole I-cache.

State and persistence: mutates hardware cache/TLB/MMU state and, during init, overwrites generic `bzero_1page`/`__copy_1page` code with HyperSPARC-specific implementations. It temporarily changes SRMMU context registers and restores them.

Dependencies/integration: includes SPARC ptrace/PSR/ASI/page/pgtable/SRMMU headers and asm offsets for `mm_context`/`vma->vm_mm`. Selected by HyperSPARC CPU setup as cache/TLB ops.

Risks: ASI operations are hardware-specific and can corrupt active contexts if restore paths fail. Some routines skip work when `mm_context == -1` on non-SMP builds. Self-modifying blockops require exact instruction count limits and I-cache flush. Comments note HyperSPARC flushes require valid mappings for physical tag match.

Test signals: HyperSPARC boot, context-switch stress, mmap/munmap cache coherency, signal trampoline flush, DMA coherency, page clear/copy memory tests, and TLB shootdown tests. Disassembly should confirm copied blockops stay within documented instruction-size limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/hypersparc.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/init_32.c -->
# sources/distributed-fs/ceph-client/arch/sparc/mm/init_32.c

Purpose: SPARC32 memory initialization, bootmem/memblock setup, highmem accounting, ramdisk reservation, valid physical address bitmap construction, cache flush exports, and VMA protection map.

Important APIs/functions: globals `phys_base`, `pfn_base`, `sp_banks`, `highstart_pfn`, `highend_pfn`, `last_valid_pfn`. Functions include `calc_highpages`, `bootmem_init`, `paging_init`, `arch_mm_preinit`, `sparc_flush_page_to_ram`, `sparc_flush_folio_to_ram`, and `DECLARE_VM_GET_PAGE_PROT`.

Control flow: `bootmem_init` adds PROM-discovered physical banks to memblock, honors `cmdline_memory_size` by trimming banks, computes kernel end/start PFNs, detects highmem above `SRMMU_MAXMEM`, reserves initrd and kernel image, limits memblock allocations to lowmem, and returns max PFN. `paging_init` delegates SRMMU page-table setup then builds device tree and scans devices. `arch_mm_preinit` validates fixmap/pkmap separation, allocates `sparc_valid_addr_bitmap`, zeros it, and marks real pages. Flush helpers call lower-level cache routines for pages/folios.

State and persistence: initializes global physical memory bank state, memblock memory/reserved ranges, highmem PFNs, valid address bitmap, initrd virtual/physical addresses, and protection map used by VM page protections.

Dependencies/integration: includes memblock, initrd, highmem, SRMMU/TLB/prom/leon headers, and `mm_32.h`. Requires `sp_banks` and base PFNs populated earlier by platform setup.

Risks: bank trimming for `mem=` must keep sentinel entries valid. Highmem split uses bank ordering and `SRMMU_MAXMEM`; holes can affect `calc_max_low_pfn`. Valid address bitmap sizes are derived from `last_valid_pfn` and 1MB chunks. Initrd address normalization handles bootloader quirks and can reserve wrong memory if `phys_base` is wrong.

Test signals: SPARC32 boot with multiple memory banks, `mem=` limits, initrd present/absent, highmem systems, pkmap/fixmap overlap assertions, valid-address checks, and page/folio cache flush callers. `/proc/iomem`/memblock logs should reflect trimmed/reserved ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/init_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/init_64.c -->
# sources/distributed-fs/ceph-client/arch/sparc/mm/init_64.c

Purpose: central SPARC64 memory-management initialization and support code. It covers PROM memory discovery, kernel linear mapping, TSB setup, MMU context allocation, cache/TLB helpers, NUMA topology parsing, hugepage/THP TSB integration, pgprot initialization for sun4u/sun4v, vmemmap population, initmem freeing, and highpage copying with ADI tags.

Important APIs/functions: exported/state globals include `kern_linear_pte_xor`, `kern_base`, `kern_size`, `sparc64_highest_unlocked_tlb_ent`, `sparc64_kern_pri_context`, `prom_trans`, `prom_trans_ents`, `kern_locked_tte_data`, `PAGE_OFFSET`, `VMALLOC_END`, `PAGE_KERNEL`, `PAGE_SHARED`, `_PAGE_IE`, `_PAGE_E`, `_PAGE_CACHE`, and NUMA lookup tables. Major functions include `paging_init`, `bootmem_init`, `kernel_physical_mapping_init`, `kernel_map_range`, `update_mmu_cache_range`, `flush_dcache_folio`, `flush_icache_range`, `get_new_mmu_context`, `hugetlb_setup`, `arch_hugetlb_valid_size`, `arch_zone_limits_init`, `mem_init`, `free_initmem`, `vm_get_page_prot`, `mk_pte_io`, `pte_sz_bits`, `__flush_tlb_all`, `copy_user_highpage`, and `copy_highpage`.

Control flow: boot begins in `paging_init`, which selects VA layout by CPU/TLB type, initializes pgprot/cacheability bits, patches TSB/TLB handlers, reads PROM translations and memory twice, fills memblock, reserves kernel/initrd/limited memory, remaps and locks the kernel image, enables trap handlers, builds device/CPU metadata, discovers page-size support, registers sun4v kernel TSBs, initializes NUMA or fallback node data, creates physical kernel mappings, flushes TSB/TLB state, and finishes boot memory setup. Runtime fault paths call `update_mmu_cache_range` and `update_mmu_cache_pmd` to insert base/huge TSB entries. Context allocation wraps versions and preserves active secondary contexts. NUMA parsing uses machine description or sun4u JBus encodings to assign memory ranges and CPU masks.

State and persistence: persistent state includes memblock ranges, node data, TSB descriptors, kernel page tables, context bitmap/version cache, per-mm TSB counts, PROM translation table, page protection globals, VA hole limits, `PAGE_OFFSET`, cache dirty bits in folio flags, and resource tree entries for system RAM/kernel segments. Some init code patches executable instructions and registers physical TSB addresses with the hypervisor.

Dependencies/integration: depends on OpenBoot PROM, sun4v hypervisor calls, machine description parser, SPARC TLB/TSB/trap assembly patch tables, core mm/memblock/hugetlb/sparsemem, perf/cache/TLB helpers, ADI/MCD ASIs, and generic resource registration. It is the integration point between hardware page-size capabilities and Linux page table abstractions.

Risks: this file has high architectural risk. VA hole and `max_phys_bits` selection must match CPU capabilities and four-level page-table limits. `kern_linear_pte_xor` drives trap-time linear TTE fabrication, so page-size/cacheability mistakes break all direct-map faults. PROM memory must be sanitized and sorted; stale OBP mappings are retained only for the OBP range. NUMA machine-description parsing assumes latency/self entries are present and normalizes by self-latency. Context wrap must avoid assigning context 0 and must synchronize with secondary contexts. D-cache dirty state is packed into high folio flag bits and protected by build-time constraints. ADI tag copy loops must keep physical source/destination progression correct.

Test signals: SPARC64 boot across sun4u and sun4v chip families, with different page sizes, memory holes, `mem=` limits, initrd, NUMA enabled/off/debug, hugetlb/THP, sparse vmemmap, debug pagealloc, modules/vmalloc, and ADI-capable systems. Fault-driven tests should exercise TSB insertion/growth and context wrap. `/proc/cpuinfo` or MMU info should show supported page sizes. Resource tree should include RAM/code/data/bss. Highpage copy tests should preserve ADI tags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/init_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/init_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/mm/init_64.h

Purpose: shared declarations for SPARC64 memory initialization state used by C and assembly, especially TLB miss handling and PROM mapping code.

Important APIs/types/functions: defines `MAX_PHYS_ADDRESS`, declares `kern_linear_pte_xor`, locked/unlocked TLB/context globals, `mmu_info`, `prom_world`, `kern_locked_tte_data`, and `struct linux_prom_translation { virt, size, data }`. Exposes `prom_trans[512]` and `prom_trans_ents` for kernel TLB miss handling in `ktlb.S`.

Control flow: header only; no runtime control flow.

State and persistence: declares persistent globals owned by `init_64.c` and consumed by assembly/runtime MMU code.

Dependencies/integration: includes `asm/page.h`; comments identify assembler consumers and SMP boot usage. It is the ABI contract between `init_64.c`, trap/TLB miss assembly, and PROM world transitions.

Risks: changing structure layout or symbol names breaks assembly consumers. `MAX_PHYS_ADDRESS` depends on `MAX_PHYS_ADDRESS_BITS` being correctly set by architecture headers.

Test signals: SPARC64 build and link, objdump/symbol checks for assembly references, boot through TLB miss handling and PROM callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/init_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/io-unit.c -->
# sources/distributed-fs/ceph-client/arch/sparc/mm/io-unit.c

Purpose: SUN4D IO-UNIT DVMA/IOMMU support and DMA mapping operations.

Important APIs/functions: `iounit_init` discovers `sbi` nodes and initializes IO-UNITs. `iounit_iommu_init` maps the external page table and installs `iounit_dma_ops`. DMA ops include `iounit_map_phys`, `iounit_unmap_phys`, `iounit_map_sg`, `iounit_unmap_sg`, and under `CONFIG_SBUS`, `iounit_alloc`/`iounit_free`. `iounit_get_area` allocates IO PTE slots and programs page-table entries.

Control flow: init allocates an `iounit_struct`, sets bitmap limits/rotors, maps the XPT resource, clears page-table entries, and attaches DMA ops to the platform device. Mapping acquires the IO-UNIT lock, chooses a bitmap range class based on required page count, scans for contiguous free slots with rotor wraparound, writes `MKIOPTE` entries, and returns an IOUNIT DMA address. Unmap clears bitmap bits. SBUS allocation allocates zeroed pages, reserves DVMA resources, maps CPU PTEs and IO PTEs, flushes cache/TLB, and returns the DVMA CPU address.

State and persistence: per-device `iounit_struct` persists in `dev.archdata.iommu`, including page table pointer, bitmap, limits, rotors, and spinlock. Hardware XPT entries persist until unmapped.

Dependencies/integration: uses OF/platform discovery, SBUS register access, DMA map ops, SPARC DMA resource allocator, cache/TLB flushes, and `mm_32.h`. `subsys_initcall` runs before drivers need DMA ops.

Risks: maximum mapping length is hard-limited to 256 KiB. `iounit_free` is unimplemented under `CONFIG_SBUS`, so consistent allocations may leak unless unused or handled elsewhere. Bitmap/page-table updates must be lock-protected. Mapping failure in scatter-gather after partial success lacks rollback.

Test signals: SUN4D/SBUS boot, DMA map/unmap for single and scatter-gather buffers around page boundaries, >256 KiB rejection, rotor wraparound, XPT programming validation, and consistent allocation/free behavior if SBUS alloc is exercised.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/io-unit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/iommu.c -->
# sources/distributed-fs/ceph-client/arch/sparc/mm/iommu.c

Purpose: SPARC32 SBUS IOMMU/DVMA support for systems with IOMMU hardware.

Important APIs/functions: `iommu_init` discovers `iommu` OF nodes and initializes each through `sbus_iommu_init`. DMA operations are split into global-flush and per-page-flush variants: `sbus_iommu_map_phys_gflush/pflush`, `sbus_iommu_map_sg_gflush/pflush`, `sbus_iommu_unmap_phys`, `sbus_iommu_unmap_sg`, and under `CONFIG_SBUS`, `sbus_iommu_alloc/free`. `ld_mmu_iommu` initializes cacheability/PTE permission defaults by CPU type.

Control flow: initialization maps IOMMU registers, enables a 256MB range, allocates and zeroes the IOMMU page table and bitmap, configures page coloring for HyperSPARC, and chooses DMA ops based on `flush_page_for_dma_global`. Mapping rejects MMIO and >256 KiB ranges, optionally flushes CPU cache pages, allocates colored IOMMU slots via `bit_map_string_get`, writes IOPTEs and invalidates IOMMU pages, flushes IOPTE cache lines, and returns a bus address. Unmap clears IOPTEs, invalidates hardware, and frees bitmap slots. Consistent allocation reserves a DVMA resource, maps kernel PTEs with `dvma_prot`, writes non-cacheable or cacheable IOPTEs depending on CPU, flushes cache/TLB, and returns CPU/DMA handles.

State and persistence: per-device `iommu_struct` persists with registers, page table, start/end, and `usemap`. Static `ioperm_noc`, `dvma_prot`, and `viking_flush` influence future mappings. Hardware IOMMU page table state persists until unmapped.

Dependencies/integration: uses OF/platform devices, SBUS IOMMU registers, `bitext` allocator, CPU cache flush routines (`viking_*`, `__flush_page_to_ram`), SPARC DMA resource allocator, and `mm_32.h`.

Risks: partial scatter-gather map failure returns `-EIO` without undoing earlier entries. Cache-coherency choices depend on CPU detection and `flush_page_for_dma_global`. Bitmap exhaustion panics. Consistent allocation/free requires exact DVMA resource and bitmap synchronization.

Test signals: SBUS DMA workloads on Viking/HyperSPARC and non-cache-coherent CPUs, map/unmap stress with page-color constraints, scatter-gather failure injection, >256 KiB rejection, consistent DMA allocation/free, and IOMMU register/page-table inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/iommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/leon_mm.c -->
# sources/distributed-fs/ceph-client/arch/sparc/mm/leon_mm.c

Purpose: LEON SPARC32 SRMMU support, including software page-table probing and cache/TLB operation implementations.

Important APIs/functions: `leon_swprobe(vaddr, paddr)` walks SRMMU tables by physical bypass loads. Cache/TLB functions include `leon_flush_icache_all`, `leon_flush_dcache_all`, `leon_flush_cache_all`, `leon_flush_tlb_all`, and per-mm/page/range wrappers. `leon3_getCacheRegs` reads LEON3 cache registers. `leon_flush_needed` decides whether context-switch cache flushing is required. `init_leon` installs `leon_ops`.

Control flow: `leon_swprobe` reads the context table pointer, validates physical pages with `_pfn_valid`, reads the current context, walks PGD/PMD/PED/PTE levels using LEON bypass loads, handles large PTEs at higher levels, computes physical address based on the found level, and returns the PTE. Flush functions issue LEON ASI cache/TLB flush instructions. `leon_flush_needed` reads cache set/size fields and disables context-switch flush when direct-mapped set size is no larger than page size. `init_leon` names the SRMMU, sets cache/TLB ops, sets poke hook, and records flush policy.

State and persistence: globals `leon_flush_during_switch` and `srmmu_swprobe_trace`; installed `sparc32_cachetlb_ops` and `poke_srmmu` persist after init. Cache/TLB hardware state is mutated by flush calls.

Dependencies/integration: includes LEON ASI/TLB headers and `mm_32.h`; integrates with SRMMU page tables, context register access, and common SPARC32 cache/TLB ops dispatch.

Risks: software probing must reject invalid physical table pointers to avoid bypass-load faults. Large-page physical address reconstruction depends on level-specific masks. Flush-needed heuristic only recognizes LEON3 cache fields and defaults to flushing when uncertain.

Test signals: LEON boot, page-fault/probe paths, context switch cache coherency with flush enabled/disabled, executable page icache coherency, DMA dcache flushes, TLB flush all/mm/page/range behavior, and cache register decoding logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/leon_mm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/mm_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/mm/mm_32.h

Purpose: SPARC32 MM internal header exposing symbols shared between fault handling, SRMMU initialization, and IOMMU/LEON support.

Important APIs/functions: declares `do_sparc_fault`, `window_overflow_fault`, `window_underflow_fault`, `window_ret_fault`, SRMMU globals `srmmu_name`, `viking_mxcc_present`, `flush_page_for_dma_global`, `poke_srmmu`, init function `srmmu_paging_init`, and IOMMU setup function `ld_mmu_iommu`.

Control flow: header only; it enables assembler-visible fault entry points and cross-file calls.

State and persistence: declares persistent global state owned by other SPARC32 MM files, particularly selected SRMMU name/model and DMA flush policy.

Dependencies/integration: consumed by `fault_32.c`, `init_32.c`, `io-unit.c`, `iommu.c`, `leon_mm.c`, and SRMMU platform code. It defines the local contract for architecture MM components without exposing them globally.

Risks: prototypes must match assembly call conventions (`asmlinkage`) and C definitions. Misdeclared globals can break platform cache/TLB setup or DMA coherency policy.

Test signals: SPARC32 build/link, boot through page fault/window fault paths, SRMMU paging init, and IOMMU initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/mm/mm_32.h -->
