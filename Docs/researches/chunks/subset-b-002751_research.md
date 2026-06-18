# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_0_sh_mask.h lines 2368-4742

## Scope

This chunk is part of the generated AMD MMHUB 1.0 register bitfield header. It contains C preprocessor constants only, using the normal AMDGPU generated-register convention:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

There are no functions, structs, variables, direct MMIO operations, branches, locking paths, or allocation paths in this range. The source is hardware ABI data: consumers pair these masks and shifts with address definitions from `mmhub_1_0_offset.h` and access helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15`.

The covered line range starts in the tail of `DAGB1_RD_CNTL_MISC`, then covers the `DAGB1` read/write arbitration and pending-state registers, and then enters the `mmhub_ea_mmeadec` address block for `MMEA0` DRAM/GMI/IO client grouping, priority, address-normalization, and address-decode registers. The chunk ends mid-register at `MMEA0_IO_WR_PRI_URGENCY_MASK__CID21_MASK_MASK`; later chunk reconciliation must merge the remaining CID masks from the following lines.

## Purpose

The constants in this range describe how MMHUB 1.0 hardware register fields are packed into 32-bit values. Driver code uses them to compose values written into MMHUB registers and to decode register values read back for clock gating, diagnostics, error collection, memory-address decoding, and memory-fabric arbitration.

The high-level hardware areas are:

- `DAGB1` data/address gather block fields for read/write client configuration, virtual-channel selection, urgency thresholds, bandwidth limits, credit accounting, clock gating, pending/busy state, debug delay selection, FIFO state, performance counters, and reserved scratch-like registers.
- `MMEA0` memory-mapping/address-decode fields for assigning client IDs to arbitration groups, mapping groups to virtual channels, tuning DRAM and IO priority algorithms, configuring normalized address ranges, DRAM holes, bank/channel/chip-select masks, hashing, harvesting, and chip-select decode tables.
- Status/counter-style fields such as pending masks, FIFO empty/full masks, credit fullness, and performance counter result controls.

This chunk does not implement MMHUB behavior by itself. Its effect is indirect: included C files use the symbolic field names when they program or inspect the MMHUB block.

## Important Macro Families

### DAGB1 Read/Write Client And Credit Controls

`DAGB1_RD_CNTL_MISC` and `DAGB1_WR_CNTL_MISC` define shared pool-credit and legacy coherency-control fields. The fields include storage pool credit, EA pool credit, IO-to-EA credit, storage/EA client-coherency legacy mode, and `UTCL2_CID`.

`DAGB1_RD_TLB_CREDIT` and `DAGB1_WR_TLB_CREDIT` split a register into six 5-bit TLB credit fields (`TLB0` through `TLB5`). These values bound MMHUB translation-side concurrency and are sensitive to deadlock and starvation tuning.

`DAGB1_WRCLI0` through `DAGB1_WRCLI15` repeat the same per-client layout: `VIRT_CHAN`, `CHECK_TLB_CREDIT`, high and low urgency thresholds, max/min bandwidth enable and value fields, OSD limiter enable, and max outstanding data. These define how each write client is routed and throttled. The repeated layout is regular, but the client indices are semantically distinct because hardware clients map to fixed CIDs.

`DAGB1_WR_CNTL`, `DAGB1_WR_GMI_CNTL`, `DAGB1_WR_ADDR_DAGB`, and `DAGB1_WR_DATA_DAGB` define aggregate write-path controls such as stalling, outstanding read/write client counts, urgent limits, GMI versus storage credit, buffer sizes, request size selection, bank-swizzle disable, virtual-channel enable, and LB/RTI buffers.

`DAGB1_WR_OUTPUT_DAGB_MAX_BURST`, `DAGB1_WR_OUTPUT_DAGB_LAZY_TIMER`, `DAGB1_WR_ADDR_DAGB_MAX_BURST[0-1]`, `DAGB1_WR_ADDR_DAGB_LAZY_TIMER[0-1]`, `DAGB1_WR_DATA_DAGB_MAX_BURST[0-1]`, and `DAGB1_WR_DATA_DAGB_LAZY_TIMER[0-1]` pack per-virtual-channel burst and lazy-timer limits. The recurring fields `VC0` through `VC7` are eight-bit or four-bit slices used to tune batching and flush behavior per virtual channel.

`DAGB1_WR_VC0_CNTL` through `DAGB1_WR_VC7_CNTL` repeat virtual-channel controls: storage credit, EA credit, max/min bandwidth enable and values, OSD limiter enable, and max OSD. These are group-level resource controls rather than per-client controls.

`DAGB1_WR_DATA_CREDIT` and `DAGB1_WR_MISC_CREDIT` add write-data and miscellaneous credit pools for deadlock virtual channels, burst categories, atomics, OSD, and OSD deadlock credits.

### DAGB1 Pending, Clock-Gating, Debug, And Perf State

`DAGB1_RDCLI_*_PENDING` and `DAGB1_WRCLI_*_PENDING` expose full-width `BUSY` masks for ask/go/global-send/TLB/OARB/OSD stages, plus DBUS ask/go pending masks on the write side. These are observational fields used to diagnose pipeline backlog or wait for quiescence.

`DAGB1_WR_CGTT_CLK_CTRL`, `DAGB1_L1TLB_WR_CGTT_CLK_CTRL`, and `DAGB1_ATCVM_WR_CGTT_CLK_CTRL` define clock-gating delay, hysteresis, light-sleep override, and soft override fields for write-side DAGB, L1 TLB, and ATCVM subblocks. In `mmhub_v1_0.c`, nearby `DAGB1_CNTL_MISC2` masks are used to enable and disable MMHUB clock-gating behavior, so this family is part of the same power-management register vocabulary.

`DAGB1_DAGB_DLY` selects debug delay, client, and position fields. `DAGB1_CNTL_MISC` and `DAGB1_CNTL_MISC2` provide EA virtual-channel remaps, EA/UTCL2 request forcing, FAW mode, L1 probe toggles, and disable bits for write/read request/return and TLB clock gating. `DAGB1_FIFO_EMPTY`, `DAGB1_FIFO_FULL`, `DAGB1_WR_CREDITS_FULL`, and `DAGB1_RD_CREDITS_FULL` are full-width status masks.

`DAGB1_PERFCOUNTER_LO`, `DAGB1_PERFCOUNTER_HI`, `DAGB1_PERFCOUNTER0_CFG`, `DAGB1_PERFCOUNTER1_CFG`, `DAGB1_PERFCOUNTER2_CFG`, and `DAGB1_PERFCOUNTER_RSLT_CNTL` define low/high counter data, event selection, event mode, client ID selection, and performance-result controls. `DAGB1_RESERVE0` through `DAGB1_RESERVE17` are full-width reserved data fields and should not be treated as stable feature controls without hardware documentation.

### MMEA0 DRAM Arbitration And Priority Controls

The `addressBlock: mmhub_ea_mmeadec` section begins with DRAM arbitration maps. `MMEA0_DRAM_RD_CLI2GRP_MAP0/1` and `MMEA0_DRAM_WR_CLI2GRP_MAP0/1` map CIDs 0-31 into four two-bit arbitration groups for DRAM reads and writes. `MMEA0_DRAM_RD_GRP2VC_MAP` and `MMEA0_DRAM_WR_GRP2VC_MAP` map the four groups to virtual channels.

`MMEA0_DRAM_RD_LAZY` and `MMEA0_DRAM_WR_LAZY` define per-group lazy delays. `MMEA0_DRAM_RD_CAM_CNTL` and `MMEA0_DRAM_WR_CAM_CNTL` define per-group CAM depths and reorder limits. `MMEA0_DRAM_PAGE_BURST` defines read/write page-burst limits.

`MMEA0_DRAM_RD_PRI_AGE`, `MMEA0_DRAM_WR_PRI_AGE`, `MMEA0_DRAM_RD_PRI_QUEUING`, `MMEA0_DRAM_WR_PRI_QUEUING`, `MMEA0_DRAM_RD_PRI_FIXED`, `MMEA0_DRAM_WR_PRI_FIXED`, `MMEA0_DRAM_RD_PRI_URGENCY`, and `MMEA0_DRAM_WR_PRI_URGENCY` describe the four-group priority algorithm: aging rate, age coefficient, queuing coefficient, fixed coefficient, urgency coefficient, and urgency mode. `MMEA0_DRAM_*_PRI_QUANT_PRI[1-3]` adds per-group priority thresholds.

These DRAM priority and grouping registers influence fairness and latency among MMHUB clients. Incorrect values can bias page traffic, IO traffic, or GMI traffic and can show up as bandwidth collapse, high latency, or starvation rather than as an obvious compile failure.

### MMEA0 Address Normalization And DRAM Decode

`MMEA0_ADDRNORM_BASE_ADDR0/1`, `MMEA0_ADDRNORM_LIMIT_ADDR0/1`, `MMEA0_ADDRNORM_OFFSET_ADDR1`, and `MMEA0_ADDRNORM_HOLE_CNTL` define address-range validity, legacy MMIO hole handling, channel/socket/die interleave settings, base/limit addresses, high-address offset, destination fabric ID, and DRAM hole offset.

`MMEA0_ADDRDEC_BANK_CFG` and `MMEA0_ADDRDEC_MISC_CFG` describe DRAM/GMI bank masks, bank-group selection, bank-group interleave, VCM enables, PCH/channel/chip-select/rank-module masks, and the GMI variants of those masks. These fields are address-layout critical: they define how physical/fabric addresses are decoded to memory topology.

`MMEA0_ADDRDECDRAM_ADDR_HASH_BANK0` through `BANK4`, `MMEA0_ADDRDECDRAM_ADDR_HASH_PC`, `MMEA0_ADDRDECDRAM_ADDR_HASH_PC2`, and `MMEA0_ADDRDECDRAM_ADDR_HASH_CS0/1` define XOR-enable and XOR-source fields for bank, pseudo-channel, and chip-select hashing. `MMEA0_ADDRDECDRAM_HARVEST_ENABLE` adds forced bank-harvest enable/value bits for banks 3 and 4.

`MMEA0_ADDRDEC0_*` and `MMEA0_ADDRDEC1_*` define two parallel address-decode table instances. Each instance contains base addresses for `CS0` through `CS3` and `SECCS0` through `SECCS3`, mask registers for CS pairs and secondary CS pairs, address configuration for CS01/CS23, address-selection registers for bank and row bits, low and high column-selection registers, and rank-module selection registers for primary and secondary chip selects. The repeated fields encode memory geometry: number of bank groups, rank modules, row-low bits, row-high bits, columns, banks, bank bit positions, column bit positions, rank-module bits, channel bit, and row-MSB inversion policy.

### MMEA0 IO Arbitration And Priority Controls

`MMEA0_IO_RD_CLI2GRP_MAP0/1` and `MMEA0_IO_WR_CLI2GRP_MAP0/1` mirror the DRAM CID-to-group mapping pattern for IO read and write clients. `MMEA0_IO_RD_COMBINE_FLUSH` and `MMEA0_IO_WR_COMBINE_FLUSH` define per-group combine-flush timers, while `MMEA0_IO_GROUP_BURST` defines read/write burst low/high limits.

`MMEA0_IO_RD_PRI_AGE`, `MMEA0_IO_WR_PRI_AGE`, `MMEA0_IO_RD_PRI_QUEUING`, `MMEA0_IO_WR_PRI_QUEUING`, `MMEA0_IO_RD_PRI_FIXED`, `MMEA0_IO_WR_PRI_FIXED`, `MMEA0_IO_RD_PRI_URGENCY`, and `MMEA0_IO_WR_PRI_URGENCY` define the same four-group priority components for IO traffic. `MMEA0_IO_RD_PRI_URGENCY_MASK` contains full CID0-CID31 one-bit masks, and this chunk contains the beginning of `MMEA0_IO_WR_PRI_URGENCY_MASK` through CID21. The trailing CID22-CID31 masks are outside this chunk and must be reconciled by the merge lane.

## Control Flow And State Behavior

This header has no local runtime control flow. Including C translation units receive constants at compile time. Runtime effects occur when AMDGPU code passes register values through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_ENTRY`.

Most fields describe persistent hardware configuration state. Once programmed, DAGB client routing, credit limits, burst timers, lazy timers, clock-gating settings, MMEA group maps, priority coefficients, normalized address ranges, address hashing, and chip-select decode tables remain in MMHUB registers until changed by initialization, reset, suspend/resume restore, firmware, or hardware power-state transitions.

Several fields are observational state rather than configuration: pending masks, FIFO empty/full state, credit-full state, performance counter results, and performance counter high/low data. These fields are read to infer MMHUB activity, debug routing, or collect counters.

Some fields are command-like or latch-like in practice even though this header only defines bit positions. Examples include performance counter result control fields, clock-gating soft override bits, delay/debug selectors, and force/harvest controls. Consumers must preserve reserved bits where required by the hardware register contract, especially for read-modify-write sequences.

The header itself stores no state and performs no persistence. Persistence lives in MMHUB hardware registers, GPU reset/save-restore flows, and driver code that reprograms the MMHUB during init/resume/reset.

## Dependencies And Integration Points

This chunk depends on the generated AMD MMHUB register-header set:

- `mmhub_1_0_offset.h` supplies the matching `mmDAGB1_*` and `mmMMEA0_*` register addresses.
- `mmhub_1_0_default.h` supplies default register values where generated defaults exist.
- `mmhub_1_0_sh_mask.h` supplies the field masks and shifts described here.

Direct include sites for `mmhub/mmhub_1_0_sh_mask.h` in this source tree include:

- `drivers/gpu/drm/amd/amdgpu/mmhub_v1_0.c`
- `drivers/gpu/drm/amd/amdgpu/uvd_v7_0.c`
- `drivers/gpu/drm/amd/amdgpu/vce_v4_0.c`
- `drivers/gpu/drm/amd/display/dc/resource/dce120/dce120_resource.c`

`mmhub_v1_0.c` is the main integration point. It initializes MMHUB virtual memory apertures, page-table base registers, TLB/L2/cache behavior, protection-fault controls, invalidation ranges, and clock-gating behavior with SOC15 accessors. It uses nearby generated MMHUB field definitions through `REG_SET_FIELD`, `REG_GET_FIELD`, and direct masks. In the clock-gating path it reads and writes `mmDAGB1_CNTL_MISC2` and toggles `DAGB1_CNTL_MISC2__DISABLE_*_CG_MASK` bits, which are in the same `DAGB1` control family as this chunk's write/read client and clock-gating fields.

The MMEA0 address-decode and arbitration macros also sit near RAS and error-counter integration. `mmhub_v1_0.c` defines MMHUB EDC counter table entries using `SOC15_REG_ENTRY` and `SOC15_REG_FIELD` for `MMEA0_EDC_CNT*_VG20` fields outside this chunk. That makes the `MMEA0` namespace part of both memory-routing setup and reliability/error-reporting paths.

The UVD, VCE, and display include sites share the same MMHUB field vocabulary for media/display blocks that need to program or interpret MMHUB-related register fields on MMHUB 1.0 ASICs.

## Risks And Edge Cases

- Bitfield drift is high impact. A wrong mask or shift can silently program the wrong MMHUB bits, changing memory routing, virtual-channel assignment, priority arbitration, credit limits, or address decoding.
- Repeated register families are easy to copy incorrectly. `DAGB1_WRCLI0-15`, `DAGB1_WR_VC0-7_CNTL`, DRAM/IO `CLI2GRP_MAP0/1`, `ADDRDEC0/1`, and CS01/CS23/SECCS variants have regular layouts but are not interchangeable.
- Address-decode fields are memory-topology critical. Incorrect `ADDRNORM`, `ADDRDEC_BANK_CFG`, hashing, chip-select base/mask/config/select, column select, rank-module select, or harvest bits can lead to wrong physical memory targeting and data corruption.
- Arbitration fields can fail as performance bugs. Bad CID-to-group maps, group-to-VC maps, urgency masks, priority coefficients, lazy timers, combine flush timers, or burst limits may appear as latency spikes, starvation, or bandwidth collapse rather than immediate faults.
- Credit fields are deadlock-sensitive. Incorrect TLB, storage, EA, OSD, atomic, or burst credits can overcommit queues or stall clients permanently.
- Status and pending masks are full-width. Consumers should treat them as unsigned 32-bit values; sign extension from `0x80000000L`-style masks or host-width assumptions can corrupt diagnostics.
- Reserved fields and `DAGB1_RESERVE*` registers should not be reinterpreted as software feature flags. Generated names describe register layout, not necessarily safe writable behavior.
- The chunk boundary is mid-register. `MMEA0_IO_WR_PRI_URGENCY_MASK` is incomplete in this document's source range; whole-file research must merge the following chunk before presenting that register as complete.

## Test And Validation Signals

There are no direct unit tests for this macro-only chunk. Useful validation is integration-level and hardware-facing:

- Build AMDGPU, display, UVD, and VCE code that includes `mmhub_1_0_sh_mask.h`; this catches missing, renamed, or syntactically broken macros.
- Static mask/shift consistency checks can verify that contiguous masks shift down to dense fields, single-bit masks match their bit index, full-width masks use shift zero, and repeated register families keep consistent layouts.
- Exercise MMHUB 1.0 initialization, suspend/resume, GPU reset, SR-IOV paths, and clock-gating enable/disable flows in `mmhub_v1_0.c`, especially paths that read-modify-write DAGB clock-gating and VM/MMHUB registers.
- Run VM/GART and memory stress tests that cover system aperture, VRAM aperture, page-table setup, invalidations, protection faults, media/display clients, and concurrent read/write pressure through MMHUB.
- Validate bandwidth and latency under DRAM, GMI, and IO traffic mixes to catch arbitration misconfiguration in CID group maps, virtual-channel maps, priority coefficients, urgency masks, lazy timers, and burst limits.
- Compare register dumps against known-good firmware/ASIC programming for `DAGB1_*` and `MMEA0_*` registers after boot, resume, and reset.
- Exercise RAS/EDC and MMHUB diagnostic flows where available, confirming that MMEA/DAGB counters and status fields decode correctly and do not report impossible client or group states.

## Chunk Notes For Merge Lane

This is a partial range of a larger generated register header. The final per-file document should treat it as the MMHUB 1.0 `DAGB1` arbitration/control plus early `MMEA0` memory-address-decode/arbitration section. It should merge with adjacent chunks for the full `DAGB1_RD_*` setup before line 2368 and the remainder of `MMEA0_IO_WR_PRI_URGENCY_MASK` plus later MMEA0 registers after line 4742.
