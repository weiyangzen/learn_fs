## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32/sigreturn.S

Purpose: provides 32-bit vDSO signal-return trampolines and unwind CFI for normal and realtime signal frames.

Important APIs/symbols: `__kernel_sigreturn`, `__kernel_rt_sigreturn`, `vdso32_sigreturn_landing_pad`, `vdso32_rt_sigreturn_landing_pad`, and `STARTPROC_SIGNAL_FRAME`. It uses `__NR_sigreturn`, `__NR_rt_sigreturn`, IA32 sigcontext offsets, and DWARF CFI macros.

Control flow: `__kernel_sigreturn` pops the signal frame return code into EAX, loads `sigreturn`, and executes `int $0x80`; `__kernel_rt_sigreturn` loads `rt_sigreturn` and executes `int $0x80`. Both land on `ud2a` pads after the syscall instruction for kernel recognition and unwind/debug behavior.

State/persistence: no owned data; it encodes CFI and fixed instruction bytes in the vDSO ABI. The comments document a libgcc unwinder workaround that requires byte-exact sequences.

Integration points: signal delivery, unwinding libraries, `arch_syscall_is_vdso_sigreturn()`, 32-bit syscall entry, and the vdso32 linker version script.

Risks: instruction sequence changes can break legacy libgcc unwinding and signal return recognition. Test signals include 32-bit signal/unwind tests, gdb backtraces through signal frames, byte-sequence inspection, and syscall restart tests.
