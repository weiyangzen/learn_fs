<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v5_0_2.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v5_0_2.c

## Purpose
Implements the VCN 5.0.2 IP block. It is a leaner AID-aware VCN 5 path that keeps unified encode rings, DPG/direct boot sequencing, node-id interrupt routing, and sysfs reset-mask support, while omitting SR-IOV MMSCH startup, RAS setup, register dump initialization, and queue reset support for now.

## Important APIs, Types, And Functions
`vcn_v5_0_2_ip_block` exports the IP block callbacks. Core routines include `vcn_v5_0_2_early_init()`, `sw_init()`, `hw_init()`, `suspend()`, `resume()`, `vcn_v5_0_2_start()`, `vcn_v5_0_2_start_dpg_mode()`, `vcn_v5_0_2_stop()`, and `vcn_v5_0_2_stop_dpg_mode()`. Memory windows are programmed by `vcn_v5_0_2_mc_resume()` and `mc_resume_dpg_mode()`. Ring operations are doorbell-backed through `get_rptr()`, `get_wptr()`, and `set_wptr()`; the ring function table reuses VCN 4.0.3 emit helpers but does not define a reset callback.

## Control Flow
Early init assigns one unified encode ring per instance, installs ring and IRQ functions, sets `set_pg_state`, and calls common VCN early init. Software init registers the unified trap with `SOC_V1_0_IH_CLIENTID_VCN`, initializes firmware and rings for every VCN instance, computes doorbell indices using `32 * GET_INST(VCN, i)`, assigns MMHUB by `aid_id`, initializes firmware shared state, and exposes only the soft/full reset mask. Hardware init detects RRMT with bit `0x200`, clears video-tile antihang status bits, programs NBIO doorbell ranges, refreshes shared firmware state, and tests each ring. Start paths mirror 5.0.1 with longer VCPU boot delays in the direct path; DPG start supports indirect PSP SRAM upload and AID selection through the dummy DPG write. Stop drains RB/LMI state or disables DPG mode, then resets VCPU/LMI for direct mode.

## State And Persistence
State is centered in `adev->vcn.inst[]`: `aid_id`, ring doorbell metadata, firmware shared queue flags, pause state, current power state, and DPG SRAM staging. `adev->vcn.supported_reset` intentionally excludes per-queue reset pending firmware support. `sw_fini()` clears firmware shared queue state, suspends/frees common VCN state, tears down sysfs reset mask, and frees `adev->vcn.ip_dump`.

## Dependencies And Integration Points
Depends on VCN 5.0 register definitions, VCN 5.0.1 RRMT constants, VCN 4.0.3 ring emit helpers, SOC15/SOC24 MMIO helpers, PSP SRAM update, NBIO doorbell programming, common VCN firmware/ring/sysfs helpers, node-id to physical map routing, and DRM liveness checks.

## Risks And Test Signals
Risks include no ring reset implementation despite exposing reset masks, a TODO around `ip_dump` freeing, no poison/RAS handling, and sensitive AID/doorbell/physical-instance mapping. The very long direct VCPU polling delays can hide hangs but also reflect expected slow firmware boot. Test signals are ring and IB tests, fence interrupts routed by node ID, RRMT capability bit setting, DPG pause/ack behavior, PSP SRAM update success, suspend/resume, and sysfs reset-mask contents showing no per-queue reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v5_0_2.c -->
