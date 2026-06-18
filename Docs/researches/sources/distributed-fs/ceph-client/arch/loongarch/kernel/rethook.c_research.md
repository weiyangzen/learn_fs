## sources/distributed-fs/ceph-client/arch/loongarch/kernel/rethook.c

### Purpose
`rethook.c` implements the LoongArch architecture glue for generic return hooks. It saves a function's original return address into a `rethook_node`, replaces the live return address with the architecture trampoline, and dispatches trampoline callbacks to the generic rethook handler.

### Important APIs, Types, And Functions
It defines `arch_rethook_trampoline_callback` and `arch_rethook_prepare`, and marks `arch_rethook_trampoline` as not probeable. It uses `struct rethook_node`, `struct pt_regs`, and `rethook_trampoline_handler`.

### Control Flow
Preparation records `regs->regs[1]` as `rhn->ret_addr`, clears `rhn->frame`, and overwrites `regs->regs[1]` with the assembly trampoline address. When the instrumented function returns, the trampoline builds `pt_regs` and calls `arch_rethook_trampoline_callback`, which asks generic rethook code for the real return address.

### State, Persistence, And Dependencies
Per-invocation state persists in the `rethook_node` until generic rethook handling completes. It depends on LoongArch using register 1 as return address, the assembly trampoline preserving registers, and kprobes/rethook recursion avoidance.

### Integration Points
Generic rethook and kretprobe infrastructure call this file. `rethook_trampoline.S` provides the actual control-transfer and register-save code.

### Risks
Replacing the return address is control-flow sensitive; any mismatch between `pt_regs` saved by assembly and generic rethook expectations can return to the wrong location. The `mcount` argument is ignored, so future mcount-specific behavior would need explicit handling.

### Test Signals
Run kretprobe/rethook tests on normal functions, nested returns, and functions with live argument/return registers. Confirm the trampoline is absent from kprobeable symbols and that original return addresses are restored.
