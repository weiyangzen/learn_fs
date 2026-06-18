<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_ctx.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_ctx.h

## Purpose
Defines Lima context and context-manager structures and declares the context API.

## Important APIs, types, and functions
`struct lima_ctx` contains a kref, device pointer, scheduler contexts for all pipes, and debug process identity. `struct lima_ctx_mgr` contains a mutex and xarray. Prototypes cover create/free/get/put/init/fini.

## Control flow
No executable flow. The declarations support IOCTL and scheduler code.

## State and persistence
Context state persists per user-created context; the manager persists per open DRM file.

## Dependencies and integration points
Includes xarray, scheduler task name size, and `lima_device.h` for pipe counts and scheduler context type.

## Risks
The header pulls in broad device definitions, so include cycles must be managed carefully. Changing `context[lima_pipe_num]` impacts scheduler ABI assumptions inside the driver.

## Test signals
Build coverage and context IOCTL tests are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_ctx.h -->
