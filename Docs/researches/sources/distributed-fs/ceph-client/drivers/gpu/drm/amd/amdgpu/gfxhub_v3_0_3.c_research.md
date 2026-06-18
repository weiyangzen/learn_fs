# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0_3.c

## Purpose
This file implements a GC 11.0.3-specific GFXHUB 3.0.3 backend. It is structurally similar to `gfxhub_v3_0.c` but uses GC 11.0.3 register headers and local default values for GCVM L2 controls.

## Important APIs, Types, and Functions
The public callback table is `gfxhub_v3_0_3_funcs`. It provides FB location/offset readers, VM page-table base programming, GART enable/disable, fault-default policy, and VM hub initialization. Private helpers produce invalidation requests and decode L2 protection faults.

## Control Flow and State
`gart_enable()` initializes VMID0 page-table base/range, system apertures, TLB and L2 cache controls, system-domain context, disabled identity aperture, contexts 1-15, and invalidate address ranges. SR-IOV VFs skip system aperture, cache, identity, and fault default writes that are PF-owned. Unlike v3.0, this file does not set the CP debug halt-disable bit in fault-default handling. `init()` records GC 11.0.3 register offsets, context/invalidation strides, fault interrupt masks, and the private `vmhub_funcs` table in `adev->vmhub`.

## Dependencies and Integration Points
The implementation depends on GC 11.0.3 offset/mask headers and SOC15 accessors. `gmc_v11_0_set_gfxhub_funcs()` selects it when GC IP version is `11.0.3`. GMC and VM code depend on the `vmhub_funcs` hooks for invalidation request encoding and fault decode.

## Risks and Test Signals
Risks are mostly generation-specific register drift, SR-IOV access assumptions, and differences from v3.0 fault behavior. Test signals include boot on GC 11.0.3 devices, GART enable/disable, VM fault decoding, VF operation, and reset/resume with TLB flushes.
