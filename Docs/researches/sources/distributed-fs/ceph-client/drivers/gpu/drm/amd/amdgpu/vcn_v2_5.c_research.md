# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v2_5.c

## Purpose

`vcn_v2_5.c` implements VCN 2.5 and VCN 2.6. It adapts the VCN 2.x design for up to two hardware instances, harvested-instance detection, per-instance doorbells and VM hubs, SR-IOV two-instance MMSCH setup, shared idle/power accounting, reuse of VCN 2.0 ring packet helpers, and VCN 2.6 RAS poison interrupt/status handling.

## Important APIs, Types, And Functions

The file exports `vcn_v2_5_ip_block`, `vcn_v2_6_ip_block`, and `vcn_v2_6_ras_hw_ops`. Lifecycle hooks are shared between 2.5 and 2.6 through `vcn_v2_5_ip_funcs` and `vcn_v2_6_ip_funcs`. `vcn_v2_5_early_init()` detects harvested instances or configures SR-IOV instances, sets ring/IRQ/RAS functions, and runs common VCN early init per instance. `vcn_v2_5_sw_init()` initializes each non-harvested instance, registers decode/encode/RAS IRQs, sets internal register aliases, configures doorbells and VM hubs, initializes rings, firmware shared flags, reset callbacks, RAS, register dump, and reset-mask sysfs.

Start/stop logic is in `vcn_v2_5_start()`, `vcn_v2_5_start_dpg_mode()`, `vcn_v2_5_stop()`, and `vcn_v2_5_stop_dpg_mode()`. `vcn_v2_5_sriov_start()` builds per-engine MMSCH v1.1 tables and `vcn_v2_5_mmsch_start()` submits them. Ring functions use VCN 2.5 pointer accessors but reuse VCN 2.0 emitters for packet content.

## Control Flow

Hardware init either starts SR-IOV and marks VF schedulers or, for bare metal, enables each instance's doorbell range and tests decode plus encoder rings. Normal start skips harvested instances, enables DPM per instance, configures anti-hang/power/clock state, programs VCPU memory windows and tiling, boots VCPU with retry loops, initializes decode and two encode rings under firmware shared queue-reset flags, and reads back status. DPG start writes the same state through DPG-mode accessors, supports indirect SRAM, enables VCN 2.6 RAS registers when applicable, and resets decode queue state.

Idle work aggregates fences across all non-harvested instances and gates the whole VCN block only when all fences and total submissions are gone. Begin/end-use increments/decrements atomic submission counters, ungates the block, updates DPG pause for encoder submissions when firmware is not handling unified queues, and manages the VCN performance profile.

## State And Persistence

State is per `adev->vcn.inst[i]`: firmware, shared firmware page, decode and encode rings, register aliases, pause state, reset callback, RAS poison IRQ, DPG SRAM, atomic DPG encoder submission count, and ring `me` instance IDs. Shared state includes `adev->vcn.num_vcn_inst`, `harvest_config`, `supported_reset`, `ras`, and `inst[0].total_submission_cnt`. Firmware shared queue mode flags persist queue-reset coordination.

## Dependencies And Integration Points

Dependencies include common VCN firmware/ring/RAS helpers, VCN 2.0 ring emitters, SOC15 VCN 2.5 registers, MMSCH v1.0/v1.1 structures, IRQ client IDs for VCN0/VCN1, DPM, NBIO doorbell ranges, PSP SRAM update, register dump/sysfs reset mask helpers, and AMDGPU RAS late init. It integrates with the RAS framework by setting `adev->vcn.ras` for IP 2.6 and processing poison IRQs through `amdgpu_vcn_process_poison_irq`.

## Risks And Test Signals

Risks include harvested-instance masking errors, using `inst[i]` state after skip, doorbell index collisions across instances, VM hub mismatch on IP 2.5, SR-IOV table size/offset mistakes, shared idle gating while another instance still has submissions, DPG pause races with atomic counters, VCN 2.6 RAS enablement on non-2.6 parts, and a suspicious fwlog init reference to `inst[i]` after an inner loop where `i` may equal `num_enc_rings`. Test signals include one- and two-instance boot, harvested-instance disable path returning `-ENOENT` when both are disabled, per-instance ring tests, SR-IOV scheduler readiness, DPG direct/indirect paths, reset-mask sysfs, RAS poison IRQ/status tests on IP 2.6, suspend/resume across all instances, and idle gating under concurrent decode/encode load.
