# subset-b-006072 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_events_hist.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_events_hist.c

## Purpose
`trace_events_hist.c` implements Linux ftrace histogram triggers. A `hist:` trigger attached to a trace event groups matching records by key fields, accumulates value fields, exposes sorted histogram output through tracefs, and can run actions such as `onmatch(...).trace(...)`, `onmax(...).save(...)`, `onchange(...).snapshot()`, and hist enable/disable commands. In this repository path it is generic upstream kernel tracing infrastructure, not Ceph-specific filesystem code.

## Important APIs, Types, And Functions
The core runtime object is `struct hist_trigger_data`, which owns parsed attributes, `struct hist_field *fields[]`, value/key counts, sort keys, the backing `struct tracing_map`, variable references, actions, field variables, save variables, and the owning `struct trace_event_file`. `struct hist_field` represents keys, values, constants, expressions, aliases, variables, variable references, timestamps, CPU/comm pseudo-fields, strings, stack traces, and arithmetic nodes. `struct hist_trigger_attrs` captures parsed tracefs command options such as `keys=`, `vals=`, `sort=`, `name=`, `clock=`, `size=`, `pause`, `cont`, `clear`, and `nohitcount`.

Important parser and builder functions include `parse_hist_trigger_attrs()`, `parse_assignment()`, `parse_action()`, `parse_var_defs()`, `parse_field()`, `parse_atom()`, `parse_expr()`, `parse_unary()`, `create_hist_field()`, `create_val_fields()`, `create_var_fields()`, `create_key_fields()`, `create_sort_keys()`, `parse_actions()`, `create_actions()`, and `create_hist_data()`. Important variable/action helpers include `find_var_field()`, `find_event_var()`, `create_var_ref()`, `resolve_var_refs()`, `create_field_var_hist()`, `trace_action_create()`, `track_data_create()`, `onmatch_parse()`, `track_data_parse()`, and `action_create()`.

Runtime paths are centered on `event_hist_trigger()`, `hist_trigger_elt_update()`, `hist_trigger_actions()`, `hist_fn_call()`, and the many `hist_field_*()` evaluator functions. Tracefs output and diagnostics use `hist_show()`, `event_hist_open()`, `hist_trigger_print_key()`, `hist_trigger_print_val()`, `print_entries()`, `event_hist_trigger_print()`, `hist_debug_show()`, and `event_hist_debug_open()`. Registration is provided by `trigger_hist_cmd`, `register_trigger_hist_cmd()`, `trigger_hist_enable_cmd`, `trigger_hist_disable_cmd`, and `register_trigger_hist_enable_disable_cmds()`.

## Control Flow
A user writes a `hist:` trigger to an event's tracefs `trigger` file. `event_hist_trigger_parse()` splits the optional filter from the trigger body, normalizes `.sym-offset` for the expression parser, parses attributes, constructs `hist_trigger_data`, installs filter state, handles remove/update-only operations, creates actions and variable references, initializes the tracing map, registers the trigger, and enables it on the event. Named triggers are reconciled with existing named trigger data so that compatible named histograms can be shared across event files.

The parser first turns `keys=`, `vals=`, variable assignments, sort options, clock options, and action strings into `hist_trigger_attrs`. Value fields always include an internal hitcount, unless `nohitcount` suppresses display and a non-hitcount value exists. `parse_expr()` recursively builds expression trees for `+`, `-`, `*`, `/`, and explicit unary minus, limits expression nesting, rejects string operands, checks timestamp-unit compatibility, folds constant expressions, and preselects optimized division evaluators for constant divisors. Key creation rejects variable references because keys must be derived from the current record and stored as stable map keys.

When a trace event fires, `event_hist_trigger()` obtains a per-CPU `hist_pad`, evaluates key fields from the record, builds a compound key when necessary, resolves non-self variable references, inserts or finds the `tracing_map` element, updates sums and variables through `hist_trigger_elt_update()`, resolves self references, runs actions, and wakes histogram poll waiters. `hist_trigger_elt_update()` updates sum fields, map variables, saved strings/stack traces, and field variables. Actions either emit synthetic events through `trace_synth()`, track max/change values before saving data, or request conditional snapshots when `CONFIG_TRACER_SNAPSHOT` is available.

Read-side output opens the per-event `hist` or `hist_debug` file, sorts map entries with configured sort keys, computes percent and graph statistics, prints formatted keys and values, and appends action state such as max/change saved variables or snapshot details. Clear/pause/continue flows match existing triggers and either clear the map, set paused flags, or continue a paused trigger without rebuilding the whole trigger.

## State And Persistence
All histogram state is in memory. Trigger configuration is stored in `event_trigger_data` plus `hist_trigger_data` on the owning `trace_event_file`. Aggregated data lives in `struct tracing_map`, whose elements own `struct hist_elt_data` for saved `comm`, string variables, stack variable storage, and per-trigger variable reference values. Cross-trigger variables are tracked on `trace_array->hist_vars`, with a trace-array reference held while variables are globally visible.

The file also owns global diagnostic state for the last histogram command (`last_cmd`, `last_cmd_loc`) and per-CPU scratch storage (`hist_pads`, `hist_pad_cnt`, `hist_pad_ref`). Named triggers are persisted only as live kernel objects and disappear when unregistered. Tracefs files show current state but do not persist it across reboot or module/kernel teardown.

## Dependencies And Integration Points
This file depends on ftrace event infrastructure (`trace_event_file`, `trace_event_call`, event triggers, filters, named triggers), `tracing_map` for aggregation and sorting, tracefs/seq_file for presentation, ring-buffer timestamps for `common_timestamp`, stacktrace capture, syscall-name formatting, conditional snapshots, RCU-trigger lists, `event_mutex`, `trace_types_lock`, and trace-array clocks. It integrates tightly with `trace_events_synth.c` through `struct synth_event`, `find_synth_event()`, and synthetic tracepoint emission used by `onmatch` and `trace` actions.

The tracefs integration surface is the `hist` trigger command plus `enable_hist` and `disable_hist` commands. External user-visible behavior is driven by command strings such as `keys=pid`, `vals=latency`, `sort=hitcount.descending`, `name=foo`, `onmax($lat).save(...)`, and `onmatch(sched.sched_wakeup).trace(...)`.

## Risks
The highest-risk area is parser and lifetime correctness. Hist triggers create nested expression trees, variable aliases, cross-event variable references, automatically generated field-variable histograms, action objects, and synthetic-event references; a failed create/remove path must unwind all of these without leaking or freeing shared named trigger state too early. Variable reference safety is subtle because one trigger cannot be removed while another trigger references its variables, and `remove_hist_vars()` intentionally refuses removal when `check_var_refs()` finds users.

Runtime risks include incorrect key construction for strings, dynamic strings, relative dynamic strings, stack traces, and compound keys; overflow or truncation around `HIST_KEY_SIZE_MAX`, `STR_VAR_LEN_MAX`, bucket sizing, percent calculation, and optimized division; and context constraints around per-CPU `hist_pad` nesting from normal, softirq, IRQ, and NMI contexts. Timestamp fields have additional risk because the trigger may switch the trace clock and disable filter buffering while timestamp histograms are active.

Concurrency risks are guarded by `event_mutex`, RCU trigger traversal, tracepoint synchronization during clear/remove, per-CPU pad accounting, and tracing-map internals. Changes must preserve lock ordering around trigger registration, trace-array references, snapshot locks, map operations, and synthetic-event reference counts.

## Test Signals
Useful test signals come from ftrace selftests that create, read, pause, continue, clear, and remove histogram triggers. Coverage should include numeric keys, string keys, stacktrace keys, `common_cpu`, `common_comm`, `common_timestamp.usecs`, bucket/log2 modifiers, hex/sym/syscall formatting, `nohitcount`, sort validation, percent/graph output, expression parsing, division by zero rejection, timestamp-unit mismatch rejection, duplicate variables, ambiguous variables, and key variable-reference rejection.

Action tests should create synthetic events and verify `onmatch(...).trace(...)`, `trace(...)` keyword handling, `onmax`, `onchange`, `save`, and snapshot behavior where enabled. Cross-event field-variable tests should verify that compatible helper histograms are automatically created and unregistered. Negative tests should check error logging through `tracing_log_err()`, `-EBUSY` removal when variables are referenced, and duplicate/named-trigger mismatch handling. Runtime stress with lockdep, KASAN, KCSAN, and concurrent tracefs trigger updates is valuable because most bugs here are lifetime or race failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_events_hist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_events_inject.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_events_inject.c

## Purpose
`trace_events_inject.c` implements trace event injection through a tracefs file operation. It lets privileged tracefs users write field assignments for an existing trace event, constructs a synthetic raw event record matching that event's format, and commits the record into the event's trace buffer. The implementation is generic tracing test/debug infrastructure and is not Ceph-specific.

## Important APIs, Types, And Functions
The exported object is `event_inject_fops`, with `tracing_open_file_tr`, write support through `event_inject_write()`, read rejection through `event_inject_read()`, and `tracing_release_file_tr`. `trace_inject_entry()` reserves and commits the record with `trace_event_buffer_reserve()` and `trace_event_buffer_commit()` under scheduler RCU read-side protection.

Parsing and record construction are handled by `parse_field()`, `trace_get_entry_size()`, `trace_alloc_entry()`, and `parse_entry()`. The code uses `struct trace_event_call`, `struct trace_event_file`, `struct ftrace_event_field`, `struct trace_event_buffer`, filter helpers such as `is_string_field()` and `is_function_field()`, and field filter types such as `FILTER_STATIC_STRING`, `FILTER_DYN_STRING`, and `FILTER_RDYN_STRING`.

## Control Flow
`event_inject_write()` rejects writes of one page or larger, copies the user buffer with NUL termination, trims whitespace, takes `event_mutex`, obtains the target `trace_event_file` from the opened file, parses the assignment string into a binary entry, injects it when parsing succeeds, drops the mutex, frees temporary memory, advances the file position by the number of bytes written into the trace record, and returns the original user byte count on success.

`parse_entry()` allocates a zeroed record initialized with `tracing_generic_entry_update()`, then repeatedly calls `parse_field()` while the command string still contains assignments. `parse_field()` accepts `field=value` pairs, finds the field by name, parses numeric values with signedness-aware `kstrtoll()` or `kstrtoull()`, and parses quoted string values with simple backslash skipping. It returns the number of consumed bytes so the caller can continue scanning the same command line.

`trace_alloc_entry()` computes the base event payload size from the event's fields and prepares empty defaults for string-like fields. Dynamic and relative dynamic strings get zero-length `__data_loc` metadata pointing to the end of the fixed entry. Pointer string fields are initialized to an empty kernel string. Static string storage remains part of the fixed record.

When `parse_entry()` applies a parsed field, numeric fields are copied according to their declared size of 1, 2, 4, or 8 bytes. Static strings are copied directly into the fixed field. Dynamic and relative dynamic strings grow the entry with `krealloc()`, copy the string to the new dynamic tail, and update the packed length/location value. Non-static pointer string fields are not populated from user-supplied pointers; they are set to the sentinel string `STATIC STRING CAN NOT BE INJECTED`.

## State And Persistence
The file stores no durable state. Each write allocates a temporary record, injects it into the tracing ring buffer, and frees it. The only persistent effect is a new trace-buffer entry in the current trace array. File position is advanced after a successful write, but injection commands are otherwise stateless.

## Dependencies And Integration Points
This code depends on tracefs event files, event field metadata, event filtering type information, `event_mutex`, tracing ring-buffer reservation/commit helpers, generic trace entry initialization, and user-copy helpers. It integrates with the per-event `inject` tracefs file, so the target event's format file is the contract that determines valid field names, offsets, sizes, signedness, and string layout.

## Risks
The main risks are malformed input handling, event-format layout correctness, and memory safety when dynamically resizing records. Numeric parsing must reject strings for numeric fields, nonnumeric suffixes, and invalid signedness conversions. String parsing must reject unterminated quotes and values longer than `MAX_FILTER_STR_VAL`. Dynamic string injection must keep fixed-field `__data_loc` offsets consistent after `krealloc()`, including relative dynamic strings whose location is relative to the field.

There is also a semantic risk that injected records are not produced by the event's normal call site, so fields not explicitly set are zero or default string values. Injection of function fields is rejected because those fields are not ordinary payload data. Pointer-string fields are deliberately not trusted as user pointers, which avoids dereferencing arbitrary addresses but means injected output may contain the sentinel instead of the requested value.

## Test Signals
Test signals should include writing valid numeric, negative signed, hexadecimal, static string, dynamic string, and relative dynamic string assignments to an event's `inject` file and confirming the event appears in the trace buffer with the expected values. Negative tests should cover unknown fields, missing `=`, strings assigned to numeric fields, numbers assigned to string fields, unterminated quotes, oversized strings, function fields, invalid numeric suffixes, writes at or above `PAGE_SIZE`, and read attempts returning `-EPERM`.

Concurrency and safety checks should run with lockdep and KASAN while injecting into enabled and disabled events. Format-sensitive tests should compare injected event bytes against the event's `format` metadata, especially for `__data_loc` strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_events_inject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_events_synth.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_events_synth.c -->
