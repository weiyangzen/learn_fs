<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/trace.c -->
# sources/distributed-fs/ceph-client/net/handshake/trace.c

## Purpose
Instantiates transport security handshake tracepoints.

## APIs, Types, and Functions
Defines `CREATE_TRACE_POINTS` and includes `trace/events/handshake.h` after importing network, socket, inet, netlink, genetlink, and internal handshake types.

## Control Flow, State, and Persistence
There is no runtime logic beyond tracepoint definition generation at build time. This translation unit causes the tracepoint storage and metadata declared in the trace header to be emitted once.

## Dependencies and Integration
Depends on the trace event definitions for handshake, TLS alerts, and related socket context. It is linked into `handshake.o` by the Makefile and used by `alert.c`, `netlink.c`, and `request.c`.

## Risks and Test Signals
Risks are mainly build integration failures if trace event prototypes drift from included types. Test signals are successful build with tracing enabled and observable events for submit, notify errors, accept, done, cancel, destruct, TLS alert send/receive, and content type parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/trace.c -->
