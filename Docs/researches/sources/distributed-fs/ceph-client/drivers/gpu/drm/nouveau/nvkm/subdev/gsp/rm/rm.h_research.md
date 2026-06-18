<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/rm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/rm.h

## Purpose
Declares the Nouveau-side abstraction for GSP Resource Manager implementations. It defines RM implementation metadata, WPR layout policy, function tables for GSP/RPC/control/allocation/client/device/FBSR/display/FIFO/engines/GR, and cross-version helper exports.

## Important APIs, Types, And Functions
Important types are nvkm_rm_impl, nvkm_rm, nvkm_rm_wpr, nvkm_rm_api and nested nvkm_rm_api_gsp/rpc/ctrl/alloc/client/device/fbsr/disp/fifo/engine/gr structs. Important declarations include R535 and R570 implementation objects, r535_gsp ACPI/static-info helpers, allocation/control/RPC/client/device APIs, FBSR/disp/fifo/engine/GR helpers, r570_gr_gpc_mask/r570_gr_tpc_mask, and r570_ofa.

## Control Flow
No executable flow exists. Runtime code dereferences selected rm->api hooks after firmware interface selection, allowing version-specific behavior to plug into common Nouveau GSP code.

## State, Persistence, Dependencies, And Integration
State represented here is the selected RM implementation and WPR/API policy installed in struct nvkm_gsp/nvkm_rm. Dependencies include subdev/gsp.h, handles.h, ACPI types, nvkm display/output/GR/FIFO/MMU abstractions, and generated NVRM payload headers from implementation files.

## Risks And Test Signals
Risks: function-pointer contracts are broad and version skew can create subtle NULL dereferences or ABI mismatches; new RM versions must either supply hooks or safely reuse old ones. Test signals are compile coverage for all initializer tables and runtime coverage of client/device allocation, controls, display, FIFO, GR, FBSR, and engine alloc/free paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/rm.h -->
