<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_umsch_mm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_umsch_mm.h

## Purpose
`amdgpu_umsch_mm.h` defines the UMSCH MM scheduler interface: engine and priority enums, packet input layouts, firmware-log format, function pointer table, device state container, register-write macro, helper wrappers, and exported lifecycle/utility APIs.

## Important APIs, Types, And Functions
`enum UMSCH_SWIP_ENGINE_TYPE` names VCN0, VCN1, combined VCN, and VPE engines. `enum UMSCH_CONTEXT_PRIORITY_LEVEL` defines idle, normal, focus, realtime, and count. `struct umsch_mm_set_resource_input` configures VMID masks, collaboration, logging VMID, engine mask, and feature flags. Queue add/remove packet structures carry process, page-table, VA range, quantum, CSA, priority, doorbell, engine, MQD, context handles, VM context control, and suspend/collaboration flags. `struct MQD_INFO` mirrors queue ring state. `struct umsch_mm_funcs` abstracts version-specific set-resource, queue, register, microcode, and ring operations. `struct amdgpu_umsch_mm` is the persistent scheduler state.

The header declares packet submission, fence polling, microcode init/allocation, PSP command-buffer execution, ring init, firmware-log setup, and the `umsch_mm_v4_0_ip_block`. The `WREG32_SOC15_UMSCH` macro either appends register writes to the PSP command buffer or writes registers directly depending on firmware load type.

## Control Flow
Common code calls wrapper macros like `umsch_mm_set_hw_resources`, `umsch_mm_load_microcode`, and `umsch_mm_ring_start`, which dispatch only when the selected version table provides an implementation. IP-version-specific code fills the function table and register offsets during early init.

## State And Persistence
The `amdgpu_umsch_mm` struct persists across IP-block lifetime and owns ring, firmware, command buffer, writeback, masks, AGDB indices, mutex, and log memory. Command-buffer pointer state is especially important under PSP load because register writes become serialized PSP commands.

## Dependencies And Integration Points
The header is consumed by common UMSCH code and `umsch_mm_v4_0` implementation files, and it depends on AMDGPU ring, BO, firmware, VCN, VPE, PSP, and doorbell infrastructure.

## Risks
Packet structure layout must match firmware exactly. The register-write macro assumes `adev` is available in lexical scope and that `cmd_buf_curr_ptr` has enough space. Function wrapper macros silently return success when callbacks are absent, which is convenient for optional hooks but can hide missing version implementations. Locking is exposed as thin mutex helpers and must be consistently used by queue users.

## Test Signals
Compile v4.0 UMSCH with PSP and non-PSP load types, validate command-buffer register programming, add/remove queue packet binary layout, priority and engine masks, firmware-log struct interpretation, and callback presence for supported VCN versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_umsch_mm.h -->
