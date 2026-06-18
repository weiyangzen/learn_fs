# sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/rethook.c

Purpose: Provides RISC-V architecture glue for generic rethook/kretprobe return interception.

Important APIs/types/functions: Implements `arch_rethook_trampoline_callback()` and `arch_rethook_prepare()`.

Control flow: Kretprobe setup calls `arch_rethook_prepare()` to save the original return address and replace it with `arch_rethook_trampoline`. When the function returns, the trampoline builds a register frame and calls `arch_rethook_trampoline_callback()`, which runs generic rethook handlers and returns the real target address.

State and persistence: Per-call rethook nodes store original return addresses; `pt_regs` is transient during trampoline handling.

Dependencies and integration points: Depends on generic rethook, kprobes/kretprobes, `rethook_trampoline.S`, and RISC-V return address conventions.

Risks and test signals: Return address replacement must preserve normal call ABI and handle mcount/ftrace interactions. Test kretprobes on normal and traced functions, nested returns, faulting handlers, and module functions.
