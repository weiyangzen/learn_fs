# sources/distributed-fs/ceph-client/arch/arm64/kernel/ptrace.c

Purpose: this file implements ARM64 ptrace register access, hardware breakpoint/watchpoint regsets, native and compat regset views, PAC/tagged-address/POE/GCS state access, MTE tag ptrace requests, syscall tracing, and user register validation.

Important APIs and state: public helpers include `regs_query_register_offset()`, `regs_get_kernel_stack_nth()`, `ptrace_disable()`, `flush_ptrace_hw_breakpoint()`, `ptrace_hw_copy_thread()`, `task_user_regset_view()`, `arch_ptrace()`, `compat_arch_ptrace()`, `syscall_trace_enter()`, `syscall_trace_exit()`, and `valid_user_regs()`. The main regset tables are `aarch64_regsets`, `aarch32_regsets`, and `aarch32_ptrace_regsets`. Optional regsets expose FPMR, SVE, streaming SVE, ZA, ZT, PAC masks/keys, tagged-address control, POE, and GCS.

Control flow: get/set handlers synchronize live architectural state before exposing or mutating it. FPSIMD/SVE/SME setters flush task FP state and allocate vector storage as needed. SVE/SME headers validate vector length and payload layout, rejecting mismatched actual VL. Hardware breakpoint regsets lazily allocate perf breakpoints, validate control fields by note type, and use nospec index masking. Compat ptrace converts AArch32 GPR, VFP, TLS, syscall, and hardware breakpoint requests into regset/perf operations.

State and persistence: ptrace reads/writes `task_pt_regs()`, `thread.uw.fpsimd_state`, `thread.sve_state`, `thread.sme_state`, `thread.keys_user`, `thread.sctlr_user`, `thread.por_el0`, `thread.gcs_*`, and `thread.debug` breakpoint arrays. PAC key checkpoint/restore regsets directly serialize 128-bit key halves when configured.

Dependencies and integration: depends on generic ptrace/regset, perf hardware breakpoints, FPSIMD/SVE/SME, PAC, MTE, GCS, POE, audit, seccomp, syscall tracepoints, rseq, and signal register validation. `process.c` and `signal.c` share validation and state synchronization expectations.

Risks: ptrace is a privileged ABI surface; setters must reject invalid pstate, unsupported features, bad vector layouts, unknown GCS flags, and invalid breakpoints. Syscall tracing intentionally clobbers x7/r12 during stops and restores it, which is ABI-observable. Failure to flush/sync FP state can resurrect stale vector data.

Test signals: kernel selftests under `tools/testing/selftests/arm64/abi` and `fp`, ptrace syscall-stop tests, MTE tag peek/poke, hardware breakpoint tests, compat ptrace tests, and checkpoint/restore PAC key tests.
