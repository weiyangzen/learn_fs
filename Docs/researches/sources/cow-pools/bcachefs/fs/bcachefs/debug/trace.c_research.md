# File Research: sources/cow-pools/bcachefs/fs/bcachefs/debug/trace.c

Instantiates bcachefs tracepoints.

Key behavior:
- Includes core bcachefs, allocator, btree, data, and utility headers needed by tracepoint format code.
- Defines `CREATE_TRACE_POINTS` before including `debug/trace.h`, causing tracepoint definitions to be emitted in this compilation unit.

Filesystem relevance:
- Provides the concrete tracepoint objects used by bcachefs runtime tracing and debugging.
