# sources/distributed-fs/ceph-client/tools/perf/util/tool.c

## Purpose

`tool.c` initializes perf event-processing dispatch tables and implements default handlers and delegation wrappers. It lets each perf command override only the event callbacks it cares about while preserving safe defaults for all perf record types.

## Important APIs, Types, and Functions

`perf_tool__init()` fills `struct perf_tool` callbacks and option flags. Default stubs include sample, generic event, finished-round, attr/event-update, tracing data, stat, time-conv, thread/cpu-map, compressed data, BPF metadata, and schedstat handlers. `perf_tool__compressed_is_stub()` detects missing zstd support. `delegate_tool__init()` builds a wrapper whose callbacks forward to another `perf_tool`. With zstd support, `perf_session__process_compressed_event()` streams `PERF_RECORD_COMPRESSED` and `PERF_RECORD_COMPRESSED2` payloads into session decompression buffers.

## Control Flow and State

Initialization sets defaults such as ordered-events mode, feature-header behavior, and deferred callchain merge. Ordered tools get real finished-round handling; unordered tools get a stub. The auxtrace stub consumes auxtrace bytes from pipes so stream alignment remains valid even when a command ignores auxtrace. Compressed handling mmaps a decompression node, preserves leftovers from the previous node, appends to the active decompression chain, and records source file offset/path metadata.

## Dependencies and Integration Points

It depends on session, data, event, stat, header, TSC, zstd helpers when enabled, and ordered-events. Every perf command that processes perf.data or live events relies on this callback table.

## State and Persistence Behavior

`struct perf_tool` is caller-owned state. Delegates store a pointer to an existing tool and do not own it. Decompression nodes are attached to `session->active_decomp` for later event replay.

## Risks and Test Signals

Risks include callback signature mismatch, missing default consumption of variable-length pipe payloads, decompression buffer sizing bugs, and incomplete delegate forwarding when new callbacks are added. Tests should initialize tools with ordered and unordered modes, process ignored auxtrace from a pipe, inspect dump output for stubs, read compressed perf.data with and without zstd support, and verify delegate callbacks forward all event classes.
