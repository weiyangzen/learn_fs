# sources/distributed-fs/ceph-client/arch/s390/kernel/rethook.c

Purpose: provides s390 architecture callbacks for the generic rethook infrastructure used by kretprobes/fprobe-style return hooks.

Important APIs/functions: `arch_rethook_prepare()` saves the original return address and frame pointer from `%r14` and `%r15`, then replaces `%r14` with `arch_rethook_trampoline`. `arch_rethook_fixup_return()` restores the real return address into `%r14`. `arch_rethook_trampoline_callback()` calls `rethook_trampoline_handler(regs, regs->gprs[15])`. The trampoline symbol is declared elsewhere and marked not probeable here.

Control flow: when a probed function is prepared, its link register return path is redirected to the trampoline. When the trampoline runs, it calls back into generic rethook handling with the current frame pointer; generic code decides the correct return address, and fixup writes that address back into the register set.

State and persistence: per-hook state is stored in the generic `struct rethook_node` fields `ret_addr` and `frame`. The file itself owns no global state.

Dependencies and integration points: depends on `linux/rethook.h`, `linux/kprobes.h`, s390 `pt_regs` register numbering, the assembly `arch_rethook_trampoline`, and generic rethook/kprobe no-probe annotations.

Risks: s390 return conventions use `%r14`; saving or restoring the wrong register would corrupt returns. The trampoline and callbacks are marked `NOKPROBE_SYMBOL` to avoid recursive probing. Stack frame assumptions must match the low-level trampoline.

Test signals: kretprobe or fprobe return hooks should fire and return to the original caller, nested return hooks should unwind correctly, and kprobe blacklisting should prevent probing the trampoline/callback path.
