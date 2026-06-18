# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_0_0.c

Purpose: implements JPEG v5.0.0 for a single instance with VCN 5 register names, optional DPG mode, v5 IRQ source handling, v4.0.3 packet helper reuse, and standard amdgpu JPEG lifecycle integration.

Important APIs and functions: exports `jpeg_v5_0_0_ip_block`. Lifecycle functions initialize shared JPEG state, ring, register dump, reset sysfs, doorbell range, power/clock gating, suspend/resume, and reset. DPG helpers `jpeg_engine_5_0_0_dpg_clock_gating_mode()`, `jpeg_v5_0_0_start_dpg_mode()`, and `_stop_dpg_mode()` write SOC24 JPEG DPG registers or indirect SRAM entries.

Control flow and state: sw init registers `VCN_5_0__SRCID__JPEG_DECODE`, creates a doorbell `jpeg_dec` ring, and uses v5 register dump entries. HW init programs the doorbell range, then skips ring test when JPEG DPG is supported because pause-DPG is not implemented. Start enables DPM, chooses DPG or normal mode, configures power/clock gating, tiling, JMI, interrupts, doorbell control, and JRBC ring base/size. Ring funcs use local pointer callbacks but v4.0.3 packet emission for IB/fence/VM flush/reg wait/wreg/start/end/NOP.

Dependencies and integration: depends on VCN 5.0 register headers, v5 IRQ source IDs, `jpeg_v5_0_0.h` SOC24 DPG offsets, v4.0.3 packet helper declarations, amdgpu JPEG/DPM/reset/sysfs helpers, NBIO doorbells, PSP SRAM update helper, and SOC15/SOC24 register macros.

Risks and test signals: DPG start calls `jpeg_v5_0_0_enable_power_gating()` before enabling PG mode, which is generation-specific and should be validated on hardware. Non-DPG `disable_power_gating()` programs DLDO even without checking `AMD_PG_SUPPORT_JPEG`, unlike enable. Ring tests are skipped under DPG. Packet helpers inherited from v4.0.3 must remain compatible with v5 offsets. Test signals include v5 decode IRQ fence completion, DPG direct/indirect SRAM programming, PSP update, skipped ring test coverage through real IB submission, powergating transitions, and reset recovery.
