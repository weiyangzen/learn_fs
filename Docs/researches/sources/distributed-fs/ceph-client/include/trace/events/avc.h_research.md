# sources/distributed-fs/ceph-client/include/trace/events/avc.h

## Purpose
`avc.h` exposes a SELinux AVC audit tracepoint for permission-check audit decisions.

## Important APIs, types, and functions
The single event is `selinux_audited`. It records fields from `struct selinux_audit_data`: requested, denied, audited, and result, plus source context, target context, and target class strings.

## Control flow
SELinux audit code calls this event after constructing audit data and context strings. The tracepoint copies strings with `__assign_str()` and emits a formatted record.

## State and persistence behavior
There is no header-owned state. Each event snapshots one audited access decision and its string contexts.

## Dependencies and integration points
It depends on SELinux audit data definitions available to the call site and `<linux/tracepoint.h>`. It integrates SELinux decisions with ftrace/perf/BPF monitoring.

## Risks and test signals
Risks include leaking sensitive security contexts to trace readers, string lifetime mistakes at call sites, and missing non-audited denials. Test signals are SELinux policy tests that produce audited allow/deny decisions and verify requested/denied/audited bitmasks and result codes.
