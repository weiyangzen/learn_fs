# sources/distributed-fs/ceph-client/include/trace/define_remote_events.h

## Purpose
`define_remote_events.h` is the remote-event analogue of the kernel tracepoint generator. It consumes a header named by `REMOTE_EVENT_INCLUDE_FILE` and expands each `REMOTE_EVENT()` declaration into a packed event-format structure, a printer, field metadata, and a `struct remote_event` registration object.

## Important APIs, types, and functions
The important surface is macro based: `REMOTE_EVENT_INCLUDE()`, `REMOTE_PRINTK_COUNT_ARGS()`, `remote_printk()`, `RE_PRINTK()`, `re_field()`, and `REMOTE_EVENT()`. It depends on `REMOTE_EVENT_FORMAT()` and `struct remote_event` from the remote trace event support headers. `__REMOTE_EVENT_SECTION()` optionally places generated descriptors in a named linker section when `REMOTE_EVENT_SECTION` is defined.

## Control flow
The file includes the remote-event declaration file twice. The first pass defines `REMOTE_EVENT()` to emit a `remote_event_print_<name>()` function that casts the raw event record to `struct remote_event_format_<name>` and writes to a `trace_seq`. The second pass redefines `re_field()` and `REMOTE_EVENT()` to emit a field-array, print-format string, and initialized `remote_event_<name>` descriptor.

## State and persistence behavior
There is no runtime mutable state in this header. Persistent build artifacts are generated C symbols: per-event field arrays, format strings, print callbacks, and optional linker-section entries. The trace data state lives in remote-event producers and consumers.

## Dependencies and integration points
It integrates with `<linux/trace_events.h>`, `<linux/trace_remote_event.h>`, `<linux/trace_seq.h>`, `is_signed_type()`, `__COUNT_ARGS`, `CONCATENATE`, and `__stringify`. Users must define `REMOTE_EVENT_INCLUDE_FILE`, and their event declarations must be valid under both passes.

## Risks and test signals
Risks are macro ABI drift, mismatched `re_field()` declarations versus binary payload layout, malformed `RE_PRINTK()` arguments, and section-name mistakes that silently drop descriptors from discovery. Test signals are compile coverage of a remote-event declaration file, inspection of generated `remote_event_fields_*` arrays, remote trace formatting through `trace_seq`, and linker-map checks when `REMOTE_EVENT_SECTION` is used.
