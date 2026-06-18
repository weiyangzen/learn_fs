# sources/distributed-fs/ceph-client/drivers/infiniband/core/cm_trace.h

## Purpose

`cm_trace.h` declares tracepoints for the InfiniBand Connection Manager. The events expose CM ID state, LAP state, reject reasons, send/receive anomalies, MAD send failures, and QP initialization errors for debugging and observability.

## Important APIs, Types, And Functions

- `TRACE_SYSTEM ib_cma` names the trace event subsystem.
- `IB_CM_STATE_LIST`, `IB_CM_LAP_STATE_LIST`, and `IB_CM_REJ_REASON_LIST` define enum-to-string mappings using `TRACE_DEFINE_ENUM()` and `__print_symbolic()`.
- `DECLARE_EVENT_CLASS(icm_id_class)` captures CM ID pointer, local ID, remote ID, CM state, and LAP state.
- `DEFINE_CM_SEND_EVENT()` emits send events for REQ, REP, duplicate REQ/REP, RTU, MRA, SIDR, DREQ, and DREP.
- `TRACE_EVENT(icm_send_rej)` records reject sends with a symbolic reject reason.
- Error event classes cover establish, no-listener, DREQ unknown, MRA unknown, QP INIT/RTR/RTS errors, stale connection, missing private state, unknown handlers, and MAD send completion failures.
- The footer sets `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` for the kernel trace header generator.

## Control Flow

The header uses standard Linux tracepoint macros. At compile time, it defines enum mappings and event structures. At runtime, `trace_icm_*()` callsites in `cm.c` populate fixed event fields and print symbolic state/reason/status strings when tracing is enabled.

## State And Persistence

The header declares trace event schemas, not durable state. Event records are transient in kernel tracing buffers. It intentionally stores pointer values for eBPF correlation plus integer IDs/states for stable decoding.

## Dependencies And Integration Points

It includes `<linux/tracepoint.h>`, `<rdma/ib_cm.h>`, and `<trace/misc/rdma.h>`. `cm.c` depends on the generated `trace_icm_*` helpers. Tracing tools consume the `ib_cma` event namespace to diagnose CM state transitions and failures.

## Risks

- Enum lists must stay synchronized with public RDMA CM enums; missing values degrade trace readability.
- Trace payloads must avoid dereferencing freed CM IDs. Current callsites pass live IDs while holding appropriate references or locks.
- The relative `TRACE_INCLUDE_PATH` must match the source tree layout for trace generation.
- Event fields are part of observability contracts for scripts; renaming events or fields can break external tooling.

## Test Signals

Signals include successful trace header generation, visible `ib_cma:*` events, symbolic rendering of CM states/LAP states/reject reasons/WC statuses, and trace output during CM handshakes, duplicate handling, REJ/MRA paths, send errors, and QP attribute failures.
