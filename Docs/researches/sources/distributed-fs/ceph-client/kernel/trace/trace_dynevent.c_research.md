# sources/distributed-fs/ceph-client/kernel/trace/trace_dynevent.c

## Purpose
`trace_dynevent.c` implements the generic dynamic event control layer behind tracefs `dynamic_events`. It manages dynamic event type registration, creation dispatch, deletion, listing, reference checks, and a command-building helper API used by kprobe and synthetic event generators.

## Important APIs, types, and functions
Key globals are `dyn_event_ops_mutex`, `dyn_event_ops_list`, and `dyn_event_list`. Public functions include `trace_event_dyn_try_get_ref()`, `trace_event_dyn_put_ref()`, `trace_event_dyn_busy()`, `dyn_event_register()`, `dyn_event_release()`, `dyn_event_create()`, `dyn_events_release_all()`, sequence callbacks, and dynevent command helpers (`dynevent_cmd_init()`, `dynevent_arg_init()`, `dynevent_arg_add()`, `dynevent_arg_pair_init()`, `dynevent_arg_pair_add()`, `dynevent_str_add()`, `dynevent_create()`).

## Control flow
Tracefs writes to `dynamic_events` call `trace_parse_run_command()` with `create_dyn_event()`. Commands beginning with `-` or `!` route to `dyn_event_release()`; otherwise `create_dyn_event()` walks registered dynamic event operation providers until one accepts the command or reports a non-cancel error. Reads iterate `dyn_event_list` under `event_mutex` and call each event type's `show()` method. Opening with write-truncate releases all dynamic events after lockdown and trace open checks.

## State and persistence behavior
Dynamic event providers are registered in `dyn_event_ops_list`; live dynamic events are linked in `dyn_event_list` and tied to `trace_event_call` objects marked `TRACE_EVENT_FL_DYNAMIC`. Reference counts on dynamic trace events prevent unsafe deletion while users hold references. Command builders use caller-supplied buffers and `seq_buf` state rather than allocating persistent command storage.

## Dependencies and integration points
The file depends on tracefs/debugfs infrastructure, security lockdown checks, `event_mutex`, `trace_event_sem`, `ftrace_events`, `trace_parse_run_command()`, error logging, and type-specific providers such as kprobes, uprobes, fprobes, eprobes, and synthetic events.

## Risks
Deletion parsing is subtle because commands can match event-only, system/event, and extra arguments through type-specific `match()` functions. `dyn_events_release_all()` aborts on busy events and may partially release events on other errors. Locking boundaries matter: operation registration is protected by `dyn_event_ops_mutex`, live event mutation by `event_mutex`, and reference lookup by `trace_event_sem`.

## Test signals
Exercise `dynamic_events` create/list/delete/truncate flows for every registered provider. Verify busy deletion returns `-EBUSY`, malformed commands produce trace errors, lockdown blocks open, command-builder tests reject oversized buffers, and repeated create/delete leaves no events in `dyn_event_list`.
