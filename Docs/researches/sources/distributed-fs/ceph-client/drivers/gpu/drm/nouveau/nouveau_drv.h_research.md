
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_drv.h

## Purpose
Defines the central Nouveau DRM data structures, driver identity, logging helpers, client abstraction, global device object, PM prototypes, platform creation prototype, and legacy NVKM accessors used across the driver.

## Important APIs, Types, and Functions
Key types are `struct nouveau_cli`, `struct nouveau_cli_work`, `struct nouveau_drm`, `struct nouveau_drm_tile`, `enum nouveau_drm_object_route`, and `enum nouveau_drm_handle`. Inline helpers include `nouveau_cli()`, `nouveau_cli_uvmm()`, `nouveau_cli_uvmm_locked()`, `nouveau_cli_vmm()`, `nouveau_cli_disable_uvmm_noinit()`, `u_memcpya()`, `u_free()`, `nouveau_drm()`, `nouveau_drm_use_coherent_gpu_mapping()`, and `nvxx_device()` plus NVKM subdevice macros. Prototypes include PM hooks, platform device creation, device removal, and client deferred work queueing.

## Control Flow
This header does not execute control flow directly, but it shapes cross-file control flow by determining how callers resolve per-file clients, select classic VMM versus SVM versus UVMM, copy arrays from userspace safely with overflow checking, and log through the correct DRM/client context. `nouveau_cli_disable_uvmm_noinit()` is part of the UAPI separation flow that prevents mixing legacy GEM pushbuf and VM_BIND/EXEC APIs.

## State and Persistence
`struct nouveau_drm` is the persistent per-device state root. It contains NVIF root objects, the root client, per-file client list, TTM/GEM accounting, synchronization backend, channel/runlist metadata, scheduler workqueue, kernel acceleration channels, tiling state, display/HPD state, PM helpers, hwmon/debugfs/LED/SVM/DMEM pointers, and audio component registration state. `struct nouveau_cli` is persistent per DRM file or root client and owns VMM/MMU/device objects, optional UVMM/SVM contexts, scheduler, ABI16 object list, deferred work, and naming.

## Dependencies and Integration Points
Includes Linux notifier and DRM/TTM headers, NVIF client/device/ioctl/MMU/VMM headers, UAPI Nouveau DRM definitions, and local fence/BIOS/scheduler/VMM/UVMM headers. Nearly every Nouveau DRM file depends on this header for the device and client model.

## Risks and Test Signals
Risks are ABI and locking related: changes to these structures affect many subsystems. The direct NVKM accessor macros are explicitly discouraged for new code, especially with GSP-RM paths where NVKM subdevices can be stubbed. Test signals include allmodconfig builds, GSP and non-GSP devices, legacy and UVMM UAPI separation tests, lockdep around `client_mutex`/`clients_lock`/client locks, and compile coverage for optional subsystems.
