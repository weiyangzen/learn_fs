# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-arm.h

Purpose: `rseq-arm.h` supplies ARM-specific rseq ABI constants, memory barriers, descriptor table macros, abort signatures, and include-time template expansion for 32-bit ARM selftests.

Important APIs, types, and functions: it defines `RSEQ_SIG`, `rseq_smp_mb()`, `rseq_smp_rmb()`, `rseq_smp_wmb()`, `rseq_smp_load_acquire()`, `rseq_smp_acquire__after_ctrl_dep()`, `rseq_smp_store_release()`, `RSEQ_ASM_DEFINE_TABLE()`, `RSEQ_ASM_DEFINE_EXIT_POINT()`, `RSEQ_ASM_STORE_RSEQ_CS()`, `RSEQ_ASM_CMP_CPU_ID()`, `RSEQ_ASM_DEFINE_ABORT()`, and `RSEQ_ASM_DEFINE_CMPFAIL()`.

Control flow: after defining ARM assembly building blocks, the file includes `rseq-arm-bits.h` five times: CPU-id relaxed, CPU-id release, mm-cid relaxed, mm-cid release, and CPU-id-none relaxed. This generates the concrete function names expected by `rseq.h`.

State and persistence: the macros describe how the active rseq critical-section descriptor is written into TLS and how the linker-visible `__rseq_cs`, `__rseq_cs_ptr_array`, and exit-point sections are populated. Runtime state is still owned by the generated helpers and kernel rseq handling.

Dependencies and integration points: it is selected by `rseq.h` for `__ARMEL__`. It uses ARM `dmb` barriers and a signature chosen around ARM endian/code-mode constraints. `param_test.c` relies on the generated helpers when built on ARM.

Risks and test signals: the highest risk is signature and endian mismatch, because the kernel expects a safe uncommon trap pattern. Table encoding uses 32-bit words for 64-bit ABI fields, so ordering and zero-extension must remain correct. Test signals come from build success on ARM and rseq operation/injection tests.
