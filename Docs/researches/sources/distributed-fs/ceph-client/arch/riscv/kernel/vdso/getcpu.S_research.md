<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/getcpu.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/getcpu.S

Purpose: Provides the vDSO `__vdso_getcpu` entry point.

Important APIs/types/functions: Defines `__vdso_getcpu`.

Control flow: Executes the `getcpu` syscall through `ecall` using the architecture syscall number and returns the kernel result.

State and persistence: No local state.

Dependencies and integration points: Exported by vDSO to libc and userspace; kernel side dispatch comes from generic getcpu syscall support.

Risks: vDSO register ABI mismatch causes userspace-visible wrong CPU/node values.

Test signals: libc `sched_getcpu()`/getcpu tests and syscall fallback comparison.

Source read size: 22 lines, 431 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/getcpu.S -->
