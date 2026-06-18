## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/object.c

### Purpose
`object.c` implements the base NVKM object model: client-visible handles, object lookup/removal/insertion, method and notification dispatch, map/bind hooks, hierarchical init/fini/destroy ordering, and default object construction.

### Important APIs, types, and functions
The central type is `struct nvkm_object`, driven by `struct nvkm_object_func` callbacks. Public functions include `nvkm_object_search()`, `nvkm_object_insert()`, `nvkm_object_remove()`, `nvkm_object_mthd()`, `nvkm_object_ntfy()`, `nvkm_object_map()`, `nvkm_object_unmap()`, `nvkm_object_bind()`, `nvkm_object_init()`, `nvkm_object_fini()`, `nvkm_object_dtor()`, `nvkm_object_del()`, `nvkm_object_ctor()`, `nvkm_object_new_()`, and `nvkm_object_new()`.

### Control flow
Client objects live in an rb-tree keyed by the `object` handle and protected by `client->obj_lock`. Search with handle zero returns the client's root object. Lifecycle is hierarchical: init runs the object callback first, then children in forward list order; fini runs children in reverse order before the object callback; destroy deletes children, unmaps, calls the type destructor, unreferences the backing engine, removes from client lookup, unlinks from its parent tree, and frees memory.

### State and persistence behavior
Objects persist until `nvkm_object_del()` deletes them. They keep client, engine reference, oclass, handle, rb-tree node, and parent/child list state. Suspend fini has rollback logic: if a child or object fails during suspend/runtime suspend, already-finished objects are reinitialized to restore operational state.

### Dependencies
The file depends on `core/object.h`, client locking and rb-tree state from `core/client.h`, engine references from `core/engine.h`, NVIF logging helpers, Linux rb-tree/list primitives, and kernel time helpers for debug timing.

### Integration points
The object model underpins NVIF user objects, engine classes, events, GPU object binding, method dispatch, memory mapping, and child class enumeration. Engine implementations provide `bind`, `map`, `mthd`, `sclass`, and `uevent` callbacks through this common layer.

### Risks
Lifetime ordering is the main risk. A destructor that returns a different allocation pointer must still be compatible with the final `kfree(*pobject)`. Missing callback checks return `-ENODEV`, so callers must distinguish unsupported operations from object errors. Failing to remove objects from the rb-tree or child list can leave stale handles. Init/fini rollback must remain symmetrical to avoid partially initialized hardware after suspend failures.

### Test signals
Good coverage comes from NVIF object create/destroy tests, duplicate handle insertion rejection, lookup under concurrent client access, object tree init/fini failure injection, suspend/resume rollback, and bind/map/unmap paths for engine classes.
