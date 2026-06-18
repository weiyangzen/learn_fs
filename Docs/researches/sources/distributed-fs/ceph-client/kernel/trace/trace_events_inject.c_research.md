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
