# sources/distributed-fs/ceph-client/kernel/printk/printk_safe.c

## Purpose
`printk_safe.c` tracks printk contexts where legacy console printing must be deferred or forced to avoid recursion, deadlock, or unsafe spinning. It also routes `vprintk()` through KDB when kernel debugger printk trapping is active.

## Important APIs, types, and functions
`printk_force_console_enter()`, `printk_force_console_exit()`, and `is_printk_force_console()` maintain an atomic force-console nesting counter. `__printk_safe_enter()` and `__printk_safe_exit()` update a per-CPU `printk_context`. `__printk_deferred_enter()` and `__printk_deferred_exit()` wrap those updates with `cant_migrate()`. `is_printk_legacy_deferred()` evaluates global forced-kthread mode, per-CPU context, NMI state, and printk CPU-sync ownership. `vprintk()` dispatches either to `vkdb_printf()` or `vprintk_default()`.

## Control flow
Callers enter safe or deferred sections before printk-deadlock-prone activity and exit afterward. Legacy printk paths ask `is_printk_legacy_deferred()` to decide whether synchronous console work should be deferred. If KGDB/KDB traps printk and the current CPU is not already in KDB printf recursion, `vprintk()` sends the formatted output to KDB.

## State and persistence behavior
State is volatile runtime-only: an atomic global force counter and per-CPU nesting count. The per-CPU count is safe to read in any context because migration is disabled while it is set. No state persists across boot or module boundaries.

## Dependencies and integration points
The file depends on preemption/migration checks, NMI detection, KDB/KGDB optional support, SMP/per-CPU primitives, printk internal helpers, and exported `vprintk` ABI used by kernel code.

## Risks and invariants
Enter/exit nesting must remain balanced. Per-CPU context increments can be preempted by NMI, so operations must remain simple and NMI-tolerant. Incorrect deferral decisions can deadlock legacy console paths or suppress urgent console output. KDB routing must avoid recursion via `kdb_printf_cpu`.

## Test signals
Signals include nested safe/deferred printk paths, NMI printk, console lock recursion testing, KDB printk trapping, and lockdep reports around console and port locks. Balanced force-console and per-CPU nesting can be asserted indirectly by verifying later printk paths return to normal synchronous behavior.
