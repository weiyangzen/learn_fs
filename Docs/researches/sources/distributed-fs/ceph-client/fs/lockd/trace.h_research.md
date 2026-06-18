# sources/distributed-fs/ceph-client/fs/lockd/trace.h

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/trace.h` declares lockd trace events for NLM client lock operations. It defines symbolic NLM status rendering and an event class capturing lock owner, server address, file-handle hash, range, and status. The source was read as a complete 107-line file for this report.

## Important APIs, Types, and Functions

Important macros include `TRACE_SYSTEM lockd`, `NLM_STATUS_LIST`, `show_nlm_status`, `DECLARE_EVENT_CLASS(nlmclnt_lock_event)`, and `DEFINE_NLMCLNT_EVENT`. Declared events are `nlmclnt_test`, `nlmclnt_lock`, `nlmclnt_unlock`, and `nlmclnt_grant`. Event fields include owner-handle CRC, `svid`, NFS file-handle hash, range start/length, sockaddr, and status.

## Control Flow

The header expands into trace event declarations and, when included by `trace.c` with `CREATE_TRACE_POINTS`, definitions. At runtime, callers hit generated tracepoint probes; the fast-assign block hashes the owner handle and file handle, stores the lock range and status, and copies the sockaddr for formatted output.

## State and Persistence Behavior

No persistent lockd state is owned here. Trace records are transient tracing-buffer entries managed by the kernel tracing subsystem.

## Dependencies and Integration Points

It includes `linux/tracepoint.h`, `linux/crc32.h`, `linux/nfs.h`, and `lockd.h`. It integrates with ftrace/perf tracepoint tooling and the generated trace include mechanism via `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE`.

## Risks and Edge Cases

The status list differs with `CONFIG_LOCKD_V4`; symbolic rendering must match available NLM constants. Trace output intentionally hashes owner and file handles rather than dumping raw bytes. The event uses `lock->lock_start` and `lock->lock_len`, so callers must keep those legacy fields populated if traces are expected to show meaningful ranges.

## Test Signals

Build with tracing, list events under the lockd trace system, enable `nlmclnt_*` events during client lock tests, and verify status names, sockaddr formatting, and range fields for NLMv3 and NLMv4 operations.
