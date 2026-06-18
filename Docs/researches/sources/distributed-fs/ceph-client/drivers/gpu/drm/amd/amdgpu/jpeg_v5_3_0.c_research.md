<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_3_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_3_0.c

Purpose: implements JPEG IP block version 5.3.0 for a single JPEG decode instance and ring. It provides normal and dynamic power-gating startup paths, clock-gating controls, ring setup, interrupt processing, and reset integration with the common AMDGPU JPEG ring command helpers.

Important APIs and functions: `jpeg_v5_3_0_early_init()` forces one JPEG instance and one ring, then installs ring and IRQ funcs. `jpeg_v5_3_0_sw_init()` registers the JPEG trap IRQ, initializes common JPEG software/firmware, creates the single decode ring with a doorbell, records pitch register mappings, and initializes reset-mask sysfs. `jpeg_v5_3_0_start()`, `jpeg_v5_3_0_stop()`, `jpeg_v5_3_0_start_dpg_mode()`, and `jpeg_v5_3_0_stop_dpg_mode()` own power and ring programming. `jpeg_v5_3_0_ip_block` exports the AMD IP callbacks.

Control flow: hardware init programs the VCN doorbell range, skips ring testing when JPEG DPG is enabled because pause-DPG is not implemented, and otherwise tests the ring. Non-DPG start enables DPM JPEG clocks, disables power gating, disables clock gating, programs tiling, enables JMI and JRBC interrupts, configures doorbell control, programs the ring base/rptr/wptr/size, and reads back wptr. DPG start enables power gating, sets `JPEG_PG_MODE`, optionally writes DPG SRAM commands and asks PSP to update SRAM, then programs the same JRBC ring registers. Stop reverses DPG mode or resets JMI, enables clock gating, enables power gating, and disables DPM JPEG clocks.

State and persistence behavior: persistent state is in `adev->jpeg.cur_state`, `adev->jpeg.inst[0]`, the decode ring, the ring writeback pointer, DPG SRAM cursor when indirect SRAM is used, and JPEG power/clock/JRBC registers. The ring uses doorbell write pointers via `ring->wptr_cpu_addr` and `WDOORBELL32`. Reset is stop/start based rather than per-core stall/drop.

Dependencies and integration points: depends on VCN 5.3 generated offsets/masks, SOC15 and SOC24 JPEG DPG access macros, PSP SRAM update helpers, DPM JPEG enablement, common JPEG helpers, `jpeg_v4_0_3` packet emitters, and AMDGPU ring/IRQ infrastructure. The ring funcs include `amdgpu_jpeg_dec_parse_cs` and standard JPEG IB/fence/vm-flush emitters.

Risks and edge cases: DPG mode skips ring tests, reducing startup validation. `hw_fini()` only gates if `cur_state` is ungated and the JRBC status register is nonzero. Reset returns early on stop/start failure without calling `amdgpu_ring_reset_helper_end()`, which can leave helper state incomplete. The header guard comment names v5.0.0, a cosmetic but confusing mismatch. Power-gating waits depend on DLDO status bits and `pg_flags` correctness.

Test signals: validate single-ring creation, doorbell programming, normal and DPG start/stop, DPM JPEG toggling, ring test when DPG is disabled, interrupt fence processing for `VCN_5_0__SRCID__JPEG_DECODE`, reset after a timed-out fence, clock-gating enable refusal while not idle, PSP SRAM update on indirect DPG, and suspend/resume through power-state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_3_0.c -->
