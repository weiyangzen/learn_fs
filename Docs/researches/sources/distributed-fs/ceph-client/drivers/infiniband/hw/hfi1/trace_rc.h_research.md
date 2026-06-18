# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_rc.h

## Purpose

`trace_rc.h` defines tracepoints for reliable connection send, ACK, receive-error, completion, and ACK-processing state. It provides compact visibility into QP PSN and flag state around RC protocol transitions.

## Important Events

`hfi1_rc_template` captures device name, QP number, send flags, the event PSN, `s_psn`, `s_next_psn`, `s_sending_psn`, `s_sending_hpsn`, and `r_psn`. It instantiates `hfi1_sendcomplete`, `hfi1_ack`, `hfi1_rcv_error`, and `hfi1_rc_completion`.

`hfi1_rc_ack_template` captures device, QP, AETH, PSN, WQE opcode, WQE start PSN, and WQE last PSN. It instantiates `hfi1_rc_ack_do`.

## Control Flow and State

The events are emitted by RC send/completion/error/ACK paths. They snapshot QP state at protocol boundaries and do not mutate state.

## Dependencies and Integration Points

The header depends on `struct rvt_qp`, `struct rvt_swqe`, `dd_from_ibdev()`, and common trace macros. TID RDMA uses ordinary RC ACK/completion helpers in several places, so these tracepoints complement the TID-specific tracepoints when diagnosing mixed RC/TID behavior.

## Risks and Test Signals

The main risk is interpreting PSN snapshots without the matching TID or packet-header traces, especially when TID RDMA uses both verbs PSNs and KDETH flow PSNs. Test signals include monotonic RC PSN movement, expected ACK/completion events after TID READ responses and TID WRITE ACKs, and receive-error traces during injected PSN mismatch.
