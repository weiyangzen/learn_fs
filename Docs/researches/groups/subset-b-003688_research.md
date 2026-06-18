# subset-b-003688 Research

Grouped source-tree-aligned research for the requested Nouveau GSP/RM, I2C, ICC sense, and instmem files. Each section is delimited for reconciliation into per-file reports.

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/client.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/client.h

## Purpose
Defines the minimal R570 RM root-client allocation contract used by Nouveau's RM allocation layer. The file is an imported NVIDIA open-gpu-kernel-modules 570.144 ABI excerpt rather than executable logic.

## Important APIs, Types, And Functions
Important definitions are NV01_ROOT, NV_PROC_NAME_MAX_LENGTH, and NV0000_ALLOC_PARAMETERS with hClient, processID, processName, and aligned pOsPidInfo. The comment noting hClient must remain first is part of the ABI contract.

## Control Flow
There is no runtime control flow in this header. Consumers allocate a root/client object by filling NV0000_ALLOC_PARAMETERS and passing it through the GSP-RM allocation API selected by r570_client/r535_alloc.

## State, Persistence, Dependencies, And Integration
State is entirely caller-owned payload memory. Dependencies are nvrm/nvtypes.h for NvHandle, NvU32, NvP64, and alignment macros. Integration points are the R570 client ctor declared in rm.h and RM alloc RPCs.

## Risks And Test Signals
Risks: field order or size drift breaks RM allocation. Test signals are compile-time struct compatibility and successful creation/destruction of internal and user RM clients under 570.144 firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/disp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/disp.h

## Purpose
Provides R570 RM display control IDs, payload structures, flags, and allocation parameters used by the Nouveau display RM API. It covers static display data, connector and DP capabilities, link rates, active/connect state, backlight control, DP control, stream/audio control, and display channel pushbuffer/channel DMA allocation.

## Important APIs, Types, And Functions
Key APIs/types include NV2080_CTRL_INTERNAL_DISPLAY_GET_STATIC_INFO_PARAMS, NV0073_CTRL_SYSTEM_GET_SUPPORTED_PARAMS, NV0073_CTRL_SPECIFIC_GET_CONNECTOR_DATA_PARAMS, NV0073_CTRL_CMD_DP_GET_CAPS_PARAMS and DSC caps, NV0073_CTRL_SYSTEM_GET_CONNECT_STATE_PARAMS, NV0073_CTRL_DFP_GET_INFO_PARAMS and DFP flag fields, NV0073_CTRL_SYSTEM_GET_ACTIVE_PARAMS, NV0073_CTRL_SPECIFIC_BACKLIGHT_BRIGHTNESS_PARAMS, NV0073_CTRL_CMD_DP_CONFIG_INDEXED_LINK_RATES_PARAMS, NV0073_CTRL_DP_CTRL_PARAMS, NV0073_CTRL_CMD_DP_CONFIG_STREAM_PARAMS, NV0073_CTRL_DP_SET_AUDIO_MUTESTREAM_PARAMS, NV2080_CTRL_INTERNAL_DISPLAY_CHANNEL_PUSHBUFFER_PARAMS, NV50VAIO_CHANNELDMA_ALLOCATION_PARAMETERS, ChannelPBSize, and PBTARGETAPERTURE.

## Control Flow
The header has no executable control flow. Display code issues RM control calls using these command IDs, fills input fields such as subDeviceInstance/displayId/head/sorIndex, and reads output masks, caps, link tables, active display IDs, or error fields. Channel setup uses pushbuffer physical address/limit/aperture/cache fields before allocating DMA display channels.

## State, Persistence, Dependencies, And Integration
State is marshalled in RPC/control payloads and then copied into display/output objects. Dependencies are nvrm/nvtypes.h and bitfield macro conventions. Integration points are nvkm_rm_api_disp hooks, DP AUX/I2C output probing, display channel allocation, backlight operations, and modeset/link-training code that needs RM DP caps.

## Risks And Test Signals
Risks: duplicate DP_GET_CAPS define is harmless but shows imported-header fragility; bitfield values must match RM exactly; display hotplug/backlight/link-rate behavior depends on firmware interpreting these payloads. Test signals include display enumeration masks, connector data retrieval, DP caps/link-rate configuration, active-head queries, backlight get/set, and display channel pushbuffer allocation on R570 firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/disp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/engine.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/engine.h

## Purpose
Defines the R570 RM engine namespace: MC interrupt/source engine indices, RM_ENGINE_TYPE values, and NV2080_ENGINE_TYPE values. It is the reference used when translating firmware/RM engine identifiers into Nouveau engine instances.

## Important APIs, Types, And Functions
Important definitions include MC_ENGINE_IDX_* ranges for GSP, DISP, CE0-CE19, NVENC, NVJPEG, NVDEC, OFA, GR, GSPLITE, DPAUX, etc.; RM_ENGINE_TYPE_* enum values; and NV2080_ENGINE_TYPE_* constants for graphics, copy, video decode/encode, NVJPG, OFA, and compressed/decompressed copy engines.

## Control Flow
There is no runtime control flow. Consumers such as r570_gsp_xlat_mc_engine_idx and FIFO channel allocation code compare integer engine IDs against these constants and derive nvkm_subdev_type plus instance or NV2080 engine type.

## State, Persistence, Dependencies, And Integration
State is purely symbolic compile-time ABI. Dependencies are nvrm/nvtypes.h. Integration points are GSP notification/fault decoding, FIFO runlist/channel setup, engine object allocation, and RM control payloads that name engines.

## Risks And Test Signals
Risks: numeric drift between this header and the firmware version would misattribute faults, allocate channels on wrong engines, or ignore newer engine IDs. Test signals include correct CE/NVDEC/NVENC/NVJPG/OFA instance discovery and fault recovery messages mapping to expected Nouveau engines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/engine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/fbsr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/fbsr.h

## Purpose
Defines the RM control payload for internal framebuffer suspend/resume initialization. It binds an RM client and system-memory object to the sysmem suspend/resume data area used across low-power transitions.

## Important APIs, Types, And Functions
Important API is NV2080_CTRL_CMD_INTERNAL_FBSR_INIT and NV2080_CTRL_INTERNAL_FBSR_INIT_PARAMS with hClient, hSysMem, bEnteringGcoffState, and aligned sysmemAddrOfSuspendResumeData.

## Control Flow
No local control flow exists. FBSR code fills this struct during suspend entry so GSP-RM can save or restore video memory state and know whether the transition is GC-off related.

## State, Persistence, Dependencies, And Integration
State is the sysmem physical address and RM handles supplied by the caller. Dependencies are nvrm/nvtypes.h. Integration points are nvkm_rm_api_fbsr, GSP SR metadata in gsp.h, and r570_gsp_set_rmargs resume flags.

## Risks And Test Signals
Risks: wrong sysmem address or handle corrupts suspend/resume state; GC-off flag mismatch may select the wrong firmware path. Test signals are successful runtime/system suspend-resume with preserved allocations and no FBSR_INIT control failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/fbsr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/fifo.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/fifo.h

## Purpose
Provides R570 RM payloads and flags for GPFIFO channel allocation, memory descriptors, runqueue/privilege/channel options, RC-triggered event payloads, constructed falcon discovery, and active-channel scheduling control.

## Important APIs, Types, And Functions
Key types include NV_MEMORY_DESC_PARAMS, NV_CHANNEL_ALLOC_PARAMS/NV_CHANNELGPFIFO_ALLOCATION_PARAMETERS, NVOS04_FLAGS_* channel bitfields, ErrorNotifierType, NV_KERNELCHANNEL_ALLOC_INTERNALFLAGS_* fields, rpc_rc_triggered_v17_02, NV2080_CTRL_GPU_CONSTRUCTED_FALCON_INFO, NV2080_CTRL_GPU_GET_CONSTRUCTED_FALCON_INFO_PARAMS, and NV2080_CTRL_INTERNAL_FIFO_TOGGLE_ACTIVE_CHANNEL_SCHEDULING_PARAMS.

## Control Flow
No executable flow is present. FIFO allocation code fills memory descriptors for instance, USERD, RAMFC, method buffer, notifier memory, GP FIFO offset/entries, VASpace handle, engine type, cid, and subdevice mask before asking GSP-RM to allocate a channel. RC event handlers decode rpc_rc_triggered_v17_02 and may call Nouveau recovery logic by chid.

## State, Persistence, Dependencies, And Integration
State is command payload memory and firmware event payloads. Dependencies are nvrm/nvtypes.h and R570 NV2080 engine constants. Integration points are nvkm_rm_api_fifo, channel object allocation, fault recovery notification, constructed falcon context sizing, and scheduler quiesce paths.

## Risks And Test Signals
Risks: packed flexible rcJournalBuffer must be length-checked by consumers; channel memory aperture/cache fields must match actual nvkm_memory backing; flag drift can change privilege/security behavior. Test signals include channel creation/destruction on graphics/copy/video engines, RC recovery for faulted chids, scheduler toggle controls, and constructed falcon info queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/fifo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/gr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/gr.h

## Purpose
Defines R570 graphics RM control payloads for context buffer discovery, GPC/TPC topology queries, a graphics scrubber workaround, and ZCULL information.

## Important APIs, Types, And Functions
Important definitions are NV2080_CTRL_INTERNAL_STATIC_GR_GET_CONTEXT_BUFFERS_INFO_PARAMS, NV2080_CTRL_INTERNAL_STATIC_GR_CONTEXT_BUFFERS_INFO, NV2080_CTRL_INTERNAL_ENGINE_CONTEXT_BUFFER_INFO, engine context property IDs, NV2080_CTRL_GPU_GET_FERMI_GPC_INFO_PARAMS, NV2080_CTRL_GPU_GET_FERMI_TPC_INFO_PARAMS, KGRAPHICS_SCRUBBER_HANDLE_* constants, NV2080_CTRL_INTERNAL_GR_INIT_BUG4208224_WAR_PARAMS, and NV2080_CTRL_GR_GET_ZCULL_INFO_PARAMS.

## Control Flow
There is no local control flow. GR code issues internal controls to fetch per-engine context-buffer size/alignment, query global GPC mask and per-GPC TPC masks, set up or tear down the scrubber workaround, and retrieve ZCULL geometry constraints.

## State, Persistence, Dependencies, And Integration
State lives in RM control payloads and then is copied into r535/r570 GR objects. Dependencies are nvrm/nvtypes.h and the RM control path. Integration points are r570_gr_gpc_mask/r570_gr_tpc_mask used by gsp.c, GR channel/context promotion, scrubber initialization, and ZCULL allocation setup.

## Risks And Test Signals
Risks: context-buffer enum count must match RM; topology masks are used to size GPU resources; scrubber handle constants must not collide. Test signals include correct GR unit counts, context promotion success, ZCULL info availability, and graphics workload startup after scrubber init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/gr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/gsp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/gsp.h

## Purpose
Defines the core R570 GSP-RM ABI payloads for static configuration, host system information, ACPI data, WPR/SR metadata, boot arguments, heap sizing constants, and FMC/ACR boot parameters. It is the primary data contract consumed by gsp.c and tu102.c.

## Important APIs, Types, And Functions
Key types include NV2080_CTRL_CMD_FB_GET_FB_REGION_INFO_PARAMS and region entries, GspStaticConfigInfo, BUSINFO, DOD/JT/MUX/CAPS/ACPI_METHOD_DATA, GSP_VF_INFO, GSP_PCIE_CONFIG_REG, GspSystemInfo, rpc_os_error_log_v17_00, GspFwWprMeta, MESSAGE_QUEUE_INIT_ARGUMENTS, GSP_SR_INIT_ARGUMENTS, GSP_ARGUMENTS_CACHED, GspFwSRMeta, GSP_FMC_INIT_PARAMS, GSP_ACR_BOOT_GSP_RM_PARAMS, GSP_RM_PARAMS, GSP_SPDM_PARAMS, and GSP_FMC_BOOT_PARAMS. Important constants include GSP_FW_WPR_META_MAGIC/REVISION and heap-size constants for LIBOS2/LIBOS3/TU10X/GH100.

## Control Flow
No executable flow is present. Boot code fills GspFwWprMeta with sysmem addresses for radix3 ELF, bootloader, signature, FB WPR/non-WPR heap ranges, FRTS, VGA workspace, and partition/crash-report fields. r570_gsp_get_static_info consumes GspStaticConfigInfo, and r570_gsp_set_system_info produces GspSystemInfo. Resume uses GspFwSRMeta plus GSP_ARGUMENTS_CACHED SR flags.

## State, Persistence, Dependencies, And Integration
State modeled here persists across boot, runtime, and suspend/resume: framebuffer layout, internal RM handles, BAR PDE bases, ACPI data, SR payload addresses, heap sizing, boot count, and verified status. Dependencies are nvrm/nvtypes.h and engine.h. Integration points are secure booter, ACR/FMC flows, GSP message queues, RM RPC setup, ACPI display integration, FB region setup, and suspend/resume.

## Risks And Test Signals
Risks: this is a firmware ABI boundary with strict sizes/alignment; WPR metadata is security-sensitive and corrupted offsets can prevent boot or expose protected memory; heap constants influence low-memory failures; ACPI and PCI fields are platform-specific. Test signals include successful secure boot, verified WPR metadata, static/system info RPC exchange, FB region parsing, suspend/resume SR metadata reuse, and firmware version compatibility with 570.144.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/gsp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/msgfn.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/msgfn.h

## Purpose
Defines the GSP event IDs used by the host message notification path. It maps symbolic event names to the 0x1000-series values emitted by GSP-RM.

## Important APIs, Types, And Functions
Important entries include GSP_INIT_DONE, POST_EVENT, RC_TRIGGERED, MMU_FAULT_QUEUED, OS_ERROR_LOG, UCODE_LIBOS_PRINT, DISPLAY_MODESET, GSP_LOCKDOWN_NOTICE, UPDATE_GSP_TRACE, GSP_POST_NOCAT_RECORD, FECS_ERROR, RECOVERY_ACTION, and NUM_EVENTS.

## Control Flow
No executable flow exists. Code registers callbacks for selected event IDs with r535_gsp_msg_ntfy_add and the message receiver dispatches incoming GSP events by these values.

## State, Persistence, Dependencies, And Integration
State is event identity only. Dependencies are nvrm/nvtypes.h. Integration points are r570_gsp_drop_post_nocat_record, FIFO RC handling, OS error logging, display event handling, and GSP boot/init notification.

## Risks And Test Signals
Risks: enum drift drops or misroutes asynchronous firmware notifications. Test signals include GSP_INIT_DONE delivery, RC_TRIGGERED processing, lockdown/nocat filtering at expected debug levels, and absence of unknown event spam.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/msgfn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/ofa.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/ofa.h

## Purpose
Defines the Optical Flow Accelerator allocation payload used by the R570 OFA engine allocation hook.

## Important APIs, Types, And Functions
Important type is NV_OFA_ALLOCATION_PARAMETERS with size, prohibitMultipleInstances, and engineInstance.

## Control Flow
No control flow exists. r570_ofa_alloc creates this payload, sets size to sizeof payload and engineInstance to the requested instance, then submits the RM allocation.

## State, Persistence, Dependencies, And Integration
State is caller-owned allocation payload. Dependencies are nvrm/nvtypes.h. Integration points are r570_ofa in ofa.c and the generic nvkm_rm_api_engine allocator path.

## Risks And Test Signals
Risks: wrong size or instance value can make RM reject OFA allocation or allocate the wrong hardware instance. Test signals are OFA object allocation on chips exposing OFA0/OFA1 and correct failure on absent instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/ofa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/rpcfn.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/rpcfn.h

## Purpose
Defines the global GSP/RM/UVM RPC function IDs for 570.144. The file uses an X macro so it can either define enum values directly or be included by another macro consumer.

## Important APIs, Types, And Functions
Important IDs include GET_GSP_STATIC_INFO=65, GSP_SET_SYSTEM_INFO=72, GSP_RM_CONTROL=76, GSP_RM_ALLOC=103, many CTRL_* operations for FIFO/GR/MMU/perf/NVLINK/fabric, SAVE_HIBERNATION_DATA/RESTORE_HIBERNATION_DATA, INVALIDATE_TLB, RM_API_CONTROL, and NUM_FUNCTIONS=227.

## Control Flow
There is no executable flow. RPC helpers pass these IDs in message headers so GSP-RM dispatches to the correct server-side handler. The X macro pattern allows alternate generation of tables or enums.

## State, Persistence, Dependencies, And Integration
State is symbolic RPC identity. Dependencies are nvrm/nvtypes.h and the message/RPC helpers. Integration points include every R570 RM API table entry, gsp.c static/system info RPCs, allocation/control paths, UVM paging channels, hibernation data handling, and TLB invalidation.

## Risks And Test Signals
Risks: one wrong numeric value can call the wrong firmware operation; deprecated/reserved values must not be reused by host code casually. Test signals include successful boot-time RPC sequence, object allocation/control operations, TLB invalidation, and no firmware status errors for known IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/rpcfn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/ofa.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/ofa.c

## Purpose
Implements the R570 RM engine allocator for OFA objects. It adapts the generic nvkm_rm_api_engine allocation hook to the R570 NV_OFA_ALLOCATION_PARAMETERS payload.

## Important APIs, Types, And Functions
Main API is r570_ofa_alloc(parent, handle, oclass, inst, ofa), exported through const struct nvkm_rm_api_engine r570_ofa. It uses nvkm_gsp_rm_alloc_get and nvkm_gsp_rm_alloc_wr.

## Control Flow
Allocation requests reserve an RM payload/object under the parent, fill size and engineInstance, then write the allocation to GSP-RM. IS_ERR is treated as a warning and returned as PTR_ERR.

## State, Persistence, Dependencies, And Integration
State is the initialized nvkm_gsp_object for the OFA engine and the firmware-side allocation. Dependencies are rm/engine.h and nvrm/ofa.h. Integration points are r570_api.ofa, engine object creation, and R570 engine index translation for OFA instances.

## Risks And Test Signals
Risks: no local validation of inst beyond RM failure; WARN_ON on allocation-get errors may be noisy if absent hardware is probed incorrectly. Test signals include successful OFA allocation for valid instances and clean -errno propagation for unsupported classes/instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/ofa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/rm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/rm.c

## Purpose
Defines R570 WPR heap layout profiles and the central R570 RM API table that combines R570-specific GSP/client/display/fifo/GR/FBSR/OFA hooks with reused R535 allocation/control/device/video-engine helpers.

## Important APIs, Types, And Functions
Important objects are r570_wpr_libos2, r570_wpr_libos3, r570_wpr_libos3_gh100, r570_wpr_libos3_gb10x, r570_wpr_libos3_gb20x, r570_api, and exported nvkm_rm_impl instances r570_rm_tu102, r570_rm_ga102, r570_rm_gh100, r570_rm_gb10x, and r570_rm_gb20x.

## Control Flow
There is no branching control flow beyond static initializer selection. Chip-specific GSP firmware interface tables select one of these nvkm_rm_impl profiles; boot/layout code then reads rm->wpr for heap/carveout/reserved sizes and rm->api for operations.

## State, Persistence, Dependencies, And Integration
State is immutable function-pointer and WPR configuration data. Dependencies are rm.h and R570/R535 helper exports. Integration points are tu102/tu116 GSP fwif entries, GH100/GB10x/GB20x GSP implementations, WPR metadata construction, and all RM object/control APIs.

## Risks And Test Signals
Risks: mixing R535 and R570 hooks assumes ABI compatibility where reused; WPR heap sizes and offset_set_by_acr change secure-boot memory layout; wrong profile for a chip can break boot or suspend. Test signals include firmware load on each listed family, correct heap sizing, object allocation across display/FIFO/GR/video engines, and suspend/resume on ACR-offset platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/rm.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/rpc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/rpc.h

## Purpose
Declares shared helper interfaces for GSP-RM RPC/message handling and payload container recovery.

## Important APIs, Types, And Functions
Important APIs are to_payload_hdr(p, header), r535_gsp_rpc_poll, r535_gsp_msg_recv, r535_gsp_msg_ntfy_add, and r535_rpc_status_to_errno.

## Control Flow
No implementation is present. Callers use to_payload_hdr to recover an enclosing RPC header from a params pointer, poll/wait for RPC completion, receive asynchronous messages, register notification callbacks, and translate RM status values to Linux errno.

## State, Persistence, Dependencies, And Integration
State is held by the caller's nvkm_gsp queues and message buffers. Dependencies are rm.h and container_of semantics. Integration points are r570_gsp static/system RPCs, event registration for nocat/lockdown notices, FIFO RC events, and all RM control/allocation helpers.

## Risks And Test Signals
Risks: wrong payload/header association corrupts message parsing; status translation must preserve actionable errno. Test signals include RPC completion under load, asynchronous event callback delivery, and correct errno propagation from firmware failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/rpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/tu1xx.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/tu1xx.c

## Purpose
Defines the static RM GPU class table for TU1xx/Turing GSP-RM operation. It names display, usermode, FIFO channel, copy, graphics, and video engine classes exposed to RM allocation paths.

## Important APIs, Types, And Functions
Important object is const struct nvkm_rm_gpu tu1xx_gpu. Fields include display root/caps/core/window/immediate/cursor classes, TURING_USERMODE_A, TURING_CHANNEL_GPFIFO_A plus tu102_chan_doorbell_handle, TURING_DMA_COPY_A, graphics class set, NVC4B0_VIDEO_DECODER, and NVC4B7_VIDEO_ENCODER.

## Control Flow
There is no control flow. tu102/tu116 GSP function tables point rm.gpu at tu1xx_gpu so RM allocation code can choose the correct class IDs for objects and channels.

## State, Persistence, Dependencies, And Integration
State is immutable class metadata. Dependencies are gpu.h, engine/fifo/priv.h, and nvif/class.h. Integration points are Turing GSP firmware interface entries, channel allocation, display channel allocation, and GR/video engine object creation.

## Risks And Test Signals
Risks: wrong class IDs cause RM object allocation failure or incompatible pushbuffer/channel behavior. Test signals include Turing display channel creation, GPFIFO channel startup, CE/GR/NVDEC/NVENC object allocation, and doorbell writes using the expected handle format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/tu1xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/tu102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/tu102.c

## Purpose
Implements Turing TU102-family GSP firmware loading, secure booter setup, WPR metadata construction, framebuffer layout calculation, init/fini boot sequences, and firmware interface selection for R570/R535/fallback modes.

## Important APIs, Types, And Functions
Important functions are tu102_gsp_fwsec_sb_ctor/dtor, tu102_gsp_booter_unload/load, tu102_gsp_booter_ctor, tu102_gsp_fwsec_load_bld, tu102_gsp_reset, tu102_gsp_fini, tu102_gsp_init, tu102_gsp_wpr_meta_init, tu102_gsp_wpr_heap_size, tu102_gsp_vga_workspace_addr, tu102_gsp_oneinit, tu102_gsp_load_rm, tu102_gsp_load, and tu102_gsp_new. Important objects are tu102_gsp_fwsec, tu102_gsp_flcn, tu102_gsp, tu102_gsps, and NVKM_GSP_FIRMWARE_BOOTER declarations.

## Control Flow
Load path optionally honors NvGspRm, loads gsp/bootloader/booter_load/booter_unload firmware, and selects R570 570.144 before R535 535.113.01, then nofw fallback. oneinit measures FB, reserves BIOS/VGA workspace, constructs booter falcon firmware, runs common R535 oneinit, computes FRTS/boot/ELF/heap/WPR/non-WPR FB regions downward from the top of usable FB, creates WPR metadata, prepares FRTS, resets GSP into RISC-V mode, and writes libos address to falcon registers. init passes WPR meta on cold boot or SR meta on resume to booter-load, then enters r535_gsp_init. fini tears down RM, resets falcon, reloads secure booter state, and runs booter-unload with optional SR meta mailbox.

## State, Persistence, Dependencies, And Integration
Persists firmware blobs, falcon firmware objects, FB layout, WPR metadata, SR metadata, booter mailboxes, and rm implementation selection. Dependencies include SEC2 falcon, nvfw bin/HS headers, gm200 falcon helpers, r535 GSP common code, R570/R535 RM impls, framebuffer sizing, and GSP memory helpers. Integration points are Nouveau device init/fini, suspend/resume, firmware request infrastructure, secure boot, and RM RPC startup.

## Risks And Test Signals
Risks: FB layout arithmetic must avoid overlap with BIOS workspace; secure firmware signature parsing assumes HS header validity; booter unload treats WPR2 residual state as error; resume depends on SR metadata existing and valid. Test signals include firmware load by version, secure booter load/unload success, WPR2 cleared after unload, GSP init RPC availability, suspend/resume through SR metadata, and fallback when NvGspRm is disabled or firmware missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/tu102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/tu116.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/tu116.c

## Purpose
Defines the TU116/TU117 GSP function table by reusing the TU102 implementation with TU11x signature section and the same Turing RM GPU class table.

## Important APIs, Types, And Functions
Important objects are tu116_gsp, tu116_gsps, tu116_gsp_new, and NVKM_GSP_FIRMWARE_BOOTER declarations for tu116/tu117 at 535.113.01 and 570.144.

## Control Flow
There is little local control flow. tu116_gsp_new calls nvkm_gsp_new_ with an fwif list that tries R570 570.144, then R535 535.113.01, then GV100 no-firmware fallback. All init/fini/load/reset/oneinit hooks delegate to TU102 functions.

## State, Persistence, Dependencies, And Integration
State is immutable firmware-interface metadata and signature-section selection. Dependencies are priv.h, TU102 helper exports, r570_rm_tu102/r535_rm_tu102, and tu1xx_gpu. Integration points are TU116/TU117 device constructors and shared Turing GSP boot/RM logic.

## Risks And Test Signals
Risks: signature section mismatch would fail firmware authentication; shared TU102 layout assumptions must hold for TU11x. Test signals include firmware discovery for tu116/tu117, secure boot with .fwsignature_tu11x, and successful RM startup using the reused TU102 path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/tu116.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/Kbuild

## Purpose
Lists all Nouveau nvkm I2C subdev objects built into nvkm-y: base constructors, generation frontends, pad implementations, bus implementations, bit-bang logic, AUX implementations, and ANX9805 external encoder support.

## Important APIs, Types, And Functions
Important entries include base.o, nv04/nv4e/nv50/g94/gf117/gf119/gk104/gk110/gm200.o, pad*.o, bus*.o, bit.o, aux*.o, and anx9805.o.

## Control Flow
Kbuild has no runtime control flow; it controls link inclusion so chip constructors can reference shared helpers and generation-specific ops.

## State, Persistence, Dependencies, And Integration
State is build-system configuration. Dependencies are the surrounding DRM/Nouveau make hierarchy. Integration points are kernel build/link and module symbol availability.

## Risks And Test Signals
Risks: omitting one object breaks constructor references or feature support for a GPU generation. Test signals are successful kernel/module build and probe of each generation-specific I2C constructor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/anx9805.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/anx9805.c

## Purpose
Implements an nvkm_i2c_pad for Analogix ANX9805 external DisplayPort encoders, exposing a downstream emulated I2C bus and DP AUX channel over an upstream GPU I2C bus.

## Important APIs, Types, And Functions
Important types/functions include anx9805_pad, anx9805_bus, anx9805_aux, anx9805_bus_xfer, anx9805_bus_new, anx9805_aux_xfer, anx9805_aux_lnk_ctl, anx9805_aux_new, anx9805_pad_func, and anx9805_pad_new.

## Control Flow
The bus xfer resets/arms the encoder, supports EDID-style reads from address 0x50 with segment/offset tracking and segment writes to 0x30, polls a status bit, and disables the bridge command register on exit. AUX xfer writes payload bytes to encoder registers, programs command/address/size, starts the transaction, waits for completion, checks error status, and copies read data back. Link control writes bandwidth/lane/enhanced framing registers and polls training completion.

## State, Persistence, Dependencies, And Integration
State includes upstream bus pointer, encoder I2C addresses, segment/offset locals, per-pad bus/aux child objects, and hardware register state inside ANX9805. Dependencies are nvkm I2C helpers, bus/pad/aux constructors, and nvkm_rdi2cr/nvkm_wri2cr. Integration points are DCB external encoder discovery in base.c and DP output AUX/link-training paths.

## Risks And Test Signals
Risks: only a narrow set of I2C message patterns is supported; polling uses fixed 5 ms intervals and retry limits; address mapping only handles encoder addresses 0x39/0x3b. Test signals include external DP EDID reads, AUX DPCD access, ANX link training, and clean -ETIMEDOUT/-EIO behavior on missing encoders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/anx9805.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/auxch.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/auxch.c

## Purpose
Provides the common nvkm_i2c_aux object lifecycle and Linux i2c_adapter bridge for DisplayPort AUX channels, including acquisition, release, monitor mode, and I2C-over-AUX transfer splitting.

## Important APIs, Types, And Functions
Important APIs include nvkm_i2c_aux_i2c_xfer, nvkm_i2c_aux_monitor, nvkm_i2c_aux_acquire/release, nvkm_i2c_aux_xfer, nvkm_i2c_aux_lnk_ctl, nvkm_i2c_aux_ctor/new_/del/init/fini, and the nvkm_i2c_aux_i2c_algo.

## Control Flow
I2C-over-AUX transfers acquire the AUX pad, split messages into <=16 byte chunks, sets read/write and MOT bits, retries zero-length completions up to 32 times, and returns the original message count on success. Lifecycle functions toggle enabled under a mutex, register/unregister i2c_adapter objects, and delegate hardware transactions to aux->func.

## State, Persistence, Dependencies, And Integration
State includes aux enabled flag, mutex, pad pointer, id, interrupt mask bit, and registered i2c_adapter. Dependencies are Linux I2C core, pad arbitration, and generation-specific AUX xfer functions. Integration points are DP EDID over AUX, DPCD access, hotplug events, and external encoder AUX implementations.

## Risks And Test Signals
Risks: address-only transactions are rejected unless the backend advertises support; chunk retry handling relies on backend updating cnt; pad arbitration can return -EBUSY. Test signals include DP EDID reads over AUX I2C, direct AUX DPCD reads/writes, monitor mode switching, hotplug interrupt delivery, and suspend/resume init/fini.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/auxch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/auxch.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/auxch.h

## Purpose
Declares the internal AUX backend interface, constructors, generation-specific AUX constructors, transfer helper, link-control hook, autodpcd wrapper, and logging macros.

## Important APIs, Types, And Functions
Important type is nvkm_i2c_aux_func with address_only, xfer, and lnk_ctl. Important declarations include nvkm_i2c_aux_ctor/new_/del/init/fini/xfer, g94_i2c_aux_new/_xfer, gf119_i2c_aux_new, gm200_i2c_aux_new, and AUX_* macros.

## Control Flow
No executable control flow except inline nvkm_i2c_aux_autodpcd, which calls the i2c function hook when present. The inline currently passes false to the hook regardless of enable, so users should inspect whether this is intentional for disabling HW DPCD around manual AUX transactions.

## State, Persistence, Dependencies, And Integration
State is API contract only. Dependencies are pad.h and priv.h. Integration points are auxch.c, auxg94.c, auxgf119.c, auxgm200.c, anx9805.c, and generation i2c constructors.

## Risks And Test Signals
Risks: backend xfer signatures must honor size in/out semantics; the autodpcd helper's enable argument is not forwarded and is a review hotspot. Test signals include compile coverage of all backends and functional AUX transactions on generations with/without autodpcd hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/auxch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/auxg94.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/auxg94.c

## Purpose
Implements DP AUX transfers for G94-style hardware using MMIO blocks at 0x00e4c0/0x00e4d0/0x00e4e0/0x00e4e4/0x00e4e8 plus pad ownership handshakes.

## Important APIs, Types, And Functions
Important functions are g94_i2c_aux_init/fini, g94_i2c_aux_xfer, g94_i2c_aux_new_, g94_i2c_aux_new, and g94_i2c_aux_func.

## Control Flow
Transfer init waits for idle, requests AUX ownership with magic bits, checks sink detect, disables autodpcd, writes up to 16 bytes for writes, programs type/size/address, resets and starts the transaction, polls up to 2 ms, decodes retry/timeout/error status, optionally retries up to 32 times, reads data/status for reads, re-enables autodpcd, and releases ownership.

## State, Persistence, Dependencies, And Integration
State includes channel number, aux interrupt bit, temporary transfer buffer, and hardware control/status registers. Dependencies are auxch.h, nvkm MMIO helpers, pad->i2c, and optional aux_autodpcd hook. Integration points are g94/gf119 pad constructors and DP AUX/DPCD/EDID logic.

## Risks And Test Signals
Risks: fixed register offsets and bit meanings are generation-specific; sink-not-detected is returned as -ENXIO; retry/status code mapping must match hardware. Test signals include DPCD reads/writes, hotplug detect, AUX retry behavior, and no stuck ownership after timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/auxg94.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/auxgf119.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/auxgf119.c

## Purpose
Provides a GF119 AUX backend wrapper that reuses the G94 transfer implementation while enabling address-only AUX transactions.

## Important APIs, Types, And Functions
Important object is gf119_i2c_aux and constructor gf119_i2c_aux_new, which calls g94_i2c_aux_new_.

## Control Flow
No independent transfer flow exists; all hardware operations delegate to g94_i2c_aux_xfer with address_only set true.

## State, Persistence, Dependencies, And Integration
State is the base g94_i2c_aux object created by g94_i2c_aux_new_. Dependencies are auxch.h and auxg94.c. Integration points are GF119 pad constructors and GF119/GK/GPU generations using the G94-style AUX register block.

## Risks And Test Signals
Risks: assumes GF119 register layout is compatible with G94 while changing address-only semantics. Test signals are address-only DPCD operations and normal AUX reads/writes on GF119-class hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/auxgf119.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/auxgm200.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/auxgm200.c

## Purpose
Implements DP AUX transfers for GM200-style hardware using the 0x00d930/0x00d940/0x00d950/0x00d954/0x00d958 register block and supports address-only transactions.

## Important APIs, Types, And Functions
Important functions are gm200_i2c_aux_init/fini, gm200_i2c_aux_xfer, gm200_i2c_aux_new, and gm200_i2c_aux_func.

## Control Flow
Control flow mirrors g94 AUX: acquire ownership, check sink detect, disable autodpcd, write data for write commands, program command/address/size, reset/start, poll completion, decode status and retry, copy read data, restore autodpcd, and release ownership.

## State, Persistence, Dependencies, And Integration
State includes channel index, aux interrupt mask, temporary xbuf, and GM200 control/status registers. Dependencies are auxch.h, nvkm MMIO, and GM200 pad/autodpcd hooks. Integration points are gm200_i2c pad constructors and DP AUX users on Maxwell-era display hardware.

## Risks And Test Signals
Risks: uses 8 native aux channels in gm200.c but one-bit interrupt per ch; timeout handling must leave hardware in a usable state; GSP-RM path disables native GM200 I2C. Test signals include DP AUX on GM200 without GSP-RM, address-only transactions, and clean failure on absent sinks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/auxgm200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/base.c

## Purpose
Constructs and manages Nouveau I2C pads, bit-bang/native I2C buses, AUX channels, external encoder pads, and AUX interrupt events from BIOS DCB tables.

## Important APIs, Types, And Functions
Important APIs include nvkm_i2c_bus_find, nvkm_i2c_aux_find, nvkm_i2c_intr, nvkm_i2c_preinit/init/fini/dtor, nvkm_i2c_new_, and the internal nvkm_i2c_drv table mapping ANX9805 extdev IDs to anx9805_pad_new.

## Control Flow
Constructor parses DCB I2C entries, creates shared or per-CCB pads, creates bus objects based on DCB type and pad capabilities, creates AUX objects for NVIO_AUX/PMGR entries, then parses display outputs for external encoders and creates external ANX9805 bus/AUX children. Preinit brings up pads/buses early for VBIOS scripts; init also enables AUX; fini disables AUX/buses/pads and masks/acks interrupts; intr reads aux_stat and emits NVKM_I2C_PLUG/UNPLUG/IRQ/DONE events per aux id.

## State, Persistence, Dependencies, And Integration
State includes i2c pad/bus/aux lists, event object, enabled state inside children, and BIOS-derived IDs. Dependencies are BIOS DCB/I2C/output parsers, nvkm_event, generation-specific pad funcs, and ANX9805 support. Integration points are display probing, EDID/DDC, DP AUX/hotplug, VBIOS init scripts, and power-sensor I2C users.

## Risks And Test Signals
Risks: malformed BIOS entries can create no bus/aux or ignored CCBs; primary/secondary bus remapping depends on DCB I2C table version; external encoders require known extdev IDs. Test signals include CCB debug logs, I2C adapter registration, EDID read on primary/secondary buses, AUX hotplug event delivery, and clean teardown with no list leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/bit.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/bit.c

## Purpose
Implements Nouveau's optional internal bit-banging I2C transfer engine over per-bus drive/sense callbacks when CONFIG_NOUVEAU_I2C_INTERNAL is enabled.

## Important APIs, Types, And Functions
Important functions are nvkm_i2c_raise_scl, i2c_start, i2c_stop, i2c_bitw, i2c_bitr, nvkm_i2c_get_byte, nvkm_i2c_put_byte, i2c_addr, and nvkm_i2c_bit_xfer. Constants define timeout/rise-fall/hold timing.

## Control Flow
Transfers emit repeated starts per message, send address with read bit, read/write bytes MSB-first, generate ACK/NACK, stop at the end, and return number of messages or a negative errno. SCL raising polls for clock-stretch release and times out.

## State, Persistence, Dependencies, And Integration
State is the electrical line state driven via bus->func callbacks. Dependencies are bus.h, udelay, and generation-specific drive/sense callbacks. Integration points are nv04/nv4e/nv50/gf119 bus implementations and i2c_adapter setup in bus.c when internal bit-bang is selected.

## Risks And Test Signals
Risks: timing constants are conservative and may be slow; CONFIG_NOUVEAU_I2C_INTERNAL disabled makes the function return -ENODEV; stuck lines return -EBUSY/-ETIMEDOUT. Test signals include DDC reads with internal algorithm enabled, clock-stretch timeout behavior, and fallback to Linux i2c-algo-bit when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/bit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/bus.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/bus.c

## Purpose
Provides common nvkm_i2c_bus lifecycle, adapter registration, pad arbitration, Linux I2C algorithm selection, and device probing helpers.

## Important APIs, Types, And Functions
Important APIs include nvkm_i2c_bus_init/fini/acquire/release/probe/del/ctor/new_, nvkm_i2c_bus_xfer, nvkm_i2c_bus_pre_xfer/post_xfer, and line drive/sense callbacks for i2c-algo-bit.

## Control Flow
Constructor registers an i2c_adapter either with Linux i2c_bit_algo using drive/sense callbacks or with a custom algorithm calling bus->func->xfer. Transfers acquire the bus mutex and pad in I2C mode, call backend xfer, then release. Probe temporarily adjusts bit-bang udelay for specific devices and scans candidate addresses.

## State, Persistence, Dependencies, And Integration
State includes bus enabled flag, mutex, pad pointer, id, i2c_adapter, optional algo_data, and backend function table. Dependencies are Linux I2C core, core options NvI2C, and pad arbitration. Integration points are BIOS-created DDC buses, iccsense sensors, external encoder upstream I2C, and display EDID paths.

## Risks And Test Signals
Risks: bus->func constructor return values are not always checked by chip-specific new functions; pad contention yields -EBUSY; adapter registration failures must unwind via nvkm_i2c_bus_del. Test signals include adapter enumeration, EDID/I2C transfers through both algorithm modes, probe detection logs, and suspend/resume enable gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/bus.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/bus.h

## Purpose
Declares the backend function table and constructors/destructors for nvkm I2C bus objects plus generation-specific bus constructors and logging macros.

## Important APIs, Types, And Functions
Important type is nvkm_i2c_bus_func with init, drive_scl, drive_sda, sense_scl, sense_sda, and xfer hooks. Declarations include nvkm_i2c_bus_ctor/new_/del/init/fini, nvkm_i2c_bit_xfer, nv04/nv4e/nv50/gf119 bus constructors, and BUS_* macros.

## Control Flow
No executable control flow is present. Implementations fill this function table to expose either line-level bit-bang support or backend xfer support to bus.c.

## State, Persistence, Dependencies, And Integration
State is API contract only. Dependencies are pad.h and Linux i2c_msg through included headers. Integration points are bus.c, bit.c, and all bus*.c implementations.

## Risks And Test Signals
Risks: backends must provide a coherent set of hooks; drive_scl without intended bit-algo selection changes adapter behavior. Test signals are compile coverage and working DDC/I2C transfers on each generation-specific bus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/bus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/busgf119.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/busgf119.c

## Purpose
Implements GF119-style I2C line control via MMIO registers at 0x00d014 + drive*0x20.

## Important APIs, Types, And Functions
Important functions are gf119_i2c_bus_drive_scl, gf119_i2c_bus_drive_sda, gf119_i2c_bus_sense_scl, gf119_i2c_bus_sense_sda, gf119_i2c_bus_init, and gf119_i2c_bus_new.

## Control Flow
Init writes 0x7 to the bus register. Drive functions set bits 0/1 for SCL/SDA outputs; sense functions read bits 4/5; transfers use nvkm_i2c_bit_xfer through the common bus core.

## State, Persistence, Dependencies, And Integration
State includes per-bus register address and inherited bus state. Dependencies are bus.h and nvkm MMIO helpers. Integration points are GF119/GK/GM pad constructors and DCB-created bus instances.

## Risks And Test Signals
Risks: drive index directly selects register offset without range validation. Test signals include DDC transfer on GF119-class busses and correct line high/low sensing under i2c-algo-bit/internal bit-bang.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/busgf119.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/busnv04.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/busnv04.c

## Purpose
Implements legacy NV04 I2C bit-banging through VGA CRTC registers for drive and sense lines.

## Important APIs, Types, And Functions
Important functions are nv04_i2c_bus_drive_scl/sda, nv04_i2c_bus_sense_scl/sda, and nv04_i2c_bus_new.

## Control Flow
Drive callbacks modify VGA register bits 0x20/0x10 and set enable bit 0x01; sense callbacks read bits 0x04/0x08 from the sense register. Transfers use nvkm_i2c_bit_xfer.

## State, Persistence, Dependencies, And Integration
State includes drive and sense register indices from BIOS CCB entries. Dependencies are subdev/vga.h, bus.h, and VGA register access helpers. Integration points are nv04_i2c_pad_new and legacy DDC/VBIOS I2C.

## Risks And Test Signals
Risks: VGA register access must be valid for the device and head; no range validation on BIOS-provided drive/sense values. Test signals include EDID reads on NV04-era hardware and no stuck line errors during VBIOS I2C use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/busnv04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/busnv4e.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/busnv4e.c

## Purpose
Implements NV4E-era I2C line control using an MMIO address derived from 0x600800 + BIOS drive offset.

## Important APIs, Types, And Functions
Important functions are nv4e_i2c_bus_drive_scl/sda, nv4e_i2c_bus_sense_scl/sda, and nv4e_i2c_bus_new.

## Control Flow
Drive callbacks mask low control bits for SCL/SDA; sense callbacks read high status bits 0x00040000/0x00080000. Transfers use nvkm_i2c_bit_xfer.

## State, Persistence, Dependencies, And Integration
State is the calculated register address. Dependencies are bus.h and nvkm MMIO helpers. Integration points are nv4e_i2c_pad_new and DCB I2C buses for NV4E-style hardware.

## Risks And Test Signals
Risks: BIOS drive offset is trusted; wrong offset can touch unrelated MMIO. Test signals include DDC transfers on NV4E devices and correct -ETIMEDOUT behavior for clock-stretch/stuck bus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/busnv4e.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/busnv50.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/busnv50.c

## Purpose
Implements NV50 I2C bit-banging over a fixed table of MMIO register addresses selected by BIOS drive index.

## Important APIs, Types, And Functions
Important functions are nv50_i2c_bus_drive_scl/sda, nv50_i2c_bus_sense_scl/sda, nv50_i2c_bus_init, and nv50_i2c_bus_new.

## Control Flow
Constructor validates drive against a 10-entry address table, initializes cached data to 0x7, and registers the bus. Init writes 0x7; drive callbacks update cached bits 0/1 and write the register; sense callbacks read bits 0/1.

## State, Persistence, Dependencies, And Integration
State includes selected register address and cached output data. Dependencies are bus.h, subdev/vga.h include, and MMIO helpers. Integration points are nv50/g94 pad constructors and BIOS CCB bus creation.

## Risks And Test Signals
Risks: only known drive indices are supported; cached data must stay synchronized with hardware writes. Test signals include EDID reads on each valid NV50 bus index and warning/-ENODEV for unknown bus indices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/busnv50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/g94.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/g94.c

## Purpose
Defines the G94 I2C function table with G94 pad constructors, four native AUX channels, and G94 AUX interrupt status/mask operations.

## Important APIs, Types, And Functions
Important functions are g94_aux_stat, g94_aux_mask, and g94_i2c_new; important object is g94_i2c.

## Control Flow
Interrupt status reads pending/enable registers, expands four-bit per-AUX event fields into hi/lo/request/transaction masks, and acks pending interrupts. Masking updates enabled event bits per AUX channel. Constructor delegates to nvkm_i2c_new_.

## State, Persistence, Dependencies, And Integration
State is AUX interrupt enable/pending MMIO and the common nvkm_i2c object. Dependencies are priv.h, pad.h, and G94 pad/AUX backends. Integration points are hotplug/AUX events and DCB-created G94 buses.

## Risks And Test Signals
Risks: eight-channel loops with aux=4 rely on mask bits; event type bit layout must match hardware. Test signals are plug/unplug IRQs and AUX DONE events on G94 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/g94.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/gf117.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/gf117.c

## Purpose
Creates a minimal GF117 I2C subdev using GF119 external pad constructors and no native AUX interrupt hooks.

## Important APIs, Types, And Functions
Important object is gf117_i2c and constructor gf117_i2c_new.

## Control Flow
The constructor delegates to nvkm_i2c_new_ with only pad_x_new set.

## State, Persistence, Dependencies, And Integration
State is common nvkm_i2c state populated from BIOS. Dependencies are priv.h and pad.h. Integration points are GF117 display DDC bus creation.

## Risks And Test Signals
Risks: absence of pad_s_new/aux hooks means BIOS AUX/shared-pad entries may be ignored. Test signals are successful DDC I2C adapter creation on GF117.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/gf117.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/gf119.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/gf119.c

## Purpose
Defines GF119 I2C using GF119 pad constructors and G94-style AUX interrupt registers with four native AUX channels.

## Important APIs, Types, And Functions
Important object is gf119_i2c and constructor gf119_i2c_new.

## Control Flow
Constructor delegates to nvkm_i2c_new_; interrupt stat/mask hooks reuse g94_aux_stat/g94_aux_mask.

## State, Persistence, Dependencies, And Integration
State is common I2C lists plus AUX event registers. Dependencies are pad.h and g94.c helpers. Integration points are GF119 DDC/AUX/hotplug.

## Risks And Test Signals
Risks: shared G94 interrupt layout assumption. Test signals include I2C adapter registration, AUX transfers, and hotplug events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/gf119.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/gk104.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/gk104.c

## Purpose
Defines GK104 I2C with GF119 pads and GK104-specific AUX interrupt registers at 0x00dc60/0x00dc68.

## Important APIs, Types, And Functions
Important functions are gk104_aux_stat, gk104_aux_mask, gk104_i2c_new, and object gk104_i2c.

## Control Flow
Status reads pending/mask registers, decodes four event bits per AUX channel, acks pending bits, and masking updates enabled event bits. Constructor delegates to nvkm_i2c_new_.

## State, Persistence, Dependencies, And Integration
State is common nvkm_i2c plus GK104 AUX interrupt registers. Dependencies are GF119 pad constructors and MMIO. Integration points are GK104 DP AUX/hotplug.

## Risks And Test Signals
Risks: interrupt ack/mask register values must be correct. Test signals are hotplug and AUX DONE/IRQ events on GK104.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/gk104.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/gk110.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/gk110.c

## Purpose
Extends GK104-style I2C with an autodpcd control hook for GK110 AUX channels.

## Important APIs, Types, And Functions
Important function is gk110_aux_autodpcd and constructor gk110_i2c_new.

## Control Flow
Autodpcd masks bit 16 in 0x00e4f8 + aux*0x50 based on enable, while other behavior uses GF119 pads and GK104 aux stat/mask.

## State, Persistence, Dependencies, And Integration
State is common I2C plus autodpcd MMIO bit. Dependencies are priv.h/pad.h and nvkm_mask. Integration points are AUX transfers that temporarily disable hardware DPCD reads.

## Risks And Test Signals
Risks: auxch.h wrapper currently passes false to aux_autodpcd regardless of requested enable, affecting this hook. Test signals are stable manual AUX transfers around hardware DPCD access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/gk110.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/gm200.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/gm200.c

## Purpose
Defines GM200 native I2C/AUX support with GM200 shared pads, GF119 external pads, eight AUX channels, GK104 interrupt hooks, GM200 autodpcd control, and disables this path when GSP-RM is active.

## Important APIs, Types, And Functions
Important functions are gm200_aux_autodpcd and gm200_i2c_new; object is gm200_i2c.

## Control Flow
Constructor first checks nvkm_gsp_rm(device->gsp) and returns -ENODEV if GSP-RM owns the display/I2C services; otherwise delegates to nvkm_i2c_new_. Autodpcd updates bit 16 at 0x00d968 + aux*0x50.

## State, Persistence, Dependencies, And Integration
State is common I2C plus GM200 autodpcd and AUX interrupt registers. Dependencies include subdev/gsp.h, GF119/GM200 pad and AUX backends. Integration points are non-GSP GM200 display probing and GSP ownership arbitration.

## Risks And Test Signals
Risks: returning -ENODEV under GSP-RM must be expected by callers; eight AUX channels with GK104 mask hooks must align. Test signals include no duplicate native I2C under GSP-RM and working AUX/DDC without GSP-RM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/gm200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/nv04.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/nv04.c

## Purpose
Defines the NV04 I2C subdev with legacy NV04 pad creation only.

## Important APIs, Types, And Functions
Important object is nv04_i2c and constructor nv04_i2c_new.

## Control Flow
Constructor delegates to nvkm_i2c_new_ with pad_x_new = nv04_i2c_pad_new.

## State, Persistence, Dependencies, And Integration
State is common I2C lists created from BIOS. Dependencies are priv.h and pad.h. Integration points are NV04 DDC/VBIOS I2C.

## Risks And Test Signals
Risks: supports only legacy bit-bang bus entries. Test signals are adapter creation and EDID reads on NV04 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/nv04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/nv4e.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/nv4e.c

## Purpose
Defines the NV4E I2C subdev with NV4E pad creation only.

## Important APIs, Types, And Functions
Important object is nv4e_i2c and constructor nv4e_i2c_new.

## Control Flow
Constructor delegates to nvkm_i2c_new_ with pad_x_new = nv4e_i2c_pad_new.

## State, Persistence, Dependencies, And Integration
State is common I2C lists. Dependencies are priv.h/pad.h. Integration points are NV4E DCB I2C bus creation.

## Risks And Test Signals
Risks: no AUX support. Test signals are DDC transfers on NV4E hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/nv4e.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/nv50.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/nv50.c

## Purpose
Defines the NV50 I2C subdev with NV50 pad creation only.

## Important APIs, Types, And Functions
Important object is nv50_i2c and constructor nv50_i2c_new.

## Control Flow
Constructor delegates to nvkm_i2c_new_ with pad_x_new = nv50_i2c_pad_new.

## State, Persistence, Dependencies, And Integration
State is common I2C lists. Dependencies are priv.h/pad.h. Integration points are NV50 DDC bus creation.

## Risks And Test Signals
Risks: no native AUX hooks in this frontend. Test signals are DDC adapter creation and EDID reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/nv50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/pad.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/pad.c

## Purpose
Implements common pad arbitration, mode switching, construction/destruction, and init/fini for physical pins shared by I2C and AUX users.

## Important APIs, Types, And Functions
Important APIs are nvkm_i2c_pad_mode, nvkm_i2c_pad_acquire/release, nvkm_i2c_pad_init/fini/del/ctor/new_, and internal nvkm_i2c_pad_mode_locked.

## Control Flow
Acquire locks the pad mutex and either accepts the current mode, switches from OFF to requested I2C/AUX mode, or returns -EBUSY if another mode owns the pad. Release unlocks and may call mode_locked for OFF state. Init reapplies stored mode; fini forces OFF.

## State, Persistence, Dependencies, And Integration
State includes pad mode, mutex, id, list link, i2c pointer, and backend mode hook. Dependencies are pad.h and generation-specific mode functions. Integration points are bus and aux acquire/release paths.

## Risks And Test Signals
Risks: pad_release appears to call mode_locked only when mode is OFF, so active mode may remain selected until explicit mode/fini; contention bugs surface as -EBUSY. Test signals include concurrent I2C/AUX access rejection and correct mode register programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/pad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/pad.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/pad.h

## Purpose
Declares pad identifiers, modes, backend function table, constructors, generation-specific pad constructors, ANX9805 pad constructor, and logging macros.

## Important APIs, Types, And Functions
Important definitions are NVKM_I2C_PAD_HYBRID/CCB/EXT, enum nvkm_i2c_pad_mode, nvkm_i2c_pad_func with bus_new_0/bus_new_4/aux_new_6/mode, and pad constructor declarations.

## Control Flow
No executable flow exists. The header defines how base.c asks pads to create buses/AUX objects and how bus/aux code arbitrates pin mode.

## State, Persistence, Dependencies, And Integration
State is API contract. Dependencies are priv.h. Integration points are all pad*.c, bus*.c, aux*.c, and external encoder code.

## Risks And Test Signals
Risks: ID namespaces must not collide; mode callbacks must be valid for shared pads. Test signals are compile coverage and correct pad IDs in trace logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/pad.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padg94.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padg94.c

## Purpose
Implements G94 pad mode programming and pad constructors for shared/native and external pads.

## Important APIs, Types, And Functions
Important APIs are g94_i2c_pad_mode, g94_i2c_pad_s_new, and g94_i2c_pad_x_new.

## Control Flow
Mode programming selects OFF/I2C/AUX by writing 0x00e500 and 0x00e50c offsets based on hybrid pad id. Shared pads provide bus_new_4, aux_new_6, and mode; external pads provide bus/AUX constructors without mode hook.

## State, Persistence, Dependencies, And Integration
State is pad mode and hardware selection bits. Dependencies are pad.h, auxch.h, bus.h, nv50_i2c_bus_new, and g94_i2c_aux_new. Integration points are G94/GF119 constructors and DCB shared pad entries.

## Risks And Test Signals
Risks: base calculation assumes HYBRID id namespace. Test signals are successful switching between DDC I2C and DP AUX on shared G94 pads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padg94.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padgf119.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padgf119.c

## Purpose
Defines GF119 pad constructors using GF119 bus and AUX backends while reusing G94 shared-pad mode programming.

## Important APIs, Types, And Functions
Important APIs are gf119_i2c_pad_s_new and gf119_i2c_pad_x_new.

## Control Flow
Shared pad constructor supplies gf119_i2c_bus_new, gf119_i2c_aux_new, and g94_i2c_pad_mode; external pad constructor supplies bus/AUX constructors without mode hook.

## State, Persistence, Dependencies, And Integration
State is inherited nvkm_i2c_pad state. Dependencies are pad.h, auxch.h, bus.h, and G94 mode helper. Integration points are GF119/GK constructors.

## Risks And Test Signals
Risks: assumes G94 pad mode registers apply to GF119 shared pads. Test signals are DDC/AUX operation and mode switching on GF119 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padgf119.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padgm200.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padgm200.c

## Purpose
Implements GM200 shared-pad mode programming and pad constructors using GF119 bus and GM200 AUX backends.

## Important APIs, Types, And Functions
Important APIs are gm200_i2c_pad_s_new and gm200_i2c_pad_x_new; internal helper is gm200_i2c_pad_mode.

## Control Flow
Mode programming writes GM200 registers 0x00d970 and 0x00d97c per hybrid pad to select OFF/I2C/AUX. Shared pads include mode hook; external pads do not.

## State, Persistence, Dependencies, And Integration
State is pad mode and GM200 hardware selection bits. Dependencies are pad.h, auxch.h, bus.h, gf119_i2c_bus_new, and gm200_i2c_aux_new. Integration points are gm200_i2c frontend.

## Risks And Test Signals
Risks: register offset must match GM200 display block and native path is bypassed under GSP-RM. Test signals are DDC/AUX transfers on non-GSP GM200 and correct shared-pad arbitration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padgm200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padnv04.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padnv04.c

## Purpose
Defines a minimal NV04 pad function table capable of creating NV04 legacy bit-bang buses.

## Important APIs, Types, And Functions
Important object is nv04_i2c_pad_func and API nv04_i2c_pad_new.

## Control Flow
Constructor delegates to nvkm_i2c_pad_new_ with bus_new_0 = nv04_i2c_bus_new.

## State, Persistence, Dependencies, And Integration
State is common pad state only. Dependencies are pad.h and bus.h. Integration points are nv04_i2c_new and legacy CCB entries.

## Risks And Test Signals
Risks: no mode hook/AUX support. Test signals are NV04 DDC bus creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padnv04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padnv4e.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padnv4e.c

## Purpose
Defines a minimal NV4E pad function table capable of creating NV4E MMIO bit-bang buses.

## Important APIs, Types, And Functions
Important object is nv4e_i2c_pad_func and API nv4e_i2c_pad_new.

## Control Flow
Constructor delegates to nvkm_i2c_pad_new_ with bus_new_4 = nv4e_i2c_bus_new.

## State, Persistence, Dependencies, And Integration
State is common pad state only. Dependencies are pad.h and bus.h. Integration points are nv4e_i2c_new.

## Risks And Test Signals
Risks: no AUX/shared mode support. Test signals are NV4E DDC bus creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padnv4e.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padnv50.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padnv50.c

## Purpose
Defines a minimal NV50 pad function table capable of creating NV50 MMIO bit-bang buses.

## Important APIs, Types, And Functions
Important object is nv50_i2c_pad_func and API nv50_i2c_pad_new.

## Control Flow
Constructor delegates to nvkm_i2c_pad_new_ with bus_new_4 = nv50_i2c_bus_new.

## State, Persistence, Dependencies, And Integration
State is common pad state only. Dependencies are pad.h and bus.h. Integration points are nv50_i2c_new and G94 external pads.

## Risks And Test Signals
Risks: no AUX/shared mode support in this file. Test signals are NV50 DDC bus creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padnv50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/priv.h

## Purpose
Defines the private nvkm_i2c function table and shared helper declarations used by all I2C generation implementations.

## Important APIs, Types, And Functions
Important type is nvkm_i2c_func with pad_x_new, pad_s_new, aux count, aux_stat, aux_mask, and aux_autodpcd hooks. It declares nvkm_i2c_new_, g94/gk104 aux stat/mask helpers, and nvkm_i2c container macro.

## Control Flow
No executable flow exists. base.c consumes this table to construct pads/buses/AUX and handle interrupts/autodpcd.

## State, Persistence, Dependencies, And Integration
State is API contract. Dependencies are subdev/i2c.h and BIOS/display core types. Integration points are all generation frontend files and auxch.h.

## Risks And Test Signals
Risks: optional hooks must be NULL-checked consistently; aux count must match hardware/backend support. Test signals are compile coverage and runtime probe on generations with and without AUX hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/iccsense/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/iccsense/Kbuild

## Purpose
Adds ICC sense base and GF100 frontend objects to nvkm-y.

## Important APIs, Types, And Functions
Entries are nvkm/subdev/iccsense/base.o and gf100.o.

## Control Flow
No runtime control flow; it controls link inclusion.

## State, Persistence, Dependencies, And Integration
State is build configuration. Dependencies are Nouveau Kbuild. Integration points are kernel build and GF100 iccsense constructor availability.

## Risks And Test Signals
Risks: missing objects remove power sensor support. Test signals are successful build and gf100_iccsense_new symbol availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/iccsense/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/iccsense/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/iccsense/base.c

## Purpose
Implements Nouveau current/power sensing from BIOS-described INA209/INA219/INA3221 sensors over I2C, including sensor validation, rail creation, sensor configuration, and aggregate power reads.

## Important APIs, Types, And Functions
Important functions include nvkm_iccsense_validate_device, nvkm_iccsense_poll_lane, nvkm_iccsense_ina209/ina219/ina3221_read, nvkm_iccsense_sensor_config, nvkm_iccsense_read_all, nvkm_iccsense_create_sensor/get_sensor, nvkm_iccsense_oneinit, nvkm_iccsense_init, nvkm_iccsense_dtor, nvkm_iccsense_ctor, and nvkm_iccsense_new_.

## Control Flow
oneinit reads BIOS power budget caps, parses ICCSENSE rails, creates validated sensors from external-device BIOS entries and primary/secondary I2C buses, checks supported sensor IDs, records config, creates enabled resistor rails with sensor-specific read callbacks, and stores power limits. init writes config to each sensor. read_all iterates rails and sums calculated power from shunt and bus voltage registers.

## State, Persistence, Dependencies, And Integration
State includes sensor list, rail list, data_valid flag, power_w_max/crit, sensor config/address/type/i2c adapter, and rail resistor/index/read callback. Dependencies are BIOS extdev/iccsense/power_budget parsers, nvkm_i2c_bus_find, I2C register helpers, and supported INA sensor register maps. Integration points are thermal/power management consumers reading total board power.

## Risks And Test Signals
Risks: invalid or unknown sensors disable or taint readings; arithmetic is integer and assumes BIOS resistor milliohms and sensor LSBs; I2C failures abort aggregate reads. Test signals include BIOS parse logs, sensor ID validation, config writes, plausible power readings under load, and graceful behavior when sensors are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/iccsense/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/iccsense/gf100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/iccsense/gf100.c

## Purpose
Provides the GF100-generation constructor for the common ICC sense implementation.

## Important APIs, Types, And Functions
Important API is gf100_iccsense_new, which calls nvkm_iccsense_new_.

## Control Flow
No additional control flow; all behavior is in base.c.

## State, Persistence, Dependencies, And Integration
State is common nvkm_iccsense state. Dependencies are priv.h. Integration points are GF100 device/subdev construction and power sensor consumers.

## Risks And Test Signals
Risks: assumes GF100 uses the generic BIOS/I2C-driven implementation. Test signals are successful subdev creation and sensor reads on GF100-class boards with ICCSENSE tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/iccsense/gf100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/iccsense/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/iccsense/priv.h

## Purpose
Declares private sensor and rail structures plus constructors for the ICC sense subdev.

## Important APIs, Types, And Functions
Important types are nvkm_iccsense_sensor with id/type/i2c/addr/config and nvkm_iccsense_rail with read callback/sensor/index/mohm. It declares nvkm_iccsense_ctor and nvkm_iccsense_new_.

## Control Flow
No executable control flow. base.c owns list population and callbacks.

## State, Persistence, Dependencies, And Integration
State is structure layout for sensors/rails. Dependencies are subdev/iccsense.h and BIOS extdev types. Integration points are base.c and gf100.c.

## Risks And Test Signals
Risks: sensor lifetime is tied to iccsense dtor and rail pointers must not outlive sensors. Test signals are clean teardown and no use-after-free under subdev destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/iccsense/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/Kbuild

## Purpose
Adds the instance-memory base plus generation implementations to nvkm-y.

## Important APIs, Types, And Functions
Entries include base.o, nv04.o, nv40.o, nv50.o, gk20a.o, and gh100.o.

## Control Flow
No runtime flow; controls link inclusion.

## State, Persistence, Dependencies, And Integration
State is build configuration. Dependencies are Nouveau Kbuild. Integration points are device-specific instmem constructor availability.

## Risks And Test Signals
Risks: omitting a generation object breaks device probe. Test signals are successful build and symbol resolution for all listed constructors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/base.c

## Purpose
Implements common instance-memory object lifecycle, save/restore, allocation wrapper, zeroing fallback, boot object separation, and subdev init/fini/suspend/resume plumbing.

## Important APIs, Types, And Functions
Important APIs include nvkm_instobj_load/save/dtor/ctor/wrap/new, nvkm_instmem_rd32/wr32/boot, nvkm_instmem_fini/init/oneinit/dtor, and nvkm_instmem_ctor.

## Control Flow
instobj_save allocates a suspend buffer and copies memory via kmap or ro32 loop; load restores via kmap or wo32 loop then frees suspend. new delegates to imem->func->memory_new, optionally zeroes if backend lacks zero support, marks preserve, and returns nvkm_memory. boot moves current objects to a boot list for slowpath access. fini optionally calls backend suspend and marks suspended, then backend fini; init resumes if suspended or initializes BAR2 otherwise.

## State, Persistence, Dependencies, And Integration
State includes instobj list/boot list, spinlock, mutex, suspend flag, per-object preserve and suspend buffer, and backend function table. Dependencies are nvkm_memory, nvkm_bar_bar2_init, backend instmem funcs, and memory mapping helpers. Integration points are FIFO/GR/MMU object allocations, BAR2 instance access, and system suspend/resume.

## Risks And Test Signals
Risks: save/load size assumes 32-bit aligned memory; zeroing fallback can be slow; list moves require lock correctness; preserve flag influences suspend behavior. Test signals include instmem allocations with zero flag, suspend/resume restoration, BAR2 init on cold boot, and no list corruption on object destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/gh100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/gh100.c

## Purpose
Defines GH100 instance-memory support by using the R535/nv50 instmem implementation with a GH100-specific BAR0 window programming hook.

## Important APIs, Types, And Functions
Important functions are gh100_instmem_set_bar0_window_addr and gh100_instmem_new; important object is gh100_instmem.

## Control Flow
The hook writes NV_XAL_EP_BAR0_WINDOW with the shifted address. Constructor calls r535_instmem_new with fini/memory_new/memory_wrap inherited from nv50-style helpers and the set_bar0_window_addr hook.

## State, Persistence, Dependencies, And Integration
State is common r535/nv50 instmem state plus BAR0 window register. Dependencies are priv.h, nvhw/ref/gh100/pri_nv_xal_ep.h, nv50/r535 instmem helpers. Integration points are GH100 device construction and GSP-era BAR0 windowed instance access.

## Risks And Test Signals
Risks: window base shift must match GH100 hardware spec; reused nv50 helpers must remain compatible. Test signals include GH100 probe, BAR0 window accesses hitting expected instance memory, and allocation/wrap success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/gh100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/gk20a.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/gk20a.c

## Purpose
Implements instance memory for Tegra GK20A, which lacks dedicated VRAM, using either IOMMU-flattened system pages or physically contiguous DMA memory, with write-combined CPU mappings and L2 cache maintenance.

## Important APIs, Types, And Functions
Important types include gk20a_instobj, gk20a_instobj_dma, gk20a_instobj_iommu, and gk20a_instmem. Important functions include target/page/addr/size callbacks, acquire/release for DMA/IOMMU, vaddr GC/recycle, rd32/wr32/map, DMA/IOMMU destructors, constructors, gk20a_instobj_new, gk20a_instmem_dtor, and gk20a_instmem_new.

## Control Flow
Constructor selects IOMMU if the Tegra device has a domain, otherwise DMA API with weak-ordering/write-combine attrs. Allocation rounds size/align to pages, creates either contiguous DMA memory or individual pages mapped into the GPU IOMMU address space, sets nvkm_memory callbacks, and returns NCOH memory. IOMMU acquire flushes LTC, reuses or creates vmap write-combined mappings, maintains use counts, and enforces a 1 MiB vaddr LRU budget; release moves idle mappings to LRU and invalidates LTC. DMA acquire/release returns the persistent DMA vaddr and flushes/invalidates LTC. Destructors free DMA memory or unmap/free IOMMU pages and address-space nodes.

## State, Persistence, Dependencies, And Integration
State includes GPU address node, CPU vaddr, IOMMU pages/dma_addrs/use count/LRU links, vaddr usage counters, Tegra IOMMU domain/mm/bit/pgshift, DMA attrs, and common instmem lists. Dependencies are core Tegra device data, nvkm_mm, iommu API, DMA API, vmap/vunmap, nvkm_ltc_flush/invalidate, nvkm_vmm_map, and nv04 suspend/resume helpers. Integration points are GK20A MMU/FIFO/GR instance allocations and coherent access on integrated-memory GPUs.

## Risks And Test Signals
Risks: IOMMU bit manipulation and pgshift must match Tegra addressing; vaddr LRU must not recycle mappings in use; cache maintenance is conservative but essential for correctness; error unwind in IOMMU allocation must free partially mapped pages. Test signals include operation with and without IOMMU, instmem read/write/map correctness, vaddr budget recycling, suspend/resume through nv04 helpers, and no DMA/IOMMU leaks on allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/gk20a.c -->
