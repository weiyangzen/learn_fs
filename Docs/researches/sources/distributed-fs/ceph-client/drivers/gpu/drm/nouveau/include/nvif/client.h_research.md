# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/client.h

## Purpose
Declares the top-level NVIF client wrapper that binds a driver backend to an NVIF root object.

## Important APIs, Types, And Functions
Defines `struct nvif_client` with embedded `nvif_object` and `nvif_driver`, plus `nvif_client_ctor`, `nvif_client_dtor`, suspend, and resume functions.

## Control Flow
Construction initializes the backend driver and root object. Suspend/resume forward lifecycle transitions to the driver.

## State And Persistence
Client state holds the root object and backend pointer for the entire Nouveau device/client lifetime.

## Dependencies And Integration Points
Depends on `nvif/object.h` and `nvif/driver.h`; used by device, object, and logging layers.

## Risks
Client lifetime errors invalidate every child object. Suspend/resume ordering affects mapped objects and firmware state.

## Test Signals
Driver initialization, object creation under the client, suspend/resume tests, and clean teardown validate behavior.
