# sources/distributed-fs/ceph-client/include/linux/qed/roce_common.h

Purpose: defines RoCE-specific firmware constants and asynchronous event identifiers shared between QED firmware command handling and the RDMA provider.

Important APIs and types: constants include request inline-data and WQE sizing, maximum QP counts, DCQCN NP/RP QP limits, and the LKEY memory-window DIF enable bit. `enum roce_async_events_type` enumerates firmware-reported events and errors such as communication established, SQ drained, SRQ limit/empty, CQ errors/overflow, local access/request/catastrophic errors, QP catastrophic errors, destroy-QP completion, and XRC errors.

Control flow: firmware completion/event handlers translate async event codes into RDMA core events and provider callbacks. QP/SRQ/CQ management code also uses the sizing constants to validate resource creation and command construction.

State and persistence: no state is owned. Event values represent transient firmware notifications; resource limits constrain in-memory/device contexts.

Dependencies and integration points: integrates QED firmware protocol definitions with the RoCE provider and upper RDMA core event model.

Risks and test signals: risks include event-number ABI mismatch, incomplete translation of catastrophic/error events, and off-by-one resource sizing around `ROCE_MAX_QPS`. Test async event injection or firmware fault paths, CQ overflow handling, SRQ limit/empty events, destroy-QP completion, DCQCN-enabled configurations, and RDMA userspace verbs boundary cases.
