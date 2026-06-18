# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_default.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002496`: lines 1-2930, `Docs/researches/chunks/subset-b-002496_research.md`
- `subset-b-002497`: lines 2931-5857, `Docs/researches/chunks/subset-b-002497_research.md`
- `subset-b-002498`: lines 5858-6114, `Docs/researches/chunks/subset-b-002498_research.md`

## Chunk Research

### subset-b-002496: lines 1-2930

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_default.h lines 1-2930

## Purpose

This chunk is generated AMD Graphics Core 11.0.0 register reset/default metadata. It has no executable C logic; it publishes preprocessor constants named `reg..._DEFAULT` for hardware register reset values used by AMDGPU GC, SDMA, GFXHUB, MES, queue, VM, shader, render, and PF/VF setup code.

The requested range is the first 2,930 lines of a 6,114-line header. It starts at the file license and include guard, then covers these generated address blocks:

- Full `gc_sdma0_sdma0dec` and `gc_sdma0_sdma1dec` SDMA engine default families, including engine control/status, UTCL1, error, doorbell, queue, indirect-buffer, preemption, and mid-command registers for queues 0-7.
- GRBM, CP, PA, SQ, SHS/SPI, texture, GDS, RB, GCEA, PMM, UTCL1, GCVM shared/PF/VC, shader-program, graphics/compute queue, TCP, GDS partition, render-context, PF/VF, RMI, DIDT, SPI debug, and UTCL1 PF-only default blocks.
- The final visible line stops inside `gc_pfonly_utcl1dec` at `regGCRD_SA0_TARGETS_DISABLE_DEFAULT`; subsequent default blocks are outside this chunk and must be reconciled by neighboring chunk reports.

The chunk contains 2,793 `#define` lines. Most values are zero reset states; repeated non-zero defaults encode known hardware reset programming such as SDMA queue controls, VM context enables, L2 invalidation request defaults, MQD/HQD queue control defaults, GDS VMID sizes, raster configuration, RMI/UTC settings, DIDT EDC patterns, and PF/VF raster/binning defaults.

Although this source tree is under a `ceph-client` mirror, this file is AMDGPU kernel-driver hardware metadata and does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, includes, locks, allocation paths, or direct register accesses in this chunk. The public interface is the generated macro namespace:

- `reg<REGISTER>_DEFAULT`: 32-bit numeric default/reset value for an MMIO register or register-backed queue/MQD field.
- Address-block comments such as `// addressBlock: gc_cpphqddec`: generated grouping hints that align defaults with matching offset and field-mask headers.

The macros are normally paired with:

- Register offsets from `gc_11_0_0_offset.h`, such as `regCP_HQD_PQ_CONTROL`, `regGCVM_L2_CNTL3`, `regSDMA0_QUEUE0_RB_CNTL`, and `regGCMC_VM_MX_L1_TLB_CNTL`.
- Bitfield definitions from `gc_11_0_0_sh_mask.h`, such as `CP_HQD_PQ_CONTROL`, `CP_GFX_HQD_CNTL`, `GCVM_L2_CNTL3`, and `CP_HQD_PERSISTENT_STATE` fields.
- AMDGPU helper macros and accessors including `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15_PREREG`, and SOC15 register offset helpers.

High-value macro families in this range include:

- `regSDMA0_*_DEFAULT` and `regSDMA1_*_DEFAULT`: reset defaults for both SDMA engines. Queue defaults are repeated for queues 0-7; representative values include ring-buffer control `0x00040800`, indirect-buffer control `0x00000100`, context status `0x00000804`, AQL control `0x00004000`, and dummy register `0x0000000f`.
- `regCP_GFX_*_DEFAULT`: graphics queue MQD/HQD defaults, including `regCP_GFX_MQD_CONTROL_DEFAULT`, `regCP_GFX_HQD_VMID_DEFAULT`, `regCP_GFX_HQD_QUEUE_PRIORITY_DEFAULT`, `regCP_GFX_HQD_QUANTUM_DEFAULT`, `regCP_GFX_HQD_CNTL_DEFAULT`, `regCP_RB_DOORBELL_CONTROL_DEFAULT`, and pointer defaults.
- `regCP_HQD_*_DEFAULT`: compute/MES queue defaults, including `regCP_HQD_EOP_CONTROL_DEFAULT`, `regCP_HQD_PQ_CONTROL_DEFAULT`, `regCP_HQD_PERSISTENT_STATE_DEFAULT`, `regCP_HQD_IB_CONTROL_DEFAULT`, `regCP_HQD_EOP_RPTR_DEFAULT`, `regCP_HQD_EOP_WPTR_DEFAULT`, and HQ scheduler/status defaults.
- `regGCVM_*_DEFAULT` and `regGCMC_*_DEFAULT`: graphics VM and cache defaults for contexts 0-15, invalidation engines 0-17, page-table base/start/end address registers, per-PF/VF PTE cache fragment sizes, L2 cache controls, fault/default-page addresses, and system aperture/AGP registers.
- `regSPI_SHADER_*_DEFAULT` and `regCOMPUTE_*_DEFAULT`: shader program address/resource/user-data defaults for PS, GS/ESGS, HS/LSHS, compute, trap, accumulators, and request-control registers.
- `regDB_*`, `regPA_SC_*`, `regPA_CL_*`, `regCB_*`, and `regVGT_*`: render-context defaults for depth/stencil, scissor/viewport state, rasterization, VRS, primitive restart, color targets 0-7, DCC base extensions, blend constants, and context metadata.
- PF/VF and PF-only defaults such as `regCP_MEC_CNTL_DEFAULT`, `regCP_ME_CNTL_DEFAULT`, `regPA_SC_VRS_SURFACE_CNTL_DEFAULT`, `regRLC_SAFE_MODE_DEFAULT`, `regSQ_RUNTIME_CONFIG_DEFAULT`, `regDIDT_*_DEFAULT`, and `regUTCL1_*_DEFAULT`.

## Control Flow

This header has no local control flow. It affects runtime behavior when included code uses a generated default as a baseline, modifies selected fields, then writes the result into a hardware register or queue descriptor.

The clearest queue initialization flow is in GFX/MES code:

1. GFX v11 graphics MQD initialization starts from defaults such as `regCP_GFX_MQD_CONTROL_DEFAULT`, `regCP_GFX_HQD_VMID_DEFAULT`, `regCP_GFX_HQD_QUANTUM_DEFAULT`, `regCP_GFX_HQD_CNTL_DEFAULT`, and `regCP_RB_DOORBELL_CONTROL_DEFAULT`.
2. The driver applies runtime queue properties with `REG_SET_FIELD`, including VMID, privilege/cache policy, queue priority, ring-buffer size, TMZ, non-privileged mode, and doorbell offset/enabling.
3. The initialized MQD is copied to GPU-visible memory and restored from backup on reset/suspend paths.

Compute and MES queue setup follows the same pattern:

1. The driver zeros the MQD, fills fixed software fields, then derives EOP, MQD, HQD, read-pointer, write-pointer, and queue-base addresses from ring or queue properties.
2. It starts with defaults such as `regCP_HQD_EOP_CONTROL_DEFAULT`, `regCP_MQD_CONTROL_DEFAULT`, `regCP_HQD_PQ_CONTROL_DEFAULT`, `regCP_HQD_PQ_DOORBELL_CONTROL_DEFAULT`, `regCP_HQD_PERSISTENT_STATE_DEFAULT`, `regCP_HQD_IB_CONTROL_DEFAULT`, `regCP_HQD_IQ_TIMER_DEFAULT`, and `regCP_HQD_QUANTUM_DEFAULT`.
3. It overlays fields for queue size, RPTR block size, unordered/tunneled dispatch, KMD/private state, TMZ, doorbells, preload size, and minimum IB availability before activating the queue.

The VM/cache programming path uses the same default-as-template model:

1. GFXHUB initialization programs AGP/system-aperture/fault address registers from `adev->gmc`, scratch memory, and dummy page addresses.
2. It reads or starts from GCVM defaults, especially `regGCVM_L2_CNTL3_DEFAULT`, `regGCVM_L2_CNTL4_DEFAULT`, and `regGCVM_L2_CNTL5_DEFAULT`.
3. It sets cache-bank selection, fragment sizes, request mode, and small-page fragment fields before writing back with SOC15 helpers.

SDMA defaults in this chunk are also data inputs for ring/MQD programming. In this tree, SDMA v6 includes `gc_11_0_0_default.h`, and later SDMA code for newer generations mirrors some queue defaults as literals with comments referencing `regSDMA0_QUEUE0_RB_AQL_CNTL_DEFAULT` and `regSDMA0_QUEUE0_DUMMY_REG_DEFAULT`.

Render, shader, PF/VF, RMI, DIDT, and UTCL1 defaults do not impose ordering themselves. Actual sequencing is provided by surrounding GFX initialization, context programming, reset, power-management, SR-IOV PF/VF, KFD, and firmware/MES paths.

## State And Persistence Behavior

The header stores no software state and persists nothing on its own. It describes hardware reset/default state and default queue-descriptor field values.

Runtime persistence comes from consumers:

- MQD/HQD defaults become persistent GPU-visible queue descriptors in memory. GFX queue setup backs up MQDs in `adev->gfx.me.mqd_backup` and restores them across reset/suspend paths when appropriate.
- Doorbell defaults start disabled and are converted into active doorbell programming only when runtime queue properties request doorbells.
- VM defaults become live GCVM/GCMC MMIO state. Context enablement, page-table base/start/end, invalidation requests, fault addresses, and cache controls persist until GPU reset, suspend/resume reprogramming, VM hub reinitialization, or SR-IOV PF intervention changes them.
- Shader and render-context defaults represent reset state for graphics pipeline context registers. Command submission and context switching replace these defaults with per-draw, per-dispatch, or per-context state.
- SDMA queue defaults represent inactive queues with zeroed bases, pointers, doorbells, and CSA addresses until ring setup programs real buffers and writeback addresses.
- PF/VF-only defaults separate virtualization surfaces. VF-accessible defaults and PF-only defaults are not interchangeable; SR-IOV paths may leave some PF-only registers programmed by the host/PF rather than by guest driver code.

Most defaults are not evidence that a field is safe to rewrite at arbitrary times. Register side effects, read-only status, write-one-to-clear behavior, firmware ownership, and reserved-bit rules are defined by hardware documentation and by the associated driver sequencing code, not by this default header.

## Dependencies And Integration Points

This chunk must remain synchronized with AMD's generated GC 11.0.0 register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h` for matching register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h` for matching field shifts and masks.
- SOC15/GFX/MES/GFXHUB register access infrastructure that consumes these macros through `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15`.

Direct include sites observed in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v12_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v12_1.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v6_0.c`

There are also closely related local copies of defaults in `gfx_v11_0.c`, `gfx_v12_0.c`, `gfx_v12_1.c`, and GFXHUB/MMHUB files. Those copies show the intended runtime use of this style of macro even where the generated header is not directly included in that translation unit.

Concrete consumers and behavior tied to macros in this chunk:

- `gfx_v11_0_gfx_mqd_init()` uses graphics queue defaults as baselines for MQD control, HQD VMID, quantum, HQD control, doorbell control, and read-pointer initialization.
- `gfx_v11_0_compute_mqd_init()` uses compute HQD defaults for EOP control, MQD control, PQ control, PQ doorbell control, PQ read pointer, persistent state, and IB control.
- `mes_v11_0_mqd_init()`, `mes_v12_0_mqd_init()`, and `mes_v12_1_mqd_init()` include this header and use compute HQD defaults for MES ring MQD construction.
- `gfxhub_v3_0.c` includes this header and uses `regGCVM_L2_CNTL3_DEFAULT`, `regGCVM_L2_CNTL4_DEFAULT`, and `regGCVM_L2_CNTL5_DEFAULT` while programming GC VM L2 cache behavior.
- `sdma_v6_0.c` includes this header for SDMA v6/GC 11 register defaults and offsets; SDMA queue setup depends on the same queue-control reset semantics represented here.

## Risks And Edge Cases

- The macros are untyped numeric constants. A wrong generated default compiles cleanly but can silently program an unsafe queue, VM, cache, render, or power/clock state.
- Defaults are often used as baselines before `REG_SET_FIELD`. If a reset value changes but copied local definitions or generated headers diverge, fields not explicitly overwritten may retain stale bits.
- Queue defaults are security- and stability-sensitive. Incorrect `CP_GFX_*` or `CP_HQD_*` defaults can break doorbells, write pointers, VMID assignment, KMD/private state, TMZ handling, EOP buffers, IB availability, or queue activation.
- VM defaults are fault-path critical. Bad `GCVM_CONTEXT*`, invalidation engine, L2 control, or fault-default address defaults can produce VM faults, stale TLB/cache state, page migration failures, or invalid memory accesses.
- SDMA defaults are heavily repeated. A single generation/copy error in one queue instance can affect only a subset of queues and be missed by single-ring smoke tests.
- Many register families are per-VMID, per-context, per-shader-stage, per-render-target, or per-invalidation-engine. Repetition makes off-by-one and partial-family updates easy during generated-header refreshes.
- PF/VF and PF-only defaults must be respected under SR-IOV. Programming a PF-owned register from a VF path may fail, be ignored, or violate virtualization assumptions.
- Some defaults include magic-looking non-zero values (`0x0be05501`, `0x00308509`, `0x02f80000`, `0x2a00126a`, RMI maps, DIDT stall patterns). These should be treated as generated hardware contract values, not simplified unless verified against the ASIC register database.
- This chunk is partial for the full file. It covers complete early blocks but stops inside `gc_pfonly_utcl1dec`; file-level conclusions must merge with later chunks.

## Test Signals

Useful validation is mostly build, hardware initialization, queue execution, and reset testing:

- Kernel build coverage with AMDGPU, GFXHUB, SDMA v6, MES v11/v12, GFX v11, and KFD enabled catches missing, renamed, or conflicting default macros.
- GFX ring and compute ring initialization should complete without MQD programming errors, doorbell failures, ring timeouts, or invalid queue activation after using `CP_GFX_*` and `CP_HQD_*` defaults as baselines.
- MES firmware queues should initialize and submit work successfully on GC 11/related ASICs; failures often surface as MES ring timeouts or queue map/unmap errors.
- VM/GART initialization should complete without GCVM protection faults, repeated TLB invalidation timeouts, or bad fault-default-address behavior.
- SDMA rings should pass copy/fill tests and suspend/resume/reset cycles with stable read/write pointer and doorbell behavior.
- Graphics workloads should exercise render-context defaults indirectly through clear, depth/stencil, color target, viewport/scissor, VRS, and shader-stage programming without hangs or corrupted output.
- SR-IOV validation should cover both PF and VF paths, ensuring PF-only defaults are not assumed writable by VF code.
- Reset, suspend/resume, and GPU recovery tests are important because defaults become most visible when queue descriptors and VM/cache state are rebuilt from reset baselines.

### subset-b-002497: lines 2931-5857

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_default.h lines 2931-5857

## Scope

This chunk is a large generated segment of the AMDGPU GC 11.0.0 default-register header. It contains C preprocessor constants only: `reg..._DEFAULT` macros for memory-mapped GC registers and `ix..._DEFAULT` macros for indexed registers. It declares no functions, structs, enums, storage, or executable initialization logic.

The range starts with the tail of the `gc_pfonly_utcl1dec` area (`regGCRD_SA1_TARGETS_DISABLE_DEFAULT` and `regGCRD_CREDIT_SAFE_DEFAULT`), then covers 41 generated address blocks through the first part of `gccacind`. In this slice there are 2,804 `_DEFAULT` macros. The largest sections are CP/MES/RS64 command processor defaults, RLC/RLCS defaults, GCMC/GCVM and MARC VM defaults, GFX IMU defaults, performance-counter defaults, cache/GUS/GL1/GL2 defaults, hypervisor/PSP-visible defaults, and global CAC indexed defaults.

## Purpose

`gc_11_0_0_default.h` is hardware metadata for AMD graphics core 11.0.0. Its constants document the reset or generated default values for registers whose addresses are defined in `gc_11_0_0_offset.h` and whose bit layouts are defined in `gc_11_0_0_sh_mask.h`. Runtime code usually uses the register offsets and masks directly; this default header gives the matching baseline values for review, tables, register dumping, restoration, and generated-register consistency.

This chunk describes the baseline for several critical GC 11 surfaces:

- PF-only controls for GCR/PMM, TCP invalidation/status, GDS enhancement, SEDC overrides, global and shader-engine CAC, and SPI CU resource reservation.
- Command processor and scheduler-facing state: CP EOP/fence/doorbell/wptr state, MES program and interrupt registers, RS64 aperture and firmware-visible control registers, queue status, scratch, HQD, trap, and interrupt defaults.
- Graphics memory and cache state: GUS, GL1, GL1H, CH/CHC/CHCG, GL2/GL2C/GL2A, GCMC/GCVM, GCUTCL2, and MARC PF/VF mapping defaults.
- Performance infrastructure: PERF counter data registers, select/config registers, result controls, and SDMA0/SDMA1 performance counter defaults.
- Firmware and power infrastructure: GFX IMU mailbox/RAM/timer/reset defaults, GDFLL/RTAVFS defaults, RLC/RLCS defaults, CGTT/CGTS/ICG clock controls, GFX power controls, PSP-facing indirect/register firewall surfaces, and hypervisor/SRIOV register windows.
- Indexed `gccacind` defaults for GC CAC activity accumulators and stall/power-brake transition LUTs.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The interface is the generated macro naming convention:

- `reg<REGISTER>_DEFAULT` gives the generated default for a direct register symbol.
- `ix<REGISTER>_DEFAULT` gives the generated default for an indexed register symbol.
- `// addressBlock: ...` comments group macros by hardware decode block.
- Matching offsets live in `gc_11_0_0_offset.h`; matching field shifts and masks live in `gc_11_0_0_sh_mask.h`.

Representative nonzero defaults are important because they encode hardware reset behavior, not arbitrary software choices. Examples include `regGCR_GENERAL_CNTL_DEFAULT = 0x00f00400`, `regPMM_CNTL2_DEFAULT = 0x60000000`, `regTCP_CNTL2_DEFAULT = 0x0000200a`, `regSEDC_GL1_GL2_OVERRIDES_DEFAULT = 0x00002828`, `regGC_CAC_CTRL_1_DEFAULT = 0x00000108`, `regGC_CAC_CTRL_2_DEFAULT = 0x00007fc4`, `regSPI_GS_THROTTLE_CNTL1_DEFAULT = 0x12355123`, `regSPI_GS_THROTTLE_CNTL2_DEFAULT = 0x0001544d`, `regSPI_ATTRIBUTE_RING_SIZE_DEFAULT = 0x00020000`, `regCP_MES_PRGRM_CNTR_START_DEFAULT = 0x00000800`, `regGUS_IO_WR_COMBINE_FLUSH_DEFAULT = 0x01000000`, `regGL2C_CTRL_DEFAULT = 0xf37fff7f`, `regGL2C_CTRL2_DEFAULT = 0x0402002f`, `regRLC_CNTL_DEFAULT = 0x00000001`, `regRLC_RLCS_EXCEPTION_REG_1_DEFAULT = 0x0003b984`, `regSDMA0_UCODE_SELFLOAD_CONTROL_DEFAULT = 0x00000223`, `regSDMA0_F32_CNTL_DEFAULT = 0x08084001`, and `ixGC_CAC_CNTL_DEFAULT = 0x000000ff`.

## Register Families Covered

The opening PF-only region covers the end of UTCL1/GCRD credit defaults, GCR/PMM controls, TCP invalidation/status/debug registers, GDS enhancement/CGPG restore defaults, SEDC GL1/GL2 override state, and the global CAC control block. The CAC block includes global and per-shader-engine aggregate counters, EDC and throttle controls, PCC/power-brake/DIDT stall patterns, power counters, many per-client activity weights, indirect index/data registers, and per-SE CAC windows. Most weights and counters default to zero, while the controls and stall pattern selectors have nonzero reset words.

`gc_pfonly2_spidec` is the SPI CU resource reservation area. It defines reserve and reserve-enable defaults for CUs 0-15. Every macro in this small block defaults to zero, meaning no generated per-CU reservation is active at reset.

`gc_gfxudec` and `gc_cprs64dec` are command processor and graphics user-decode surfaces. They include CP EOP done addresses/data, last fence, doorbell and write-pointer state, scratch registers, queue/reset/status state, GRBM/VGT/GE/PA/SQ/SQC/DB controls, SPI shader resource and attribute-ring defaults, MES program counters and interrupt vectors, HQD and queue descriptors, trap/debug state, MEC/MES/RS64 firmware-visible registers, and RS64 data-cache aperture base/mask/control pairs. This is one of the highest-risk parts of the chunk because command submission, MES scheduling, firmware loading, trap handling, and queue recovery depend on these register names and reset assumptions.

`gc_gusdec`, `gc_gl1dec`, `gc_chdec`, `gc_gl2dec`, and `gc_gl1hdec` cover graphics fabric, cache, and channel defaults. They include GUS read/write priority, L1 SA registers, combine flush behavior, GL1 and GL1C UTCL0 defaults, CH/CHC/CHCG arbitration and clock-gating controls, GL2C cache control, address-match masks and sizes, writeback/invalidate defaults, GL2A address-match controls, and GL1H burst settings. Several cache and arbitration defaults are nonzero and should be treated as hardware reset policy.

`gc_perfddec`, `gc_gcvml2perfddec`, `gc_gcvml2prdec`, `gc_sdma0_sdma0perfddec`, and `gc_sdma0_sdma1perfddec` are performance-counter data blocks. Their counter low/high result registers reset to zero. The matching select/config blocks in `gc_perfsdec`, `gc_gcvml2perfsdec`, `gc_gcvml2pldec`, `gc_sdma0_sdma0perfsdec`, and `gc_sdma0_sdma1perfsdec` hold mostly nonzero selector defaults such as `0x000fffff`, `0x000003ff`, `0x0000ffff`, and result-control defaults such as `0x04000000`. These values define the disabled or unselected baseline for GC, VM L2, UTCL2, GUS, and SDMA performance monitoring.

`gc_gfx_imu_gfx_imudec` and `gc_gfx_imu_gfx_imu_pspdec` describe the GFX IMU mailbox, C2P/P2C message, RAM access, timer, fuse, interrupt-gasket, RLC bootloader, and firmware loading defaults. The IMU region is mostly zero but includes a nonzero interrupt-gasket control default. It integrates with firmware-driven graphics bring-up rather than normal driver data structures.

`gc_gdfll_gdfll_dec`, `gc_gdfll_se_gdfll_dec`, `gc_grtavfs_grtavfs_dec`, `gc_grtavfsdec`, and `gc_grtavfs_se_grtavfs_dec` cover graphics droop and real-time adaptive voltage/frequency controls. GDFLL hysteresis control defaults to `0x00000001`; RTAVFS soft reset and clock controls include nonzero reset defaults. These registers are power-management and firmware-tuning surfaces.

`gc_rlcdec` and `gc_rlcsdec` describe run-list controller state. They include RLC control/status, timestamps, SRAM/firmware addresses, save/restore controls, CP table addresses, queue and interrupt info, SRM/IMU bootload state, RLCS dump/exception/debug registers, PMM CGCG controls, memory power controls, and decode start/end markers. `regRLC_CNTL_DEFAULT` is enabled at `0x00000001`, and the repeated RLCS exception registers default to `0x0003b984`.

`gc_pwrdec` covers clock and power controls such as CGTS, CGTT, GFX power, and ICG clock gating. Defaults here are small in count but semantically sensitive because they affect graphics clock gating, memory power behavior, and power transitions.

`gc_cphypdec`, `gc_hypdec`, `gc_sdma0_sdma0hypdec`, `gc_sdma0_sdma1hypdec`, and `gc_gcvmsharedhvdec` are hypervisor and SRIOV-facing surfaces. They include CP firmware upload addresses/data, MEC memory bounds, GFX pipe priority, GRBM save/restore data, GPU IOV busy/status registers, SDMA firmware self-load defaults, SDMA F32 control defaults, and per-VF framebuffer size/offset defaults. These registers are relevant when the same GC hardware is partitioned between PF and VF contexts.

`gc_pspdec` and `gc_gcvml2pspdec` expose PSP- or security-owned controls: CP/MES/MEC/RS64 debug-module index/data, GRBM CAM data, firewall violation address, GCUTCL2 translation bypass, translation assist control, 16 MARC base/relocation/length entries, 16 MARC PF/VF mappings, and translation-fault controls. The MARC mapping entries default to `0x0001ffff`, while base/relocation/length values default to zero.

The final `gccacind` section contains indexed global CAC defaults. It includes `ixGC_CAC_ID_DEFAULT`, `ixGC_CAC_CNTL_DEFAULT`, many `ixGC_CAC_ACC_*` accumulators for CP, EA, UTCL2, GDS, GE, PMM, GL2C, PH, SDMA, CHC, GUS, and RLC clients, plus release/stall and power-brake LUT entries and fixed-pattern performance counters. Except for `ixGC_CAC_CNTL_DEFAULT = 0x000000ff`, this covered part of `gccacind` resets to zero.

## Control Flow

This header has no runtime control flow. All behavior is indirect through compile-time macro substitution.

The normal consumer flow is:

1. Include `gc_11_0_0_offset.h`, `gc_11_0_0_sh_mask.h`, and `gc_11_0_0_default.h` for GC 11 ASIC code.
2. Use `reg...` or `ix...` symbols with AMDGPU SOC15 and indirect-register helpers to read or write hardware registers.
3. Use field masks with `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15_PREREG`, and related helpers.
4. Treat `_DEFAULT` values as generated reset baselines for documentation, register lists, initialization tables, state restore, or comparison.

Direct include sites in this source tree include `amdgpu/gfxhub_v3_0.c`, `amdgpu/sdma_v6_0.c`, and MES v11/v12 sources. `gfxhub_v3_0.c` uses the matching GC 11 register names for GART aperture setup, system aperture setup, VM page-table base programming, L1/L2 TLB and cache programming, and protection-fault reporting. `sdma_v6_0.c` uses the matching register namespace for SDMA status, queue, UTCL1, firmware, and hypervisor register handling. MES sources include the same header set while setting up scheduler rings, firmware-driven command submission, and register access through MES packets.

## State And Persistence

The macros themselves have no storage and no persistence. They are preprocessor constants.

The represented state is persistent hardware state within a GPU reset epoch. CP/MES/RLC/SDMA firmware registers, queue state, doorbells, write pointers, scratch registers, trap state, and HQD/MQD-facing registers are reinitialized during firmware load, ring setup, GPU reset recovery, suspend/resume, and MES or KIQ bring-up. VM and GCMC/GCVM registers persist as the active address-translation configuration until reprogrammed or reset. Cache and fabric controls persist across normal workloads and are re-established by initialization or power-management paths when needed.

Some values are used as baselines for state that driver code stores elsewhere. For example, GFXHUB v3 code reads and writes GCMC/GCVM registers to configure GART and system apertures, protection-fault addresses, TLB behavior, and L2 cache policy. SDMA v6 code records and reports SDMA status/queue registers and manages firmware-controlled queue state. MES code uses CP/MES register surfaces indirectly while submitting scheduler commands and waiting for completion. The default header does not own those state transitions, but incorrect defaults or mismatched names make those transitions harder to validate and debug.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register set remaining synchronized:

- `gc_11_0_0_offset.h` must define the corresponding register addresses.
- `gc_11_0_0_sh_mask.h` must define the corresponding field masks and shifts.
- AMDGPU SOC15 helpers provide the read/write operations for direct registers.
- Indirect register helpers and firmware interfaces access `ix...` and firmware-owned surfaces.
- GFXHUB v3, SDMA v6, MES v11/v12, RLC, PSP, SRIOV, performance-monitoring, and power-management code all share the same generated register namespace.

Important integration surfaces include VM setup and fault reporting through GCMC/GCVM/GCUTCL2; command submission and scheduler state through CP, MES, RS64, RLC, and HQD registers; SDMA firmware and queue state through SDMA0/SDMA1 hypervisor and performance blocks; power and throttling through CAC, DIDT, GDFLL, RTAVFS, CGTT, and ICG registers; and debug/performance tooling through perf counter select/result registers, accumulators, trap state, scratch registers, and firewall violation registers.

## Risks And Edge Cases

Generated-header drift is the primary risk. A default value can compile cleanly while being wrong for the offset or mask header generated beside it. That kind of mismatch can surface only as hardware bring-up failures, unstable power behavior, incorrect register dumps, or broken reset/resume behavior.

The high-risk groups in this chunk are CP/MES/RS64 and RLC/RLCS defaults, because scheduler, firmware, trap, and queue recovery paths depend on precise register contracts; GCMC/GCVM/GCUTCL2 defaults, because VM aperture and fault-handling bugs can become memory corruption or GPU faults; SDMA hypervisor defaults, because firmware self-load and F32 controls affect DMA engine availability; CAC/DIDT/power defaults, because wrong stall, EDC, throttle, or clock-gating baselines can cause hangs or severe performance/power regressions; and MARC PF/VF mapping defaults, because SRIOV partitioning and security boundaries depend on correct PF/VF mapping state.

Many blocks are mostly zero. That does not mean they are safe to delete or normalize. Zero defaults are still part of the generated hardware contract, especially for firmware mailboxes, fault latches, queue pointers, accumulators, and reserved surfaces. Conversely, opaque nonzero values such as RS64 aperture controls, RLC exception words, cache controls, RTAVFS controls, and SDMA self-load controls should be validated against the generator or hardware database rather than inferred from local source.

Because this is generated metadata, manual edits are risky. Any change should be checked against the matching offset and mask headers, the AMD register database or upstream generated source, and at least one direct consumer path that includes the GC 11 header set.

## Test Signals

There are no unit-testable functions in this chunk. Useful validation is build, hardware, and register-observation oriented.

Compile-time signals include successful AMDGPU builds for files that include `gc_11_0_0_default.h`, especially GFXHUB v3, SDMA v6, and MES v11/v12 sources. Missing or renamed macros should fail at compile time where direct references exist, but wrong numeric defaults will not.

Runtime signals include successful probe and firmware loading on GC 11 ASICs, stable MES/KIQ scheduler initialization, working SDMA ring setup and queue execution, correct GART and system-aperture programming, sane VM fault reporting, successful GPU reset and suspend/resume, and no regressions under graphics and compute workloads.

Debug and diagnostics signals include plausible register dumps for CP/MES/RLC/SDMA status, expected zero-baseline performance counters before programming, working perf counter selection and result reads, correct protection-fault client/status decoding in GFXHUB v3, no unexpected CAC/EDC/throttle events, and stable SRIOV/PF-VF behavior where hypervisor and MARC mapping registers are visible.

### subset-b-002498: lines 5858-6114

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_default.h lines 5858-6114

## Scope

This chunk is the final segment of the generated AMD GC 11.0.0 default-register header. It contains only C preprocessor `#define` constants for hardware reset/default values; it declares no functions, structs, enums, storage objects, or executable initialization code.

The range starts at the tail of the `gccacind` address block with `ixFIXED_PATTERN_PERF_COUNTER_4_DEFAULT` through `ixFIXED_PATTERN_PERF_COUNTER_10_DEFAULT` and `ixHW_LUT_UPDATE_STATUS_DEFAULT`. It then covers the full `secacind` block, the full `grtavfsind` RTAVFS register table from `ixRTAVFS_REG0_DEFAULT` through `ixRTAVFS_REG194_DEFAULT`, and the tail `sqind` block from local SQ debug state through selected-wave execution masks. The range ends with the header's `#endif`.

## Purpose

`gc_11_0_0_default.h` is generated hardware metadata for AMDGPU GC 11 ASICs. Its `_DEFAULT` macros document the reset value associated with register names from the matching GC register offset header. Driver code includes this header with `gc_11_0_0_offset.h` and `gc_11_0_0_sh_mask.h` so GC 11 code can compile against one ASIC-specific set of register names, offsets, masks, and known baseline values.

This chunk documents late-file indexed register defaults rather than programming policy:

- The fixed-pattern counter and LUT-status defaults describe the idle baseline for the end of the global CAC/power-management indexed register area.
- The `secacind` defaults describe per-shader-engine CAC selector/control reset state.
- The `grtavfsind` defaults describe real-time adaptive voltage/frequency scaling table and status reset words.
- The `sqind` defaults describe selected-wave debug/readout state reset values for shader queue wave inspection.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The important interface is the generated macro convention:

- `ix<REGISTER>_DEFAULT` gives the default value for an indexed register accessed through an indirect register block.
- Matching `ix<REGISTER>` address macros live in `gc_11_0_0_offset.h`.
- Matching bit shifts and masks live in `gc_11_0_0_sh_mask.h`.
- Normal consumers combine these generated definitions with AMDGPU register helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `REG_SET_FIELD`, `REG_GET_FIELD`, and indirect-register selector/data sequences.

Notable macro groups in this chunk:

- `ixFIXED_PATTERN_PERF_COUNTER_4_DEFAULT` through `ixFIXED_PATTERN_PERF_COUNTER_10_DEFAULT`: fixed-pattern performance-counter defaults at the end of the global CAC indexed block. All reset to `0x00000000`.
- `ixHW_LUT_UPDATE_STATUS_DEFAULT`: hardware LUT update status default. It resets to `0x00000000`, matching an idle/no-status baseline.
- `ixSE_CAC_ID_DEFAULT` and `ixSE_CAC_CNTL_DEFAULT`: shader-engine CAC ID and control defaults. `ID` resets to zero; `CNTL` resets to `0x000000ff`. In the companion mask header, `SE_CAC_CNTL` exposes a `CAC_THRESHOLD` field, so the default represents a nonzero threshold/control value rather than an all-disabled word.
- `ixRTAVFS_REG0_DEFAULT` through `ixRTAVFS_REG194_DEFAULT`: RTAVFS register-table defaults. The table is mostly zero but has several important nonzero runs and singleton values:
  - `REG0`-`REG4` = `0x01000000`.
  - `REG32`-`REG42` = `0x000000ff`.
  - `REG43` = `0xcccdbcdd`, whose masks split the word into PI-controller proportional/integral nibbles (`RTAVFSKP*`/`RTAVFSKI*`).
  - `REG44` = `0x2587d190`, whose masks expose voltage-code fields and binary-search/hardware-calibration bits.
  - `REG46` = `0x000211cd`, `REG47` = `0x000af12c`, `REG48` = `0x00000010`, and `REG51` = `0x00000008`.
  - `REG54`-`REG72`, `REG80`-`REG101`, `REG109`-`REG111`, and `REG115`-`REG117` = `0x01000000`.
  - `REG73`-`REG79`, `REG102`-`REG108`, and `REG112`-`REG114` = `0x00000100`.
  - `REG118`-`REG188` are zero, except `REG189` = `0x0007d12c`.
  - `REG193` = `0x00000001`; `REG190`-`REG192` and `REG194` reset to zero.
- `ixSQ_DEBUG_STS_LOCAL_DEFAULT` and `ixSQ_DEBUG_CTRL_LOCAL_DEFAULT`: local SQ debug status/control defaults, both zero.
- `ixSQ_WAVE_ACTIVE_DEFAULT` and `ixSQ_WAVE_VALID_AND_IDLE_DEFAULT`: selected-wave slot/activity/idle views, both zero at reset.
- `ixSQ_WAVE_MODE_DEFAULT`, `ixSQ_WAVE_STATUS_DEFAULT`, and `ixSQ_WAVE_TRAPSTS_DEFAULT`: selected-wave mode, status, and trap-state views. The companion mask header defines floating-point mode bits, exception enables, privilege/debug/status bits, valid/idle flags, trap events, and exception fields; all reset to zero in this generated default table.
- `ixSQ_WAVE_GPR_ALLOC_DEFAULT`, `ixSQ_WAVE_LDS_ALLOC_DEFAULT`, `ixSQ_WAVE_IB_STS_DEFAULT`, `ixSQ_WAVE_IB_STS2_DEFAULT`, `ixSQ_WAVE_IB_DBG1_DEFAULT`, and `ixSQ_WAVE_FLUSH_IB_DEFAULT`: selected-wave allocation, instruction-buffer status, debug, and flush views, all zero.
- `ixSQ_WAVE_PC_LO_DEFAULT`, `ixSQ_WAVE_PC_HI_DEFAULT`, `ixSQ_WAVE_FLAT_SCRATCH_LO_DEFAULT`, `ixSQ_WAVE_FLAT_SCRATCH_HI_DEFAULT`, `ixSQ_WAVE_M0_DEFAULT`, `ixSQ_WAVE_EXEC_LO_DEFAULT`, and `ixSQ_WAVE_EXEC_HI_DEFAULT`: full-width selected-wave scalar/debug state and execution-mask words, all zero.
- `ixSQ_WAVE_HW_ID1_DEFAULT` and `ixSQ_WAVE_HW_ID2_DEFAULT`: selected-wave hardware identity words, both zero. The mask header splits these into wave/SIMD/WGP/SA/SE and queue/pipe/ME/state/workgroup/VM fields.
- `ixSQ_WAVE_TTMP0_DEFAULT`, `ixSQ_WAVE_TTMP1_DEFAULT`, and `ixSQ_WAVE_TTMP3_DEFAULT` through `ixSQ_WAVE_TTMP15_DEFAULT`: trap temporary register defaults, all zero. `TTMP2` is not present in this chunk's generated list.
- `ixSQ_WAVE_POPS_PACKER_DEFAULT`, `ixSQ_WAVE_SCHED_MODE_DEFAULT`, and `ixSQ_WAVE_SHADER_CYCLES_DEFAULT`: selected-wave packing, scheduling, and cycle-count views, all zero.

## Control Flow

This header has no runtime control flow. The direct behavior is compile-time substitution of constants by the C preprocessor.

The implied consumer flow is:

1. Include the GC 11.0.0 offset, shift/mask, and default headers for the active ASIC generation.
2. Select a register through an `ix...` macro and the appropriate indirect-address path.
3. Read, write, or read-modify-write the selected register through SOC15 or block-specific helpers.
4. Use the `_DEFAULT` macro as generated reset documentation, an initialization-table baseline, or a comparison/restoration value.

The SQ wave debug path shows the register-access pattern around this chunk. In `gfx_v11_0.c`, `wave_read_ind()` writes `regSQ_IND_INDEX` with a wave ID and indexed SQ register address, then reads `regSQ_IND_DATA`. `gfx_v11_0_read_wave_data()` reads many of this chunk's `ixSQ_WAVE_*` registers, including `STATUS`, `PC_LO`, `PC_HI`, `EXEC_LO`, `EXEC_HI`, `HW_ID1`, `HW_ID2`, `GPR_ALLOC`, `LDS_ALLOC`, `TRAPSTS`, `IB_STS`, `IB_STS2`, `IB_DBG1`, `M0`, and `MODE`.

For CAC and RTAVFS registers, real sequencing occurs in power-management, firmware, or hardware-init paths outside this file: choose the indexed block, program thresholds or table entries, poll status, and restore hardware policy after reset/resume. This header only records the generated reset baseline those flows must be compatible with.

## State And Persistence

The chunk stores no software state. All definitions are compile-time constants and allocate no memory.

The represented state is hardware state:

- Fixed-pattern counters and hardware LUT status represent counter/status state in the global CAC indexed block.
- `secacind` state represents per-shader-engine CAC identity and threshold/control state.
- RTAVFS state represents adaptive voltage/frequency controller table entries, PI-controller constants, voltage-code values, binary-search/calibration controls, status words, and FSM state. Several defaults are nonzero and should be treated as ASIC-specific reset data.
- SQ state represents selected-wave debug state: activity, validity/idle status, mode/status/trap flags, register allocation metadata, program counter, instruction-buffer counters, scratch pointers, hardware identity, trap temporaries, scalar `M0`, execution masks, scheduling state, and shader-cycle accounting.

Hardware reset, GPU reset, suspend/resume, runtime power management, firmware bring-up, and shader debug/fault collection are the events that make these defaults relevant. Runtime software may observe values very different from these defaults after firmware or driver initialization, especially for RTAVFS and SQ wave state.

## Dependencies And Integration Points

This generated header depends on the surrounding ASIC register description set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h` supplies indexed register addresses such as `ixFIXED_PATTERN_PERF_COUNTER_4`, `ixSE_CAC_CNTL`, `ixRTAVFS_REG0`, `ixRTAVFS_REG189`, and `ixSQ_WAVE_ACTIVE`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h` supplies field interpretation for `SE_CAC_CNTL`, RTAVFS table words, and SQ wave debug/status registers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0.c` uses the matching SQ indexed register names to read wave debug data through `regSQ_IND_INDEX` and `regSQ_IND_DATA`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v11_0.c`, `mes_v12_0.c`, `mes_v12_1.c`, `sdma_v6_0.c`, and `gfxhub_v3_0.c` include `gc_11_0_0_default.h` with the matching offset/mask headers for GC 11-family programming.
- Other GC 11 consumers include `amdgpu_amdkfd_gfx_v11.c`, `imu_v11_0.c`, `soc21.c`, display helpers, and SDMA/GFXHUB paths that include the offset and mask headers even when they do not include this default header directly.

The chunk is source-tree-aligned with `drivers/gpu/drm/amd/include/asic_reg/gc/`. It must remain synchronized with the generated GC 11.0.0 offset and mask headers; changing a default independently from the generated address/mask metadata can create a compile-clean but semantically inconsistent hardware description.

## Risks And Edge Cases

- Generated-header drift is the primary risk. Defaults, offsets, and masks must come from the same hardware database and ASIC revision.
- RTAVFS names are opaque (`REG0`-`REG194`), so many values cannot be reviewed semantically from the default header alone. Nonzero defaults such as `0xcccdbcdd`, `0x2587d190`, `0x000211cd`, `0x000af12c`, `0x0007d12c`, and `0x00000001` need validation against the generator or hardware specification.
- The RTAVFS table contains large repeated runs of `0x01000000`, `0x00000100`, `0x000000ff`, and zeros. Mechanical regeneration, sorting, or deduplication mistakes could silently move values to the wrong table index.
- `ixSE_CAC_CNTL_DEFAULT` is `0x000000ff`, not zero. Treating all CAC registers as zero-initialized would lose a meaningful shader-engine threshold/control default.
- SQ wave defaults are zero because they describe reset/idle selected-wave readout state, not because live wave state is expected to be zero. Debug and hang-analysis code must read live registers through the SQ indirect path after selecting the target wave.
- The generated SQ TTMP list skips `ixSQ_WAVE_TTMP2_DEFAULT` in this chunk. Consumers should rely on generated register names rather than assuming every numbered register appears in a contiguous default list.
- The header itself cannot validate hardware behavior. Incorrect values can surface only as ASIC-specific power-management instability, throttling anomalies, GPU reset/resume issues, hang-dump decoding errors, or shader debug regressions.

## Test Signals

There are no unit-testable functions in this chunk. Useful validation signals are build, generation, and hardware-integration oriented:

- Build coverage for AMDGPU files that include `gc_11_0_0_default.h`, especially MES, SDMA v6, and GFXHUB GC 11 paths.
- Compile-time detection of missing or renamed `ix...` macros when default, offset, and mask headers are regenerated inconsistently.
- GPU initialization and firmware bring-up logs on GC 11 hardware, especially MES and SDMA initialization paths that include this default header.
- Runtime power-management and throttling telemetry that can expose incorrect CAC or RTAVFS defaults after reset/resume.
- Suspend/resume and GPU reset testing on GC 11 ASICs, which can expose bad assumptions about RTAVFS or CAC reset state.
- Shader fault, hang-dump, wave-debug, and trap handling tests that exercise SQ indirect reads of `SQ_WAVE_*` registers through `gfx_v11_0_read_wave_data()`.
- Register-header regeneration checks comparing this file against the authoritative hardware database so table index/value ordering is preserved.
