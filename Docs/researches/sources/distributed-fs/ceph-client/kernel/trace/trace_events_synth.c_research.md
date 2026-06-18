# sources/distributed-fs/ceph-client/kernel/trace/trace_events_synth.c

## Purpose
`trace_events_synth.c` implements synthetic trace events. Synthetic events are dynamic events under the `synthetic` event system whose fields are defined at runtime through tracefs or kernel APIs and whose records can be emitted by histogram actions or by kernel callers using exported `synth_event_*()` helpers. This file provides the parser, dynamic-event registration, trace-event call setup, print formatting, and direct emission APIs.

## Important APIs, Types, And Functions
The dynamic-event integration is defined by `synth_event_ops`, with `create_synth_event()`, `synth_event_show()`, `synth_event_is_busy()`, `synth_event_release()`, and `synth_event_match()`. `struct synth_event` instances own the dynamic event node, event name, fields, dynamic-field list, tracepoint, trace-event class/call, module owner, reference count, and field layout metadata. `struct synth_field` describes each field's type, name, size, signedness, string/stack/dynamic status, field position, and offset.

Parsing and registration helpers include `parse_synth_field()`, `synth_field_size()`, `synth_field_signed()`, `synth_field_is_string()`, `synth_field_is_stack()`, `synth_field_string_size()`, `alloc_synth_event()`, `register_synth_event()`, `unregister_synth_event()`, `free_synth_event()`, `__create_synth_event()`, `create_or_delete_synth_event()`, `create_synth_event()`, and `destroy_synth_event()`. Formatting and record layout use `synth_event_define_fields()`, `synth_field_fmt()`, `set_synth_event_print_fmt()`, `print_synth_event()`, `trace_string()`, and `trace_stack()`.

Exported kernel APIs include `find_synth_event()`, `synth_event_add_field()`, `synth_event_add_field_str()`, `synth_event_add_fields()`, `__synth_event_gen_cmd_start()`, `synth_event_gen_cmd_array_start()`, `synth_event_create()`, `synth_event_delete()`, `synth_event_cmd_init()`, `synth_event_trace()`, `synth_event_trace_array()`, `synth_event_trace_start()`, `synth_event_add_next_val()`, `synth_event_add_val()`, and `synth_event_trace_end()`.

## Control Flow
Tracefs creation uses the `synthetic_events` file. Writes are routed through `trace_parse_run_command()` to `create_or_delete_synth_event()`, which records the last command for diagnostics, validates minimal command shape, extracts the event name, and either deletes `!name` or creates an event from the remaining field declarations. Dynamic-event command creation also supports the `s:` prefix path through `create_synth_event()`, accepting `s:synthetic/name ...` style commands.

`__create_synth_event()` validates the event name, takes `event_mutex`, rejects duplicates, splits field declarations on semicolons, tokenizes each declaration with `argv_split()`, builds `struct synth_field` objects, enforces `SYNTH_FIELDS_MAX`, allocates the `struct synth_event`, registers a synthetic tracepoint and trace-event call, and adds the event to the dynamic-event list. Field parsing accepts scalar integer aliases, `bool`, `pid_t`, `gfp_t`, fixed-size `char[N]`, dynamic `char[]`, and `long[]` stack fields. Dynamic strings and stacks are represented as `__data_loc` fields in the trace format.

Event registration initializes the trace-event class, fields array, trace functions, tracepoint object, register callback, and raw probe function. `synth_event_define_fields()` lays out fixed fields as a flexible array of `union trace_synth_field`, reserves multiple u64 slots for fixed strings, and records each field's runtime offset. `set_synth_event_print_fmt()` constructs the `print_fmt` used by trace consumers.

Emission has two paths. Histogram actions call the synthetic tracepoint probe path through `trace_event_raw_event_synth()`, passing variable-reference values and a mapping from synthetic field positions to hist variable slots. Direct kernel callers use `synth_event_trace()` or `synth_event_trace_array()` to reserve a ring-buffer entry and copy all values at once, or use `synth_event_trace_start()`, `synth_event_add_next_val()` / `synth_event_add_val()`, and `synth_event_trace_end()` for piecewise fixed-size events. All emission paths honor event enabled/soft-disabled state and use ring-buffer nesting guards because synthetic events are commonly emitted from within other tracing paths.

Deletion uses `synth_event_delete()` or dynamic-event release. It refuses removal while the event has histogram references (`event->ref`) or dynamic trace users (`trace_event_dyn_busy()`), unregisters the event call, removes the dynamic event, frees fields, print format, tracepoint, system string, and event storage, and resets trace buffers for module-owned events to avoid stale event id interpretation after module unload.

## State And Persistence
Synthetic event definitions are live kernel dynamic-event state. They persist while the kernel is running until removed through tracefs, dynamic-event release, or `synth_event_delete()`, but they do not survive reboot. `last_cmd` under `lastcmd_mutex` is only diagnostic state for error reporting. Each event maintains an in-memory reference count used by hist triggers and module ownership to prevent unsafe removal.

Trace records emitted by synthetic events are persisted only in tracing ring buffers. Dynamic string and stack payloads are copied into each record's dynamic area; fixed strings are copied into reserved u64 slots inside the record. The tracefs `synthetic_events` seq file reflects current synthetic event definitions.

## Dependencies And Integration Points
This file depends on dynamic events, tracefs, trace-event registration, tracepoint registration, ring-buffer event reservation/commit, trace probe string helpers, event filter field definitions, kernel lockdown checks for tracefs open, module reference management, gfp flag print names, and the shared `trace_synth.h` ABI. It integrates directly with histogram triggers in `trace_events_hist.c`, which locate synthetic events by name, compare field types to hist variables, increment `event->ref`, and emit synthetic tracepoints from actions.

Kernel modules and in-kernel tracing users integrate through the exported `synth_event_*()` command-building and trace-emission APIs. User space integrates through `synthetic_events` and through generated event files under `events/synthetic/<name>/`.

## Risks
The parser must preserve backward compatibility with old space-separated field syntax while supporting semicolon-separated fields and future field-version checks. Field type validation is security- and ABI-sensitive because trace format layout, printer format strings, dynamic data locations, and emitted record size all derive from user-provided strings. Dynamic `char[]` and stack fields require exact length and offset accounting before ring-buffer reservation; incorrect accounting can corrupt trace records or print garbage.

Lifetime risks center on `event->ref`, module ownership, dynamic-event busy checks, and trace-event unregister sequencing. Histogram triggers can hold references to synthetic events; deleting an event while a hist action can still emit it would be unsafe. Module-owned synthetic events require trace-buffer reset on delete to avoid later modules reusing ids and causing stale records to be decoded with the wrong callbacks.

Direct trace APIs have correctness constraints: callers must pass values in field order, cast pointers to `u64`, avoid NULL strings, and always call `synth_event_trace_end()` after a successful piecewise start. Piecewise tracing does not support dynamic fields, and named-field and next-field setters cannot be mixed for one open trace state.

## Test Signals
Tracefs tests should create and delete synthetic events with scalar fields, `gfp_t`, fixed strings, dynamic strings, stack fields, unsigned types, arrays, invalid names, invalid types, incomplete types, too many fields, duplicate event names, and `!name` deletion. The `synthetic_events` file should show definitions without internal `__data_loc` prefixes, and generated event `format` files should show correct offsets, sizes, signedness, and filter types.

Emission tests should cover histogram `onmatch(...).trace(...)` events, direct `synth_event_trace()`, `synth_event_trace_array()`, and piecewise fixed-field tracing. Assertions should verify disabled events return success without writing, enabled events produce correctly printed records, dynamic strings and stacks are copied into the record, `gfp_t` values print symbolic flags, type/count mismatches are rejected, and deletion fails with `-EBUSY` while hist triggers or trace users still reference the event. Lockdown, lockdep, KASAN, and module unload tests are useful for tracefs security, locking, record bounds, and stale-id behavior.
