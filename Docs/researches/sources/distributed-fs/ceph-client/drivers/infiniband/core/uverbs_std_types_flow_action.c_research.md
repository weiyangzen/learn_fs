# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_flow_action.c

## Purpose

`uverbs_std_types_flow_action.c` registers the flow action uverbs object and its destroy method. Creation is expected to come from provider-specific UAPI extensions; the core file provides the standard object lifetime and destroy hook.

## Important APIs, Types, and Functions

- `uverbs_free_flow_action()` rejects destruction while `action->usecnt` is nonzero and calls provider `destroy_flow_action`.
- `UVERBS_METHOD_FLOW_ACTION_DESTROY` declares the mandatory destroy handle.
- `UVERBS_OBJECT_FLOW_ACTION` registers an IDR-backed object using the destructor.
- `uverbs_def_obj_flow_action[]` gates the object on provider `destroy_flow_action`.

## Control Flow

The generic destroy path resolves the IDR object with `UVERBS_ACCESS_DESTROY`, invokes `uverbs_free_flow_action()`, and then the default destroy handler completes the method. No create or modify path is defined in this core file.

## State and Persistence Behavior

State is the provider-created `ib_flow_action`, its `usecnt`, and the owning uobject. The object cannot be destroyed while referenced by flows or provider resources.

## Dependencies and Integration Points

The file depends on provider `destroy_flow_action`, `rdma_core` IDR object handling, and provider-defined methods that allocate or attach flow actions. It is chained into the core UAPI by `uverbs_uapi.c`.

## Risks and Edge Cases

The main risk is mismatched provider extension behavior: if provider create paths do not initialize `usecnt`, `device`, or object ownership consistently, core destroy can fail or call the wrong op. Gating only on destroy support means provider-specific creation definitions must be coherent.

## Test Signals

Test provider-created flow action destroy, destroy while referenced, provider destroy failure, UAPI absence when `destroy_flow_action` is missing, and interop with flow objects that hold action references.
