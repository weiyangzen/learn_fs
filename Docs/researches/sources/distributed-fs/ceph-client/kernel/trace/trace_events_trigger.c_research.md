# sources/distributed-fs/ceph-client/kernel/trace/trace_events_trigger.c

## Purpose
Implements trace event trigger infrastructure for tracefs event `trigger` files. It lets users attach commands such as `traceon`, `traceoff`, `snapshot`, `stacktrace`, `enable_event`, `disable_event`, and histogram-related commands to trace events, optionally with counts and filters. Runtime trigger dispatch is integrated into tracepoint event emission so triggers can fire before or after an event is committed.

## Important APIs, Types, And Functions
The central state is `struct event_trigger_data`, owned by a per-event `trace_event_file->triggers` RCU list and configured by `struct event_command` operations. The file maintains a global `trigger_commands` registry protected by `trigger_cmd_mutex`, a global `named_triggers` list for shared named trigger data, and a deferred free path using `trigger_data_free_list`, `trigger_data_kthread_mutex`, and `trigger_kthread`.

Primary exported or shared APIs include `event_triggers_call()`, `event_triggers_post_call()`, `__trace_trigger_soft_disabled()`, `trigger_process_regex()`, `register_event_command()`, `unregister_event_command()`, `event_trigger_count()`, `event_trigger_init()`, `trace_event_trigger_enable_disable()`, `clear_event_triggers()`, `update_cond_flag()`, `trigger_data_alloc()`, `event_trigger_parse_num()`, `set_trigger_filter()`, named-trigger helpers, and enable/disable trigger helpers. `event_trigger_fops` wires the event `trigger` file to open/read/write/release callbacks.

## Control Flow
When a trace event fires, `event_triggers_call()` walks `file->triggers` under RCU. It skips paused entries, checks optional event filters against the just-created record, executes immediate triggers through `data_ops_trigger()`, and returns a bitmask for post triggers. `event_triggers_post_call()` later walks the same list and executes triggers whose `trigger_type` bit was returned. `__trace_trigger_soft_disabled()` is the fast-path gate for events that are otherwise soft-disabled but still need trigger-mode evaluation.

User configuration enters through tracefs `trigger` writes. `event_trigger_regex_write()` copies a bounded user buffer, locks `event_mutex`, resolves the `trace_event_file`, and calls `trigger_process_regex()`. The parser splits command name, optional removal prefix `!`, colon parameters, and optional `if` filters. Generic `event_trigger_parse()` allocates trigger data, parses count values, installs filters, bumps temporary references, and calls the command-specific register function. Removal paths create a temporary match object and call the command-specific unregister operation.

Registration adds trigger data to `file->triggers` with `list_add_rcu()`, updates `EVENT_FILE_FL_TRIGGER_COND` when filters/post triggers/record-dependent commands require deferred evaluation, and toggles trigger mode by incrementing `tm_ref` through `trace_event_trigger_enable_disable()`. Enable/disable-event triggers also hold a reference to the target event call and enable soft mode on that target.

## State And Persistence
Trigger definitions persist in kernel memory while present in the tracefs event trigger list. Counts are stored in `event_trigger_data->count`, with `-1` meaning unlimited. Filters are RCU-published via `event_trigger_data->filter` and mirrored as printable `filter_str`. `tm_ref`, `sm_ref`, and event file flags record trigger-mode and soft-mode state. Named triggers share common data by storing a first owner in `named_triggers` and pointing later entries at it through `named_data`.

Freeing is intentionally deferred. `trigger_data_free()` clears filters, queues data on an llist, and wakes the `trigger_data_free` kthread, which calls `tracepoint_synchronize_unregister()` before `kfree()`. Boot-time failures are handled by queuing and draining later in `trigger_data_free_init()` or synchronously if kthread creation fails.

## Dependencies And Integration Points
The file depends on trace core types in `trace.h`, trace event filters, tracefs file lifetimes, RCU list traversal, tracepoint unregister synchronization, the tracing snapshot subsystem, stack tracing, dynamic ftrace histogram support, and event module reference helpers. It integrates with trace event emission paths, event file flags, `tracing_on`, snapshot buffers, stack capture, and cross-event enable/disable behavior.

## Risks
The main risks are lifetime and concurrency bugs: trigger data is read from tracepoint context while users can remove triggers, so RCU and `tracepoint_synchronize_unregister()` ordering is critical. Filter replacement must not expose partially initialized filters or leak failed filters. Register/unregister paths must keep `tm_ref`, target event references, and soft-mode flags balanced, especially on partial failures. Counted triggers execute on multiple CPUs without strong serialization beyond the trigger data operations, so count semantics are best-effort for concurrent hits. Named triggers share data across entries, making pause/unpause and deletion correctness dependent on consistent `name` handling.

## Test Signals
Useful signals are tracefs trigger smoke tests: writing valid/invalid commands, removing with `!`, reading back available and active triggers, and checking `traceon`, `traceoff`, `stacktrace`, `snapshot`, and enable/disable behavior. Filter tests should verify `if` syntax, failed filter cleanup, and conditional post-trigger execution. Concurrency tests should repeatedly add/remove triggers while generating the event and watching for KASAN/KCSAN/RCU warnings, leaked event references, and stale trigger-mode flags.
