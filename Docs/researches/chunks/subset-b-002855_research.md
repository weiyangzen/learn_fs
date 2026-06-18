# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 33174-35538

## Scope

This chunk covers generated shift and mask macros from the AMD MMHUB 9.4.1 register mask header. It starts in the `MMEA5_GMI_RD_PRI_QUANT_PRI3` priority threshold fields, covers the remainder of the `mmhub_ea_mmeadec5` register field map, and ends partway through the initial `mmhub_ea_mmeadec6` DRAM CAM control fields. The range contains only C preprocessor definitions and register-block comments. There are no functions, structs, variables, runtime branches, allocations, locks, or persistent software data structures in this chunk.

The main register families covered are:

- `MMEA5_GMI_*` read/write priority quantum threshold registers.
- `MMEA5_ADDRNORM*` range, hole, interleave, non-power-of-two channel, and global hash-control registers.
- `MMEA5_ADDRDEC*` bank, channel, chip-select, row/column, hash, harvest, and address selection fields for DRAM and GMI address decode.
- `MMEA5_IO_*` client-to-group, combine flush, burst, priority, urgency, and quantum fields for IO traffic.
- `MMEA5_SDP_*` arbitration, priority, credit, tag reserve, virtual-channel reserve, and request-control fields.
- `MMEA5_MISC`, latency sampling, performance counter, EDC, DSM, clock-gating, error-status, and address-decoder select fields.
- The beginning of `MMEA6_DRAM_*` QoS fields: client-to-group maps, group-to-VC maps, lazy accumulation, and read/write CAM depth/reorder controls.

## Purpose

`mmhub_9_4_1_sh_mask.h` is the bitfield layout companion for MMHUB 9.4.1 registers. For each hardware register field, it exposes the conventional generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the field's bit position.
- `<REGISTER>__<FIELD>_MASK`, the field's 32-bit mask.

The sibling `mmhub_9_4_1_offset.h` header supplies register addresses, while `mmhub_9_4_1_default.h` supplies reset/default values. `amdgpu/mmhub_v9_4.c` includes all three headers and uses the same register helper style (`RREG32_SOC15`, `RREG32_SOC15_OFFSET`, `WREG32_SOC15_OFFSET`, `REG_SET_FIELD`) to compose and access MMHUB registers. This specific chunk is mostly hardware contract data for address decoding and QoS scheduling, even if many of these fields are not directly referenced by open-coded initialization paths in `mmhub_v9_4.c`.

## Important Macro Families

### GMI Priority Quantum Fields

The chunk begins with `MMEA5_GMI_RD_PRI_QUANT_PRI3` and then defines `MMEA5_GMI_WR_PRI_QUANT_PRI1..3`. Each register packs four 8-bit group thresholds at shifts `0x0`, `0x8`, `0x10`, and `0x18`, with masks covering each byte. The matching defaults in `mmhub_9_4_1_default.h` are `0x3f3f3f3f`, `0x7f7f7f7f`, and `0xffffffff` for priority levels 1 through 3. These fields describe traffic aging/threshold behavior for GMI read/write priority arbitration.

### Address Normalization

`MMEA5_ADDRNORM_BASE_ADDR0..5`, `LIMIT_ADDR0..5`, and `OFFSET_ADDR1/3/5` describe address normalization windows. Base registers include:

- `ADDR_RNG_VAL`, enabling a range.
- `LGCY_MMIO_HOLE_EN`, handling legacy MMIO hole behavior.
- `INTLV_NUM_CHAN`, `INTLV_NUM_DIES`, `INTLV_NUM_SOCKETS`, and `INTLV_ADDR_SEL`, describing interleave topology.
- `BASE_ADDR`, using the high 20 bits of the register.

Limit registers pair `DST_FABRIC_ID` with `LIMIT_ADDR`. Offset registers provide `HI_ADDR_OFFSET_EN` and high-address offset fields. The default header initializes these ranges and holes to zero, which means firmware or platform-specific setup must program meaningful topology before hardware uses the ranges.

The chunk also covers DRAM and GMI hole controls, non-power-of-two channel configuration, and global hash interleave controls. The DRAM/GMI variants are parallel: the same logical field names are repeated for separate DRAM and GMI paths, so mismatched edits between those families would create asymmetric address routing.

### Address Decode and Hashing

`MMEA5_ADDRDEC_BANK_CFG` and `MMEA5_ADDRDEC_MISC_CFG` configure bank masks, bank-group selection/interleave, VCM enables, physical channel masks, channel masks, chip-select masks, and rank-mask fields. The DRAM and GMI hash families then expose XOR-enable and XOR input selections for bank, pseudo-channel, and chip-select hashing:

- `MMEA5_ADDRDECDRAM_ADDR_HASH_BANK0..5`, `PC`, `PC2`, `CS0`, `CS1`, and `HARVEST_ENABLE`.
- `MMEA5_ADDRDECGMI_ADDR_HASH_BANK0..5`, `PC`, `PC2`, `CS0`, `CS1`, and `HARVEST_ENABLE`.

The hash bank fields split into `XOR_ENABLE`, `COL_XOR`, and `ROW_XOR`. Chip-select hashes use `NA_XOR` after the enable bit. Harvest-enable fields can force bank bits B3/B4/B5 to fixed values, likely to hide harvested or unavailable memory resources.

### Per-Decoder Chip-Select Layout

The chunk defines repeated `MMEA5_ADDRDEC0`, `ADDRDEC1`, and `ADDRDEC2` families. Each decoder includes:

- Base address registers for `CS0..CS3` and secondary chip selects `SECCS0..SECCS3`, with `CS_EN` and `BASE_ADDR`.
- Address mask registers for `CS01`, `CS23`, `SECCS01`, and `SECCS23`.
- Address configuration registers defining bank-group count, rank-mask count, row-low/high widths, column width, bank count, and high-column enable.
- Address selection registers mapping bank bits, row low/high bits, and the sixth bank bit.
- Column selection low/high registers mapping `COL0..COL15`.
- Rank-mask selection registers for primary and secondary chip-select pairs, including rank-map inputs, channel-bit selection, and row-MSB inversion controls.

The repeated structure is important: driver or firmware code can derive programming loops over decoder instances, but the actual ABI is still a flat macro namespace. Any automated update must preserve identical field layouts across decoder 0, 1, and 2 unless the hardware spec intentionally diverges.

### IO QoS and Priority Control

`MMEA5_IO_RD_CLI2GRP_MAP0/1` and `MMEA5_IO_WR_CLI2GRP_MAP0/1` pack 32 client IDs into two registers, with two bits per client selecting group 0 through 3. `MMEA5_IO_RD_COMBINE_FLUSH` and `WR_COMBINE_FLUSH` contain four group timers and a `FORWARD_COMB_ONLY` bit. `MMEA5_IO_GROUP_BURST` defines read/write low/high burst limits.

The IO priority registers mirror common QoS math:

- `*_PRI_AGE` has four aging-rate fields and four age-coefficient fields.
- `*_PRI_QUEUING`, `*_PRI_FIXED`, and `*_PRI_URGENCY` provide per-group queue, fixed, and urgency coefficients.
- `*_PRI_URGENCY` also has per-group urgency mode bits.
- `*_PRI_URGENCY_MASKING` has one mask bit per client ID.
- `*_PRI_QUANT_PRI1..3` has four 8-bit group thresholds per priority level.

The defaults show the intended reset policy: client-to-group maps default to `0xe4e4e4e4`, priority coefficients have non-zero tuned defaults, urgency masks default to all ones, and priority quantum registers follow the same `0x3f`, `0x7f`, `0xff` threshold pattern used by GMI.

### SDP Arbitration and Reservations

`MMEA5_SDP_ARB_DRAM`, `MMEA5_SDP_ARB_GMI`, and `MMEA5_SDP_ARB_FINAL` define arbitration score thresholds, score update factors, winners, and arbiter behavior across DRAM, GMI, and final arbitration stages. The priority registers (`MMEA5_SDP_DRAM_PRIORITY`, `GMI_PRIORITY`, `IO_PRIORITY`) expose four per-target priority fields.

`MMEA5_SDP_CREDITS`, `TAG_RESERVE0/1`, `VCC_RESERVE0/1`, and `VCD_RESERVE0/1` manage return/data credit and reserved tag/virtual-channel capacity. `MMEA5_SDP_REQ_CNTL` exposes per-source request enable bits for DRAM, GMI, both SDP subpaths, and IO. These fields are integration points for bandwidth and fairness tuning between memory paths.

### Miscellaneous, Observability, and Error Fields

`MMEA5_MISC` contains a dense set of mode bits and limits: dynamic credit handling, XGMI flags, page-flip and channel width settings, atomic/datapath modes, credit counters, delay/disable knobs, and forced-partial-read behavior. `MMEA5_LATENCY_SAMPLING` configures sampling enable, select, masks, IDs, timer, and threshold. `MMEA5_PERFCOUNTER_*` exposes low/high counters, event selectors, clear/select fields, and result-control options.

`MMEA5_EDC_CNT`, `EDC_CNT2`, `EDC_CNT3`, and `EDC_MODE` provide error-detection counters, clear bits, count selectors, read/write data access, and disable flags. `MMEA5_ERR_STATUS` distinguishes correctable and uncorrectable error status, validity, logging, and clear bits. DSM and clock controls (`DSM_CNTL*`, `CGTT_CLK_CTRL`) define memory power/clock gating behavior. `MMEA5_ADDRDEC_SELECT` selects DRAM and GMI address decoders.

These registers are stateful hardware controls or counters. The macros do not persist anything by themselves, but writes through the MMIO helpers program persistent hardware state until reset or reprogramming; status and counter fields represent hardware-maintained state.

### MMEA6 DRAM QoS Start

At line 35331 the chunk enters `addressBlock: mmhub_ea_mmeadec6`. The covered `MMEA6_DRAM_*` families mirror the QoS pattern used by earlier blocks:

- `RD_CLI2GRP_MAP0/1` and `WR_CLI2GRP_MAP0/1` map 32 client IDs to four groups with two-bit fields.
- `RD_GRP2VC_MAP` and `WR_GRP2VC_MAP` map the four groups to three-bit virtual-channel IDs.
- `RD_LAZY` and `WR_LAZY` configure per-group lazy delay plus request accumulation threshold, timeout, and idle maximum.
- `RD_CAM_CNTL` and the beginning of `WR_CAM_CNTL` define CAM depth per group, reorder limits per group, and refill-chain control.

The range ends at `MMEA6_DRAM_WR_CAM_CNTL__REORDER_LIMIT_GROUP2__SHIFT`, so the remaining write-CAM masks and subsequent MMEA6 DRAM priority fields belong to later chunks.

## Control Flow

There is no executable control flow in this chunk. The effective runtime flow is indirect:

1. A C file includes `mmhub_9_4_1_offset.h`, `mmhub_9_4_1_sh_mask.h`, and often `mmhub_9_4_1_default.h`.
2. Code reads a 32-bit MMIO register with `RREG32_SOC15*` or starts from a default value.
3. Code composes or extracts fields with `REG_SET_FIELD`, `REG_GET_FIELD`, masks, and shifts from this header.
4. Code writes the value back with `WREG32_SOC15*`.
5. The hardware interprets the bits as address decode, QoS, counter, error, or clock/power configuration.

Because the macros are compile-time constants, there is no runtime validation that a given value fits a field. Callers must mask, shift, and range-check values before writing hardware registers.

## State and Persistence

The header itself has no storage and no persistence. The persistent state is in MMHUB hardware registers programmed using these macros. Important state classes represented in this chunk include:

- Address normalization and decode topology, which controls how physical addresses map onto DRAM/GMI fabric destinations, channels, banks, rows, columns, ranks, and chip selects.
- QoS and arbitration policy, including group mappings, priority coefficients, thresholds, virtual-channel mappings, lazy accumulation, and CAM reorder limits.
- Debug and observability state, including latency sampling, performance counters, EDC counters, and error status bits.
- Clock/power mode state, including DSM and CGTT controls.

Several fields are status or clear bits (`*_ERR_STATUS__CLR_*`, EDC counter clear fields, performance-counter clear/select fields). These must be treated differently from ordinary configuration fields because reads may expose latched hardware state and writes may acknowledge or clear it.

## Dependencies and Integration Points

- `amdgpu/mmhub_v9_4.c` includes this header with the matching offset/default headers and demonstrates the MMHUB register access pattern for v9.4 hardware.
- `soc15.h` and related AMDGPU helpers provide the register access macros that use these generated names.
- `mmhub_9_4_1_offset.h` is required to map the field names to actual MMIO register addresses.
- `mmhub_9_4_1_default.h` is useful for reset-value validation and for detecting whether a field map matches the expected silicon defaults.
- Firmware, SMU/platform initialization, and RAS/debug paths are likely consumers of these address-decode, QoS, EDC, and error-status definitions even when the open `mmhub_v9_4.c` path does not explicitly program every register in this chunk.

## Risks

- The macro names encode a hardware ABI. Renaming or changing a shift/mask silently changes generated register values at compile time and can misprogram memory routing or QoS policy.
- Address normalization, address decode, hash, and harvest fields are high risk: incorrect values can route requests to the wrong memory channel, chip select, row/column bit, GMI destination, or harvested resource.
- DRAM and GMI register families are intentionally parallel. Updating only one side can create asymmetric behavior between local memory and fabric memory paths.
- Client-to-group and priority fields are dense packed bitfields. Off-by-one client IDs, wrong two-bit group encodings, or unmasked values can alter multiple clients at once.
- Status/clear fields such as EDC and error-status bits must not be handled like normal read-modify-write configuration without checking hardware semantics; write-one-to-clear style fields can lose diagnostic information.
- The chunk boundary starts and ends mid-family. Research or generated edits that assume complete families inside this one chunk can miss the first part of `MMEA5_GMI_RD_PRI_QUANT_PRI3` and the rest of `MMEA6_DRAM_WR_CAM_CNTL`.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, register-dump, and hardware-behavior checks:

- Build AMDGPU with `mmhub_v9_4.c` including this header to catch missing or malformed macro definitions.
- Compare generated masks and shifts against the sibling default values by decoding known defaults such as `MMEA5_IO_RD_CLI2GRP_MAP0_DEFAULT`, `MMEA5_SDP_*_DEFAULT`, `MMEA5_MISC_DEFAULT`, and `MMEA6_DRAM_RD_CAM_CNTL_DEFAULT`.
- On supported hardware, use MMIO/register dumps before and after MMHUB initialization to confirm address decode, QoS, EDC, and counter fields match expected firmware/driver programming.
- Exercise memory allocation, GPUVM/GART access, peer/GMI traffic, and IO DMA paths; address-decode mistakes are likely to surface as memory faults, data corruption, hangs, or RAS errors.
- Exercise performance-counter and latency-sampling paths if these fields are programmed by diagnostics; verify counters increment, clear, and select expected events.
- Check RAS/error-injection or fault-reporting paths for correctable/uncorrectable `MMEA5_ERR_STATUS` handling where platform support exists.
