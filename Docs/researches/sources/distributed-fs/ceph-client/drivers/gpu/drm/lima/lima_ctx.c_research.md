<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_ctx.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_ctx.c

## Purpose
Manages per-file Lima GPU contexts. A context owns one DRM scheduler entity per hardware pipe and carries process debug identity.

## Important APIs, types, and functions
Exports `lima_ctx_create()`, `lima_ctx_free()`, `lima_ctx_get()`, `lima_ctx_put()`, `lima_ctx_mgr_init()`, and `lima_ctx_mgr_fini()`. `lima_ctx_do_release()` tears down scheduler contexts when the reference count reaches zero.

## Control flow
Create allocates a context, initializes scheduler contexts for GP and PP pipes, inserts the context into an xarray handle table, and records current PID and process name. Free erases the handle under the manager mutex and drops the reference. Get loads and refcounts a context under the same mutex. Manager fini walks any remaining handles and releases them.

## State and persistence
State is held in `struct lima_ctx`: kref, device pointer, scheduler contexts, process name, and PID. The manager owns a locked xarray of user-visible context IDs. State persists until explicit free or DRM file close.

## Dependencies and integration points
Depends on `lima_sched_context_init/fini()` and the per-file private data in `lima_drv.c`. IOCTL submit paths lookup contexts before scheduling work.

## Risks
Partial create unwinding must match the number of initialized pipes. Context handles are per DRM file; use-after-free is prevented by krefs but scheduler jobs must hold their references correctly.

## Test signals
Create/free IOCTL tests, submit after free rejection, file-close cleanup, multi-pipe context initialization failure injection, and process name/PID in error dumps validate this path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_ctx.c -->
