# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/client.c

## Purpose
This file implements NVKM client objects, including root client creation and user-visible child client construction.

## Important APIs, Types, and Functions
Main public function is `nvkm_client_new`. Internal pieces include `nvkm_uclient_new`, `nvkm_client_child_get`, `nvkm_client_child_new`, and `nvkm_client_dtor`.

## Control Flow
`nvkm_client_new` allocates a client, constructs its root NVKM object, records name/device/debug options, initializes object tree and memory lists, and stores the event callback. The user-client class constructor unpacks NVIF args, creates a child client sharing the parent device/event callback, inherits debug level, and returns it as an object. Child class lookup exposes client and device classes.

## State and Persistence Behavior
State includes client name, device handle, debug level, root object tree, object lock, event callback, user memory list, and lock.

## Dependencies and Integration Points
It depends on NVKM object construction, option parsing, NVIF client/device ABI, and ioctl child-class enumeration.

## Risks
Child client creation must preserve parent event and debug state. Object tree locking is initialized here and later used by ioctl/object lookup. Invalid unpacked args reject construction.

## Test Signals
Signals include root client creation, nested client creation through NVIF, object tree insert/delete, debug option parsing, and teardown.
