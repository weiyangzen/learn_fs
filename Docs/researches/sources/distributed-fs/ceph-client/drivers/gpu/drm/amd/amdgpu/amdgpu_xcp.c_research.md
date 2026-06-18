# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_xcp.c

## Purpose

This file implements AMDGPU XCP, the compute partition manager. It tracks XCP partitions, maps IP instances into partitions, creates per-partition DRM nodes, routes file opens and scheduler selection to partitions, handles partition-mode switching, exposes partition resource/metric sysfs, and coordinates KFD around partition changes.

## Important APIs, types, and functions

Transition APIs are `amdgpu_xcp_prepare_suspend()`, `amdgpu_xcp_suspend()`, `amdgpu_xcp_prepare_resume()`, and `amdgpu_xcp_resume()`, implemented through `amdgpu_xcp_run_transition()`. Manager and mode APIs include `amdgpu_xcp_init()`, `amdgpu_xcp_switch_partition_mode()`, `amdgpu_xcp_restore_partition_mode()`, `amdgpu_xcp_query_partition_mode()`, `amdgpu_xcp_mgr_init()`, `amdgpu_xcp_update_supported_modes()`, `amdgpu_xcp_pre_partition_switch()`, and `amdgpu_xcp_post_partition_switch()`. Runtime APIs include `amdgpu_xcp_get_partition()`, `amdgpu_xcp_get_inst_details()`, `amdgpu_xcp_dev_register()`, `amdgpu_xcp_dev_unplug()`, `amdgpu_xcp_open_device()`, `amdgpu_xcp_select_scheds()`, `amdgpu_xcp_release_sched()`, `amdgpu_xcp_update_partition_sched_list()`, `amdgpu_xcp_sysfs_init()`, and `amdgpu_xcp_sysfs_fini()`.

## Control flow, state, and persistence behavior

`amdgpu_xcp_mgr_init()` allocates a manager, stores device/function hooks, initializes the lock, optionally initializes partitions, attaches the manager to the device, and allocates extra partition DRM devices. `amdgpu_xcp_init()` clears old XCP validity, asks the hardware-specific manager for IP details per XCP/block, adds valid blocks, calculates memory partition ids, sets unique IDs from GFX instance UID data, sets the mode and memory allocation mode, and rebuilds partition scheduler lists. Partition switching takes `xcp_lock`, marks mode transient, calls the hardware switch hook, updates sysfs visibility on success, and repairs cached mode on failure.

Runtime file open maps a render node to an XCP id and assigns `fpriv->vm.mem_id`. Scheduler selection picks the least-used partition when the file has no partition, otherwise uses the selected XCP's scheduler array for the requested hardware IP/priority and increments a partition refcount. Release decrements the refcount for the scheduler's ring partition. Scheduler-list updates assign each ring an `xcp_id` based on ring type and instance mask, then populate per-XCP scheduler arrays; selected VCN rings can be shared by adjacent partitions.

Sysfs configuration creates `compute_partition_config` with supported XCP modes, optional supported NPS modes, writable `xcp_config`, and per-resource child kobjects with `num_inst` and `num_shared`. Per-partition `xcp` kobjects expose metrics from DPM and hide attributes when a partition is invalid. State is runtime-only and tied to current partition mode, DRM nodes, KFD init state, scheduler arrays, sysfs kobjects, and hardware partition configuration.

## Dependencies and integration points

The file depends on AMDGPU XCP manager hooks, DRM device allocation/registration, AMD partition driver redirection, ring schedulers, KFD init/fini, DPM metrics, GFX/XCC topology, GMC memory partition modes, and sysfs/kobject APIs. It also touches per-file private VM memory partition selection through `fpriv->vm.mem_id`.

## Risks and test signals

Risks include switching partition mode while queues are active (the pre-switch TODO is explicit), stale cached mode versus hardware mode, sysfs kobject cleanup mistakes, out-of-range scheduler array indexing by ring type/priority, refcount imbalance in scheduler selection/release, invalid partition opens, and shared VCN partition assignment errors. Test signals include successful creation/removal of render nodes, valid partition-specific file opens, scheduler selection load balancing, KFD teardown/reprobe on mode switch, sysfs `compute_partition_config` contents, DPM metrics reads per XCP, and ring `xcp_id` assignments matching hardware instance masks.
