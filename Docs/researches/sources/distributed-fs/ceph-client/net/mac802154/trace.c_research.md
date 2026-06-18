# sources/distributed-fs/ceph-client/net/mac802154/trace.c

Purpose: instantiates mac802154 tracepoints defined in `trace.h`.

Important APIs and functions: defines `CREATE_TRACE_POINTS` after including cfg802154 and driver ops headers, causing tracepoint storage and registration code to be emitted for the header declarations.

Control flow and state: no runtime logic beyond tracepoint instantiation; guarded by `#ifndef __CHECKER__`.

Dependencies and integration: depends on `trace.h`, `driver-ops.h`, and kernel ftrace/tracepoint infrastructure. Build placement must ensure this file is compiled exactly once for the trace system.

Risks and test signals: duplicate inclusion or missing compilation would break tracepoint symbols. Build/link tests and enabling mac802154 trace events are the primary validation signals.
