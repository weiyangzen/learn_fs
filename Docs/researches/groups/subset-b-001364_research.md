# Research: subset-b-001364

Grouped research for AMDGPU UVD/VCE generation-specific IP blocks under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v3_1.c -->
## Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v3_1.c

Purpose: Implements the UVD 3.1 AMDGPU IP block for a single legacy decode engine. It wires the UVD lifecycle into `amd_ip_funcs`, programs the firmware/heap/stack memory controller windows, boots and stops the UVD VCPU, exposes one decode ring, and processes UVD trap interrupts as fence completions.

Important APIs and functions: `uvd_v3_1_ip_block` exports the block version. `uvd_v3_1_early_init`, `sw_init`, `hw_init`, `suspend`, `resume`, `soft_reset`, and `hw_fini` are the driver lifecycle hooks. Ring callbacks include `uvd_v3_1_ring_get_rptr`, `get_wptr`, `set_wptr`, `emit_ib`, `emit_fence`, `test_ring`, and `insert_nop`. Firmware and boot helpers include `uvd_v3_1_mc_resume`, `uvd_v3_1_fw_validate`, `uvd_v3_1_start`, `uvd_v3_1_stop`, `uvd_v3_1_set_dcm`, and `uvd_v3_1_enable_mgcg`.

Control flow: early init declares one UVD instance and installs ring/IRQ function tables. SW init registers legacy IRQ source 124, runs shared `amdgpu_uvd_sw_init`, initializes the `uvd` ring, resumes firmware BO state, and extracts `adev->uvd.keyselect` from the loaded firmware image. HW init programs MC windows, enables memory clock gating, ensures clocks are on for firmware validation, validates firmware via `mmUVD_FW_START`/`mmUVD_FW_STATUS`, starts the VCPU, tests the ring, and writes semaphore timeout defaults. Suspend cancels idle work, disables UVD DPM or clocks/gates, then stops hardware and suspends shared UVD state. Resume restores shared UVD memory and runs HW init again.

State and persistence: Persistent state lives in `adev->uvd`: firmware BO GPU/CPU addresses, `max_handles`, `keyselect`, delayed idle work, IRQ state, and the single ring. Hardware state is mostly register-resident: RBC read/write pointers, ring base, VCPU cache windows, keyselect validation status, CGC gates, and semaphore settings. `uvd_v3_1_mc_resume` deliberately skips memory programming if `mmUVD_FW_START` is already set, avoiding a second keyselect perturbation.

Dependencies and integration points: Depends on shared AMDGPU UVD helpers (`amdgpu_uvd_sw_init`, `resume`, `suspend`, `prepare_suspend`, parse/test helpers), ring/fence helpers, DPM/ASIC clock hooks, register definitions from `sid.h`, `uvd_3_1`, and `oss_1_0`, and firmware layout constants from `amdgpu_uvd.h`. Interrupt processing calls `amdgpu_fence_process` on the decode ring.

Risks: Firmware validation is timing-sensitive and returns `-ETIMEDOUT` or `-EINVAL` if status bits do not progress. Ring fences are explicitly not 64-bit user fences, and only the low 40 bits of fence address are emitted. Register polling loops use fixed retry counts and can leave a partially initialized block if VCPU start repeatedly fails. The suspend TODO notes DPM/clock/power gating ownership is not cleanly isolated. `set_interrupt_state`, clockgating, and powergating hooks are stubs, so behavior relies on surrounding DPM/idle flows.

Test signals: `amdgpu_ring_test_helper`, the local context-register ring test, shared `amdgpu_uvd_ring_test_ib`, firmware validation pass bits, successful semaphore programming, and `"UVD initialized successfully."` are the main positive signals. Negative signals include `"UVD Firmware validate fail"`, `"UVD not responding"`, ring allocation/test failures, and timeout returns from idle/reset polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v3_1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v3_1.h -->
## Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v3_1.h

Purpose: Declares the UVD 3.1 IP block version exported by `uvd_v3_1.c`.

Important APIs and types: The only functional declaration is `extern const struct amdgpu_ip_block_version uvd_v3_1_ip_block;`, protected by `__UVD_V3_1_H__`.

Control flow and integration: Other AMDGPU IP discovery or ASIC tables include this header to reference the UVD 3.1 block without depending on implementation internals.

State and persistence: The header owns no state. The declared object is immutable block metadata in the C file.

Dependencies and risks: It assumes `struct amdgpu_ip_block_version` is visible to includers through the broader AMDGPU include chain. Any symbol rename or major/minor mismatch must be fixed in both the C file and ASIC block table users.

Test signals: Build coverage is the main signal: missing or mismatched declarations surface as compile/link errors when the UVD 3.1 block is selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v3_1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v4_2.c -->
## Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v4_2.c

Purpose: Implements the UVD 4.2 decode IP block for CIK-era hardware. It provides a single UVD ring, start/stop/reset sequencing, DCM/MGCG programming, SMC-backed power-gating transitions, and trap-to-fence interrupt handling.

Important APIs and functions: `uvd_v4_2_ip_block` exports the block. Lifecycle hooks are `uvd_v4_2_early_init`, `sw_init`, `hw_init`, `hw_fini`, `prepare_suspend`, `suspend`, `resume`, `is_idle`, `wait_for_idle`, `soft_reset`, and gating hooks. Ring callbacks mirror UVD 3.1: read/write pointers, IB emission, fence emission, NOP insertion, and ring tests. `uvd_v4_2_set_powergating_state` is a notable generation-specific hook that programs `mmUVD_PGFSM_CONFIG` when DPM is not active.

Control flow: early init refuses to enable the block when global `amdgpu_dpm` is disabled because this generation needs DPM to ungate UVD. SW init registers legacy IRQ 124, initializes shared UVD state, creates the `uvd` ring, and resumes UVD memory. HW init enables MGCG, sets UVD clocks, tests the ring, and configures semaphore timeouts. Power-on from `set_powergating_state(UNGATE)` powers through SMC PG status checks and then runs `uvd_v4_2_start`; gate stops UVD and can request PG FSM power down. Start programs LMI, cache, MPC mux, VCPU reset release, interrupt enable, and RBC ring registers.

State and persistence: Uses `adev->uvd.inst->ring`, `adev->uvd.inst->irq`, `adev->uvd.max_handles`, firmware/heap/stack offsets, `adev->gfx.config.gb_addr_config`, DPM/PG flags, and SMC current PG status. Hardware state persists in UVD cache windows, LMI extension registers, RBC pointers/base/size, CGC memory control, and PG FSM registers.

Dependencies and integration points: Includes `cikd`, UVD 4.2, OSS 2.0, BIF 4.1, and SMU 7.0.1 register definitions. Uses shared UVD helpers for firmware BO management, parser/test helpers, idle work, and DPM clock hooks. IRQ registration uses `AMDGPU_IRQ_CLIENTID_LEGACY` source 124.

Risks: Early init failure when DPM is disabled is intentional but can surprise board bring-up. Power-gating comments state the hook only reinitializes the block while actual gating belongs to SMC/DPM. Interrupt set is a TODO stub. Fixed VCPU polling can fail under slow firmware start. Ring and fence formats remain 32-bit-address constrained for command payloads.

Test signals: Ring test helper, local context-register ring test, shared UVD IB test, semaphore programming, and the init success log validate the path. Timeout/error logs around VCPU reset attempts, ring allocation failures, and `-ENOENT` from early init are useful failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v4_2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v4_2.h -->
## Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v4_2.h

Purpose: Declares the UVD 4.2 AMDGPU IP block descriptor.

Important APIs and types: Exports `extern const struct amdgpu_ip_block_version uvd_v4_2_ip_block;` behind `__UVD_V4_2_H__`.

Control flow and integration: ASIC initialization code can include this header to add the CIK UVD 4.2 block to an IP block list.

State and persistence: No runtime state is stored here; all state is in the implementation and `adev->uvd`.

Dependencies and risks: Requires callers to have the AMDGPU IP block type available. Declaration drift would create compile or link failures.

Test signals: Successful compilation and linkage of ASIC tables referencing `uvd_v4_2_ip_block`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v4_2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v5_0.c -->
## Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v5_0.c

Purpose: Implements UVD 5.0 decode support for VI-era hardware. Compared with UVD 4.2, it uses 64-bit BAR registers for VCPU and ring buffers, has broader clock-gating programming, exposes clock-gating state, and keeps one decode ring.

Important APIs and functions: `uvd_v5_0_ip_block` is the exported descriptor. Lifecycle hooks include `uvd_v5_0_early_init`, `sw_init`, `hw_init`, suspend/resume/fini, `soft_reset`, gating setters, and `get_clockgating_state`. Ring callbacks are `uvd_v5_0_ring_*` helpers. Core hardware helpers are `uvd_v5_0_mc_resume`, `start`, `stop`, `enable_clock_gating`, `set_sw_clock_gating`, and `enable_mgcg`.

Control flow: SW init registers the VISLANDS30 UVD system-message interrupt, initializes shared UVD state, creates the `uvd` ring, and resumes firmware state. HW init sets UVD clocks, ungates clocking, enables MGCG, tests the ring, and writes semaphore timeouts. Start disables dynamic power gating, programs VCPU cache BAR low/high registers and cache offsets, resets UVD subblocks, boots VCPU, enables interrupts, programs RBC ring base/size/read-write pointers, then clears `RB_NO_FETCH`. Stop idles RBC, stalls LMI, resets VCPU, disables VCPU clock, unstalls LMI, and clears status.

State and persistence: Persistent driver state is held in `adev->uvd.inst->ring`, IRQ, firmware BO address, `max_handles`, PM mutex, DPM/PG/CG flags, and GFX tiling address config. Hardware state includes `mmUVD_LMI_VCPU_CACHE_64BIT_BAR_*`, `mmUVD_LMI_RBC_RB_64BIT_BAR_*`, RBC control, UVD power status, semaphore registers, and CGC gate/control registers.

Dependencies and integration points: Uses `vid`, UVD 5.0, OSS/BIF 5.0, VI, SMU 7.1.2, and VISLANDS interrupt definitions. Integrates with shared UVD parser/test/begin/end helpers, DPM clock control, ring/fence core, and SMC PG status for clock-gating queries.

Risks: Interrupt set remains a TODO stub. `get_clockgating_state` refuses to inspect when UVD is powergated and depends on SMC status accuracy. Fixed polling and reset delays remain sensitive to firmware/hardware timing. `set_powergating_state` states it does not own actual SMC power gating. The `#if 0` hardware clock-gating path documents dormant code that may diverge from real hardware expectations.

Test signals: Ring helper test, local register write test, shared UVD IB test, semaphore timeout writes, clock-gating state readback, and init success logs. Failure signals include ring alloc/test errors, VCPU timeout logs, `-EBUSY` when gating while non-idle, and powergated-state messages from clock-gating queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v5_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v5_0.h -->
## Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v5_0.h

Purpose: Declares the UVD 5.0 IP block descriptor.

Important APIs and types: Provides `extern const struct amdgpu_ip_block_version uvd_v5_0_ip_block;` behind `__UVD_V5_0_H__`.

Control flow and integration: Used by ASIC-specific block tables to select the UVD 5.0 implementation.

State and persistence: None in the header; the declared block metadata is defined in `uvd_v5_0.c`.

Dependencies and risks: Depends on the including translation unit knowing `struct amdgpu_ip_block_version`. Header/API drift would surface at build or link time.

Test signals: Compile and link coverage for ASIC tables referencing the symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v5_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v6_0.c -->
## Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v6_0.c

Purpose: Implements UVD 6.x decode plus optional UVD ENC support. It supports one decode ring, up to two HEVC encoder rings on supported Polaris/Vegam firmware, physical or VM decode ring modes, encoder VM commands, multi-stage reset callbacks, and generation-specific clock/power gating.

Important APIs and functions: Exports `uvd_v6_0_ip_block`, `uvd_v6_2_ip_block`, and `uvd_v6_3_ip_block`, all sharing `uvd_v6_0_ip_funcs`. `uvd_v6_0_enc_support` gates encoder availability by ASIC and firmware version. Encode helpers include `uvd_v6_0_enc_ring_test_ring`, create/destroy message builders, `enc_ring_test_ib`, encoder fence/IB/VM flush/pipeline/end helpers. Decode helpers include VM/physical ring function tables, `ring_emit_vm_flush`, `emit_pipeline_sync`, `emit_wreg`, and the usual start/stop/lifecycle hooks.

Control flow: early init checks UVD harvest fuses for dGPU, installs decode ring functions, enables two encoder rings only when `uvd_v6_0_enc_support` passes, and sizes IRQ types accordingly. SW init registers decode and optional encode trap sources, initializes shared UVD, disables encoder rings if firmware support later fails, initializes rings, and resumes firmware memory. HW init sets clocks, ungates, enables MGCG, tests decode and optional encoder rings, then writes decode semaphore timeouts. Start disables DPG, programs MC windows and max handles scratch, boots VCPU, programs decode RBC, then initializes both encoder ring buffers if enabled. Reset is split into check/pre/soft/post phases storing `adev->uvd.inst->srbm_soft_reset`.

State and persistence: Persistent state includes `adev->uvd.num_uvd_inst`, `num_enc_rings`, firmware version, `ib_bo`, per-ring function pointers, IRQ type counts, `srbm_soft_reset`, PM/CG/PG flags, and VMIDs derived from jobs. Hardware state includes decode RBC registers, encoder ring registers `mmUVD_RB_*`, VCPU cache BARs, GP scratch max handles, CGC gates, SMC PG status, and SRBM reset bits.

Dependencies and integration points: Depends on shared UVD helpers, amdgpu job/IB/fence submission, VM/GMC TLB flush helpers, VI flush constants, HEVC encoder command definitions from UVD headers, VISLANDS interrupt IDs, SMU PG status, and ring core callbacks. Interrupt processing demultiplexes source 124 to decode and 119/120 to encoder rings.

Risks: Encoder support depends on both ASIC range and firmware version `FW_1_130_16`; unsupported cases must null encoder ring funcs and shrink IRQ types. VM ring frame sizes must stay consistent with emitted TLB flush and fence command counts. `set_interrupt_state` is still a TODO. Reset state is stored in `adev->uvd.inst->srbm_soft_reset`; stale or missed checks can skip needed restart. Clock-gating waits can return `-EBUSY` if status never clears.

Test signals: Decode ring helper test, local decode register write test, shared UVD IB test, encoder ring END test, encoder create/destroy IB test with fence wait, successful init log distinguishing UVD-only from UVD+ENC, and reset logs showing SRBM bits. Failure signals include unsupported encoder logs, unhandled interrupt errors, ring test timeouts, and busy clock-gating returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v6_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v6_0.h -->
## Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v6_0.h

Purpose: Declares UVD 6.x IP block descriptors backed by the shared UVD 6.0 implementation.

Important APIs and types: Exports `uvd_v6_0_ip_block`, `uvd_v6_2_ip_block`, and `uvd_v6_3_ip_block`.

Control flow and integration: ASIC tables can select the correct major/minor descriptor while reusing the same C implementation and function table.

State and persistence: No direct state; descriptor definitions live in `uvd_v6_0.c`.

Dependencies and risks: Inclusion assumes the AMDGPU IP block type is declared. Adding a new 6.x descriptor requires matching declaration and definition.

Test signals: Compile/link tests for all three exported descriptor symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v6_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v7_0.c -->
## Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v7_0.c

Purpose: Implements SOC15 UVD 7.0 decode and encode support, including multiple UVD hardware instances on Vega20, per-instance harvest handling, PSP firmware loading integration, SR-IOV VF startup through MMSCH tables, doorbell encoder write pointers, and VM-mode ring operations.

Important APIs and functions: `uvd_v7_0_ip_block` exports the block. Lifecycle hooks include `early_init`, `sw_init`, `hw_init`, suspend/resume/fini, and a no-op clockgating setter used for unload. `uvd_v7_0_sriov_start` and `uvd_v7_0_mmsch_start` are the major SR-IOV path. Ring helpers include per-instance decode/encoder pointer access, encoder create/destroy tests, SOC15 decode IB/fence/wreg/reg_wait/vm_flush helpers, encoder IB/fence/reg_wait/vm_flush/wreg helpers, and `uvd_v7_0_ring_patch_cs_in_place` for second-instance register offsets.

Control flow: early init detects Vega20 dual instances and harvest masks, sets one or two encoder rings depending on SR-IOV VF status, and installs ring/IRQ functions per live instance. SW init registers per-instance decode and encode interrupts, initializes shared UVD state, registers firmware with PSP when needed, initializes decode rings only for non-VF, initializes encoder rings for all live instances, configures VF doorbells, resumes UVD memory, and allocates the virtualization MM table. HW init chooses direct start or SR-IOV MMSCH start, then tests decode rings for PF and encoder rings for all live instances. Direct start programs MC windows, VCPU boot, decode RBC, and encoder rings for each unharvested instance. VF start builds an MMSCH command table and kicks the multimedia scheduler mailbox.

State and persistence: Persistent state includes `adev->uvd.num_uvd_inst`, `harvest_config`, `num_enc_rings`, per-instance ring/IRQ structs, PSP `adev->firmware.ucode[]` entries and accumulated firmware size, virtualization MM table, doorbell indices, ring `me`, `vm_hub`, `use_doorbell`, and write pointer CPU mappings. Hardware state is per SOC15 instance via `RREG32_SOC15/WREG32_SOC15`, plus VCE MMSCH mailbox registers for VF setup.

Dependencies and integration points: Depends on SOC15 register access, UVD 7.0 and VCE 4.0 offsets, MMHUB VM hub data, MMSCH v1.0 command structures/macros, PSP firmware loading, amdgpu virtual MM table allocation, shared UVD firmware/ring helpers, and interrupt client IDs `SOC15_IH_CLIENTID_UVD/UVD1`. Encode rings share HEVC command protocol with UVD 6.0.

Risks: Multi-instance register patching must correctly rewrite IB register offsets for instance 1. SR-IOV avoids direct register touch in stop/fini and relies on MMSCH command table correctness; bad table offsets or mailbox timeout return `-EBUSY`. Doorbell write pointers only apply for VF encoder rings. PSP and non-PSP MC resume paths differ in firmware cache base/offset handling. `set_powergating_state` is NULL and clockgating setter is a no-op, so power management is delegated elsewhere.

Test signals: PF decode ring tests, encoder END/create/destroy tests, semaphore programming, successful MMSCH mailbox response bits, init success log, and unhandled client/source interrupt errors. VF-specific tests should verify doorbell writes and MMSCH table size/offset fields; PF tests should cover Vega20 harvested and dual-instance configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v7_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v7_0.h -->
## Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v7_0.h

Purpose: Declares the SOC15 UVD 7.0 IP block descriptor.

Important APIs and types: Exports `extern const struct amdgpu_ip_block_version uvd_v7_0_ip_block;` behind `__UVD_V7_0_H__`.

Control flow and integration: ASIC block tables include this header to attach UVD 7.0 lifecycle and ring functions implemented in the C file.

State and persistence: No state; all runtime data is in `adev->uvd` and firmware/virtualization structures.

Dependencies and risks: Requires consistent symbol definition in `uvd_v7_0.c`; any future minor descriptor would need a new declaration if exported.

Test signals: Build/link coverage for the exported symbol in SOC15 ASIC configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v7_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vce_v1_0.c -->
## Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vce_v1_0.c

Purpose: Implements first-generation AMDGPU VCE encode support. It initializes two VCE rings, loads and validates a firmware signature for supported SI ASICs, ensures the VCPU BO is mapped below 4 GiB, starts/stops the VCE ECPU, manages MGCG, and routes trap interrupts to ring fences.

Important APIs and functions: `vce_v1_0_ip_block` exports the IP descriptor. Major helpers include `vce_v1_0_load_fw_signature`, `wait_for_fw_validation`, `ensure_vcpu_bo_32bit_addr`, `mc_resume`, `start`, `stop`, `firmware_loaded`, `lmi_clean`, and `enable_mgcg`. Lifecycle hooks are `early_init`, `sw_init`, `hw_init`, `hw_fini`, `suspend`, `resume`, idle/wait, clock/power gating. Ring functions are mostly generic VCE helpers with generation-specific read/write pointer callbacks.

Control flow: early init runs shared VCE early setup, sets two rings, and installs funcs/IRQs. SW init registers legacy IRQ 167, allocates shared VCE firmware/stack/data memory, resumes the firmware BO, copies the firmware signature into the VCPU BO, reserves low GART entries for a 32-bit VCPU mapping, and initializes both rings with VCE priorities. HW init enables VCE DPM/clocks and tests both rings; ring begin-use powers and starts the block as needed through shared VCE helpers. Start programs MC windows, validates firmware keyselect, programs both ring buffers, enables VCPU clock, resets/releases ECPU/FME, waits for firmware loaded, and clears status.

State and persistence: Persistent state includes `adev->vce.fw`, `cpu_addr`, `gpu_addr`, `vcpu_bo`, `gart_node`, `keyselect`, `ring[]`, IRQ, idle work, and DPM/CG flags. Firmware signature state is copied into the VCPU BO and keyselect stored in `adev->vce.keyselect`. Hardware state includes VCE cache offsets/sizes, LMI controls, ring bases/pointers, clock-gating registers, VCPU control, soft reset, firmware status, and system interrupt enable/status.

Dependencies and integration points: Depends on shared VCE helpers (`amdgpu_vce_sw_init`, `resume`, `suspend`, parse/test/emit helpers, ring begin/end), GART/GTT manager, firmware headers, SI/VCE/OSS register definitions, DPM clock hooks, and fence processing. Interrupt data `src_data[0]` selects ring 0 or 1.

Risks: Only TAHITI/VERDE/PITCAIRN chip IDs are accepted for signature selection. Firmware validation appears one-shot; `mc_resume` avoids revalidating when keyselect is already set. Low-32-bit GART placement can fail and must be freed on SW fini. Stop warns rather than hard-failing on some idle failures, which can mask hardware still busy. Ring pointer register selection depends on `ring->me` values set during init.

Test signals: Firmware signature selection and validation pass, low-GART mapping success, ring test helper for both rings, VCE firmware loaded status bit, IRQ enable/trap fence processing, and `"VCE initialized successfully."` logs. Failure signals include chip ID not found, validation timeout/fail/busy timeout, low address allocation errors, firmware loaded timeout, and unhandled interrupt source data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vce_v1_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vce_v1_0.h -->
## Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vce_v1_0.h

Purpose: Declares the VCE 1.0 IP block descriptor.

Important APIs and types: Exports `extern const struct amdgpu_ip_block_version vce_v1_0_ip_block;` behind `__VCE_V1_0_H__`.

Control flow and integration: ASIC tables include this header when selecting the VCE 1.0 implementation.

State and persistence: No state is defined in the header.

Dependencies and risks: Header users must have AMDGPU IP block type definitions available. Symbol drift creates build or link failures.

Test signals: Successful compilation/linkage for SI VCE 1.0 configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vce_v1_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vce_v2_0.c -->
## Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vce_v2_0.c

Purpose: Implements VCE 2.0 encode support for CIK-era hardware. It manages two physical VCE rings, firmware memory layout, ECPU boot/stop, dynamic or software clock gating, SMC-style power-gating reinitialization, soft reset, and trap interrupt fence processing.

Important APIs and functions: `vce_v2_0_ip_block` is the descriptor. Hardware helpers include `vce_v2_0_mc_resume`, `start`, `stop`, `firmware_loaded`, `lmi_clean`, `disable_cg`, `init_cg`, `set_sw_cg`, `set_dyn_cg`, and `enable_mgcg`. Lifecycle hooks cover early/sw/hw init/fini, suspend/resume, idle/wait, soft reset, clock/power gating. Ring callbacks use generic VCE emit/parse/test helpers with generation-specific pointer accessors.

Control flow: early init runs shared VCE setup, sets two rings, and installs ring/IRQ functions. SW init registers legacy IRQ 167, allocates VCE memory sized for firmware/stack/data, resumes the firmware BO, and initializes both rings. HW init sets clocks, enables dynamic MGCG, and ring-tests both rings. Start marks VCE busy, initializes and disables CG for boot, programs MC windows and both ring buffers, enables ECPU clock, releases reset, waits for firmware loaded, and clears busy. Power gate stops the block; ungate starts it.

State and persistence: Uses `adev->vce.gpu_addr`, `ring[0..1]`, IRQ, idle work, firmware version/state from shared helpers, DPM/CG flags, and PM structures. Hardware state includes 40-bit VCPU cache BAR, cache offsets/sizes, VCE LMI controls, ring base/pointers, CGTT override, clock gating registers, VCPU control, soft reset, and VCE status.

Dependencies and integration points: Depends on `amdgpu_vce` shared code, CIK/VCE 2.0/SMU/OSS register definitions, DPM/ASIC clock hooks, ring/fence core, and legacy interrupt source 167. It processes `entry->src_data[0]` as the ring index.

Risks: `hw_fini` only cancels idle work and does not call `vce_v2_0_stop`; stop is reached through suspend/power-gating paths. Some stop failures log and return 0 when LMI is not idle or VCE busy, which may leave hardware running. Soft reset asserts SRBM VCE reset and immediately calls start, so correctness depends on prior state. Clock-gating mode selection differs between HW init and set_clockgating_state.

Test signals: Ring tests for both rings, firmware loaded status bit, successful trap IRQ processing, clock-gating transitions, and init success log. Failure signals include firmware loaded timeouts, VCE busy/not-idle logs, unhandled interrupt ring indices, and soft reset/start errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vce_v2_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vce_v2_0.h -->
## Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vce_v2_0.h

Purpose: Declares the VCE 2.0 AMDGPU IP block descriptor.

Important APIs and types: Exports `extern const struct amdgpu_ip_block_version vce_v2_0_ip_block;` behind `__VCE_V2_0_H__`.

Control flow and integration: Included by ASIC block selection code for CIK VCE 2.0.

State and persistence: None in the header.

Dependencies and risks: Requires matching symbol definition in `vce_v2_0.c` and visible AMDGPU IP block type declarations.

Test signals: Compile/link coverage in configurations that include VCE 2.0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vce_v2_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vce_v3_0.c -->
## Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vce_v3_0.c

Purpose: Implements VCE 3.x encode support for VI-era hardware. It handles harvested VCE instances, up to three rings when firmware supports it, physical or VM ring modes, per-instance register selection via `GRBM_GFX_INDEX`, firmware boot, clock-gating state reporting, and multi-stage soft reset.

Important APIs and functions: Exports `vce_v3_0_ip_block`, `vce_v3_1_ip_block`, and `vce_v3_4_ip_block`. Key helpers include `vce_v3_0_get_harvest_config`, `start`, `stop`, `mc_resume`, `firmware_loaded`, `check_soft_reset`, `pre_soft_reset`, `soft_reset`, `post_soft_reset`, `set_vce_sw_clock_gating`, VM IB/flush/pipeline helpers, and ring pointer accessors protected by `adev->grbm_idx_mutex`. Two ring function tables support physical and VM modes.

Control flow: early init reads harvest fuses, disables the block if both instances are harvested, runs shared VCE early setup, starts with three rings, and installs funcs/IRQs. SW init registers the VISLANDS VCE trap, allocates memory for two firmware stack/data regions, reduces to two rings if firmware is older than 52.8.3, resumes firmware memory, and initializes rings. HW init overrides VCE clock gating, sets clocks, and ring-tests all active rings. Start iterates live VCE instances, selects instance registers through `GRBM_GFX_INDEX`, programs ring buffers, MC cache windows, VCPU clock/reset, waits for firmware loaded, and clears busy.

State and persistence: Driver state includes `adev->vce.harvest_config`, `num_rings`, `fw_version`, `srbm_soft_reset`, `ring[]`, IRQ, idle work, PM/CG flags, and `grbm_idx_mutex`. Hardware state includes per-instance VCE registers selected through GRBM, cache BAR/offset/size registers, VCE status bits, ring pointers/base/size, VCE clock-gating registers, SRBM reset bits, and SMC PG status for clock-gating queries.

Dependencies and integration points: Uses shared VCE parser/test/fence helpers, VM-mode VCE CS parser, GFX/SMU/OSS/VCE register headers, VISLANDS interrupt IDs, DPM clock hooks, and ring core VM callbacks. VM mode is selected for `CHIP_STONEY` and newer; older chips use physical mode.

Risks: GRBM instance selection must always be restored to default and protected by the mutex; missed restoration affects unrelated register access. Harvest configuration changes ring/instance mapping and can disable the block. Firmware version gates three-ring support. `check_soft_reset` uses VCE status bits for both instances and sets both VCE0/VCE1 reset bits when either appears busy. Some offsets in `mc_resume` use narrower masks for instance 1 and should be kept consistent with firmware memory layout.

Test signals: Ring tests for active rings, firmware loaded bit per live instance, harvest fuse behavior, VM IB/flush tests where VM mode is active, clock-gating state readback, SRBM reset logs, and trap IRQ processing for rings 0..2. Failure signals include both-instances-harvested `-ENOENT`, firmware loaded timeout, idle wait timeout, unhandled interrupt source data, and reset/resume failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vce_v3_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vce_v3_0.h -->
## Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vce_v3_0.h

Purpose: Declares the VCE 3.x IP block descriptors implemented by `vce_v3_0.c`.

Important APIs and types: Exports `vce_v3_0_ip_block`, `vce_v3_1_ip_block`, and `vce_v3_4_ip_block`.

Control flow and integration: ASIC block tables use the matching descriptor for VCE major/minor variants while sharing the same implementation.

State and persistence: The header owns no runtime state.

Dependencies and risks: Requires matching definitions for all three descriptors. New minor variants require both a C definition and a header declaration.

Test signals: Compile/link coverage for ASIC configurations referencing any of the three VCE 3.x descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vce_v3_0.h -->
