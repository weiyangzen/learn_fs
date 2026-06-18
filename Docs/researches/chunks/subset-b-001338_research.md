# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_0.c lines 1-7600

## Scope

This chunk covers the first 7,600 lines of `gfx_v9_0.c`, the AMDGPU GFX9 graphics/compute IP implementation. The source file continues past this chunk; this report intentionally stops at the beginning of the compute/KIQ ring function table area and does not synthesize the final per-file report.

## Purpose

The chunk implements most of the GFX9 IP block for AMD GPUs: firmware declaration and loading, chip-specific golden register programming, RLC/MEC/KIQ setup, graphics and compute ring initialization, command packet emission, interrupt handling, reset/recovery helpers, clock/power gating, RAS/ECC accounting, and debug dump support. It is the bridge between the generic AMDGPU IP/ring/RAS frameworks and GFX9-family register programming for Vega, Raven/Picasso/Renoir/Green Sardine, Arcturus/Aldebaran, and related GC 9.x variants.

## Important Data and Tables

- Firmware module declarations register required `amdgpu/<chip>_{ce,pfp,me,mec,mec2,rlc}.bin` blobs, including special Picasso AM4, Raven kicker, Arcturus, Renoir, Green Sardine, Aldebaran, and Aldebaran SR-IOV SJT MEC variants.
- `gc_reg_list_9` and `gc_cp_reg_list_9` define core GFX and per-HQD compute queue registers captured by IP dump/print paths.
- `ta_ras_gfx_subblock`, `struct ras_gfx_subblock`, `ras_gfx_subblocks`, and `gfx_v9_0_ras_fields` map AMDGPU RAS sub-blocks to PSP TA IDs, hardware/software supported error types, and SEC/DED bitfields.
- Golden setting arrays (`golden_settings_gc_9_0`, `_vg10`, `_vg20`, `_9_1`, Raven/Raven2/Renoir variants, Vega12, Arcturus, and common 9.x settings) provide masked register programming selected by GC IP version.
- `rlcg_access_gc_9_0` lists registers allowed through RLCG access checking.
- `GFX_RLC_SRM_INDEX_CNTL_ADDR_OFFSETS` and `_DATA_OFFSETS` drive RLC save/restore indirect register table programming.
- Embedded compute shader bytecode and register tables initialize VGPR/SGPR state during EDC GPR workarounds.
- `gfx_v9_0_ip_funcs`, `gfx_v9_0_ring_funcs_gfx`, and `gfx_v9_0_sw_ring_funcs_gfx` expose this implementation to AMDGPU’s IP block and ring subsystems within this chunk.

## Initialization and Lifecycle

`gfx_v9_0_early_init()` installs `adev->gfx.funcs`, sets the number of graphics rings to zero for compute-only GFX 9.4.1/9.4.2 parts, computes the KCQ count, installs KIQ PM4, ring, IRQ, GDS, and RLC function tables, initializes RLCG register-access metadata, then requests firmware through `gfx_v9_0_init_microcode()`.

Firmware setup is split by engine:

- `gfx_v9_0_init_cp_gfx_microcode()` requests PFP, ME, and CE firmware and initializes CP microcode metadata.
- `gfx_v9_0_init_rlc_microcode()` chooses normal, AM4-specific Picasso, or Raven kicker RLC firmware and initializes RLC metadata from the firmware header.
- `gfx_v9_0_init_cp_compute_microcode()` requests MEC/MEC2 firmware, suppressing MEC2 for 9.3.0, 9.4.1, and 9.4.2, and using Aldebaran SJT firmware in SR-IOV VF mode.
- `gfx_v9_0_check_fw_write_wait()` records whether firmware is new enough for native wait-reg-mem register-write/wait sequences and warns on old CP firmware.
- `gfx_v9_0_check_if_need_gfxoff()` disables or enables GFXOFF support based on PCI quirks, RLC firmware capability, APU flags, and IP version.

`gfx_v9_0_sw_init()` creates software-visible state: MEC topology, optional cleaner shader state, IRQ source IDs, RLC BOs, MEC EOP and firmware BOs, hardware GFX rings, software GFX rings and muxer for MCBP, compute rings allocated horizontally across MEC pipes, reset masks, KIQ ring/MQD state, GFX early hardware config, RAS block init, IP dump buffers, and GFX sysfs. `gfx_v9_0_sw_fini()` unwinds rings, MQDs, KIQ, cleaner shader, MEC/RLC BOs, firmware, sysfs, and dump buffers.

`gfx_v9_0_hw_init()` uploads/initializes cleaner shader data, programs golden registers on bare metal, initializes constants/VMID/GDS/SQ/TCP config, resumes RLC, resumes CP/KIQ/KCQ, and applies GFX 9.4.2 power-brake sequencing. `gfx_v9_0_hw_fini()` disables IRQs, disables KCQ unless handling RAS-triggered recovery, handles SR-IOV polling shutdown, optionally deinitializes KIQ registers, disables CP, and stops RLC except for XGMI-to-CPU reset and newer RLC-controlled-clock cases. Suspend and resume delegate to hw fini/init.

## Hardware Configuration

`gfx_v9_0_gpu_early_init()` populates `adev->gfx.config` by GC IP version, assigning context counts, SC FIFO sizes, GB address config, RAS implementation pointers, and optional Atom firmware-derived topology. It decodes fields such as pipe count, bank count, RBs per SE, shader engines, and pipe interleave size.

`gfx_v9_0_constants_init()` programs GRBM timeout, derives RB and CU info, records `DB_DEBUG2`, initializes shader memory apertures per VMID, initializes compute VMID LDS/scratch/GPUVM apertures for KFD VMIDs, clears GDS/GWS/OA access for nonzero VMIDs, and applies SQ configuration. `gfx_v9_0_select_se_sh()`, `gfx_v9_0_setup_rb()`, and `gfx_v9_0_get_rb_active_bitmap()` select per-SE/SH instances and compute active RB masks under `grbm_idx_mutex`.

RLC setup includes clear-state buffer sizing/parsing, APU CP table allocation, save/restore list programming for RLC v2.1-capable ASICs, load-balancing per-wave (LBPW) setup, RLCG access scratch register setup, and RLC start/stop/reset/resume. `gfx_v9_0_rlc_resume()` handles PSP versus legacy RLC firmware loading, power-gating table programming, LBPW enablement, SPM VMID initialization, and RLC startup.

## Ring, Queue, and Packet Control Flow

The KIQ PM4 helpers emit command packets for queue resource setup, queue mapping/unmapping, status queries, TLB invalidations, and per-HQD resets. Queue reset enters RLC safe mode, selects the HQD with SRBM/GRBM, issues dequeue/reset registers, polls `CP_HQD_ACTIVE`, restores broadcast selection, and exits safe mode.

Graphics ring bring-up (`gfx_v9_0_cp_gfx_resume()` and `gfx_v9_0_cp_gfx_start()`) resets write pointers, programs RB size/base/RPTR/WPTR/doorbells, enables CP GFX engines, emits the clear-state preamble from `gfx9_cs_data`, sets CE partition base, and initializes VGT index type. Compute bring-up loads MEC firmware through CPC IC base registers when firmware is not PSP-loaded, initializes KIQ registers/MQD, initializes or restores KCQ MQDs, maps KCQs through KIQ, and tests rings.

`gfx_v9_0_mqd_init()` builds a `struct v9_mqd` for compute/KIQ queues: EOP base/control, doorbell control, MQD base/control, HQD PQ base/control, read/write pointer report/poll addresses, VMID, persistent state, IB control, priority, and active flag for KIQ. KIQ and KCQ init paths preserve backup MQDs across reset/suspend and clear ring buffers/wptrs when restoring.

Ring callbacks in this chunk implement:

- Pointer access: 32-bit hardware RPTR reads, doorbell-backed WPTR reads/writes, and BUG paths for unsupported non-doorbell compute WPTR.
- IB emission: GFX emits `INDIRECT_BUFFER` or `INDIRECT_BUFFER_CONST` with preemption metadata and CE/DE metadata support; compute emits `INDIRECT_BUFFER` and can reset GDS wave IDs before dispatch.
- Synchronization: RELEASE_MEM fences, ACQUIRE_MEM cache sync, partial pipeline flush events, HDP flush waits, GPU TLB flushes, PFP/ME sync, switch-buffer, context control, frame control, conditional execution, register read/write/wait, and cleaner shader launch.
- Preemption/recovery/reset: IB preemption via KIQ unmap with trailing fence, soft recovery through `SQ_CMD`, KGQ VMID reset sequencing, and KCQ dequeue/remap reset sequencing.

## Interrupts and Fault Handling

`gfx_v9_0_sw_init()` registers IRQ IDs for EOP, bad opcode, privileged register, privileged instruction, CP ECC, and CP FUE events. `gfx_v9_0_late_init()` enables selected fault IRQs, runs ECC late workarounds, and initializes debug trap config for KFD VMIDs.

IRQ state functions program CP ring and MEC pipe interrupt-enable bits. EOP IRQ handling decodes `entry->ring_id` into ME, pipe, and queue; it processes fences on the real GFX ring, software rings under MCBP, or matching compute rings. Bad opcode, privileged register, and privileged instruction IRQ handlers log the illegal command-stream condition and call `drm_sched_fault()` on the affected scheduler through `gfx_v9_0_fault()`.

## RAS and ECC Behavior

RAS support is integrated through `gfx_v9_0_ras_ops`. Error injection validates RAS support, sub-block bounds, named/supported sub-blocks, hardware/software error-type support, translates AMDGPU RAS IDs to PSP TA IDs, and calls `psp_ras_trigger_error()` under `grbm_idx_mutex`.

EDC workarounds run during ECC late init. The GDS workaround clears GDS through a CPDMA packet on compute ring 0 and polls compute RPTR. The GPR workaround builds a direct IB containing VGPR and SGPR compute shader payloads, dispatches them over selected CU/thread dimensions, and waits on the returned fence.

Error queries iterate `gfx_v9_0_edc_counter_regs` across shader engines and instances under `grbm_idx_mutex`, read counter registers, decode fields via `gfx_v9_0_ras_fields`, and aggregate CE/UE counts. UTC/VM L2 and ATC L2 ECC status uses indexed registers and string tables. Resetting counters reads back per-instance counters and indexed ECC counters, then restores index registers to 255.

## Power, Clock, and Safe Mode

GFXOFF and power gating are guarded by IP-version quirks, firmware capability, PCI quirk list, and APU stability handling. `gfx_v9_0_set_powergating_state()` toggles GFXOFF, SCLK slow-down, CP power gating, GFX CG power gating, and static/dynamic per-CU gating for Raven/Renoir-like IPs; Vega12 delegates to immediate GFXOFF control.

Clock gating uses RLC safe mode. Enabling orders MGCG/MGLS before 3D CGCG/CGLS and coarse CGCG/CGLS; disabling reverses the order. State reporting reads RLC/CP sleep and CGCG registers through KIQ-safe register reads and sets AMD_CG flags.

`gfx_v9_0_get_gpu_clock_counter()` reads Renoir SMUIO TSC registers atomically for IP 9.3.0. Other IPs disable GFXOFF and use either KIQ register read in Vega10 SR-IOV runtime or RLC GPU clock capture registers under `gpu_clock_mutex`.

## State and Persistence

Persistent driver state lives mostly in `adev->gfx`: firmware pointers and version flags, RLC clear-state/CP table/register-list data, MEC firmware/EOP BOs, ring and MQD allocations, KIQ/KCQ MQD backups, cleaner shader buffers, ring muxer, IP dump buffers, CU/RB topology, RAS hooks, and power/clock gating flags. Hardware-visible persistence includes VRAM/GTT BOs for rings, EOP buffers, MEC firmware, clear-state blocks, CP tables, MQDs, writeback slots, and command-stream metadata in CSA.

Reset and suspend paths rely on MQD backups, zeroed ring write pointers, `amdgpu_in_reset()`, `adev->in_suspend`, and SR-IOV checks to decide whether to restore or rebuild queue state. Many register accesses are serialized with `srbm_mutex`, `grbm_idx_mutex`, `gpu_clock_mutex`, or `kiq->ring_lock`.

## Dependencies and Integration Points

This code depends on AMDGPU core subsystems (`amdgpu_device`, `amdgpu_ring`, `amdgpu_ib`, fences, writeback, BO management, sysfs), SOC15 register access helpers, GMC TLB flushing, NBIO HDP flush offsets, Atom firmware topology, PSP RAS services, KFD VMID ranges, DRM scheduler fault signaling, ring muxing for MCBP, GFX cleaner shader support, and GFX 9.4/9.4.2 sibling modules for Arcturus/Aldebaran-specific RAS, SQ, golden registers, EDC workarounds, debug traps, and power brake setup.

The exported `gfx_v9_0_ip_funcs` table is the main integration point with AMDGPU IP block management. `gfx_v9_0_gfx_funcs`, `gfx_v9_0_ras_ops`, `gfx_v9_0_rlc_funcs`, and ring function tables are secondary callback surfaces consumed by generic AMDGPU code and, indirectly, KFD/compute scheduling.

## Risks and Fragile Areas

- Register programming is highly IP-version-specific; a wrong IP-version branch can load the wrong firmware, program incompatible golden registers, or enable unsupported MEC2/RAS/GFX ring behavior.
- Queue reset and restore paths depend on precise mutex coverage, GRBM/SRBM selection restore, and RLC safe mode. Missed restore can leave later register accesses targeting the wrong HQD/SE/SH.
- Several paths use `BUG_ON()` for alignment, unsupported compute non-doorbell access, or indirect table invariants, so malformed state can panic rather than fail gracefully.
- Firmware version gates for wait-reg-mem and cleaner shader support are safety-critical; enabling these on unsupported firmware can hang queues.
- RAS counter decoding spans many dense tables with per-register instance counts. Any table drift relative to hardware register definitions can undercount, overcount, or log misleading CE/UE events.
- GFXOFF/power-gating handling has device quirks and APU-specific stability workarounds; changes here can surface as suspend/resume failures, ring timeouts, or intermittent compute hangs.
- KIQ clock/register reads deliberately avoid indefinite waiting during reset; callers must tolerate `~0` clock values.
- The GPR EDC workaround constructs raw IBs with embedded shaders and hard-coded register counts; table-size comments indicate updates must keep helper size assumptions synchronized.

## Test and Validation Signals

Useful signals include successful firmware requests, absence of CP firmware age warnings, successful `amdgpu_ring_test_helper()` for GFX/KIQ/compute rings, successful IB test on software rings, KCQ map/unmap without timeout, no `fail to wait on hqd deactive` messages, working suspend/resume and reset paths, stable GFXOFF/power-gating transitions, and correct DRM scheduler faulting on illegal command-stream IRQs.

RAS validation should check successful GDS/GPR EDC workarounds when RAS is enabled, correct CE/UE aggregation from `gfx_v9_0_query_ras_error_count()`, reset-by-read clearing behavior, and PSP RAS injection error paths for unsupported sub-blocks or types. Debug validation includes non-empty IP dump buffers, sane core/HQD register dumps, and correct fence processing for GFX, software GFX, and compute EOP interrupts.
