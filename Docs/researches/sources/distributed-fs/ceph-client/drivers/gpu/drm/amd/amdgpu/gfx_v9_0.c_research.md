# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_0.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001338`: lines 1-7600, `Docs/researches/chunks/subset-b-001338_research.md`
- `subset-b-001339`: lines 7601-7916, `Docs/researches/chunks/subset-b-001339_research.md`

## Chunk Research

### subset-b-001338: lines 1-7600

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

### subset-b-001339: lines 7601-7916

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_0.c lines 7601-7916

## Purpose

This chunk is the tail of the AMDGPU GFX9 graphics IP driver. It finishes the ring-function dispatch tables, wires those tables and interrupt-source callbacks into `struct amdgpu_device`, initializes GDS/GWS/OA sizing for supported GFX9 ASIC variants, computes active compute-unit topology, and exports the `gfx_v9_0_ip_block` descriptor used by the AMDGPU IP-block framework.

The range starts at the final `.end_use` entry of `gfx_v9_0_sw_ring_funcs_gfx`, then fully covers the compute and KIQ ring function tables. These tables are static vtables of `struct amdgpu_ring_funcs` callbacks used by the common AMDGPU ring scheduler and IB submission paths. The rest of the chunk contains setup helpers called from `gfx_v9_0_early_init()` and a CU topology helper called from `gfx_v9_0_constants_init()`.

The highest-value behavior in this chunk is wiring. No command submission happens directly here; instead, this code decides which low-level packet emission, fence, VM flush, register access, reset, isolation, and test callbacks later ring operations will use. It also records chip-dependent limits, such as GDS size and maximum GDS wave ID, in `adev->gds`, and records active CU topology in `adev->gfx.cu_info`.

## Important APIs, Types, And Functions

- `static const struct amdgpu_ring_funcs gfx_v9_0_ring_funcs_compute`: callback table for GFX9 compute rings. It supplies compute ring pointer accessors, IB emission, fence emission, synchronization, VM/TLB flush, GDS/HDP handling, register wait/write helpers, wave-limit emission, KCQ reset, cleaner shader emission, and compute ring begin/end hooks.
- `static const struct amdgpu_ring_funcs gfx_v9_0_ring_funcs_kiq`: callback table for the kernel interface queue. It uses compute-style ring pointer accessors but a KIQ-specific fence emitter and exposes register read/write/wait callbacks for kernel queue management.
- `gfx_v9_0_set_ring_funcs(struct amdgpu_device *adev)`: assigns ring function tables into `adev->gfx.kiq[0].ring`, every hardware graphics ring, optional software graphics rings when MCBP is enabled, and every compute ring.
- `static const struct amdgpu_irq_src_funcs ...`: five IRQ source vtables for end-of-pipe interrupts, privileged register faults, bad opcode faults, privileged instruction faults, and CP ECC/FUE errors.
- `gfx_v9_0_set_irq_funcs(struct amdgpu_device *adev)`: initializes IRQ source type counts and callback tables under `adev->gfx`.
- `gfx_v9_0_set_rlc_funcs(struct amdgpu_device *adev)`: selects `gfx_v9_0_rlc_funcs` for known GFX9 IP versions that support this RLC implementation.
- `gfx_v9_0_set_gds_init(struct amdgpu_device *adev)`: sets `adev->gds.gds_size`, `gds_compute_max_wave_id`, `gws_size`, and `oa_size` according to the GC IP version and Raven APU variant.
- `gfx_v9_0_set_user_cu_inactive_bitmap(struct amdgpu_device *adev, u32 bitmap)`: writes `mmGC_USER_SHADER_ARRAY_CONFIG` to apply a per-SE/SH disabled-CU bitmap when the bitmap is nonzero.
- `gfx_v9_0_get_cu_active_bitmap(struct amdgpu_device *adev)`: reads hardware and user inactive-CU masks, combines them, and returns the active CU bitmap constrained to `max_cu_per_sh`.
- `gfx_v9_0_get_cu_info(struct amdgpu_device *adev, struct amdgpu_cu_info *cu_info)`: walks all shader engines and shader arrays, selects each SE/SH through GRBM indexing, applies disabled-CU masks, reads active CUs, and fills `amdgpu_cu_info`.
- `const struct amdgpu_ip_block_version gfx_v9_0_ip_block`: exported IP-block descriptor for GFX major 9, minor 0, rev 0, linked to `gfx_v9_0_ip_funcs`.

## Control Flow

The ring callback tables are static data, but they determine later runtime dispatch. Compute rings use `gfx_v9_0_ring_get_rptr_compute()`, `gfx_v9_0_ring_get_wptr_compute()`, and `gfx_v9_0_ring_set_wptr_compute()` for queue pointer handling. Their frame-size budget accounts for GDS switches, HDP invalidation, pipeline sync, TLB flush register writes/waits, fences, memory sync, wave-limit updates, and cleaner shader emission. KIQ rings share compute pointer handling but use a smaller frame-size budget and a KIQ-specific fence path.

`gfx_v9_0_early_init()` calls `gfx_v9_0_set_ring_funcs()`, `gfx_v9_0_set_irq_funcs()`, `gfx_v9_0_set_gds_init()`, and `gfx_v9_0_set_rlc_funcs()` after setting `adev->gfx.funcs`, graphics ring count, XCC mask, compute ring count, and KIQ PM4 callbacks. In this chunk's setup flow:

1. The first KIQ ring receives `gfx_v9_0_ring_funcs_kiq`.
2. Each configured graphics ring receives the graphics ring function table defined immediately before this chunk.
3. If MCBP is enabled and graphics rings exist, all `GFX9_NUM_SW_GFX_RINGS` software graphics rings receive `gfx_v9_0_sw_ring_funcs_gfx`.
4. Each configured compute ring receives `gfx_v9_0_ring_funcs_compute`.
5. IRQ source structures are assigned their callback vtables and type counts.
6. RLC callbacks are installed only for enumerated GC IP versions.
7. GDS sizing is selected from the GC IP version and APU flags.

The CU information path is invoked later from `gfx_v9_0_constants_init()`. `gfx_v9_0_get_cu_info()` first validates `adev` and `cu_info`, then rejects layouts where `max_shader_engines * max_sh_per_se` exceeds the fixed 16-entry disable-mask capacity. It obtains disabled-CU masks through `amdgpu_gfx_parse_disable_cu()`, locks `adev->grbm_idx_mutex`, and iterates each shader engine and shader array. For each SE/SH pair it selects the register index, applies the user inactive-CU bitmap, reads the active bitmap, stores it in `cu_info->bitmap`, builds an always-on CU bitmap, and accumulates the active CU count. At the end it restores the broadcast SE/SH selection, unlocks the mutex, and fills `cu_info->number`, `cu_info->ao_cu_mask`, and `cu_info->simd_per_cu`.

## State And Persistence Behavior

Most state changes in this chunk are assignments into `struct amdgpu_device`. Ring and IRQ setup persist as driver software state for the lifetime of the device instance or until another initialization/reset path overwrites those pointers. The function tables themselves are static `const` storage and are not mutated.

`gfx_v9_0_set_gds_init()` persists chip-derived resource limits in `adev->gds`. GDS internal memory size is `0x10000` for several discrete GFX9 variants, `0x1000` for Raven/Renoir-style variants, and `0` for Aldebaran (`IP_VERSION(9, 4, 2)`) because that ASIC removed GDS internal memory and only supports kernel-side GWS-style operations. `gws_size` is always set to 64 and `oa_size` to 16 in this chunk.

CU discovery has both software and hardware side effects. It writes `mmGC_USER_SHADER_ARRAY_CONFIG` for each selected SE/SH when a disable bitmap is present, then reads `mmCC_GC_SHADER_ARRAY_CONFIG` and `mmGC_USER_SHADER_ARRAY_CONFIG` to derive active CUs. It stores the result in `adev->gfx.cu_info` through the caller. The GRBM index selection is protected by `adev->grbm_idx_mutex` and is restored to broadcast values before unlocking, which is important because later MMIO reads/writes elsewhere in the driver assume predictable SE/SH selection state.

No disk persistence, heap allocation, or user-visible file state is created here. Hardware register writes made during CU discovery and later ring use remain effective until reset, reinitialization, or another register programming path changes them.

## Dependencies

This chunk depends on the AMDGPU core ring and interrupt abstractions:

- `struct amdgpu_ring_funcs` defines the callback contract consumed by common ring scheduling, IB submission, fence, VM flush, and reset paths.
- `struct amdgpu_irq_src_funcs` defines the IRQ source callback contract consumed by AMDGPU interrupt registration and processing.
- `struct amdgpu_device`, especially `adev->gfx`, `adev->gds`, `adev->apu_flags`, and `adev->grbm_idx_mutex`, is the central mutable state object.
- Ring packet constants such as `PACKET3(PACKET3_NOP, 0x3FFF)` and flush-size macros such as `SOC15_FLUSH_GPU_TLB_NUM_WREG` and `SOC15_FLUSH_GPU_TLB_NUM_REG_WAIT` must match the packet emitters referenced in the tables.
- Register access helpers `RREG32_SOC15()` and `WREG32_SOC15()` and register-field masks for `mmGC_USER_SHADER_ARRAY_CONFIG` and `mmCC_GC_SHADER_ARRAY_CONFIG` must match the GFX9 register layout.
- ASIC detection through `amdgpu_ip_version(adev, GC_HWIP, 0)` and `IP_VERSION()` drives RLC function selection and GDS sizing.
- CU topology helpers `amdgpu_gfx_parse_disable_cu()`, `amdgpu_gfx_select_se_sh()`, and `amdgpu_gfx_create_bitmask()` provide disabled-CU policy, GRBM indexing, and mask construction.

The final `gfx_v9_0_ip_block` depends on the larger file's `gfx_v9_0_ip_funcs` table. That table is the external integration point used by the AMDGPU IP-block framework to call early init, software init, hardware init, suspend/resume, reset, idle, clockgating, and diagnostic hooks.

## Integration Points

The immediate integration point is `gfx_v9_0_early_init()`, which calls the setup helpers in this chunk before microcode initialization. If any function table pointer is wrong or omitted, later queue setup and command submission will dispatch through the wrong low-level operations or through null callbacks.

The ring tables integrate with multiple common AMDGPU subsystems:

- Graphics and compute schedulers consume `.emit_ib`, `.emit_fence`, `.test_ring`, `.test_ib`, `.pad_ib`, and pointer callbacks.
- VM and memory-management paths consume `.emit_vm_flush`, TLB flush frame-size accounting, `.emit_mem_sync`, and HDP/GDS synchronization callbacks.
- Reset and recovery paths use `.reset`, `.soft_recovery` for software graphics rings, and the begin/end-use isolation hooks.
- KIQ paths use `.emit_rreg`, `.emit_wreg`, `.emit_reg_wait`, and `.emit_reg_write_reg_wait` to perform register operations through the queue when direct MMIO is not appropriate.

The IRQ tables integrate with CP interrupt handling. EOP interrupts have `AMDGPU_CP_IRQ_LAST` types; privileged register, bad opcode, and privileged instruction faults each expose one type; CP ECC error handling exposes two types for C5 ECC and C9 FUE error sources. Their `.process` callbacks route events into GFX9-specific handlers or the common `amdgpu_gfx_cp_ecc_error_irq()` handler.

CU topology integrates with initialization and user-visible capability reporting through `adev->gfx.cu_info`. The array remapping in `gfx_v9_0_get_cu_info()` keeps the older 4x4 bitmap layout compatible with Arcturus-style 8x1 SE/SH topology by mapping `SE4..SE7,SH0` into the second SH column of the existing array.

The exported `gfx_v9_0_ip_block` makes the entire file available as the GFX IP implementation for GFX major 9. Other driver code registers this block based on ASIC discovery and then operates through the IP-block function table rather than calling most local functions directly.

## Risks And Edge Cases

- Ring frame-size constants must remain synchronized with the packet emitters they describe. Underestimating `.emit_frame_size` can cause command emission to overrun reserved ring space; overestimating wastes ring capacity and can mask accounting bugs.
- The compute and KIQ tables share several callbacks but intentionally differ in fence emission, test-IB exposure, register read support, reset support, and NOP insertion. Copying entries between them without checking queue semantics can break KIQ register programming or compute queue reset.
- `gfx_v9_0_set_ring_funcs()` assumes `adev->gfx.kiq[0]` exists and that ring counts were already initialized. That is satisfied by the surrounding early-init ordering, but changes to early-init sequencing could make this unsafe.
- Software graphics rings are assigned only when `adev->gfx.mcbp` and at least one graphics ring are present. Code expecting `sw_gfx_ring[i].funcs` on MCBP-disabled or compute-only ASICs must tolerate null function pointers.
- `gfx_v9_0_set_rlc_funcs()` silently leaves `adev->gfx.rlc.funcs` unchanged for unknown IP versions. New GFX9-like variants need explicit review to avoid missing RLC support.
- GDS sizing is hard-coded by IP version, with Raven2 differentiated by `AMD_APU_IS_RAVEN2`. Incorrect ASIC identification can expose wrong GDS capacity or wave-ID limits to later queue setup.
- `gfx_v9_0_set_user_cu_inactive_bitmap()` returns without writing when the disable bitmap is zero. This relies on the selected SE/SH already having no stale user inactive-CU bits, or on earlier initialization having cleared the register.
- `gfx_v9_0_get_cu_info()` rejects layouts larger than the fixed 4x4 disable-mask storage. A future GFX9 derivative with more SE/SH combinations would fail CU discovery until the data structure and mapping are expanded.
- The CU info helper writes user inactive-CU configuration while probing. If an error path were added inside the locked loop, it would need to restore broadcast GRBM selection before returning.
- `ao_cu_mask` is populated only for `i < 2 && j < 2`, so it preserves the legacy compact mask behavior and is not a complete representation for larger topologies. Consumers must use the full bitmap arrays when they need all SE/SH entries.

## Test Signals

- Driver probe on representative GFX9 ASICs should show successful `gfx_v9_0_early_init()` and no null ring-function dereferences during software/hardware init.
- Ring self-tests should pass for graphics rings, compute rings, and the KIQ ring, covering `.test_ring`, `.test_ib` where provided, pointer get/set, IB emission, and fence emission.
- VM stress and GPU memory-management tests should exercise `.emit_vm_flush`, TLB wait/write sequences, `.emit_mem_sync`, and HDP/GDS synchronization on compute and graphics queues.
- Queue reset and recovery tests should cover KGQ, KCQ, and software graphics ring reset/recovery callbacks where those ring types are enabled.
- KIQ register-access tests should validate `.emit_rreg`, `.emit_wreg`, `.emit_reg_wait`, and `.emit_reg_write_reg_wait`, especially on paths where direct MMIO is restricted.
- Interrupt tests or fault injection should confirm EOP, privileged-register, bad-opcode, privileged-instruction, and CP ECC/FUE IRQ sources dispatch to the expected handlers with the configured `num_types`.
- ASIC matrix testing should verify GDS size and `gds_compute_max_wave_id` for `IP_VERSION(9,0,1)`, `(9,2,1)`, `(9,4,0)`, `(9,2,2)`, `(9,1,0)`, `(9,4,1)`, and `(9,4,2)`, including Raven2 versus Raven1 behavior.
- CU topology tests should compare `adev->gfx.cu_info` against known fuse/disable masks, including Arcturus-style 8x1 layouts, disabled-CU module parameters, and the legacy `ao_cu_mask` fields.
- Static checks should flag drift between ring emitters and `.emit_frame_size` arithmetic, and should detect any new GFX9 IP version that lacks explicit RLC/GDS/CU topology review.
