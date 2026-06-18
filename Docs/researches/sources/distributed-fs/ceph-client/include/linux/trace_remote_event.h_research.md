# sources/distributed-fs/ceph-client/include/linux/trace_remote_event.h

## Purpose
Defines the metadata and format macros for remote trace events consumed through `trace_remote`.

## Important APIs, Types, And Functions
Exports `struct remote_event_hdr`, `struct remote_event`, `REMOTE_EVENT_NAME_MAX`, `RE_STRUCT`, `re_field`, and `REMOTE_EVENT_FORMAT()`. A remote event holds name, id, enabled state, parent remote pointer, field descriptors, print format, and a `print()` callback.

## Control Flow
The header has no runtime control flow. Providers define packed-ish event payload structs with `REMOTE_EVENT_FORMAT()`, attach field metadata and print functions, and tracefs uses those to expose and render remote records.

## State, Persistence, And Dependencies
Event state includes the enabled bit, metadata pointers, and format callback owned by the remote provider. Dependencies are forward declarations of tracing structures.

## Integration Points
Pairs with `trace_remote_register()` and tracefs event presentation. `struct remote_event_hdr.id` maps raw records back to metadata entries.

## Risks And Test Signals
Risks include id/name mismatches, format structs not matching remote ring-buffer payloads, dangling field or print-format pointers, and name truncation at 30 bytes. Test signals are event format dumps, raw-record print tests, enable/disable propagation, and payload-size/layout assertions.
