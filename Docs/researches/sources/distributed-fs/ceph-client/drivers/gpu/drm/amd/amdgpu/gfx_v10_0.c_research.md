# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_0.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001330`: lines 1-3706, `Docs/researches/chunks/subset-b-001330_research.md`
- `subset-b-001331`: lines 3707-10239, `Docs/researches/chunks/subset-b-001331_research.md`

## Chunk Research

### subset-b-001330: lines 1-3706

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_0.c lines 1-3706

## Scope And Purpose

This chunk is the front matter and hardware-configuration base of the AMDGPU GFX10 IP implementation. It covers the include set, local register aliases, firmware declarations, debug register lists, golden register-setting tables, shader-memory defaults, and forward declarations for functions implemented later in `gfx_v10_0.c`.

The covered range does not contain the main executable function bodies for GFX10 bring-up, ring operation, reset, power management, or interrupt handling. Instead, it provides the static data and declarations those later functions depend on. The final per-file report should merge this chunk with later chunks before describing full initialization, suspend/resume, ring emit, compute queue, RLC, and power-gating behavior.

At a high level, the data here supports several generations and ASIC families in the GFX10 line: Navi10/Navi12/Navi14, Sienna Cichlid and related GC 10.3 parts, Vangogh, Dimgrey Cavefish, Beige Goby, Yellow Carp, Cyan Skillfish, and GC 10.3.6/10.3.7. The large golden-setting tables encode ASIC-specific register masks and values that later initialization paths apply through SOC15 register helpers.

## Important APIs, Types, And Tables

The file depends on AMDGPU and SOC15 driver infrastructure through `amdgpu.h`, `amdgpu_gfx.h`, `amdgpu_psp.h`, `soc15.h`, `soc15_common.h`, `gfx_v10_0.h`, generated GC/SMUIO offset and mask headers, Navi enums, and GFX IRQ source IDs. Those headers provide the important local types used in this chunk: `struct amdgpu_device`, `struct amdgpu_ring`, `struct amdgpu_ip_block`, `struct amdgpu_cu_info`, `struct amdgpu_hwip_reg_entry`, `struct soc15_reg_golden`, and SOC15 register accessor/encoding macros.

The local register `#define`s fill gaps or provide ASIC-specific aliases for registers and fields not coming directly from the generated headers. Examples include Sienna Cichlid-specific RLC, SPI, VGT, GCR, doorbell, throttle, and TCC-disable registers; Vangogh-specific VGT/SPI/GCR/TSC locations; hypervisor CP microcode loading registers; PSP debug GPA override bits; shader-array disable masks; PBB mode control bits; and GC 10.3.6 TSC register locations.

`MODULE_FIRMWARE()` entries declare the firmware blobs this driver may request at runtime. The chunk covers CE, PFP, ME, MEC, MEC2, and RLC firmware for Navi10, Navi12, Navi14 including workstation Navi14 variants, Sienna Cichlid, Navy Flounder, Vangogh, Dimgrey Cavefish, Beige Goby, Yellow Carp, Cyan Skillfish 2, GC 10.3.6, and GC 10.3.7. These declarations affect kernel module firmware dependency metadata; actual selection and loading occur later through firmware initialization code.

`gc_reg_list_10_1[]` is the general GFX debug snapshot list. It names GRBM status registers, CP stalled/busy/status registers, ring buffer registers, IB base/size registers, UTCL1/UTCL0 status registers, GDS protection-fault registers, GCVM L2 fault registers, CP instruction pointers, RLC/SMU registers, RLC debug registers, MES header dump, and per-SE GRBM status registers.

`gc_cp_reg_list_10[]` is the compute queue/HQD debug list. It covers HQD VMID, persistent state, priority, quantum, PQ base/read/write/poll/doorbell/control fields, IB state, dequeue request/status, EOP state, context-save state, GDS resource state, error, and repeated MEC header-dump entries.

`gc_gfx_queue_reg_list_10[]` is the graphics queue debug list. It covers GFX HQD active/priority/base/offset/read/write/dequeue/mapped/manager/control/status fields, CE poll/offset/read/write fields, MQD base, RB write-pointer poll addresses, and repeated CE/PFP/ME header dump entries.

The golden-setting arrays are `static const struct soc15_reg_golden` tables. Each entry is a register, mask, and programmed value consumed later by common SOC15 golden-register programming helpers. Covered regular GC tables include `golden_settings_gc_10_1`, `golden_settings_gc_10_1_1`, `golden_settings_gc_10_1_2`, `golden_settings_gc_10_3`, `golden_settings_gc_10_3_2`, `golden_settings_gc_10_3_vangogh`, `golden_settings_gc_10_3_3`, `golden_settings_gc_10_3_4`, `golden_settings_gc_10_3_5`, `golden_settings_gc_10_0_cyan_skillfish`, `golden_settings_gc_10_3_6`, and `golden_settings_gc_10_3_7`. Empty placeholder tables are present for `golden_settings_gc_10_0_nv10`, `golden_settings_gc_10_1_nv14`, `golden_settings_gc_10_1_2_nv12`, and `golden_settings_gc_10_3_sienna_cichlid`.

The large RLC SPM golden tables are `golden_settings_gc_rlc_spm_10_0_nv10`, `golden_settings_gc_rlc_spm_10_1_nv14`, and `golden_settings_gc_rlc_spm_10_1_2_nv12`. These tables repeatedly program `mmGRBM_GFX_INDEX` to select broadcast or per-shader-engine contexts, then write RLC SPM global and per-SE sample-delay, mux-select, sample-skew, mux-skew, and deserializer-start-skew registers. They are long because each counter/mux lane gets explicit calibration values and selected SEs are addressed separately.

`DEFAULT_SH_MEM_CONFIG` defines the default shader memory mode later used for compute/graphics queue setup: 64-bit addressing, unaligned alignment mode, all retry mode, and an initial instruction prefetch value of `3`. `CYAN_SKILLFISH_GB_ADDR_CONFIG_GOLDEN` is a temporary hard-coded GB address config value with a TODO noting that the golden value is pending.

The forward declarations at the end expose the major implementation areas that later chunks define: ring/IRQ/GDS/RLC/MQD function-table setup, CU discovery, clock counter reads, SE/SH selection, active WGP bitmap discovery, RLC backdoor autoload buffer lifecycle and enable/wait paths, CE/DE/frame-control packet emission, disabled shader-array discovery, PBB mode programming, power brake sequencing, TLB invalidation, SPM VMID update, and power-gating state changes.

## Control Flow And Runtime Use

There is very little runtime control flow in this chunk. The active behavior is compile-time and link-time setup:

1. Kernel and AMDGPU headers provide register definitions, bitfield macros, firmware APIs, SOC15 helpers, and local driver types.
2. `MODULE_FIRMWARE()` statements make firmware names visible to the kernel build/module metadata.
3. Static register lists and golden-setting tables are compiled into read-only data.
4. Later functions, outside this chunk, select the appropriate table according to `adev->asic_type`, IP version, or family-specific conditions and apply entries through SOC15 masked-register writes.
5. Debug and reset paths later reference the `amdgpu_hwip_reg_entry` lists to collect hardware state for diagnostics.

The regular golden tables configure clocks, cache/GL2 behavior, shader and geometry frontend settings, DB/PA/SPI/SQ/TA/TCP/UTCL1 controls, performance counter select defaults, and known workaround registers. Some entries are explicitly documented as hang fixes, such as `mmLDS_CONFIG` workarounds for Navy Flounder and Vangogh.

The RLC SPM tables are ordered register-programming scripts. Their repeated `mmGRBM_GFX_INDEX` writes matter because following indirect RLC SPM writes target global broadcast, SE0, SE1, or all-SE contexts depending on the selected value. A later consumer must preserve ordering; these are not independent key-value settings that can be freely sorted.

The declarations near lines 3677-3706 signal the subsequent control-flow areas but do not define them in this chunk. For example, RLC autoload buffer initialization and `gfx_v10_0_wait_for_rlc_autoload_complete()` are declared here, but allocation, polling, timeout, and error handling are in later code.

## State And Persistence Behavior

All tables and constants in this chunk are static driver data. They live in the kernel module or built-in kernel image, are read-only after load, and have no direct allocation, I/O, locking, or persistence side effects.

Firmware declarations are persistent only as module metadata and as build/runtime dependency hints. They do not load firmware by themselves. Later firmware loading state will reside in `adev` and related firmware/RLC/CP structures.

The golden tables encode persistent hardware policy for each supported ASIC family. Applying them later mutates device registers, not the tables. Because hardware registers retain values only while powered/reset state allows, these settings must be reapplied during initialization and relevant resume/reset paths by code outside this chunk.

The debug register lists also do not store snapshots. They describe what later diagnostic paths should read. Captured values, if any, are stored by the caller or emitted through driver diagnostics elsewhere.

`DEFAULT_SH_MEM_CONFIG` and the shader-array/PBB/register field macros are stateless compile-time constants. Their persistence risk is semantic: changing them changes the default state later programmed into queue or graphics hardware.

## Dependencies And Integration Points

This chunk is tightly coupled to generated register headers under `gc/`, `smuio/`, and `ivsrcid/gfx/`. The register names, offsets, base indices, masks, and shifts must match the GFX10 hardware generation. Several locally defined aliases exist because the generated headers are incomplete or because ASIC-specific offsets differ from the base GC 10.1 definitions.

The SOC15 integration point is central. `SOC15_REG_ENTRY_STR()` converts register names into debug-readable hardware IP register descriptors. `SOC15_REG_GOLDEN_VALUE()` converts register/mask/value triples into golden-setting data consumed by shared SOC15 code.

The firmware integration point is Linux firmware loading via AMDGPU. Later code chooses blob prefixes and requests the files declared in this chunk. Mismatches between `MODULE_FIRMWARE()` declarations and actual runtime firmware names can cause missing firmware packaging or request failures.

The debug integration point is AMDGPU device-state capture. The three `amdgpu_hwip_reg_entry` lists are intended for general GC, compute queue, and graphics queue diagnostics. They include repeated header-dump registers because repeated reads can expose successive dump words through the same register address.

The hardware bring-up integration point is later GFX10 initialization code, which selects golden settings by ASIC. Tables for Navi10/Navi14/Navi12 and GC 10.3 variants must align with the ASIC switch logic outside this chunk. Placeholder empty tables indicate that some ASIC-specific golden programming was pending or intentionally delegated to other table combinations.

The RLC SPM tables integrate with RLC performance monitoring, SPM sampling, and shader-engine selection. Their use depends on `GRBM_GFX_INDEX` selection semantics and RLC SPM indirect address/data register behavior.

The forward-declared functions integrate with the broader AMDGPU IP-block model: ring function tables for scheduler/ring operations, IRQ callbacks, GDS initialization, RLC function hooks, MQD programming, CU-info reporting, power management, VM/TLB invalidation, and IP-block power-gating callbacks.

## Risks And Edge Cases

The biggest risk in this chunk is table drift. Golden settings are hardware workarounds and tuning values; changing a mask or value can cause hangs, degraded performance, bad cache behavior, broken shader/geometry behavior, or regressions limited to a single ASIC family.

The RLC SPM tables are especially fragile because ordering is meaningful. Reordering entries around `mmGRBM_GFX_INDEX`, dropping a broadcast reset, or using an incorrect SE selector can silently program the wrong shader engine or leave calibration asymmetric.

Locally defined register offsets can diverge from generated headers or hardware documentation. They are useful when generated headers lag, but they bypass the stronger consistency provided by generated register metadata.

Firmware declarations must track runtime firmware naming exactly. A new ASIC table without matching firmware declarations, or renamed firmware without updating `MODULE_FIRMWARE()`, can break distribution packaging even if the source compiles.

Placeholder golden-setting arrays are easy to misinterpret. Empty tables such as `golden_settings_gc_10_0_nv10` or `golden_settings_gc_10_3_sienna_cichlid` do not mean the ASIC needs no programming; later selection logic may combine common tables, rely on firmware, or still need future fill-in.

Debug register lists contain repeated entries for header-dump registers and one apparent duplicate `mmCP_RB2_WPTR`. These may be intentional for successive readback semantics, but generic duplicate-removal refactors would be risky without checking the hardware read behavior.

The chunk uses ASIC names in symbol names, including mixed-case `Sienna_Cichlid` local register names. Style-only normalization could break references or obscure which values are ASIC-specific overrides.

The forward declarations create dependency pressure between later code sections. Signature changes must update declarations and all function-table assignments consistently, especially for callbacks like power-gating state changes and TLB invalidation packet emission.

## Test Signals

Build coverage should compile this file with the relevant AMDGPU configuration enabled and with warnings treated seriously enough to catch stale forward declarations, missing register symbols, or invalid firmware macro use.

ASIC-specific smoke tests should boot or initialize representative GFX10 devices: Navi10, Navi12, Navi14, Sienna Cichlid/Navy Flounder class GC 10.3 parts, Vangogh, Cyan Skillfish, and GC 10.3.6/10.3.7 if available. The expected signal is successful firmware load, GFX IP bring-up, ring test, and no early GPU hang.

Golden-setting validation should compare applied register writes against expected masks and values for each selected ASIC path. This is most valuable around `mmLDS_CONFIG`, `mmGB_ADDR_CONFIG`, GL2 address masks, clock-gating controls, `mmSQ_CONFIG`, and Vangogh/Sienna-specific aliases.

RLC SPM validation should confirm that later code applies the RLC SPM tables in order and that SPM sampling works per shader engine. Failures may show as bad counter data rather than immediate boot failure.

Debug-dump tests should exercise GPU reset/hang capture paths and verify the general GC, compute HQD, and graphics queue register lists produce sane output without invalid register access on supported ASICs.

Firmware packaging tests should verify every declared firmware name exists in the target firmware package or is intentionally optional for the built kernel/device matrix.

Power-management and reset tests should include suspend/resume, runtime power transitions, GPU reset, and power-gating toggles, because the static golden settings from this chunk must be replayed correctly by later runtime paths after hardware loses state.

### subset-b-001331: lines 3707-10239

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_0.c lines 3707-10239

## Scope

This chunk is the implementation-heavy back half of the AMDGPU GFX10 IP block. It covers KIQ PM4 command construction, golden-register programming, firmware loading, RLC/MEC/CP initialization, queue MQD creation, ring bring-up and reset, power and clock gating, PM4 packet emitters, interrupt routing, diagnostic IP dumps, CU/RB topology discovery, and final function-table registration for `gfx_v10_0_ip_block`.

The earlier chunk defines many tables, register lists, packet helpers, constants, and some forward declarations used here. This chunk contains the operational glue that wires GFX10 ASIC variants into the DRM/AMDGPU IP lifecycle.

## Purpose

The code initializes and manages the GFX10 graphics/compute command processor stack for Navi/Cyan Skillfish/Vangogh/Sienna Cichlid era ASICs. It converts generic AMDGPU concepts such as IP block callbacks, rings, IRQ sources, MQDs, fences, VM flushes, and power states into GFX10-specific register programming and PM4 packets.

Major responsibilities include:

- Building KIQ packets to map, unmap, query, preempt, reset, and invalidate queues.
- Loading PFP, ME, CE, RLC, MEC, and optional MEC2 firmware through direct, PSP autoload, or RLC backdoor autoload paths.
- Allocating persistent kernel BOs for clear-state blocks, firmware images, RLC autoload buffers, MEC EOP memory, KIQ/MQD state, cleaner shader state, and IP dump snapshots.
- Discovering hardware topology from fuse/VBIOS registers, including shader engines, shader arrays, WGP/CU active masks, render backend masks, TCC disable masks, and disabled SAs.
- Initializing graphics and compute rings, their doorbells, writeback pointers, EOP buffers, ring buffer registers, and queue descriptors.
- Implementing `amd_ip_funcs`, `amdgpu_ring_funcs`, `amdgpu_irq_src_funcs`, `amdgpu_rlc_funcs`, and MQD callbacks consumed by the common AMDGPU core.
- Managing runtime controls such as GFXOFF, CGCG/CGLS/MGCG/MGLS/FGCG clock gating, Vangogh-style power gating, GUI idle interrupts, and RLC safe mode.
- Emitting PM4 commands for IB submission, fences, context control, VM/TLB flushes, HDP flushes, GDS switches, preemption, register reads/writes, memory synchronization, cleaner shader execution, and frame control.
- Handling command processor interrupts, illegal instruction/register/opcode faults, per-queue fence processing, queue reset recovery, soft reset, suspend/resume, and diagnostic dump/print paths.

## Important APIs And Types

`gfx_v10_0_ip_block` is the exported block descriptor. Its `amd_ip_funcs` table names the block `gfx_v10_0` and supplies early/late/software/hardware init and fini callbacks, suspend/resume, idle/wait/reset handlers, clock/power gating handlers, and IP dump/print hooks.

`gfx_v10_0_early_init()` is the first GFX10 wiring point. It assigns `adev->gfx.funcs`, sets the GFX ring count by GC IP version, computes compute ring count from `amdgpu_gfx_get_num_kcq()`, installs KIQ PM4 callbacks, ring callbacks, IRQ callbacks, GDS defaults, RLC callbacks, MQD callbacks, RLCG access control registers, and requests firmware.

`gfx_v10_0_sw_init()` allocates and configures software-visible runtime state: delayed profile work, ME/MEC topology, cleaner shader support gated by firmware versions, IRQ IDs, RLC clear-state BOs, MEC HPD/EOP and direct-load firmware BOs, graphics and compute ring objects, supported reset masks, KIQ state, MQD software state, optional RLC autoload buffers, CE RAM size, early GPU config, IP dump buffers, and GFX sysfs state.

`gfx_v10_0_hw_init()` performs hardware bring-up: golden registers, cleaner shader upload, optional SMU firmware loading and GPA override for direct firmware load, GRBM CAM remapping, constants/topology initialization, RLC resume, TCP harvest repair for older Navi variants, CP resume, PBB programming for Sienna Cichlid, and power brake setup for GFX10.3 non-SR-IOV devices.

`gfx_v10_0_hw_fini()`, `gfx_v10_0_suspend()`, and `gfx_v10_0_resume()` implement shutdown and resume around queue disables, CP halt, IRQ release, GUI idle interrupt disable, Vangogh power-gating workaround, SR-IOV-specific limitations, and delayed work cancellation.

The ring function tables split behavior by queue type:

- `gfx_v10_0_ring_funcs_gfx` handles graphics rings with secure submission, context control, switch-buffer, preemption, metadata save/restore, GFX queue reset, and cleaner shader emission.
- `gfx_v10_0_ring_funcs_compute` handles compute rings with compute IB emission, compute queue reset, GDS/HDP/VM/fence operations, and cleaner shader emission.
- `gfx_v10_0_ring_funcs_kiq` handles the kernel interface queue with compute-style pointers, KIQ fence emission, KIQ register read/write helpers, and KIQ-safe HDP/register wait helpers.

The KIQ PM4 table `gfx_v10_0_kiq_pm4_funcs` provides queue management packet builders: `gfx10_kiq_set_resources()`, `gfx10_kiq_map_queues()`, `gfx10_kiq_unmap_queues()`, `gfx10_kiq_query_status()`, `gfx10_kiq_invalidate_tlbs()`, and `gfx_v10_0_kiq_reset_hw_queue()`. Their size fields are consumed by common KIQ helpers before ring allocation.

The RLC function tables are `gfx_v10_0_rlc_funcs` and `gfx_v10_0_rlc_funcs_sriov`. Both expose safe mode, clear-state, stop/reset/start, resume, and SPM VMID update operations; the SR-IOV table additionally exposes `is_rlcg_access_range`.

The MQD callbacks initialize `struct v10_gfx_mqd` and `struct v10_compute_mqd`. Graphics MQDs program GFX HQD pointers, VMID, priority, quantum, ring buffer base/control, read/write pointer writeback addresses, doorbell control, and active state. Compute MQDs program EOP memory, PQ doorbells, queue base/control, MQD base, VMID, persistent state, IB control, pipe/queue priorities, tunneling, KMD queue marking, and active state.

Interrupt source function tables cover EOP, privileged register fault, bad opcode fault, privileged instruction fault, and KIQ generic interrupt processing. The handlers decode `entry->ring_id` into ME/pipe/queue and route to `amdgpu_fence_process()` or `drm_sched_fault()`.

## Control Flow

Initialization is staged through the AMDGPU IP block lifecycle. `early_init` installs function pointers and requests firmware. `sw_init` sizes queues, allocates BO-backed state, registers IRQ IDs, creates rings, allocates KIQ/MQD resources, and initializes software-only helper state. `hw_init` programs device registers, loads or waits for microcode, initializes RLC and CP, maps queues, tests rings, and applies ASIC-specific workarounds. `late_init` enables fault IRQs after the block is otherwise ready.

Firmware flow depends on `adev->firmware.load_type`. Direct loading copies CP firmware into GTT BOs, invalidates instruction caches, programs instruction cache base registers, writes jump-table words through CP HYP or MEC ucode registers, and records firmware versions in address registers. PSP autoload waits for RLC autoload completion and then initializes clear state and RLC SRM. RLC backdoor autoload parses the PSP TOC into `rlc_autoload_info`, allocates a consolidated autoload BO, copies TOC, SDMA, PFP, CE, ME, RLC, and MEC ucode into TOC-defined offsets, programs RLC bootload address/size, waits for bootload completion, then programs CP instruction cache bases to the autoload BO offsets.

RLC resume first handles PSP/autoload cases, then initializes the clear-state block, sets SPM VMID, optionally enables SRM, and starts RLC. Direct and backdoor paths explicitly stop RLC, disable RLC clock/power gating controls during loading, load ucode, initialize CSB, update SPM VMID, start RLC, and wait for autoload if needed.

CP resume disables GUI idle interrupts on discrete devices, loads direct firmware if needed, initializes KIQ, enables compute queues through KCQ, brings up graphics rings through either legacy CP RB register programming or async KGQ MQD mapping, then tests every graphics and compute ring. Graphics ring resume programs CP RB registers, ring buffer sizes, write pointers, rptr/wptr writeback addresses, base addresses, active bits, doorbell controls, and then emits the clear-state preamble. Compute queue resume initializes per-ring MQDs and maps queues through common KIQ enable helpers.

Queue reset uses KIQ as the recovery control path. Graphics queue reset writes `CP_VMID_RESET`, waits for MQD `cp_gfx_hqd_active` to clear, waits for reset register clear, reinitializes/restores the KGQ MQD, maps the queue again, tests KIQ, and completes the reset helper. Compute queue reset emits KIQ `UNMAP_QUEUES` with `RESET_QUEUES`, waits in RLC safe mode for `CP_HQD_ACTIVE` to clear, restores and clears the KCQ ring, remaps through KIQ, tests KIQ, and completes the reset helper.

IB submission emits different PM4 packet streams for graphics and compute. Graphics chooses `INDIRECT_BUFFER` or `INDIRECT_BUFFER_CNST`, adds VMID, optional preemption control, and DE metadata emission when MCBP preemption is active. Compute can first reset GDS max wave ID, then emits `INDIRECT_BUFFER` with valid bit, length, and VMID. Fences use `RELEASE_MEM` for normal rings and `WRITE_DATA` plus optional `CPC_INT_STATUS` interrupt trigger for KIQ. VM flush delegates to GMC TLB flush emission and synchronizes PFP to ME on graphics rings.

Clock and power management enter RLC safe mode before mutating sensitive registers. Clock gating enable runs fine-grain, medium-grain, 3D, and coarse-grain updates in enable order and applies a Navi1x medium-grain workaround; disable reverses that order. Power gating is mostly `amdgpu_gfx_off_ctrl()` for many ASICs, while Vangogh-like devices also program `RLC_PG_CNTL` and a CGPG hysteresis value through `gfx_v10_cntl_pg()`.

## State And Persistence Behavior

Most durable state lives under `struct amdgpu_device`, especially `adev->gfx`, `adev->gds`, `adev->mqds`, `adev->firmware`, `adev->psp`, and ring-local fields. This chunk mutates firmware pointers and versions, firmware BO addresses, RLC clear-state/autoload BOs, KIQ/MEC/GFX MQD backups, ring doorbell indices, writeback addresses, scheduler readiness, supported reset masks, IP dump arrays, GDS size/limits, CU/RB/TCC masks, and power/clock flags.

Several BO allocations persist across the SW lifetime until `sw_fini`: RLC clear-state and CP table BOs, MEC HPD/EOP BO, direct-load PFP/CE/ME/MEC firmware BOs, KIQ/MQD BOs owned by common helpers, RLC TOC/autoload BOs for backdoor autoload, cleaner shader BOs, and IP dump arrays. `sw_fini` tears these down and releases firmware blobs in the reverse broad order.

MQD backup arrays are important reset persistence. KGQ, KCQ, and KIQ initialization copy freshly initialized MQDs into backup memory when not in reset/suspend. Reset and restore paths copy backup MQDs back into MMIO-visible MQD memory, reset software/hardware write pointers to zero, clear ring buffers, and remap queues. This preserves a clean queue descriptor template across GPU resets without reconstructing every field from scratch.

Register state is partly persistent until reset and partly reprogrammed on every resume. Golden registers, GRBM CAM remapping, SH memory apertures, GDS VMID access, trap config, RLC safe mode, clock gating, power gating, CP ring registers, doorbell ranges, CP instruction cache bases, and RLC CSB addresses are all restored during `hw_init`/resume.

Firmware-derived state is version-sensitive. `gfx_v10_0_check_fw_write_wait()` sets `adev->gfx.cp_fw_write_wait`, which selects whether PM4 `WAIT_REG_MEM` can perform write-wait sequences or whether the generic helper must be used. Cleaner shader enablement is also gated by per-IP firmware version thresholds.

SR-IOV changes state behavior. VF paths skip golden register programming, often skip RLC firmware loading, avoid some power/clock controls, use SR-IOV RLC funcs for RLCG access, initialize CSB without direct RLC control in some paths, and avoid clearing KIQ position during hardware fini because that can hang peer guests.

## Dependencies And Integration Points

This code is tightly integrated with the common AMDGPU subsystems:

- Ring core: `amdgpu_ring_init`, `amdgpu_ring_alloc`, `amdgpu_ring_write`, `amdgpu_ring_commit`, `amdgpu_ring_test_helper`, `amdgpu_ring_clear_ring`, and ring function tables.
- Firmware core: `amdgpu_ucode_request`, `request_firmware`, CP/RLC firmware header parsing, `amdgpu_gfx_cp_init_microcode`, `amdgpu_gfx_rlc_init_microcode`, and PSP TOC/autoload state.
- Memory manager: `amdgpu_bo_create_reserved`, `amdgpu_bo_free_kernel`, `amdgpu_bo_gpu_offset`, GTT-domain firmware/autoload/EOP buffers, and writeback memory from `amdgpu_device_wb_get`.
- GFX common helpers: queue acquisition, KIQ/KCQ/KGQ enable/disable, MQD SW init/fini, reset helpers, cleaner shader helpers, sysfs, CU disable parsing, HDP flush mask discovery, RLC safe mode wrappers, GFXOFF control, profile/isolation begin/end hooks, and KFD VMID ranges.
- GMC/NBIO/SMU/PSP/SDMA integration: TLB flush emission, HDP flush request/done offsets, SMU firmware direct-load sequencing, PSP TOC data, SDMA firmware blobs for backdoor autoload, and SMUIO timestamp counter registers.
- DRM scheduler and IRQ layers: `amdgpu_irq_add_id`, `amdgpu_irq_get/put`, `amdgpu_fence_process`, `dma_fence_wait_timeout`, and `drm_sched_fault`.
- Register access infrastructure: SOC15 register macros, KIQ/no-KIQ register accessors, `nv_grbm_select`, `srbm_mutex`, `grbm_idx_mutex`, and per-IP-version register aliases such as Sienna Cichlid and Vangogh variants.

Externally visible integration points are the GFX and compute rings used by command submission, KFD compute queue ownership, sysfs/debug facilities, GPU reset recovery, runtime power management, firmware loading policy, and debug dumps printed through DRM printers.

## Risks And Edge Cases

Firmware loading is fragile. Missing required PFP/ME/CE/MEC firmware returns errors; MEC2 is optional. RLC firmware is deliberately not validated in one path because some deployed firmware has incorrect size headers. Direct-load paths depend on correctly sized BOs, GTT visibility, instruction cache invalidation completion, jump-table offsets, and SMU firmware being loaded before RLC.

Backdoor autoload has several TOC assumptions. It trusts PSP TOC size and entries enough to copy them into a BO, aligns CP firmware offsets for some IDs, uses global `rlc_autoload_info`, and computes total size from TOC sizes and last offset. Bad TOC data, missing SDMA firmware, or mismatched firmware sizes can misplace ucode or leave zero-padded regions that hardware later consumes.

Many waits are bounded by `adev->usec_timeout` or fixed 50 ms cache-invalidation loops. Timeout failures leave partially initialized hardware and typically return `-ETIMEDOUT` or `-EINVAL`. Ring tests and CP/RLC status checks are therefore important before accepting the block as usable.

Queue reset and preemption depend on a functioning KIQ. If KIQ PM4 callbacks are absent, KIQ ring allocation fails, KIQ ring tests fail, or KIQ cannot submit while another reset is in progress, per-queue reset returns errors and may require broader GPU reset.

Pointer and alignment constraints are enforced with `BUG_ON()` in several PM4 emitters, including IB dword alignment, fence address alignment, and memory wait dword alignment. Bad callers can crash the kernel rather than receive a recoverable error.

ASIC version branching is broad and easy to regress. Many registers differ for GFX10.1, GFX10.3, Sienna Cichlid, Vangogh, Cyan Skillfish, and SR-IOV. Adding or moving IP versions requires auditing golden settings, queue topology, GFX ring count, firmware thresholds, clock/power controls, timestamp registers, CAM remapping, disabled SA handling, and register aliases.

The interrupt setup for compute notes that AMDGPU controls only the first MEC while other pipes can be owned by KFD. Enabling, disabling, or interpreting per-pipe/per-queue interrupts incorrectly can lose fence signals or incorrectly fault unrelated queues.

Clock and power gating writes occur around RLC safe mode and GFXOFF control. Incorrect ordering can race active command submission, GUI idle interrupts, or RLC firmware state. Vangogh has an explicit suspend workaround, indicating hardware/SMU interaction sensitivity.

IP dump allocation failures are non-fatal but reduce debug visibility. Dump routines guard null arrays, but partial allocation means later diagnostics may omit core, compute queue, or graphics queue state.

## Test Signals

Bring-up signals include successful `early_init`, `sw_init`, `hw_init`, and `late_init` with no firmware request failures, BO allocation failures, RLC autoload timeout, instruction cache invalidation timeout, ring init failures, or sysfs init failures.

Runtime ring tests are direct health checks. `gfx_v10_0_ring_test_ring()` writes `0xDEADBEEF` through PM4 to `SCRATCH_REG0`; `gfx_v10_0_ring_test_ib()` writes `0xDEADBEEF` to a writeback slot through an IB and waits on a DMA fence. `gfx_v10_0_cp_resume()` runs `amdgpu_ring_test_helper()` for every GFX and compute ring after queue mapping.

Firmware-path tests should cover direct load, PSP autoload, and RLC backdoor autoload where supported. Useful signals are CP/RLC status reaching idle, `RLC_RLCS_BOOTLOAD_STATUS.BOOTLOAD_COMPLETE`, successful cache invalidation bits, nonzero firmware BO GPU addresses, and no "CP firmware version too old" warning on expected modern firmware.

Reset tests should trigger per-queue KGQ and KCQ resets and verify KIQ unmap/map packets complete, `CP_HQD_ACTIVE` or MQD active state clears, queues remap, KIQ tests pass, and subsequent submissions complete without full GPU reset.

IRQ tests should verify EOP fence processing for graphics rings and compute rings, KIQ generic interrupt fence processing, and scheduler faults on illegal register, bad opcode, and privileged instruction command streams.

Power-management tests should suspend/resume and toggle GFXOFF/clock-gating states on representative GFX10.1 and GFX10.3 ASICs, including Vangogh-style power gating and SR-IOV VFs. Expected signals include no SMU suspend failure, no queue hang after resume, GUI idle interrupts disabled on fini, and clock-gating state bits matching requested flags.

Topology tests should compare discovered CU, WGP, RB, TCC, disabled SA, and GDS values against ASIC expectations and harvested configurations. Changes to `gfx_v10_0_get_cu_info()`, `gfx_v10_0_setup_rb()`, or disabled-SA handling should be validated on partially harvested devices.

Diagnostic tests should call the IP dump and print paths after a hang or reset and confirm core registers plus per-MEC/per-pipe/per-queue compute and graphics registers are captured without null dereferences or stale GRBM selections.
