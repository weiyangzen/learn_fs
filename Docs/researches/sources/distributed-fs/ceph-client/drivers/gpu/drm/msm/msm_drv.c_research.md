# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_drv.c

## Purpose
Implements the top-level MSM DRM driver: module parameters, DRM device allocation/registration, component binding, per-file contexts, IOCTL dispatch, GPU/KMS split-device support, and module init/exit registration of subdrivers.

## Important APIs, types, and functions
- Module params: `dumpstate`, `modeset`, `separate_gpu_kms`, and optional `prefer_mdp5`.
- `msm_drm_init()`/`msm_drm_uninit()` allocate, bind, register, debugfs-init, and tear down DRM devices.
- `msm_open()`, `msm_postclose()`, `context_init()`, and `context_close()` manage per-file `msm_context`.
- IOCTL handlers cover params, GEM create/info/cpu prep/fini/madvise, submit queues, wait fence, submit, and VM_BIND.
- `msm_drv_probe()`, `msm_gpu_probe()`, `msm_gpu_remove()`, and component ops integrate display/GPU platform devices.

## Control flow
Module init registers display, HDMI, DP, DSI, GPU, MDP, DPU, and MDSS subdrivers unless modeset is disabled. Probe builds a component match list from MDP graph endpoints and optional GPU nodes, sets DMA masks, and registers a component master. `msm_drm_init()` allocates `drm_device`, initializes object/LRU/fault-stall state, initializes KMS mode config when needed, binds components, starts the GEM shrinker, initializes KMS, registers DRM, and then initializes late debugfs/post-init. Open lazily loads the GPU and creates a context. Close disables sysprof and closes submit queues.

## State and persistence
Driver-private state lives in `struct msm_drm_private`, including KMS/GPU pointers, GEM object list, LRUs, shrinker, debug state, devfreq config, and fault-stall state. Per-file state is `struct msm_context`, submit queues, VM, sequence number, and memory accounting. IOCTL metadata/name state is stored on GEM objects.

## Dependencies and integration points
Depends on DRM core, component framework, OF graph helpers, Adreno GPU loader, KMS implementations, GEM/shrinker, debugfs/perf/rd modules, submitqueue and VM_BIND code, dma-fence, syncobj, and PRIME import/export hooks.

## Risks
Initialization/unwind ordering is complex: DRM unregister, KMS unregister/uninit, shrinker cleanup, debugfs cleanup, GPU/component unbind, and drm_dev_put must stay ordered. Lazy GPU load on open means render users may see ENXIO before firmware/GPU availability. GEM_INFO metadata size and string handling are UABI-visible. `separate_gpu_kms` changes component topology and driver feature sets.

## Test signals
Probe/remove for combined and split GPU/KMS devices, all IOCTL validation paths, GEM fault injection, metadata get/set, submitqueue lifecycle, wait fence timeout/boost, component graph variations, and module unload are key signals.
