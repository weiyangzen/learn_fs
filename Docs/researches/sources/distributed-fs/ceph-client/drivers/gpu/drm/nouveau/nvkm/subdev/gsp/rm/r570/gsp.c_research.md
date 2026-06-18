<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/gsp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/gsp.c

## Purpose
Implements the R570-specific nvkm_rm_api_gsp hooks used by Nouveau's GSP-RM path. It sizes suspend/resume data from WPR metadata, suppresses selected noisy GSP event records at normal debug levels, translates RM MC engine indices into nvkm subdev/engine types, pulls static RM information, sends host system information to GSP-RM, and fills cached boot arguments for normal boot and resume.

## Important APIs, Types, And Functions
r570_gsp_sr_data_size, r570_gsp_drop_post_nocat_record, r570_gsp_xlat_mc_engine_idx, r570_gsp_get_static_info, r570_gsp_acpi_info, r570_gsp_set_system_info, r570_gsp_set_rmargs, and the exported r570_gsp api table. It consumes GspStaticConfigInfo, GspSystemInfo, GSP_ARGUMENTS_CACHED, GspFwWprMeta, ACPI_METHOD_DATA, and R570 engine enum values.

## Control Flow
Static info is requested through NV_VGPU_MSG_FUNCTION_GET_GSP_STATIC_INFO; returned internal client/device/subdevice handles are installed into gsp->internal, BAR PDBs and FB region data are copied, optional ACR-provided WPR offsets patch the metadata, and GR GPC/TPC masks are queried to populate gsp->gr counts. System info allocation fills PCI BAR physical addresses, PCI IDs, ACPI display data, config mirror details, primary-display state, and memory-preservation policy before writing the RPC with no reply sequence. Resume changes only the SR argument block, setting oldLevel to GPU level 3 and bInPMTransition.

## State, Persistence, Dependencies, And Integration
Persists internal RM handles, BAR1/BAR2 PDB values, framebuffer region layout, WPR offsets, and GR topology inside struct nvkm_gsp. It depends on r535 helpers for ACPI and FB-region interpretation, nvkm_gsp RPC allocation/write helpers, PCI-backed nvkm_device layout, asm-generic video primary detection, and r570_gr mask functions. Integration points are the r570_api table in rm.c, tu102/tu116 GSP boot flows, FIFO/engine fault translation, and suspend/resume metadata sizing.

## Risks And Test Signals
Risks: ABI drift in GspStaticConfigInfo/GspSystemInfo would corrupt host/GSP contracts; engine-index ranges must match R570 RM enums; TASK_SIZE and ACPI fields are host-architecture sensitive; negative sr_data_size is possible if WPR metadata offsets are inconsistent. Test signals include successful GSP boot with 570.144 firmware, GET_GSP_STATIC_INFO and GSP_SET_SYSTEM_INFO RPC success, correct GR GPC/TPC counts, clean suspend/resume with preserved SR metadata, and no unexpected engine translation failures in fault paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/gsp.c -->
