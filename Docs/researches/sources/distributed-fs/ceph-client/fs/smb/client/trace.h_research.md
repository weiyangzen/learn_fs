# sources/distributed-fs/ceph-client/fs/smb/client/trace.h

Read coverage: full file.

## Purpose
This header defines the CIFS/SMB client tracepoint surface for the Linux tracing subsystem. It is included by client code that emits `trace_smb3_*`, `trace_cifs_*`, and `trace_smb3_eio` events for request lifecycles, I/O errors, credit accounting, session/tree connection references, reconnects, authentication, leases, locks, opens, ioctls, shutdowns, and structured EIO reasons.

## Important APIs, types, and functions
The file exports trace enums through macro lists: `smb_eio_traces`, `smb3_rw_credits_traces`, and `smb3_tcon_ref_traces`. These become `enum smb_eio_trace`, `enum smb3_rw_credits_trace`, and `enum smb3_tcon_ref_trace`, are registered with `TRACE_DEFINE_ENUM`, and are printed through `__print_symbolic`.

The tracepoint API is mostly declarative: `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, and `TRACE_EVENT`. Event classes cover read/write success and failure, other handle-based operations, copy range/reflink, EOF updates, fd operations, byte-range locks, query/set/notify info, compound path operations, SMB command enter/done/error, MID latency, function enter/exit, tree connect, open/create, leases, transport connect/reconnect, Kerberos auth, tcon refs, read/write credit flow, and detailed EIO causes.

## Control flow
At compile time, the tracing macros generate event descriptors and inline trace helpers. Runtime control flow is external: call sites collect identifiers such as xid, fid, tid, session id, offsets, lengths, credit counts, MID numbers, hostnames, and socket addresses, then call the generated trace helper. The tracepoint copies scalar fields and selected strings or sockaddr storage into the event payload inside `TP_fast_assign`, and `TP_printk` formats the tracefs output.

## State and persistence behavior
The header itself persists no SMB state. Its only durable ABI-like surface is trace event names, field names, enum values, and printed strings exposed under tracefs/perf/ftrace. Some tracepoints copy transient strings, user names, hostnames, and socket addresses into ring-buffer records, so the observable trace payload survives beyond the originating stack frame.

## Dependencies and integration points
The file depends on kernel tracepoint infrastructure plus socket address definitions. It integrates with transport, session setup, tree connect, read/write, lease, close, xattr/security, reparse, compression, and error-handling paths throughout the SMB client. `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE trace` require a matching include arrangement when `trace/define_trace.h` instantiates the events.

## Risks and test signals
Tracepoint field names and print formats are user-visible diagnostics; renaming or changing enum order can break tracing scripts. The copy range print formats display the source fid using `target_fid` in the current format expression, which is a diagnostic accuracy risk. String tracepoints can expose host/user/path data to privileged tracing consumers. Build tests should compile with tracing enabled, and runtime tests should enable representative `cifs:*` events in tracefs while exercising mount, negotiate/session setup, open/read/write/close, lease break, reconnect, copychunk, query info, and xattr paths.
