<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cma_trace.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/cma_trace.h

## Purpose

`cma_trace.h` defines the `rdma_cma` trace event set used to observe RDMA CMA state-machine activity, QP creation/destruction, lower CM events, consumer callbacks, and RDMA device add/remove notifications. It gives operators and developers structured visibility into `cma.c` without changing CM behavior.

## Important APIs, types, and functions

The file defines event classes `cma_fsm_class`, `cma_qp_class`, and `cma_client_class`, plus concrete events `cm_send_rtu`, `cm_send_rej`, `cm_prepare_mra`, `cm_send_sidr_req`, `cm_send_sidr_rep`, `cm_disconnect`, `cm_sent_drep`, `cm_sent_dreq`, `cm_id_destroy`, `cm_id_attach`, `cm_send_req`, `cm_send_rep`, `cm_qp_destroy`, `cm_qp_create`, `cm_req_handler`, `cm_event_handler`, `cm_event_done`, `cm_add_one`, and `cm_remove_one`.

Most events record the CMA resource ID, source and destination socket addresses, TOS, and sometimes QP number, PD ID, WR capacities, return code, lower IB CM event, RDMA CM event, or device name. The `IB_QP_TYPE_LIST` helpers register QP type enum values and print them symbolically through `rdma_show_qp_type()`.

## Control flow

At compile time the trace macros emit declarations or definitions depending on whether `CREATE_TRACE_POINTS` is set. At runtime, `cma.c` calls `trace_cm_*` helpers at key transitions: attach, QP create/destroy, send REQ/REP/RTU/REJ/SIDR, disconnect, request handler entry, consumer handler entry/exit, ID destroy, and device client add/remove. The tracepoint fast paths are cheap when disabled and write structured records when enabled by ftrace/perf.

## State and persistence

Trace events copy selected fields into trace buffers at event time. They do not own CMA objects or persist state beyond kernel trace storage. Address fields are copied as `sockaddr_in6`-sized byte arrays so `%pISpc` can print IPv4/IPv6 socket addresses consistently. The data represents a point-in-time snapshot and may not reflect later ID changes.

## Dependencies and integration points

The header depends on Linux tracepoint APIs, `trace/misc/rdma.h` helpers such as RDMA/IB event stringification, RDMA verb QP type definitions, and `struct rdma_id_private` fields. `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` are set so `trace/define_trace.h` can find the header from `cma_trace.c`. The primary integration point is `cma.c`; trace consumers are tracefs, perf, and debugging scripts.

## Risks

Tracepoint field layouts become part of tooling expectations, so renaming events or changing fields can break observability. The code assumes source and destination address storage can be meaningfully copied into a `sockaddr_in6`-sized buffer; unusual AF_IB rendering may be less informative than IP rendering. Event prototypes expose private CMA fields, so structure changes must update trace assignments. Tracepoint headers are sensitive to include guards, `TRACE_HEADER_MULTI_READ`, and `TRACE_INCLUDE_*` settings.

## Test signals

Builds with `CONFIG_TRACING` should compile without duplicate definitions. Runtime tests should enable `events/rdma_cma/*`, perform RDMA CM connect/listen/multicast/device add-remove operations, and verify event records contain expected CM IDs, addresses, QP types, statuses, consumer return codes, and device names. `perf list` or tracefs event enumeration should show the `rdma_cma` group.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cma_trace.h -->
