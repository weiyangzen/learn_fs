<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/ctrl.c

## Purpose
Implements R535 RM control RPC get/push/done wrappers.

## Important APIs, Types, And Functions
Defines `r535_gsp_rpc_rm_ctrl_get`, `r535_gsp_rpc_rm_ctrl_push`, `r535_gsp_rpc_rm_ctrl_done`, and exports `r535_ctrl`.

## Control Flow
Get creates a `GSP_RM_CONTROL` RPC with client handle, object handle, command ID, and parameter size, returning the parameter payload. Push sends the RPC, converts RM status to errno, optionally returns reply parameters for caller inspection, or completes the RPC immediately. Done releases a retained reply.

## State And Persistence
Control RPC buffers are transient. Object and client handles identify persistent RM objects.

## Dependencies And Integration Points
Used by display, FIFO, GR, FBSR, BAR, and device event code for control commands.

## Risks And Edge Cases
Callers must call done when push returns reply parameters. Nonzero RM status is logged except retry/busy cases. `NULL` params are tolerated in done.

## Test Signals
Successful control calls, correct error propagation, and no leaked RPC buffers during repeated display/FIFO operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/ctrl.c -->
