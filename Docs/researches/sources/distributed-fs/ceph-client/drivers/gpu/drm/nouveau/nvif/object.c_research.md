# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/object.c

## Purpose
This file is the core NVIF object wrapper. It formats ioctl packets, creates/destroys objects, invokes methods, queries supported child classes, and maps/unmaps backend objects.

## Important APIs, Types, and Functions
Public functions include `nvif_object_ioctl`, `nvif_object_ctor`, `nvif_object_dtor`, `nvif_object_mthd`, `nvif_object_sclass_get`, `nvif_object_sclass_put`, `nvif_object_map`, `nvif_object_unmap`, `nvif_object_map_handle`, and `nvif_object_unmap_handle`.

## Control Flow
Ioctl fills the target object handle and delegates to the client driver. Constructor initializes local object fields and, for non-root objects, sends a NEW ioctl through the parent and stores returned private data/client pointer. Method and map helpers allocate stack/heap packets as needed, copy arguments in/out, and call ioctl. Destructor unmaps first, sends DEL, and clears the client pointer.

## State and Persistence Behavior
Object state includes name, handle, class, parent/root relation, client pointer, backend private pointer, and optional map pointer/size. Mapping can be direct virtual address or an IO mapping returned by the driver.

## Dependencies and Integration Points
It depends on NVIF ioctl ABI, NVIF client driver vtable, object handle rules, and all higher-level NVIF wrappers.

## Risks
Handle assignment and root-object special cases are central to correctness. Map failure must unmap backend handles. Argument size overflow checks prevent undersized ioctl buffers. Destructor must be safe on partially constructed objects.

## Test Signals
Signals include object create/delete, method round trips, class queries, IO and VA mapping paths, constructor failures, and repeated destructor calls.
