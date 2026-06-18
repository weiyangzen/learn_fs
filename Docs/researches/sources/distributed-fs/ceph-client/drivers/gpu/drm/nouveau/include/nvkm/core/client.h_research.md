# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/client.h

## Purpose
Declares the server-side NVKM client object backing NVIF clients and client-facing object logging.

## Important APIs, Types, And Functions
Defines `struct nvkm_client` with root object, name, device handle, debug level, RB-tree object registry, event callback, user memory list, locks, and `nvkm_client_new`. Logging macros include `nvif_fatal/error/debug/trace/info/ioctl`.

## Control Flow
Client creation initializes object tracking and event callback plumbing. Logging macros gate messages by `client->debug`.

## State And Persistence
Client state persists for the NVIF client lifetime and owns server-side object lookup and user-memory tracking.

## Dependencies And Integration Points
Depends on `core/object.h`; bridges NVIF ioctls into NVKM object management and logging.

## Risks
Object-tree locking, handle uniqueness, event callback lifetime, and user-memory cleanup are central risks.

## Test Signals
Client creation/destruction, object leak checks, debug-level filtering, and ioctl trace logs validate behavior.
