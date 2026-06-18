# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/client.c

## Purpose
This file implements NVIF client construction, destruction, suspend, and resume wrappers.

## Important APIs, Types, and Functions
Public functions are `nvif_client_ctor`, `nvif_client_dtor`, `nvif_client_suspend`, and `nvif_client_resume`.

## Control Flow
Constructor creates an `NVIF_CLASS_CLIENT` object either as a child of a parent client or as the root client, copies the driver pointer, marks the object handle as root, and stores the client backpointer. Suspend/resume delegate to the selected NVIF driver backend using the root object private pointer. Destructor destroys the NVIF object and clears the driver pointer.

## State and Persistence Behavior
State includes the client NVIF object, driver vtable pointer, object handle, object client backpointer, and backend private pointer.

## Dependencies and Integration Points
It depends on NVIF object construction, the NVIF driver interface, and client class ABI structures. It is used by `nvif_driver_init` and nested client creation.

## Risks
Root client construction uses `parent == client` special handling. Driver pointer propagation must be correct or later ioctls/suspend calls dereference NULL or the wrong backend.

## Test Signals
Signals include root and child client creation, suspend/resume delegation, destructor idempotence, and backend init failure handling.
