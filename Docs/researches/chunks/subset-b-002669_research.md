# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_sh_mask.h lines 4872-7289

## Purpose

This chunk is a generated ASIC register field header for the AMD GC 9.4.2 graphics block. It does not contain executable C logic; it defines `__SHIFT` and `_MASK` constants that describe bit layouts for memory-address decode, graphics-cache/power-control, error-detection, performance-counter, and GDS/GDSP registers. Driver code combines these constants with the matching register offsets from `gc_9_4_2_offset.h` and AMDGPU helper macros such as `REG_SET_FIELD`, `WREG32_SOC15`, `RREG32_SOC15`, and `SOC15_REG_OFFSET`.

The slice contains 2,418 source lines, 2,171 `#define` entries, and 236 register/comment block markers. It starts in the middle of `GCEA_ADDRDEC_MISC_CFG`, then covers complete groups for GCEA address decoding and IO scheduling, GCEA perf/EDC/DSM control, GC CAC/DIDT/throttling/EDC, GDS protection and counters, and the beginning of per-VMID GDS/GWS/OA partition registers.

## Important Register Groups And Fields

The `GCEA_ADDRDEC*` section describes the graphics engine address decoder. `GCEA_ADDRDECDRAM_HARVEST_ENABLE` and `GCEA_ADDRDECGMI_HARVEST_ENABLE` provide force-enable/value bits for harvested address bits `B3` through `B5`. The repeated `GCEA_ADDRDEC{0,1,2}_...` groups define three decoder instances, each with base address registers for primary chip-selects `CS0` through `CS3` and secondary chip-selects `SECCS0` through `SECCS3`, address masks for `CS01`/`CS23` and secondary pairs, and detailed address mapping fields. Those mapping fields include bank group count, row/column layout, bank selectors, channel-bit selectors, column selectors `COL0` through `COL15`, row-major selectors, and row-MSB inversion controls. The matching offset header maps these fields to registers around `regGCEA_ADDRDEC0_BASE_ADDR_CS0` at `0x0a5f`, through `regGCEA_ADDRDEC2_RM_SEL_SECCS23` at `0x0aac`.

`GCEA_ADDRNORM*` and `GCEA_IO_*` define normalization and client arbitration controls. The IO maps assign read/write clients to groups (`GCEA_IO_RD_CLI2GRP_MAP0/1`, `GCEA_IO_WR_CLI2GRP_MAP0/1`), define combine-flush behavior, group burst sizing, read/write priority aging, queueing, fixed priority, urgency, urgency masks, and quantum settings for priorities 1 through 3. These constants represent low-level memory-system scheduling policy rather than normal kernel data structures.

The GCEA perf/EDC/DSM region includes `GCEA_MISC`, `GCEA_LATENCY_SAMPLING`, performance counter low/high result registers, counter configuration registers, result control, EDC counters (`GCEA_EDC_CNT`, `GCEA_EDC_CNT2`, `GCEA_EDC_CNT3`), DSM controls, crossbar credit and max-burst knobs, probe controls/map, error status, DRAM-bank arbitration, and address-decoder select. These fields are diagnostic and reliability surfaces: they count or configure hardware events, expose ECC/EDC state, and control built-in scan/debug modes.

`GCEA_CGTT_CLK_CTRL` belongs to the power-decode address block and exposes clock-gating control/status style bits for the GCEA area. It is separate from the main base-index-0 GC register ranges; the matching offset header marks it with base index 1.

The `GC_CAC*`, `GC_DIDT*`, `GC_THROTTLE*`, and `GC_EDC*` section describes compute activity counting, dynamic current/power management, throttling, and graphics-core error detection. Important fields include CAC aggregation controls, CAC indirect index/data access, DIDT enables and weights, throttle pattern/program step controls, power-brake fields, EDC status/overflow/threshold controls, and rolling power delta reporting. `gfx_v9_4_2_set_power_brake_sequence()` directly uses `GC_THROTTLE_CTRL1__PWRBRK_STALL_EN_*` through `REG_SET_FIELD(tmp, GC_THROTTLE_CTRL1, PWRBRK_STALL_EN, 1)` before writing `regGC_THROTTLE_CTRL1`.

The `GDS_*` section covers Global Data Share configuration, status, protection faults, virtual-memory protection faults, EDC counters, DSM controls, and a work-distributor GDS CSB register. `GDS_CONFIG` describes capacity/layout knobs; `GDS_CNTL_STATUS` includes status and control bits; `GDS_PROTECTION_FAULT` and `GDS_VM_PROTECTION_FAULT` expose fault address/status fields; and `GDS_EDC_*` registers track EDC events across GDS, GRBM, OA, PHY, and pipe paths.

The `gc_gdspdec` part begins the per-VMID partition table. `GDS_VMID0_BASE` through `GDS_VMID15_BASE` expose 16-bit base fields, paired `GDS_VMID0_SIZE` through `GDS_VMID15_SIZE` expose 17-bit sizes, and `GDS_GWS_VMID0` through `GDS_GWS_VMID15` pack a 6-bit GWS base with a size field at bit 16. The chunk ends at `GDS_OA_VMID9`; the remaining OA VMID masks continue after this slice. Other GFX generations use the same register pattern in init and command-submission paths, so these constants define the ABI between KFD/AMDGPU queue setup and hardware VMID-local GDS/GWS/OA allocation.

## APIs, Types, And Integration Points

There are no functions, structs, enums, or storage objects in this chunk. The public interface is the macro naming scheme:

- `<REGISTER>__<FIELD>__SHIFT` gives the right shift for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the raw 32-bit register value.
- Register addresses are intentionally not in this file; they come from `gc_9_4_2_offset.h` as `reg<REGISTER>` constants and `reg<REGISTER>_BASE_IDX`.

The principal consumer is `drivers/gpu/drm/amd/amdgpu/gfx_v9_4_2.c`, which includes both `gc/gc_9_4_2_offset.h` and this header. The AMDGPU SOC15 register helpers combine the offset constants with these masks. `REG_SET_FIELD` depends on exact macro spelling, so a field rename or mask mismatch is a compile-time or silent hardware-programming risk depending on which macro is affected.

Cross-version integration is also important. Similar macro groups appear in `gc_9_0_sh_mask.h`, `gc_9_2_1_sh_mask.h`, `gc_9_4_3_sh_mask.h`, and later GC 10/11 headers, but fields are not perfectly identical. For example, the GC 9.4.2 `GC_THROTTLE_CTRL1` layout contains `PATTERN_EXTEND_*`, `FP_PATTERN_CLAMP_EN`, and `PWRBRK_STALL_EN`, while some later headers use different power-brake program-min/max fields. Version-specific source must include the matching header pair.

## Control Flow And State

This header has no runtime control flow. Its constants are consumed by control flow in AMDGPU initialization, RAS, power management, debug, and queue/GDS setup paths. The typical sequence is:

1. Driver code selects the target SOC15 block/instance and, when needed, a shader/SE/VMID context.
2. Code reads or initializes a 32-bit register value.
3. `REG_SET_FIELD` or explicit shift/mask arithmetic inserts one of these field values.
4. `WREG32_SOC15`/`WREG32` writes the resulting register value to the GC block.

State is persistent in hardware registers rather than kernel-owned data. Address-decoder, arbitration, throttle, and GDS partition settings survive as device register state until reset, reinitialization, suspend/resume restoration, or another write changes them. Counter registers and fault/status registers reflect mutable hardware state and may be clear-on-write or latch-like depending on the hardware contract, which is not encoded in this header.

## Dependencies

The masks depend on the GC 9.4.2 register specification and must remain synchronized with:

- `gc_9_4_2_offset.h`, which supplies the register addresses and base indices for the same symbolic names.
- AMDGPU SOC15 register access helpers in the driver (`SOC15_REG_OFFSET`, `WREG32_SOC15`, `RREG32_SOC15`, `WREG32_SOC15_OFFSET`).
- Field helper macros such as `REG_SET_FIELD`, which derive the shift and mask macro names from the register and field tokens.
- Firmware and hardware initialization expectations for GCEA, CAC/DIDT, EDC, and GDS blocks.

The file is independent of Ceph or distributed-filesystem logic despite residing under the repository's source mirror. It is part of the imported AMD Linux DRM driver tree.

## Risks

The main risk is silent hardware misprogramming. A wrong shift or mask can write a neighboring bitfield while leaving C compilation successful. The highest-risk groups are address decode (`GCEA_ADDRDEC*`), throttling/power brake (`GC_THROTTLE*`), and per-VMID GDS partitioning (`GDS_VMID*`, `GDS_GWS_VMID*`, `GDS_OA_VMID*`) because they affect memory routing, power throttling behavior, and process/queue resource isolation.

The repeated register families are easy to update inconsistently. `GCEA_ADDRDEC0`, `GCEA_ADDRDEC1`, and `GCEA_ADDRDEC2` have nearly identical field layouts; a generator or manual patch that changes only one instance would create hard-to-debug ASIC-specific behavior. The same applies to the 16 VMID base/size/GWS/OA families.

Generated-header skew is another risk. If `gc_9_4_2_offset.h` and `gc_9_4_2_sh_mask.h` come from different hardware-description revisions, field updates may be paired with the wrong register addresses. Because the driver often builds register names from tokens, this can appear as correct source-level code while targeting an incorrect raw register or bit range.

The chunk boundary itself is a documentation risk: it starts after the first `GCEA_ADDRDEC_MISC_CFG` field definitions and ends before all `GDS_OA_VMID*` registers are listed. Any final per-file research should reconcile this chunk with adjacent chunks before claiming a complete register inventory.

## Test Signals

Useful build-time signals are successful compilation of GC 9.4.2 AMDGPU code and absence of `REG_SET_FIELD` macro-expansion failures for fields such as `GC_THROTTLE_CTRL1.PWRBRK_STALL_EN`, `GDS_GWS_VMID0.SIZE`, and GDS/GCEA EDC counters. A header-name or field-name mismatch should fail compilation where a field is used directly.

Runtime validation requires hardware or emulator coverage. Signals include successful GC 9.4.2 device initialization, stable suspend/resume, no GDS/GWS allocation faults under KFD/compute workloads, correct RAS/EDC counter reads for GDS and GCEA registers, and no unexpected GCEA address decode, GDS protection, or VM protection fault reports. For power-brake coverage, the `gfx_v9_4_2_set_power_brake_sequence()` path should program `regGC_THROTTLE_CTRL`, `regGC_THROTTLE_CTRL1`, and the CAC indirect power-brake stall pattern without register-access faults.
