# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_xcp.h

## Purpose
This header defines the AMDGPU XCP, or accelerator partition, contract used to expose and manage compute partitions inside one physical GPU. It models partition modes, per-partition IP instance ownership, resource counts, per-XCP DRM-facing state, and the function-table interface that ASIC-specific code such as Aqua Vanjaram implements.

## Important APIs, types, and functions
`MAX_XCP` caps manager-owned partitions at eight. `AMDGPU_XCP_MODE_NONE`, `AMDGPU_XCP_MODE_TRANS`, `AMDGPU_XCP_FL_LOCKED`, `AMDGPU_XCP_NO_PARTITION`, and `AMDGPU_XCP_OPS_KFD` define sentinel and operation flags used by partition switching paths. `XCP_INST_MASK()` maps an instance count and partition id to a contiguous bitmask.

`enum AMDGPU_XCP_IP_BLOCK` names partitionable IP classes: GFXHUB, GFX, SDMA, and VCN. `enum AMDGPU_XCP_STATE` names suspend/resume phases. `enum amdgpu_xcp_res_id` names user-visible resources: XCC, DMA, decode, and JPEG.

`struct amdgpu_xcp_ip_funcs` provides per-IP prepare/suspend/resume hooks over an instance mask. `struct amdgpu_xcp_ip` binds those hooks to one IP block and mask. `struct amdgpu_xcp` stores partition identity, memory id, validity, refcount, DRM device aliases, scheduler arrays, sysfs object, and a unique id. `struct amdgpu_xcp_mgr` stores the owning `amdgpu_device`, lock, function table, XCP array, active mode, supported/available mode bitmaps, resource configuration, and memory allocation mode. `struct amdgpu_xcp_mgr_funcs` is the ASIC extension point for querying and switching partition modes, deriving IP details, mapping memory ids, and optional state transitions.

The exported functions cover manager initialization, XCP initialization, partition query/switch/restore, partition lookup by IP instance, scheduler selection/release, XCP DRM-device registration/open/unplug, KFD-aware pre/post partition switching, supported mode refresh, and sysfs init/fini. `amdgpu_xcp_get_num_xcp()`, `amdgpu_get_next_xcp()`, and `for_each_xcp` are inline iteration helpers.

## Control flow
The header itself has no executable flow beyond helper iteration. Its API implies a standard flow: initialize the manager with ASIC callbacks, query or derive the current mode, initialize `xcp[]` entries, ask ASIC callbacks for each partition's IP masks and resources, then let scheduler/open paths pick per-XCP scheduling state. Mode switches flow through `amdgpu_xcp_pre_partition_switch()`, ASIC `switch_partition_mode`, `amdgpu_xcp_init()`, and `amdgpu_xcp_post_partition_switch()`.

## State and persistence behavior
XCP state is in-memory kernel state attached to `amdgpu_device`. It persists for the lifetime of the device driver instance and is exposed through DRM devices, scheduler lists, and sysfs kobjects. The manager lock serializes mutation. Refcounts and kobjects are important lifetime boundaries for partition device users.

## Dependencies
The header depends on Linux PCI and xarray types, DRM device/scheduler concepts, `amdgpu_ctx.h`, and many declarations from broader AMDGPU headers. ASIC-specific implementers provide `amdgpu_xcp_mgr_funcs`; GFXHUB/GFX/SDMA implementations provide `amdgpu_xcp_ip_funcs`.

## Integration points
Aqua Vanjaram is a direct consumer and implementer of this contract. KFD integration is signaled through `AMDGPU_XCP_OPS_KFD`, scheduler arrays, and partition scheduler update APIs. DRM file open paths use `amdgpu_xcp_open_device()`, and sysfs uses per-XCP kobjects and resource config kobjects.

## Risks and edge cases
The bitmask math assumes contiguous allocation and sane `num_inst`; invalid mode-to-instance ratios can expose empty masks or overlapping partitions. `amdgpu_xcp_get_num_xcp(NULL)` returns one, preserving non-partitioned behavior but requiring callers to understand the fallback. Lifetime bugs around DRM aliases, kobjects, and refcounts would be high impact because XCPs are user-visible devices. Mode switches must coordinate with KFD and schedulers or active queues can point at stale partition topology.

## Test signals
Useful validation comes from ASIC partition-mode switching tests, KFD queue creation across modes, sysfs resource/mode enumeration, suspend/resume across XCPs, and scheduler selection for each hardware IP. Static checks should cover max XCP count, mask overlap, and resource accounting for all supported modes.
