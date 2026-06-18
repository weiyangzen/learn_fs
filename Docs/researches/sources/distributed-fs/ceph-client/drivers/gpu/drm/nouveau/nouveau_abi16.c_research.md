# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_abi16.c

## Purpose

This file implements Nouveau's legacy ABI16 DRM/NVIF compatibility layer. It preserves old userspace ioctls for parameters, Z-cull information, channel allocation/free, engine object allocation, notifier allocation, GPU object freeing, and a restricted subset of the old `DRM_NOUVEAU_NVIF` object API.

## Important APIs, Types, and Functions

Important entry points are `nouveau_abi16_get`, `nouveau_abi16_put`, `nouveau_abi16_fini`, `nouveau_abi16_swclass`, `nouveau_abi16_ioctl_getparam`, `nouveau_abi16_ioctl_get_zcull_info`, `nouveau_abi16_ioctl_channel_alloc`, `nouveau_abi16_ioctl_channel_free`, `nouveau_abi16_ioctl_grobj_alloc`, `nouveau_abi16_ioctl_notifierobj_alloc`, `nouveau_abi16_ioctl_gpuobj_free`, and `nouveau_abi16_ioctl`. Internal tracking uses `struct nouveau_abi16_obj`, `struct nouveau_abi16_chan`, and `struct nouveau_abi16_ntfy`.

## Control Flow

The `get` helper lazily allocates ABI16 state under the client mutex; `put` releases that mutex. Channel allocation disables late UVMM mixing, selects a runlist/engine, creates a Nouveau channel, optionally creates a scheduler for VM_BIND clients, applies CE compatibility workarounds, allocates/pins a notifier buffer, maps it for Tesla+, creates a GEM handle, and initializes an `nvkm_mm` notifier heap. Object allocation maps legacy class aliases to available NVIF classes before constructing objects under the channel user object. Notifier allocation suballocates from the notifier heap and builds an old `NV_DMA_IN_MEMORY` object against VM, AGP, or buffer offsets. The restricted NVIF ioctl path copies user data, validates route/version, dispatches sclass/new/del/mthd, and copies results back.

## State and Persistence Behavior

Per-file state lives on `nouveau_cli->abi16`: lists of legacy channels and tracked NVIF objects. Each channel owns a Nouveau channel, optional CE workaround object, notifier BO/VMA, notifier heap, scheduler, and notifier objects. Cleanup idles channels, destroys scheduler state, frees notifiers, unpins buffers, tears down NVIF objects, and clears `cli->abi16`.

## Dependencies and Integration Points

It depends on DRM ioctl copying, NVIF object/class/device APIs, Nouveau channel/GEM/VMA/scheduler helpers, TTM memory usage reporting, NVKM GR/MM range helpers, and legacy UAPI structures from `drm_nouveau_drm.h`.

## Risks

The layer intentionally allows old userspace behavior, so compatibility hacks are easy to regress. Mutex ownership is coupled to `nouveau_abi16_get/put`; early returns must release it. User-provided handles/classes need strict validation. Notifier heap offsets differ across VM, AGP, and pre-Tesla paths. UVMM and ABI16 UAPIs must not be mixed after initialization.

## Test Signals

Run legacy Mesa/DDX channel creation, getparam coverage, Z-cull ioctl on supported/unsupported GR, object class alias allocation, notifier allocation/free on pre-Fermi and Tesla paths, restricted NVIF new/sclass/mthd/del, malformed ioctl size/version/route tests, and client teardown leak checks.
