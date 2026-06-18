# subset-b-001367 Research

Grouped research for AMDGPU VCN 4.0.5/5.0.x and Vega10 IH/register initialization files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v4_0_5.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v4_0_5.c

## Purpose
Implements the AMDGPU VCN 4.0.5 IP block driver. It wires VCN firmware loading, unified encode ring setup, dynamic/static power management, memory-controller windows, interrupt dispatch, ring reset, register-dump support, and IP block lifecycle callbacks for VCN 4.0.5/4.0.6 class hardware.

## Important APIs, Types, And Functions
The exported integration point is `vcn_v4_0_5_ip_block`, whose `amd_ip_funcs` cover early/software/hardware init, fini, suspend/resume, idle waits, clockgating, powergating, and VCN IP-state dump/print helpers. `vcn_v4_0_5_early_init()` sets one encode ring per VCN instance as the unified queue, installs ring and IRQ functions, attaches `set_pg_state`, and calls `amdgpu_vcn_early_init()`. `vcn_v4_0_5_sw_init()` allocates VCN software state, resumes firmware buffers, registers general-purpose and poison IRQ IDs, initializes the doorbell-backed unified ring, configures `amdgpu_vcn4_fw_shared`, optional firmware logging, DPG pause hooks, reset masks, SR-IOV MM table state, sysfs reset mask, and register dump coverage. `vcn_v4_0_5_start()`, `vcn_v4_0_5_stop()`, and their DPG variants are the core hardware sequencing routines. The `amdgpu_ring_funcs` instance reuses VCN 2.0 encoder packet emitters and supports reset through stop/start.

## Control Flow
Normal probe flows through early init, software init, then hardware init. Hardware init programs NBIO VCN doorbell ranges and runs `amdgpu_ring_test_helper()` on every non-harvested instance. Ungating calls `vcn_v4_0_5_start()`: DPM is enabled when available, DPG mode is selected if supported, otherwise static PG is disabled, VCPU/LMI/MPC registers are initialized, firmware cache/stack/context/shared windows are programmed, the VCPU is released from reset, readiness is polled with reset retries, master interrupts are enabled, and RB1 is configured. Gating sets firmware queue holdoff, drains ring and LMI clean status, resets VCPU/LMI, clears status, reapplies clock/power gating, and disables DPM. DPG start writes an SRAM command stream directly or indirectly through PSP, then programs RB1 and doorbell while managing firmware queue reset bits. Interrupts demux VCN0/VCN1 client IDs to an instance, process fence interrupts on the unified ring, and forward poison interrupts to common VCN poison handling.

## State And Persistence
Persistent driver state lives in `adev->vcn.inst[]`: firmware BO addresses, shared firmware memory, ring pointers, `sched_score`, per-instance `cur_state`, DPG pause state, SRAM staging pointers, reset masks, and delayed idle work. Hardware state is persisted in VCN registers and doorbells until suspend/reset. The firmware shared area advertises unified queue, SMU DPM interface type, optional VF RB setup, DRM key-injection workaround, and queue enable/reset/holdoff bits. SR-IOV additionally allocates/free a virtualization MM table.

## Dependencies And Integration Points
Depends on common AMDGPU VCN helpers, SOC15 register macros, VCN 4.0.5 offsets/masks, VCN 4.0 IRQ IDs, PSP firmware loading, NBIO doorbell aperture control, DPM, DRM device liveness guards, VCN firmware logging, sysfs reset-mask plumbing, and ring/fence scheduler helpers. It integrates with reset infrastructure through `supported_reset`, with debug collection through `amdgpu_vcn_reg_dump_init()`, and with secure submission by enabling `secure_submission_supported` for IP 4.0.5.

## Risks And Test Signals
Risks cluster around ordering-sensitive MMIO: VCPU boot polling, DPG pause/ack waits, readbacks used as write flushes, and ring reset bit transitions. Doorbell index math differs for SR-IOV and bare metal and can break ring progress if mismatched. Harvested instances must be skipped consistently. Test signals include successful `amdgpu_ring_test_helper()`, VCN IB tests, fence interrupts, sysfs reset-mask exposure, ring reset recovery, suspend/resume, poison interrupt handling, and VCN firmware log output when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v4_0_5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v4_0_5.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v4_0_5.h

## Purpose
Declares the public interface for the VCN 4.0.5 implementation. It gives other AMDGPU IP discovery and RAS code a stable symbol for the VCN 4.0.5 IP block and names the RAS-queryable VCN sub-blocks for this generation.

## Important APIs, Types, And Functions
`enum amdgpu_vcn_v4_0_5_sub_block` currently defines `AMDGPU_VCN_V4_0_5_VCPU_VCODEC` and the `AMDGPU_VCN_V4_0_5_MAX_SUB_BLOCK` sentinel. `extern const struct amdgpu_ip_block_version vcn_v4_0_5_ip_block` exposes the implementation object defined in `vcn_v4_0_5.c`.

## Control Flow
This header has no executable control flow. At compile time, device-family tables can reference `vcn_v4_0_5_ip_block`; at runtime, the AMDGPU IP framework invokes the function table attached to that object. The enum is intended for bounded iteration or switch statements over VCN RAS sub-blocks.

## State And Persistence
No state is stored by the header. The enum values become ABI-like constants within the driver build, and the external IP block symbol resolves to the lifecycle state machine in the C file.

## Dependencies And Integration Points
The header assumes consumers have the definition of `struct amdgpu_ip_block_version` from AMDGPU core headers. It integrates with the source file that defines the object and with ASIC tables that select the VCN implementation.

## Risks And Test Signals
The main risk is enum drift: RAS/status code must update `MAX_SUB_BLOCK` if new sub-blocks are added. Build coverage is the primary signal: missing `amdgpu_ip_block_version` declarations or mismatched symbol names fail compilation. Runtime signal comes indirectly when the selected VCN IP block probes and initializes successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v4_0_5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v5_0_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v5_0_0.c

## Purpose
Implements the VCN 5.0.0 AMDGPU IP block. It is structurally similar to VCN 4.0.5 but uses VCN 5.0 register definitions, VCN 5 firmware shared memory, SOC24 DPG programming paths, and generation-specific IRQ IDs.

## Important APIs, Types, And Functions
`vcn_v5_0_0_ip_block` is the exported IP block object. Lifecycle functions include `vcn_v5_0_0_early_init()`, `sw_init()`, `sw_fini()`, `hw_init()`, `hw_fini()`, `suspend()`, and `resume()`. Start/stop paths are split into direct and DPG variants: `vcn_v5_0_0_start()`, `vcn_v5_0_0_start_dpg_mode()`, `vcn_v5_0_0_stop()`, and `vcn_v5_0_0_stop_dpg_mode()`. Memory setup lives in `vcn_v5_0_0_mc_resume()` and `vcn_v5_0_0_mc_resume_dpg_mode()`. Ring operations are implemented by `vcn_v5_0_0_unified_ring_get_rptr()`, `get_wptr()`, `set_wptr()`, and `vcn_v5_0_0_ring_reset()`. Interrupt processing handles unified ring fence events and VCN poison traps.

## Control Flow
Early init makes every VCN instance expose one unified encode ring, installs ring/IRQ function tables, and calls common VCN early init per instance. Software init skips harvested instances, initializes firmware BOs and shared memory, registers VCN 5.0 general-purpose and poison IRQs, sets doorbell indices, initializes the unified ring, marks firmware shared unified queue state, enables SMU DPM interface metadata, and registers reset/sysfs/debug support. Hardware init opens NBIO doorbell ranges and runs ring tests. Non-DPG start powers tiles on, marks VCN busy, enables VCPU/LMI, programs firmware windows and tiling config, releases VCPU reset, polls readiness, enables interrupts, and configures RB1. DPG start uses SOC24 DPG-mode writes and optional PSP SRAM upload before RB1 setup. Stop drains status/LMI, disables channels and VCPU, soft-resets LMI, clears status, and optionally static-power-gates.

## State And Persistence
The file mutates `adev->vcn.inst[]` ring, firmware, pause, and power state, plus `adev->vcn.supported_reset`. Firmware shared state uses `struct amdgpu_vcn5_fw_shared`; it advertises unified queue and SMU DPM interface and stores queue reset/holdoff bits. Clockgating functions are intentionally empty, so clockgating state transitions mostly validate idleness without changing VCN CG registers in this generation.

## Dependencies And Integration Points
Depends on VCN 5.0 offsets/masks, IRQ source IDs, SOC15/SOC24 MMIO helpers, common VCN/ring/fence helpers, NBIO doorbell programming, PSP SRAM update for indirect DPG, DPM hooks, and DRM device-enter checks during fini. Reset integration includes soft/full reset masks and per-queue reset outside SR-IOV.

## Risks And Test Signals
Important risks are DPG SRAM programming correctness, PSP-vs-driver firmware cache address selection, doorbell index arithmetic, and empty clockgating hooks that must match hardware expectations. The VCPU boot loop can take up to repeated polling/reset attempts. Test signals are ring test/IB success, fence interrupt delivery, poison IRQ handling, DPG pause/unpause behavior, suspend/resume, sysfs reset-mask exposure, and register dumps including the listed VCN registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v5_0_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v5_0_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v5_0_0.h

## Purpose
Defines small VCN 5.0.0 public constants and declares the VCN 5.0.0 IP block object. The address constants describe VCN video/AON SOC and IP-relative base addresses for multiple instances.

## Important APIs, Types, And Functions
The file defines `VCN_VID_SOC_ADDRESS`, `VCN_AON_SOC_ADDRESS`, `VCN1_VID_SOC_ADDRESS`, `VCN1_AON_SOC_ADDRESS`, `VCN_VID_IP_ADDRESS`, and `VCN_AON_IP_ADDRESS`. It declares `extern const struct amdgpu_ip_block_version vcn_v5_0_0_ip_block`.

## Control Flow
There is no runtime control flow. Compile-time consumers include ASIC/IP discovery code and VCN implementation files that need these base address constants or the external IP block symbol.

## State And Persistence
The header stores no state. The constants become compile-time inputs to code that maps VCN register spaces; the external symbol points to lifecycle functions in `vcn_v5_0_0.c`.

## Dependencies And Integration Points
Requires AMDGPU core declarations for `struct amdgpu_ip_block_version`. It is included by VCN 5.0.x implementation files, so changes can affect address calculations outside only 5.0.0.

## Risks And Test Signals
Incorrect SOC/IP address constants would cause register programming against the wrong aperture, usually surfacing as VCN boot, ring, or interrupt failures. Build success checks symbol consistency; runtime ring tests and firmware boot are the meaningful integration signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v5_0_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v5_0_1.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v5_0_1.c

## Purpose
Implements VCN 5.0.1, adding AID-aware instance mapping, SR-IOV MMSCH initialization, per-queue reset gating by PSP/DPM capabilities, JPEG-coordinated VCN reset, and RAS/ACA poison reporting on top of the VCN 5 unified-ring model.

## Important APIs, Types, And Functions
`vcn_v5_0_1_ip_block` exports lifecycle callbacks including a `late_init()` that computes supported reset types. `vcn_v5_0_1_fw_shared_init()` lazily initializes `amdgpu_vcn5_fw_shared`. `vcn_v5_0_1_start_sriov()` builds and submits an MMSCH v5 init table for VF environments. `vcn_v5_0_1_start_dpg_mode()` and `stop_dpg_mode()` handle SOC24 DPG programming and PSP SRAM upload using `AMDGPU_UCODE_ID_VCN0_RAM`. `vcn_v5_0_1_ring_reset()` coordinates VCN reset with JPEG pre/post helpers. RAS logic is provided by `vcn_v5_0_1_query_poison_status()`, ACA bank parser/validator functions, and `vcn_v5_0_1_ras_late_init()`.

## Control Flow
Early init installs unified ring, IRQ, and RAS functions, assigns one encode ring per instance, and calls common VCN early init. Software init registers one shared VCN IRQ source and a separate poison IRQ source, initializes every instance, computes doorbell indices from `GET_INST(VCN, i)` with SR-IOV-specific spacing, sets the MMHUB from `aid_id`, initializes rings, allocates VF MM tables, initializes RAS if supported, and enables register dump/sysfs reset mask state. Hardware init either asks MMSCH to initialize VCN in SR-IOV and marks rings ready, or configures doorbells, refreshes firmware shared state, checks RRMT capability, and tests rings. Direct start follows VCPU boot sequencing with physical VCN instance IDs; DPG start also writes a dummy `0xDEADBEEF` DPG entry to communicate AID selection to PSP when using indirect SRAM. Interrupts map `entry->node_id` through `node_id_to_phys_map`, find the VCN instance with matching `aid_id`, and process fence interrupts.

## State And Persistence
State includes `aid_id`, `cur_state`, ring doorbell indices, firmware shared queue state, VF RB setup data inside shared memory, RAS block binding, poison IRQ registration, and per-instance reset mutexes. SR-IOV persists a guest-visible MMSCH table in `adev->virt.mm_table` and uses mailbox registers for completion status. Ring reset temporarily manipulates JPEG scheduler and power-gating state because VCN reset also resets JPEG.

## Dependencies And Integration Points
Depends on VCN 5.0 registers, VCN 4.0.3 ring emit helpers for VM flush/HDP/wreg/reg-wait, MMSCH v5 command formats, SR-IOV virtualization MM tables, DPM reset support, PSP SOS firmware version checks, JPEG power/scheduler helpers, RAS core, ACA bank decoding/cache logging, and AMDGPU IRQ/ring/fence infrastructure.

## Risks And Test Signals
Risks include logical-vs-physical instance mismatches, shared `adev->vcn.inst->irq` setup for multiple instances, SR-IOV mailbox timeout or incomplete status handling, incorrect MMSCH table sizes, and reset interactions with JPEG queues. RAS risks include filtering the wrong ACA banks or missing poison IRQ enablement. Test signals include VF MMSCH mailbox OK/pass status, ring and IB tests, AID-routed fence interrupts, JPEG rings recovering after VCN reset, DPM per-queue reset success, RAS poison query logs, ACA error counts, suspend/resume under reset, and RRMT capability detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v5_0_1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v5_0_1.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v5_0_1.h

## Purpose
Declares the VCN 5.0.1 IP block and generation-specific constants needed by the implementation, including the RRMT control register and RAS sub-block identifiers.

## Important APIs, Types, And Functions
Defines `regVCN_RRMT_CNTL` and `regVCN_RRMT_CNTL_BASE_IDX`, which are used to detect RRMT capability in VCN 5.0.1/5.0.2 paths. `enum amdgpu_vcn_v5_0_1_sub_block` currently contains `AMDGPU_VCN_V5_0_1_VCPU_VCODEC` plus a `MAX_SUB_BLOCK` sentinel for RAS iteration. The external symbol is `vcn_v5_0_1_ip_block`.

## Control Flow
No executable flow exists in the header. Runtime behavior occurs when VCN implementation code reads the RRMT register or iterates the enum-defined sub-block range in poison-status queries.

## State And Persistence
The header contributes constants only. Register reads using these constants may set persistent capability bits such as `AMDGPU_VCN_CAPS(RRMT_ENABLED)` in `adev->vcn.caps`, but that state is held outside the header.

## Dependencies And Integration Points
Assumes AMDGPU core declarations for the IP block type. It is included by both `vcn_v5_0_1.c` and `vcn_v5_0_2.c`, so the RRMT definitions are shared across nearby VCN revisions.

## Risks And Test Signals
Wrong RRMT register metadata can mis-detect firmware/hardware capability. RAS enum drift can cause missing sub-block scans. Build success validates declarations; runtime signals are RRMT capability bits and poison query coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v5_0_1.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v5_0_2.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v5_0_2.h

## Purpose
Declares the VCN 5.0.2 IP block object. This is the source-level hook that lets ASIC/IP discovery tables select the VCN 5.0.2 implementation.

## Important APIs, Types, And Functions
The single public declaration is `extern const struct amdgpu_ip_block_version vcn_v5_0_2_ip_block`, defined in `vcn_v5_0_2.c`.

## Control Flow
The header has no runtime control flow. When an ASIC table references `vcn_v5_0_2_ip_block`, the AMDGPU IP framework invokes the lifecycle function table bound to that object.

## State And Persistence
No state is stored here. Runtime state is held by the IP block object and the per-device `adev->vcn` structures initialized by the C file.

## Dependencies And Integration Points
Requires the core AMDGPU IP block type declaration to be visible to consumers. It integrates only through symbol linkage with the implementation and ASIC selection code.

## Risks And Test Signals
Risk is limited to declaration/symbol mismatch or incorrect ASIC table selection. Build success catches declaration issues; runtime probe, VCN ring tests, and interrupt delivery validate the chosen implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v5_0_2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vega10_ih.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vega10_ih.c

## Purpose
Implements the Vega10-generation interrupt handler IP block. It initializes IH ring buffers, programs IH MMIO register offsets, toggles interrupt delivery, reads and advances ring pointers, handles overflow/rearm behavior, dispatches self-interrupt work for secondary rings, and exposes IH lifecycle callbacks to the AMDGPU IP framework.

## Important APIs, Types, And Functions
`vega10_ih_ip_block` and `vega10_ih_ip_funcs` are the IP framework entry points; `vega10_ih_funcs` supplies low-level IH operations: `get_wptr`, IV decoding helpers, and `set_rptr`. `vega10_ih_init_register_offset()` maps ring0/ring1/ring2 register addresses and PSP register IDs into `amdgpu_ih_regs`. `vega10_ih_irq_init()` disables rings, runs NBIO IH control, applies Renoir MC-space handling, enables each ring, configures doorbell ranges, sets PCI bus master, and re-enables interrupts. `vega10_ih_get_wptr()` handles writeback and overflow recovery; `vega10_ih_set_rptr()` updates doorbells or MMIO RPTR; `vega10_ih_self_irq()` schedules secondary ring workers.

## Control Flow
Early init installs IH and self-IRQ callbacks. Software init registers the self IRQ source, allocates ring0, optionally allocates ring1/ring2 on non-APU devices, assigns doorbell indices, initializes register offsets, creates the software IH ring, and calls common IRQ software init. Hardware init calls `vega10_ih_irq_init()`. Enabling a ring writes base addresses, composes `IH_RB_CNTL` fields, configures writeback for ring0, clears pointers, programs RPTR doorbell control, and then `vega10_ih_toggle_interrupts(true)` sets `RB_ENABLE`, GPU timestamping, and ring0 `ENABLE_INTR`. SR-IOV programs IH control registers through PSP instead of raw writes. Runtime interrupt processing reads WPTR from writeback/registers, clears overflows, advances RPTR via doorbell/MMIO, and may rearm doorbells for SR-IOV if writes are lost.

## State And Persistence
State lives in `adev->irq.ih`, `ih1`, `ih2`, and `ih_soft`: ring size, GPU base address, writeback/rptr CPU pointers, doorbell index, enabled flag, pointer mask, and current `rptr`. Register offsets and PSP IDs persist in each `ih_regs` substructure. Hardware state persists in IH RB control/base/pointer/doorbell registers. Clockgating state is updated through `mmIH_CLK_CTRL` when `AMD_CG_SUPPORT_IH_CG` is enabled.

## Dependencies And Integration Points
Depends on OSSSYS 4.0 offsets/masks, SOC15 register helpers, NBIO IH control/doorbell range callbacks, PSP register programming for SR-IOV, PCI bus mastering, common AMDGPU IH allocation/IRQ initialization, IV decode helpers, workqueues for secondary rings, and chip-specific behavior for Renoir. It is consumed by the AMDGPU interrupt dispatch path through `adev->irq.ih_funcs`.

## Risks And Test Signals
Risks include incorrect register offset selection for optional rings, PSP programming timeout in SR-IOV, IH ring overflow losing vectors, lost doorbell writes requiring rearm, writeback availability only on ring0, and clockgating override differences on Renoir. `is_idle()` is a stub returning true and `wait_for_idle()` returns `-ETIMEDOUT`, so generic idle diagnostics are weak. Test signals include successful IRQ init, interrupt delivery on ring0, scheduled work on ring1/ring2 self IRQs, overflow warnings with recovery, SR-IOV PSP programming success, suspend/resume interrupt recovery, and correct RPTR/WPTR movement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vega10_ih.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vega10_ih.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vega10_ih.h

## Purpose
Declares the public Vega10 IH integration symbols for the AMDGPU IP framework and any code that needs the IH function table.

## Important APIs, Types, And Functions
Declares `extern const struct amd_ip_funcs vega10_ih_ip_funcs` and `extern const struct amdgpu_ip_block_version vega10_ih_ip_block`, both defined by `vega10_ih.c`.

## Control Flow
The header contains no executable flow. The AMDGPU device/IP setup code references the declared IP block, then invokes the lifecycle callbacks and IH functions provided by the C file.

## State And Persistence
No state is stored in the header. It exposes symbols that control per-device IH state in `adev->irq` at runtime.

## Dependencies And Integration Points
Consumers need declarations for `struct amd_ip_funcs` and `struct amdgpu_ip_block_version`. It integrates with ASIC discovery and the interrupt subsystem by linking those symbols.

## Risks And Test Signals
Risk is confined to symbol drift or wrong IP block selection. Compilation validates the declarations; runtime validation comes from interrupt ring initialization and actual GPU interrupt handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vega10_ih.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vega10_reg_init.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vega10_reg_init.c

## Purpose
Initializes Vega10 register base tables and doorbell index assignments in the AMDGPU device. This is foundational setup that lets SOC15 register macros and ring code compute correct MMIO offsets and doorbell locations for Vega10-class hardware.

## Important APIs, Types, And Functions
`vega10_reg_base_init(struct amdgpu_device *adev)` fills `adev->reg_offset[HWIP][instance]` for GC, HDP, MMHUB, ATHUB, NBIO, MP0, MP1, UVD, VCE, VCN, DF, DCE, OSSSYS, SDMA0/1, SMUIO, PWR, NBIF, THM, and CLK using tables from `vega10_ip_offset.h`. `vega10_doorbell_index_init(struct amdgpu_device *adev)` assigns `adev->doorbell_index` fields for KIQ, MEC rings, user queues, GFX, SDMA, IH, UVD/VCE, VCN, non-CP range, maximum assignment, and SDMA doorbell range.

## Control Flow
Register base initialization loops from zero to `MAX_INSTANCE - 1`, assigning every supported HWIP slot to the corresponding static base table instance. Doorbell initialization is straight-line assignment of symbolic Vega10 doorbell constants into the device structure. Callers run these routines during ASIC/device initialization before subsystems use `SOC15_REG_OFFSET()` or doorbell writes.

## State And Persistence
The file persists per-device register base pointers in `adev->reg_offset` and doorbell layout in `adev->doorbell_index`. These values remain central throughout device lifetime: MMIO helpers use register bases, while ring/IH/VCN/SDMA/GFX code derives doorbell indices from this table.

## Dependencies And Integration Points
Depends on `amdgpu.h`, `soc15.h`, `soc15_common.h`, and `vega10_ip_offset.h`. It integrates with every SOC15 IP block using `adev->reg_offset`, and with queue/ring initialization for KIQ, MEC, GFX, SDMA, IH, UVD/VCE, and VCN doorbells.

## Risks And Test Signals
Incorrect base-table assignment can redirect MMIO reads/writes to the wrong IP block, causing broad bring-up failures. Doorbell mistakes can break scheduler queues, IH pointer updates, VCN/UVD/VCE progress, or user queue bounds. The comment in `vega10_reg_base_init()` contains typos but the code is direct. Test signals include successful ASIC probe, valid register reads through SOC15 macros, ring tests for GFX/SDMA/VCN/UVD/VCE, interrupt delivery through IH doorbells, and absence of doorbell range faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vega10_reg_init.c -->
