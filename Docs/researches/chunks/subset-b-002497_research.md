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
