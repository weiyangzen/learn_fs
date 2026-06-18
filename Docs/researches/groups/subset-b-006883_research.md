# subset-b-006883 research

Grouped research report for the rseq selftest files and the rtc selftest Makefile. Each section is source-tree aligned and delimited for deterministic reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/param_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/param_test.c

Purpose: `param_test.c` is the main stress and correctness exerciser for the userspace restartable sequence helper layer. It drives the rseq primitives through sharded spinlocks, per-cpu increments, linked-list push/pop, bounded pointer buffers, memcpy-based buffers, and the membarrier restart path. It can run in ordinary, legacy, compare-twice, CPU-id, and mm-cid modes depending on how the Makefile builds the binary and what command-line flags the runner passes.

Important APIs, types, and functions: the file defines test data families around `percpu_lock`, `spinlock_test_data`, `inc_test_data`, `percpu_list`, `percpu_buffer`, and `percpu_memcpy_buffer`. Core helpers include `rseq_this_cpu_lock()`, `rseq_percpu_unlock()`, `this_cpu_list_push()`, `this_cpu_list_pop()`, `this_cpu_buffer_push()`, `this_cpu_buffer_pop()`, `this_cpu_memcpy_buffer_push()`, and `this_cpu_memcpy_buffer_pop()`. Test entry points are `test_percpu_spinlock()`, `test_percpu_inc()`, `test_percpu_list()`, `test_percpu_buffer()`, `test_percpu_memcpy_buffer()`, and `test_membarrier()`. The code calls the public wrappers from `rseq.h`: `__rseq_register_current_thread()`, `rseq_unregister_current_thread()`, `rseq_cmpeqv_storev()`, `rseq_cmpnev_storeoffp_load()`, `rseq_addv()`, `rseq_cmpeqv_trystorev_storev()`, `rseq_cmpeqv_cmpeqv_storev()`, `rseq_cmpeqv_trymemcpy_storev()`, and conditionally `rseq_offset_deref_addv()`.

Control flow: `main()` parses flags, installs the SIGUSR1 handler, optionally registers rseq for the main thread, validates the selected CPU/mm-cid source, and dispatches by `-T`. Each test allocates per-cpu state, starts `opt_threads` pthreads, lets each worker register/unregister rseq, loops for `opt_reps`, and validates aggregate invariants after joining. The delay-injection macros can add assembly delay loops and C-level yield/signal/sleep points inside critical sections, which exercises abort and restart behavior under preemption-like interruptions.

State and persistence: all state is in process memory. Global options control test mode, injection, memory ordering, registration, and thread counts. Thread-local counters track delivered signals, injected yields, and rseq aborts. Per-cpu arrays are padded to reduce false sharing and are indexed either by `cpu_id_start`/`cpu_id` or by `mm_cid`, selected at build time by `BUILDOPT_RSEQ_PERCPU_MM_CID`.

Dependencies and integration points: it depends on pthreads, scheduler affinity, signals, membarrier, and the local `rseq.h` helper stack. It is orchestrated by `run_param_test.sh`, which runs all variants and injection modes. Membarrier coverage is compiled only when the selected architecture exposes `RSEQ_ARCH_HAS_OFFSET_DEREF_ADDV`.

Risks and test signals: `CPU_SETSIZE` bounds all per-cpu arrays, so unusual CPU/mm-cid values outside that range would be unsafe. `opt_reps / 10` appears in progress logging and assumes the default nonzero repetition count. The correctness signals are process exit status and assertions that counters and object sums match their expected totals; failures abort immediately. Successful coverage is stronger when run under injection, compare-twice, legacy, optimized, CPU-id, and mm-cid variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/param_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-abi.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-abi.h

Purpose: `rseq-abi.h` defines the userspace/kernel ABI structures and constants for restartable sequences as consumed by the selftests. It mirrors the syscall-facing contract: registration states, unregister flags, critical-section flags, the critical-section descriptor, and the per-thread `struct rseq_abi` layout.

Important APIs, types, and functions: key types are `enum rseq_abi_cpu_id_state`, `enum rseq_abi_flags`, `enum rseq_abi_cs_flags_bit`, `enum rseq_abi_cs_flags`, `struct rseq_abi_cs`, `struct rseq_abi_slice_ctrl`, and `struct rseq_abi`. `struct rseq_abi_cs` records `version`, `flags`, `start_ip`, `post_commit_offset`, and `abort_ip`. `struct rseq_abi` exposes `cpu_id_start`, `cpu_id`, `rseq_cs`, `flags`, `node_id`, `mm_cid`, `slice_ctrl`, and an extensible end marker.

Control flow: this header has no runtime control flow. It supplies declarations used by `rseq.c`, `rseq.h`, and the architecture headers. Runtime code writes `rseq_cs.arch.ptr` before critical sections, the kernel validates the active descriptor, and aborts clear or redirect through the descriptor state.

State and persistence: the ABI state is per-thread TLS once registered. Kernel-updated fields include CPU IDs, node ID, mm CID, and time-slice grant state. User space writes the active critical-section pointer and slice extension request. The alignment attributes are important persistent ABI properties because the kernel expects cache-line-friendly, atomic access to fields.

Dependencies and integration points: it depends on `<linux/types.h>` and byte-order macros. `rseq.c` allocates a TLS instance of this structure, and `rseq.h` uses offsets and feature-size checks to guard access to extension fields such as `node_id`, `mm_cid`, and `slice_ctrl`. `slice_test.c` uses `slice_ctrl` directly.

Risks and test signals: ABI drift is the primary risk. Incorrect alignment, offset, endian handling, or feature-size assumptions can break the syscall contract across all architectures. Test coverage comes indirectly from registration, syscall error checks, per-cpu operation tests, mm-cid tests, and slice extension tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-arm-bits.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-arm-bits.h

Purpose: `rseq-arm-bits.h` instantiates ARM 32-bit rseq critical sections through the common template mechanism. It is included multiple times by `rseq-arm.h` to produce CPU-id, mm-cid, relaxed, release, and CPU-id-independent helper names.

Important APIs, types, and functions: it defines always-inline implementations for `rseq_cmpeqv_storev`, `rseq_cmpnev_storeoffp_load`, `rseq_addv`, `rseq_cmpeqv_cmpeqv_storev`, `rseq_cmpeqv_trystorev_storev`, and `rseq_cmpeqv_trymemcpy_storev`, each renamed by `RSEQ_TEMPLATE_IDENTIFIER()`. These functions map directly to the generic wrappers in `rseq.h`.

Control flow: each function builds an `asm goto` critical section. The sequence stores the active `rseq_cs`, compares the current CPU/mm-cid field with the caller-provided value, performs one or more data checks or speculative stores, reaches the post-commit label on success, or branches to comparison-failure and abort labels. The abort paths call `RSEQ_INJECT_FAILED` and return a negative value, while comparison failures return a positive value.

State and persistence: it updates only caller-provided memory locations and the thread-local active `rseq_cs` pointer. It relies on the kernel to redirect execution to the abort IP when preemption, signal delivery, or migration invalidates the sequence. Release variants insert the ARM memory-ordering operation before the final commit store.

Dependencies and integration points: it depends on macros from `rseq-arm.h` for table emission, abort signatures, CPU comparison, and memory-order operations, plus `rseq-bits-template.h` for suffix selection. It is exercised by `param_test.c` operations on ARM little-endian builds.

Risks and test signals: inline assembly register constraints, Thumb/A32 signature handling, and exact label/table placement are fragile. The header intentionally has no standalone include guard because repeated inclusion is the generation mechanism. Test signals are successful `param_test` runs, especially injected aborts and release-mode buffer/memcpy tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-arm-bits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-arm.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-arm.h

Purpose: `rseq-arm.h` supplies ARM-specific rseq ABI constants, memory barriers, descriptor table macros, abort signatures, and include-time template expansion for 32-bit ARM selftests.

Important APIs, types, and functions: it defines `RSEQ_SIG`, `rseq_smp_mb()`, `rseq_smp_rmb()`, `rseq_smp_wmb()`, `rseq_smp_load_acquire()`, `rseq_smp_acquire__after_ctrl_dep()`, `rseq_smp_store_release()`, `RSEQ_ASM_DEFINE_TABLE()`, `RSEQ_ASM_DEFINE_EXIT_POINT()`, `RSEQ_ASM_STORE_RSEQ_CS()`, `RSEQ_ASM_CMP_CPU_ID()`, `RSEQ_ASM_DEFINE_ABORT()`, and `RSEQ_ASM_DEFINE_CMPFAIL()`.

Control flow: after defining ARM assembly building blocks, the file includes `rseq-arm-bits.h` five times: CPU-id relaxed, CPU-id release, mm-cid relaxed, mm-cid release, and CPU-id-none relaxed. This generates the concrete function names expected by `rseq.h`.

State and persistence: the macros describe how the active rseq critical-section descriptor is written into TLS and how the linker-visible `__rseq_cs`, `__rseq_cs_ptr_array`, and exit-point sections are populated. Runtime state is still owned by the generated helpers and kernel rseq handling.

Dependencies and integration points: it is selected by `rseq.h` for `__ARMEL__`. It uses ARM `dmb` barriers and a signature chosen around ARM endian/code-mode constraints. `param_test.c` relies on the generated helpers when built on ARM.

Risks and test signals: the highest risk is signature and endian mismatch, because the kernel expects a safe uncommon trap pattern. Table encoding uses 32-bit words for 64-bit ABI fields, so ordering and zero-extension must remain correct. Test signals come from build success on ARM and rseq operation/injection tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-arm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-arm64-bits.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-arm64-bits.h

Purpose: `rseq-arm64-bits.h` provides AArch64 generated rseq primitive implementations. It is a template body included by `rseq-arm64.h` for each CPU-id/mm-cid and relaxed/release combination.

Important APIs, types, and functions: generated helpers include `rseq_cmpeqv_storev`, `rseq_cmpnev_storeoffp_load`, `rseq_addv`, `rseq_cmpeqv_cmpeqv_storev`, `rseq_cmpeqv_trystorev_storev`, and `rseq_cmpeqv_trymemcpy_storev`. Unlike x86, RISC-V, and OR1K, this file does not define `RSEQ_ARCH_HAS_OFFSET_DEREF_ADDV`.

Control flow: each helper emits an AArch64 `asm goto` critical section using macros such as `RSEQ_ASM_STORE_RSEQ_CS`, `RSEQ_ASM_CMP_CPU_ID`, compare/load/store operations, and the final post-commit label. Compare failures and aborts are separated to let callers distinguish expected data contention from kernel-triggered restart.

State and persistence: the generated code writes the active `rseq_cs` pointer, reads the ABI CPU/mm-cid field, and updates caller memory atomically relative to migration/preemption semantics. Release forms use store-release/fence-style final stores supplied by `rseq-arm64.h`.

Dependencies and integration points: it depends on AArch64 temporary registers and operation macros from `rseq-arm64.h`, and template suffixing from `rseq-bits-template.h`. `param_test.c` uses these helpers for AArch64 per-cpu structures.

Risks and test signals: risks include clobber list accuracy, register allocation conflicts, and copy-loop correctness in `trymemcpy`. Since rseq correctness relies on exact instruction ranges, label placement around final stores is critical. Test signals are passing buffer, memcpy, and compare-twice variants on AArch64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-arm64-bits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-arm64.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-arm64.h

Purpose: `rseq-arm64.h` defines the AArch64 rseq architecture layer: trap signature, memory barriers, acquire/release primitives, descriptor-section encoding, and assembly operation macros.

Important APIs, types, and functions: it defines `RSEQ_SIG_CODE`, endian-adjusted `RSEQ_SIG_DATA`, `RSEQ_SIG`, `rseq_smp_*` barriers, typed `rseq_smp_load_acquire()` and `rseq_smp_store_release()`, scratch registers `x15`, `w15`, `x14`, table/exit/abort macros, compare/store/load/add macros, and byte-copy helpers.

Control flow: the header sets up reusable operation snippets, then includes `rseq-arm64-bits.h` for CPU-id relaxed/release, mm-cid relaxed/release, and CPU-id-none relaxed helpers. The generated functions are then selected by the generic wrappers in `rseq.h`.

State and persistence: state is not stored in this header directly, but its macros define how generated helpers publish `struct rseq_abi_cs` records into ELF sections and how they store the active critical-section pointer into the TLS ABI area.

Dependencies and integration points: selected by `rseq.h` for `__AARCH64EL__`. It depends on AArch64 barrier and load-acquire/store-release instructions. It integrates with `param_test.c` and any other selftest including `rseq.h` on AArch64.

Risks and test signals: risks include endian-specific signature representation, missing clobbers for scratch registers, and unsupported object sizes in acquire/release helpers. Passing selftests on AArch64, especially `-M` release-mode buffer/memcpy runs, are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-arm64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-bits-reset.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-bits-reset.h

Purpose: `rseq-bits-reset.h` cleans up template macros after a generated `*-bits.h` inclusion. It prevents one include pass from leaking suffix and CPU-id field definitions into the next pass.

Important APIs, types, and functions: it undefines `RSEQ_TEMPLATE_IDENTIFIER`, `RSEQ_TEMPLATE_CPU_ID_FIELD`, `RSEQ_TEMPLATE_CPU_ID_OFFSET`, and `RSEQ_TEMPLATE_SUFFIX`.

Control flow: there is no runtime behavior. The control-flow role is preprocessor-only: each architecture bits file includes this reset at the end so the parent architecture header can safely set a new `RSEQ_TEMPLATE_*` combination.

State and persistence: no runtime state exists. The only persistent effect is on the preprocessor macro namespace during compilation.

Dependencies and integration points: it is paired with `rseq-bits-template.h` and included at the end of architecture-specific `*-bits.h` files. All architecture headers rely on this cleanup because they intentionally include their bits files multiple times.

Risks and test signals: if this file misses a template macro, generated helper names or CPU-id field offsets can silently use stale state. Build failures or duplicate/missing symbols in architecture builds are the strongest test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-bits-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-bits-template.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-bits-template.h

Purpose: `rseq-bits-template.h` maps preprocessor mode flags to generated rseq helper suffixes and ABI CPU/mm-cid field offsets. It is the common naming and field-selection layer for all architecture bits headers.

Important APIs, types, and functions: it defines `RSEQ_TEMPLATE_CPU_ID_OFFSET`, `RSEQ_TEMPLATE_CPU_ID_FIELD`, `RSEQ_TEMPLATE_SUFFIX`, and `RSEQ_TEMPLATE_IDENTIFIER(x)`. Modes include `RSEQ_TEMPLATE_CPU_ID`, `RSEQ_TEMPLATE_MM_CID`, and `RSEQ_TEMPLATE_CPU_ID_NONE`, combined with `RSEQ_TEMPLATE_MO_RELAXED` or `RSEQ_TEMPLATE_MO_RELEASE`.

Control flow: there is no runtime control flow. The preprocessor selects one branch and constructs identifiers such as `_relaxed_cpu_id`, `_release_cpu_id`, `_relaxed_mm_cid`, `_release_mm_cid`, or `_relaxed`.

State and persistence: no runtime state. The generated values select whether helpers compare `cpu_id`, `mm_cid`, or no CPU-like ABI field, which affects runtime validation inside critical sections.

Dependencies and integration points: it depends on architecture headers defining offsets such as `RSEQ_CPU_ID_OFFSET` and `RSEQ_MM_CID_OFFSET`, and on `RSEQ_COMBINE_TOKENS` from the compiler helper stack. Every `*-bits.h` file includes it first.

Risks and test signals: misuse by direct include is explicitly rejected. Incorrect suffixes or offsets would cause link failures or, worse, helpers comparing the wrong ABI field. Test signals include successful multi-variant builds and passing CPU-id/mm-cid variants in `run_param_test.sh`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-bits-template.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-generic-thread-pointer.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-generic-thread-pointer.h

Purpose: `rseq-generic-thread-pointer.h` supplies the fallback implementation of `rseq_thread_pointer()` using the compiler builtin thread-pointer intrinsic.

Important APIs, types, and functions: it exposes `static inline void *rseq_thread_pointer(void)`, wrapped for C++ compatibility.

Control flow: the function simply returns `__builtin_thread_pointer()`. There are no branches besides header guards and C++ extern handling.

State and persistence: no state is stored. Its return value is used by `rseq.c` to compute the offset between the architecture thread pointer and the selftest-owned TLS rseq area, and by `rseq_get_abi()` to recover the current thread's ABI area.

Dependencies and integration points: included by `rseq-thread-pointer.h` on architectures without a dedicated implementation. It depends on compiler support for `__builtin_thread_pointer()`.

Risks and test signals: the risk is compiler or architecture support mismatch. If the builtin returns a pointer using semantics different from libc TLS layout, rseq ABI lookup fails. Test signals are successful registration and current CPU reads on generic-path architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-generic-thread-pointer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-mips-bits.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-mips-bits.h

Purpose: `rseq-mips-bits.h` implements the MIPS generated rseq operations used by the generic wrappers. It supports the common compare/store, pop/load, add, double-compare, speculative-store, and memcpy/final-store primitives.

Important APIs, types, and functions: it generates `rseq_cmpeqv_storev`, `rseq_cmpnev_storeoffp_load`, `rseq_addv`, `rseq_cmpeqv_cmpeqv_storev`, `rseq_cmpeqv_trystorev_storev`, and `rseq_cmpeqv_trymemcpy_storev` variants. It does not advertise `RSEQ_ARCH_HAS_OFFSET_DEREF_ADDV`.

Control flow: generated helpers use MIPS branch-and-label assembly inside `asm goto`. Each critical section stores the active descriptor, validates the ABI CPU/mm-cid field, performs data comparisons, commits through a final store, or exits through abort/cmpfail labels.

State and persistence: runtime writes are limited to caller memory and the thread-local `rseq_cs` field. Comparison failure versus abort return values are used by higher-level retry loops in `param_test.c`.

Dependencies and integration points: this file depends on `rseq-mips.h` for register-size selection, RSEQ signature emission, table layout, compare/load/store macros, and memory barriers. It is selected only through `rseq.h` on `__mips__`.

Risks and test signals: MIPS mode differences, delay slots, endian/word-size table encoding, and inline-assembly constraints are the main risks. Test signals are architecture build success and passing `run_param_test.sh` variants on MIPS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-mips-bits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-mips.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-mips.h

Purpose: `rseq-mips.h` is the architecture glue for MIPS rseq selftest helpers. It chooses the signature encoding for MIPS, microMIPS, and nanoMIPS, defines barriers and word-size-dependent instruction macros, and generates concrete helper variants.

Important APIs, types, and functions: it defines `RSEQ_SIG`, `rseq_smp_mb()`, `rseq_smp_rmb()`, `rseq_smp_wmb()`, acquire/release helpers, load/store operation macros, `RSEQ_ASM_DEFINE_TABLE()`, `RSEQ_ASM_DEFINE_EXIT_POINT()`, `RSEQ_ASM_STORE_RSEQ_CS()`, `RSEQ_ASM_CMP_CPU_ID()`, abort/cmpfail macros, and repeated inclusion of `rseq-mips-bits.h`.

Control flow: after architecture macro setup, the file includes the bits header for CPU-id relaxed/release, mm-cid relaxed/release, and CPU-id-none relaxed helpers. The generated code then supplies the symbols called by `rseq.h` wrappers.

State and persistence: it does not hold runtime data but defines ELF section records and TLS `rseq_cs` update sequences used at runtime. Memory-order macros are used by both generated critical sections and higher-level locking helpers.

Dependencies and integration points: selected by `rseq.h` on `__mips__`. It depends on MIPS assembler syntax and `_MIPS_SZLONG` for register-width selection. It integrates with `param_test.c` for MIPS correctness coverage.

Risks and test signals: signature handling across MIPS ISA modes is fragile. Incorrect word-size selection or branch delay behavior can invalidate critical-section ranges. Test signals are successful MIPS builds and passing injected rseq tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-mips.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-or1k-bits.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-or1k-bits.h

Purpose: `rseq-or1k-bits.h` provides OpenRISC generated rseq primitive implementations for the selftest helper stack.

Important APIs, types, and functions: it generates `rseq_cmpeqv_storev`, `rseq_cmpnev_storeoffp_load`, `rseq_addv`, `rseq_cmpeqv_cmpeqv_storev`, `rseq_offset_deref_addv`, `rseq_cmpeqv_trystorev_storev`, and `rseq_cmpeqv_trymemcpy_storev`. The presence of `RSEQ_ARCH_HAS_OFFSET_DEREF_ADDV` enables the membarrier test path in `param_test.c`.

Control flow: each helper emits OpenRISC `asm goto` using the parent header's compare/load/store, final-store, abort, and memcpy snippets. Success reaches a post-commit label; logical comparison failures and kernel aborts return distinct statuses.

State and persistence: the code updates the TLS active critical-section pointer and caller-supplied data. Offset-deref-add follows a pointer plus offset, loads the target value, adds an increment, and commits within the rseq range.

Dependencies and integration points: it depends on `rseq-or1k.h` temporary-register choices and memory-order macros, plus the common template header. It is included multiple times to build CPU-id and mm-cid variants.

Risks and test signals: OR1K branch delay slots and scratch register choices are sensitive. The manual byte-copy helper and offset-deref-add operation need architecture-specific test coverage. Test signals include successful OR1K builds, `-T r` membarrier coverage, and injection-heavy `param_test` runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-or1k-bits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-or1k-thread-pointer.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-or1k-thread-pointer.h

Purpose: `rseq-or1k-thread-pointer.h` implements thread-pointer retrieval for OpenRISC.

Important APIs, types, and functions: it exposes `static inline void *rseq_thread_pointer(void)`, implemented by copying OR1K register `r10` into a C pointer through inline assembly.

Control flow: the function has no branches. Header guards prevent duplicate definition.

State and persistence: no state is stored. The returned thread pointer is used by `rseq.c` and `rseq.h` to locate the current thread's rseq ABI area.

Dependencies and integration points: selected by `rseq-thread-pointer.h` when `__or1k__` is defined. It integrates with the self-owned TLS registration path in `rseq.c`.

Risks and test signals: the risk is ABI dependence on `r10` as the thread register. Incorrect register selection would make `rseq_get_abi()` point at invalid TLS. Registration success and correct CPU/mm-cid reads are the practical test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-or1k-thread-pointer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-or1k.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-or1k.h

Purpose: `rseq-or1k.h` defines the OpenRISC architecture layer for rseq helper generation.

Important APIs, types, and functions: it defines `RSEQ_SIG`, `rseq_smp_mb()`, `rseq_smp_rmb()`, `rseq_smp_wmb()`, acquire/release helpers, temporary registers, table/exit/abort macros, compare/load/store/add macros, final-store variants, a byte-copy loop, and offset-deref-add support.

Control flow: the header defines instruction snippets and includes `rseq-or1k-bits.h` for CPU-id relaxed/release, mm-cid relaxed/release, and CPU-id-none relaxed variants.

State and persistence: it contributes linker-visible critical-section descriptors and runtime TLS `rseq_cs` stores through generated helpers. Memory-order macros influence higher-level lock release behavior in `param_test.c`.

Dependencies and integration points: selected by `rseq.h` for `__or1k__`. It depends on OpenRISC instruction syntax and integrates with `rseq-or1k-thread-pointer.h`.

Risks and test signals: delay-slot handling is visible in several snippets and is a key correctness risk. The architecture also supports membarrier-related offset-deref-add, so `test_membarrier()` is a relevant signal in addition to the common parameter tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-or1k.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-ppc-bits.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-ppc-bits.h

Purpose: `rseq-ppc-bits.h` implements generated PowerPC rseq primitives for the selftest wrapper API.

Important APIs, types, and functions: generated functions are `rseq_cmpeqv_storev`, `rseq_cmpnev_storeoffp_load`, `rseq_addv`, `rseq_cmpeqv_cmpeqv_storev`, `rseq_cmpeqv_trystorev_storev`, and `rseq_cmpeqv_trymemcpy_storev`. It does not define offset-deref-add support.

Control flow: the functions emit PowerPC `asm goto` critical sections using CR7 comparisons and parent-defined load/store macros. Success commits through the final store and returns zero. Data mismatch returns a comparison-failure code, while kernel abort returns a retry/abort code after `RSEQ_INJECT_FAILED`.

State and persistence: it updates the current thread's active rseq descriptor and caller memory. The generated helpers assume the caller passes the CPU/mm-cid value already read from the ABI area.

Dependencies and integration points: depends on `rseq-ppc.h` for 32-bit/64-bit instruction selection, `lwsync`/`sync` barriers, table encoding, and scratch register usage. It feeds the generic wrappers used by `param_test.c`.

Risks and test signals: PowerPC 32-bit big-endian table encoding, register clobbering, and CR7 use are sensitive. Test signals are architecture build success and passing common rseq stress variants, especially compare-twice and release-mode buffer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-ppc-bits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-ppc-thread-pointer.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-ppc-thread-pointer.h

Purpose: `rseq-ppc-thread-pointer.h` returns the PowerPC thread pointer for locating TLS rseq state.

Important APIs, types, and functions: it exposes `static inline void *rseq_thread_pointer(void)`. On powerpc64 it reads register `r13`; on 32-bit PowerPC it reads register `r2`.

Control flow: there are only compile-time branches for 64-bit versus 32-bit. Runtime behavior is a register move through an empty inline assembly constraint.

State and persistence: no state is stored. The result is used to compute `rseq_offset` and to access `rseq_get_abi()` on each thread.

Dependencies and integration points: selected by `rseq-thread-pointer.h` under `__PPC__`. It integrates with `rseq.c` initialization and all PowerPC rseq helpers.

Risks and test signals: ABI mismatch around TLS register conventions would break all helper access. Successful rseq registration and current CPU reads on PowerPC are the validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-ppc-thread-pointer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-ppc.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-ppc.h

Purpose: `rseq-ppc.h` is the PowerPC architecture definition layer for rseq selftest helpers.

Important APIs, types, and functions: it defines the PowerPC trap signature `RSEQ_SIG`, `sync`/`lwsync` barriers, acquire/release helpers, 32-bit versus 64-bit load/store instruction macros, `RSEQ_ASM_DEFINE_TABLE()`, `RSEQ_ASM_DEFINE_EXIT_POINT()`, `RSEQ_ASM_STORE_RSEQ_CS()`, `RSEQ_ASM_CMP_CPU_ID()`, `RSEQ_ASM_DEFINE_ABORT()`, compare/store/load/add snippets, and a byte-copy helper.

Control flow: after selecting 32-bit or 64-bit instruction forms, it includes `rseq-ppc-bits.h` for CPU-id relaxed/release, mm-cid relaxed/release, and CPU-id-none relaxed helpers.

State and persistence: no standalone runtime state is owned here. It defines how descriptors are emitted into ELF sections and how generated helpers store `rseq_cs` in TLS and commit caller memory.

Dependencies and integration points: selected by `rseq.h` for `__PPC__`. It depends on PowerPC ABI register and endian assumptions, and its generated helpers are used by the parameter test suite.

Risks and test signals: risks include 32-bit versus 64-bit table layout, PC-relative address construction, and memory-order semantics. Test signals are successful PowerPC builds and passing selftests across CPU-id/mm-cid and relaxed/release variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-ppc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-riscv-bits.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-riscv-bits.h

Purpose: `rseq-riscv-bits.h` implements RISC-V generated rseq primitives.

Important APIs, types, and functions: it generates `rseq_cmpeqv_storev`, `rseq_cmpnev_storeoffp_load`, `rseq_addv`, `rseq_cmpeqv_cmpeqv_storev`, `rseq_offset_deref_addv`, `rseq_cmpeqv_trystorev_storev`, and `rseq_cmpeqv_trymemcpy_storev`. The offset-deref-add implementation enables membarrier testing on RISC-V.

Control flow: helpers are `asm goto` sections that store the active descriptor, validate current CPU/mm-cid, execute RISC-V load/compare/store or byte-copy sequences, and return through success, abort, or comparison-failure labels.

State and persistence: state changes are limited to TLS `rseq_cs` and caller memory. The helpers rely on fences from `rseq-riscv.h` for release-mode final stores and higher-level synchronization.

Dependencies and integration points: it depends on register-width macros, temporary register names, and operation snippets from `rseq-riscv.h`, plus the template header. `param_test.c` exercises it through all generic wrappers.

Risks and test signals: little-endian-only support is enforced in the parent header. Risks include fence placement, scratch register clobbers, byte-copy correctness, and offset-deref-add commit semantics. Passing `run_param_test.sh`, including `-T r`, is the main test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-riscv-bits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-riscv.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-riscv.h

Purpose: `rseq-riscv.h` defines the RISC-V architecture-specific rseq layer.

Important APIs, types, and functions: it selects `RSEQ_SIG`, enforces little-endian builds, picks `ld/sd` versus `lw/sw` through `__riscv_xlen`, defines `RISCV_FENCE`-based memory barriers, acquire/release helpers, table/exit/abort macros, CPU compare, load/store/add snippets, byte-copy helper, and offset-deref-add operation.

Control flow: it expands `rseq-riscv-bits.h` for CPU-id relaxed/release, mm-cid relaxed/release, and CPU-id-none relaxed variants.

State and persistence: it defines descriptor and active-CS publication behavior but owns no runtime state directly. Generated helpers update TLS and caller memory according to rseq semantics.

Dependencies and integration points: selected by `rseq.h` on `__riscv`. It depends on `<asm/fence.h>`, endian definitions, and RISC-V assembler syntax. It integrates with `param_test.c` and membarrier coverage.

Risks and test signals: the signature uses an uncommon privileged CSR instruction instead of `ebreak`, making exact encoding important. Register-width and endian constraints are key. Passing RISC-V CPU-id/mm-cid tests and membarrier restart tests validate this layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-riscv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-s390-bits.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-s390-bits.h

Purpose: `rseq-s390-bits.h` provides s390 generated rseq primitive implementations.

Important APIs, types, and functions: it generates `rseq_cmpeqv_storev`, `rseq_cmpnev_storeoffp_load`, `rseq_addv`, `rseq_cmpeqv_cmpeqv_storev`, `rseq_cmpeqv_trystorev_storev`, and `rseq_cmpeqv_trymemcpy_storev`. It does not provide offset-deref-add support.

Control flow: generated helpers emit s390 `asm goto` critical sections. They publish the descriptor address, compare CPU/mm-cid, execute long-word load/compare/store sequences, and branch to abort or cmpfail labels as needed.

State and persistence: only TLS `rseq_cs` and caller-provided memory are modified. Return values tell higher-level retry loops whether the operation committed, saw a data mismatch, or aborted due to rseq restart.

Dependencies and integration points: it depends on `rseq-s390.h` for `trap4` signature handling, `bcr` barriers, long-word instruction aliases, table macros, and jump syntax. It feeds the generic `rseq.h` wrappers.

Risks and test signals: the main risks are long-word instruction assumptions, clobber lists, and correct s390 jump/label placement. Test signals are successful s390 builds and passing parameter tests, including injection and compare-twice modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-s390-bits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-s390.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-s390.h

Purpose: `rseq-s390.h` is the s390 architecture layer for rseq selftest helpers.

Important APIs, types, and functions: it defines `RSEQ_SIG` using `trap4`, `rseq_smp_mb()`, `rseq_smp_rmb()`, `rseq_smp_wmb()`, acquire/release helpers, long-word instruction aliases, table/exit macros, `RSEQ_ASM_STORE_RSEQ_CS()`, `RSEQ_ASM_CMP_CPU_ID()`, `RSEQ_ASM_DEFINE_ABORT()`, and `RSEQ_ASM_DEFINE_CMPFAIL()`.

Control flow: the header prepares s390 assembly snippets and includes `rseq-s390-bits.h` for CPU-id relaxed/release, mm-cid relaxed/release, and CPU-id-none relaxed generated helpers.

State and persistence: no direct runtime state. The macros define how active critical-section pointers are stored in TLS and how critical-section descriptors are emitted for kernel/debugger use.

Dependencies and integration points: selected by `rseq.h` for `__s390__`. It integrates with `param_test.c`, `syscall_errors_test.c`, and the shared registration layer in `rseq.c`.

Risks and test signals: alternate user address-space behavior affects syscall error tests, and this header's trap signature must remain safe and recognizable. Passing s390 builds and parameter tests are key validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-s390.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-slice-hist.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-slice-hist.py

Purpose: `rseq-slice-hist.py` is an offline trace analysis helper for rseq time-slice extension experiments. It reads `trace.dat` produced by `trace-cmd` hrtimer events and prints per-task histograms for rseq slice timer cancellation latency and expiration.

Important APIs, types, and functions: it imports `tracecmd.Trace`, defines `load_kallsyms()`, `OnlineHarmonicMean`, `handle_start()`, `handle_cancel()`, and `handle_expire()`. Global dictionaries `pending`, `histograms`, and `ohms` track outstanding timers, latency buckets, and per-command harmonic means.

Control flow: at startup it loads `/proc/kallsyms`, opens `trace.dat`, iterates events per CPU, and routes `hrtimer_start`, `hrtimer_cancel`, and `hrtimer_expire_entry` records. Starts whose function symbol contains `rseq_slice_expired` enter `pending`. Cancels compute duration and bucket counts. Expirations add an `EXPIRED` bucket.

State and persistence: state is in memory only and is keyed by hrtimer pointer and task command name. The script reads but does not modify kernel symbol state or trace files.

Dependencies and integration points: it depends on the Python `tracecmd` module, a readable `trace.dat`, and optionally readable `/proc/kallsyms`. It is complementary to `slice_test.c` and the comment documents the intended `trace-cmd record` invocation.

Risks and test signals: direct `ksyms[addr]` lookup can raise `KeyError` if symbols are unavailable or addresses are hidden. `handle_expire()` records histograms but not harmonic means, while the final print unconditionally reads `ohms[comm]`, so tasks with only expirations can fail. Useful output is a populated histogram with latency buckets and mean values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-slice-hist.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-thread-pointer.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-thread-pointer.h

Purpose: `rseq-thread-pointer.h` dispatches to the architecture-specific implementation of `rseq_thread_pointer()`.

Important APIs, types, and functions: it does not define a function itself; it includes `rseq-x86-thread-pointer.h`, `rseq-ppc-thread-pointer.h`, `rseq-or1k-thread-pointer.h`, or `rseq-generic-thread-pointer.h` based on target macros.

Control flow: compile-time selection chooses the appropriate include. Runtime behavior is supplied by the selected header.

State and persistence: no runtime state. The chosen thread-pointer function is foundational for computing and using `rseq_offset`.

Dependencies and integration points: included by `rseq.h` before `rseq_get_abi()` is defined. It is used by `rseq.c` constructor logic to either compute a self-owned TLS offset or use libc-provided offset symbols.

Risks and test signals: wrong architecture dispatch causes invalid TLS access. Test signals include successful compilation on each supported architecture and successful registration/current CPU tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-thread-pointer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-x86-bits.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-x86-bits.h

Purpose: `rseq-x86-bits.h` implements the generated x86 restartable-sequence primitives for both x86-64 and i386.

Important APIs, types, and functions: for x86-64 it generates `rseq_cmpeqv_storev`, `rseq_cmpnev_storeoffp_load`, `rseq_addv`, `rseq_offset_deref_addv`, `rseq_cmpeqv_cmpeqv_storev`, `rseq_cmpeqv_trystorev_storev`, and `rseq_cmpeqv_trymemcpy_storev`. For i386 it generates the same common set except offset-deref-add is not present in the scanned lower half. `RSEQ_ARCH_HAS_OFFSET_DEREF_ADDV` is defined for x86-64, enabling membarrier tests.

Control flow: each helper uses `asm goto`, stores `rseq_cs`, compares the ABI CPU/mm-cid field through the FS or GS TLS segment, performs operation-specific checks and writes, and exits through success, cmpfail, or abort labels. Optional `RSEQ_COMPARE_TWICE` adds duplicate validation labels to catch compiler/kernel consistency problems.

State and persistence: the helpers modify TLS `rseq_cs` and caller-provided memory. They use active CS descriptors emitted into `__rseq_cs` and pointer arrays for kernel and debugger consumption.

Dependencies and integration points: depends on `rseq-x86.h` for signatures, segment selectors, memory barriers, table layout, and abort/cmpfail macros. Called through wrappers in `rseq.h` by `param_test.c`.

Risks and test signals: x86 inline asm has separate 32-bit and 64-bit paths, with known compiler constraints around TLS memory operands. The memcpy helper copies bytewise within a critical section and must keep final store placement exact. Passing x86 default, compare-twice, mm-cid, release, and membarrier tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-x86-bits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-x86-thread-pointer.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-x86-thread-pointer.h

Purpose: `rseq-x86-thread-pointer.h` implements `rseq_thread_pointer()` for x86 targets.

Important APIs, types, and functions: it exposes `static inline void *rseq_thread_pointer(void)`. GCC 11.1 and newer use `__builtin_thread_pointer()`. Older compiler paths read `%fs:0` on x86-64 or `%gs:0` on i386.

Control flow: compile-time branches select builtin versus inline assembly and 64-bit versus 32-bit segment register. Runtime behavior is a simple thread-pointer load.

State and persistence: no state is stored. The return value anchors all TLS rseq ABI access.

Dependencies and integration points: selected by `rseq-thread-pointer.h` for `__x86_64__` or `__i386__`. It depends on glibc feature macros for `__GNUC_PREREQ`.

Risks and test signals: wrong segment selection or compiler-version detection breaks `rseq_get_abi()`. Test signals are successful registration and current CPU access on old and new GCC builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-x86-thread-pointer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-x86.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-x86.h

Purpose: `rseq-x86.h` supplies the x86 architecture layer for rseq selftest helpers.

Important APIs, types, and functions: it defines `RSEQ_SIG`, CPU/rseq/mm-cid offsets, `RSEQ_ASM_TP_SEGMENT`, memory barriers, acquire/release helpers, x86-64 and i386 descriptor table encodings, exit-point macros, `RSEQ_ASM_STORE_RSEQ_CS()`, `RSEQ_ASM_CMP_CPU_ID()`, abort and cmpfail section macros, and the include-time expansion of `rseq-x86-bits.h`.

Control flow: separate compile-time branches define x86-64 versus i386 assembly forms. The file then generates CPU-id relaxed/release, mm-cid relaxed/release, and CPU-id-none relaxed helpers.

State and persistence: no standalone state. Its macros store descriptor addresses into TLS and emit `__rseq_cs`, `__rseq_cs_ptr_array`, `__rseq_exit_point_array`, and failure sections. The barriers are also used by higher-level lock/unlock helpers.

Dependencies and integration points: selected by `rseq.h` for x86 targets. It integrates with `rseq-x86-thread-pointer.h`, `rseq.c`, and the param test runner.

Risks and test signals: the code works around GCC asm-goto/TLS operand issues, so compiler behavior is a risk. i386 has stronger barrier macros than x86-64. Test signals include passing optimized, legacy, compare-twice, mm-cid, and injection tests on x86.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-x86.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq.c

Purpose: `rseq.c` is the runtime registration and discovery implementation behind `rseq.h`. It supports both libc-owned rseq areas and a selftest-owned TLS fallback.

Important APIs, types, and functions: exported state includes `ptrdiff_t rseq_offset`, `unsigned int rseq_size`, and `unsigned int rseq_flags`. Public functions are `rseq_available()`, `__rseq_register_current_thread()`, `rseq_unregister_current_thread()`, `rseq_fallback_current_cpu()`, and `rseq_fallback_current_node()`. Internal helpers are `sys_rseq()`, `sys_getcpu()`, `get_rseq_kernel_feature_size()`, constructor `rseq_init()`, and destructor `rseq_exit()`.

Control flow: the constructor first checks weak libc symbols `__rseq_offset`, `__rseq_size`, and `__rseq_flags`, retrying with `dlsym(RTLD_NEXT, ...)` when weak values are absent. If libc owns rseq, it mirrors libc offset, size, and flags with compatibility handling for 20/32 byte historical sizes. Otherwise it computes the offset to an internal `__thread union rseq_tls` area and marks ownership. Registration uses auxv `AT_RSEQ_FEATURE_SIZE`/`AT_RSEQ_ALIGN` to choose allocation size and invokes `__NR_rseq`. Unregistration calls the same syscall with `RSEQ_ABI_FLAG_UNREGISTER`.

State and persistence: `__rseq` is per-thread TLS and initially has `cpu_id` set to `RSEQ_ABI_CPU_ID_UNINITIALIZED`. Global process state records ownership, active size, allocation size, offset, and flags. Destructor invalidates self-owned global state.

Dependencies and integration points: depends on syscall numbers, auxv constants, dlfcn, scheduler fallback APIs, `kselftest.h`, and `rseq.h`. All selftest programs link this file to use registration and current CPU/node helpers.

Risks and test signals: libc interposition and feature-size compatibility are subtle. A process-wide successful registration followed by a later thread failure aborts as incoherent. Test signals include `basic_test`, `legacy_check`, `syscall_errors_test`, `param_test`, and any test that runs with `GLIBC_TUNABLES=glibc.pthread.rseq=0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq.h

Purpose: `rseq.h` is the public userspace helper API for the rseq selftests. It defines generic wrappers, memory-order modes, per-cpu indexing modes, ABI accessors, injection hooks, and architecture dispatch.

Important APIs, types, and functions: exposed enums are `enum rseq_mo` and `enum rseq_percpu_mode`. Key inline APIs are `rseq_get_abi()`, `rseq_register_current_thread()`, `rseq_current_cpu_raw()`, `rseq_cpu_start()`, `rseq_current_cpu()`, `rseq_node_id_available()`, `rseq_current_node_id()`, `rseq_mm_cid_available()`, `rseq_current_mm_cid()`, `rseq_clear_rseq_cs()`, `rseq_prepare_unload()`, and wrappers for all rseq primitives. External functions and variables are supplied by `rseq.c`.

Control flow: architecture selection includes the correct `rseq-*.h` based on compiler target. Generic wrappers validate memory ordering and per-cpu mode, then dispatch to generated names such as `_relaxed_cpu_id`, `_release_mm_cid`, or `_relaxed`. Unsupported memory-order/mode combinations return `-1`.

State and persistence: the header reads and writes the current thread's `struct rseq_abi` through `rseq_thread_pointer() + rseq_offset`. Feature availability for node ID and mm CID is based on `rseq_size`. `rseq_prepare_unload()` clears the active critical-section pointer so code or descriptor memory can be reclaimed safely.

Dependencies and integration points: depends on `rseq-abi.h`, `compiler.h`, thread-pointer headers, and one architecture header. It is included by all rseq selftest C files and is the contract between high-level tests and low-level assembly.

Risks and test signals: wrapper dispatch must stay aligned with generated symbol names. Returning `-1` for unsupported modes is expected but can cause tests to spin or fail if the caller requested an impossible mode. Test signals are broad: successful builds on all architectures and passing all C selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/run_legacy_check.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/run_legacy_check.sh

Purpose: `run_legacy_check.sh` is a small wrapper that runs the `legacy_check` binary with glibc rseq auto-registration disabled.

Important APIs, types, and functions: it sets `GLIBC_TUNABLES="${GLIBC_TUNABLES:-}:glibc.pthread.rseq=0"` for the command invocation and executes `./legacy_check`.

Control flow: straight-line shell execution. The script's exit status is the binary's exit status.

State and persistence: it mutates only the environment for the child process; no files are written.

Dependencies and integration points: depends on the built `legacy_check` executable and glibc honoring the `glibc.pthread.rseq=0` tunable. It is part of the kselftest generated runner set for rseq.

Risks and test signals: if glibc ignores the tunable or the shell does not preserve intended environment syntax, the test may check the wrong ownership path. A zero exit from `legacy_check` is the signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/run_legacy_check.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/run_param_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/run_param_test.sh

Purpose: `run_param_test.sh` orchestrates the broad rseq parameter test matrix.

Important APIs, types, and functions: it computes `NR_CPUS` from `/proc/cpuinfo`, sets `NR_THREADS` to six times CPU count, defines `TEST_LIST`/`TEST_NAME`, exports `GLIBC_TUNABLES` to disable glibc rseq registration, defines `do_tests()`, and defines `inject_blocking()`.

Control flow: it runs default parameters for every test type against `param_test`, `param_test_compare_twice`, `param_test_mm_cid`, and `param_test_mm_cid_compare_twice`. It then injects fixed delay loops at injection points 1 through 9. Next it runs legacy-mode blocking injections with yield, signal, and sleep at 25%, 50%, and 100%. Finally it probes `./check_optimized`; if supported, it repeats blocking injections in optimized mode.

State and persistence: state is shell variables and child-process environment only. Extra command-line arguments are appended to every binary invocation through `EXTRA_ARGS`.

Dependencies and integration points: depends on all four built param-test variants and `check_optimized`. It is the main integration point for `param_test.c` and architecture helper coverage.

Risks and test signals: it assumes `/proc/cpuinfo` has `processor` lines and that arrays are supported by `/bin/bash`. A single failing child exits the whole script with status 1. Useful signals are the printed phase names and final zero exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/run_param_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/run_syscall_errors_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/run_syscall_errors_test.sh

Purpose: `run_syscall_errors_test.sh` executes the syscall error validation binary in an environment where glibc does not pre-register rseq.

Important APIs, types, and functions: it sets `GLIBC_TUNABLES="${GLIBC_TUNABLES:-}:glibc.pthread.rseq=0"` and runs `./syscall_errors_test`.

Control flow: straight-line shell wrapper. The child program owns the validation logic and exit status.

State and persistence: no files are written. Only child environment state is adjusted.

Dependencies and integration points: depends on `syscall_errors_test` being built and on the glibc tunable being available. It integrates the C syscall validation into kselftest runners.

Risks and test signals: if libc already owns rseq despite the tunable, expected EBUSY/EINVAL sequences may differ. The test signal is a zero exit status from `syscall_errors_test`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/run_syscall_errors_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/run_timeslice_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/run_timeslice_test.sh

Purpose: `run_timeslice_test.sh` runs the rseq time-slice extension test when optimized rseq mode is available.

Important APIs, types, and functions: it exports `GLIBC_TUNABLES` with `glibc.pthread.rseq=0`, invokes `./check_optimized`, and then runs `./slice_test`.

Control flow: the script disables glibc rseq registration, checks optimized-mode support, prints a skip message and exits zero if unsupported, otherwise executes `slice_test`.

State and persistence: only environment state is changed. No persistent output is generated beyond stdout/stderr.

Dependencies and integration points: depends on `check_optimized`, `slice_test`, and kernel support for the optimized rseq mode and slice extension. It is the runner counterpart to `slice_test.c`.

Risks and test signals: unsupported optimized mode is treated as a skip rather than failure. Real failures are nonzero exits from `slice_test`. The output counters printed by `slice_test` are useful diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/run_timeslice_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/slice_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/slice_test.c

Purpose: `slice_test.c` validates the rseq time-slice extension using the kselftest harness. It requests short slice extensions while a noise thread creates intermittent CPU pressure, then reports whether requests succeed, yield, schedule out, race, or abort.

Important APIs, types, and functions: it defines `struct noise_params`, a `slice_ext` fixture, three fixture variants, `elapsed()`, `noise_thread()`, fixture setup/teardown, and `TEST_F(slice_ext, slice_test)`. It uses `rseq_get_abi()`, `__rseq_register_current_thread()`, `RSEQ_READ_ONCE()`, `RSEQ_WRITE_ONCE()`, `prctl(PR_RSEQ_SLICE_EXTENSION, ...)`, and `syscall(__NR_rseq_slice_yield)`.

Control flow: setup registers rseq in nolibc mode, enables the slice extension with `prctl`, pins the test to one nonzero allowed CPU, and starts a noise thread. The test loop runs for the variant duration, writes `slice_ctrl.request`, busy-waits for the target slice span, clears pending requests, handles granted slices by either yielding or forcing an abort path, and counts outcomes. Teardown stops and joins the noise thread.

State and persistence: state lives in the fixture, the noise thread's `run` flag, and the current thread's `rseq_abi.slice_ctrl`. The kernel may set and clear `slice_ctrl.granted`; userspace writes `request`.

Dependencies and integration points: depends on kselftest harness macros, pthreads, scheduler affinity, `prctl` slice extension constants, the rseq syscall stack, and optional fallback syscall numbers/constants for newer kernel interfaces.

Risks and test signals: this is timing-sensitive and can skip when rseq or the extension is unsupported. It assumes at least one allowed CPU greater than zero for pinning. Test signals are successful harness completion and printed counters for total, success, yielded, aborted, scheduled, and raced events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/slice_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/syscall_errors_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/syscall_errors_test.c

Purpose: `syscall_errors_test.c` verifies expected `errno` behavior for invalid and duplicate `rseq` syscall operations.

Important APIs, types, and functions: it defines `sys_rseq()` and `main()`. It uses `rseq_get_abi()`, `rseq_available()`, `RSEQ_SIG`, `RSEQ_ABI_FLAG_UNREGISTER`, and direct `syscall(__NR_rseq, ...)`.

Control flow: `main()` skips to error if the syscall is unavailable, then exercises invalid registration flags, unaligned ABI address, invalid size, optionally invalid address on most 64-bit builds, successful registration, double registration, unregister with wrong signature, successful unregister, and double unregister. Each step captures `errno`, prints a diagnostic, and fails if the observed errno differs from the expected value.

State and persistence: state is the current thread's registration status and local errno snapshots. No persistent files are written.

Dependencies and integration points: depends on glibc `strerrorname_np()`, syscall availability, and the local rseq ABI allocation from `rseq.c`. `run_syscall_errors_test.sh` disables glibc rseq ownership before invoking it.

Risks and test signals: architecture-specific address-space behavior is handled by skipping the EFAULT invalid-address test on 32-bit userspace and s390 alternate address-space cases. A zero exit means all expected syscall errors matched.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/syscall_errors_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rtc/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rtc/Makefile

Purpose: this Makefile wires the RTC kselftest directory into the kernel selftests build system.

Important APIs, types, and functions: it appends to `CFLAGS` with optimization, linker no-as-needed, warnings, and the in-tree UAPI include path. It appends to `LDLIBS` with `-lrt`, `-lpthread`, and `-lm`. It sets `TEST_GEN_PROGS = rtctest`, `TEST_FILES := settings`, and includes `../lib.mk`.

Control flow: make reads these variables and delegates build/install/run behavior to the common selftests `lib.mk`. `rtctest.c` is compiled into the generated test program, and `settings` is copied or packaged as a test file.

State and persistence: build outputs are generated by kselftest infrastructure, not by this file directly. The Makefile itself has no runtime state.

Dependencies and integration points: depends on the parent selftests make infrastructure, the RTC test source in the same directory, realtime/pthread/math libraries, and UAPI headers under `$(top_srcdir)/usr/include`.

Risks and test signals: `-Wl,-no-as-needed` and library ordering matter for some toolchains. Missing `top_srcdir` or unavailable libraries can break builds. Test signals are successful `make` generation of `rtctest` and inclusion of `settings` in the selftest artifact set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rtc/Makefile -->
