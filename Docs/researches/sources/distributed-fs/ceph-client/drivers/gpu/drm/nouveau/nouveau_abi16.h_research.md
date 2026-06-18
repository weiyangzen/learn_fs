# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_abi16.h

## Purpose

This header declares the legacy ABI16 compatibility structures and ioctl entry points implemented by `nouveau_abi16.c`.

## Important APIs, Types, and Functions

It defines `ABI16_IOCTL_ARGS`, `struct nouveau_abi16_ntfy`, `struct nouveau_abi16_chan`, `struct nouveau_abi16`, `struct drm_nouveau_grobj_alloc`, `struct drm_nouveau_setparam`, domain flags `NOUVEAU_GEM_DOMAIN_VRAM/GART`, legacy ioctl numbers, and prototypes for getparam, Z-cull, channel/object/notifier operations, `nouveau_abi16_get`, `nouveau_abi16_put`, `nouveau_abi16_fini`, `nouveau_abi16_swclass`, and `nouveau_abi16_ioctl`.

## Control Flow

The header has no direct execution; DRM ioctl tables and Nouveau client teardown paths include it to dispatch old UAPI requests into the ABI16 implementation.

## State and Persistence Behavior

The structures define per-client ABI16 state: channel lists, tracked NVIF objects, per-channel notifier heaps, notifier BO/VMA, optional scheduler, and notifier object nodes.

## Dependencies and Integration Points

It integrates legacy DRM Nouveau UAPI definitions with Nouveau's modern `nouveau_cli`, `nouveau_channel`, `nouveau_bo`, `nouveau_vma`, NVIF object, and NVKM MM types.

## Risks

Structure layout and ioctl numbers are user ABI and must not drift. Locking expectations around `nouveau_abi16_get/put` are implicit and must be followed by callers.

## Test Signals

Build old-UAPI ioctl dispatch, run legacy userspace allocation/free paths, and verify teardown frees all ABI16 channels/notifiers/objects.
