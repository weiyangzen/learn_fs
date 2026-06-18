# subset-b-001366 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v3_0.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v3_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v3_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v3_0.h

## Purpose

This header is the public declaration surface for the VCN 3.0 AMDGPU IP block implementation. It lets the AMDGPU device/IP discovery code reference the VCN 3.0 block without exposing internal register programming or ring callbacks.

## Important APIs, Types, And Functions

The only API is `extern const struct amdgpu_ip_block_version vcn_v3_0_ip_block;`. That object is defined in `vcn_v3_0.c` and contains the IP block type, version tuple `3.0.0`, and the `amd_ip_funcs` table for lifecycle operations. The header has no local structs, helper functions, inline functions, or macros beyond its include guard.

## Control Flow

The header participates at compile/link time. Platform code includes it, selects `vcn_v3_0_ip_block` for matching hardware, and the function table in the `.c` file drives runtime init, suspend/resume, reset, power gating, and interrupt behavior. No runtime control flow is implemented in the header itself.

## State And Persistence

No state is stored here. The declaration points consumers to the singleton IP block descriptor defined by the implementation file. Persistent VCN state lives in `struct amdgpu_device`, `struct amdgpu_vcn`, and `struct amdgpu_vcn_inst`, not in this header.

## Dependencies And Integration Points

The declaration assumes `struct amdgpu_ip_block_version` is visible to including translation units through AMDGPU headers included before or around this header. The main integration point is the AMDGPU IP block table used during ASIC initialization.

## Risks

The risk surface is intentionally small. Renaming or removing the exported symbol without updating ASIC registration code would produce link or probe failures. Since the header does not include the type definition itself, include order must continue to provide `struct amdgpu_ip_block_version`.

## Test Signals

Build coverage is the key signal: objects that include this header must compile and link against `vcn_v3_0_ip_block`. Runtime confirmation comes indirectly when VCN 3.0 devices bind to the correct IP block and execute the lifecycle functions in `vcn_v3_0.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v3_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v4_0.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v4_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v4_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v4_0.h

## Purpose

This header declares the VCN 4.0 IP block descriptor and the sub-block enumeration used by VCN 4.0 RAS poison status code. It is the small public interface for `vcn_v4_0.c`.

## Important APIs, Types, And Functions

`enum amdgpu_vcn_v4_0_sub_block` defines `AMDGPU_VCN_V4_0_VCPU_VCODEC` and `AMDGPU_VCN_V4_0_MAX_SUB_BLOCK`. The implementation uses these values when iterating sub-blocks in poison status queries. `extern const struct amdgpu_ip_block_version vcn_v4_0_ip_block;` exposes the VCN 4.0 lifecycle descriptor. No functions are defined in the header.

## Control Flow

The enum constrains loops in the implementation that call `vcn_v4_0_query_poison_by_instance()` for every VCN instance/sub-block pair. The IP block descriptor declaration is consumed by ASIC discovery/registration code, which selects this VCN generation and then calls the function table defined in `vcn_v4_0.c`.

## State And Persistence

The header stores no state. It defines compile-time constants for sub-block IDs and declares the singleton block descriptor. Persistent state is managed by `adev->vcn`, firmware shared memory, IRQ sources, and RAS structures in the implementation.

## Dependencies And Integration Points

The header depends on external visibility of `struct amdgpu_ip_block_version`. Its enum values are part of the local contract between the VCN 4.0 implementation and RAS poison status handling. The declaration integrates with the AMDGPU IP block table.

## Risks

Adding new RAS sub-blocks requires updating both this enum and the switch in `vcn_v4_0_query_poison_by_instance()`. If `MAX_SUB_BLOCK` becomes inconsistent, poison polling may skip registers or read unsupported sub-blocks. Symbol declaration drift for `vcn_v4_0_ip_block` would break build/link integration.

## Test Signals

Build/link coverage verifies the exported descriptor declaration. Runtime RAS testing should confirm that `AMDGPU_VCN_V4_0_MAX_SUB_BLOCK` bounds exactly the implemented poison-status sub-blocks and that VCN 4.0 hardware selects `vcn_v4_0_ip_block`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v4_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v4_0_3.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v4_0_3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v4_0_3.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v4_0_3.h

## Purpose

This header declares the VCN 4.0.3 IP block, its RAS sub-block IDs, and generation-specific ring emit helper APIs. Unlike the earlier headers in this work item, it exposes helper functions because other AMDGPU code needs VCN 4.0.3-specific register wait/write, VM flush, and HDP flush behavior.

## Important APIs, Types, And Functions

`enum amdgpu_vcn_v4_0_3_sub_block` defines `AMDGPU_VCN_V4_0_3_VCPU_VCODEC` and `AMDGPU_VCN_V4_0_3_MAX_SUB_BLOCK` for RAS poison scanning. `extern const struct amdgpu_ip_block_version vcn_v4_0_3_ip_block;` exposes the IP descriptor. The declared helpers are `vcn_v4_0_3_enc_ring_emit_reg_wait()`, `vcn_v4_0_3_enc_ring_emit_wreg()`, `vcn_v4_0_3_enc_ring_emit_vm_flush()`, and `vcn_v4_0_3_ring_emit_hdp_flush()`.

## Control Flow

AMDGPU ASIC registration selects `vcn_v4_0_3_ip_block`, whose function table is implemented in `vcn_v4_0_3.c`. Ring code can call the declared emit helpers through the VCN 4.0.3 `amdgpu_ring_funcs` table. VM flush emits a GMC TLB flush and waits on the page table base register; register wait/write helpers normalize register offsets when RRMT is not enabled; HDP flush intentionally emits no VCN packet as a workaround for RRMT behavior.

## State And Persistence

The header itself stores no mutable state. Its helper declarations operate on `struct amdgpu_ring`, whose `adev`, `vm_hub`, `me`, write pointer, and runtime VCN capabilities determine emitted packet contents. RAS enum values are compile-time constants used by poison query loops.

## Dependencies And Integration Points

The header depends on AMDGPU type declarations for `struct amdgpu_ip_block_version` and `struct amdgpu_ring`, plus integer typedefs such as `uint32_t` and `uint64_t` from kernel headers. It is integrated by the VCN 4.0.3 implementation and any code that needs these generation-specific ring operations.

## Risks

Because helpers are externally visible, their ABI must remain consistent with ring function expectations. VM flush callers depend on the wait register/mask semantics implemented in the `.c` file. HDP flush is a no-op by design; callers must tolerate that VCN 4.0.3 does not perform HDP flush through the VCN ring. Adding sub-block enum values requires matching implementation updates.

## Test Signals

Build/link tests should verify all declared helpers are defined exactly once and consumed by the VCN 4.0.3 ring function table. Runtime signals include successful VM flush waits with normalized register offsets, absence of VCN HDP flush packet failures under RRMT, and RAS poison scans bounded by `AMDGPU_VCN_V4_0_3_MAX_SUB_BLOCK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v4_0_3.h -->
