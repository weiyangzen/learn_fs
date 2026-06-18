# sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/rethook_trampoline.S

Purpose: Implements the RISC-V assembly trampoline entered when a probed function returns through rethook.

Important APIs/types/functions: Defines `arch_rethook_trampoline`.

Control flow: The trampoline saves a full register frame compatible with `pt_regs`, calls `arch_rethook_trampoline_callback()`, receives the real return address, restores registers, and jumps to the original caller.

State and persistence: Uses stack-resident saved registers only. Persistent per-return state is held by generic rethook nodes.

Dependencies and integration points: Depends on `pt_regs` offsets, RISC-V ABI, `rethook.c`, and generic kretprobe/rethook handling.

Risks and test signals: Register save/restore omissions or stack alignment bugs corrupt returning functions. Test kretprobes on functions with many live registers, nested returns, interrupt-disabled contexts, and ftrace/mcount combinations.
