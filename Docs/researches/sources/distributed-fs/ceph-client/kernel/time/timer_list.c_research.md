# sources/distributed-fs/ceph-client/kernel/time/timer_list.c

## Purpose
This diagnostic file prints active high-resolution timers, tick scheduler state, and clock event devices through `/proc/timer_list` and SysRq-Q. It is for observability, not for timer scheduling.

## Important APIs, types, and functions
`struct timer_list_iter` tracks proc iteration state: CPU, second pass, and snapshot `now`. `SEQ_printf()` abstracts output to either seq_file or console. `print_timer()`, `print_active_timers()`, `print_base()`, `print_cpu()`, and `print_tickdevice()` emit timer and clockevent details. `sysrq_timer_list_show()` prints to console. The proc path is implemented by `timer_list_show()`, `move_iter()`, `timer_list_start()`, `timer_list_next()`, `timer_list_stop()`, `timer_list_sops`, and `init_timer_list_procfs()`.

## Control flow
SysRq output snapshots `ktime_get()` once, prints a header, iterates online CPUs, prints hrtimer bases, then prints broadcast and per-CPU tick devices when generic clockevents are enabled. The proc implementation uses seq_file iteration: the first pass prints per-CPU hrtimer/tick scheduler data, and the optional second pass prints clockevent device data. `print_active_timers()` deliberately locks, copies one timer, unlocks for printing, and repeats by index to avoid holding base locks during potentially slow formatting.

## State and persistence behavior
The file does not own scheduler state. It reads live per-CPU hrtimer bases, tick scheduler state, clockevent devices, and jiffies. Proc iterator state is per-open file private data. Output is a snapshot with possible races; it favors diagnostic usefulness and watchdog friendliness over a fully atomic global view.

## Dependencies and integration points
It depends on procfs, seq_file, kallsyms symbol formatting, hrtimer internals, tick internals, clockevents, broadcast tick support, CPU online masks, and NMI watchdog touching. It complements `timer.c` and hrtimer/tick code by exposing their current state to operators and developers.

## Risks
The main risk is diagnostic traversal racing with timer changes. The O(N*N) active timer walk is intentional to avoid printing under locks but can be expensive on systems with many timers. Pointer and symbol output must respect kernel pointer formatting/security policy. Procfs creation failure simply disables the interface.

## Test signals
Signals include successful creation and readable output of `/proc/timer_list` when `CONFIG_PROC_FS` is enabled, SysRq-Q output, stable behavior under timer churn, and watchdog non-triggering during large dumps. Build coverage should include combinations of `CONFIG_GENERIC_CLOCKEVENTS`, broadcast support, high-resolution timers, tick oneshot, and procfs.
