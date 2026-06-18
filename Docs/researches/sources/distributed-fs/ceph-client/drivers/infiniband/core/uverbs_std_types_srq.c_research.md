# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_srq.c

## Purpose

`uverbs_std_types_srq.c` implements shared receive queue create and destroy for ioctl uverbs, including basic, XRC, and tag-matching SRQ variants. It wires async events and returns provider-adjusted attributes to userspace.

## Important APIs, Types, and Functions

- `uverbs_free_srq()` calls `ib_destroy_srq_user()`, decrements XRCD references for XRC SRQs, and releases async event state.
- `UVERBS_METHOD_SRQ_CREATE` parses PD, SRQ type, caps/limit/user handle, optional XRCD, optional CQ, optional max tag count, optional event FD, and provider udata.
- `UVERBS_METHOD_SRQ_DESTROY` returns async events reported.
- The declarations register required/optional attributes and gate the object on provider `destroy_srq`.

## Control Flow

Create reads base attributes, resolves a CQ if the selected SRQ type requires one, then branches by type. XRC SRQ requires an XRCD object and increments the XRCD wrapper refcount; tag-matching SRQ reads `max_num_tags`; basic SRQ needs no extension. It resolves async event FD, initializes event list and handler, calls `ib_create_srq_user()`, stores the SRQ in the uobject, finalizes creation, returns adjusted `max_wr` and `max_sge`, and returns SRQ number for XRC. Error paths release event FD and XRCD refcount.

Destroy is split between `uverbs_free_srq()` for hardware/object teardown and the destroy handler for reporting event count.

## State and Persistence Behavior

State includes `struct ib_srq`, `ib_usrq_object`, event list/counters, optional async event file, optional XRCD reference, and provider-owned SRQ payload. XRC references persist until destroy succeeds.

## Dependencies and Integration Points

The file depends on PD, CQ, XRCD, async event FD objects, `ib_create_srq_user()`, `ib_destroy_srq_user()`, `ib_srq_has_cq()`, and event delivery through `ib_uverbs_srq_event_handler()`.

## Risks and Edge Cases

Risks include SRQ type matrix errors, missing XRCD/CQ for types that require them, XRCD refcount leaks on create failure, optional tag matching fields accepted for wrong types, and event-file reference cleanup. Provider-adjusted caps must be copied back after successful creation.

## Test Signals

Test basic, XRC, and tag-matching SRQ create; invalid type; missing/invalid XRCD or CQ; event FD behavior; provider create failure cleanup; XRC refcount increment/decrement; destroy response event count; and destroy while QPs reference the SRQ.
