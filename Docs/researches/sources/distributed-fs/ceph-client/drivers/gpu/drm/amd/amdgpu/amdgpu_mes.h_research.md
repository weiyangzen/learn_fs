## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mes.h

Purpose: declares the MES core data model, firmware command input structures, function table, priority/pipe constants, doorbell/version macros, lock helpers, and exported MES operations.

Important APIs/types: `struct amdgpu_mes` stores scheduler/firmware versions, rings, firmware BOs, MQD backups, IRQs, VMID/HQD masks, writeback slots, doorbells, event log, resource BOs, hung queue buffers, cooperative dispatch buffers, and callback table. `struct amdgpu_mes_gang`, `struct amdgpu_mes_queue`, and property structs model process/gang/queue scheduling entities. `mes_*_input` structs are firmware command payloads for queue add/remove/map/unmap/suspend/resume/reset, TLB invalidation, and misc operations. `struct amdgpu_mes_funcs` is the firmware/backend command vtable.

Control flow contract: version-specific MES implementations set `adev->mes.funcs`, KIQ callbacks, ring data, firmware versions, and resource sizes. Generic callers use exported wrappers that serialize with `amdgpu_mes_lock()` where needed. `amdgpu_mes_lock()` wraps `mutex_lock()` with `memalloc_noreclaim_save()` because MES locks can be taken from MMU notifier/reclaim contexts.

State and persistence: the header defines extensive runtime state but no durable persistence. Fence queue IDs use `AMDGPU_FENCE_MES_QUEUE_FLAG` and mask constants to distinguish MES queues in fence IDs.

Dependencies/integration: includes AMDGPU IRQ, KFD interface, GFX, doorbell, and Linux scheduler/MM headers. It connects DRM scheduler, KFD, user queues, firmware, and memory-notifier paths.

Risks: command structs mirror firmware ABI and must remain layout-compatible with MES firmware. Lock helper comments explicitly warn against taking reservation locks or triggering reclaim under MES lock. Pipe/instance macros assume `AMDGPU_MAX_MES_PIPES` times GC instance layout. Duplicated fence flag definitions in `amdgpu_mes_ctx.h` must stay consistent.

Test signals: ABI tests against firmware command versions, queue lifecycle stress, MMU notifier eviction under memory pressure, user queue creation/destruction, MES reset paths, and no-reclaim lockdep validation.
