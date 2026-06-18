# sources/distributed-fs/ceph-client/kernel/printk/printk.c

## Purpose

`printk.c` is the central kernel logging and console-output implementation. It owns the printk ringbuffer pointer, log-level policy, `/dev/kmsg` and `syslog(2)` access paths, console command-line selection, console registration/unregistration, legacy and nbcon flushing policy, panic flushing, deferred wakeups, kmsg dumpers, and CPU-synchronous printk helpers.

## Important state

Major global state includes `console_printk[]`, `suppress_printk`, `console_mutex`, `console_sem`, `console_list`, `console_srcu`, `console_cmdline[]`, `preferred_console`, `console_set_on_cmdline`, `syslog_lock`, `syslog_seq`, `clear_seq`, `log_buf`, `log_buf_len`, the global `struct printk_ringbuffer *prb`, console class flags (`have_legacy_console`, `have_nbcon_console`, `have_boot_console`), panic synchronization (`legacy_allow_panic_sync`), irq-work blocking (`console_irqwork_blocked`), kthread readiness/running flags, recursion counters, wakeup irq_work, and the kmsg dumper list.

## Message ingestion and storage

`vprintk_emit()` is the main entry. It suppresses nonessential messages after panic, chooses flush types before storing, handles scheduler-context deferral, applies optional boot delay, calls `vprintk_store()`, then flushes or wakes nbcon/legacy/klogd paths. `vprintk_store()` performs recursion tracking with IRQs disabled, timestamps early, formats the message, parses printk prefixes, handles continuation records with `prb_reserve_in_last()`, truncates oversized records, fills `struct printk_info`, stores device and execution context metadata, commits final or non-final records, and returns stored length.

## Userspace log interfaces

`/dev/kmsg` uses `struct devkmsg_user` to track a reader sequence, ratelimit state, lock, and buffers. Writes parse optional syslog priority, enforce userspace facility, and call `vprintk_emit()`. Reads format extended records, block on `log_wait`, return `-EPIPE` when records were overwritten, and support limited seeks to first, clear point, and end. `do_syslog()` implements `syslog(2)` actions for reading, read-all, read-clear, clear, console level control, unread size, and buffer size, guarded by `check_syslog_permissions()` and `security_syslog()`.

## Buffer setup and formatting

Early boot uses a static ringbuffer. `setup_log_buf()` optionally allocates a larger memblock-backed dynamic ringbuffer, copies existing records, switches `prb`, and copies any late static records that appeared during the switch. Formatting helpers produce syslog prefixes, timestamps, caller IDs, extended headers, escaped text, device dictionaries, and console-ready multi-line text with per-line prefixes.

## Console selection and registration

`console_setup()` parses `console=` options, including null console, braille options, tty shorthand, `DEVNAME:0.0` style names, indices, and option strings. `__add_preferred_console()` records preferred consoles and tracks user-specified entries. `register_console()` validates duplicate and boot/real console ordering, allocates nbcon state if needed, enables default or preferred consoles, skips normal printk registration for braille consoles, chooses the initial sequence with `get_init_console_seq()`, updates global console-class flags, inserts the console into the SRCU-protected hlist, unregisters boot consoles after real handoff, notifies sysfs, and starts or stops printer threads as needed. `unregister_console_locked()` flushes, disables, removes, synchronizes SRCU, updates global flags, frees nbcon state, calls optional exit, and refreshes kthreads.

## Console flushing and threading

Legacy flushing is serialized by `console_sem`; the code also implements a spinning handoff so another printk caller can take over console output without long stalls. `console_emit_next_record()` formats one record for legacy consoles, handles dropped-message notices, calls the console `write()` callback, updates sequence, and may hand off the lock. `console_flush_one_record()` iterates usable consoles under SRCU and uses either legacy output or `nbcon_legacy_emit_next_record()` depending on flags and current flush policy. `pr_flush()` waits for all usable consoles, optionally resetting timeout on progress. `printk_kthreads_check_locked()` manages the PREEMPT_RT legacy printer thread and nbcon kthreads.

## Panic, suspend, replay, and dump paths

`console_flush_on_panic()` can rewind consoles for replay-all, atomically flush nbcon consoles, and flush legacy consoles only after `printk_legacy_allow_panic_sync()` allows it. `console_suspend_all()` flushes, blocks irq_work, marks consoles suspended, and synchronizes SRCU; resume reverses that and wakes appropriate paths. `console_try_replay_all()` rewinds all consoles and triggers available flushing. The kmsg dumper API registers RCU-protected dumpers and provides line or buffer iterators over the ringbuffer for panic/oops/shutdown consumers.

## Dependencies and integration

The file integrates with the printk ringbuffer, console core, tty, sysctl, security hooks, VMCOREINFO, memblock, CPU hotplug, irq_work, SRCU/RCU, tracepoints, panic/oops state, braille helpers, nbcon helpers, and kmsg dumper consumers. It exports many public kernel symbols including `_printk`, `vprintk_emit`, console lock/list helpers, console registration APIs, syslog handling, rate-limit helpers, kmsg dump APIs, and CPU-sync helpers.

## Risks and test signals

Locking spans semaphores, mutexes, SRCU, spinlocks, irq_work, per-CPU recursion counters, and panic exceptions. Reordering can deadlock or lose console output. `/dev/kmsg` and syslog behavior are userspace ABI. Console registration must synchronize boot consoles, real consoles, nbcon hardware locks, and braille consoles without duplicate output. Test boot with static/dynamic buffers, `/dev/kmsg`, syslog actions, console parsing, boot handoff, legacy and nbcon flushing, PREEMPT_RT, suspend/resume, panic replay, kmsg dumpers, rate limiting, recursion suppression, CPU hotplug, `CONFIG_PRINTK=n`, and execution-context metadata.
