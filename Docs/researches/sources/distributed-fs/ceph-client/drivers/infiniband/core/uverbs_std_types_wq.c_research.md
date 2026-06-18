# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_wq.c

## Purpose

`uverbs_std_types_wq.c` implements work queue create and destroy for ioctl uverbs. It supports receive queues attached to PD/CQ, optional async event FDs, selected WQ flags, provider udata, and destroy-time event reporting.

## Important APIs, Types, and Functions

- `uverbs_free_wq()` destroys a WQ through `ib_destroy_wq_user()` and releases async event state.
- `UVERBS_METHOD_WQ_CREATE` parses create flags, max SGE/WR, user handle, WQ type, PD, CQ, optional event FD, and provider data; then calls provider `create_wq`.
- `UVERBS_METHOD_WQ_DESTROY` returns async events reported.
- `uverbs_def_obj_wq[]` exposes the object when provider `destroy_wq` exists.

## Control Flow

Create validates flags, copies max SGE/WR and user handle, obtains WQ type, and accepts only `IB_WQT_RQ`. It resolves PD and CQ, resolves optional async event FD, initializes event list and handler, calls `pd->device->ops.create_wq()`, initializes the returned `ib_wq`, increments PD/CQ use counts, stores the uobject, finalizes creation, and returns adjusted max WR/SGE plus optional WQ number. On provider failure it releases the event FD reference.

Destroy invokes provider destruction through the object destructor and then copies the event count response.

## State and Persistence Behavior

State includes `struct ib_wq`, `ib_uwq_object`, PD/CQ references, event list/counters, optional async event file, WQ number, use count, and provider payload. PD and CQ use counts remain elevated until WQ destroy.

## Dependencies and Integration Points

The file depends on PD and CQ objects, async event FDs, provider `create_wq`/`destroy_wq`, `ib_uverbs_wq_event_handler()`, and RWQ indirection tables that can later reference WQs through object definitions in `uverbs_std_types.c`.

## Risks and Edge Cases

Risks include provider create being called despite missing `create_wq` if UAPI gating is incomplete, accepting unsupported WQ types, use-count leaks on partial create, event FD cleanup, and mismatch between optional CQ declaration and provider assumptions. The code enforces receive-queue-only WQ type but relies on UAPI/provider gating for ops.

## Test Signals

Test valid receive WQ create, invalid WQ types, flag validation, provider create failure cleanup, event FD delivery/release, adjusted caps response, WQ number response, destroy event-count response, and PD/CQ use-count behavior.
