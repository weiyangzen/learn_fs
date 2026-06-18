<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/rt_sigreturn.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/rt_sigreturn.S

Purpose: Provides the vDSO `__vdso_rt_sigreturn` trampoline.

Important APIs/types/functions: Defines `__vdso_rt_sigreturn`.

Control flow: Loads the `rt_sigreturn` syscall number and executes `ecall`; normal control does not return except through restored signal context.

State and persistence: Operates on the user signal frame through the kernel syscall path; no local state.

Dependencies and integration points: Signal setup writes this symbol address into user RA for MMU systems.

Risks: The trampoline address and instruction sequence are ABI-critical for signal return, unwinders, and CFI shadow-stack handling.

Test signals: Signal delivery/return, unwinder recognition, vDSO symbol resolution, and malformed signal frame handling.

Source read size: 20 lines, 389 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/rt_sigreturn.S -->
