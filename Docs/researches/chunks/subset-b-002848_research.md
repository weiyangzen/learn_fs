# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 16551-18899

## Scope

This chunk covers generated shift and mask macros from the AMD MMHUB 9.4.1 register mask header. The range starts in the middle of `MMEA2_IO_WR_CLI2GRP_MAP0` and continues through the beginning of `MMEA3_ADDRDEC0_COL_SEL_LO_CS23`. It spans the tail of the MMEA2 address-engine controls and the start of the `mmhub_ea_mmeadec3` address block.

The file is a hardware register bitfield map only. It defines preprocessor constants with the standard AMDGPU generated-header shape:

- `<REGISTER>__<FIELD>__SHIFT` for the bit offset.
- `<REGISTER>__<FIELD>_MASK` for the 32-bit mask.

There are no C functions, structs, variables, memory allocation paths, locks, or executable control flow in this chunk.

## Purpose

The purpose of this header section is to provide the bit-level ABI between the AMDGPU MMHUB v9.4 driver code and MMHUB 9.4.1 hardware. The covered MMEA registers describe request grouping, arbitration, priorities, virtual-channel mapping, SDP credit behavior, error detection/correction counters, error injection controls, clock-gating controls, performance counters, and physical address decoding for MMEA2 and MMEA3.

Driver code normally consumes these masks through AMDGPU register helpers and macros such as `SOC15_REG_FIELD`, `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`. The matching offset names live in the sibling MMHUB offset header, while this file supplies field positions and masks.

## Important Macro Families

### MMEA2 IO Arbitration and Priority

The opening MMEA2 IO section completes the `MMEA2_IO_WR_CLI2GRP_MAP0` masks and defines `MMEA2_IO_WR_CLI2GRP_MAP1`. These map client IDs `CID0` through `CID31` into 2-bit arbitration groups. In this chunk only the upper half of `MAP0` is present, followed by the complete `MAP1` for `CID16` through `CID31`.

The IO read/write controls that follow are symmetric:

- `MMEA2_IO_RD_COMBINE_FLUSH` and `MMEA2_IO_WR_COMBINE_FLUSH` provide four group timers plus `FORWARD_COMB_ONLY`.
- `MMEA2_IO_GROUP_BURST` defines independent low/high read and write burst limits.
- `MMEA2_IO_RD_PRI_AGE` and `MMEA2_IO_WR_PRI_AGE` define per-group aging rates and age coefficients.
- `MMEA2_IO_RD_PRI_QUEUING`, `MMEA2_IO_WR_PRI_QUEUING`, `MMEA2_IO_RD_PRI_FIXED`, and `MMEA2_IO_WR_PRI_FIXED` define queueing and fixed-priority coefficients.
- `MMEA2_IO_RD_PRI_URGENCY` and `MMEA2_IO_WR_PRI_URGENCY` define urgency coefficients and urgency modes for groups 0-3.
- `MMEA2_IO_RD_PRI_URGENCY_MASKING` and `MMEA2_IO_WR_PRI_URGENCY_MASKING` expose one mask bit per `CID0` through `CID31`.
- `MMEA2_IO_RD_PRI_QUANT_PRI1/2/3` and `MMEA2_IO_WR_PRI_QUANT_PRI1/2/3` define per-group threshold fields used by the quantitative priority path.

These fields are policy knobs for IO-side arbitration. A bad value can change fairness, latency, or starvation behavior across clients rather than just affecting a single request.

### MMEA2 SDP Arbitration and Credits

The `MMEA2_SDP_*` families describe the SDP path after the IO/DRAM/GMI arbiters:

- `MMEA2_SDP_ARB_DRAM`, `MMEA2_SDP_ARB_GMI`, and `MMEA2_SDP_ARB_FINAL` configure burst limits, early read/write switching, end-of-burst behavior, read/write bank-state coupling, chain breaking, read-only virtual channels, and error event/halt behavior.
- `MMEA2_SDP_DRAM_PRIORITY`, `MMEA2_SDP_GMI_PRIORITY`, and `MMEA2_SDP_IO_PRIORITY` map read and write groups 0-3 to 4-bit priority values.
- `MMEA2_SDP_CREDITS` controls tag, write-response, and read-response credit limits.
- `MMEA2_SDP_TAG_RESERVE0/1`, `MMEA2_SDP_VCC_RESERVE0/1`, and `MMEA2_SDP_VCD_RESERVE0/1` reserve tag and virtual-channel credits across VC0-VC7, with distribution-pool controls on the second reserve registers.
- `MMEA2_SDP_REQ_CNTL` provides request override bits for read, write, atomic, DRAM/GMI chaining, and inner-domain mode.

Together these masks describe how requests are admitted and shaped after client grouping. They are tightly coupled to hardware scheduling assumptions and are not generic software queue controls.

### MMEA2 Miscellaneous, Latency, Performance, and EDC

`MMEA2_MISC` exposes a dense set of arbitration and link-manager controls: relative priority enables for DRAM/GMI/IO read and write arbiters, early write-return enablement per VC0-VC7, early SDP original-data handling, link-manager dynamic mode and thresholds, mid-chain/last-chip-select favoritism, and write-to-read chip-select switching.

`MMEA2_LATENCY_SAMPLING` selects latency sampler filters. It can independently choose DRAM, GMI, IO, read, write, atomic-return, atomic-no-return, and VC masks for two samplers. `MMEA2_PERFCOUNTER_LO`, `MMEA2_PERFCOUNTER_HI`, `MMEA2_PERFCOUNTER0_CFG`, `MMEA2_PERFCOUNTER1_CFG`, and `MMEA2_PERFCOUNTER_RSLT_CNTL` define the local performance counter data, selector ranges, modes, enable/clear bits, start/stop triggers, and saturation behavior.

The EDC and diagnostic sections are hardware reliability integration points:

- `MMEA2_EDC_CNT`, `MMEA2_EDC_CNT2`, and `MMEA2_EDC_CNT3` expose SEC/DED/SED count fields for DRAM read/write command memory, write data memory, read/write return tag memory, page memory, IO command/data memory, GMI command/data/page memory, and MAM D0-D3 memories.
- `MMEA2_DSM_CNTL`, `MMEA2_DSM_CNTLA`, `MMEA2_DSM_CNTL2`, and `MMEA2_DSM_CNTL2A` expose DSM irritator data, single-write enables, error-injection enables, delay selectors, and global injection delay fields for the same memory classes.
- `MMEA2_EDC_MODE` provides count, gate, DED mode, propagation, and bypass bits.
- `MMEA2_ERR_STATUS` exposes SDP read/write response status, data status, data parity error, clear-error-status, busy-on-error, and FUE flag bits.

In-tree `amdgpu/mmhub_v9_4.c` consumes the `MMEA2_EDC_CNT*` and `MMEA3_EDC_CNT*` fields in its MMHUB RAS register table via `SOC15_REG_FIELD(...)`, mapping these generated masks into correctable, deferred, and uncorrectable error reporting.

### MMEA2 Clock and Address-Decoder Selection

`MMEA2_CGTT_CLK_CTRL` defines clock-gating timing and override fields: on-delay, off-hysteresis, spare fields, soft-stall overrides for write/read/return, light-sleep override, and soft overrides for write/read/return/register paths.

`MMEA2_MISC2` contains chip-select group swap controls, chip-select group burst limits for DRAM and GMI, IO read/write priority enablement, and read-return swap mode. `MMEA2_ADDRDEC_SELECT` selects the DRAM and GMI address-decoder channel ranges, pairing start and end fields for each target.

### MMEA3 DRAM and GMI Request Scheduling

The `mmhub_ea_mmeadec3` address block starts at line 17514. Its first families mirror the MMEA2 scheduling ideas for MMEA3 DRAM and GMI traffic:

- `MMEA3_DRAM_RD_CLI2GRP_MAP0/1`, `MMEA3_DRAM_WR_CLI2GRP_MAP0/1`, `MMEA3_GMI_RD_CLI2GRP_MAP0/1`, and `MMEA3_GMI_WR_CLI2GRP_MAP0/1` map `CID0` through `CID31` into four 2-bit client groups.
- `MMEA3_DRAM_RD_GRP2VC_MAP`, `MMEA3_DRAM_WR_GRP2VC_MAP`, `MMEA3_GMI_RD_GRP2VC_MAP`, and `MMEA3_GMI_WR_GRP2VC_MAP` map groups 0-3 to 3-bit virtual-channel values.
- `MMEA3_DRAM_RD_LAZY`, `MMEA3_DRAM_WR_LAZY`, `MMEA3_GMI_RD_LAZY`, and `MMEA3_GMI_WR_LAZY` configure per-group delays plus request accumulation threshold, timeout, and idle maximum.
- `MMEA3_DRAM_RD_CAM_CNTL`, `MMEA3_DRAM_WR_CAM_CNTL`, `MMEA3_GMI_RD_CAM_CNTL`, and `MMEA3_GMI_WR_CAM_CNTL` define group CAM depths and, for GMI, chip-select CAM depths.
- `MMEA3_DRAM_PAGE_BURST` and `MMEA3_GMI_PAGE_BURST` define read/write page-burst limits.
- DRAM and GMI read/write priority families cover aging, queueing, fixed coefficients, urgency coefficients/modes, urgency masks, and quantitative threshold registers.

The MMEA3 GMI urgency masking registers again expose one bit per CID for both reads and writes. These masks can suppress urgency behavior for selected clients and therefore directly affect request latency under contention.

### MMEA3 Address Normalization and Decode

From `MMEA3_ADDRNORM_BASE_ADDR0` onward, the chunk moves from scheduling into address normalization and chip-select decode:

- `MMEA3_ADDRNORM_BASE_ADDR0` through `MMEA3_ADDRNORM_BASE_ADDR5` define valid bits, legacy MMIO hole enable, interleave channel/die/socket counts, interleave address selection, and high base address fields.
- `MMEA3_ADDRNORM_LIMIT_ADDR0` through `MMEA3_ADDRNORM_LIMIT_ADDR5` define destination fabric IDs and high limit address fields.
- `MMEA3_ADDRNORM_OFFSET_ADDR1`, `MMEA3_ADDRNORM_OFFSET_ADDR3`, and `MMEA3_ADDRNORM_OFFSET_ADDR5` define high-address offset enable and offset values.
- `MMEA3_ADDRNORMDRAM_HOLE_CNTL` and `MMEA3_ADDRNORMGMI_HOLE_CNTL` define DRAM hole valid/offset fields for DRAM and GMI spaces.
- `MMEA3_ADDRNORMDRAM_NP2_CHANNEL_CFG` and `MMEA3_ADDRNORMGMI_NP2_CHANNEL_CFG` define non-power-of-two 64K-space sizing fields.
- `MMEA3_ADDRDEC_BANK_CFG` and `MMEA3_ADDRDEC_MISC_CFG` define bank masks, bank-group selection/interleave, VCM enables, package/channel/chip-select/rank-mask fields for DRAM and GMI.
- `MMEA3_ADDRDECDRAM_ADDR_HASH_*` and `MMEA3_ADDRDECGMI_ADDR_HASH_*` define XOR-based hash controls for banks 0-5, pseudo-channel, chip-select, and bank XOR fields.
- `MMEA3_ADDRDECDRAM_HARVEST_ENABLE` and `MMEA3_ADDRDECGMI_HARVEST_ENABLE` define force-enable/value controls for harvested bank bits B3-B5.
- `MMEA3_ADDRDEC0_BASE_ADDR_CS*`, `MMEA3_ADDRDEC0_BASE_ADDR_SECCS*`, `MMEA3_ADDRDEC0_ADDR_MASK_*`, `MMEA3_ADDRDEC0_ADDR_CFG_*`, `MMEA3_ADDRDEC0_ADDR_SEL_*`, `MMEA3_ADDRDEC0_ADDR_SEL2_*`, and the beginning of `MMEA3_ADDRDEC0_COL_SEL_LO_*` define chip-select enables, base addresses, masks, geometry, bank/row selector routing, secondary chip-select regions, and low column selectors.

These fields determine how physical addresses are normalized, interleaved, hashed, and routed to DRAM or GMI chip-select resources. They are part of platform bring-up and memory topology programming, not normal runtime data structures.

## Control Flow

This chunk has no runtime control flow. Its "flow" is structural:

1. Driver code includes `mmhub_9_4_1_sh_mask.h`.
2. Register programming code combines one or more `__SHIFT` and `_MASK` constants with a register address from the offset header.
3. MMIO helpers read, compose, write, or extract 32-bit hardware register values.
4. Hardware interprets those bitfields as scheduling, decoding, reliability, or counter state.

For RAS counters specifically, `amdgpu/mmhub_v9_4.c` stores register/field triples in tables, and the RAS path later uses those table entries to read and classify MMHUB EDC counts.

## State and Persistence Behavior

The macros themselves hold no state. The state lives in MMHUB hardware registers:

- Arbitration, priority, credit, clock-gating, address-normalization, and address-decoder fields are persistent hardware configuration until rewritten or reset.
- Performance counters and EDC counters are hardware-observed state that may accumulate until cleared, reset, or reconfigured.
- `CLEAR`, `CLEAR_ALL`, `CLEAR_ERROR_STATUS`, error-injection enable, and DSM single-write controls are command/configuration fields where write ordering and hardware side effects matter.
- Address decode and hash fields persist as part of the active memory topology and can affect every memory access routed through the corresponding MMEA instance.

Because these fields describe MMIO state, persistence is tied to device reset, suspend/resume, GPU reset, and driver initialization sequences rather than C object lifetime.

## Dependencies and Integration Points

This header depends on the AMDGPU generated register-header convention and is paired with MMHUB 9.4.1 offset definitions. It is included by `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c`, which provides the main in-tree integration for this ASIC generation.

Important integration points include:

- `amdgpu/mmhub_v9_4.c`, which includes this header and consumes `MMEA2_EDC_CNT*` and `MMEA3_EDC_CNT*` fields for RAS register tables.
- AMDGPU SOC15 register helpers that require exact `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` names.
- RAS handling, which relies on the EDC count masks to classify correctable, deferred, and uncorrectable MMHUB errors.
- GPU memory initialization and platform topology code, which would use the address normalization, address hash, chip-select, bank, row, and column selector fields when programming MMHUB memory decode.
- Performance/debug tooling, which can use the MMEA performance counter and latency sampler fields for MMHUB traffic observation.

## Risks

- The range starts mid-register at `MMEA2_IO_WR_CLI2GRP_MAP0`; consumers need the previous chunk for the corresponding lower fields and `__SHIFT` definitions for `CID0` through `CID15`.
- Off-by-one shift or mask errors in generated headers silently program the wrong hardware bits. For arbitration and address decode fields, that can manifest as severe performance regressions, memory routing failures, or hangs rather than obvious build failures.
- Address normalization, hash, chip-select, and bank selector masks are topology-critical. Incorrect programming can route physical addresses to the wrong fabric ID, chip select, bank, row, or column.
- Error-injection and EDC mode fields can create or mask reliability events. Tests or debug code using `MMEA2_DSM_*` must avoid leaving injection enabled.
- `CLEAR`, `CLEAR_ALL`, and `CLEAR_ERROR_STATUS` fields have side effects; read-modify-write code must avoid accidentally toggling them while updating unrelated fields.
- The generated naming convention is part of the source contract. Renaming fields breaks `SOC15_REG_FIELD(...)` expansion even when numeric masks are unchanged.

## Test Signals

Useful validation signals for changes touching this chunk are:

- Compile coverage of `amdgpu/mmhub_v9_4.c`; failures in `SOC15_REG_FIELD(MMEA2_EDC_CNT*, ...)` or `SOC15_REG_FIELD(MMEA3_EDC_CNT*, ...)` catch missing or renamed EDC masks.
- Header consistency checks ensuring every field has both a `__SHIFT` and `_MASK` definition, with masks aligned to shifts and no unintended overlap within a register.
- RAS tests or hardware validation that read MMHUB EDC counters through the v9.4 RAS table and confirm expected SEC/DED/SED classification.
- GPU reset, suspend/resume, and memory-init validation on MMHUB 9.4.1 ASICs to catch address-decoder, clock-gating, or arbitration register programming regressions.
- Performance counter smoke tests that configure `MMEA2_PERFCOUNTER*_CFG`, start/stop via `MMEA2_PERFCOUNTER_RSLT_CNTL`, and verify stable counter reads from `MMEA2_PERFCOUNTER_LO/HI`.
- Stress tests with DRAM, GMI, and IO traffic under contention to detect regressions in client grouping, virtual-channel mapping, urgency masks, priority coefficients, and SDP credit settings.
