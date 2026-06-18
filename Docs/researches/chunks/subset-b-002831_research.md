# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_3_0_sh_mask.h lines 2368-4743

## Scope

This chunk covers the middle of the generated AMDGPU MMHUB 9.3.0 shift/mask header. It contains only C preprocessor constants for 32-bit MMIO register fields: each field is represented as a `REGISTER__FIELD__SHIFT` macro and a matching `REGISTER__FIELD_MASK` macro. There are no functions, structs, storage declarations, loops, branches, or direct register accesses in this range.

The range starts with the remaining masks for `DAGB1_RD_CNTL_MISC`, then covers the `DAGB1` read/write arbitration, credit, clock-gating, status, and performance-counter register fields. It then enters the `mmhub_ea_mmeadec` address block and covers DRAM/IO client grouping, priority, address normalization, DRAM address decode, hashing, chip-select mapping, and part of the IO urgency-mask register group. The last visible line in this chunk is `MMEA0_IO_WR_PRI_URGENCY_MASK__CID3_MASK_MASK`; the rest of that register's masks are outside this exact line range and should be merged from the following chunk.

## Purpose

The purpose of this chunk is to define the bit-level software contract for MMHUB 9.3.0 DAGB1 and MMEA0 registers. Driver and debug code pair these field definitions with offsets from `mmhub_9_3_0_offset.h` when composing or decoding register values through AMDGPU/SOC15 helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15`.

This header is generated hardware-description data. Its correctness matters because a single stale shift or mask can redirect writes to the wrong bit lane while still compiling cleanly. In this tree there is no direct C runtime file named for `mmhub_9_3_0`; the header appears as a generated ASIC register contract, with analogous DAGB/MMEA families consumed by other MMHUB generations.

## Important Macro Families

### `DAGB1` Read and Write Arbitration

The `DAGB1` portion defines control for the second DAGB instance's read/write request path:

- `DAGB1_RD_CNTL_MISC` tail masks expose EA pool credit, IO EA credit, legacy coherent-client modes, and `UTCL2_CID`.
- `DAGB1_RD_TLB_CREDIT` and `DAGB1_WR_TLB_CREDIT` split six 5-bit TLB credit counters across one register.
- `DAGB1_WRCLI0` through `DAGB1_WRCLI15` share a repeated client layout: virtual channel, TLB-credit checking, urgency high/low thresholds, max/min bandwidth enable and values, OSD limiter enable, and max OSD.
- `DAGB1_WR_CNTL`, `DAGB1_WR_GMI_CNTL`, `DAGB1_WR_ADDR_DAGB`, and `DAGB1_WR_DATA_DAGB` describe global write-side bandwidth windows, GMI credits, DAGB enablement, jump-ahead behavior, self-init disablement, and instance identity.
- `DAGB1_WR_VC0_CNTL` through `DAGB1_WR_VC7_CNTL` define per-virtual-channel credits and bandwidth/OSD limits.

The repeated register shape is intentional: client- and VC-indexed fields are packed into identical 32-bit layouts so firmware or driver tables can program traffic policy consistently across clients.

### `DAGB1` Timers, Clock Gating, Status, and Counters

The chunk also covers the lower-level DAGB1 control and observability surface:

- `DAGB1_WR_OUTPUT_DAGB_MAX_BURST` and `DAGB1_WR_OUTPUT_DAGB_LAZY_TIMER` define per-VC 4-bit max-burst and lazy-timer controls.
- `DAGB1_WR_ADDR_DAGB_MAX_BURST0/1`, `DAGB1_WR_ADDR_DAGB_LAZY_TIMER0/1`, `DAGB1_WR_DATA_DAGB_MAX_BURST0/1`, and `DAGB1_WR_DATA_DAGB_LAZY_TIMER0/1` split clients 0-15 into two packed registers per control type.
- `DAGB1_WR_CGTT_CLK_CTRL`, `DAGB1_L1TLB_WR_CGTT_CLK_CTRL`, and `DAGB1_ATCVM_WR_CGTT_CLK_CTRL` define clock-gating delay, hysteresis, soft-stall override, and LS override bits.
- `DAGB1_WRCLI_*_PENDING` and `DAGB1_RDCLI_*_PENDING` expose full-width pending/busy bitmaps for ask, go, global-send, TLB, OARB, OSD, and write data-bus stages.
- `DAGB1_FIFO_EMPTY`, `DAGB1_FIFO_FULL`, `DAGB1_WR_CREDITS_FULL`, and `DAGB1_RD_CREDITS_FULL` expose packed fullness/emptiness indicators.
- `DAGB1_PERFCOUNTER_LO`, `DAGB1_PERFCOUNTER_HI`, `DAGB1_PERFCOUNTER0_CFG`, `DAGB1_PERFCOUNTER1_CFG`, `DAGB1_PERFCOUNTER2_CFG`, and `DAGB1_PERFCOUNTER_RSLT_CNTL` define performance counter values, compare value, event selectors, modes, enables, clears, triggers, and saturation behavior.
- `DAGB1_RESERVE0` through `DAGB1_RESERVE17` expose full-width reserved registers.

The masks in `DAGB1_CNTL_MISC2` are especially visible in nearby MMHUB generation code: similar fields control fine-grained clock gating disable bits for write request/return, read request/return, and TLB paths.

### `MMEA0` DRAM and IO Arbitration

After the `addressBlock: mmhub_ea_mmeadec` marker, the chunk defines the MMEA0 external-address decode/arbitration register fields:

- `MMEA0_DRAM_RD_CLI2GRP_MAP0/1`, `MMEA0_DRAM_WR_CLI2GRP_MAP0/1`, `MMEA0_IO_RD_CLI2GRP_MAP0/1`, and `MMEA0_IO_WR_CLI2GRP_MAP0/1` map CIDs 0-31 into four 2-bit arbitration groups for read and write traffic.
- `MMEA0_DRAM_RD_GRP2VC_MAP` and `MMEA0_DRAM_WR_GRP2VC_MAP` map those groups to virtual channels.
- `MMEA0_DRAM_RD_LAZY`, `MMEA0_DRAM_WR_LAZY`, `MMEA0_DRAM_PAGE_BURST`, `MMEA0_IO_RD_COMBINE_FLUSH`, `MMEA0_IO_WR_COMBINE_FLUSH`, and `MMEA0_IO_GROUP_BURST` define delay, accumulation, page-burst, combine-flush, and group-burst policy.
- `MMEA0_DRAM_RD_CAM_CNTL` and `MMEA0_DRAM_WR_CAM_CNTL` define per-group CAM depth and reorder limits.
- `MMEA0_DRAM_*_PRI_*` and `MMEA0_IO_*_PRI_*` define age, queuing, fixed, urgency, and quantum coefficients. These register families determine how the MMEA arbiter chooses among traffic groups under load.
- `MMEA0_IO_RD_PRI_URGENCY_MASK` defines a full CID0-CID31 urgency mask. `MMEA0_IO_WR_PRI_URGENCY_MASK` begins in this chunk with all CID shifts and the first visible CID mask definitions through CID3.

### `MMEA0` Address Normalization and Decode

The address decode region describes how incoming MMEA traffic is normalized, routed to chip selects, and distributed across memory geometry:

- `MMEA0_ADDRNORM_BASE_ADDR0/1`, `MMEA0_ADDRNORM_LIMIT_ADDR0/1`, and `MMEA0_ADDRNORM_OFFSET_ADDR1` define normalized address windows, valid bits, source/destination ID selectors, and offset behavior.
- `MMEA0_ADDRNORMDRAM_HOLE_CNTL` and `MMEA0_ADDRNORMDRAM_TRICHANNEL_CFG` define DRAM-hole enable/base and tri-channel hashing.
- `MMEA0_ADDRDEC_BANK_CFG` and `MMEA0_ADDRDEC_MISC_CFG` expose bank/row/column address selection, row-bit range, DRAM type, channel mode, enable flags, and UMA/routing mode controls.
- `MMEA0_ADDRDECDRAM_ADDR_HASH_BANK0` through `BANK4`, `PC`, `PC2`, `CS0`, and `CS1` define XOR-based hashing across columns, rows, banks, pseudo-channel, and chip-select address bits.
- `MMEA0_ADDRDECDRAM_HARVEST_ENABLE` can force bank-3 or bank-4 values, which is relevant when physical memory resources are harvested or disabled.
- `MMEA0_ADDRDEC0_*` and `MMEA0_ADDRDEC1_*` duplicate chip-select decode tables for two decode instances. They cover primary and secondary chip-select base addresses, masks, geometry configuration, bank/row/column selectors, rank-module selectors, channel-bit selection, and row-MSB inversion.

These definitions are not virtual memory page-table controls. They are lower-level memory fabric and external-address decode controls that decide how MMHUB requests are grouped, prioritized, and mapped onto physical DRAM/IO routing.

## Control Flow and Runtime Use

There is no control flow in this header chunk. Runtime behavior is created by code that includes this generated header and uses the macros to build read-modify-write values for MMIO registers.

The expected runtime pattern is:

1. Include the matching `mmhub_9_3_0_offset.h` and this `mmhub_9_3_0_sh_mask.h`.
2. Select a register offset such as `mmDAGB1_WRCLI0`, `mmDAGB1_CNTL_MISC2`, `mmMMEA0_DRAM_RD_CLI2GRP_MAP0`, `mmMMEA0_ADDRDEC0_BASE_ADDR_CS0`, or `mmMMEA0_IO_WR_PRI_URGENCY_MASK`.
3. Use the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` pair, usually through `REG_SET_FIELD` or `REG_GET_FIELD`, to update or decode one packed field without disturbing neighboring fields.
4. Write or read the resulting 32-bit value through SOC15 MMIO helpers.

Searches in this source tree found `mmhub_9_3_0_offset.h` and `mmhub_9_3_0_sh_mask.h`, but no direct `mmhub_v9_3_0.c` consumer. Similar DAGB1 and MMEA0 field names are used in other MMHUB generations, especially for clock-gating control, RAS/error reporting, golden register values, and memory-hub diagnostics. That means this chunk is best treated as generated platform data whose direct runtime consumer may be firmware, debug tooling, generated tables, or code outside the visible tree.

## State and Persistence Behavior

This file stores no software state. It names hardware state in MMHUB registers. The state itself persists in GPU MMIO registers until reset, suspend/resume power loss, firmware reinitialization, driver reprogramming, or ASIC-specific power-gating events.

Important represented state includes:

- Per-client write arbitration state for 16 DAGB1 write clients: virtual channel selection, urgency thresholds, max/min bandwidth policy, and OSD limiting.
- DAGB1 credit and pending state for TLB, data, miscellaneous, ask/go/global-send, OARB, OSD, and data-bus stages.
- Clock-gating policy for write, L1 TLB write, and ATCVM write sub-blocks.
- Performance-counter selection, enable, clear, trigger, and result state.
- MMEA0 CID-to-group and group-to-VC routing for both DRAM and IO reads/writes.
- MMEA0 priority coefficients and urgency masks that decide how traffic is aged, queued, fixed-prioritized, or urgency-boosted.
- Address normalization windows, DRAM hole handling, tri-channel configuration, DRAM geometry, address hashing, harvesting overrides, chip-select base/mask tables, and column/row/rank-module selectors.

Because these are persistent hardware registers, initialization order matters. Address decode and normalization fields must match the actual memory topology before traffic is allowed to rely on them. Arbitration and clock-gating fields should be restored after reset and should not be blindly shared between ASIC generations.

## Dependencies and Integration Points

Primary dependencies:

- `mmhub_9_3_0_offset.h` provides the matching register offsets and base indices. Examples in this chunk's area include `mmDAGB1_WRCLI0` at `0x00ac`, `mmDAGB1_CNTL_MISC2` at `0x00e3`, `mmMMEA0_DRAM_RD_CLI2GRP_MAP0` at `0x0100`, `mmMMEA0_ADDRDEC0_BASE_ADDR_CS0` at `0x015d`, and `mmMMEA0_IO_WR_PRI_URGENCY_MASK` at `0x01e5`.
- AMDGPU register helpers depend on the naming convention `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`.
- MMHUB code in neighboring generations shows the typical integration pattern for `DAGB1_CNTL_MISC2` and related masks: read a register, clear or set specific clock-gating disable bits, then write the register back.
- Golden-register programming, RAS/error handling, debugfs register dumps, firmware handoff code, and ASIC init tables are plausible consumers of the DAGB/MMEA fields even when no direct 9.3.0 C implementation is present in this tree.

The field definitions must stay paired with the 9.3.0 offset header. Many register names recur across MMHUB generations, but offsets, base indices, field width, and even field meaning can differ.

## Risks and Edge Cases

- Mixing `mmhub_9_3_0_sh_mask.h` with another MMHUB generation's offset header can silently program the wrong register or bit position.
- This chunk begins and ends inside larger register families. Merge/reconciliation must combine it with adjacent chunks so `DAGB1_RD_CNTL_MISC` and `MMEA0_IO_WR_PRI_URGENCY_MASK` are not documented as complete solely from this range.
- Repeated client/VC register layouts are easy to update incorrectly by copy/paste. A single off-by-4-bit shift in a packed client register would affect the wrong client or virtual channel.
- Clock-gating override and disable fields can create hard-to-debug hangs or power regressions if programmed outside the expected init sequence.
- Address normalization, chip-select base/mask, row/column selector, and hashing fields are topology-sensitive. Bad values can route requests to the wrong memory location, break interleaving, or corrupt data.
- Harvest-enable fields can force bank values; stale settings could expose disabled memory resources or reduce usable routing entropy.
- Urgency and bandwidth fields are performance-sensitive. They may not fail functionally when wrong, but they can cause starvation, latency spikes, or reduced throughput for specific MMHUB clients.
- Full-width `*_PENDING`, `*_FULL`, `*_EMPTY`, and reserved fields should not be treated as arbitrary writable data without hardware documentation.

## Test and Verification Signals

Useful validation signals for this chunk are mostly compile coverage, register readback, and traffic behavior:

- Build coverage should verify that all generated macros in this header parse cleanly and that paired `mmhub_9_3_0_offset.h` symbols are available.
- Static checks can compare every `__SHIFT` with its corresponding `_MASK` width and position, especially for repeated 2-bit CID group maps, 3-bit group/VC maps, 4-bit client/column maps, and 5-bit TLB-credit fields.
- Register readback after ASIC initialization should confirm that `DAGB1_CNTL_MISC2` clock-gating policy matches the selected power-management mode.
- MMHUB traffic tests should exercise read and write clients across all visible DAGB1 client slots and confirm no client is starved by urgency, min/max bandwidth, or OSD-limiter programming.
- Performance-counter tests can select events with `DAGB1_PERFCOUNTER*_CFG`, start/stop through `DAGB1_PERFCOUNTER_RSLT_CNTL`, and verify monotonic counter behavior in `LO/HI`.
- Memory-topology tests should validate address normalization, DRAM hole handling, chip-select mapping, and hashing against the actual ASIC memory configuration.
- Reset and suspend/resume tests should confirm that DAGB/MMEA arbitration and address decode registers are restored after hardware state loss.
- RAS or fault-injection tests should watch for memory routing, parity, or response-status anomalies when MMEA address decode and urgency policy are changed.

## Cross-Chunk Notes

This is only one chunk of `mmhub_9_3_0_sh_mask.h`. The final per-file research document should merge it with earlier and later chunks that define the rest of MMHUB 9.3.0 VM, fault, invalidate, RAS, DAGB0/DAGB1, and MMEA0 register fields. The next chunk is needed to finish `MMEA0_IO_WR_PRI_URGENCY_MASK`, whose shift definitions and first four mask definitions are visible here but whose remaining mask definitions continue after line 4743.
