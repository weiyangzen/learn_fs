# sources/distributed-fs/ceph-client/arch/arm64/kernel/probes/kprobes_trampoline.S

Purpose: this assembly file defines the ARM64 kretprobe trampoline target. Kretprobes replace a function return address with this symbol so a breakpoint exception can route return handling through the kprobe core.

Important symbols: `__kretprobe_trampoline` is emitted with `SYM_CODE_START/END`. It executes `brk #KRETPROBES_BRK_IMM`, then `ASM_BUG()` as a non-return fallback.

Control flow: normal execution should never proceed past the `brk`. The exception is recognized by `kretprobe_brk_handler()` in `kprobes.c`, which checks that `regs->pc` equals the trampoline symbol, calls `kretprobe_trampoline_handler()` with the frame pointer, and replaces PC with the original return destination.

Dependencies and integration: includes Linux linkage, assembler, and bug macros. It is linked only when `CONFIG_KPROBES` is enabled by the probes Makefile.

Risks: the trampoline must remain minimal and placed in executable kernel text. Any instruction after the BRK is defensive only; reaching it indicates the debug hook failed to claim the kretprobe breakpoint.

Test signals: kretprobe tests should show return handlers firing and no execution of `ASM_BUG()`. Symbol lookup and blacklist behavior should prevent normal probes from corrupting the trampoline path.
