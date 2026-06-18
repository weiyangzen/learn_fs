# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002755`: lines 1-2457, `Docs/researches/chunks/subset-b-002755_research.md`
- `subset-b-002756`: lines 2458-4934, `Docs/researches/chunks/subset-b-002756_research.md`
- `subset-b-002757`: lines 4935-5125, `Docs/researches/chunks/subset-b-002757_research.md`

## Chunk Research

### subset-b-002755: lines 1-2457

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_offset.h lines 1-2457

## Scope

This chunk covers the first 2,457 lines of the generated-style AMD MMHUB 1.7 register offset header. It contains the AMD license, an include guard, and 2,400 `#define` symbols for MMHUB register offsets and their `_BASE_IDX` values.

The range is entirely preprocessor metadata. There are no functions, structs, enums, includes, variables, allocations, locks, loops, callbacks, or runtime branches. Although the source tree path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware register metadata, not Ceph filesystem logic.

The chunk contains these address blocks:

- `mmhub_dagb_dagbdec0` through `mmhub_dagb_dagbdec5`, base addresses `0x68000` through `0x68a00`.
- `mmhub_ea_mmeadec0`, base address `0x68c00`.
- Most of `mmhub_ea_mmeadec1`, base address `0x69100`.

The selected range ends at `regMMEA1_ADDRDEC_SELECT_BASE_IDX` on line 2457. The immediately following lines define `regMMEA1_EDC_CNT3`, `regMMEA1_MISC_AON`, and then begin `mmhub_ea_mmeadec2`, so full-file research must reconcile this chunk with later chunks before treating the MMEA1 and MMEA2+ domains as complete.

## Purpose

`mmhub_1_7_offset.h` provides symbolic register-offset names for AMDGPU's MMHUB 1.7 IP block. Driver code uses these names with SOC15 register access helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_OFFSET`, `WREG32_SOC15_OFFSET`, `SOC15_REG_ENTRY`, and `SOC15_REG_OFFSET` to compute MMIO addresses without hard-coding raw offsets at call sites.

The `DAGB` blocks describe duplicated data/address gateway decode instances. Each instance exposes read and write client registers, request/return path controls, virtual-channel controls, credit counters, pending-state registers, snoop override registers, fatal-error status/clear registers, FIFO fullness/emptiness status, performance-counter registers, and reserve slots.

The `MMEA` blocks describe MMHUB external-address/address-decoder instances. They expose DRAM/GMI/IO client-to-group maps, group-to-virtual-channel maps, lazy timers, CAM/page-burst controls, priority/urgency registers, address-normalization base/limit/offset/mega-region registers, address-decoder chip-select and row/column/rank-selection registers, SDP arbitration/priority/credit registers, latency/performance counters, EDC counters, DSM controls, clock-gating controls, error status, and address-decoder selection.

## Important APIs, Types, And Constants

The exported interface is entirely compile-time constants:

- Register names use the `reg<block>_<register>` pattern and map to MMHUB register offsets, not byte addresses. SOC15 helpers combine these offsets with the MMHUB IP base/index metadata.
- Every register offset in this chunk is paired with a `<name>_BASE_IDX` definition. All base indexes in this range are `0`, which ties these symbols to MMHUB base index 0 for this IP version.
- The six complete `DAGB` instances each contribute 128 register-offset defines and 128 base-index defines. Their offset windows are regular: `DAGB0` starts at `0x0000`, `DAGB1` at `0x0080`, through `DAGB5` at `0x0280`.
- Important `DAGB` families include `RDCLI0..15`, `WRCLI0..15`, `RD_CNTL`, `WR_CNTL`, `RD_GMI_CNTL`, `WR_GMI_CNTL`, `RD_ADDR_DAGB`, `WR_ADDR_DAGB`, `WR_DATA_DAGB`, `*_MAX_BURST*`, `*_LAZY_TIMER*`, `RD_VC0..7_CNTL`, `WR_VC0..7_CNTL`, `*_TLB_CREDIT`, `*_CREDIT_CNTL`, `*_PENDING`, `WRCLI_GPU_SNOOP_OVERRIDE`, `FATAL_ERROR_*`, `FIFO_*`, `PERFCOUNTER_*`, and `L1TLB_REG_RW`.
- `MMEA0` contributes a complete address-decoder block in this chunk, from `regMMEA0_DRAM_RD_CLI2GRP_MAP0` at `0x0300` through `regMMEA0_MISC_AON` at `0x0415`.
- `MMEA1` contributes most of the next address-decoder block, from `regMMEA1_DRAM_RD_CLI2GRP_MAP0` at `0x0440` through `regMMEA1_ADDRDEC_SELECT` at `0x0553`. The chunk omits the following `MMEA1_EDC_CNT3` and `MMEA1_MISC_AON` definitions.
- Important `MMEA` families include DRAM/GMI/IO `*_CLI2GRP_MAP*`, `*_GRP2VC_MAP`, `*_LAZY`, `*_CAM_CNTL`, priority age/queue/fixed/urgency/quantum registers, `ADDRNORM_*`, `ADDRDEC*_*`, `SDP_*`, `PERFCOUNTER_*`, `EDC_CNT*`, `DSM_CNTL*`, `CGTT_CLK_CTRL`, `EDC_MODE`, `ERR_STATUS`, `MISC*`, and `ADDRDEC_SELECT`.

## Control Flow

This header has no direct control flow. The implied driver flow is:

1. `mmhub_v1_7.c` includes this offset header and `mmhub_1_7_sh_mask.h`.
2. MMHUB setup, power-management, RAS, and diagnostic code chooses symbolic register names from this header.
3. SOC15 register macros combine the selected offset with MMHUB IP-instance/base-index metadata.
4. Driver code reads, writes, polls, or records the resulting MMIO register address.

Concrete consumers in `mmhub_v1_7.c` include:

- Snoop override initialization computes the distance between `regDAGB1_WRCLI_GPU_SNOOP_OVERRIDE` and `regDAGB0_WRCLI_GPU_SNOOP_OVERRIDE`, then iterates DAGB instances with `RREG32_SOC15_OFFSET`/`WREG32_SOC15_OFFSET`.
- Medium-grain clock gating reads and updates `regDAGB0_CNTL_MISC2` and `regDAGB1_CNTL_MISC2` using bit masks from the companion shift/mask header.
- RAS field tables use `regMMEA0_EDC_CNT`, `regMMEA0_EDC_CNT2`, `regMMEA0_EDC_CNT3`, `regMMEA1_EDC_CNT`, `regMMEA1_EDC_CNT2`, `regMMEA1_EDC_CNT3`, and related `ERR_STATUS` registers to query and reset MMHUB error counters.

All sequencing, error handling, locking, and hardware state transitions live in the C driver and MMIO helper layers, not in this header.

## State And Persistence Behavior

The file itself is stateless and persistent only as source metadata. Its constants describe hardware state locations.

When surrounding AMDGPU code writes DAGB registers, state can persist in the MMHUB until reset, power-gated, or explicitly reprogrammed. Examples include snoop override bits, clock-gating controls, read/write path controls, virtual-channel controls, credit settings, and fatal-error clear/status behavior.

MMEA address-normalization and address-decoder registers define how physical address ranges, DRAM/GMI/IO routing, chip-select mapping, rank/row/column selection, harvesting, holes, and non-power-of-two channel behavior are interpreted. Wrong persisted values can route memory traffic incorrectly or make diagnostic counters point at the wrong memory path.

MMEA EDC and error-status registers are diagnostic state. `mmhub_v1_7.c` reads EDC counters for correctable/uncorrectable error reporting and resets the counters by writing zero when MMHUB RAS is supported. The counters are not owned by this header, but the offsets here decide which hardware counters the driver reads or clears.

Performance-counter registers in the DAGB and MMEA blocks are dynamic hardware observations controlled by adjacent `PERFCOUNTER*_CFG` and result-control registers. Incorrect offsets can produce plausible-looking but wrong performance data.

## Dependencies And Integration Points

This header depends on the MMHUB 1.7 register database remaining synchronized with the companion `mmhub_1_7_sh_mask.h` field definitions and the SOC15 MMHUB IP-base table. The constants are meaningful only when used with matching MMHUB 1.7 hardware.

Key integration points are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.c`, which includes this header directly and uses these symbols for MMHUB initialization, cache/TLB setup, DAGB snoop override, clock gating, RAS/EDC counter reporting, and error-status reads.
- SOC15 register helper macros that translate `reg...` offsets and `_BASE_IDX` data into actual MMIO addresses.
- The companion shift/mask header, which provides bit positions and masks for the registers named here.
- AMDGPU GMC/VM code, because MMHUB register programming affects GPU virtual memory apertures, page-table access, protection-fault handling, memory routing, and cache/TLB behavior.
- AMDGPU RAS code, because the `MMEA*_EDC_CNT*` and `MMEA*_ERR_STATUS` offsets feed correctable/uncorrectable error accounting.
- Power-management and clock-gating paths, because `DAGB*_CNTL_MISC2`, `MMEA*_CGTT_CLK_CTRL`, and related registers participate in MMHUB gating behavior.

The chunk also has cross-version coupling by naming convention. Other MMHUB versions carry similarly named `regDAGB*` and `regMMEA*` symbols with different offsets or base indexes, so include selection must match the active IP version.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong offset or stale `_BASE_IDX` compiles successfully but makes the driver read or write the wrong MMHUB register.
- The `DAGB` windows are regular, and driver code relies on offset deltas between instances. If a later ASIC revision breaks spacing but code still computes instance offsets from `DAGB1 - DAGB0`, snoop override or diagnostics could target the wrong instance.
- The chunk boundary is inside `MMEA1`. Research or validation based only on this chunk must not assume MMEA1 is complete, because `EDC_CNT3` and `MISC_AON` appear immediately after line 2457.
- All symbols are preprocessor macros in the global namespace. Including multiple generated headers for different MMHUB versions in one C translation unit can create name collisions or accidental version mixing.
- RAS paths are sensitive to offset accuracy. A wrong `MMEA*_EDC_CNT*` or `ERR_STATUS` offset can undercount, overcount, misattribute, or incorrectly clear memory error telemetry.
- Address-normalization and address-decoder registers are hardware-routing controls. Misprogramming them can cause memory corruption, VM faults, bad GMI/DRAM/IO routing, or failures that look like unrelated GPU hangs.
- Pending, FIFO, credit, and fatal-error status registers are often used for debug and recovery. Bad definitions can hide real deadlocks or make recovery code diagnose the wrong sub-block.
- `_BASE_IDX` values are all zero in this chunk; accidentally copying definitions from a different MMHUB version with a different base index would silently change SOC15 address calculation.

## Test Signals

Useful validation signals include:

- AMDGPU kernel build coverage for `mmhub_v1_7.c` with this header and `mmhub_1_7_sh_mask.h`.
- Mechanical comparison against AMD's authoritative MMHUB 1.7 register database for every offset and `_BASE_IDX` in lines 1-2457.
- Static checks that repeated `DAGB0..5` windows have the expected stride and identical register families where the hardware database says they should.
- Cross-checks that every `reg...` symbol used by `mmhub_v1_7.c` is defined by the matching MMHUB 1.7 offset header, and every `SOC15_REG_FIELD` use has a matching shift/mask definition.
- Boot and initialization tests on MMHUB 1.7 hardware, especially VM/GART setup, page-table access, TLB/cache initialization, and protection-fault default-address behavior.
- Snoop override validation for SDMA writes, because `mmhub_v1_7_init_snoop_override_regs()` depends on the DAGB instance spacing and the `WRCLI_GPU_SNOOP_OVERRIDE` offsets.
- Clock-gating tests that toggle medium-grain clock gating and light sleep, then verify no MMHUB access failures, hangs, or incorrect gating-state reporting.
- RAS tests or fault-injection runs that exercise `MMEA0` and `MMEA1` EDC counters and `ERR_STATUS` registers, checking that correctable and uncorrectable counts are attributed to the expected sub-blocks.
- Performance-counter smoke tests for DAGB and MMEA counters under targeted memory traffic, looking for nonzero and plausible counter movement.
- Runtime warning signs include GPU VM faults during normal memory traffic, failed GART/VRAM aperture setup, SDMA coherency issues, unexpected MMHUB RAS counts, unchanging performance counters, bad error-status attribution, or GPU hangs around MMHUB clock-gating transitions.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002755`. It covers lines 1-2457 of `mmhub_1_7_offset.h`. The final per-file research should merge this with later chunks to complete the remaining `MMEA1` tail, `MMEA2+` address-decoder blocks, VM/L2/ATC/MC registers, and the closing include guard.

### subset-b-002756: lines 2458-4934

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_offset.h lines 2458-4934

## Scope

This chunk covers the middle-to-late portion of the generated MMHUB 1.7 register offset header. It starts with the tail of the `MMEA1` range at `regMMEA1_EDC_CNT3` and `regMMEA1_MISC_AON`, then covers complete `MMEA2` through `MMEA5` address blocks, MMHUB L1 TLB status and performance counter offsets, PCTL deep-sleep/power-control offsets, ATC L2 and L2 TLB offsets, VM L2 control/fault/performance offsets, and the beginning of the VM-context register table through `regVM_CONTEXT13_PAGE_TABLE_END_ADDR_HI32`.

The chunk contains preprocessor constants only. Each hardware register is represented by a `reg...` offset macro plus a matching `reg..._BASE_IDX` macro. There are no C functions, structs, variables, executable control flow, or software storage in this header section.

Covered address blocks include:

- `mmhub_ea_mmeadec2` at base address `0x69600`, 217 register offsets from `regMMEA2_DRAM_RD_CLI2GRP_MAP0` through `regMMEA2_MISC_AON`.
- `mmhub_ea_mmeadec3` at base address `0x69b00`, 217 register offsets with the same layout for `MMEA3`.
- `mmhub_ea_mmeadec4` at base address `0x6a000`, 217 register offsets with the same layout for `MMEA4`.
- `mmhub_ea_mmeadec5` at base address `0x6a500`, 217 register offsets with the same layout for `MMEA5`.
- `mmhub_l1tlb_vml1dec`, `mmhub_l1tlb_vml1pldec`, and `mmhub_l1tlb_vml1prdec` for L1 TLB status and counters.
- `mmhub_pctldec0` for MMHUB power-control and slice deep-sleep control.
- `mmhub_utcl2_atcl2dec`, `mmhub_utcl2_atcl2pfcntldec`, and `mmhub_utcl2_atcl2pfcntrdec` for ATC L2 control, status, cache data, DSM, clock, and performance counters.
- `mmhub_utcl2_l2tlbdec`, `mmhub_utcl2_l2tlbpldec`, and `mmhub_utcl2_l2tlbprdec` for L2 TLB status, GPUVA/VMID translation-assist windows, and L2 TLB counters.
- `mmhub_utcl2_vml2pfdec`, `mmhub_utcl2_vml2pldec`, `mmhub_utcl2_vml2prdec`, and `mmhub_utcl2_vml2vcdec` for VM L2 control, protection-fault, invalidation, per-context, and page-table aperture registers.

## Purpose

This header section provides the address portion of the MMHUB 1.7 MMIO ABI used by AMDGPU code. The offset macros are consumed by SOC15 register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `SOC15_REG_OFFSET`, `SOC15_REG_ENTRY`, and `SOC15_REG_ENTRY_OFFSET`. The sibling `mmhub_1_7_sh_mask.h` header supplies the field masks and shifts for many of the same register names, while this file tells the driver where the registers live within the MMHUB IP block.

For MMHUB, these offsets are central to memory-management bring-up: framebuffer and AGP aperture setup, GART page-table base programming, VMID context ranges, VM invalidation request/ack windows, L1/L2 TLB control, MMHUB RAS error counting, ATC/L2 status, and clock/power-management hooks.

## Important Macro Families

### MMEA2 Through MMEA5 Address-Decode Ranges

The dominant part of the chunk is four repeated MMEA address-decode blocks, `MMEA2`, `MMEA3`, `MMEA4`, and `MMEA5`. Each block has the same 217-register shape. The major groups are:

- DRAM read/write client-to-group, group-to-VC, lazy, CAM, page-burst, priority-age, priority-queueing, fixed-priority, urgency, and priority-quantum registers.
- GMI read/write equivalents, including urgency masking.
- Address-normalization windows: base, limit, offset, megabase, megalimit, DRAM/GMI hole controls, and non-power-of-two channel configuration.
- Address-decode controls for bank/misc configuration, DRAM/GMI harvest enable, base addresses, address masks, address configuration, address selection, MAM, and secondary chip-select entries.
- XGMI decode link and hash/offset controls.
- DRAM and GMI page-insert controls.
- Channel and address-index multiplexing controls.
- Clock-gating, EDC mode, error status, corrected/uncorrected error status, EDC counters, and always-on miscellaneous registers.

The repeated layout matters because driver code and diagnostics often treat these ranges as an indexed hardware family. `amdgpu/mmhub_v1_7.c` builds RAS tables over `regMMEA2_EDC_CNT`, `regMMEA3_EDC_CNT`, `regMMEA4_EDC_CNT`, `regMMEA5_EDC_CNT`, matching `EDC_CNT2`/`EDC_CNT3`, and the corresponding `ERR_STATUS` registers.

### L1 TLB and L1 Performance Counter Offsets

The L1 TLB section defines status offsets for `regMC_VM_MX_L1_TLB0_STATUS` through `regMC_VM_MX_L1_TLB7_STATUS`. It also defines `regMC_VM_MX_L1_PERFCOUNTER0_CFG` through `regMC_VM_MX_L1_PERFCOUNTER3_CFG`, `regMC_VM_MX_L1_PERFCOUNTER_RSLT_CNTL`, and the low/high counter result registers.

The actual L1 TLB control register used by `mmhub_v1_7_init_tlb_regs()` appears outside this chunk, but these status and counter windows are part of the same MMHUB VM front end. They support debug, profiling, and validation of TLB activity after the driver enables the L1 TLB and advanced driver model.

### PCTL0 Power-Control Offsets

`PCTL0` covers MMHUB deep-sleep and slice controls:

- Global control and deep-sleep override registers.
- Power-gating ignore controls.
- Per-slice `CFG_DAGB_BUSY`, `CFG_DS_ALLOW`, `CFG_DS_ALLOW_IB`, and `SLICE*_MISC` offsets for slices 0 through 5.
- `regPCTL0_UTCL2_MISC` for shared UTCL2-related power-control state.

These offsets are integration points for clock-gating, deep-sleep, and power-management paths. Their values are hardware control-plane state, not persistent software state.

### ATC L2 and L2 TLB Offsets

The ATC L2 block exposes control, status, cache data, DSM, memory power, clock, and MM group real-time-class registers:

- `regATC_L2_CNTL`, `regATC_L2_CNTL2`, `regATC_L2_CNTL3`, and `regATC_L2_CNTL4`.
- `regATC_L2_STATUS` and `regATC_L2_STATUS2`.
- `regATC_L2_CACHE_DATA0..3`, plus 4K, 32K, and 2M DSM index/control registers.
- `regATC_L2_MISC_CG`, `regATC_L2_MEM_POWER_LS`, and `regATC_L2_CGTT_CLK_CTRL`.
- ATC L2 performance counter configuration and low/high result registers.

`amdgpu/mmhub_v1_7.c` reads and writes `regATC_L2_MISC_CG` in medium-grain clock-gating updates, so offset drift here can break power-management behavior even though the header itself has no logic.

The L2 TLB block defines `regL2TLB_TLB0_STATUS`, GPUVA/VMID translation-assist request and response low/high registers, plus L2 TLB performance-counter config/result offsets.

### VM L2 Control, Fault, and Performance Offsets

The VM L2 block includes:

- VM L2 controls and status: `regVM_L2_CNTL`, `regVM_L2_CNTL2`, `regVM_L2_CNTL3`, and `regVM_L2_STATUS`.
- Dummy page fault control and address registers.
- protection-fault default address, status, control, control2, and instance registers.
- Context invalidate control, invalidate request, acknowledge, and per-engine address-range low/high registers.
- UTCL2 EDC mode/status/config and VM L2 performance counters.

`mmhub_v1_7_init()` records several of these offsets into `adev->vmhub[AMDGPU_MMHUB0(0)]`, including the first invalidation request/ack registers and protection-fault status/control registers. It also computes invalidate-engine spacing from adjacent offset macros. That makes the exact numeric progression of `regVM_INVALIDATE_ENG0_REQ`, `regVM_INVALIDATE_ENG1_REQ`, and the address-range offsets part of the driver's implicit contract.

### VM Context and Page-Table Aperture Offsets

The `mmhub_utcl2_vml2vcdec` section begins the per-VMID context table. This chunk includes:

- `regVM_CONTEXT0_CNTL` through `regVM_CONTEXT15_CNTL`.
- `regVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32/HI32` through context 15.
- `regVM_CONTEXT0_PAGE_TABLE_START_ADDR_LO32/HI32` through context 15.
- `regVM_CONTEXT0_PAGE_TABLE_END_ADDR_LO32/HI32` through context 13 high; contexts 14 and 15 end-address registers continue in the next chunk.

These offsets are directly used by `mmhub_v1_7_setup_vm_pt_regs()` and `mmhub_v1_7_init_gart_aperture_regs()`. The driver writes context 0 page-table base, start, and end registers during GART setup and computes `ctx_addr_distance` as the difference between context 1 and context 0 page-table base offsets.

## Control Flow and State Behavior

This chunk has no runtime control flow. It changes behavior by defining compile-time constants that driver code uses to address MMIO registers.

The persistent state described by the macros is hardware state:

- MMEA DRAM/GMI routing, address-normalization, address-decode, harvest, XGMI, page-insert, clock-gating, and EDC/RAS state.
- L1 and L2 TLB status and performance counter configuration/result state.
- MMHUB PCTL deep-sleep and slice power-control state.
- ATC L2 cache, DSM, clock-gating, memory power, and performance counter state.
- VM L2 control, fault-default-address, fault status/control, invalidation request/ack, invalidate address ranges, and EDC state.
- Per-VMID context controls, page-table base addresses, and page-table virtual address ranges.

Some registers are durable configuration while others are status, counters, request/ack windows, or error latches. The header does not encode ordering, polling, reset, privilege, or timeout rules. Those rules live in the AMDGPU MMHUB implementation and hardware documentation.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header convention:

- `mmhub_1_7_sh_mask.h` supplies masks and shifts for field-level access to many registers named here.
- `soc15_common.h` and `soc15.h` provide the SOC15 register access macros that combine IP block, instance, base index, and offset.
- `amdgpu/mmhub_v1_7.c` includes this header directly and is the primary local consumer in this source tree.

Observed integration points include:

- `mmhub_v1_7_get_fb_location()`, which reads `regMC_VM_FB_LOCATION_BASE` and `regMC_VM_FB_LOCATION_TOP` from adjacent VM aperture definitions.
- `mmhub_v1_7_setup_vm_pt_regs()`, which writes `regVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32/HI32` plus a VMID-scaled offset.
- `mmhub_v1_7_init_gart_aperture_regs()`, which writes context 0 page-table start/end registers covered by this chunk.
- `mmhub_v1_7_init_system_aperture_regs()`, which uses VM L2 protection-fault default/control registers in this register family.
- `mmhub_v1_7_init()`, which stores VM hub offsets and computes context and invalidate-engine register distances from adjacent macros.
- `mmhub_v1_7_update_medium_grain_clock_gating()`, which accesses `regATC_L2_MISC_CG`.
- MMHUB RAS tables in `mmhub_v1_7.c`, which reference `MMEA2` through `MMEA5` EDC counters and error-status registers from this chunk.

The same source tree also has `mmhub_v1_8.c` and `mmhub_1_8_0_offset.h` with similar but not identical register offsets. Consumers must include the matching MMHUB generation; copying an offset between generations can silently address the wrong register.

## Risks

- Offset drift is high impact. A wrong numeric offset can make the driver read or write a different MMHUB register while still compiling cleanly.
- The repeated `MMEA2` through `MMEA5` blocks are mechanically similar. A single copied prefix or skipped offset can corrupt RAS accounting, address decoding, or memory-routing diagnostics for only one range.
- RAS integration depends on matching offset and mask headers. `SOC15_REG_ENTRY(MMHUB, 0, regMMEA*_EDC_CNT*)` pairs with `SOC15_REG_FIELD(MMEA*_EDC_CNT*, ...)`; mismatched names or generations can produce incorrect SEC/DED counts.
- VM context spacing is assumed by code, not individually enumerated at every call site. If `regVM_CONTEXT1_PAGE_TABLE_BASE_ADDR_LO32 - regVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32` changes unexpectedly, VMID page-table programming can target the wrong context.
- Invalidate-engine spacing is similarly inferred from adjacent macros. Bad `regVM_INVALIDATE_ENG*` offsets can break TLB invalidation and lead to stale translations.
- Page-table base, start, and end registers split 64-bit address state into low/high 32-bit registers. Address shift errors in callers or wrong offsets in this header can expose invalid virtual memory ranges.
- PCTL and ATC clock-gating offsets touch power-management state. Incorrect offsets can cause hangs, missed idle states, or power regressions that are hard to attribute to a generated header.
- The chunk ends mid-family at `regVM_CONTEXT13_PAGE_TABLE_END_ADDR_HI32`; the final merged report must connect it to the next chunk for context 14/15 end-address registers and later VM aperture registers.

## Test and Validation Signals

Useful validation is mostly integration and hardware-facing:

- Build AMDGPU with MMHUB 1.7 enabled to catch missing or renamed offset macros.
- Exercise GART and VM bring-up paths that program context 0 page-table base/start/end registers.
- Run VM invalidation tests or GPU workloads that require page-table updates; failures may implicate `regVM_INVALIDATE_ENG*` request/ack/address-range offsets or context distance calculations.
- Validate suspend/resume, reset, and medium-grain clock-gating paths that read or write ATC/PCTL clock and power-control registers.
- Query and reset MMHUB RAS counters, checking `MMEA2` through `MMEA5` SEC/DED counts and `ERR_STATUS` handling.
- Use fault-injection or invalid-address tests to verify VM L2 protection-fault default address, status, and control paths.
- Run performance/debug validation for L1 TLB, ATC L2, L2 TLB, and VM L2 performance counters to confirm counter config/result offsets match the hardware.
- Compare generated `mmhub_1_7_offset.h` against the authoritative register database during header regeneration, especially around repeated MMEA blocks and the VM context table.

## Unresolved Cross-Chunk References

The chunk starts after most of the `MMEA1` block has already been defined and only includes the `MMEA1_EDC_CNT3` and `MMEA1_MISC_AON` tail. It also stops before the VM context table is complete: `VM_CONTEXT14_PAGE_TABLE_END_ADDR_*`, `VM_CONTEXT15_PAGE_TABLE_END_ADDR_*`, and later VM/MC aperture registers are in the following chunk. The merge/reconciliation lane should stitch those neighboring chunks together for the final per-file report.

### subset-b-002757: lines 4935-5125

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_offset.h lines 4935-5125

## Scope

This chunk covers the final 191 lines of the generated AMD MMHUB 1.7 register offset header. It starts at the tail of the `VM_CONTEXT13/14/15_PAGE_TABLE_END_ADDR_*` context range, then covers the complete `mmhub_utcl2_vmsharedhvdec`, `mmhub_utcl2_vmsharedpfdec`, and `mmhub_utcl2_vmsharedvcdec` offset blocks before the closing `#endif`.

The range contains 177 `#define` macros. Each register offset is paired with a `_BASE_IDX` macro, and every `_BASE_IDX` in this slice is `0`. There are no C functions, types, inline helpers, storage objects, or executable statements.

## Purpose

`mmhub_1_7_offset.h` is a generated hardware-register map for the AMDGPU MMHUB 1.7 block. This tail slice provides symbolic register numbers for VM context address bounds, per-VF framebuffer sizing, MARC remap windows, PCIe ATS controls, virtualization/shared-function state, PF aperture setup, VC framebuffer/AGP/system aperture setup, and MMHUB L1 TLB control.

The header exists so MMHUB 1.7 driver code can use `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET` with named `reg...` constants instead of raw register offsets. The matching field definitions live in `mmhub_1_7_sh_mask.h`; this file supplies addresses only.

## Important APIs, Types, And Data

The exported API is the preprocessor namespace of register-offset constants:

- `regVM_CONTEXT14_PAGE_TABLE_END_ADDR_LO32/HI32` and `regVM_CONTEXT15_PAGE_TABLE_END_ADDR_LO32/HI32` finish the VMID page-table range-address register family. The first line is the `_BASE_IDX` for `regVM_CONTEXT13_PAGE_TABLE_END_ADDR_HI32`, showing this chunk begins mid-family.
- `regMC_VM_FB_SIZE_OFFSET_VF0` through `regMC_VM_FB_SIZE_OFFSET_VF15` describe per-virtual-function framebuffer size/offset registers in `mmhub_utcl2_vmsharedhvdec`.
- `regMC_VM_MARC_BASE_LO/HI_0..3`, `regMC_VM_MARC_RELOC_LO/HI_0..3`, and `regMC_VM_MARC_LEN_LO/HI_0..3` define four MARC base, relocation, and length windows.
- `regVM_PCIE_ATS_CNTL` and `regVM_PCIE_ATS_CNTL_VF_0..15` define PF/global and per-VF PCIe ATS control registers. The companion mask header gives the global `STU` and `ATC_ENABLE` fields and per-VF `ATC_ENABLE` fields.
- `regMC_SHARED_ACTIVE_FCN_ID` and `regMC_VM_XGMI_GPUIOV_ENABLE` expose shared active-function identity and XGMI GPU-IOV enable state.
- `regMC_VM_FB_OFFSET`, `regMC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_LSB/MSB`, `regMC_VM_STEERING`, `regMC_SHARED_VIRT_RESET_REQ`, `regMC_MEM_POWER_LS`, `regMC_VM_CACHEABLE_DRAM_ADDRESS_START/END`, `regMC_VM_APT_CNTL`, `regMC_VM_LOCAL_HBM_ADDRESS_START/END`, `regMC_VM_LOCAL_HBM_ADDRESS_LOCK_CNTL`, `regUTCL2_CGTT_CLK_CTRL`, `regMC_VM_XGMI_LFB_CNTL`, `regMC_VM_XGMI_LFB_SIZE`, `regMC_VM_CACHEABLE_DRAM_CNTL`, and `regMC_VM_HOST_MAPPING` are PF/shared aperture and memory-location controls.
- `regMC_VM_FB_LOCATION_BASE/TOP`, `regMC_VM_AGP_TOP/BOT/BASE`, `regMC_VM_SYSTEM_APERTURE_LOW_ADDR/HIGH_ADDR`, and `regMC_VM_MX_L1_TLB_CNTL` are VC aperture and L1 TLB control registers used by MMHUB setup paths.

The numeric offsets in this chunk run from the context tail near `0x0c87` through `0x0d1d`, with PF and VC blocks using lower offsets such as `0x0cab` through `0x0cc7`. The address-block comments identify the hardware decode domains and their base addresses: `0x6b380`, `0x6b290`, and `0x6b300`.

## Control Flow

This header has no runtime control flow. Runtime behavior appears when C code includes this offset header and combines the macros with SOC15 MMIO helpers:

1. `amdgpu/mmhub_v1_7.c` includes `mmhub/mmhub_1_7_offset.h` and `mmhub/mmhub_1_7_sh_mask.h`.
2. Initialization reads framebuffer location registers with `RREG32_SOC15(MMHUB, 0, regMC_VM_FB_LOCATION_BASE/TOP)` and stores the derived byte addresses in `adev->gmc.fb_start` and `adev->gmc.fb_end`.
3. GART/system aperture setup writes `regMC_VM_AGP_*`, `regMC_VM_SYSTEM_APERTURE_LOW_ADDR/HIGH_ADDR`, `regMC_VM_FB_LOCATION_*`, `regMC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_LSB/MSB`, and protection-fault defaults.
4. TLB setup reads and writes `regMC_VM_MX_L1_TLB_CNTL`, using fields from the companion mask header to enable L1 TLB, advanced driver model, MTYPE, system access mode, and ATC.
5. VMID setup loops over contexts through `WREG32_SOC15_OFFSET` using offsets and spacing computed elsewhere in `mmhub_v1_7_init()`. The `VM_CONTEXT14/15_PAGE_TABLE_END_ADDR_*` constants in this chunk are the tail of that contiguous context-address register layout.

Many macros in the hypervisor/PF shared blocks are not directly referenced by current `mmhub_v1_7.c`, but they are still part of the generated ABI for SR-IOV, ATS, XGMI, MARC, and aperture programming paths.

## State And Persistence Behavior

The macros are compile-time constants and do not persist state. The registers they name hold persistent GPU hardware state:

- VM context page-table end addresses bound the legal GPU virtual address range for VMIDs. MMHUB setup writes these during GART enable and leaves them active until reset, suspend/resume restore, GPU reset, or GART disable changes context state.
- Framebuffer, AGP, system aperture, default page, cacheable DRAM, local HBM, host-mapping, and XGMI LFB registers define address routing for MMHUB memory accesses. Incorrect values persist in hardware and affect translations until rewritten.
- `MC_VM_MX_L1_TLB_CNTL` controls TLB behavior and ATC participation. MMHUB enable programs it; GART disable clears key enable bits.
- Per-VF framebuffer offset/size, ATS, active-function, virtual-reset, and XGMI GPU-IOV registers describe virtualization state. They are hardware-visible isolation and routing controls, not normal kernel memory.
- MARC windows define base, relocation, and length state for memory remapping windows. These are long-lived aperture descriptors once programmed.

There is no disk state, reference counting, locking, allocation, or software-owned lifetime in this header. Ordering, locking, reset handling, and SR-IOV policy are responsibilities of the MMHUB/GMC/virtualization callers.

## Dependencies

This chunk depends on the generated MMHUB 1.7 register specification and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_sh_mask.h`, which defines bit fields for the same register names, including `MC_VM_FB_SIZE_OFFSET_VF*`, `MC_VM_MARC_*`, `VM_PCIE_ATS_CNTL*`, `MC_VM_FB_OFFSET`, `MC_VM_XGMI_LFB_CNTL`, `MC_VM_HOST_MAPPING`, and `MC_VM_MX_L1_TLB_CNTL`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.c`, the primary local MMHUB 1.7 consumer.
- AMDGPU SOC15 helpers and register-addressing macros such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, and `REG_GET_FIELD`.
- AMDGPU GMC state in `struct amdgpu_device`, especially `adev->gmc.fb_start`, `fb_end`, `agp_start`, `agp_end`, `gart_start`, `gart_end`, `pdb0_bo`, `translate_further`, `xgmi.connected_to_cpu`, and VM manager geometry.

The `_BASE_IDX` values are part of SOC15 register-address calculation. They are all zero in this slice, but callers still rely on the generated form being present and consistent.

## Integration Points

- `mmhub_v1_7_get_fb_location()` reads `regMC_VM_FB_LOCATION_BASE/TOP`, masks the 24-bit fields via the companion mask header, shifts by 24, and publishes the resulting VRAM aperture to `adev->gmc`.
- `mmhub_v1_7_init_system_aperture_regs()` programs `regMC_VM_AGP_BASE/BOT/TOP`, `regMC_VM_SYSTEM_APERTURE_LOW_ADDR/HIGH_ADDR`, optionally disables FB/AGP apertures when `pdb0_bo` is used, and writes `regMC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_LSB/MSB`.
- `mmhub_v1_7_init_tlb_regs()` programs `regMC_VM_MX_L1_TLB_CNTL` for L1 TLB enablement, system access mode, advanced driver model, MTYPE, unmapped-access behavior, and ATC enable.
- `mmhub_v1_7_setup_vmid_config()` programs VM context page-table start/end registers for VMIDs 1-15 using contiguous context register spacing; the context end-address tail in this chunk is part of that range.
- SR-IOV and virtualization integration is represented by the per-VF framebuffer, ATS, active-function, virtual-reset, and XGMI GPU-IOV registers. Some of these are reserved for PF/hypervisor flows and may be programmed by firmware or host-side code rather than by normal VF driver paths.
- XGMI and large-framebuffer integration is represented by `regMC_VM_XGMI_LFB_CNTL`, `regMC_VM_XGMI_LFB_SIZE`, and `regMC_VM_XGMI_GPUIOV_ENABLE`, which describe large-framebuffer and GPU-IOV routing state for multi-GPU or CPU-connected fabrics.

## Risks

- Offset drift is the central risk. If a generated `reg...` value does not match the MMHUB 1.7 hardware spec, the driver can read or write the wrong register while still compiling cleanly.
- The chunk begins mid-register-family. Merge/reconciliation should not treat the `VM_CONTEXT13_PAGE_TABLE_END_ADDR_HI32` group as fully described by this chunk alone.
- Context end-address registers are split low/high page-number values. Unit mistakes between bytes, 4 KiB pages, and higher-address bits can silently widen or shrink VMID access ranges.
- Per-VF framebuffer, ATS, active-function, reset, and XGMI GPU-IOV controls affect SR-IOV isolation. Misprogramming them can route memory traffic to the wrong VF, break guest address translation, or strand a VF during reset.
- Aperture registers such as framebuffer location, AGP bounds, system aperture bounds, default address, local HBM, cacheable DRAM, and host mapping affect memory routing globally for the hub. Bad values can cause VM faults, poisoned default-page accesses, display/media failures, or hangs.
- MARC base/relocation/length registers define remap windows. Incorrect pairing of LO/HI/base/reloc/length indices can redirect an aperture even if each individual write is well formed.
- Cross-generation similarity is dangerous. MMHUB 1.7, MMHUB 1.8, GC 9.x, and later GC/MMHUB headers use similar names with different numeric offsets and sometimes different base indices; including or copying the wrong ASIC header can produce valid C that targets invalid hardware addresses.

## Test Signals

- Build AMDGPU with MMHUB 1.7 support so `mmhub_v1_7.c` compiles against this offset header and the companion mask header.
- Static generated-header validation should compare every register in this slice against the authoritative MMHUB 1.7 register source and verify matching field groups exist in `mmhub_1_7_sh_mask.h`.
- Boot/runtime smoke on MMHUB 1.7 hardware should confirm framebuffer location discovery, GART enable, VMID setup, TLB setup, suspend/resume, and GPU reset do not produce VM faults or register-access warnings.
- GPUVM stress should allocate and evict buffers across VMIDs, force page-table updates, and validate no stale translations or protection-fault storms occur after context range and invalidation setup.
- SR-IOV validation should exercise PF plus VF boot/reset paths, per-VF framebuffer aperture visibility, ATS enable behavior, virtual reset request handling, and active-function reporting.
- XGMI or large-framebuffer systems should verify LFB region/size and GPU-IOV state across boot, reset, and peer-memory workloads.
- Aperture diagnostics should compare `adev->gmc.fb_start/fb_end`, AGP/system aperture bounds, default-page programming, and L1 TLB control values against known-good traces from the same ASIC generation.
