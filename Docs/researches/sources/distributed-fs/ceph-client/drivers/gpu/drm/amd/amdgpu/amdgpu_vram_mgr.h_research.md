# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vram_mgr.h

## Purpose

This header defines the VRAM manager's public structures and small helpers around `gpu_buddy` blocks and AMDGPU TTM resources.

## Important APIs, types, and functions

`struct amdgpu_vram_mgr` embeds a `ttm_resource_manager`, `gpu_buddy`, mutex, pending/reserved reservation lists, atomic visible usage, default page size, and allocated-resource list. `struct amdgpu_vres_task` stores pid/command ownership. `struct amdgpu_vram_block_info` reports a block start, size, and owning task. `struct amdgpu_vram_mgr_resource` extends `ttm_resource` with allocated buddy blocks, flags, list node, and task owner. Inline helpers expose block start/size/cleared state, convert `ttm_resource` to AMDGPU VRAM resource, and mark a resource cleared. The exported query is `amdgpu_vram_mgr_query_address_block_info()`.

## Control flow, state, and persistence behavior

There is no standalone control flow. The structures define the state that `amdgpu_vram_mgr.c` maintains while the device is active: buddy allocator contents, reservation lists, visible usage, and per-allocation task metadata. State is rebuilt on driver init and destroyed on manager fini.

## Dependencies and integration points

The header depends on Linux `gpu_buddy` and TTM resource types. It is included by AMDGPU memory management code that needs to inspect VRAM allocations, mark cleared resources, or query which task owns a physical VRAM address block.

## Risks and test signals

Risks include misuse of the `to_amdgpu_vram_mgr_resource()` cast on non-VRAM resources, double-setting `GPU_BUDDY_CLEARED`, and stale task metadata if resources are not removed from the allocation list. Test signals are compile coverage, clear-state reset behavior, and address-owner queries returning expected pid/comm during VRAM allocation stress.
