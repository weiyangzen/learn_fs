# sources/distributed-fs/ceph-client/kernel/debug/kdb/kdb_bt.c

## Purpose
`kdb_bt.c` implements KDB stack traceback commands: current task backtrace, task-by-pid backtrace, task-struct-address backtrace, all-task backtrace, and current-task-on-CPU backtrace.

## Important APIs, types, and functions
Functions include `kdb_show_stack()`, `kdb_bt1()`, `kdb_bt_cpu()`, and command handler `kdb_bt()`. It uses KDB helpers `kdb_task_has_cpu()`, `kdb_process_cpu()`, `KDB_TSK()`, `kdb_task_state()`, `kdb_ps1()`, `kdb_getarea()`, `kdb_getchar()`, `kdbgetintenv()`, `kdbgetenv()`, `kdbgetularg()`, `kdbgetaddrarg()`, and `kdb_parse()`.

## Control flow
`kdb_show_stack()` increments `kdb_trap_printk`, then either asks the stopped CPU to dump its own stack via `kdb_dump_stack_on_cpu()` when the task is actively running and no alternate stack address is supplied, or calls `show_stack()` for the target task/address. It temporarily raises console loglevel for remote CPU self-dumps.

`kdb_bt()` dispatches by command name. `bta` walks online current tasks first, then all non-current process threads, filtering by a task-state mask from the argument or `PS` environment and optionally prompting between tasks based on `BTAPROMPT`. `btp` finds a task by PID in the init PID namespace. `btt` treats the argument as a `struct task_struct *`. `btc` dumps one CPU's current task or, with no CPU argument, prints CPU status via recursive `kdb_parse("cpu\n")` and then dumps every online CPU. Plain `bt` dumps the current KDB task or uses an address expression as an alternate stack location.

## State and persistence behavior
The command mutates transient KDB output state: `kdb_trap_printk`, pager line tracking, console loglevel during CPU stack dumps, and watchdog touch timing. It does not persist data or change debug breakpoints.

## Dependencies and integration points
It integrates with KGDB/KDB CPU roundup state through `kdb_dump_stack_on_cpu()`, scheduler task iteration, init PID namespace task lookup, stack unwinder `show_stack()`, KDB process display helpers, KDB environment variables, console logging, and NMI watchdog touch logic.

## Risks and edge cases
Backtracing a running task on another CPU is architecture-sensitive, so this file asks stopped slave CPUs to dump themselves when possible. If a CPU failed to stop in the debugger or lacks a recorded task, `btc` prints warnings. `btt` trusts an arbitrary address after only `kdb_getarea()` checks in `kdb_bt1()`. `bta` can produce very large output and uses prompting plus interrupt flag checks to stop. Recursive `kdb_parse()` means `btc` must discard `argv` afterward.

## Test signals
Test current `bt`, alternate-stack `bt <addr>`, `btp <pid>`, `btt <task_addr>`, `bta` with default and explicit masks, prompt quit/continue behavior, `btc` for one CPU and all CPUs, CPUs that are offline or not rounded up, KDB interrupt during all-task traversal, and systems with/without reliable frame pointers.
