<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/alloc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/alloc.c

## Purpose
Implements R535 RM object allocation and free RPC wrappers.

## Important APIs, Types, And Functions
Defines `r535_gsp_rpc_rm_alloc_get`, `r535_gsp_rpc_rm_alloc_push`, `r535_gsp_rpc_rm_alloc_done`, `r535_gsp_rpc_rm_free`, and exports `r535_alloc`.

## Control Flow
Allocation get builds an `NV_VGPU_MSG_FUNCTION_GSP_RM_ALLOC` RPC with client, parent, object handle, class, and parameter size, returning the parameter payload. Push submits it, checks RM status, converts errors with `r535_rpc_status_to_errno`, logs non-retry failures, and releases the RPC. Free sends `NV_VGPU_MSG_FUNCTION_FREE` with root and object handles.

## State And Persistence
RM object handles persist in `struct nvkm_gsp_object` until freed. RPC buffers are transient and returned to the GSP RPC layer.

## Dependencies And Integration Points
Used by all R535 RM object constructors through generic `nvkm_gsp_rm_alloc_*` helpers. Depends on RPC functions and NVRM allocation structures.

## Risks And Edge Cases
RPC allocation failure maps to `-EIO` or pointer errors. RM retry statuses are intentionally not logged as hard errors. Free depends on valid client/object relationships.

## Test Signals
Successful RM object allocations, meaningful RM_ALLOC error logs, and no leaked RM handles on teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/alloc.c -->
