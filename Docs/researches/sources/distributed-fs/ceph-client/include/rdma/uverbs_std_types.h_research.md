# sources/distributed-fs/ceph-client/include/rdma/uverbs_std_types.h

Purpose: Supplies standard uverbs object lookup/allocation/destroy helpers and flow object support for write-based and ioctl-based RDMA user APIs.

Important APIs/types/functions: Macros `uobj_get_read()`, `uobj_get_write()`, `uobj_get_destroy()`, `uobj_perform_destroy()`, `uobj_alloc()`, and `uobj_get_obj_read()` wrap lookup against a uverbs API object. `uobj_put_*()`, `uobj_alloc_abort()`, and `uobj_finalize_uobj_create()` handle lifetime completion. `struct uverbs_api_object` records type attributes, type class, disabled state, and object ID. Flow helpers include `ib_uflow_resources`, `ib_uflow_object`, `flow_resources_alloc/add/free()`, `uverbs_flow_action_fill_action()`, and `ib_set_flow()`.

Control flow and state: IDR/FD lookups are done with explicit read/write/destroy modes and must be paired with the matching put. Allocation starts through core uobject APIs, initializes driver object pointers, then commits or aborts. Flow resources track counters and action collections associated with an `ib_flow`.

Dependencies and integration: Depends on uverbs type classes, ioctl bundles, RDMA user ioctl verbs, `ib_uobject`, `ib_flow`, `ib_qp`, and `ib_device`.

Risks and test signals: Risks include wrong ID type for legacy write API, missing put on error paths, committing an uninitialized object, usecount leaks on QPs, and flow resource cleanup mismatches. Tests should cover read/write/destroy lookup modes, create abort paths, default destroy handler paths, flow creation with counters/actions, and object disable behavior.
