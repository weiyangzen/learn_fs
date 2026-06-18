## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/oproxy.c

### Purpose
`oproxy.c` implements an NVKM object proxy that exposes the standard object callback surface while delegating most behavior to another wrapped `struct nvkm_object`. It lets a wrapper add before/after lifecycle hooks around an underlying object.

### Important APIs, types, and functions
The exported constructors are `nvkm_oproxy_ctor()` and `nvkm_oproxy_new_()`. The callback table `nvkm_oproxy_func` implements `dtor`, `init`, `fini`, `mthd`, `ntfy`, `map`, `unmap`, `bind`, `sclass`, and `uevent`. Wrapper-specific behavior is supplied by `struct nvkm_oproxy_func` arrays `init[2]`, `fini[2]`, and `dtor[2]`.

### Control flow
Method, notification, map, bind, subclass, and uevent calls forward to `oproxy->object`. Init runs pre-hook, underlying object init, then post-hook. Fini runs pre-hook, underlying object fini, then post-hook, returning errors only during suspend-style operations. Destruction runs pre-dtor hook, deletes the underlying object through `nvkm_object_del()`, then runs post-dtor hook.

### State and persistence behavior
The proxy owns a base `nvkm_object`, a function table pointer, and the wrapped object pointer. It does not clone underlying object state; it forwards to the live child. `nvkm_oproxy_unmap()` tolerates a missing wrapped object and returns success, which matters during teardown.

### Dependencies
It depends on `core/oproxy.h` and the base object APIs from `core/object.h`. The wrapped object must already implement the relevant callbacks.

### Integration points
Proxy objects integrate with the same NVIF object tree and handle model as normal objects. They are useful where a class needs to adapt lifecycle behavior without reimplementing method, map, bind, notification, or event forwarding.

### Risks
Most callbacks assume `oproxy->object` is valid; only `unmap` checks for NULL. Constructor users must assign the wrapped object before any forwarded operation. Init/fini hook failures can leave the wrapper and wrapped object initialized to different depths. `sclass` rewrites `oclass->parent` to the wrapped object, so child object constructors depend on that parent substitution.

### Test signals
Test with proxy creation over a real object, forwarded method/map/bind/uevent calls, init and fini hook failure injection, destruction of proxies with and without an underlying object, and child class enumeration through the proxy.
