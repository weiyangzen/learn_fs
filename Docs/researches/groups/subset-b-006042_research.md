# subset-b-006042 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/printk/Makefile -->
# sources/distributed-fs/ceph-client/kernel/printk/Makefile

## Purpose

This Makefile is the build manifest for the kernel printk subsystem in this source tree. It selects the core printk implementation unconditionally, then layers optional console safety, non-blocking console support, braille-console support, printk format indexing, sysctl support, and the ringbuffer KUnit test according to Kconfig symbols.

## Important build targets

- `obj-y = printk.o` makes `printk.c` part of the kernel build regardless of `CONFIG_PRINTK`, because that file also provides stubs and console infrastructure used by non-printk builds.
- `obj-$(CONFIG_PRINTK) += printk_safe.o nbcon.o` adds recursion-safe printk support and non-blocking console support only when printk is enabled.
- `obj-$(CONFIG_A11Y_BRAILLE_CONSOLE) += braille.o` adds command-line braille console integration.
- `obj-$(CONFIG_PRINTK_INDEX) += index.o` exposes indexed printk format strings through debugfs.
- `obj-$(CONFIG_PRINTK) += printk_support.o` defines a composite object whose required member is `printk_ringbuffer.o`; `printk_support-$(CONFIG_SYSCTL) += sysctl.o` adds sysctl controls when enabled.
- `obj-$(CONFIG_PRINTK_RINGBUFFER_KUNIT_TEST) += printk_ringbuffer_kunit_test.o` builds the ringbuffer test object.

## Control flow and integration

The build graph keeps the always-needed console/syslog facade in `printk.o` while putting the actual record storage backend in `printk_support.o` only for `CONFIG_PRINTK`. `nbcon.o` is built with printk because its APIs are declared from `internal.h` and called by `printk.c` for console flushing. `braille.o` is independent of general printk enablement but is only selected for accessibility braille console support. `index.o` is tied to `CONFIG_PRINTK_INDEX` and depends on linker-emitted `__start_printk_index` and module section metadata.

## State and persistence behavior

This file has no runtime state. Its main persistence effect is compile-time: it determines which object files become part of vmlinux or built-in kernel objects. Mis-gating an object here can produce missing symbols in one configuration or dead code in another.

## Dependencies

The manifest depends on Kbuild variable conventions and Kconfig symbols: `CONFIG_PRINTK`, `CONFIG_A11Y_BRAILLE_CONSOLE`, `CONFIG_PRINTK_INDEX`, `CONFIG_SYSCTL`, and `CONFIG_PRINTK_RINGBUFFER_KUNIT_TEST`.

## Risks

- `printk.o` must stay unconditional because several public console functions and stubs are needed even when `CONFIG_PRINTK` is disabled.
- `nbcon.o` must not be built without printk support unless all references and storage backing are stubbed; it depends on the printk ringbuffer and full console state.
- Moving `sysctl.o` outside `printk_support` would need matching changes to the sysctl init stubs in `internal.h`.

## Test signals

Build coverage should include `CONFIG_PRINTK=y`, `CONFIG_PRINTK=n`, `CONFIG_SYSCTL=y/n`, `CONFIG_PRINTK_INDEX=y`, `CONFIG_A11Y_BRAILLE_CONSOLE=y`, and `CONFIG_PRINTK_RINGBUFFER_KUNIT_TEST=y`. The strongest direct test target is the ringbuffer KUnit object selected by `CONFIG_PRINTK_RINGBUFFER_KUNIT_TEST`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/printk/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/printk/braille.c -->
# sources/distributed-fs/ceph-client/kernel/printk/braille.c

## Purpose

`braille.c` bridges printk console command-line parsing with the kernel braille-console driver. It recognizes braille prefixes in `console=` arguments, stores parsed braille options in `struct console_cmdline`, and registers or unregisters the braille backend when a matching console is enabled or removed.

## Important APIs

- `_braille_console_setup(char **str, char **brl_options)` parses `console=` fragments. `brl,` means braille with empty braille options and advances `*str` past the prefix. `brl=<opts>,<port>` stores the substring after `brl=` as braille options, replaces the separator comma with `NUL`, and advances `*str` to the serial or console port string.
- `_braille_register_console(struct console *console, struct console_cmdline *c)` checks `c->brl_options`, sets `CON_BRL`, and calls `braille_register_console(console, c->index, c->options, c->brl_options)`.
- `_braille_unregister_console(struct console *console)` calls `braille_unregister_console()` only for consoles flagged `CON_BRL`.

## Control flow

`printk.c:console_setup()` calls `_braille_console_setup()` before it decodes the tty name and options. Later, `try_enable_preferred_console()` calls `_braille_register_console()` after a candidate console matches a preferred command-line entry but before normal console setup. On unregister, `unregister_console_locked()` calls `_braille_unregister_console()` before disabling and removing the console from the console list.

## State and persistence behavior

The parser mutates the boot command-line string in place by writing a `NUL` over the comma after `brl=<opts>`. The persistent state is the `brl_options` pointer saved in `struct console_cmdline` and the `CON_BRL` flag set on the `struct console`. The file itself owns no global state.

## Dependencies

It depends on `linux/console.h` for `struct console` and `CON_BRL`, `console_cmdline.h` for the parsed console record, and the external braille console APIs declared through kernel console headers. The parser uses `str_has_prefix()` and `strchr()`.

## Integration points

The integration is deliberately narrow: normal printk consoles do not output to the braille console after registration. In `register_console()`, a successful braille registration or a `CON_BRL` flag causes the normal console registration path to skip adding that console as a printk output console.

## Risks

- The parser assumes mutable boot option storage. Passing immutable strings would fault when it writes the separator `NUL`.
- `brl=` without a following comma is rejected with `-EINVAL`; `console_setup()` treats that as consumed setup input and returns.
- Lifetime of `brl_options` is tied to the command-line option buffer, so callers must not free or reuse the parsed string.

## Test signals

Useful signals are boot tests with `console=brl,ttyS0`, `console=brl=<driver-options>,ttyS0`, malformed `console=brl=<driver-options>`, and unregister tests confirming `CON_BRL` consoles call braille unregister and skip normal printk output registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/printk/braille.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/printk/braille.h -->
# sources/distributed-fs/ceph-client/kernel/printk/braille.h

## Purpose

`braille.h` provides the internal printk-facing braille console API. It hides `CONFIG_A11Y_BRAILLE_CONSOLE` behind no-op inline stubs so the main console registration and command-line parsing code can call braille helpers unconditionally.

## Important APIs

- `braille_set_options(struct console_cmdline *c, char *brl_options)` stores parsed braille options in the command-line console entry when braille support is enabled.
- `_braille_console_setup(char **str, char **brl_options)` parses braille syntax from `console=` options.
- `_braille_register_console(struct console *console, struct console_cmdline *c)` registers the braille backend and marks the console `CON_BRL`.
- `_braille_unregister_console(struct console *console)` unregisters a braille console during console teardown.

When `CONFIG_A11Y_BRAILLE_CONSOLE` is disabled, all helpers compile to no-ops returning success.

## Control flow

`printk.c` uses this header in command-line parsing and console registration. The enabled build stores braille options in `struct console_cmdline`; the disabled build drops them and lets the normal console parsing path proceed without braille-specific state.

## State and persistence behavior

The header itself owns no state. It controls whether `struct console_cmdline::brl_options` is populated. In disabled builds, the field does not exist because `console_cmdline.h` also gates it on the same Kconfig symbol.

## Dependencies

The header depends on `struct console_cmdline` and `struct console` being visible to users. It must remain synchronized with `console_cmdline.h`; otherwise inline access to `c->brl_options` could break disabled or enabled builds.

## Integration points

The key integration pattern is compile-time polymorphism. `printk.c` can always call `braille_set_options()`, `_braille_console_setup()`, `_braille_register_console()`, and `_braille_unregister_console()` while the compiler removes all braille behavior from non-accessibility builds.

## Risks

- Any future added braille state must be gated consistently in both `braille.h` and `console_cmdline.h`.
- The stub functions return success, so callers must not rely on a nonzero result to detect that braille support is absent.
- Missing prototypes here would let `printk.c` accidentally depend on full braille driver headers.

## Test signals

Build tests should cover `CONFIG_A11Y_BRAILLE_CONSOLE=y` and `n`. Runtime coverage should confirm that the same `console=` options either register braille behavior in enabled builds or are harmless in disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/printk/braille.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/printk/console_cmdline.h -->
# sources/distributed-fs/ceph-client/kernel/printk/console_cmdline.h

## Purpose

`console_cmdline.h` defines `struct console_cmdline`, the internal record used by printk to retain preferred console choices collected from kernel command-line options, platform defaults, device tree, SPCR, or subsystem prediction.

## Important type

`struct console_cmdline` contains:

- `name[16]`: console driver name, such as `ttyS`.
- `index`: minor or port index to use. A negative value is used for unresolved `DEVNAME:0.0` style entries until a driver name and index can be associated.
- `devname[32]`: firmware or device-name style console identifier.
- `user_specified`: distinguishes command-line entries from platform defaults.
- `options`: driver option string after the console name, for example baud/parity bits.
- `brl_options`: braille driver options, present only with `CONFIG_A11Y_BRAILLE_CONSOLE`.

## Control flow

`printk.c` maintains a fixed array of these records. `console_setup()` fills entries from `console=` parameters. `add_preferred_console()` adds platform defaults. `match_devname_and_update_preferred_console()` resolves `devname` entries once a subsystem knows the eventual console driver and index. `try_enable_preferred_console()` consumes the records when drivers call `register_console()`.

## State and persistence behavior

These records persist for the life of the kernel. They are not dynamically allocated and are capped by `MAX_CMDLINECONSOLES` in `printk.c`. The `options` and `brl_options` fields point into boot option storage rather than owning copied strings.

## Dependencies

The header depends on `bool` being available from the including translation unit. Its optional `brl_options` member must stay aligned with the braille helper stubs and implementation.

## Integration points

This structure is the contract between early boot parsing and later console registration. It lets console drivers register after command-line parsing and still be matched against earlier preferences. The `devname` field supports consoles whose tty driver identity is not known at early parameter time.

## Risks

- Fixed-size `name` and `devname` buffers require bounded copies. Existing callers use `strscpy()` and a `static_assert` in `console_setup()` for expected derived tty names.
- Pointer fields rely on long-lived source strings.
- The fixed entry count means excess `console=` parameters fail with `-E2BIG` in `__add_preferred_console()`.

## Test signals

Tests should cover command-line consoles with explicit tty names, numeric serial shorthand, `DEVNAME:0.0` resolution, duplicate preferred entries, platform defaults versus user-specified entries, and braille-enabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/printk/console_cmdline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/printk/index.c -->
# sources/distributed-fs/ceph-client/kernel/printk/index.c

## Purpose

`index.c` implements the userspace-visible printk format index under debugfs. It exposes compile-time collected `struct pi_entry` records for vmlinux and loaded modules so tools can inspect printk callsite metadata and format strings without scanning binary text.

## Important APIs and functions

- `pi_get_entry(const struct module *mod, loff_t pos)` selects either module `printk_index_start/size` metadata or vmlinux linker symbols `__start_printk_index` and `__stop_printk_index`.
- `pi_start()`, `pi_next()`, `pi_show()`, and `pi_stop()` implement a `seq_file` iterator.
- `pi_show()` prints a header, parses embedded log-level prefixes with `printk_parse_prefix()`, emits continuation markers, and escapes format strings with `seq_escape_str()`.
- `pi_create_file()` creates one debugfs file per module name, with `vmlinux` used for built-in entries.
- `pi_module_notify()` adds a file at `MODULE_STATE_COMING` and removes it at `MODULE_STATE_GOING`.
- `pi_init()` creates `debugfs/printk/index`, registers the module notifier, and creates the vmlinux file via `postcore_initcall()`.

## Control flow

At postcore init, the file creates a debugfs root directory named `printk`, an `index` child, then exposes the built-in index. When modules are enabled, the notifier mirrors module lifetime by adding and removing per-module debugfs files. Reads are lazy: seq_file uses the file inode private pointer as the module key and indexes entries by file position.

## State and persistence behavior

The only owned persistent state is `dfs_index`, the debugfs dentry for the index directory, and the module notifier object. Actual printk index entries live in linker sections or module metadata. Debugfs files disappear when modules go away.

## Dependencies

This file depends on debugfs, seq_file helper macros, module notifier infrastructure, `struct pi_entry` from printk headers, linker section symbols, and `printk_parse_prefix()` from `printk.c`. With `CONFIG_MODULES=n`, module handling compiles to vmlinux-only stubs.

## Integration points

The output format is `# <level/flags> filename:line function "format"` followed by one row per indexed callsite. It understands separate `entry->level`, inline printk prefixes in `entry->fmt`, `LOG_CONT`, and optional `entry->subsys_fmt_prefix`, so it is coupled to the printk indexing compiler/linker instrumentation.

## Risks

- Debugfs creation failures are not checked; missing debugfs support or allocation failure simply results in absent files.
- Module file lifetime relies on notifier ordering and debugfs lookup/removal by module name.
- Format escaping must remain correct for quotes and backslashes. The local macro uses `ESCAPE_ANY | ESCAPE_NAP | ESCAPE_APPEND` with explicit quote/backslash selection to avoid under-escaping.
- Entry pointers are trusted kernel metadata; corrupted module index sections could produce invalid reads.

## Test signals

Enable `CONFIG_PRINTK_INDEX` and inspect `/sys/kernel/debug/printk/index/vmlinux`. With modules enabled, load and unload a module containing printk calls and confirm the per-module debugfs file appears and disappears. Include callsites with `KERN_CONT`, explicit log levels, subsystem prefixes, quotes, and backslashes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/printk/index.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/printk/internal.h -->
# sources/distributed-fs/ceph-client/kernel/printk/internal.h

## Purpose

`internal.h` is the private interface shared by printk implementation files. It centralizes build-dependent stubs, console flushing policy, nbcon hooks, message buffer structures, printk ringbuffer accessors, sysctl hooks, and cross-file state flags.

## Important APIs, types, and macros

- `printk_sysctl_init()` and `devkmsg_sysctl_set_loglvl()` are available only with `CONFIG_PRINTK && CONFIG_SYSCTL`; otherwise initialization is a stub.
- `con_printk(lvl, con, fmt, ...)` formats console lifecycle messages with legacy, boot, name, and index context.
- `force_legacy_kthread()` is true on `CONFIG_PREEMPT_RT`, forcing legacy console output through a dedicated thread.
- `PRINTK_PREFIX_MAX`, `PRINTK_MESSAGE_MAX`, and `PRINTKRB_RECORD_MAX` define formatted output and ringbuffer record limits.
- `enum printk_info_flags` defines `LOG_FORCE_CON`, `LOG_NEWLINE`, and `LOG_CONT`.
- The header declares `vprintk_store()`, `vprintk_default()`, safe printk enter/exit helpers, `printk_parse_prefix()`, console lock handover helpers, nbcon sequence/alloc/free/kthread/flush functions, and `printk_get_next_message()`.
- `struct console_flush_type` describes which output paths to use: `nbcon_atomic`, `nbcon_offload`, `legacy_direct`, and `legacy_offload`.
- `printk_get_console_flush_type()` computes the flush strategy from nbcon priority, registered console classes, boot console presence, kthread state, panic state, deferred legacy policy, and irq-work availability.
- `struct printk_buffers` and `struct printk_message` define the shared out/scratch buffers and a formatted message container.

## Control flow

Most callers store a record, call `printk_get_console_flush_type()`, then either flush nbcon consoles atomically, wake nbcon kthreads, run the legacy loop directly, or defer to irq work/legacy kthread. Panic and emergency contexts move `nbcon_get_default_prio()` away from normal priority and narrow the permitted output paths. When `CONFIG_PRINTK` is disabled, stubs preserve API availability while returning no work.

## State and persistence behavior

The header declares cross-file global state owned mostly by `printk.c`: `prb`, `printk_kthreads_running`, `printk_kthreads_ready`, `debug_non_panic_cpus`, `have_boot_console`, `have_nbcon_console`, `have_legacy_console`, `legacy_allow_panic_sync`, `console_irqwork_blocked`, and `printk_shared_pbufs`. These flags persist for runtime and drive both console registration and output decisions.

## Dependencies

It depends on console core types, sysctl declarations, `enum nbcon_prio`, rcuwait, task command sizes under execution-context support, and the printk ringbuffer type without exposing the ringbuffer internals to every user.

## Integration points

This header is the contract between `printk.c`, `nbcon.c`, `index.c`, `sysctl.c`, `printk_safe.c`, and ringbuffer support. It also bridges external console driver callbacks by defining the buffers and ownership checks that nbcon write callbacks use.

## Risks

- Flush policy changes are high risk because they affect panic visibility, PREEMPT_RT behavior, boot consoles that may share hardware with real consoles, and scheduler-context logging.
- The disabled-`CONFIG_PRINTK` stubs must remain ABI-compatible with enabled declarations.
- `printk_get_console_flush_type()` depends on global flags being updated before or after nbcon allocation/free in precise order.
- Buffer sizes define truncation boundaries and must stay compatible with ringbuffer reservation logic.

## Test signals

Important coverage includes normal boot, boot-console handoff, nbcon-only systems, legacy-only systems, mixed boot/nbcon systems, PREEMPT_RT forced threading, panic flushing, emergency sections, `CONFIG_PRINTK=n`, and sysctl-enabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/printk/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/printk/nbcon.c -->
# sources/distributed-fs/ceph-client/kernel/printk/nbcon.c

## Purpose

`nbcon.c` implements non-blocking console printing for consoles that do not rely on the legacy `console_lock` as their primary serialization mechanism. It provides atomic ownership transfer, per-console sequence tracking, emergency and panic priority handling, threaded printing, legacy-loop compatibility, and driver-facing helpers for marking unsafe hardware regions.

## Important state and APIs

Each nbcon console stores an atomic `nbcon_state` with owner priority, owner CPU, requested handover priority, unsafe state, and permanent unsafe-takeover state. Per-console sequence fields track the next ringbuffer record to print and the previous sequence used to detect replay. Global state includes `nbcon_cpu_emergency_cnt`, per-CPU emergency nesting, `panic_nbcon_pbufs`, and `panic_nbcon_allow_unsafe_takeover`.

Key exported or cross-file functions include:

- `nbcon_seq_read()` and `nbcon_seq_force()` read or set a console's next record sequence.
- `nbcon_can_proceed()`, `nbcon_enter_unsafe()`, `nbcon_exit_unsafe()`, and `nbcon_reacquire_nobuf()` are used by nbcon console drivers during callbacks.
- `nbcon_legacy_emit_next_record()` lets the legacy console loop print an nbcon console when atomic/threaded nbcon paths are unavailable.
- `nbcon_atomic_flush_pending()` and `nbcon_atomic_flush_unsafe()` flush nbcon consoles through `write_atomic()`, with the unsafe version permitting panic-only hostile takeover.
- `nbcon_cpu_emergency_enter()` and `nbcon_cpu_emergency_exit()` raise a CPU-local emergency priority and control kthread suppression/wakeup.
- `nbcon_alloc()` and `nbcon_free()` initialize and tear down per-console buffers, rcuwait, irq_work, state, sequence, and kthreads.
- `nbcon_device_try_acquire()` / `nbcon_device_release()` and `nbcon_kdb_try_acquire()` / `nbcon_kdb_release()` protect driver or KDB direct hardware use.

## Ownership control flow

Acquisition tries three paths. Direct acquire succeeds if the console is unlocked or owned by a lower priority context while safe. Friendly handover sets `req_prio`, waits for the lower priority owner to leave its unsafe region, then takes ownership. Hostile takeover is panic-only and marks `unsafe_takeover` when the panic CPU must print despite unsafe state. Release clears owner priority but preserves permanent unsafe status after hostile takeover.

`nbcon_context_can_proceed()` is the central checkpoint. Owners call it when entering or exiting unsafe regions and before expensive work. If a higher priority waiter exists and the console is safe, ownership is released so the waiter can proceed. Drivers are expected to stop immediately when helpers report lost ownership.

## Printing flow

`nbcon_emit_one()` optionally takes the console's driver lock for thread context, acquires nbcon ownership, and calls `nbcon_emit_next_record()`. That function enters unsafe state to read and format the next printk record, accounts dropped messages, prepends replay notices when a takeover reprints a sequence, leaves unsafe state for the actual driver callback, calls `write_atomic()` or `write_thread()`, then re-enters unsafe state to update dropped count and sequence. If ownership is lost at any point, the higher priority owner becomes responsible for pending records.

## Threading, panic, and emergency behavior

`nbcon_kthread_func()` waits on `con->rcuwait`, suppresses normal threaded output while any CPU is in emergency or panic, holds SRCU across console usability checks and output, and loops while backlog remains. `nbcon_kthreads_wake()` queues per-console irq_work only when threads are actually waiting. Emergency nesting disables preemption and increments global and per-CPU counters; exiting wakes kthreads when the last emergency context leaves and offload is available. Panic priority suppresses non-panic CPUs and can enable unsafe takeover for final flushing.

## Dependencies and integration

The file depends on `printk_ringbuffer` helpers, the shared `printk_get_next_message()` formatter, console SRCU list access, console driver callbacks (`write_thread`, optional `write_atomic`, `device_lock`, `device_unlock`), irq_work, rcuwait, kthreads, panic/KDB helpers, and the policy state declared in `internal.h`. `printk.c` calls nbcon allocation during console registration, freeing during unregister, atomic flushes during printk and panic, and kthread wakeups during deferred output.

## Risks

- Atomic state transitions are subtle. Incorrect owner CPU, priority, or unsafe-bit handling can allow duplicate hardware access or missed panic output.
- Hostile takeover is intentionally unsafe and must remain panic-only.
- Threaded writes require `device_lock()` and migration constraints. Missing driver callbacks are fatal in `nbcon_alloc()`.
- Sequence updates race with `nbcon_seq_force()` and panic takeover; the code uses cmpxchg and rereads to avoid corrupting progress.
- Boot consoles share hardware with real consoles, so nbcon kthreads are suppressed while boot consoles exist.

## Test signals

Coverage should include nbcon registration failure when mandatory callbacks are absent, normal threaded printing, atomic-only flushing, dropped-message accounting, replay after takeover, emergency nesting, panic flush with and without unsafe takeover, KDB acquire/release, device acquire/release during port configuration, mixed boot and nbcon consoles, and PREEMPT_RT behavior where legacy flushing is forced to a thread.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/printk/nbcon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/printk/printk.c -->
# sources/distributed-fs/ceph-client/kernel/printk/printk.c

## Purpose

`printk.c` is the central kernel logging and console-output implementation. It owns the printk ringbuffer pointer, log-level policy, `/dev/kmsg` and `syslog(2)` access paths, console command-line selection, console registration/unregistration, legacy and nbcon flushing policy, panic flushing, deferred wakeups, kmsg dumpers, and CPU-synchronous printk helpers.

## Important state

Major global state includes `console_printk[]`, `suppress_printk`, `console_mutex`, `console_sem`, `console_list`, `console_srcu`, `console_cmdline[]`, `preferred_console`, `console_set_on_cmdline`, `syslog_lock`, `syslog_seq`, `clear_seq`, `log_buf`, `log_buf_len`, the global `struct printk_ringbuffer *prb`, console class flags (`have_legacy_console`, `have_nbcon_console`, `have_boot_console`), panic synchronization (`legacy_allow_panic_sync`), irq-work blocking (`console_irqwork_blocked`), kthread readiness/running flags, recursion counters, wakeup irq_work, and the kmsg dumper list.

## Message ingestion and storage

`vprintk_emit()` is the main entry. It suppresses nonessential messages after panic, chooses flush types before storing, handles scheduler-context deferral, applies optional boot delay, calls `vprintk_store()`, then flushes or wakes nbcon/legacy/klogd paths. `vprintk_store()` performs recursion tracking with IRQs disabled, timestamps early, formats the message, parses printk prefixes, handles continuation records with `prb_reserve_in_last()`, truncates oversized records, fills `struct printk_info`, stores device and execution context metadata, commits final or non-final records, and returns stored length.

`printk_parse_prefix()` decodes kernel log-level and continuation prefixes. `printk_sprint()` formats text, strips trailing newline into `LOG_NEWLINE`, strips embedded prefixes for kernel facility records, and fires the console tracepoint.

## Userspace log interfaces

`/dev/kmsg` uses `struct devkmsg_user` to track a reader sequence, ratelimit state, lock, and buffers. Writes parse optional syslog priority, enforce userspace facility, and call `vprintk_emit()`. Reads format extended records, block on `log_wait`, return `-EPIPE` when records were overwritten, and support limited seeks to first, clear point, and end. `do_syslog()` implements `syslog(2)` actions for reading, read-all, read-clear, clear, console level control, unread size, and buffer size, guarded by `check_syslog_permissions()` and `security_syslog()`.

## Buffer setup and formatting

Early boot uses a static ringbuffer. `setup_log_buf()` optionally allocates a larger memblock-backed dynamic ringbuffer, copies existing records, switches `prb`, and copies any late static records that appeared during the switch. Formatting helpers produce syslog prefixes, timestamps, caller IDs, extended headers, escaped text, device dictionaries, and console-ready multi-line text with per-line prefixes.

## Console selection and registration

`console_setup()` parses `console=` options, including null console, braille options, tty shorthand, `DEVNAME:0.0` style names, indices, and option strings. `__add_preferred_console()` records preferred consoles and tracks user-specified entries. `match_devname_and_update_preferred_console()` resolves firmware device names later.

`register_console()` validates duplicate and boot/real console ordering, allocates nbcon state if needed, enables default or preferred consoles, skips normal printk registration for braille consoles, chooses the initial sequence with `get_init_console_seq()`, updates global console-class flags, inserts the console into the SRCU-protected hlist, unregisters boot consoles after real handoff, notifies sysfs, and starts or stops printer threads as needed. `unregister_console_locked()` flushes, disables, removes, synchronizes SRCU, updates global flags, frees nbcon state, calls optional exit, and refreshes kthreads.

## Console flushing and threading

Legacy flushing is serialized by `console_sem`; the code also implements a spinning handoff (`console_lock_spinning_enable()`, `console_lock_spinning_disable_and_check()`, `console_trylock_spinning()`) so another printk caller can take over console output without long stalls. `console_emit_next_record()` formats one record for legacy consoles, handles dropped-message notices, calls the console `write()` callback, updates sequence, and may hand off the lock.

`console_flush_one_record()` iterates usable consoles under SRCU and uses either legacy output or `nbcon_legacy_emit_next_record()` depending on flags and current flush policy. `console_flush_all()`, `__console_flush_and_unlock()`, and `console_unlock()` drain pending records. `pr_flush()` waits for all usable consoles, optionally resetting timeout on progress.

`printk_set_kthreads_ready()` enables printer threads after early init. `printk_kthreads_check_locked()` manages the PREEMPT_RT legacy printer thread and nbcon kthreads. Shutdown stops threaded printers and falls back to atomic flushing.

## Panic, suspend, replay, and dump paths

`console_flush_on_panic()` can rewind consoles for replay-all, atomically flush nbcon consoles, and flush legacy consoles only after `printk_legacy_allow_panic_sync()` allows it. `console_suspend_all()` flushes, blocks irq_work, marks consoles suspended, and synchronizes SRCU; resume reverses that and wakes appropriate paths. `console_try_replay_all()` rewinds all consoles and triggers available flushing. The kmsg dumper API registers RCU-protected dumpers and provides line or buffer iterators over the ringbuffer for panic/oops/shutdown consumers.

## Dependencies and integration

The file integrates with the printk ringbuffer, console core, tty, sysctl, security hooks, VMCOREINFO, memblock, CPU hotplug, irq_work, SRCU/RCU, tracepoints, panic/oops state, braille helpers, nbcon helpers, and kmsg dumper consumers. It exports many public kernel symbols including `_printk`, `vprintk_emit`, console lock/list helpers, console registration APIs, syslog handling, rate-limit helpers, kmsg dump APIs, and CPU-sync helpers.

## Risks

- Locking spans semaphores, mutexes, SRCU, spinlocks, irq_work, per-CPU recursion counters, and panic exceptions. Reordering can deadlock or lose console output.
- Panic behavior intentionally drops non-panic CPU messages unless debugging is enabled; changes can hurt panic diagnostics.
- `/dev/kmsg` and syslog behavior are userspace ABI and preserve historical quirks.
- Console registration must synchronize boot consoles, real consoles, nbcon hardware locks, and braille consoles without duplicating output or racing callbacks.
- Ringbuffer resizing during early boot must preserve records across NMI and normal contexts.

## Test signals

Key signals include boot with static and dynamic log buffers, `/dev/kmsg` read/write/seek/poll behavior, syslog actions and permission failures, console command-line parsing variants, boot-to-real console handoff, legacy-only and nbcon-only flushing, PREEMPT_RT legacy kthread behavior, suspend/resume, panic replay and panic sync, kmsg dumper iteration, rate limiting, recursion suppression, CPU hotplug flushes, `CONFIG_PRINTK=n`, and `CONFIG_PRINTK_EXECUTION_CTX` metadata propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/printk/printk.c -->
