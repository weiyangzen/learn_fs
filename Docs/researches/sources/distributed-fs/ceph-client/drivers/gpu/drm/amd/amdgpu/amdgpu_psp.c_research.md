
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_psp.c

## Purpose
Implements the Platform Security Processor IP block for AMDGPU. It selects ASIC-specific PSP function tables, loads PSP and non-PSP firmware, creates and drives the PSP command ring, manages trusted memory regions, initializes and invokes trusted applications, supports RAS/XGMI/HDCP/DTM/RAP/SecureDisplay services, handles suspend/resume/reset, exposes firmware update/dump interfaces, and registers PSP IP block versions.

## Important APIs, Types, and Functions
IP lifecycle is provided through `psp_ip_funcs`: `psp_early_init`, `psp_sw_init`, `psp_sw_fini`, `psp_hw_init`, `psp_hw_fini`, `psp_suspend`, and `psp_resume`. Command transport centers on `psp_cmd_submit_buf`, `acquire_psp_cmd_buf`, `release_psp_cmd_buf`, and `psp_ring_cmd_submit`. Firmware loading uses `psp_init_sos_microcode`, `psp_init_ta_microcode`, `psp_init_cap_microcode`, `psp_execute_ip_fw_load`, `psp_load_non_psp_fw`, `psp_load_fw`, `psp_rlc_autoload_start`, and `amdgpu_psp_get_fw_type`. TA helpers are `psp_ta_load`, `psp_ta_unload`, `psp_ta_invoke`, and `psp_ta_init_shared_buf`.

## Control Flow
Early init maps MP0 IP versions to version-specific PSP ops and feature flags, then requests microcode. Software init allocates command/fence/firmware BOs, checks runtime DB entries, and optionally performs memory training. Hardware init initializes firmware BOs, creates or reuses the PSP ring, runs bootloader stages, updates firmware-reserved VRAM, sets up TMR/VMR, loads SMU and other firmware in the required order, starts RLC autoload, and initializes ASD plus optional TA services. Command submission copies a command into the shared command BO, writes a ring frame, waits for the fence value with timeout/RAS-interrupt handling, records PSP response status, and returns failures in SR-IOV or timeout cases. Suspend/hw_fini terminate TAs, unload TMR, and stop/destroy rings; resume repeats memory training and firmware/TA load.

## State and Persistence Behavior
All PSP state is anchored in `adev->psp`: BOs and GPU addresses for private firmware, command, fence, ring, TMR, TA shared buffers, firmware descriptors, command mutex, fence counter, autoload/TMR feature flags, runtime boot config, memory training cache, TA session IDs/status, and staged flash buffers. Runtime DB and boot config are read from VRAM/PSP firmware interfaces; firmware reservation state is reflected into TTM reserved VRAM ranges. Flash staging buffers persist between sysfs write and read-triggered update.

## Dependencies and Integration Points
Depends on version-specific PSP backends (`psp_v3_1` through `psp_v15_0_8`), firmware request/parsing helpers, AMDGPU BO allocation, TTM VRAM reservation, GMC addressing, RAS, XGMI hive state, SecureDisplay helpers, DRM device enter/exit, sysfs attribute groups, debugfs, runtime PM, and SR-IOV policy. It is central to secure firmware loading for gfx, SDMA, SMU, multimedia, DMUB, VPE, ISP, UMSCH, and related IPs.

## Risks and Test Signals
Risks are high because this file gates boot and recovery: wrong firmware order, stale GPU addresses after XGMI migration, command timeout handling, TMR sizing/alignment, SR-IOV skip policy, optional TA failures that should not hard-fail init, mutex deadlocks around command and TA shared buffers, flash buffer bounds, and sysfs/debugfs exposure of firmware update paths. Test signals include successful firmware load on each MP0 generation, SR-IOV VF reset, suspend/resume, RAS error injection/query, XGMI topology discovery, HDCP/DTM/SecureDisplay enablement, IFWI/USB-C PD update visibility gated by capability flags, SPI ROM debugfs dump serialization, and fallback to direct firmware load on PSP init failure.
