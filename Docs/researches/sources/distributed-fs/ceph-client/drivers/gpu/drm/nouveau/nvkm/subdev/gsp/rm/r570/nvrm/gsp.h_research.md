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
