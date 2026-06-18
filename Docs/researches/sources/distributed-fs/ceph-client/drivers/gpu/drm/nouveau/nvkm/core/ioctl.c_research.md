# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/ioctl.c

## Purpose
This file is the NVKM backend implementation of the NVIF ioctl protocol. It routes class queries, object creation/deletion, method calls, map/unmap, and unsupported read/write/nop requests.

## Important APIs, Types, and Functions
Main public API is `nvkm_ioctl`. Internal dispatchers include `nvkm_ioctl_sclass`, `nvkm_ioctl_new`, `nvkm_ioctl_del`, `nvkm_ioctl_mthd`, `nvkm_ioctl_map`, `nvkm_ioctl_unmap`, `nvkm_ioctl_path`, and class enumeration helper `nvkm_ioctl_sclass_`.

## Control Flow
Top-level ioctl unpacks version 0 headers, finds the target object by handle, and dispatches by type. Class query counts or copies child classes, including uevent class if supported. New finds a matching child class, refs an engine if present, calls its constructor, initializes the object, links it into the parent tree and client handle tree, and returns backend data through the `hack` pointer. Delete finalizes and deletes an object and returns 1 to suppress normal data extraction. Methods and maps delegate to object functions.

## State and Persistence Behavior
State changes include object tree insertion/removal, object initialization/finalization, engine references, client temporary `data` for created objects, and object mapping handles.

## Dependencies and Integration Points
It depends on NVIF ioctl ABI, NVKM object lifecycle, engine refs, user-event construction, and client object lookup.

## Risks
Object creation has many staged failure paths requiring fini/delete. The special return value 1 changes top-level cleanup behavior. Class enumeration and object handle uniqueness are security-sensitive for userspace APIs.

## Test Signals
Signals include ioctl class query sizing, object new/delete, duplicate handle rejection, method dispatch, map/unmap, unsupported rd/wr/nop errors, and engine ref failure injection.
