# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 37904-40269

## Scope

This chunk is a generated AMDGPU MMHUB 9.4.1 shift/mask header segment. It contains 2,170 C preprocessor `#define` entries for 32-bit MMIO register fields, plus generated register/address-block comments. There are no functions, structs, enums, variables, allocations, locks, branches, loops, or direct register reads/writes in this range.

The chunk starts in the middle of the `MMEA6_SDP_VCC_RESERVE0` register, covers the tail of the `mmhub_ea_mmeadec6` block, then enters `// addressBlock: mmhub_ea_mmeadec7` and covers `MMEA7` arbitration, address-normalization, address-hash, harvest, and address-decoder fields through the beginning of `MMEA7_ADDRDEC2_RM_SEL_CS01`.

Although the repository path is under a `ceph-client` source mirror, this source is Linux AMDGPU hardware register metadata, not Ceph filesystem logic.

## Purpose

`mmhub_9_4_1_sh_mask.h` provides the bit-level ABI for composing and decoding MMHUB 9.4.1 register values. This chunk's constants let driver code work with named fields instead of hard-coded bit positions when programming or inspecting memory-engine address arbitration, virtual-channel crediting, RAS/EDC status, error-injection controls, clock-gating controls, physical address normalization, DRAM/GMI hashing, chip-select decoding, bank/column/row-machine selection, and performance counters.

The exported convention is consistent across the generated header:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit position.
- `<REGISTER>__<FIELD>_MASK` gives the positioned 32-bit mask used to isolate or update that field.

These field constants are meaningful only when paired with `mmhub_9_4_1_offset.h`, which supplies register offsets such as `mmMMEA6_EDC_CNT`, `mmMMEA7_DRAM_RD_CLI2GRP_MAP0`, `mmMMEA7_ADDRNORM_BASE_ADDR0`, and `mmMMEA7_ADDRDEC2_COL_SEL_HI_CS23`, and with `mmhub_9_4_1_default.h`, which supplies reset/default register values.

## Important Macro Families

### MMEA6 SDP, performance, EDC, DSM, and status tail

The first part completes `MMEA6` fields that began in the prior chunk:

- `MMEA6_SDP_VCC_RESERVE1`, `MMEA6_SDP_VCD_RESERVE0`, and `MMEA6_SDP_VCD_RESERVE1` split virtual-channel credit reserves across `VC0_CREDITS` through `VC7_CREDITS` and include `DISTRIBUTE_POOL` flags on the high reserve registers.
- `MMEA6_SDP_REQ_CNTL` exposes request policy override bits for read, write, atomic, DRAM chaining, GMI chaining, and `INNER_DOMAIN_MODE`.
- `MMEA6_MISC` contains arbitration priority bits for DRAM/GMI/IO reads and writes, early write-return enables for VC0-VC7, link-manager dynamic/halt/reconnect/idle fields, and chip-select switching/favoring controls.
- `MMEA6_LATENCY_SAMPLING` selects sampler filters by target path (`DRAM`, `GMI`, `IO`), operation (`READ`, `WRITE`, atomic return/no-return), and virtual channel.
- `MMEA6_PERFCOUNTER_LO`, `MMEA6_PERFCOUNTER_HI`, `MMEA6_PERFCOUNTER0_CFG`, `MMEA6_PERFCOUNTER1_CFG`, and `MMEA6_PERFCOUNTER_RSLT_CNTL` define counter value, compare value, event-selection, enable, clear, start/stop trigger, and stop-on-saturate fields.
- `MMEA6_EDC_CNT`, `MMEA6_EDC_CNT2`, and `MMEA6_EDC_CNT3` expose small saturated count fields for single-error-corrected, double-error-detected, and single-error-detected conditions across DRAM, GMI, IO, return-tag, page, and MAM memories.
- `MMEA6_DSM_CNTL`, `MMEA6_DSM_CNTLA`, `MMEA6_DSM_CNTL2`, and `MMEA6_DSM_CNTL2A` define diagnostic/stress fields: irritator data, single-write enable, per-memory error-injection enable, injection-delay selectors, and a shared `INJECT_DELAY`.
- `MMEA6_CGTT_CLK_CTRL` defines on/off timing and soft clock/light-sleep override bits for write, read, return, and register paths.
- `MMEA6_EDC_MODE`, `MMEA6_ERR_STATUS`, `MMEA6_MISC2`, and `MMEA6_ADDRDEC_SELECT` define RAS mode/status behavior, SDP response/parity error flags, error clear/busy/FUE bits, arbitration swap/burst controls, and channel range selection for DRAM/GMI address decoders.

The visible `MMEA6` RAS fields are integrated by `amdgpu/mmhub_v9_4.c`, which includes this exact mask header and builds EDC/error-status tables using `SOC15_REG_ENTRY`, `SOC15_REG_FIELD`, and `REG_GET_FIELD`.

### MMEA7 DRAM and GMI arbitration

The `mmhub_ea_mmeadec7` address block starts at line 38359. It mirrors the same MMEA register shape for another memory-engine/address-decoder instance.

The DRAM and GMI read/write client maps use dense repeated bitfields:

- `MMEA7_DRAM_RD_CLI2GRP_MAP0/1`, `MMEA7_DRAM_WR_CLI2GRP_MAP0/1`, `MMEA7_GMI_RD_CLI2GRP_MAP0/1`, and `MMEA7_GMI_WR_CLI2GRP_MAP0/1` map client IDs `CID0` through `CID31` into four groups using 2-bit fields.
- `MMEA7_*_GRP2VC_MAP` maps group 0-3 into 3-bit virtual-channel values.
- `MMEA7_*_LAZY` provides per-group delay fields plus accumulated request threshold, timeout, and idle-max fields.
- `MMEA7_*_CAM_CNTL` configures CAM depth/behavior fields for the corresponding DRAM or GMI read/write path.
- `MMEA7_*_PAGE_BURST`, `*_PRI_AGE`, `*_PRI_QUEUING`, `*_PRI_FIXED`, `*_PRI_URGENCY`, and `*_PRI_QUANT_PRI1/2/3` describe page-burst and arbitration priority tuning by group.
- `MMEA7_GMI_RD_PRI_URGENCY_MASKING` and `MMEA7_GMI_WR_PRI_URGENCY_MASKING` provide one-bit masks for `CID0` through `CID31`; these are especially dense and easy to misuse because the field names themselves include `MASK`, producing generated names like `CID0_MASK_MASK`.

This block is pure metadata, but incorrect values would directly affect memory traffic arbitration if consumed by initialization, debug, or tuning code.

### MMEA7 address normalization and apertures

`MMEA7_ADDRNORM_BASE_ADDR0` through `BASE_ADDR5` define repeated address-range descriptors:

- `ADDR_RNG_VAL` enables the range.
- `LGCY_MMIO_HOLE_EN` controls legacy MMIO-hole handling.
- `INTLV_NUM_CHAN`, `INTLV_NUM_DIES`, `INTLV_NUM_SOCKETS`, and `INTLV_ADDR_SEL` describe interleave topology.
- `BASE_ADDR` occupies the high 20 bits of the register.

The matching `MMEA7_ADDRNORM_LIMIT_ADDR0` through `LIMIT_ADDR5` expose destination fabric ID and high limit address fields. `MMEA7_ADDRNORM_OFFSET_ADDR1/3/5` provide optional high-address offset enable/value fields. `MMEA7_ADDRNORMDRAM_HOLE_CNTL` and `MMEA7_ADDRNORMGMI_HOLE_CNTL` expose DRAM-hole valid/offset fields, and `MMEA7_ADDRNORMDRAM_NP2_CHANNEL_CFG` plus `MMEA7_ADDRNORMGMI_NP2_CHANNEL_CFG` describe non-power-of-two channel-space sizing.

These macros sit on the address-translation path from normalized GPU/system addresses toward DRAM or GMI fabric routing. Their correctness is critical for aperture and interleave programming.

### MMEA7 address decode, hashing, and harvesting

`MMEA7_ADDRDEC_BANK_CFG` and `MMEA7_ADDRDEC_MISC_CFG` define bank, bank-group, pseudo-channel, channel, chip-select, and row-machine masks and enable bits for DRAM and GMI decode.

`MMEA7_ADDRDECDRAM_ADDR_HASH_BANK0` through `BANK5`, `PC`, `PC2`, `CS0`, and `CS1` define XOR-based hash controls for DRAM address decoding. The GMI variants, `MMEA7_ADDRDECGMI_ADDR_HASH_*`, repeat the same shape. Bank and pseudo-channel hash fields include `XOR_ENABLE`, `COL_XOR`, `ROW_XOR`, and `BANK_XOR` masks; chip-select hash registers include `XOR_ENABLE` and a wide `NA_XOR`.

`MMEA7_ADDRDECDRAM_HARVEST_ENABLE` and `MMEA7_ADDRDECGMI_HARVEST_ENABLE` provide force-enable/value fields for bank bits B3-B5, which are used to account for harvested or disabled memory resources.

### MMEA7 address decoders 0-2

The chunk covers complete `MMEA7_ADDRDEC0_*` and `MMEA7_ADDRDEC1_*` families and most of `MMEA7_ADDRDEC2_*` through the start of `ADDRDEC2_RM_SEL_CS01`.

For each decoder:

- `BASE_ADDR_CS0` through `BASE_ADDR_CS3` and `BASE_ADDR_SECCS0` through `SECCS3` expose `CS_EN` and wide `BASE_ADDR` fields.
- `ADDR_MASK_CS01`, `ADDR_MASK_CS23`, `ADDR_MASK_SECCS01`, and `ADDR_MASK_SECCS23` define wide address-mask fields shared by chip-select pairs.
- `ADDR_CFG_CS01` and `ADDR_CFG_CS23` describe number of bank groups, row machines, row low/high bits, columns, banks, and high-column enable.
- `ADDR_SEL_CS01` and `ADDR_SEL_CS23` select address bit positions for bank 0-4 and row low/high; `ADDR_SEL2_*` carries bank 5.
- `COL_SEL_LO_*` and `COL_SEL_HI_*` select column bit positions for columns 0-15.
- `RM_SEL_*` selects row-machine bit positions and row-MSB inversion behavior. The line range ends just after the first `MMEA7_ADDRDEC2_RM_SEL_CS01` shift definitions begin, so the remainder of `ADDRDEC2_RM_SEL_*` belongs to the next chunk.

## Control Flow And Runtime Behavior

There is no runtime control flow in this header chunk. The effective control flow happens in consumers:

1. A driver source includes `mmhub_9_4_1_offset.h`, `mmhub_9_4_1_sh_mask.h`, and often `mmhub_9_4_1_default.h`.
2. Code reads a register with SOC15 helpers, composes or extracts fields with macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `SOC15_REG_ENTRY`, or direct mask operations, then writes the updated register value.
3. Hardware persists the resulting register state until reset, suspend/resume save/restore, power-gating transitions, or explicit reprogramming.

`amdgpu/mmhub_v9_4.c` is the exact in-tree integration point for this generated header. In that file, MMEA EDC count registers for instances 0-7, including `MMEA6_EDC_CNT*` and `MMEA7_EDC_CNT*`, are listed in RAS error-count tables, and `MMEA*_ERR_STATUS` fields are used to detect SDP read/write response and data-parity errors. Other parts of the same driver use the generated MMHUB mask convention for VM, DAGB, clock-gating, and aperture programming.

## State And Persistence

This chunk declares no C storage, so it has no software persistence by itself. The persistent state is the hardware state represented by the registers:

- Credit, request policy, priority, arbitration, and lazy-timer fields affect live MMHUB traffic scheduling until changed or reset.
- Address normalization, address decoding, hash, harvest, chip-select, column, bank, and row-machine fields define routing of physical memory accesses and must match the ASIC memory topology.
- EDC count/status fields are hardware counters or status bits used by RAS collection and may be clear-on-write or clear-through-control depending on the hardware register semantics.
- DSM and error-injection fields can alter diagnostic behavior and should only be used under controlled RAS/test flows.
- Clock-gating override fields can change power/performance behavior and can mask real idle/busy behavior during debugging.

## Dependencies And Integration Points

Primary dependencies:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_offset.h`: matching register offsets and base indices. For this chunk, `MMEA7` offsets run in the `0x3500` range and use base index `1`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_default.h`: reset/default values for the same registers. The defaults show non-zero DRAM/GMI arbitration, lazy, CAM, priority, address-mask/config/select, SDP, clock, and error-status values for `MMEA6` and `MMEA7`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c`: includes this header and consumes MMEA EDC/status masks through AMDGPU/SOC15 register helpers.
- AMDGPU helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `SOC15_REG_ENTRY`, `RREG32_SOC15`, `WREG32_SOC15`, and offset variants.

The generated naming contract is the key integration surface. If a macro is renamed, duplicated incorrectly, or paired with the wrong generation's offset header, callers can still compile but program the wrong bits.

## Risks

- Boundary risk: line 37904 starts inside `MMEA6_SDP_VCC_RESERVE0`, and line 40269 ends inside `MMEA7_ADDRDEC2_RM_SEL_CS01`; reconciliation must merge adjacent chunks for complete register-family documentation.
- Generation-pairing risk: these masks must be used with `mmhub_9_4_1_offset.h` and `mmhub_9_4_1_default.h`, not another MMHUB generation with similar register names.
- Bitfield drift risk: a single wrong shift or mask can silently redirect writes to an unrelated hardware control bit.
- Dense repeated-field risk: client maps, urgency masks, and address-decode selectors are mechanically repetitive, so off-by-one client IDs or chip-select pair mix-ups are easy during manual edits.
- RAS/debug risk: EDC, error-status, DSM, and error-injection fields affect error counting, fault signaling, or injected failures. Incorrect masks can hide real errors, falsely report RAS events, or enable diagnostic behavior in normal operation.
- Memory-routing risk: address normalization, hash, harvest, and chip-select decode fields can misroute memory traffic if programmed inconsistently with actual memory topology.
- Power/performance risk: clock-gating overrides and arbitration/priority fields can change latency, bandwidth fairness, and power behavior.

## Test And Validation Signals

Useful validation for this chunk is mostly structural and hardware-facing:

- Compile coverage of `amdgpu/mmhub_v9_4.c` with this generated header included verifies that expected macro names are present.
- Static generated-header checks should confirm each `__SHIFT` has a matching `_MASK`, masks are 32-bit values, and repeated fields advance monotonically without overlap inside each register.
- Cross-header checks should confirm every register prefix in this chunk has matching `mm<REGISTER>` and `mm<REGISTER>_DEFAULT` entries where expected in the offset/default headers.
- RAS tests should exercise MMHUB EDC count collection for `MMEA6_EDC_CNT*` and `MMEA7_EDC_CNT*`, plus `MMEA*_ERR_STATUS` read/clear behavior.
- GPU bring-up, suspend/resume, and reset tests should confirm MMHUB traffic remains functional after register programming/restoration.
- Memory-topology validation should cover address normalization, chip-select decode, harvested-bank configurations, and DRAM/GMI address hashing on hardware variants with different channel/bank layouts.
- Performance and power tests should watch for regressions in bandwidth, latency, fairness, and clock-gating residency when arbitration or clock-control fields are changed.
