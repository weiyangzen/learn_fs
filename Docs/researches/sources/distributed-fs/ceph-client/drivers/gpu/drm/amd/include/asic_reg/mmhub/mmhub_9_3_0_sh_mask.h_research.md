# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_3_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002830`: lines 1-2367, `Docs/researches/chunks/subset-b-002830_research.md`
- `subset-b-002831`: lines 2368-4743, `Docs/researches/chunks/subset-b-002831_research.md`
- `subset-b-002832`: lines 4744-7094, `Docs/researches/chunks/subset-b-002832_research.md`
- `subset-b-002833`: lines 7095-9511, `Docs/researches/chunks/subset-b-002833_research.md`
- `subset-b-002834`: lines 9512-10265, `Docs/researches/chunks/subset-b-002834_research.md`

## Chunk Research

### subset-b-002830: lines 1-2367

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_3_0_sh_mask.h lines 1-2367

## Purpose

This chunk is generated AMDGPU MMHUB 9.3.0 register bitfield metadata for the opening portion of `mmhub_9_3_0_sh_mask.h`. It defines C preprocessor `*_SHIFT` and `*_MASK` constants for the `mmhub_dagbdec` address block, covering all visible `DAGB0` read/write arbitration fields and the beginning of `DAGB1` read arbitration fields.

Although the repository path is under `distributed-fs/ceph-client`, this file is Linux AMD GPU driver hardware metadata, not Ceph filesystem code. It has no executable logic and no filesystem persistence behavior.

The covered range provides field layouts for:

- `DAGB0_RDCLI0..15`: per-read-client virtual-channel routing, TLB-credit checking, urgency thresholds, max/min bandwidth controls, OSD limiter enablement, and max outstanding depth.
- `DAGB0_RD_CNTL`, `DAGB0_RD_GMI_CNTL`, and `DAGB0_RD_ADDR_DAGB`: read-side clock/window, GMI credit/level/burst/timer, DAGB enable/jump-ahead/self-init, and identity fields.
- `DAGB0_RD_OUTPUT_DAGB_*`, `DAGB0_RD_ADDR_DAGB_*`: per-VC and per-client max-burst and lazy-timer field maps for read outputs and read address routing.
- `DAGB0_RD_CGTT_CLK_CTRL`, `DAGB0_L1TLB_RD_CGTT_CLK_CTRL`, and `DAGB0_ATCVM_RD_CGTT_CLK_CTRL`: read-side clock-gating and light-sleep override fields for the DAGB, L1 TLB, and ATC/VM paths.
- `DAGB0_RD_VC0..7_CNTL`, `DAGB0_RD_CNTL_MISC`, `DAGB0_RD_TLB_CREDIT`, and read pending status registers: read virtual-channel credits, storage/EA/IO pools, legacy modes, UTCL2 client ID, TLB credits, and outstanding busy bitmaps.
- `DAGB0_WRCLI0..15`: write-client equivalents of the per-client virtual-channel, TLB-credit, urgency, bandwidth, OSD limiter, and max outstanding fields.
- `DAGB0_WR_CNTL`, `DAGB0_WR_GMI_CNTL`, `DAGB0_WR_ADDR_DAGB`, `DAGB0_WR_OUTPUT_DAGB_*`, `DAGB0_WR_ADDR_DAGB_*`, and `DAGB0_WR_DATA_DAGB*`: write-side arbitration, address/data DAGB, burst, and timer layouts.
- `DAGB0_WR_VC0..7_CNTL`, `DAGB0_WR_CNTL_MISC`, `DAGB0_WR_TLB_CREDIT`, `DAGB0_WR_DATA_CREDIT`, `DAGB0_WR_MISC_CREDIT`, and write pending status registers: write virtual-channel and data/atomic/OSD credit fields plus busy bitmaps.
- `DAGB0_DAGB_DLY`, `DAGB0_CNTL_MISC`, `DAGB0_CNTL_MISC2`, FIFO/credit-full flags, performance counter result/configuration registers, and reserved full-width placeholders.
- `DAGB1_RDCLI0..15` through `DAGB1_RD_CNTL_MISC`: the start of the second DAGB instance's read-side client, common control, GMI, address DAGB, output burst/timer, clock-gating, address burst/timer, VC control, and misc credit fields. This chunk ends immediately after `DAGB1_RD_CNTL_MISC__STOR_POOL_CREDIT_MASK`; the rest of `DAGB1_RD_CNTL_MISC` and following DAGB1 write-side/register groups belong to later chunks.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, variables, callbacks, locks, allocations, or direct MMIO accesses in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for a field in a 32-bit MMHUB register.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted field mask in the register word.
- Repeated register families intentionally share identical field layouts across clients or virtual channels. For example, every `DAGB0_RDCLI<n>` and `DAGB1_RDCLI<n>` in this range exposes `VIRT_CHAN`, `CHECK_TLB_CREDIT`, `URG_HIGH`, `URG_LOW`, `MAX_BW_ENABLE`, `MAX_BW`, `MIN_BW_ENABLE`, `MIN_BW`, `OSD_LIMITER_ENABLE`, and `MAX_OSD`.

High-signal field families include:

- Arbitration routing and priority: `VIRT_CHAN`, `URG_HIGH`, `URG_LOW`, `EA_VC<n>_REMAP`, `SHARE_VC_NUM`, `IO_LEVEL`, and `IO_LEVEL_COMPLY_VC`.
- Bandwidth and outstanding-request limiting: `MAX_BW_ENABLE`, `MAX_BW`, `MIN_BW_ENABLE`, `MIN_BW`, `OSD_LIMITER_ENABLE`, `MAX_OSD`, `CLI_MAX_BW_WINDOW`, `VC_MAX_BW_WINDOW`, `BW_INIT_CYCLE`, and `BW_RW_GAP_CYCLE`.
- Credit and deadlock controls: `STOR_CREDIT`, `EA_CREDIT`, `STOR_POOL_CREDIT`, `EA_POOL_CREDIT`, `IO_EA_CREDIT`, `TLB0..3`, `VMC0..1`, `VM_L2`, `ATOMIC_CREDIT`, `DLOCK_VC_NUM`, `OSD_CREDIT`, and `OSD_DLOCK_CREDIT`.
- Clock/power gating controls: `ON_DELAY`, `OFF_HYSTERESIS`, `SOFT_STALL_OVERRIDE`, `LS_OVERRIDE`, per-direction light-sleep override bits, and `DISABLE_*_CG` fields.
- DAGB datapath setup: `DAGB_ENABLE`, `ENABLE_JUMP_AHEAD`, `DISABLE_SELF_INIT`, `WHOAMI`, per-VC/per-client `MAX_BURST`, and `LAZY_TIMER`.
- Observability and debugging: `*_PENDING__BUSY`, FIFO empty/full flags, credit-full flags, `PERFCOUNTER_LO/HI`, `PERFCOUNTER<n>_CFG`, `PERFCOUNTER_RSLT_CNTL`, and full-width `RESERVE<n>` placeholders.

These masks are normally paired with register offsets from `mmhub_9_3_0_offset.h` and consumed by AMDGPU helpers/macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and table-driven golden-setting or diagnostics code. The offset header supplies where to read/write; this header supplies how to pack or decode fields in the 32-bit value.

## Control Flow

This chunk has no runtime control flow. Its effect is through C preprocessing.

Typical consumer flow is:

1. MMHUB 9.3.0-specific driver code includes `mmhub_9_3_0_offset.h` and `mmhub_9_3_0_sh_mask.h`.
2. Code reads a register value with a SOC15 MMIO helper or constructs a new value for a register such as a `DAGB*_*_CNTL`/credit/control register.
3. It packs or extracts fields with the generated `__SHIFT`/`_MASK` constants, often through AMDGPU field helpers.
4. Runtime MMHUB init, golden-register programming, power/clock-gating setup, VM hub bring-up, debugging, or performance-counter code performs the actual MMIO transaction.

The header itself does not encode sequencing constraints. It does not say when DAGB clients are idle, when it is safe to change arbitration or credit limits, how to drain pending bitmaps, whether a field is sticky, or whether a register is firmware-owned. Those rules live in the MMHUB implementation files, firmware protocols, hardware specifications, and companion default/offset headers.

## State And Persistence Behavior

No software state is stored here. The macros describe hardware state in MMHUB DAGB decoder registers.

The represented hardware state includes:

- Persistent-until-reprogrammed configuration: client-to-VC routing, urgency thresholds, max/min bandwidth policy, OSD limits, SCLK/window fields, GMI credits, DAGB enable/jump-ahead/self-init, VC remapping, burst limits, lazy timers, credit pools, and clock-gating overrides.
- Live or status-like state: pending busy bitmaps, FIFO empty/full fields, read/write credit-full indicators, and performance counter low/high result values.
- Trigger/control state: performance counter `ENABLE`, `CLEAR`, `CLEAR_ALL`, `START_TRIGGER`, `STOP_TRIGGER`, and `STOP_ALL_ON_SATURATE` fields can alter counter collection behavior.
- Reserved placeholders: `DAGB0_RESERVE0..17` expose full-width masks for reserved registers/slots. Their presence preserves generated register-map shape but does not imply safe software use.

Persistence is hardware-defined. Configuration fields may survive until ASIC reset, suspend/resume, power-gating reset, driver reinitialization, or explicit reprogramming. Status and counter fields may change continuously with traffic. The generated mask file cannot distinguish read-only, write-one-to-clear, write-trigger, debug-only, or reserved semantics.

## Dependencies

This chunk depends on the generated AMDGPU/SOC15 register stack:

- `mmhub_9_3_0_offset.h` provides the matching MMHUB 9.3.0 register offsets for the field names described here.
- Later chunks of `mmhub_9_3_0_sh_mask.h` complete the same header, including the rest of `DAGB1_RD_CNTL_MISC` and later DAGB1/MMHUB field families.
- SOC15 register helpers and AMDGPU field helpers consume these macros to build register values and decode readbacks.
- MMHUB implementation files, VM hub setup, power-management code, diagnostics, and golden-register programming depend on these field definitions matching the hardware register database for MMHUB 9.3.0.

The sibling MMHUB headers (`mmhub_9_1`, `mmhub_9_4_1`, `mmhub_4_*`, `mmhub_3_*`, and older `mmhub_1_*`/`2_*`) are structurally similar but not interchangeable. Cross-generation field names can compile while producing invalid bit packing if paired with the wrong ASIC generation.

## Integration Points

Primary integration points are:

- MMHUB 9.3.0 driver code that includes the corresponding offset and mask headers for initialization, register programming, suspend/resume restore, and debug paths.
- GPUVM/MMHUB setup paths that rely on the memory hub to arbitrate read/write traffic between memory clients, virtual channels, ATC/VM, L1 TLB, VM L2, storage/EA pools, and GMI/IO paths.
- Clock and power management flows that program `*_CGTT_CLK_CTRL`, light-sleep override, soft-stall override, and clock-gating disable fields.
- Performance and diagnostic flows that inspect `*_PENDING`, FIFO/full-credit status, and `DAGB0_PERFCOUNTER*` fields to diagnose stalls, bandwidth limits, or arbitration behavior.
- Golden-register or bring-up tables that write conservative hardware-recommended defaults for DAGB arbitration, credit, burst, timer, and clock-gating fields.
- Multi-instance MMHUB code. The nearly mirrored `DAGB0` and `DAGB1` names imply instance-like programming patterns; later code may compute register distances or loop over instances using paired offset macros while using these masks for common fields.

## Risks And Edge Cases

- Wrong generation pairing is the main risk. Using `mmhub_9_3_0_sh_mask.h` with offsets or driver code for a different MMHUB generation can silently pack the wrong bits.
- This chunk boundary is artificial and cuts through `DAGB1_RD_CNTL_MISC`; any per-file summary must merge later chunks before treating the DAGB1 field set as complete.
- Repeated layouts invite copy/paste or looped programming, but read-client, write-client, address-DAGB, data-DAGB, and VC-control registers have different field sets. A shared helper must select the exact register family, not just substitute `RD`/`WR` or `DAGB0`/`DAGB1` textually.
- Credit, bandwidth, and outstanding-depth fields are performance- and liveness-sensitive. Bad values can throttle memory traffic, overcommit downstream queues, create unfair arbitration, or contribute to timeout/deadlock symptoms.
- `CHECK_TLB_CREDIT`, TLB credit fields, ATC/VM clock controls, and VM L2 credit fields affect address translation paths. Incorrect programming can surface as VM faults, invalidation stalls, or memory-access hangs rather than obvious register errors.
- Clock-gating and light-sleep overrides can cause power regressions or access instability if toggled while queues are active or if firmware expects ownership.
- Pending/FIFO/credit-full fields are status-like; treating them as ordinary writable configuration would be unsafe unless the hardware spec explicitly says otherwise.
- Performance counter clear/enable fields can lose diagnostic state or skew profiling if written during active collection.
- Reserved full-width fields should not be used as a license to write arbitrary values. They are generated placeholders for reserved register slots.

## Test Signals

Useful validation signals include:

- Build coverage for MMHUB 9.3.0 AMDGPU paths that include `mmhub_9_3_0_offset.h` and `mmhub_9_3_0_sh_mask.h`.
- Static consistency checks that every field has both `__SHIFT` and `_MASK`, that repeated client/VC families use expected masks, and that this header remains synchronized with the generated offset/default headers for MMHUB 9.3.0.
- Boot/init tests on ASICs using MMHUB 9.3.0, with attention to VM hub setup, memory hub init, golden-register programming, and power-management transitions.
- GPUVM stress tests that allocate mappings, trigger TLB/VM traffic, perform invalidations, and run mixed read/write workloads while checking for VM faults, invalidation timeouts, or MMHUB hangs.
- Suspend/resume, BACO, reset, and runtime power-management tests that confirm DAGB arbitration and clock-gating settings are restored correctly.
- Performance-counter/debug tests that program `DAGB0_PERFCOUNTER*`, read low/high results, clear counters, and correlate pending/FIFO/credit status with known traffic.
- Regression indicators include ring timeouts, memory-client stalls, MMHUB/GPUVM faults, unexpected bandwidth throttling, power-management failures, incorrect performance-counter readings, or debug status that shows persistent pending/credit-full conditions after traffic drains.

### subset-b-002831: lines 2368-4743

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

### subset-b-002832: lines 4744-7094

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_3_0_sh_mask.h lines 4744-7094

## Scope

This chunk is a middle range of the generated AMDGPU MMHUB 9.3.0 shift/mask header. It contains only C preprocessor constants for register-field bit positions and bit masks. There are no functions, structs, storage declarations, includes, or executable branches in this range.

The chunk begins in the middle of `MMEA0_IO_WR_PRI_URGENCY_MASK`, then completes the remaining `MMEA0` arbiter, SDP, performance, EDC, DSM, clock-gating, and error-status field definitions. It then starts the parallel `MMEA1` register block, covering DRAM arbitration, DRAM address normalization/decoding, IO arbitration, SDP, performance, and EDC fields before ending in the middle of `MMEA1_DSM_CNTL`.

The constants in this file must be paired with `mmhub_9_3_0_offset.h`, which supplies matching `mmMMEA*` register offsets. In this tree there is no exact C runtime file including `mmhub_9_3_0_sh_mask.h`; nearby MMHUB generations, especially `amdgpu/mmhub_v9_4.c`, show the same SOC15-style integration pattern for `MMEA*` EDC/RAS fields.

## Purpose

The purpose of this chunk is to expose the bit-level software contract for two MMHUB memory-macro/arbiter instances, `MMEA0` and `MMEA1`, on MMHUB 9.3.0 hardware. These register definitions describe how software can compose or decode MMIO values for:

- DRAM and IO client-to-group mapping.
- Read/write group-to-virtual-channel mapping.
- DRAM address normalization, bank/channel/hash/harvest configuration, chip-select base/mask/config/select fields, column selection, and row-machine selection.
- DRAM and IO priority arbitration, aging, queuing, fixed priority, urgency, urgency masking, and quantum thresholds.
- SDP arbitration limits, response/tag credit reservation, virtual-channel credit reservation, request overrides, and miscellaneous link-manager behavior.
- Latency sampling and per-instance performance counters.
- EDC/RAS correctable, deferred, and single-error-detected counter fields.
- DSM irritator and single-write controls used for memory-test or debug-style behavior.
- Clock gating/training-test control and error status fields.

The macros are generated ABI-like data: driver code, debug tooling, firmware-facing paths, or RAS/perf code can rely on exact `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` names and values to program 32-bit registers safely.

## Important Macro Families

### `MMEA0` IO Priority Tail

The first visible lines finish `MMEA0_IO_WR_PRI_URGENCY_MASK`, defining one bit per client ID from `CID4_MASK` through `CID31_MASK` in the visible range. The matching shifts for the full register start before this chunk. The following `MMEA0_IO_RD_PRI_QUANT_PRI1..3` and `MMEA0_IO_WR_PRI_QUANT_PRI1..3` blocks define four 8-bit `GROUP0_THRESHOLD` through `GROUP3_THRESHOLD` fields per priority-quantum register.

These fields belong with the `mmMMEA0_IO_*` offsets around `0x01dc` through `0x01eb` in `mmhub_9_3_0_offset.h`. They govern IO read/write arbitration policy by group and client ID.

### `MMEA0` SDP Arbitration and Credits

The `MMEA0_SDP_ARB_DRAM` and `MMEA0_SDP_ARB_FINAL` blocks define burst-limit and switching controls:

- DRAM arbitration has `RDWR_BURST_LIMIT_CYCL`, `RDWR_BURST_LIMIT_DATA`, early read/write switching on priority or reservation, and `EOB_ON_EXPIRE`.
- Final SDP arbitration splits burst limits across DRAM, GMI, and IO, adds `BURST_LIMIT_MULTIPLIER`, read-only controls for `VC0..VC7`, and error policy bits `ERREVENT_ON_ERROR` and `HALTREQ_ON_ERROR`.

`MMEA0_SDP_DRAM_PRIORITY` and `MMEA0_SDP_IO_PRIORITY` define 4-bit priorities for read and write groups 0 through 3. `MMEA0_SDP_CREDITS` defines tag, write-response, and read-response credit limits. `MMEA0_SDP_TAG_RESERVE0/1`, `MMEA0_SDP_VCC_RESERVE0/1`, and `MMEA0_SDP_VCD_RESERVE0/1` reserve tag and credit resources by virtual channel.

### `MMEA0` Request, Misc, Latency, and Perf Counters

`MMEA0_SDP_REQ_CNTL` contains request override bits for read, write, atomic, and DRAM-chain behavior plus `INNER_DOMAIN_MODE`.

`MMEA0_MISC` defines relative-priority selection for DRAM/GMI/IO read and write arbiters, return-data swap behavior, early SDP original-data behavior, link-manager dynamic mode, halt/reconnect/idle thresholds, midchain/last chip-select favoring, and write-to-read switch controls.

`MMEA0_LATENCY_SAMPLING` defines two independent samplers. Each sampler can filter by DRAM/GMI/IO, read/write/atomic-return/atomic-no-return traffic, and virtual channel. The VC fields are eight-bit masks at `SAMPLER0_VC` and `SAMPLER1_VC`.

`MMEA0_PERFCOUNTER_LO`, `MMEA0_PERFCOUNTER_HI`, `MMEA0_PERFCOUNTER0_CFG`, `MMEA0_PERFCOUNTER1_CFG`, and `MMEA0_PERFCOUNTER_RSLT_CNTL` define low/high counter value fields, high-word compare value, event-selection ranges, counter mode, enable/clear bits, trigger selectors, global enable, clear-all, and stop-on-saturate behavior.

### `MMEA0` EDC, DSM, Clock, and Error Fields

`MMEA0_EDC_CNT` and `MMEA0_EDC_CNT2` expose compact 2-bit counters for memory error classes:

- DRAM read command memory SEC/DED.
- DRAM write command memory SEC/DED.
- DRAM write data memory SEC/DED.
- Read-return and write-return tag memory SEC/DED.
- DRAM page memory SED.
- IO read/write command memory SED.
- IO write data memory SED.
- GMI read/write command memory SEC/DED.
- GMI write data memory SEC/DED.
- GMI page memory SED.

`MMEA0_DSM_CNTL`, `MMEA0_DSM_CNTLA/B`, `MMEA0_DSM_CNTL2`, and `MMEA0_DSM_CNTL2A/B` define DSM irritator data and single-write enable fields for the same memory categories, with duplicated A/B blocks for command/data/page/tag domains.

`MMEA0_CGTT_CLK_CTRL` has test clock-gating and handshake fields such as `SOFT_OVERRIDE0..3`, `ACTIVATE`, `WEIGHT`, delay, `LS_OVERRIDE`, and auto-calibration controls. `MMEA0_EDC_MODE` enables EDC-related operation for command, data, page, tag, and auto mode. `MMEA0_ERR_STATUS` reports address and credit FIFO error bits, split between clearable and raw status fields. `MMEA0_MISC2` currently exposes `TAG_PARITY_CHECK_EN`.

### `MMEA1` DRAM Arbitration and Address Decoding

The `MMEA1` block starts at `MMEA1_DRAM_RD_CLI2GRP_MAP0`. `DRAM_RD_CLI2GRP_MAP0/1` and `DRAM_WR_CLI2GRP_MAP0/1` assign client IDs `CID0..CID31` to four arbitration groups using two-bit fields. `MMEA1_DRAM_RD_GRP2VC_MAP` and `MMEA1_DRAM_WR_GRP2VC_MAP` then map groups 0 through 3 to virtual channels.

`MMEA1_DRAM_RD_LAZY`, `MMEA1_DRAM_WR_LAZY`, `MMEA1_DRAM_RD_CAM_CNTL`, `MMEA1_DRAM_WR_CAM_CNTL`, and `MMEA1_DRAM_PAGE_BURST` define lazy timer, header/response age, hash modes, CAM enablement, CAM depth, sequence maintenance, and page-burst controls.

The priority blocks mirror the IO priority pattern:

- `MMEA1_DRAM_RD_PRI_AGE` and `MMEA1_DRAM_WR_PRI_AGE` define 8-bit per-group aging limits.
- `MMEA1_DRAM_RD_PRI_QUEUING` and `MMEA1_DRAM_WR_PRI_QUEUING` define 2-bit per-group queuing priorities.
- `MMEA1_DRAM_RD_PRI_FIXED` and `MMEA1_DRAM_WR_PRI_FIXED` define 2-bit fixed priorities.
- `MMEA1_DRAM_RD_PRI_URGENCY` and `MMEA1_DRAM_WR_PRI_URGENCY` define 4-bit per-group urgency.
- `MMEA1_DRAM_*_QUANT_PRI1..3` define 8-bit per-group quantum thresholds.

The `MMEA1_ADDRNORM*`, `MMEA1_ADDRDEC*`, and `MMEA1_ADDRDECDRAM*` groups are the densest register families in this chunk. They describe normalized DRAM apertures, hole control, tri-channel config, bank config, misc decoder settings, address hash selection for banks/page control/chip selects, harvest enablement, base addresses for primary and secondary chip selects, masks for chip-select pairs, chip-select address configuration, address bit selection, column bit selection, and row-machine selection for two decoder instances (`ADDRDEC0` and `ADDRDEC1`).

### `MMEA1` IO, SDP, Perf, EDC, and DSM Start

`MMEA1_IO_RD_CLI2GRP_MAP0/1` and `MMEA1_IO_WR_CLI2GRP_MAP0/1` mirror the `MMEA1` DRAM client mapping layout for IO traffic. `MMEA1_IO_RD_COMBINE_FLUSH`, `MMEA1_IO_WR_COMBINE_FLUSH`, and `MMEA1_IO_GROUP_BURST` add flush timers and per-group burst behavior. The `MMEA1_IO_*_PRI_*`, urgency-mask, and quantum-priority blocks then mirror the same age/queuing/fixed/urgency/threshold layout used by `MMEA0`.

`MMEA1_SDP_*`, `MMEA1_MISC`, `MMEA1_LATENCY_SAMPLING`, and `MMEA1_PERFCOUNTER*` mirror the `MMEA0` SDP, misc, latency sampling, and perf-counter register layouts. The corresponding offsets in `mmhub_9_3_0_offset.h` run from `mmMMEA1_SDP_ARB_DRAM` at `0x032c` through `mmMMEA1_PERFCOUNTER_RSLT_CNTL` at `0x0340`.

The chunk then defines `MMEA1_EDC_CNT` and `MMEA1_EDC_CNT2` with the same 2-bit SEC/DED/SED counter fields described for `MMEA0`. It ends in the middle of `MMEA1_DSM_CNTL`, after defining DRAM, return-tag, and GMI DSM irritator/single-write fields through `GMIWR_DATAMEM_ENABLE_SINGLE_WRITE_MASK`; `MMEA1_DSM_CNTLA` and later DSM definitions continue in the next chunk.

## Control Flow and Runtime Use

There is no control flow in this header chunk. Runtime behavior comes from code that includes the generated shift/mask header and uses these macros with matching offsets.

The common AMDGPU usage pattern is:

1. Select the correct register offset from `mmhub_9_3_0_offset.h`, such as `mmMMEA1_EDC_CNT`.
2. Use a field macro from this header through helpers such as `SOC15_REG_FIELD`, `REG_SET_FIELD`, or `REG_GET_FIELD`.
3. Read or write the 32-bit MMIO register through SOC15 helpers such as `RREG32_SOC15`, `WREG32_SOC15`, or `SOC15_REG_OFFSET`.

Nearby generation code in `amdgpu/mmhub_v9_4.c` illustrates direct RAS integration for the same `MMEA*` family: it builds `soc15_ras_field_entry` rows using `SOC15_REG_ENTRY(MMHUB, 0, mmMMEA0_EDC_CNT)` and `SOC15_REG_FIELD(MMEA0_EDC_CNT, DRAMRD_CMDMEM_SEC_COUNT)` style macros, then lists EDC counter registers for reset/collection. MMHUB 9.3.0 does not have an exact runtime include in this checked tree, so direct in-tree execution for these 9.3.0 constants was not found.

## State and Persistence Behavior

This file stores no software state. It names hardware state in MMIO registers. Values represented by these masks persist in the GPU register file until reset, power-gating loss, suspend/resume reinitialization, firmware/PF reprogramming, or explicit driver writes.

The state represented here is high impact:

- Priority, urgency, aging, and quantum fields can change DRAM/IO fairness and latency for clients.
- Client-to-group and group-to-VC maps determine which clients share arbitration groups and virtual channels.
- Address normalization and address-decoder fields control how physical DRAM addresses map to banks, channels, chip selects, columns, rows, and harvested regions.
- SDP credit and reserve fields govern outstanding tags and response credits; over-reservation can starve traffic while under-reservation can expose backpressure or ordering problems.
- Perf-counter and latency-sampling registers are diagnostic state and should be programmed/cleared consistently around sampling windows.
- EDC counters are RAS-observable hardware counters. They may be read, logged, and cleared by RAS flows, so field masks must preserve correct SEC/DED/SED classification.
- DSM and clock/test-control fields are debug/test state. Accidentally enabling irritator or test clock controls in production paths could perturb memory behavior.

## Dependencies and Integration Points

Generated-register dependencies:

- `mmhub_9_3_0_offset.h` provides the corresponding `mmMMEA0_*` and `mmMMEA1_*` register offsets. The visible chunk pairs with offsets such as `mmMMEA0_IO_RD_PRI_QUANT_PRI1` at `0x01e6`, `mmMMEA0_EDC_CNT` at `0x0206`, `mmMMEA1_DRAM_RD_CLI2GRP_MAP0` at `0x0240`, `mmMMEA1_IO_RD_PRI_URGENCY_MASK` at `0x0324`, and `mmMMEA1_EDC_CNT2` at `0x0347`.
- Earlier chunks of `mmhub_9_3_0_sh_mask.h` define the start of `MMEA0`, including the fields that precede the visible `MMEA0_IO_WR_PRI_URGENCY_MASK` tail.
- Later chunks define the rest of `MMEA1_DSM_CNTL` and the remaining `MMEA1` register families after line 7094.
- SOC15 register macros depend on the generated naming convention: `SOC15_REG_FIELD(MMEA1_EDC_CNT, DRAMRD_CMDMEM_SEC_COUNT)` expands through this header's `MMEA1_EDC_CNT__DRAMRD_CMDMEM_SEC_COUNT_MASK` and shift macro.

Driver and subsystem integration:

- MMHUB RAS code in nearby generations uses `MMEA*_EDC_CNT*` fields to build error-counter tables. The fields in this chunk are the natural source for any MMHUB 9.3.0 RAS table that reports SEC, DED, or SED counts.
- Performance and debug tools can use `MMEA*_PERFCOUNTER*` and `MMEA*_LATENCY_SAMPLING` for sampling MMEA traffic classes and VC activity.
- Memory-training, firmware, or low-level bring-up code can depend on `MMEA*_ADDRDEC*`, `MMEA*_ADDRNORM*`, and `MMEA*_ADDRDECDRAM*` to reflect the actual DRAM topology and harvest state.
- SR-IOV/PF-VF ownership matters for these registers. Address-decoder, RAS, DSM, and arbitration policy registers are typically PF-owned or firmware-owned resources; VF code should not assume it can safely program them.

## Risks and Edge Cases

- Mixing `mmhub_9_3_0_sh_mask.h` with another generation's offset header can silently program wrong registers or bit positions. Many `MMEA*` names recur across MMHUB generations.
- This chunk starts and ends across register boundaries. A merge or generated-header split that drops the preceding `MMEA0_IO_WR_PRI_URGENCY_MASK` shifts, or the following `MMEA1_DSM_CNTL` continuation, will leave incomplete research context and may hide field-pairing mistakes.
- Client-to-group maps use dense 2-bit fields for 32 client IDs across paired registers. Off-by-one client IDs can move traffic into the wrong arbitration group.
- Urgency mask registers use one bit per client ID. Wrong polarity or wrong CID bit can make a client permanently urgent or permanently masked from urgency handling.
- Address decoder fields are topology-sensitive. Incorrect base, mask, select, column, row-machine, hash, or harvest fields can misroute memory traffic, corrupt data, or break memory interleaving.
- SDP credit/tag reservations can deadlock or starve traffic if programmed inconsistently with hardware capacity and VC policy.
- RAS EDC counters pack many 2-bit fields into one register. A bad mask can swap SEC and DED accounting or hide uncorrectable/deferred conditions from RAS reporting.
- DSM irritator and single-write fields should be treated as test/debug controls. Unexpected writes to these fields can intentionally inject unusual memory behavior.
- Read-modify-write users must preserve reserved bits. These masks are field-level helpers, not whole-register default values.

## Test and Verification Signals

Useful validation signals for this chunk are generated-header build coverage, register-field expansion checks, and hardware readback on supported ASICs:

- Compile any MMHUB 9.3.0 consumer with both `mmhub_9_3_0_offset.h` and `mmhub_9_3_0_sh_mask.h` included, ensuring all `SOC15_REG_FIELD`, `REG_SET_FIELD`, and `REG_GET_FIELD` references resolve.
- Add or run static checks that every visible `REGISTER__FIELD__SHIFT` has a matching `REGISTER__FIELD_MASK` where appropriate, especially for cross-boundary `MMEA0_IO_WR_PRI_URGENCY_MASK` and `MMEA1_DSM_CNTL`.
- RAS tests should read `MMEA0_EDC_CNT`, `MMEA0_EDC_CNT2`, `MMEA1_EDC_CNT`, and `MMEA1_EDC_CNT2`, decode SEC/DED/SED fields, and verify that clear/readback flows do not conflate adjacent 2-bit counters.
- Perf tests should program `MMEA*_PERFCOUNTER*_CFG`, enable counting through `MMEA*_PERFCOUNTER_RSLT_CNTL`, and verify low/high counter readback plus clear and stop-on-saturate behavior.
- Latency-sampling tests should toggle sampler filters and VC masks and verify only expected DRAM/GMI/IO and read/write/atomic traffic is counted.
- Firmware or bring-up validation should compare `MMEA1_ADDRDEC*` and `MMEA1_ADDRNORM*` readback against expected DRAM topology, chip-select layout, hash, and harvest state.
- Arbitration smoke tests should exercise representative DRAM and IO clients under load and look for starvation, unexpected latency spikes, or deadlocks after priority/credit programming.
- Suspend/resume, GPU reset, and SR-IOV tests should verify that PF-owned MMEA arbitration, address-decoder, EDC, and debug/test registers are restored or left under firmware ownership as appropriate.

## Cross-Chunk Notes

This chunk is not a complete per-file view. The final reconciliation report should merge it with earlier chunks that define the beginning of `MMEA0` and with later chunks that complete `MMEA1_DSM_CNTL` plus the remaining MMEA/MMHUB 9.3.0 register blocks. The source path and line range above should remain attached to this chunk because it covers only lines 4744-7094.

### subset-b-002833: lines 7095-9511

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_3_0_sh_mask.h lines 7095-9511

## Scope

This chunk covers generated shift and mask macros from the AMD MMHUB 9.3.0 register mask header. It starts in the middle of the `MMEA1_DSM_CNTL` family and ends inside the `VM_CONTEXT0_PAGE_TABLE_START_ADDR_HI32` register, after the high logical-page-number shift definition but before that field's mask in the next chunk. The covered range includes:

- `MMEA1` diagnostic/safety/error-injection fields, clock-gating controls, EDC mode, error status, and memory-arbitration miscellaneous fields.
- `mmhub_pctldec` power-controller fields for deep sleep, page-gating ignore control, DAGB deep-sleep state, RENG RAM access/execution, and register-save ranges for `PCTL0`, `PCTL1`, and `PCTL2`.
- `mmhub_l1tlb_vml1dec` L1 TLB status registers for TLB instances 0 through 7.
- `mmhub_l1tlb_vml1pldec` and `mmhub_l1tlb_vml1prdec` L1 TLB performance-counter configuration, result control, and counter data windows.
- `mmhub_utcl2_atcl2dec` ATC L2 control, cache-data, status, clock-gating, and memory light-sleep fields.
- `mmhub_utcl2_vml2pfdec` VM L2 cache, page-fault/default-address, protection-fault, identity-aperture, bank-selection, parity, clock-gating, and real-time-class fields.
- `mmhub_utcl2_vml2vcdec` VM context controls for contexts 0 through 15, context-disable bits, invalidate-engine semaphore/request/ack/address-range registers for engines 0 through 17, and the beginning of VM context page-table base/start address registers.

The file is a generated hardware bitfield map. This chunk defines preprocessor constants only: there are no C functions, structs, variables, allocations, or executable branches here.

## Purpose

This header section provides the bit-level ABI used by AMDGPU MMHUB code when composing or decoding 32-bit MMIO register values for MMHUB 9.3.0. Each field follows the generated convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit mask used to isolate or insert the field.

The sibling `mmhub_9_3_0_offset.h` file supplies register addresses such as `mmPCTL_MISC`, `mmVM_L2_CNTL`, and `mmVM_CONTEXT0_CNTL`; this file supplies the field layouts for those register addresses. Driver code normally consumes these definitions through register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_OFFSET`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET`.

## Important Macro Families

### MMEA1 DSM, EDC, Error, and Arbitration Fields

The opening lines continue from the prior chunk's `MMEA1_DSM_CNTL` register. The visible fields cover DSM irritator data and single-write enables for DRAM read/write command memories, DRAM write data memory, read/write return tag memories, and GMI read/write command/data memories. `MMEA1_DSM_CNTLA` repeats the same pattern for page-memory and IO command/data paths, while `MMEA1_DSM_CNTL2` and `MMEA1_DSM_CNTL2A` define error-injection enables, inject-delay selection bits, and a shared `INJECT_DELAY` field for command/data/page memories.

`MMEA1_CGTT_CLK_CTRL` controls local clock-gating timing and overrides through `ON_DELAY`, `OFF_HYSTERESIS`, soft-stall override bits for write/read/return paths, `LS_OVERRIDE`, and soft override bits for write/read/return/register domains.

`MMEA1_EDC_MODE` exposes EDC behavior flags including fed-out counting, FUE gating, DED mode, FED propagation, and bypass. `MMEA1_ERR_STATUS` reports SDP read/write response status, read-response data status, data parity error, busy-on-error, FUE flag, and a `CLEAR_ERROR_STATUS` command bit. `MMEA1_MISC2` covers CSGROUP swap controls, DRAM/GMI burst limits, and IO read/write priority enable.

### MMHUB Power Controller and Register Save/Restore

The `mmhub_pctldec` block starts with `PCTL_MISC`, which controls deep-sleep allowance, RSMU/DAGB idle thresholds, whether STCTRL ignores protection faults, EA0/EA1 SDP acknowledgements, and page-gating FSM command status.

`PCTL_MMHUB_DEEPSLEEP`, `PCTL_MMHUB_DEEPSLEEP_OVERRIDE`, `PCTL_PG_IGNORE_DEEPSLEEP`, and `PCTL_PG_DAGB` define dense per-domain `DS0` through `DS16` bitmaps. The deep-sleep register also includes a top-bit `SETCLEAR` selector, while the ignore register adds an `ALLIPS` bit. These masks encode which MMHUB subdomains may enter deep sleep, which domains are overridden, which domains page gating should ignore, and which deep-sleep domains interact with DAGB.

`PCTL0_RENG_*`, `PCTL1_RENG_*`, and `PCTL2_RENG_*` expose three RENG control windows. Each instance has a RAM index, full 32-bit RAM data, execution control bits for power-up execution, immediate execution, immediate-mode selection, start/end pointers, and execution-on-register-update. `PCTL0` uses wider 11-bit RENG pointers than `PCTL1` and `PCTL2`, which use 10-bit pointers. The matching `PCTL*_MISC` registers lock critical registers, set tile idle thresholds, enable RENG memory light sleep, force PGFSM command completion, and, for `PCTL1`/`PCTL2`, control deep-sleep disconnect from SDP.

The `PCTL*_STCTRL_REGISTER_SAVE_RANGE0..4` registers encode base/limit pairs for state-controller register-save ranges. `PCTL*_STCTRL_REGISTER_SAVE_EXCL_SET` and `PCTL*_STCTRL_REGISTER_SAVE_EXCL_SET1` encode excluded register IDs. These fields describe hardware state-save coverage used around power transitions, not software persistence in this header.

### L1 TLB Status and Performance Counters

The `MC_VM_MX_L1_TLB0_STATUS` through `MC_VM_MX_L1_TLB7_STATUS` registers expose identical `BUSY` and `FOUND_PARITY_ERRORS` bits for eight L1 TLB instances.

The L1 performance-counter block defines `MC_VM_MX_L1_PERFCOUNTER0_CFG` through `MC_VM_MX_L1_PERFCOUNTER3_CFG`. Each counter has `PERF_SEL`, `PERF_SEL_END`, `PERF_MODE`, `ENABLE`, and `CLEAR` fields. `MC_VM_MX_L1_PERFCOUNTER_RSLT_CNTL` selects which counter is read and defines start/stop triggers, `ENABLE_ANY`, `CLEAR_ALL`, and `STOP_ALL_ON_SATURATE`.

The result-read block provides `MC_VM_MX_L1_PERFCOUNTER_LO` for the low 32 counter bits and `MC_VM_MX_L1_PERFCOUNTER_HI` for the high counter bits plus a compare value. These macros support profiling and debug paths that need MMHUB L1 TLB event counts.

### ATC L2 Control, Cache Data, Status, and Clock Gating

The `ATC_L2_*` registers describe the address-translation cache L2 path. `ATC_L2_CNTL` controls translation read/write request counts, whether request counts depend on address modifiers, cache-invalidate mode, and default-page output to system memory. `ATC_L2_CNTL2` selects banks, cache update mode, write-driven LRU updates, tag-index low-bit swap, VMID mode, and wildcard reference values.

`ATC_L2_CACHE_DATA0..2` expose cache-entry validity, cached attributes, virtual page address high/low portions, and physical page address. `ATC_L2_CNTL3` controls invalidation-request delay, ATS request credits, and component-clock request hysteresis.

`ATC_L2_STATUS` and `ATC_L2_STATUS2` report busy state and parity error information, including IFIFO nonfatal and fatal parity details. `ATC_L2_MISC_CG`, `ATC_L2_MEM_POWER_LS`, and `ATC_L2_CGTT_CLK_CTRL` define clock-gating and memory light-sleep controls for this cache block.

### VM L2 Cache and Page-Fault Handling

The `VM_L2_CNTL`, `VM_L2_CNTL2`, `VM_L2_CNTL3`, and `VM_L2_CNTL4` definitions control MMHUB's VM L2 cache behavior, L1/L2 invalidation, cache banking, update modes, hit/miss handling, PDE/PTE request behavior, IFIFO active-transaction limits, and clock-gating/light-sleep override behavior. These are core bring-up and reset registers for MMHUB address translation.

`VM_L2_STATUS` exposes cache/TLB busy and invalidation state. `VM_DUMMY_PAGE_FAULT_CNTL` plus `VM_DUMMY_PAGE_FAULT_ADDR_LO32/HI32` describe dummy-page fault behavior and the captured logical page address.

`VM_L2_PROTECTION_FAULT_CNTL`, `VM_L2_PROTECTION_FAULT_CNTL2`, `VM_L2_PROTECTION_FAULT_MM_CNTL3`, and `VM_L2_PROTECTION_FAULT_MM_CNTL4` define how range, PDE0, PDE1, valid, read, write, execute, NACK, dummy-page, and retry faults are interrupted, retried, redirected to defaults, or filtered by client ID. `VM_L2_PROTECTION_FAULT_STATUS` reports `MORE_FAULTS`, walker error, permission fault class, mapping error, client ID, read/write direction, atomic access, VMID, VF bit, and VFID. The matching address/default-address registers hold logical fault addresses and default physical page addresses.

The identity-aperture fields, `VM_L2_CONTEXT1_IDENTITY_APERTURE_LOW_ADDR_*`, `VM_L2_CONTEXT1_IDENTITY_APERTURE_HIGH_ADDR_*`, and `VM_L2_CONTEXT_IDENTITY_PHYSICAL_OFFSET_*`, encode logical aperture bounds and the physical offset for identity-mapped context 1 traffic.

`VM_L2_MM_GROUP_RT_CLASSES` is a 32-bit bitmap of real-time class assignment for MM client groups. `VM_L2_BANK_SELECT_RESERVED_CID` and `VM_L2_BANK_SELECT_RESERVED_CID2` reserve read/write client IDs for special bank-selection and invalidation behavior. `VM_L2_CACHE_PARITY_CNTL` controls parity checking and forced parity mismatch injection for 4K PTE, bigK PTE, and PDE caches, including bank/number/associativity selection.

### VM Contexts and Invalidation Engines

`VM_CONTEXT0_CNTL` through `VM_CONTEXT15_CNTL` are repeated context-control registers. Each context has fields for enabling the context, page-table depth, page-table block size, retry behavior for permission/invalid/other faults, and interrupt/default-response enables for range, dummy-page, PDE0, valid, read, write, and execute protection faults. The repeated layout lets AMDGPU program context 0 and then program contexts 1 through 15 using register-distance arithmetic.

`VM_CONTEXTS_DISABLE` provides per-context disable bits for contexts 0 through 15. The invalidate-engine block defines `VM_INVALIDATE_ENG0_SEM` through `VM_INVALIDATE_ENG17_SEM`, `REQ`, `ACK`, and address-range low/high registers. Each engine has a semaphore field, a request register with per-VMID invalidation request bits and flush/control modifiers, an ack register with a 16-bit ack bitmap, and optional address-range registers. The low address-range register carries an `S_BIT` plus low logical-page-address bits; the high register carries the remaining high address bits.

The chunk then starts the VM context page-table address block. `VM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32/HI32` through `VM_CONTEXT15_PAGE_TABLE_BASE_ADDR_LO32/HI32` hold page-directory-entry low/high words for all 16 contexts. The final visible complete register is `VM_CONTEXT0_PAGE_TABLE_START_ADDR_LO32`; the chunk ends after `VM_CONTEXT0_PAGE_TABLE_START_ADDR_HI32__LOGICAL_PAGE_NUMBER_HI4__SHIFT`, so the corresponding mask and subsequent context start/end address registers belong to the next chunk.

## Control Flow and State Behavior

This header has no runtime control flow. It affects behavior at compile time by defining how driver code constructs register writes and interprets register reads.

The state represented by this chunk lives in MMHUB hardware. Durable or latched state includes MMHUB power-controller deep-sleep selections, RENG RAM contents and execution pointers, state-controller save ranges, L1 TLB busy/parity status, performance-counter configuration and values, ATC L2 cache controls and cache-data windows, VM L2 cache configuration, protection-fault policy and captured fault status/address registers, identity-aperture bounds, VM context enable/page-table/fault policy registers, invalidation-engine requests and acks, and page-table base/start addresses.

Several fields are command-like rather than simple persistent configuration. Examples include `MMEA1_ERR_STATUS__CLEAR_ERROR_STATUS`, performance-counter `CLEAR`/`CLEAR_ALL`, RENG `RENG_EXECUTE_NOW`, VM L2 invalidation controls, fault-status capture/clear flows, and VM invalidate-engine request bits. Consumers must follow the ordering, polling, and timeout rules in MMHUB driver code and the hardware specification; the masks alone do not encode sequencing.

## Dependencies and Integration Points

The chunk depends on the generated AMD register-header convention:

- `mmhub_9_3_0_offset.h` supplies MMHUB 9.3.0 register addresses and base indices.
- AMDGPU register helpers consume the `__SHIFT` and `_MASK` definitions to build and read register values without hard-coded bit positions.
- Cross-generation MMHUB code often shares register names, but the exact layouts are generation-specific and must be paired with the matching offset/mask header.

Observed integration points in this source tree include `drivers/gpu/drm/amd/amdgpu/mmhub_v1_8.c`, which programs MMHUB L1 TLB controls, VM L2 controls, protection-fault policy, context controls, invalidation-engine offsets, and fault-status registers using the same `REG_SET_FIELD`/`SOC15_REG_OFFSET` patterns represented by these masks. That file also records MMHUB RAS CE/UE register entries for `MMEA1`, tying the `MMEA1` status/control space to error reporting.

The VM context and invalidation macros also integrate with common AMDGPU VM/GMC state. `struct amdgpu_vmhub` stores distances such as context register spacing, invalidate request spacing, and invalidate address-range spacing; those distances are derived from adjacent generated register offsets and are used to program repeated context and invalidate-engine registers.

Performance-counter masks are integration points for profiling and diagnostics. Power-controller and clock-gating masks integrate with power-management, suspend/resume, reset, and golden-register programming. Protection-fault masks integrate with VM fault interrupt handling, retry-fault behavior, default-page policy, and SR-IOV diagnostics through the VF/VFID status fields.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can write unrelated MMHUB fields, causing GPUVM faults, hangs during TLB/cache invalidation, missed interrupts, incorrect page-table configuration, bad power-state transitions, or misleading fault diagnostics.
- Many register families are mechanically repeated. `VM_CONTEXT0_CNTL` through `VM_CONTEXT15_CNTL` and invalidate engines 0 through 17 look regular, but consumers still depend on exact register spacing and field widths.
- Power-controller bits can affect hardware state save/restore and deep-sleep entry. Incorrect `PCTL_*` deep-sleep, RENG, or save-range programming can break suspend/resume, power gating, or register restoration.
- Error-injection and parity-forcing fields must remain restricted to diagnostics. Enabling MMEA1 DSM injection or VM L2 parity mismatch fields in normal paths can create artificial faults or poison error accounting.
- VM protection-fault policy fields determine whether faults interrupt, retry, or fall back to default pages. Incorrect policy can hide real memory faults, create interrupt storms, or make retryable faults unrecoverable.
- Invalidation-engine request/ack fields require sequencing. Issuing requests with wrong VMID bits, address ranges, or engine spacing can leave stale translations or make the driver wait on the wrong ack bit.
- The chunk begins and ends mid-family. The merge lane must combine it with adjacent chunks for the full `MMEA1_DSM_CNTL` and `VM_CONTEXT0_PAGE_TABLE_START_ADDR_HI32` definitions.

## Test and Validation Signals

Useful validation is mostly build, bring-up, and hardware-integration coverage:

- Build AMDGPU/MMHUB code that includes `mmhub/mmhub_9_3_0_sh_mask.h`; this catches missing or renamed macros.
- MMHUB/GMC initialization tests should verify L1 TLB enablement, VM L2 cache setup, bank selection, partition count, fault defaults, and context 0/context 1 programming.
- GPUVM tests should exercise VM context enablement, page-table depth/block-size fields, page-table base/start address programming, context disable bits, and retry-fault policy.
- TLB invalidation tests should issue full and address-range invalidations across supported engines and confirm matching ack bits and stale-translation removal.
- Page-fault tests should validate range, valid, read, write, execute, dummy-page, PDE, retry, NACK, and VF/VFID fault status reporting.
- Suspend/resume and power-gating tests should cover `PCTL_*` deep-sleep, RENG execution, state-controller register-save ranges, ATC/VM L2 clock-gating, and memory light-sleep fields.
- RAS and diagnostic tests should cover MMEA1 CE/UE reporting, EDC mode/status, parity status, parity injection controls, and status clear behavior.
- Performance-counter tests should configure L1 TLB performance events, enable/clear counters, read low/high counter data, and validate stop-on-saturate behavior.

## Unresolved Cross-Chunk References

This chunk starts after the `MMEA1_DSM_CNTL` register has already begun, so its earliest visible macros are the tail of that family. It ends after the `VM_CONTEXT0_PAGE_TABLE_START_ADDR_HI32__LOGICAL_PAGE_NUMBER_HI4__SHIFT` definition and before the associated mask. The final per-file research document should stitch this report with adjacent chunks to describe those register families completely.

### subset-b-002834: lines 9512-10265

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_3_0_sh_mask.h lines 9512-10265

## Scope

This chunk covers the final 754 lines of the generated AMD MMHUB 9.3.0 shift/mask header. The range contains 561 `#define` statements and the closing `#endif`; it has no C functions, structs, enums, variables, allocations, locks, or executable branches.

The chunk starts in the middle of the VM context page-table aperture definitions and then covers these address blocks:

- Tail of the VM context block: `VM_CONTEXT0..15_PAGE_TABLE_START_ADDR_{LO32,HI32}` and `VM_CONTEXT0..15_PAGE_TABLE_END_ADDR_{LO32,HI32}` field masks.
- `mmhub_utcl2_vml2pldec`: MC VM L2 performance-counter configuration and result-control fields.
- `mmhub_utcl2_vml2prdec`: MC VM L2 performance-counter result low/high fields.
- `mmhub_utcl2_vmsharedhvdec`: per-VF framebuffer size/offset fields, IOMMU/MARC/ATS controls, UTCL2 clock-gating controls, active PF/VF selection, and XGMI GPUIOV enable fields.
- `mmhub_utcl2_vmsharedpfdec`: PF/shared northbridge MMIO, DRAM, aperture, local HBM, power, reset, and XGMI local-framebuffer fields.
- `mmhub_utcl2_vmsharedvcdec`: visible client/shared framebuffer, AGP, system aperture, and L1 TLB control fields.
- `mmhub_utcl2_atcl2pfcntrdec` and `mmhub_utcl2_atcl2pfcntldec`: ATC L2 performance-counter result and control fields.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU DRM register metadata and is not Ceph filesystem logic.

## Purpose

The purpose of this chunk is to provide the bitfield ABI used by driver code when composing or decoding 32-bit MMHUB 9.3.0 register values. Each hardware field is represented by the generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset.
- `<REGISTER>__<FIELD>_MASK`, the bit mask.

Consumers combine these macros with AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET`. The companion `mmhub_9_3_0_offset.h` supplies the numeric register offsets, while this file supplies the bit positions and masks for those offsets.

## Important Macro Families

### VM Context Aperture Bounds

The opening section defines low and high logical page-number fields for VM context page-table start and end addresses:

- `VM_CONTEXT0..15_PAGE_TABLE_START_ADDR_LO32__LOGICAL_PAGE_NUMBER_LO32`
- `VM_CONTEXT0..15_PAGE_TABLE_START_ADDR_HI32__LOGICAL_PAGE_NUMBER_HI4`
- `VM_CONTEXT0..15_PAGE_TABLE_END_ADDR_LO32__LOGICAL_PAGE_NUMBER_LO32`
- `VM_CONTEXT0..15_PAGE_TABLE_END_ADDR_HI32__LOGICAL_PAGE_NUMBER_HI4`

The low registers expose a full 32-bit logical page number. The high registers expose the upper 4 bits through mask `0x0000000f`, matching the common AMDGPU pattern where virtual memory aperture boundaries are programmed as page numbers split across low 32 bits and high 4 bits. Nearby MMHUB setup code for related generations writes these register families from `adev->gmc.gart_start` and `adev->gmc.gart_end` shifted by 12 and 44 bits.

This chunk begins after the `VM_CONTEXT0_PAGE_TABLE_START_ADDR_LO32` field definition and includes only the `VM_CONTEXT0_PAGE_TABLE_START_ADDR_HI32` mask plus contexts 1-15 start fields. The matching base-address fields and the first context-0 start low field are owned by previous chunks.

### MC VM L2 Performance Counters

`mmhub_utcl2_vml2pldec` defines `MC_VM_L2_PERFCOUNTER0_CFG` through `MC_VM_L2_PERFCOUNTER7_CFG`, plus `MC_VM_L2_PERFCOUNTER_RSLT_CNTL`. Each counter config has the same layout:

- `PERF_SEL` at bits 0-7.
- `PERF_SEL_END` at bits 8-15.
- `PERF_MODE` at bits 24-27.
- `ENABLE` at bit 28.
- `CLEAR` at bit 29.

`MC_VM_L2_PERFCOUNTER_RSLT_CNTL` selects the active counter, start trigger, stop trigger, global enable-any, clear-all, and stop-on-saturate behavior. The result block `mmhub_utcl2_vml2prdec` supplies `MC_VM_L2_PERFCOUNTER_LO__COUNTER_LO` and `MC_VM_L2_PERFCOUNTER_HI`, whose high register combines `COUNTER_HI` with a 16-bit `COMPARE_VALUE`. These fields support hardware performance sampling of the MMHUB VM L2 path.

### SR-IOV VF Framebuffer Apertures

`MC_VM_FB_SIZE_OFFSET_VF0` through `MC_VM_FB_SIZE_OFFSET_VF15` each pack two 16-bit fields:

- `VF_FB_SIZE` in bits 0-15.
- `VF_FB_OFFSET` in bits 16-31.

These registers describe framebuffer partitioning for up to 16 virtual functions. They are hypervisor/PF-owned state in typical SR-IOV deployments; guest/VF code should not assume it can rewrite them.

### IOMMU, MARC, and ATS Control

The chunk defines several memory-translation control families:

- `VM_IOMMU_MMIO_CNTRL_1__MARC_EN` enables MARC handling.
- `MC_VM_MARC_BASE_LO/HI_0..3` encode four MARC base addresses.
- `MC_VM_MARC_RELOC_LO/HI_0..3` encode four relocation targets, with `MARC_ENABLE_n` and `MARC_READONLY_n` bits in each low register.
- `MC_VM_MARC_LEN_LO/HI_0..3` encode region lengths.
- `VM_IOMMU_CONTROL_REGISTER__IOMMUEN` enables IOMMU behavior.
- `VM_IOMMU_PERFORMANCE_OPTIMIZATION_CONTROL_REGISTER__PERFOPTEN` enables an IOMMU performance optimization.
- `VM_PCIE_ATS_CNTL` exposes `STU` and `ATC_ENABLE` for the PF/global path.
- `VM_PCIE_ATS_CNTL_VF_0..15` expose per-VF `ATC_ENABLE` bits.

These fields sit on the boundary between PCIe ATS/ATC, IOMMU address translation, and MMHUB memory routing. The macros only define bit layout; valid sequencing depends on platform firmware, PF/VF policy, and the surrounding AMDGPU VM hub code.

### UTCL2 Clock and Function Selection

`UTCL2_CGTT_CLK_CTRL` defines clock-gating and test/override fields:

- `ON_DELAY`
- `OFF_HYSTERESIS`
- `SOFT_OVERRIDE_EXTRA`
- `MGLS_OVERRIDE`
- `SOFT_STALL_OVERRIDE`
- `SOFT_OVERRIDE`

`MC_SHARED_ACTIVE_FCN_ID` encodes a 4-bit `VFID` plus a high `VF` selector bit. `MC_VM_XGMI_GPUIOV_ENABLE` contains individual enable bits for VF0-VF15 and a PF enable bit at bit 31. These are virtualization and multi-GPU/XGMI integration fields; incorrect programming can expose or hide a function's memory view.

### PF/Shared Aperture and DRAM Controls

The `mmhub_utcl2_vmsharedpfdec` block defines masks for shared PF-side memory layout:

- `MC_VM_NB_MMIOBASE`, `MC_VM_NB_MMIOLIMIT`, `MC_VM_NB_PCI_CTRL`, and `MC_VM_NB_PCI_ARB` describe MMIO and VGA-hole behavior.
- `MC_VM_NB_TOP_OF_DRAM_SLOT1`, `MC_VM_NB_LOWER_TOP_OF_DRAM2`, and `MC_VM_NB_UPPER_TOP_OF_DRAM2` describe top-of-DRAM boundaries.
- `MC_VM_FB_OFFSET` shifts framebuffer placement.
- `MC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_LSB/MSB` encode the physical default page address split across low 32 bits and high 4 bits.
- `MC_VM_STEERING` selects default steering.
- `MC_SHARED_VIRT_RESET_REQ` exposes VF reset-request bits and a PF reset-request bit.
- `MC_MEM_POWER_LS` exposes light-sleep setup/hold timing.
- `MC_VM_CACHEABLE_DRAM_ADDRESS_START/END` and `MC_VM_LOCAL_HBM_ADDRESS_START/END` define address ranges.
- `MC_VM_LOCAL_HBM_ADDRESS_LOCK_CNTL__LOCK` locks the local HBM address range.
- `MC_VM_APT_CNTL` exposes `FORCE_MTYPE_UC` and `DIRECT_SYSTEM_EN`.
- `MC_VM_XGMI_LFB_CNTL` and `MC_VM_XGMI_LFB_SIZE` define PF local-framebuffer region and sizing.

Related MMHUB and GFXHUB generation code programs system aperture default addresses from `adev->mem_scratch.gpu_addr`, configures AGP/framebuffer aperture bounds, and skips or delegates some PF-only state under SR-IOV.

### Visible Client Aperture and L1 TLB Control

The `mmhub_utcl2_vmsharedvcdec` block defines visible/shared client memory aperture fields:

- `MC_VM_FB_LOCATION_BASE` and `MC_VM_FB_LOCATION_TOP` define framebuffer base/top fields.
- `MC_VM_AGP_TOP`, `MC_VM_AGP_BOT`, and `MC_VM_AGP_BASE` define the AGP aperture.
- `MC_VM_SYSTEM_APERTURE_LOW_ADDR` and `MC_VM_SYSTEM_APERTURE_HIGH_ADDR` define low/high logical aperture boundaries.
- `MC_VM_MX_L1_TLB_CNTL` controls the client-side L1 TLB.

`MC_VM_MX_L1_TLB_CNTL` is a high-value integration point. Its fields enable the L1 TLB, set system access mode, configure unmapped-access behavior, enable the advanced driver model, set ECO bits, choose memory type, and enable ATC. Same-family MMHUB code uses `REG_SET_FIELD` on this register while initializing and disabling the MMHUB L1 TLB.

### ATC L2 Performance Counters

The final address blocks define ATC L2 performance-counter results and controls:

- `ATC_L2_PERFCOUNTER_LO__COUNTER_LO`
- `ATC_L2_PERFCOUNTER_HI__COUNTER_HI` and `COMPARE_VALUE`
- `ATC_L2_PERFCOUNTER0_CFG` and `ATC_L2_PERFCOUNTER1_CFG`
- `ATC_L2_PERFCOUNTER_RSLT_CNTL`

The ATC L2 config layout mirrors the MC VM L2 performance-counter config: event selection, event range end, mode, enable, and clear bits. Result control provides selected counter, start/stop triggers, enable-any, clear-all, and stop-on-saturate fields.

## Control Flow

This header has no runtime control flow. Its effect is compile-time substitution of symbolic shift/mask constants into driver code.

The implied runtime flow is:

1. A MMHUB 9.3.0-aware driver path selects a register offset from `mmhub_9_3_0_offset.h`.
2. The driver uses a matching shift/mask macro from this header, usually through `REG_SET_FIELD` or `REG_GET_FIELD`.
3. SOC15 register helpers compute the actual MMIO address and read, write, or read-modify-write the register.
4. MMHUB hardware applies the programmed VM aperture, translation, ATS, virtualization, power, clock, or performance-counter state.

The exact `mmhub_9_3_0` headers are not referenced by any C source found under `drivers/gpu/drm/amd` in this tree. The active related code paths are same-family MMHUB/GFXHUB implementations such as `mmhub_v3_0.c`, `mmhub_v3_0_1.c`, `mmhub_v3_0_2.c`, and `gfxhub_v3_0_3.c`, which use equivalent generated offset and sh/mask headers for their ASIC revisions.

## State and Persistence Behavior

The macros themselves are stateless. The persistent and volatile state represented by this chunk exists in hardware registers.

Persistent configuration state includes VM context start/end page bounds, per-VF framebuffer partitioning, MARC base/relocation/length windows, IOMMU enable state, PCIe ATS enablement, MMIO/DRAM/FB/AGP/system aperture ranges, default page address, local HBM range and lock state, XGMI local-framebuffer sizing, and L1 TLB policy.

Volatile or command-like state includes performance-counter enable/clear fields, result-control clear-all and stop-on-saturate bits, active VF/PF selection, virtual reset request bits, clock-gating overrides, and ATC/MC VM counter result values. Some fields may be sticky, write-one-to-clear, self-clearing, privileged-only, or reset by GPU reset, suspend/resume, firmware initialization, PF host policy, or clock/power-gating transitions. This generated header does not encode access permissions or side-effect semantics.

## Dependencies and Integration Points

This chunk depends on the generated MMHUB 9.3.0 register set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_3_0_offset.h` contains the matching offsets and base indices for registers named here.
- AMDGPU field helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` depend on the exact `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` naming convention.
- SOC15 MMIO helpers depend on the matching offset header and ASIC block instance to address the correct MMHUB register aperture.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0.c`, `mmhub_v3_0_1.c`, and `mmhub_v3_0_2.c` show the same integration pattern for VM context page-table registers, system aperture default address registers, and `MC_VM_MX_L1_TLB_CNTL`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0_3.c` shows a related graphics-hub integration pattern for framebuffer location, system aperture default address, and L1 TLB control fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gmc.h` stores hub register addresses such as `MC_VM_MX_L1_TLB_CNTL` in `struct amdgpu_gmc`, showing that these fields are part of the broader GMC/VM setup surface.

Runtime integration areas include GART setup, VMID/context page-table aperture programming, system and AGP aperture setup, VRAM/framebuffer address discovery, default fault-page programming, MMHUB L1 TLB enable/disable, SR-IOV PF/VF framebuffer partitioning, PCIe ATS/ATC configuration, IOMMU/MARC configuration, XGMI GPUIOV enablement, performance monitoring, and reset/suspend/resume restoration.

## Risks and Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask compiles cleanly but silently writes the wrong hardware bits.
- This chunk starts mid logical register family. `VM_CONTEXT0_PAGE_TABLE_START_ADDR_LO32` is in the previous chunk, while this chunk starts with the context-0 high mask and then continues contexts 1-15.
- Repeated register families are easy to mis-index. Context 0-15 aperture bounds, VF0-VF15 framebuffer fields, VF0-VF15 ATS controls, and MARC region 0-3 fields rely on stable naming and ordering.
- Address split assumptions matter. Several fields split page or physical addresses across low 32 bits and high 4 bits; using byte addresses instead of page numbers, or shifting by the wrong amount, corrupts apertures.
- SR-IOV fields are isolation-sensitive. VF framebuffer size/offset, active function ID, reset requests, ATS enable bits, and XGMI GPUIOV enable bits should follow PF/hypervisor policy.
- `MC_VM_MX_L1_TLB_CNTL` affects address translation behavior. Wrong settings for system access, unmapped access, memory type, advanced driver model, or ATC can cause page faults, stale translations, incorrect coherency, or hangs.
- MARC/IOMMU/ATS controls cross firmware, PCIe, and VM boundaries. Enabling or relocating windows in the wrong order can create invalid translations or access-permission bypasses.
- Clock-gating override fields may be needed for debug or bring-up but can affect power/performance if left forced.
- Performance-counter clear/enable/result-control fields are shared hardware resources. Profiling code must avoid racing other users and must respect counter saturation and clear semantics.
- The exact `mmhub_9_3_0` headers have no C consumer in this tree. If support is later wired in, build coverage should verify that the naming prefixes expected by new code match these generated macros.

## Test Signals

Useful validation is mostly generated-data consistency plus hardware integration:

- Build AMDGPU configurations after adding any consumer of `mmhub_9_3_0_sh_mask.h`; missing or renamed macros should fail at compile time.
- Mechanically compare every shift and mask in this line range against AMD's authoritative MMHUB 9.3.0 register database.
- Cross-check that every register family in this chunk has matching offsets in `mmhub_9_3_0_offset.h`, including base indices.
- Verify repeated families for expected counts and contiguous layout: 16 VM contexts, 16 VF framebuffer size/offset registers, 16 per-VF ATS controls, 4 MARC regions, 8 MC VM L2 performance-counter configs, and 2 ATC L2 performance-counter configs.
- Exercise MMHUB initialization on matching hardware or emulation: GART aperture programming, system aperture/default fault page setup, AGP/framebuffer aperture setup, and L1 TLB enable/disable.
- Exercise SR-IOV PF and VF configurations and check that framebuffer partitions, reset requests, ATS enablement, and GPUIOV function enables remain isolated and host-controlled where required.
- Run VM fault injection or invalid mapping tests and confirm that page-table aperture boundaries and default page handling behave as expected.
- Run ATS/ATC/IOMMU workloads with peer/device memory access and check for translation failures, stale translations, or unexpected permission faults.
- Run XGMI or multi-GPU memory tests where available, checking local-framebuffer region/size and GPUIOV enable behavior.
- Use register dumps or debugfs decoding to confirm that `REG_GET_FIELD` extracts sensible values for framebuffer base/top, AGP/system aperture ranges, L1 TLB control, VF framebuffer partitions, and performance-counter status.
- Run MMHUB and ATC performance-counter sampling, checking that event selection, enable/clear, start/stop triggers, compare value, and stop-on-saturate behavior match reference expectations.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002834`. The final per-file research should merge this with neighboring chunks for full `mmhub_9_3_0_sh_mask.h` coverage. The previous chunk owns the preceding VM context base-address and context-0 start-low definitions. This chunk owns the file tail and closes the header with `#endif`.
