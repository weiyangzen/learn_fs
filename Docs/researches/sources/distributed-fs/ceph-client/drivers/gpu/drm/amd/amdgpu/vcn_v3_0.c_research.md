# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v3_0.c

## Purpose

This file implements the AMDGPU IP block support for VCN 3.0 video firmware/hardware. It wires VCN instances into the AMDGPU IP lifecycle, creates decode and encode rings, programs firmware memory windows, handles dynamic/static power gating and clock gating, supports SR-IOV MMSCH boot setup, and routes VCN interrupts to fence processing. VCN 3.0 still exposes a separate decode ring plus up to two encode rings per instance, with special handling for harvested instances and `IP_VERSION(3, 0, 33)` where encode rings are disabled.

## Important APIs, Types, And Functions

The exported integration point is `vcn_v3_0_ip_block`, an `amdgpu_ip_block_version` whose `amd_ip_funcs` table includes early/software/hardware init and fini, suspend/resume, idle checks, clock gating, power gating, and state dump hooks. `vcn_v3_0_early_init()` configures instance counts and ring/IRQ function tables, then delegates common firmware setup to `amdgpu_vcn_early_init()`. `vcn_v3_0_sw_init()` allocates common VCN resources, resumes firmware BOs, initializes doorbells and rings, registers IRQ IDs, configures firmware shared flags, initializes fw logging, reset mask sysfs, and the register dump list. `vcn_v3_0_hw_init()` starts SR-IOV instances through MMSCH or tests physical rings directly.

The main hardware programming paths are `vcn_v3_0_start()`, `vcn_v3_0_start_dpg_mode()`, `vcn_v3_0_stop()`, `vcn_v3_0_stop_dpg_mode()`, `vcn_v3_0_pause_dpg_mode()`, and `vcn_v3_0_reset()`. Memory controller setup lives in `vcn_v3_0_mc_resume()` and `vcn_v3_0_mc_resume_dpg_mode()`. Ring callbacks include decode pointer accessors, encode pointer accessors, `vcn_v3_0_dec_ring_set_wptr()`, `vcn_v3_0_enc_ring_set_wptr()`, and the `amdgpu_ring_funcs` tables for decode, decode SW ring, and encode. `vcn_v3_0_ring_patch_cs_in_place()` parses user IBs for decode message buffers and calls `vcn_v3_0_dec_msg()` to force unsupported codecs onto VCN0 through `vcn_v3_0_limit_sched()`.

## Control Flow

Probe begins in `early_init`: SR-IOV virtual functions force two VCN instances with one encode ring each, while physical functions honor harvest masks and version-specific encode availability. Software init then iterates live instances, calls common VCN init/resume helpers, fills register offsets used by IB parsing, registers one decode interrupt and one interrupt per encode ring, creates the rings, and populates `amdgpu_fw_shared` queue flags (`AMDGPU_VCN_SW_RING_FLAG`, `AMDGPU_VCN_MULTI_QUEUE_FLAG`, RB flag, SMU interface metadata).

Hardware init diverges by virtualization. In SR-IOV, `vcn_v3_0_start_sriov()` builds an MMSCH v3 init table in the VF MM table, writes firmware/stack/context/cache windows and ring buffer descriptors, notifies MMSCH through mailbox registers, and waits for the expected response. For bare metal, each live instance opens the NBIO doorbell range and runs ring tests.

Normal start ungates DPM, optionally takes the DPG start path, disables static power gating and clock gating, enables the VCPU clock, programs LMI/MPC/tiling registers, maps firmware/stack/context/shared memory, releases VCPU reset, polls firmware readiness with retry reset pulses, enables interrupts, and initializes decode/encode ring base, size, RPTR, WPTR, and firmware queue reset bits. Stop waits for idle and LMI clean status, stalls UMC, blocks VCPU register access, resets/clocks down VCPU and LMI, clears status, gates clocks and power, and disables VCN DPM.

## State And Persistence

The file persists hardware/software state in `adev->vcn.inst[i]` fields: ring descriptors, `num_enc_rings`, `set_pg_state`, `pause_dpg_mode`, `reset`, `cur_state`, `pause_state`, register-offset metadata, firmware shared memory, and scheduler score. Doorbell indices are stable derived offsets, with a different compact layout for SR-IOV. Firmware shared memory is used as a persistent contract with VCN firmware: queue mode reset flags, decode RB `rptr/wptr`, SW ring enable state, SMU interface type, and fwlog state. DPG mode saves decode write pointers into `fw_shared->rb.wptr` and `mmUVD_SCRATCH2`, then restores encode/decode ring registers while pausing. Reset support is cached in `adev->vcn.supported_reset`.

## Dependencies And Integration Points

The driver depends on AMDGPU core IP block registration, `amdgpu_vcn_*` common helpers, `amdgpu_ring_init()` and ring scheduler infrastructure, `amdgpu_irq_add_id()`, NBIO doorbell range management, SOC15 register access macros, PSP firmware loading, MMSCH v3 command definitions, TTM BO validation/kmap for CS message inspection, DPM hooks, and DRM device enter/exit for teardown. It reuses v2.0 ring packet emit helpers for hardware rings and `vcn_sw_ring` helpers when the decode SW ring option is enabled. Interrupt processing integrates with IH client IDs `SOC15_IH_CLIENTID_VCN` and `SOC15_IH_CLIENTID_VCN1`, mapping source IDs to decode/general-purpose/low-latency encode fence processing.

## Risks

Register programming is highly order-dependent; missed readbacks, queue reset bits, or DPG stall transitions can create firmware races. SR-IOV MMSCH table construction uses manual dword sizing and mailbox polling, so table size/header errors can break VF startup. CS parsing maps user BOs to inspect codec create messages; bounds, alignment, and overflow checks are present, but any firmware message format drift can misclassify jobs. Scheduler limiting assumes VCN0 can handle codecs unsupported on other instances and returns `-EINVAL` if VCN0 is harvested. Power-gating state is not controlled by SR-IOV guests, so physical and virtual paths must remain separated. `IP_VERSION(3,0,33)` encode-disable branches must stay synchronized with ring counts and IRQ counts.

## Test Signals

Primary runtime signals are successful `amdgpu_ring_test_helper()` on decode and encode rings, successful firmware boot readiness polling through `mmUVD_STATUS`, MMSCH mailbox response in SR-IOV, clean suspend/resume cycling, fence completion after VCN interrupt source IDs, and sysfs reset mask availability. Negative tests should cover harvested VCN0/VCN1, encode-disabled 3.0.33 devices, AV1 decode/encode scheduling with nonzero `ring->me`, DPG pause/unpause around ring pointer restoration, and SR-IOV hypervisor-disabled rings.
