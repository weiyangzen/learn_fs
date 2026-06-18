# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v4_0.c

## Purpose

This file implements AMDGPU support for VCN 4.0 hardware. Compared with VCN 3.0, it uses a unified queue model by reusing `ring_enc[0]` as the single decode/encode ring per instance, adds VCN 4 firmware shared-memory fields, supports SR-IOV MMSCH v4 boot, and wires VCN RAS poison interrupt/status support for supported ASIC versions.

## Important APIs, Types, And Functions

The exported symbol is `vcn_v4_0_ip_block`, whose `amd_ip_funcs` table drives early/sw/hw init and fini, suspend/resume, idle checks, clock gating, power gating, dump, and print. `vcn_v4_0_early_init()` forces `num_enc_rings = 1`, applies SR-IOV harvest information from hypervisor-disabled VCN rings, installs unified ring functions, IRQ functions, and RAS functions, then calls common VCN early init. `vcn_v4_0_fw_shared_init()` initializes `struct amdgpu_vcn4_fw_shared`, setting unified queue flags, queue enable, SMU DPM interface type, and a 4.0.2 DRM key workaround.

Runtime programming is split across `vcn_v4_0_start()`, `vcn_v4_0_start_dpg_mode()`, `vcn_v4_0_stop()`, `vcn_v4_0_stop_dpg_mode()`, `vcn_v4_0_pause_dpg_mode()`, `vcn_v4_0_mc_resume()`, and `vcn_v4_0_mc_resume_dpg_mode()`. The ring ABI is implemented by `vcn_v4_0_unified_ring_get_rptr()`, `vcn_v4_0_unified_ring_get_wptr()`, `vcn_v4_0_unified_ring_set_wptr()`, `vcn_v4_0_ring_patch_cs_in_place()`, `vcn_v4_0_ring_reset()`, and `vcn_v4_0_unified_ring_vm_funcs`. RAS integration includes `vcn_v4_0_enable_ras()`, poison IRQ functions, `vcn_v4_0_query_poison_by_instance()`, `vcn_v4_0_query_ras_poison_status()`, and `vcn_v4_0_ras_hw_ops`.

## Control Flow

During software init, each live instance runs common VCN software setup, firmware setup/resume, scheduler-score initialization, IRQ registration for unified queue and poison interrupts, doorbell assignment, ring initialization, firmware shared initialization, and DPG pause hook assignment. Hardware init either sends an MMSCH v4 init table in SR-IOV or configures NBIO doorbell ranges and runs ring tests on physical devices.

The normal start path ungates DPM, initializes firmware shared state, optionally dispatches to DPG start, disables power/clock gating, enables and boots the VCPU, programs LMI/MPC/tiling registers, configures firmware/stack/context/shared memory windows, waits for VCPU readiness, enables interrupts, programs RB1 doorbell control, ring base/size, RB enable, RPTR/WPTR, and queue reset bits. The DPG start path performs equivalent setup through `WREG32_SOC15_DPG_MODE()`, optionally uploads indirect SRAM through PSP, enables RAS before master interrupts, then initializes the unified ring. Stop holds off firmware queue processing, waits for ring and LMI clean conditions, stalls UMC, resets/clocks down VCPU/LMI, clears status, gates clocks/power, and toggles DPM.

Command submission patching parses the unified IB. `vcn_v4_0_ring_patch_cs_in_place()` scans parameter blocks for `RADEON_VCN_ENGINE_INFO`; decode submissions route to `vcn_v4_0_dec_msg()` for message-buffer validation, while encode submissions search for AV1 session init. Unsupported-on-secondary codecs force scheduling onto VCN0 through `vcn_v4_0_limit_sched()`.

## State And Persistence

The file stores per-instance state in `adev->vcn.inst[i]`: unified ring fields, doorbell index, IRQ sources, `set_pg_state`, `pause_dpg_mode`, firmware shared memory, and scheduler scores. `struct amdgpu_vcn4_fw_shared` is a persistent firmware contract for unified queue enable, queue modes, SMU DPM interface, DRM key workaround metadata, VF ring buffer setup, and decoupled ring metadata. SR-IOV allocates and frees a VF MM table. RAS state is attached via `adev->vcn.ras`, poison IRQ source fields, and hardware status registers. Power state persists through `cur_state` and `FW_QUEUE_DPG_HOLD_OFF`/`FW_QUEUE_RING_RESET` bits.

## Dependencies And Integration Points

The implementation depends on AMDGPU VCN common helpers, ring/fence/scheduler infrastructure, SOC15 register access, MMSCH v4 definitions, TTM BO validation for message parsing, NBIO doorbell programming, PSP firmware loading, DPM, RAS helpers, and IH source IDs from VCN 4.0. It reuses VCN 2.0 encode ring packet emit helpers for unified ring submissions. SR-IOV decoupled ring buffer support integrates with `amdgpu_sriov_is_vcn_rb_decouple()` and writes metadata after the ring allocation.

## Risks

The unified ring means decode and encode scheduling rules share one ring type (`AMDGPU_RING_TYPE_VCN_ENC`), so scheduler selection, reset, and tests must account for decode workloads on an encode-class ring. The CS parser walks variable-length IB records and mapped user message buffers; bounds checks are present, but malformed or changed firmware message layouts can lead to rejected submissions or wrong scheduling. MMSCH table construction and mailbox status checks are sensitive to dword sizes and harvest/disabled-instance selection. RAS enable writes use instance zero offsets in DPG mode, which must match hardware addressing expectations. The global mutable `vcn_v4_0_unified_ring_vm_funcs.secure_submission_supported` is toggled based on IP version and is shared across instances.

## Test Signals

Signals include successful ring initialization and `amdgpu_vcn_unified_ring_test_ib`, correct doorbell operation, VCPU boot status polling, suspend/resume with queue hold-off, MMSCH mailbox pass or incomplete status in SR-IOV, poison IRQ delivery to `amdgpu_vcn_process_poison_irq`, and `query_poison_status` reporting on VCN 4.0.0. Submission tests should cover decode message parsing, AV1 encode routing, harvested VCN0 rejection, SR-IOV decoupled ring setup, DPG indirect SRAM upload, and reset recovery through `vcn_v4_0_ring_reset()`.
