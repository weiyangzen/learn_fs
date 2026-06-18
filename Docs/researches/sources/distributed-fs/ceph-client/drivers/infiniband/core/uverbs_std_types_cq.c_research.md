# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_cq.c

## Purpose

`uverbs_std_types_cq.c` implements completion queue create and destroy for the ioctl uverbs ABI. It supports traditional provider-created CQs, user CQs backed by userspace memory, dma-buf-backed CQ memory, completion channel FDs, async event FDs, restrack registration, and destruction responses reporting event counts.

## Important APIs, Types, and Functions

- `uverbs_free_cq()` calls `ib_destroy_cq_user()` and releases completion/async event queue state.
- `UVERBS_METHOD_CQ_CREATE` parses CQE count, user handle, comp vector, flags, optional completion channel, optional async event FD, and optional buffer descriptors.
- Buffer modes are mutually exclusive: `BUFFER_VA` plus `BUFFER_LENGTH` uses `ib_umem_get()`, while `BUFFER_FD` plus `BUFFER_OFFSET` plus `BUFFER_LENGTH` uses `ib_umem_dmabuf_get_pinned()`.
- Provider dispatch uses `create_user_cq` when available, otherwise legacy `create_cq`.
- `UVERBS_METHOD_CQ_DESTROY` returns `ib_uverbs_destroy_cq_resp` with completion and async event counts.
- The declaration registers all required attributes and `UVERBS_ATTR_UHW()`.

## Control Flow

Create first validates provider create/destroy support, required attributes, CQE nonzero, flags, and comp-vector range. It optionally resolves and references a completion event FD, resolves an async event FD, initializes event lists, creates or pins user memory for CQ backing, allocates `struct ib_cq`, initializes handlers/context/umem/restrack, and invokes the provider. On success it stores the CQ in the uobject, records the user handle, adds restrack, finalizes creation, and returns actual `cqe`. Error paths release umem and event-file references.

Destroy is a two-phase framework operation: the generic destroy path removes the CQ through `uverbs_free_cq()`, then the handler writes event counts back to userspace.

## State and Persistence Behavior

Persistent state includes the CQ object, `ib_ucq_object`, completion event list, async event list, event counters, optional completion channel reference, optional async event file reference, optional umem/dma-buf memory, restrack entry, and CQ use count. The file carefully releases event queues and object references after provider destruction succeeds.

## Dependencies and Integration Points

It depends on `ib_umem_get`, `ib_umem_dmabuf_get_pinned`, provider `create_cq`/`create_user_cq`/`destroy_cq`, event handlers in `uverbs_main.c`, `ib_uverbs_release_ucq()` in `uverbs_main.c`, and restrack helpers. QP, WQ, and SRQ objects may later reference CQs and increment use counts.

## Risks and Edge Cases

Risk is concentrated around mutually exclusive buffer attribute sets, comp-vector bounds, umem ownership, event-file reference balancing, and create failure after partial initialization. A provider changing `cq->umem` when core supplied one is warned. Destroy must not race with queued completion events and must report counters accurately.

## Test Signals

Test CQE zero rejection, invalid comp vector, completion channel optional reference release, async event FD wiring, VA vs dma-buf buffer exclusivity, missing length/offset combinations, provider create failures after umem allocation, destroy response event counts, and CQ destroy while referenced by QP/WQ.
