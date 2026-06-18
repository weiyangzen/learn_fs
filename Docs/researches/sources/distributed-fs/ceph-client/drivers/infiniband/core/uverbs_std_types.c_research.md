# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types.c

## Purpose

`uverbs_std_types.c` defines shared uverbs object classes and destroy behavior for common RDMA resources that do not have larger create handlers in this file: PD, completion event channel, AH, MW, flow, RWQ indirection table, XRCD, and the default destroy handler. It also provides event queue cleanup used by both completion and async event FDs.

## Important APIs, Types, and Functions

- Destructors: `uverbs_free_ah()`, `uverbs_free_flow()`, `uverbs_free_mw()`, `uverbs_free_rwq_ind_tbl()`, `uverbs_free_xrcd()`, and `uverbs_free_pd()` enforce provider destruction and dependent use-count checks.
- `ib_uverbs_free_event_queue()` closes an event queue, wakes readers, sends fasync notification, and frees queued events.
- `uverbs_completion_event_file_destroy_uobj()` destroys completion channel event queues.
- `uverbs_destroy_def_handler()` is the no-op method handler used for declarative destroy methods after the framework has already performed object destruction.
- The `DECLARE_UVERBS_NAMED_OBJECT` and `DECLARE_UVERBS_NAMED_METHOD_DESTROY` blocks register object types and their destroy methods.
- `uverbs_def_obj_intf[]` chains these object trees into the core UAPI with provider-op capability gates.

## Control Flow

Object destruction is initiated by the generic ioctl machinery for methods declared with `UVERBS_ACCESS_DESTROY`. The framework calls the object type destructor, then invokes the destroy method handler, which is generally the no-op default. Destructors reject busy objects through atomic use counts where applicable, call provider destroy/dealloc functions, release event queues or uevent lists, decrement dependent object use counts, and free wrapper memory.

## State and Persistence Behavior

The file manages in-memory uobject state: resource object pointers, atomic use counts, flow resource lists, multicast-independent event lists, completion event queues, and XRCD reference counts. It does not create durable state. Event queue cleanup sets `is_closed` so readers observe end/error behavior and queued events cannot persist past object/file release.

## Dependencies and Integration Points

It depends on `rdma_core.h`, `uverbs.h`, `rdma/uverbs_std_types.h`, provider `ib_device_ops`, and restrack/flow helpers. Its object definitions are imported by `uverbs_uapi.c` through `uverbs_def_obj_intf[]`. Other files call `ib_uverbs_free_event_queue()` and `uverbs_destroy_def_handler()`.

## Risks and Edge Cases

Risks center on reference accounting. PD, flow action, counters, RWQ table, XRCD, and similar resources must not be destroyed while in use. Flow destroy must release QP use counts and flow parser resources only after provider success. Completion channels use FD-backed uobjects and must wake blocked readers during teardown. XRCD destroy is serialized with `xrcd_tree_mutex`.

## Test Signals

Tests should cover destroy while busy, provider destroy failure, event queue read/poll after close, completion channel fd release, flow resource cleanup, RWQ indirection table dependency accounting, and UAPI pruning when required provider ops are missing.
