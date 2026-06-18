<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/sys_hwprobe.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/sys_hwprobe.S

Purpose: Provides a vDSO-local syscall wrapper symbol for `riscv_hwprobe`.

Important APIs/types/functions: Defines `riscv_hwprobe`.

Control flow: Loads the hwprobe syscall number, executes `ecall`, and returns the kernel result. `vdso/hwprobe.c` calls this when the cache fast path cannot answer.

State and persistence: No local state.

Dependencies and integration points: Tied to `__vdso_riscv_hwprobe()` fallback logic and syscall ABI.

Risks: Wrong symbol visibility or syscall number breaks vDSO fallback.

Test signals: vDSO hwprobe fallback tests for non-homogeneous masks and unsupported flags.

Source read size: 19 lines, 326 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/sys_hwprobe.S -->
