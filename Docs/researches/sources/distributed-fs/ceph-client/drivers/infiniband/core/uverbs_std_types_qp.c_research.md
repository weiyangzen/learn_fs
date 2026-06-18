# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_qp.c

## Purpose

`uverbs_std_types_qp.c` implements queue pair creation and destruction for the ioctl uverbs ABI. It validates QP type-specific dependencies, optional SRQ/XRCD/RWQ indirection table usage, raw-packet capabilities, event FD wiring, creation flags, caps, and destroy-time event reporting.

## Important APIs, Types, and Functions

- `uverbs_free_qp()` destroys QPs through `ib_destroy_qp_user()`, handles multicast attachment cleanup rules, decrements XRCD references, and releases async event state.
- `check_creation_flags()` enforces QP-type restrictions for scatter FCS, CVLAN stripping, multicast loopback, PCI write end padding, and SQ-signaled-all behavior.
- `set_caps()` copies caps between `ib_uverbs_qp_cap` and `ib_qp_init_attr`.
- `UVERBS_METHOD_QP_CREATE` parses all handles and attributes, validates QP type and dependency combinations, calls `ib_create_qp_user()`, increments use counts, finalizes creation, and returns adjusted caps and QP number.
- `UVERBS_METHOD_QP_DESTROY` returns async events reported.

## Control Flow

Create reads caps, user handle, and QP type, then branches by type. XRC target QPs require XRCD and forbid PD/CQ/SRQ/RWQ indirection table handles. RC/UC/UD/XRC initiator/raw-packet/driver QPs require PD, validate raw-packet privilege when needed, and choose either direct send/recv CQs or an RWQ indirection table. SRQ is optional but XRC SRQ compatibility is checked. Flags and optional source QPN are parsed, event FD is resolved, handlers and caps are set, and `ib_create_qp_user()` performs provider allocation. Success stores the QP in the uobject, handles XRCD reference increments, finalizes creation, and copies response caps/QP number.

Destroy is framework-driven: user-triggered destroy refuses QPs with multicast bindings still attached, while forced cleanup detaches them for real QPs before provider destruction.

## State and Persistence Behavior

Persistent state includes `struct ib_qp`, `ib_uqp_object`, event list/counters, multicast list and lock, optional XRCD reference, PD/CQ/SRQ/RWQ dependencies managed by core/provider use counts, and user handle. Event delivery uses `ib_uverbs_qp_event_handler()`.

## Dependencies and Integration Points

The file depends on PD, CQ, SRQ, XRCD, and RWQ indirection table objects; raw capability checks; `ib_create_qp_user()` and `ib_destroy_qp_user()`; event helpers in `uverbs_main.c`; multicast detach helper `ib_uverbs_detach_umcast()`; and provider destroy support for UAPI gating.

## Risks and Edge Cases

Risks include invalid QP type combinations, raw packet privilege bypass, RWQ indirection table misuse with recv caps/CQs/SRQ, XRC reference leaks, multicast bindings blocking user destroy, SQ_SIG_ALL flag translation before provider call, and event-file reference cleanup on create failure. The type matrix is the key behavioral contract.

## Test Signals

Test each QP type, invalid dependency combinations, raw-packet permission failures, creation flag restrictions by type, RWQ indirection table mode, XRC target/initiator behavior, SRQ compatibility, source QPN flagging, provider create failure cleanup, destroy with multicast bindings, forced cleanup detaching multicast, and destroy event-count response.
