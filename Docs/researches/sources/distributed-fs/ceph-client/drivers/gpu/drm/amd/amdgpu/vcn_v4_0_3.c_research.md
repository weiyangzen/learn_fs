# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v4_0_3.c

## Purpose

This file implements AMDGPU support for VCN 4.0.3. It keeps the VCN 4 unified queue model but adapts it for multi-AID/multi-instance addressing, RRMT register normalization, PSP/DPM per-queue reset gating, JPEG-coupled reset recovery, and fuller RAS/ACA integration. It exports several ring emit helpers used outside this translation unit by the VCN 4.0.3 header.

## Important APIs, Types, And Functions

The main exported descriptor is `vcn_v4_0_3_ip_block`, with early, late, sw, hw, suspend/resume, idle, clock/power-gating, dump, and print hooks. `vcn_v4_0_3_early_init()` creates one unified ring per VCN instance, installs ring/IRQ/RAS functions, assigns power-gating callbacks, and calls common VCN early init. `vcn_v4_0_3_late_init()` computes reset support and only enables per-queue reset when DPM reset support, PSP SOS firmware version, and non-SR-IOV conditions allow it.

Hardware and power control are implemented by `vcn_v4_0_3_start()`, `vcn_v4_0_3_start_dpg_mode()`, `vcn_v4_0_3_stop()`, `vcn_v4_0_3_stop_dpg_mode()`, `vcn_v4_0_3_pause_dpg_mode()`, `vcn_v4_0_3_mc_resume()`, `vcn_v4_0_3_mc_resume_dpg_mode()`, and clock-gating helpers. SR-IOV boot is handled by `vcn_v4_0_3_start_sriov()`, which sends one MMSCH v4.0.3 table per instance. Ring integration uses `vcn_v4_0_3_unified_ring_get_rptr()`, `vcn_v4_0_3_unified_ring_get_wptr()`, `vcn_v4_0_3_unified_ring_set_wptr()`, exported emit helpers for reg wait/write/VM flush/HDP flush, and `vcn_v4_0_3_ring_reset()`.

RAS support includes UE status register tables, error count query/reset callbacks, poison status callbacks, ACA bank parser/filter ops, `vcn_v4_0_3_ras_late_init()`, `vcn_v4_0_3_enable_ras()`, and poison IRQ plumbing. Interrupt handling uses a single IRQ source whose IV `node_id` is mapped through `node_id_to_phys_map` and matched to per-instance `aid_id`.

## Control Flow

Software init registers a shared VCN IRQ and poison IRQ, then iterates all VCN instances to run common init/resume, compute physical VCN instance/AID, assign doorbells (`9 * vcn_inst` on PF, `32 * vcn_inst` on VF), choose the MMHUB for the instance AID, initialize the unified ring against the shared IRQ source, initialize firmware shared memory, and set DPG pause callbacks. Hardware init either starts SR-IOV through MMSCH and marks rings ready or, on PF, detects RRMT enablement, initializes each doorbell range/DB control, reinitializes firmware shared memory after fatal RAS if needed, and ring-tests every unified ring.

Normal start programs the physical `GET_INST(VCN, i)` register instance: status busy, clock gates, VCPU clock/reset, LMI/MPC, firmware memory windows, GFX8/GFX10 tiling, VCPU boot polling, master interrupt, ring base/size, RB enable, and queue mode flags. DPG start performs the same through DPG writes, optionally passes AID selection to PSP firmware with dummy register `0xDEADBEEF`, uploads SRAM with `AMDGPU_UCODE_ID_VCN0_RAM`, pauses DPG before ring programming, then enables RB and clears reset/hold-off. Stop waits for idle and LMI clean status, stalls UMC, resets LMI/VCPU, clears status, and clock-gates.

The reset path is generation-specific: `vcn_v4_0_3_ring_reset()` locks VCN reset and JPEG power-gating state because resetting VCN also resets JPEG. It stops JPEG schedulers, may ungate JPEG, begins ring reset bookkeeping, calls `amdgpu_dpm_reset_vcn()`, restores VCN DB/RRMT/DPG start, ends ring reset, restores JPEG power state, forces/validates JPEG fences and ring tests, restarts JPEG schedulers, and unlocks.

## State And Persistence

Persistent state includes `adev->vcn.inst[i].aid_id`, `num_inst_per_aid`, unified ring metadata, `vcn.caps` RRMT flag, firmware shared queue mode, `cur_state`, DPG pause state, and reset mask support. The exported emit helpers normalize register offsets when RRMT is not enabled, making `adev->vcn.caps` a runtime ABI switch for ring packets. SR-IOV state uses the VF MM table and per-instance MMSCH table headers. RAS state is stored in `adev->vcn.ras`, poison IRQ source fields, UE counters accumulated into `ras_err_data`, and ACA error cache records. JPEG reset coupling persists scheduler/fence recovery state across VCN resets.

## Dependencies And Integration Points

The file integrates with AMDGPU VCN common helpers, SOC15 register access and instance mapping (`GET_INST`), PSP SRAM update, DPM VCN reset, NBIO doorbells, ring/fence/scheduler helpers, JPEG decode rings and power-gating lock, RAS core, ACA bank decoding/cache helpers, MMSCH v4.0.3 definitions, and IH node-id topology. It reuses VCN 2.0 packet helpers for IB/fence/end operations but overrides register write/wait and VM flush behavior for normalized offsets.

## Risks

Instance addressing is a major risk: logical VCN instance, physical `GET_INST(VCN, i)`, AID ID, MMHUB, doorbell offsets, and IV node IDs must stay consistent. `vcn_v4_0_3_start_sriov()` mixes logical and physical indices in several firmware/shared-memory references, so future changes need careful review. The DPG path uses a dummy PSP register write for AID selection and assumes firmware interpretation. RRMT controls whether ring packet register offsets are normalized; incorrect detection can break VM flush/reg wait packets. VCN reset affects JPEG, so incomplete JPEG scheduler/fence restoration can hang unrelated decode work. The pre-reset JPEG helper appears to continue when `last_seq` is nonzero and poll when zero, which is a subtle path worth validating. RAS/ACA filters are tightly coupled to SMU bank instance IDs and error codes.

## Test Signals

Key signals are successful unified ring tests per AID, correct doorbell DB control reads, VCPU boot polling, DPG indirect SRAM update with AID selection, per-queue reset availability only with suitable PSP firmware, VCN reset followed by JPEG ring tests and scheduler restart, poison IRQ delivery, RAS UE count query/reset, ACA bank binding, and no HDP flush packets through VCN when RRMT is enabled. SR-IOV should be tested with multiple instances because MMSCH setup is per instance and uses VF doorbell spacing.
