# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_1_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002824`: lines 1-2337, `Docs/researches/chunks/subset-b-002824_research.md`
- `subset-b-002825`: lines 2338-4776, `Docs/researches/chunks/subset-b-002825_research.md`
- `subset-b-002826`: lines 4777-7155, `Docs/researches/chunks/subset-b-002826_research.md`
- `subset-b-002827`: lines 7156-9627, `Docs/researches/chunks/subset-b-002827_research.md`
- `subset-b-002828`: lines 9628-9790, `Docs/researches/chunks/subset-b-002828_research.md`

## Chunk Research

### subset-b-002824: lines 1-2337

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_1_sh_mask.h lines 1-2337

## Scope

This chunk is the opening portion of the generated AMDGPU MMHUB 9.1 shift/mask header. It contains C preprocessor definitions for the `mmhub_dagbdec` address block, not executable driver code. The file uses the standard generated AMD register-field convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the raw 32-bit mask for that field.

The covered range starts with the license and `_mmhub_9_1_SH_MASK_HEADER` include guard, then defines DAGB0 read-side and write-side arbitration, credit, virtual-channel, bandwidth, outstanding-request, burst, lazy-timer, clock-gating, and pending-status fields. The chunk ends at line 2337 inside `DAGB0_WR_VC7_CNTL`, after `DAGB0_WR_VC7_CNTL__OSD_LIMITER_ENABLE_MASK`; `DAGB0_WR_VC7_CNTL__MAX_OSD_MASK` is on line 2338 and belongs to the next chunk/reconciliation context.

## Purpose

The purpose of this header section is to let MMHUB 9.1 driver code compose and decode MMIO register values for the DAGB0 decoder/arbiter path without hard-coding bit numbers. These fields describe how read and write clients are mapped to virtual channels, how bandwidth and outstanding request limits are applied, how credit pools and burst timers are configured, and how clock-gating/light-sleep overrides are controlled for the MMHUB data/address gateway.

Although this repository path is under `distributed-fs/ceph-client`, the source file is AMD GPU driver hardware metadata. It is unrelated to Ceph filesystem behavior except by being part of the mirrored source tree.

## Important Macro Families

Read client controls:

- `DAGB0_RDCLI0` through `DAGB0_RDCLI31` repeat the same 10 fields for 32 read clients: `VIRT_CHAN`, `CHECK_TLB_CREDIT`, `URG_HIGH`, `URG_LOW`, `MAX_BW_ENABLE`, `MAX_BW`, `MIN_BW_ENABLE`, `MIN_BW`, `OSD_LIMITER_ENABLE`, and `MAX_OSD`.
- These fields map each read client to one of the DAGB virtual channels, tune urgency thresholds, optionally enforce min/max bandwidth, and optionally limit outstanding transactions.

Read global and per-channel controls:

- `DAGB0_RD_CNTL` defines global read-side knobs: `SCLK_FREQ`, client and virtual-channel bandwidth-window sizes, IO level override, compliant VC selection, and shared VC count.
- `DAGB0_RD_GMI_CNTL` defines read-side GMI credit, level, max-burst, and lazy-timer fields.
- `DAGB0_RD_ADDR_DAGB` controls read address-DAGB enable bits, jump-ahead behavior, self-initialization disablement, and `WHOAMI`.
- `DAGB0_RD_OUTPUT_DAGB_MAX_BURST` and `DAGB0_RD_OUTPUT_DAGB_LAZY_TIMER` pack per-VC fields for VC0-VC7.
- `DAGB0_RD_ADDR_DAGB_MAX_BURST0..3` and `DAGB0_RD_ADDR_DAGB_LAZY_TIMER0..3` pack per-client values for clients 0-31 in groups of eight.
- `DAGB0_RD_VC0_CNTL` through `DAGB0_RD_VC7_CNTL` repeat per-virtual-channel storage credit, EA credit, max/min bandwidth, and max outstanding request fields.
- `DAGB0_RD_CNTL_MISC` defines storage pool credit, EA pool credit, IO EA credit, legacy coherency mode bits, and `UTCL2_CID`.
- `DAGB0_RD_TLB_CREDIT` defines normal and atomic TLB credit fields.

Read status/pending indicators:

- `DAGB0_RDCLI_ASK_PENDING`, `DAGB0_RDCLI_GO_PENDING`, `DAGB0_RDCLI_GBLSEND_PENDING`, `DAGB0_RDCLI_TLB_PENDING`, `DAGB0_RDCLI_OARB_PENDING`, and `DAGB0_RDCLI_OSD_PENDING` each expose a 32-bit `ID` mask for per-client pending state.

Write client controls:

- `DAGB0_WRCLI0` through `DAGB0_WRCLI31` mirror the read-client layout for write clients, with the same virtual channel, TLB credit check, urgency, min/max bandwidth, and outstanding request limiter fields.
- `DAGB0_WR_CNTL`, `DAGB0_WR_GMI_CNTL`, `DAGB0_WR_ADDR_DAGB`, `DAGB0_WR_OUTPUT_DAGB_MAX_BURST`, and `DAGB0_WR_OUTPUT_DAGB_LAZY_TIMER` mirror the global read-side register shapes for write-side address/data flow.
- `DAGB0_WR_ADDR_DAGB_MAX_BURST0..3` and `DAGB0_WR_ADDR_DAGB_LAZY_TIMER0..3` define per-client address-DAGB burst and lazy-timer tuning for clients 0-31.
- `DAGB0_WR_DATA_DAGB`, `DAGB0_WR_DATA_DAGB_MAX_BURST0..3`, and `DAGB0_WR_DATA_DAGB_LAZY_TIMER0..3` define equivalent write data-DAGB enable, identity, burst, and lazy-timer fields.
- `DAGB0_WR_VC0_CNTL` through the partial `DAGB0_WR_VC7_CNTL` define per-virtual-channel write-side storage/EA credits and bandwidth/outstanding limits. The final `MAX_OSD_MASK` for VC7 is just outside this exact line range.

Clock-gating and light-sleep controls:

- `DAGB0_RD_CGTT_CLK_CTRL`, `DAGB0_L1TLB_RD_CGTT_CLK_CTRL`, and `DAGB0_ATCVM_RD_CGTT_CLK_CTRL` define read-side `ON_DELAY`, `OFF_HYSTERESIS`, `SOFT_STALL_OVERRIDE`, and light-sleep override bits for write/read/return/register paths.
- `DAGB0_WR_CGTT_CLK_CTRL`, `DAGB0_L1TLB_WR_CGTT_CLK_CTRL`, and `DAGB0_ATCVM_WR_CGTT_CLK_CTRL` define the matching write-side clock-gating controls.

## Control Flow and Data Flow

This header has no runtime control flow. It participates in compile-time preprocessing only.

The implied consumer flow is:

1. Include the matching `mmhub_9_1_offset.h` register-address header and this `mmhub_9_1_sh_mask.h` field-layout header.
2. Select an MMHUB register such as `mmDAGB0_RDCLI0`, `mmDAGB0_RD_CNTL`, `mmDAGB0_WRCLI0`, or `mmDAGB0_WR_VC0_CNTL` from the offset header.
3. Use AMDGPU/SOC15 helper macros such as register read/write helpers and field set/get helpers to compose or decode 32-bit MMIO values using these `__SHIFT` and `_MASK` constants.
4. Let the caller enforce ordering, idleness, reset, firmware, and power-management sequencing. Those semantics are not represented in this generated header.

The data flow represented by the bitfields is hardware configuration state: per-client requests enter DAGB0, are assigned to virtual channels, consume TLB/storage/EA credits, are throttled by bandwidth and outstanding-request fields, and are shaped by burst and lazy-timer fields before leaving the MMHUB gateway. Pending-state registers provide status visibility for read clients, while clock-gating registers influence when parts of the path can stall, gate, or enter light sleep.

## State and Persistence Behavior

The macros persist no software state. They name bit positions for hardware MMIO registers whose state lives in the GPU.

Configuration-like state includes client-to-VC mappings, urgency thresholds, bandwidth windows, min/max bandwidth limits, outstanding request limits, storage and EA credits, TLB credits, GMI credit/level/burst/timer values, per-client burst and lazy-timer fields, `DAGB_ENABLE`, jump-ahead behavior, self-initialization disablement, `WHOAMI`, and clock-gating/light-sleep override values.

Volatile or observational state includes the read-client pending ID masks for ask, go, global-send, TLB, output arbiter, and outstanding-status domains. These status fields are hardware-produced and may change as requests drain or stall.

Action-like fields are mostly configuration actions rather than one-shot commands. Misprogramming enable bits, credit values, burst timers, or clock-gating overrides can alter live memory-traffic behavior immediately. The header does not encode reset defaults, reserved-bit policy, read-only/write-only access type, latch behavior, or safe update sequencing.

## Dependencies and Integration Points

Key dependencies:

- `mmhub_9_1_offset.h` supplies the matching MMIO offsets and base-index constants for these register names. For this chunk, the companion offset header maps registers such as `mmDAGB0_RDCLI0`, `mmDAGB0_RD_CNTL`, `mmDAGB0_WRCLI0`, and `mmDAGB0_WR_VC7_CNTL` to concrete MMHUB addresses.
- AMDGPU generated-register helper conventions depend on the exact suffixes `__SHIFT` and `_MASK`.
- Consumer code must include the SOC15 register helper stack that knows how to address MMHUB registers for the selected ASIC instance.
- Adjacent chunks are required for the complete MMHUB 9.1 field map; this chunk is only the first 2,337 lines of a 9,790-line header.

Observed integration points in this tree:

- `drivers/gpu/drm/amd/amdgpu/vcn_v1_0.c` includes `mmhub/mmhub_9_1_offset.h` and `mmhub/mmhub_9_1_sh_mask.h` alongside VCN 1.0 register headers, making MMHUB 9.1 fields available during VCN setup and control paths.
- `drivers/gpu/drm/amd/display/dc/resource/dcn10/dcn10_resource.c` includes the same MMHUB 9.1 offset and shift/mask headers in DCN 1.0 display resource code.
- Other MMHUB generation headers in the same directory follow the same register naming and repeated-field pattern, so cross-generation code and audits often compare these generated layouts against neighboring ASIC versions.

Primary hardware integration surfaces:

- MMHUB request arbitration and traffic shaping for read and write clients.
- Virtual-channel configuration across VC0-VC7.
- TLB/storage/EA credit accounting and throttling.
- GMI burst/timer behavior.
- Clock gating and light-sleep behavior for DAGB, L1 TLB, and ATCVM read/write paths.
- Read client pending diagnostics for hang or stall analysis.

## Risks and Edge Cases

- The largest risk is a mismatch between this shift/mask header and `mmhub_9_1_offset.h` or the ASIC register specification. The code can still compile while programming the wrong bits.
- This file is generated hardware metadata. Manual edits are high-risk because repeated families look nearly identical but map distinct clients, VCs, and offsets.
- Repeated client registers invite off-by-one mistakes. `RDCLI0..31` and `WRCLI0..31` share layouts but represent separate hardware clients.
- Packed per-client registers group clients 0-31 into groups of eight. Wrong group selection can silently tune a different client.
- Packed per-VC registers use 4-bit lanes for VC0-VC7. A wrong shift can affect an adjacent virtual channel.
- Bandwidth, credit, and outstanding-limit fields influence live memory-system behavior. Bad values can starve a client, overrun credits, reduce throughput, or contribute to GPU hangs.
- `CHECK_TLB_CREDIT` and TLB credit fields are tied to translation flow control. Incorrect values can interact badly with MMHUB VM/TLB invalidation and page-table traffic even though the VM registers are outside this chunk.
- Clock-gating fields may require idle or reset sequencing that is not visible in the header. Read-modify-write callers should preserve unrelated and reserved bits unless an ASIC-specific sequence intentionally writes a full default.
- Pending ID masks are status surfaces, not configuration knobs. Treating them as normal writable registers would be a consumer-code bug unless the hardware specification says otherwise.
- The exact requested chunk ends one line before the final mask for `DAGB0_WR_VC7_CNTL`. Whole-file reconciliation must not conclude that VC7 lacks `MAX_OSD_MASK`; it is present at line 2338, just outside this work item.

## Test and Verification Signals

Useful verification is mostly build, generated-header audit, and hardware integration coverage:

- Compile paths that include `mmhub_9_1_offset.h` and `mmhub_9_1_sh_mask.h`, including the VCN 1.0 and DCN 1.0 resource files observed in this tree.
- Static generated-header checks that each field has aligned `__SHIFT` and `_MASK` definitions, masks match the expected bit width, and repeated `RDCLI`, `WRCLI`, `RD_VC`, and `WR_VC` families are complete.
- Cross-check against `mmhub_9_1_offset.h` that every register family in this chunk has a companion `mm...` offset and base index.
- Cross-generation diff/audit against nearby MMHUB generated headers to catch unexpected layout drift for shared DAGB0 fields.
- Register readback after MMHUB initialization to confirm client VC mappings, bandwidth windows, credit fields, burst timers, and clock-gating controls decode as expected.
- GPU memory traffic stress tests covering read/write-heavy workloads, mixed display/video/compute traffic, VM pressure, and suspend/resume or reset recovery.
- Hang/stall diagnostics that compare `DAGB0_RDCLI_*_PENDING` status masks against expected in-flight clients when traffic is blocked or drained.
- Power-management tests that toggle clock gating/light sleep and verify that the DAGB, L1TLB, and ATCVM paths wake correctly without request loss or deadlock.

## Cross-Chunk Notes

This is the first chunk of the file and includes the license, include guard, and the start of `addressBlock: mmhub_dagbdec`. It covers complete read-side DAGB0 client/global/VC/status definitions and most write-side DAGB0 client/global/address/data/VC definitions through line 2337. The next chunk begins immediately after this range and should reconcile the final `DAGB0_WR_VC7_CNTL__MAX_OSD_MASK` line plus subsequent write-side miscellaneous, credit, pending, and later MMHUB field definitions.

### subset-b-002825: lines 2338-4776

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_1_sh_mask.h lines 2338-4776

## Scope

This chunk covers a generated AMD MMHUB 9.1 register shift/mask header section. It starts at the final mask field for `DAGB0_WR_VC7_CNTL`, continues through the rest of the `mmhub_dagbdec` `DAGB0` write/control/performance/reserved fields, then enters `addressBlock: mmhub_ea_mmeadec` for `MMEA0` memory-address/arbiter/error-management fields. The range ends in the first `MMEA1_DRAM_RD_CLI2GRP_MAP0` definitions, so most `MMEA1` fields are in later chunks.

The file is data-only C preprocessor material. It defines no functions, structs, variables, locks, allocations, or direct MMIO operations. Its public interface is the generated pair convention:

- `<REGISTER>__<FIELD>__SHIFT` for bit offsets.
- `<REGISTER>__<FIELD>_MASK` for 32-bit field masks.

## Purpose

This header is the bitfield side of the MMHUB 9.1 register ABI used by AMDGPU and display code. The companion `mmhub_9_1_offset.h` header provides register addresses such as `mmDAGB0_WR_CNTL_MISC`, `mmDAGB0_CNTL_MISC2`, `mmMMEA0_DRAM_RD_CLI2GRP_MAP0`, `mmMMEA0_ADDRNORM_BASE_ADDR0`, `mmMMEA0_EDC_CNT`, and `mmMMEA1_DRAM_RD_CLI2GRP_MAP0`; this file provides the field layout for those registers.

Consumers normally compose and decode values through AMDGPU register helpers and generated macros, including `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `SOC15_REG_ENTRY`, `SOC15_REG_OFFSET`, and MMIO helpers such as `RREG32_SOC15`/`WREG32_SOC15`. Direct users of this exact MMHUB 9.1 header in this source tree include `amdgpu/vcn_v1_0.c` and `display/dc/resource/dcn10/dcn10_resource.c`, while later MMHUB versions show the same macro families used for clock gating, RAS/EDC counters, and error status handling.

## Important Macro Families

### DAGB0 Write Path, Credits, Pending State, and Performance Counters

The first part finishes the DAGB0 block:

- `DAGB0_WR_CNTL_MISC` defines storage/EA/IO credit pool sizing, legacy credit-control mode bits, and `UTCL2_CID`.
- `DAGB0_WR_TLB_CREDIT`, `DAGB0_WR_DATA_CREDIT`, and `DAGB0_WR_MISC_CREDIT` describe TLB, burst-size, atomic, OSD, and deadlock-virtual-channel credit fields.
- `DAGB0_WRCLI_*_PENDING` exposes full-width `BUSY` bitmaps for ask/go/global-send/TLB/OARB/OSD/DBUS pending write-client state.
- `DAGB0_DAGB_DLY` provides delay/client/position fields, likely for internal debug or timing adjustment.
- `DAGB0_CNTL_MISC` maps EA virtual channels 0-7 and bandwidth cycle gap/init controls.
- `DAGB0_CNTL_MISC2` exposes urgent boost/halt, write/read/TLB clock-gating disable bits, EA request busy-disable bits, and swap control.
- `DAGB0_FIFO_EMPTY`, `DAGB0_FIFO_FULL`, `DAGB0_WR_CREDITS_FULL`, and `DAGB0_RD_CREDITS_FULL` are packed status masks for queue and credit saturation/empty state.
- `DAGB0_PERFCOUNTER_LO/HI`, `DAGB0_PERFCOUNTER0_CFG`, `DAGB0_PERFCOUNTER1_CFG`, `DAGB0_PERFCOUNTER2_CFG`, and `DAGB0_PERFCOUNTER_RSLT_CNTL` define 48-bit-ish counter readout, compare value, event selection ranges, modes, enable/clear bits, trigger fields, and all-counter control.

`DAGB0_RESERVE0` through `DAGB0_RESERVE101` are generated placeholders with full-width reserve masks. They preserve the register map shape but should not be treated as documented software configuration.

### MMEA0 Client Grouping and Virtual Channel Mapping

The `MMEA0_DRAM_*_CLI2GRP_MAP0/1` and `MMEA0_IO_*_CLI2GRP_MAP0/1` families map client IDs `CID0` through `CID31` to two-bit arbitration groups for DRAM reads, DRAM writes, IO reads, and IO writes. Matching `MMEA0_DRAM_RD_GRP2VC_MAP` and `MMEA0_DRAM_WR_GRP2VC_MAP` translate four arbitration groups into three-bit virtual-channel IDs.

These masks are central to routing and prioritizing memory traffic. An incorrect group map can change quality of service between clients or place traffic on a wrong virtual channel.

### MMEA0 DRAM Arbitration, Priority, and Burst Controls

The DRAM scheduling portion defines:

- Lazy timers via `MMEA0_DRAM_RD_LAZY` and `MMEA0_DRAM_WR_LAZY`.
- CAM depth and reorder limits via `MMEA0_DRAM_RD_CAM_CNTL` and `MMEA0_DRAM_WR_CAM_CNTL`.
- Page/burst limits through `MMEA0_DRAM_PAGE_BURST`.
- Aging, queuing, fixed priority, urgency, and quantized priority thresholds through `MMEA0_DRAM_RD_PRI_*` and `MMEA0_DRAM_WR_PRI_*`.

The IO side mirrors much of this policy with `MMEA0_IO_RD_COMBINE_FLUSH`, `MMEA0_IO_WR_COMBINE_FLUSH`, `MMEA0_IO_GROUP_BURST`, `MMEA0_IO_RD_PRI_*`, `MMEA0_IO_WR_PRI_*`, per-CID urgency masks, and three priority-threshold registers for read and write.

### Address Normalization and DRAM Address Decode

`MMEA0_ADDRNORM_*` fields define normalized base/limit windows, offset for a second address range, and a hole control flag. The DRAM decode section then provides:

- `MMEA0_ADDRDEC_BANK_CFG` and `MMEA0_ADDRDEC_MISC_CFG` for channel/bank/row/column decode parameters, interleave policy, channel offset, local routing, GMI-aware mode, and channel-disable state.
- `MMEA0_ADDRDECDRAM_ADDR_HASH_BANK0..4`, `PC`, `PC2`, and `CS0/CS1` for XOR-based bank, pseudo-channel, and chip-select hashing.
- `MMEA0_ADDRDECDRAM_HARVEST_ENABLE` for forcing bank-harvest bits.
- Two address-decode instances, `ADDRDEC0` and `ADDRDEC1`, each with base registers for CS0-CS3 and secondary chip-selects, address masks, address configuration, bank/row selectors, column low/high selectors, row-mask selectors, channel-bit selectors, and row-MSB inversion controls.

These fields describe persistent hardware address translation and memory topology state. They must match actual VRAM topology, interleave, harvested resources, and chip-select layout.

### SDP Arbitration, Credits, Tags, and Request Control

`MMEA0_SDP_ARB_DRAM`, `MMEA0_SDP_ARB_FINAL`, `MMEA0_SDP_DRAM_PRIORITY`, and `MMEA0_SDP_IO_PRIORITY` define burst limits, arbitration wait/expire behavior, priority switch/hold thresholds, and per-group priority thresholds. `MMEA0_SDP_CREDITS`, `MMEA0_SDP_TAG_RESERVE0/1`, `MMEA0_SDP_VCC_RESERVE0/1`, and `MMEA0_SDP_VCD_RESERVE0/1` define credit and reserved tag/virtual-channel resource partitions for DRAM, IO, GMI, and return paths. `MMEA0_SDP_REQ_CNTL` provides split/combine disable knobs for read and write request behavior.

### Miscellaneous Control, Latency Sampling, Performance, and Error Handling

The later `MMEA0` fields include:

- `MMEA0_MISC`, a broad control register for SDP request gating, credit deadlock/reorder behavior, page-start constants, write-CAM merge mode, EA response force, IO-to-GMI and GMI-to-dram behavior, priority disable, and FA failure control.
- `MMEA0_LATENCY_SAMPLING`, with request tag/counter controls and read/write/VMGPR/interrupt/return-path enables for latency measurement.
- `MMEA0_PERFCOUNTER_LO/HI`, `MMEA0_PERFCOUNTER0_CFG`, `MMEA0_PERFCOUNTER1_CFG`, and `MMEA0_PERFCOUNTER_RSLT_CNTL`, which mirror the event-select/mode/enable/clear/trigger pattern used by DAGB0.
- `MMEA0_EDC_CNT` and `MMEA0_EDC_CNT2`, exposing SEC/DED or SED/DED count fields for DRAM read/write command/data memories, read/write return tag memories, IO read/write command/data memories, and GMI read/write command/data/page memories.
- `MMEA0_DSM_CNTL` and `MMEA0_DSM_CNTLA`, with DSM irritator data and single-write enables for command/data/page memories.
- `MMEA0_DSM_CNTL2` and `MMEA0_DSM_CNTL2A`, with error-injection enable, injection-delay select, and global `INJECT_DELAY` fields for the same memory groups.
- `MMEA0_CGTT_CLK_CTRL`, exposing clock-gating timing, low-power override, soft-stall override, and soft override controls for write/read/return/register domains.
- `MMEA0_EDC_MODE`, controlling FED/FUE/DED propagation, counting, gating, and bypass behavior.
- `MMEA0_ERR_STATUS`, exposing SDP read/write response status, read-response data parity error, clear-error, and busy-on-error bits.
- `MMEA0_MISC2`, with chip-select-group swap flags and DRAM/GMI burst-limit data fields.

The chunk ends at `MMEA1_DRAM_RD_CLI2GRP_MAP0`, covering only the first `CID0` through `CID9` group fields before the remaining `MMEA1` map continues in the next chunk.

## Control Flow and State Behavior

There is no executable control flow in this header. Its effect is compile-time: it lets C code produce the exact MMIO bit patterns expected by MMHUB 9.1 hardware.

The state represented by this chunk is persistent hardware register state. Important examples include DAGB0 credit and clock-gating configuration, pending/busy and FIFO/credit-full status, performance-counter selection and results, MMEA0 client-to-group and group-to-VC routing, DRAM/IO arbitration policy, normalized address windows, DRAM address-decode topology, SDP credits/tag reservations, latency-sampling setup, EDC counters and modes, DSM/error-injection knobs, and error-status latches.

Several fields are status or command-like rather than normal durable configuration. Examples include pending `BUSY` bitmaps, FIFO/full indicators, performance-counter `CLEAR` and result-control `CLEAR_ALL`, latency sampling control bits, error-status clear, DSM error-injection controls, and clock-gating overrides. Correct users need the ordering, polling, and timeout rules from the owning AMDGPU code and hardware specification; the macros alone do not express those rules.

## Dependencies and Integration Points

This chunk depends on the generated MMHUB header set:

- `mmhub_9_1_offset.h` supplies matching register addresses and base indices.
- Other ASIC-generation MMHUB headers define similar but not interchangeable fields for later hardware.
- `soc15.h` and related AMDGPU helpers consume the `__SHIFT`/`_MASK` convention through field composition and extraction macros.

Observed integration in this source tree:

- `amdgpu/vcn_v1_0.c` includes `mmhub_9_1_offset.h` and `mmhub_9_1_sh_mask.h` while setting up VCN 1.0 rings on the MMHUB VM hub.
- `display/dc/resource/dcn10/dcn10_resource.c` includes the MMHUB 9.1 headers and defines `MMHUB_SR()` register-list expansion helpers, so display resource tables can refer to MMHUB registers by generated names.
- Later MMHUB code such as `amdgpu/mmhub_v9_4.c` shows the same families in active use: `DAGB0_CNTL_MISC2` bits are used to gate or ungate DAGB clock-gating domains, `MMEA0_EDC_CNT*` fields feed RAS/EDC error counters, and `MMEA0_ERR_STATUS` fields are decoded with `REG_GET_FIELD`.
- `amdgpu/mmhub_v1_8.c` uses MMEA error-status register ranges in RAS tables, reinforcing that MMEA EDC/error status registers are part of MMHUB reliability reporting across generations.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can write unrelated MMHUB hardware fields, causing GPU hangs, bad memory routing, incorrect QoS, broken decode topology, or misleading RAS/performance data.
- The repeated client-map fields are easy to damage mechanically. DRAM read, DRAM write, IO read, and IO write maps all pack 32 CIDs into similar two-register layouts; swapping a family or changing one field width would silently alter arbitration policy.
- Address-decode fields are topology-sensitive. Base/mask/config/select/hash/harvest errors can route physical addresses to the wrong DRAM channel, row, column, bank, pseudo-channel, or chip select.
- Reserved DAGB registers are generated placeholders. Software should not rely on them as supported control surfaces unless hardware documentation and owning driver code explicitly do so.
- Clock-gating and soft-override bits can hide power-management defects or create hangs if left asserted across reset, suspend/resume, or power-gating transitions.
- EDC/DSM/error-injection fields are reliability-sensitive. Incorrect error-injection, EDC bypass, clear-status, or busy-on-error handling can mask real memory faults or create false RAS events.
- Performance and latency-sampling controls can perturb timing and are not substitutes for normal runtime policy. Counter clear/enable/trigger sequencing must be consistent with the profiling path.
- The chunk boundary is mid-family for `MMEA1_DRAM_RD_CLI2GRP_MAP0`; the merge lane must combine this with the next chunk before making source-file-level claims about the MMEA1 block.

## Test and Validation Signals

Useful validation is mostly integration and hardware bring-up coverage:

- Build AMDGPU and display code paths that include `mmhub/mmhub_9_1_sh_mask.h`; this catches renamed or missing generated macros.
- VCN 1.0 initialization and ring tests should continue to bind decode/encode rings to the MMHUB VM hub without register-list regressions.
- DCN 1.0 display resource initialization should compile and populate MMHUB register addresses/masks through the generated register-list macros.
- MMHUB clock-gating tests, using comparable later-generation paths, should verify `DAGB0_CNTL_MISC2` style enable/disable bits preserve idle and resume behavior.
- RAS/EDC tests should read and decode `MMEA0_EDC_CNT*` and `MMEA0_ERR_STATUS` fields, verify clear behavior, and confirm SEC/DED/SED reporting matches injected or observed hardware events.
- Memory bring-up and stress tests should exercise address normalization, address decode, hashing, chip-select selection, channel-disable/harvest settings, and DRAM/IO arbitration under heavy traffic.
- Performance-counter and latency-sampling validation should verify event selection, clear/enable, trigger handling, and counter readout for DAGB0 and MMEA0 paths.

## Unresolved Cross-Chunk References

Line 2338 is the tail of `DAGB0_WR_VC7_CNTL`; the preceding shift fields and register comment belong to an earlier chunk. The last covered lines start `MMEA1_DRAM_RD_CLI2GRP_MAP0` but do not complete that register's CID list or any later `MMEA1` families. The final per-file reconciliation should stitch both boundaries to avoid treating partial register families as complete.

### subset-b-002826: lines 4777-7155

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_1_sh_mask.h lines 4777-7155

## Scope And Purpose

This chunk is a generated AMDGPU MMHUB 9.1 register shift/mask header segment. It defines preprocessor constants for bitfield extraction and composition in MMHUB memory-arbiter, address-normalization/address-decode, power-control, L1 TLB status/performance, and the first L2 SAW control registers. The public interface is a dense set of `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros. There are no functions, structs, enums, local variables, or executable branches in this range.

The chunk starts mid-way through `MMEA1_DRAM_RD_CLI2GRP_MAP0`, covering masks for client IDs 10-15 after the previous chunk's shifts and earlier masks. It then covers the rest of the `MMEA1` DRAM and IO arbitration/programming block, the MMHUB power-control block `mmhub_pctldec`, L1 TLB status and performance-counter blocks, and ends immediately after the field definitions for `VM_L2_SAW_CNTL2`; the next register comment, `VM_L2_SAW_CNTL3`, appears at the chunk boundary.

This file is paired with `mmhub_9_1_offset.h`. The offset header supplies the register addresses and base indices, while this `_sh_mask.h` header supplies each register's field layout for AMDGPU register helpers and direct mask operations.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The interface is macro-only and is consumed by register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_ENTRY`, and golden-register initialization macros.

Important macro families in this chunk include:

- `MMEA1_DRAM_RD_CLI2GRP_MAP0/1` and `MMEA1_DRAM_WR_CLI2GRP_MAP0/1`: two-bit client-ID-to-group mappings for DRAM read/write clients. Each 32-bit register packs 16 client IDs, with `MAP0` covering CID0-CID15 and `MAP1` covering CID16-CID31. This chunk includes the tail of read `MAP0`, full read `MAP1`, and full write maps.
- `MMEA1_DRAM_RD_GRP2VC_MAP` and `MMEA1_DRAM_WR_GRP2VC_MAP`: three-bit mappings from four arbitration groups to virtual channels for DRAM read/write traffic.
- `MMEA1_DRAM_RD_LAZY`, `MMEA1_DRAM_WR_LAZY`, `MMEA1_DRAM_RD_CAM_CNTL`, `MMEA1_DRAM_WR_CAM_CNTL`, and `MMEA1_DRAM_PAGE_BURST`: queue delay, CAM depth, reorder limit, and page-burst controls for DRAM-side arbitration. These fields affect how grouped memory requests are buffered and issued.
- `MMEA1_DRAM_RD_PRI_*` and `MMEA1_DRAM_WR_PRI_*`: age, queuing, fixed-priority, urgency, and priority quantum fields. These macros define the programmable scheduling policy for low, medium, and high priority DRAM traffic and for priority levels 1-3.
- `MMEA1_ADDRNORM_*`: address normalization base, limit, offset, and hole-control fields. These define normalized address ranges and optional hole behavior before address decode.
- `MMEA1_ADDRDEC_*` and `MMEA1_ADDRDECDRAM_*`: DRAM address-decoder bank/rank/stack/pipe/column/row/chip-select mapping fields. They include bank configuration, misc channel settings, hash enable/selection fields, harvest enable, per-decoder chip-select base addresses, masks, address selection, column selection, and row-mask selection for primary and secondary chip selects.
- `MMEA1_IO_RD_*` and `MMEA1_IO_WR_*`: IO client-to-group maps, combine flush controls, group burst limits, age/queuing/fixed/urgency priority controls, urgency masks, and priority quanta. These mirror the DRAM arbitration controls for IO-side traffic.
- `MMEA1_SDP_*`: SDP arbitration, priority, credit, tag reserve, virtual-credit reserve, and request-control fields. These control arbitration between DRAM/IO paths, reserve resources, and limit or block requests through SDP.
- `MMEA1_MISC`, `MMEA1_LATENCY_SAMPLING`, `MMEA1_PERFCOUNTER_LO/HI`, `MMEA1_PERFCOUNTER0_CFG`, `MMEA1_PERFCOUNTER1_CFG`, and `MMEA1_PERFCOUNTER_RSLT_CNTL`: miscellaneous behavior, latency sampling, and two performance-counter configuration/result fields for the MMEA1 block.
- `MMEA1_EDC_CNT`, `MMEA1_EDC_CNT2`, `MMEA1_DSM_CNTL*`, `MMEA1_CGTT_CLK_CTRL`, `MMEA1_EDC_MODE`, `MMEA1_ERR_STATUS`, and `MMEA1_MISC2`: error-detection counter fields, deterministic/stress-mode or injection selection fields, clock-gating timing/override fields, EDC behavior fields, SDP response error status, and CSGROUP swap/burst-limit controls.
- `PCTL_MISC`, `PCTL_MMHUB_DEEPSLEEP`, `PCTL_MMHUB_DEEPSLEEP_OVERRIDE`, `PCTL_PG_IGNORE_DEEPSLEEP`, and `PCTL_PG_DAGB`: global MMHUB power-control, deep-sleep, override, ignore, and DAGB power-gating field layouts.
- `PCTL0_*`, `PCTL1_*`, and `PCTL2_*`: three repeated power-control instances with RENG RAM index/data/execute fields, misc lock/idle/deepsleep controls, and register-save range/exclusion fields for state-controller save/restore behavior.
- `MC_VM_MX_L1_TLB0_STATUS` through `MC_VM_MX_L1_TLB7_STATUS`: status bits for eight L1 TLB instances, exposing `BUSY` and `FOUND_PARITY_ERRORS`.
- `MC_VM_MX_L1_PERFCOUNTER0_CFG` through `MC_VM_MX_L1_PERFCOUNTER3_CFG`, `MC_VM_MX_L1_PERFCOUNTER_RSLT_CNTL`, `MC_VM_MX_L1_PERFCOUNTER_LO`, and `MC_VM_MX_L1_PERFCOUNTER_HI`: L1 TLB performance-counter event selection, range end, mode, enable/clear controls, global result selection/triggers, 32-bit low counter value, and high counter/compare fields.
- `VM_L2_SAW_CNTL` and `VM_L2_SAW_CNTL2`: early L2 SAW translation-cache control fields, including L2 cache enablement, fragment processing, PTE/PDE endian swap modes, tag generation, LRU update on write, default-page routing, PDE cache split/effective sizes, identity access, swap-tag-index selection, L1/L2 invalidation controls, per-domain invalidation disable, BigK cache optimization/VMID mode, invalidate mode, and PDE cache effective size.

## Control Flow And State Behavior

This header has no runtime control flow. It is a compile-time register ABI for composing and decoding 32-bit MMIO register values. Runtime behavior happens only in code that includes this header and applies the masks/shifts while reading or writing MMHUB registers.

The `MMEA1` register fields describe persistent hardware configuration for MMHUB memory-client arbitration, address normalization, DRAM chip-select decode, IO arbitration, SDP credits/reserves, clock gating, error reporting, diagnostic/stress mode, and performance counting. Driver writes to these fields remain in the MMHUB register file until reset, power-gating restore, firmware or SMU programming, golden-register initialization, or later driver writes.

The `PCTL*` fields are tied to power management and register save/restore. The `RENG_RAM_*` fields select and write/read RENG microcode or RAM data, `RENG_EXECUTE` triggers execution with error/status bits, `*_MISC` controls register locks, idle thresholds, memory light-sleep enablement, forced power-gating state-controller completion, and deep-sleep behavior, and the `STCTRL_REGISTER_SAVE_*` fields define save ranges and exclusions. These are stateful power-management surfaces and may be sensitive to write ordering and power-state transitions.

The L1 TLB status registers are hardware-owned status. `BUSY` indicates active work in each TLB instance, while `FOUND_PARITY_ERRORS` exposes parity-detection state. The L1 performance-counter registers are mutable counter state controlled by event selection, mode, enable, clear, start/stop triggers, and stop-on-saturate fields.

The `VM_L2_SAW_CNTL*` fields configure translation-cache behavior and invalidation semantics. L2 cache enablement, fragment processing, PDE/PTE swap modes, default-page handling, identity mode, cache sizing, and invalidation bits directly affect MMHUB address translation and fault behavior. The header does not encode access type, reset value, sequencing, volatile status behavior, or whether fields are read-only, sticky, or write-one-to-clear.

## Dependencies And Integration Points

The immediate companion file is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_1_offset.h`. Matching offsets in that header include `mmMMEA1_DRAM_RD_CLI2GRP_MAP0` at `0x0240`, the MMEA1 arbitration/address-decode/SDP/EDC range through `mmMMEA1_MISC2` at `0x034d`, `mmPCTL_MISC` through `mmPCTL2_STCTRL_REGISTER_SAVE_EXCL_SET1` at `0x0380`-`0x039f`, `mmMC_VM_MX_L1_TLB0_STATUS` through `mmMC_VM_MX_L1_PERFCOUNTER_HI` at `0x0588`-`0x059d`, `mmVM_L2_SAW_CNTL` and `mmVM_L2_SAW_CNTL2` at `0x0600`-`0x0601`, and `mmMC_VM_MX_L1_TLB_CNTL` later at `0x0833`.

The most direct AMDGPU integration points are MMHUB v1.7/v1.8 and GMC v9 code paths:

- `amdgpu/mmhub_v1_7.c` includes the MMHUB v1.7 shift/mask variant, which is the related generation-specific consumer for many same-named field contracts. It programs `MC_VM_MX_L1_TLB_CNTL` with `REG_SET_FIELD`, manages MMHUB cache/TLB state, and uses `SOC15_REG_FIELD` for MMEA1 RAS counter reporting.
- `amdgpu/mmhub_v1_8.c` similarly uses `MC_VM_MX_L1_TLB_CNTL` field macros and MMEA1 RAS register entries.
- `amdgpu/mmhub_v9_4.c` uses `mmMMEA1_EDC_CNT`, `mmMMEA1_EDC_CNT2`, `mmMMEA1_ERR_STATUS`, and `SOC15_REG_FIELD(MMEA1_*, ...)` for RAS reporting in a newer MMHUB family with similar MMEA1 error-counter naming.
- `amdgpu/gmc_v9_0.c` contains a golden-register programming entry for `mmMMEA1_DRAM_WR_CLI2GRP_MAP0`, tying the MMEA1 DRAM client-to-group map to GPU initialization defaults.

The macros depend on AMDGPU register-helper naming conventions. `REG_SET_FIELD(value, REG, FIELD, field_value)` and `REG_GET_FIELD(value, REG, FIELD)` require both `REG__FIELD_MASK` and `REG__FIELD__SHIFT` to exist and to describe a contiguous field. `SOC15_REG_FIELD(REG, FIELD)` uses the same macro names for RAS/error metadata. Direct MMIO writes use the matching offset macro from `mmhub_9_1_offset.h`.

## Risks And Edge Cases

- This header is a hardware ABI. A wrong mask or shift can silently produce valid C that programs the wrong arbitration, address-decode, TLB, power-control, error, or performance-counter behavior.
- The chunk starts mid-register. Whole-file reconciliation must connect the earlier `MMEA1_DRAM_RD_CLI2GRP_MAP0` shifts and masks for CID0-CID9 from the previous chunk with CID10-CID15 masks here.
- The MMEA1 client-to-group maps pack two-bit values at every even bit position. Off-by-two shifts can remap a different client ID while still remaining inside the register.
- The address decode fields are dense and repeated across CS0-CS3, secondary chip selects, decoder 0/1, bank/hash, column, row-mask, pipe, stack, subchannel, channel, and bank selectors. Copying a field from the wrong decoder or chip-select register can generate plausible but wrong DRAM interleave behavior.
- Several fields encode address fragments, limits, masks, or selectors rather than byte addresses. Callers must preserve the hardware-specific units expected by each register and should not treat all fields as full physical addresses.
- `MMEA1_EDC_CNT*`, `MMEA1_DSM_CNTL*`, `MMEA1_EDC_MODE`, and `MMEA1_ERR_STATUS` mix diagnostic counts, injection/select controls, bypass/propagation behavior, and clear/status bits. The shift/mask header does not say which bits are safe to write during normal operation.
- `PCTL*_RENG_EXECUTE` and `PCTL*_MISC` fields can affect power-control execution, locks, and deep-sleep/state-controller behavior. Incorrect writes may interfere with save/restore or power gating rather than failing locally.
- Full-width masks such as performance-counter low values or status bitmaps should be handled as unsigned 32-bit quantities. Signed promotion and format-string mistakes can make register dumps misleading.
- Cross-generation MMHUB headers use very similar names. Mixing `mmhub_9_1_sh_mask.h` fields with offsets from another MMHUB variant can compile but target the wrong register layout.

## Test And Validation Signals

There are no direct unit tests for this macro-only chunk. Useful validation signals are compile-time, static, and hardware-facing:

- Build AMDGPU configurations that include the MMHUB 9.1 offset and shift/mask headers and compile the relevant GMC/MMHUB/RAS paths.
- Run static mask/shift checks for this chunk: single-bit masks must equal `1 << shift`; multi-bit masks must be contiguous at the documented shift; repeated map fields should advance by two bits for client groups and by three bits for virtual-channel fields; full-width masks should have shift zero.
- Compare each register comment in this chunk against `mmhub_9_1_offset.h` to ensure a matching `mm*` offset and base index exist in the expected address block.
- Validate golden-register programming and register dumps for `MMEA1_DRAM_WR_CLI2GRP_MAP0`, especially client-group fields that are touched by initialization defaults.
- Exercise MMHUB initialization, suspend/resume, power-gating, deep-sleep, and RAS/error-reporting paths on hardware using this generation. Relevant signals include stable MMEA1 arbitration values, expected PCTL save/restore behavior, correct L1 TLB busy/parity status reporting, and coherent L1 performance-counter clear/enable/read behavior.
- For address-decode fields, useful validation is hardware register-dump comparison against known-good firmware tables and stress tests that cover VRAM interleave/channel/CS configurations.
- For `VM_L2_SAW_CNTL*`, VM/GART stress, TLB invalidation tests, page-fault injection, suspend/resume, and SR-IOV or virtualization scenarios should verify that cache enablement, invalidation, identity-mode, and default-page behavior match the programming guide.

## Chunk Notes For Merge Lane

This chunk covers the second half of the `MMEA1` block, the full `mmhub_pctldec` power-control block, L1 TLB status and performance-counter blocks, and the opening L2 SAW control fields. It begins after the `MMEA1_DRAM_RD_CLI2GRP_MAP0` field list has already started and ends just before `VM_L2_SAW_CNTL3` definitions continue in the next chunk, so whole-file reconciliation should merge both boundaries with adjacent chunk documents.

### subset-b-002827: lines 7156-9627

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_1_sh_mask.h lines 7156-9627

## Scope And Purpose

This chunk is a generated-style AMDGPU MMHUB 9.1 shift/mask header section. It exposes compile-time bitfield constants for MMHUB VM L2, ATC L2, virtual-memory context, invalidation, performance-counter, SR-IOV shared aperture, MARC, IOMMU, PCIe ATS, and UTCL2 clock-gating registers. The symbols follow the hardware-register convention `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`; there are no C functions, structs, enums, variables, or executable branches in this range.

The range starts in the `VM_L2_SAW_*` block and then covers address blocks named by comments: `mmhub_utcl2_atcl2dec`, `mmhub_utcl2_vml2pfdec`, `mmhub_utcl2_vml2vcdec`, `mmhub_utcl2_vml2pldec`, `mmhub_utcl2_vml2prdec`, and `mmhub_utcl2_vmsharedhvdec`. The corresponding address constants live in `mmhub_9_1_offset.h`; this file supplies only bit positions and masks for packing and unpacking 32-bit MMIO register values.

The main purpose is to make driver register access type-safe at the preprocessor level. AMDGPU code can write `REG_SET_FIELD(tmp, VM_L2_CNTL, ENABLE_L2_CACHE, 1)` or extract fault fields with `REG_GET_FIELD(status, VM_L2_PROTECTION_FAULT_STATUS, CID)` because this header defines the exact mask and shift pairs.

## Important APIs, Types, And Constants

There are no callable APIs or C types. The exported interface is the macro set consumed by AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `SOC15_REG_OFFSET`, and register-list helpers.

Important register groups in this chunk include:

- `VM_L2_SAW_CNTL3`, `VM_L2_SAW_CNTL4`, `VM_L2_SAW_CONTEXT0_CNTL`, `VM_L2_SAW_CONTEXT0_CNTL2`, `VM_L2_SAW_CONTEXT0_PAGE_TABLE_*`, `VM_L2_SAW_CONTEXTS_DISABLE`, and `VM_L2_SAW_PIPES_BUSY`: SAW-side VM L2 cache configuration, context-0 page-table range programming, fault default/interrupt/save controls, context-disable bitmap, and pipe-busy status.
- `ATC_L2_CNTL`, `ATC_L2_CNTL2`, `ATC_L2_CACHE_DATA0/1/2`, `ATC_L2_CNTL3`, `ATC_L2_STATUS`, `ATC_L2_STATUS2`, `ATC_L2_MISC_CG`, `ATC_L2_MEM_POWER_LS`, and `ATC_L2_CGTT_CLK_CTRL`: ATC L2 translation request sizing, cache update mode, data window access, invalidation state, busy/state-change status, memory light-sleep, and clock-gating controls.
- `VM_L2_CNTL`, `VM_L2_CNTL2`, `VM_L2_CNTL3`, `VM_L2_CNTL4`, `VM_L2_STATUS`, and `VM_DUMMY_PAGE_FAULT_*`: MMHUB VM L2 cache enablement, fragment/cache modes, invalidation control, identity/tap behavior, busy status, and dummy-page fault address controls.
- `VM_L2_PROTECTION_FAULT_CNTL`, `VM_L2_PROTECTION_FAULT_CNTL2`, `VM_L2_PROTECTION_FAULT_MM_CNTL3/4`, `VM_L2_PROTECTION_FAULT_STATUS`, `VM_L2_PROTECTION_FAULT_ADDR_*`, and `VM_L2_PROTECTION_FAULT_DEFAULT_ADDR_*`: fault routing, default-page behavior, crash-on-fault policy, per-client interrupt masks, retry/PRT controls, captured fault metadata, faulting logical page address, and default physical page address.
- `VM_L2_CONTEXT1_IDENTITY_APERTURE_*` and `VM_L2_CONTEXT_IDENTITY_PHYSICAL_OFFSET_*`: identity aperture bounds and physical offset used when context identity access is enabled or disabled.
- `VM_CONTEXT0_CNTL` through `VM_CONTEXT15_CNTL`: per-VMID context controls for enablement, page-table depth and block size, retry behavior, and interrupt/default handling for range, dummy, PDE0, valid, read, write, and execute protection faults.
- `VM_CONTEXTS_DISABLE`: a 16-bit bitmap that disables contexts 0 through 15.
- `VM_INVALIDATE_ENG0_SEM` through `VM_INVALIDATE_ENG17_SEM`, `VM_INVALIDATE_ENG0_REQ` through `VM_INVALIDATE_ENG17_REQ`, `VM_INVALIDATE_ENG0_ACK` through `VM_INVALIDATE_ENG17_ACK`, and `VM_INVALIDATE_ENG*_ADDR_RANGE_*`: eighteen invalidation engines with semaphore, request, acknowledge, and optional address-range fields. Request fields include per-VMID invalidation, flush type, invalidate-L2 PTE/PDE bits, invalidate-L1-PTEs, clear-protection-fault-status, and interrupt/ack controls.
- `VM_CONTEXT*_PAGE_TABLE_BASE_ADDR_*`, `VM_CONTEXT*_PAGE_TABLE_START_ADDR_*`, and `VM_CONTEXT*_PAGE_TABLE_END_ADDR_*`: per-context page-table base and logical range fields split into low 32-bit and high 4-bit page-number fragments.
- `MC_VM_L2_PERFCOUNTER0_CFG` through `MC_VM_L2_PERFCOUNTER7_CFG`, `MC_VM_L2_PERFCOUNTER_RSLT_CNTL`, `MC_VM_L2_PERFCOUNTER_LO`, and `MC_VM_L2_PERFCOUNTER_HI`: eight VM L2 performance-counter config registers plus result control and low/high result/compare fields.
- `MC_VM_FB_SIZE_OFFSET_VF0` through `MC_VM_FB_SIZE_OFFSET_VF15`: SR-IOV virtual-function framebuffer size and offset fields, with 16-bit size in the low half and 16-bit offset in the high half.
- `VM_IOMMU_MMIO_CNTRL_1`, `VM_IOMMU_CONTROL_REGISTER`, and `VM_IOMMU_PERFORMANCE_OPTIMIZATION_CONTROL_REGISTER`: MARC enable, IOMMU enable, and IOMMU performance optimization enable bits.
- `MC_VM_MARC_BASE_*`, `MC_VM_MARC_RELOC_*`, and `MC_VM_MARC_LEN_*`: four MARC aperture base, relocation, length, enable, and read-only register sets, using 4 KB-aligned low fragments and high fragments.
- `VM_PCIE_ATS_CNTL` and `VM_PCIE_ATS_CNTL_VF_0` through `VM_PCIE_ATS_CNTL_VF_15`: PCIe ATS state, including system translation unit (`STU`) for the physical function and `ATC_ENABLE` for PF/VF paths.
- `UTCL2_CGTT_CLK_CTRL`: UTCL2 clock-gating timing, soft override, medium-grain light-sleep override, and stall override fields.

## Control Flow And State Behavior

This header has no runtime control flow. Runtime effects happen only when consumers combine these constants with MMIO access helpers. The usual pattern is read-modify-write: read a 32-bit register with `RREG32_SOC15`, update named fields with `REG_SET_FIELD`, then write back with `WREG32_SOC15` or `WREG32_SOC15_OFFSET`.

The VM L2 and ATC L2 control fields persist as hardware register state. Driver initialization enables or disables L2 cache, fragment processing, L1/L2 invalidation behavior, cache update policies, tap physical/shared/snoop attributes, and clock-gating behavior. These settings remain active until a later register write, GPU reset, power transition, or firmware/hypervisor reprogramming.

Context registers model VMID state. Context-control fields decide whether a VMID is active, how deep its page table is, the block size used by the walker, and how protection faults are handled. Page-table base/start/end registers persist the page-number fragments used by the memory-management hardware to translate GPU virtual addresses.

Invalidation-engine registers implement an asynchronous request/acknowledge flow. Software writes a request register, optionally writes address-range registers, and waits for the matching acknowledge bit/register to show completion. The `*_SEM` fields serialize access to engines, and `PER_VMID_INVALIDATE_REQ` plus invalidate PTE/PDE/L1 bits define the scope of the flush.

Protection-fault status and address registers are hardware-owned diagnostic state. `VM_L2_PROTECTION_FAULT_STATUS` captures flags such as more faults, walker error, permission faults, mapping error, client ID, read/write, atomic, VMID, VF, and VFID. The address registers capture the faulting logical page number. Control bits decide whether later faults can update this state and whether faults are redirected to a default page, generate interrupts, retry, or crash.

Performance-counter fields expose hardware accumulation state. The config registers select events and modes; result-control fields globally enable, clear, trigger, and stop counters; result registers expose low/high counts and compare values. The header does not indicate read-clear behavior or counter access ordering.

The SR-IOV VF framebuffer and ATS fields represent virtualization-facing state. VF size/offset registers define guest-visible FB windows, while PF/VF ATS enable bits control whether address translation caching is allowed for PCIe requests. MARC registers define up to four relocation apertures and their read-only/enabled attributes when MARC is enabled.

## Dependencies And Integration Points

The immediate dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_1_offset.h`, which provides the matching `mm*` register addresses and base indices. This `_sh_mask.h` file is unsafe to use with offsets from another MMHUB generation because cross-generation register names are similar while layouts and base-indexing can differ.

Direct include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v1_0.c`, which includes `mmhub_9_1_offset.h` and `mmhub_9_1_sh_mask.h` alongside VCN 1.0 headers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn10/dcn10_resource.c`, which includes this MMHUB 9.1 pair alongside DCN 1.0 and NBIO headers.

The broader MMHUB/GMC integration pattern is visible in adjacent-generation code. `mmhub_v1_0.c` and `mmhub_v1_8.c` program corresponding VM L2 and context fields during GART enablement, system aperture setup, cache initialization, VMID context setup, fault policy changes, invalidation setup, and clock-gating changes. `gmc_v9_0.c` uses same-family `VM_L2_PROTECTION_FAULT_STATUS` and `VM_INVALIDATE_ENG0_REQ` field names to decode VM faults and build invalidation requests.

These macros also integrate with `struct amdgpu_vmhub` setup. MMHUB initialization code records offsets such as context-0 page-table base, invalidation-engine request/ack registers, context control, fault status, and fault control; it also derives register spacing from `VM_CONTEXT1_* - VM_CONTEXT0_*` and `VM_INVALIDATE_ENG1_* - VM_INVALIDATE_ENG0_*`. The repeated context and engine macro groups in this chunk support that regular spacing model.

## Risks And Edge Cases

- This header is a hardware ABI. An incorrect mask or shift can compile cleanly while corrupting MMHUB translation, cache, invalidation, fault, virtualization, or power-management behavior.
- Many fields are address fragments rather than byte addresses. Page-table bases, start/end ranges, fault addresses, dummy/default page addresses, and MARC low registers use page-number or 4 KB-aligned fragments; callers must apply the generation-specific shifts consistently.
- The context and invalidation groups are repetitive. Copy/paste or generation drift can easily leave one VMID or engine with a wrong field definition while neighboring definitions look correct.
- `VM_INVALIDATE_ENG*_REQ` is densely packed with VMID, flush type, invalidate selectors, interrupt, and fault-status clear controls. A bad field boundary can cause partial TLB flushes, missed acknowledgements, or stale protection-fault state.
- Fault handling fields are policy-sensitive. Accidentally changing default-page, interrupt, retry, or crash-on-fault bits can convert recoverable GPUVM faults into hangs, silent data redirection, or excessive interrupt storms.
- Status, acknowledge, busy, and performance-counter fields may be volatile or write-one-to-clear depending on hardware semantics. The generated masks do not encode access type, reset value, side effects, or required ordering.
- `MC_VM_FB_SIZE_OFFSET_VF*`, `VM_PCIE_ATS_CNTL_VF_*`, and MARC fields are virtualization/security-sensitive. Wrong VF size/offset, ATS enablement, MARC enable, or read-only bits can expose the wrong framebuffer aperture or translate through the wrong address path.
- Full-width masks such as `0xFFFFFFFFL` should be handled as 32-bit unsigned hardware values. Signed promotion in diagnostics or helper changes can misrepresent status/counter values.
- Cross-generation headers contain many identical register and field names. Including `mmhub_9_1_sh_mask.h` with non-9.1 offsets, or reusing a newer MMHUB macro against these offsets, can silently program the wrong bit layout.

## Test And Validation Signals

There are no unit tests for this macro-only chunk. Useful validation signals are compile-time, static, and hardware-facing:

- Build AMDGPU configurations that compile the direct consumers `vcn_v1_0.c` and `dcn10_resource.c` with `mmhub_9_1_offset.h` plus `mmhub_9_1_sh_mask.h`.
- Run static mask/shift validation: single-bit masks should equal `1U << shift`; multi-bit masks should be contiguous at their shift; low/high address fragments should have shift zero or documented alignment shifts; repeated VM context, invalidation engine, VF, MARC, and perf-counter groups should have consistent field layouts.
- Compare each comment-delimited register group in this chunk against `mmhub_9_1_offset.h` to ensure a matching address definition exists and belongs to the expected address block.
- On supported MMHUB 9.1 hardware, validate GART and VM setup by checking context page-table base/start/end registers, VM L2 cache controls, fault default address programming, and identity aperture state after driver load and resume.
- Exercise VM invalidation paths and verify that request/ack registers transition as expected for all allocated engines, including per-VMID invalidation and address-range invalidation when enabled.
- Inject or observe GPUVM faults and confirm that decoded `CID`, `RW`, `ATOMIC`, `VMID`, `VF`, `VFID`, permission, walker, mapping, and more-fault fields match the faulting workload and kernel logs.
- In SR-IOV scenarios, inspect VF framebuffer size/offset registers and VF ATS enable bits across PF and VF initialization. Confirm that VFs cannot see outside their assigned aperture.
- For MARC/IOMMU/ATS features, validate enable/disable sequences against firmware policy and platform capabilities, including read-only MARC ranges and PCIe ATS behavior.
- For clock-gating and performance counters, verify that enabling/disabling clock-gating does not break register access and that perf-counter clear/enable/trigger/result fields behave consistently across suspend/resume and reset.

## Chunk Notes For Merge Lane

This chunk covers the lower MMHUB 9.1 VM and translation-control half: SAW VM L2 tail, ATC L2 controls, VM L2 protection fault and context controls, invalidation engines 0-17, per-context page-table registers, VM L2 performance counters, SR-IOV VF framebuffer windows, MARC/IOMMU/ATS controls, and the beginning of `UTCL2_CGTT_CLK_CTRL`. Whole-file reconciliation should merge this with earlier chunks that cover the opening DAGB/system-aperture blocks and later chunks, if any, that complete the trailing clock-gating fields and include guard.

### subset-b-002828: lines 9628-9790

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_1_sh_mask.h lines 9628-9790

## Scope And Purpose

This chunk is the closing range of the generated AMDGPU MMHUB 9.1 shift/mask header. It finishes the `UTCL2_CGTT_CLK_CTRL` mask definitions, defines the shared PF and virtual-channel VM aperture fields, defines the L1 TLB control fields, defines ATC L2 performance-counter fields, and ends the include guard. The source file is declarative hardware metadata: it contains preprocessor constants only, with no C functions, structs, variables, branches, loops, allocation, locking, or direct MMIO access.

The effective purpose is to provide bit-accurate field locations for SOC15 MMHUB 9.1 registers. Consumers pair these `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros with the matching register offsets from `mmhub_9_1_offset.h` and AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15*`, and `WREG32_SOC15*`.

Although this repository path is under a local Ceph client source import, this file belongs to the Linux AMDGPU DRM hardware interface. It has no Ceph filesystem behavior.

## Important APIs, Types, And Register Families

There are no callable APIs or local types in this chunk. The public surface is the macro namespace for the following register groups:

- `UTCL2_CGTT_CLK_CTRL`: clock-gating timing and override fields for the UTCL2 block. The chunk contains masks for `ON_DELAY`, `OFF_HYSTERESIS`, `SOFT_OVERRIDE_EXTRA`, `MGLS_OVERRIDE`, `SOFT_STALL_OVERRIDE`, and `SOFT_OVERRIDE`; the matching shifts start just before this chunk and are visible in nearby context.
- `MC_VM_NB_MMIOBASE` and `MC_VM_NB_MMIOLIMIT`: full-width MMIO aperture base/limit fields for the shared PF decoder.
- `MC_VM_NB_PCI_CTRL` and `MC_VM_NB_PCI_ARB`: PCI-side enable and VGA-hole fields. `MMIOENABLE` lives at bit 23, and `VGA_HOLE` at bit 3.
- `MC_VM_NB_TOP_OF_DRAM_SLOT1`, `MC_VM_NB_LOWER_TOP_OF_DRAM2`, and `MC_VM_NB_UPPER_TOP_OF_DRAM2`: top-of-memory registers for DRAM slot/TOM2 layout. `LOWER_TOP_OF_DRAM2` includes an enable bit plus a high-address field.
- `MC_VM_FB_OFFSET`: 24-bit framebuffer offset field.
- `MC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_LSB` and `MC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_MSB`: default physical page address fields used when aperture handling redirects to a default page.
- `MC_VM_STEERING`: two-bit default steering selector.
- `MC_SHARED_VIRT_RESET_REQ`: virtualization reset request bitmap, with 16 VF bits and a PF bit at bit 31.
- `MC_MEM_POWER_LS`: memory light-sleep setup and hold timing fields.
- `MC_VM_CACHEABLE_DRAM_ADDRESS_START` and `MC_VM_CACHEABLE_DRAM_ADDRESS_END`: cacheable DRAM range fields.
- `MC_VM_APT_CNTL`: aperture controls for forcing uncacheable memory type and enabling direct system access.
- `MC_VM_LOCAL_HBM_ADDRESS_START`, `MC_VM_LOCAL_HBM_ADDRESS_END`, and `MC_VM_LOCAL_HBM_ADDRESS_LOCK_CNTL`: local HBM range and one-bit lock control.
- `MC_VM_FB_LOCATION_BASE` and `MC_VM_FB_LOCATION_TOP`: 24-bit framebuffer aperture base/top fields.
- `MC_VM_AGP_TOP`, `MC_VM_AGP_BOT`, and `MC_VM_AGP_BASE`: 24-bit AGP aperture registers.
- `MC_VM_SYSTEM_APERTURE_LOW_ADDR` and `MC_VM_SYSTEM_APERTURE_HIGH_ADDR`: 30-bit logical system-aperture low/high fields.
- `MC_VM_MX_L1_TLB_CNTL`: main L1 TLB control register, including `ENABLE_L1_TLB`, `SYSTEM_ACCESS_MODE`, `SYSTEM_APERTURE_UNMAPPED_ACCESS`, `ENABLE_ADVANCED_DRIVER_MODEL`, `ECO_BITS`, `MTYPE`, and `ATC_EN`.
- `ATC_L2_PERFCOUNTER_LO` and `ATC_L2_PERFCOUNTER_HI`: low/high performance-counter words. The high word also packs a 16-bit compare value.
- `ATC_L2_PERFCOUNTER0_CFG` and `ATC_L2_PERFCOUNTER1_CFG`: ATC L2 counter event-range, mode, enable, and clear controls.
- `ATC_L2_PERFCOUNTER_RSLT_CNTL`: counter result selection, start/stop trigger fields, enable-any, clear-all, and stop-on-saturate controls.

The companion offset chunk in `mmhub_9_1_offset.h` maps these same register names to offsets: `mmUTCL2_CGTT_CLK_CTRL` at `0x0808`, shared PF registers beginning at `mmMC_VM_NB_MMIOBASE` `0x0810`, shared VC registers beginning at `mmMC_VM_FB_LOCATION_BASE` `0x082c`, ATC L2 counter result registers at `0x0840` and `0x0841`, and ATC L2 counter controls at `0x0848` through `0x084a`.

## Control Flow And Runtime Use

This chunk has no local runtime control flow. All sequencing is in consumer code that includes the header and uses the constants during device initialization, VM/GART setup, power management, SR-IOV handling, debug, or performance-counter access.

The closest AMDGPU consumers in this tree show how these fields are expected to be used:

- `mmhub_v1_7.c` and `mmhub_v1_8.c` include generation-specific MMHUB headers with the same `MC_VM_*` macro names. Their `get_fb_location` paths read `regMC_VM_FB_LOCATION_BASE` and `regMC_VM_FB_LOCATION_TOP`, mask them with `MC_VM_FB_LOCATION_*__FB_*_MASK`, shift by 24, and store `adev->gmc.fb_start` / `adev->gmc.fb_end`.
- Their system-aperture setup writes `MC_VM_AGP_*`, `MC_VM_SYSTEM_APERTURE_LOW_ADDR`, `MC_VM_SYSTEM_APERTURE_HIGH_ADDR`, `MC_VM_FB_LOCATION_BASE`, `MC_VM_FB_LOCATION_TOP`, and default-address registers according to `adev->gmc` aperture state and whether `pdb0_bo` squeezes VRAM into the GART aperture.
- Their TLB setup reads `regMC_VM_MX_L1_TLB_CNTL`, uses `REG_SET_FIELD` with the `MC_VM_MX_L1_TLB_CNTL` masks from the included shift/mask header, enables the L1 TLB, selects system access mode 3, enables the advanced driver model, disables unmapped system-aperture access, programs `MTYPE`, and enables ATC. Disable paths clear `ENABLE_L1_TLB` and `ENABLE_ADVANCED_DRIVER_MODEL`.
- `mmhub_v1_8.c` additionally handles multi-instance MMHUB programming through `adev->aid_mask`, and can route L1 TLB programming through PSP (`psp_reg_program_no_ring`) when SR-IOV requires indirect access.
- `vcn_v1_0.c` directly includes `mmhub/mmhub_9_1_offset.h` and `mmhub/mmhub_9_1_sh_mask.h`, making the MMHUB 9.1 register definitions visible to VCN 1.0 code and register checking infrastructure.

The version-selection path in `gmc_v9_0.c` routes MMHUB versions to concrete function tables. IP version `9.1.0` uses Raven client information and, for older MMHUB generations, falls back to the v1.0-style MMHUB implementation unless a newer explicit version is selected. The key integration point for this chunk is still the generated register namespace: any translation unit that includes the matching MMHUB 9.1 offset and shift/mask headers can compose these specific registers.

## State And Persistence Behavior

The header stores no software state. It describes fields in MMIO-backed GPU hardware registers. When consumer code writes these fields, values persist in MMHUB hardware until reset, power transition, firmware reinitialization, driver reprogramming, or another register writer changes them.

The state represented by this chunk includes:

- Physical and logical memory aperture state: NB MMIO base/limit, framebuffer aperture base/top, AGP aperture base/bottom/top, system aperture low/high, default physical page address, framebuffer offset, and cacheable/local memory ranges.
- Virtualization state: PF/VF reset request bits and SR-IOV-visible aperture controls. Callers must respect VF restrictions; related MMHUB setup code often returns early in SR-IOV VF mode for privileged aperture programming.
- Translation state: L1 TLB enablement, advanced driver model mode, ATC enablement, memory type selection, and unmapped-system-aperture behavior.
- Power-management state: UTCL2 clock-gating delay/override bits and memory light-sleep timing.
- Performance/debug state: ATC L2 counter values, counter compare value, event select range, mode, enable/clear controls, start/stop triggers, and global clear/stop-on-saturation controls.
- Lock state: `MC_VM_LOCAL_HBM_ADDRESS_LOCK_CNTL__LOCK` protects or freezes the programmed local HBM address range according to hardware semantics; this header only defines the bit, not the locking protocol.

The masks do not encode access permissions, side effects, reset values, or required ordering. Status/counter fields, clear bits, lock bits, and reset-request bits may be read-only, write-one-to-clear, self-clearing, sticky, privileged, or sequencing-sensitive depending on the hardware specification and firmware state.

## Dependencies And Integration Points

This chunk depends on the generated AMDGPU register-header convention:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_1_offset.h` provides the matching `mm*` register offsets and base indices for the registers described here.
- Consumer C files use SOC15 helpers from `soc15.h` / `soc15_common.h` plus AMDGPU register helpers to read/modify/write the fields.
- Generation-specific MMHUB implementations such as `mmhub_v1_7.c`, `mmhub_v1_8.c`, and older/newer MMHUB files show the common programming model for the same `MC_VM_*` and `ATC` field names, even when they include different generated headers.
- GMC initialization code owns broader routing: it initializes MMHUB client IDs, selects MMHUB function tables, drives GART enable/disable, and calls the selected MMHUB callbacks.
- VCN 1.0 includes the MMHUB 9.1 headers directly, so macro changes in this file can affect media-engine register-list or register-check compilation even if the main MMHUB setup path is elsewhere.

The chunk also mirrors names and layouts present in related generated GC/MMHUB 9.x headers, such as `gc_9_1_sh_mask.h`, but those should be treated as separate hardware contracts. Offsets, base indices, and prefixing differ between IP blocks and generations.

## Risks And Edge Cases

- These constants are a hardware ABI. A wrong mask or shift can silently program the wrong bits while compiling successfully.
- Aperture field widths vary: many address fields are 24-bit or 30-bit page/logical-address fields, while default-address LSB fields are full 32-bit and MSB fields are narrow. Callers must apply the same page shifts expected by hardware (`>> 12`, `>> 18`, `>> 24`, or high-address extraction in observed consumers) before using these masks.
- `MC_VM_FB_LOCATION_BASE/TOP`, AGP, and system-aperture fields control address decoding. Incorrect values can expose the wrong memory range, disable valid apertures, route accesses to the default page, or cause VM faults.
- `MC_VM_MX_L1_TLB_CNTL` packs several operational mode bits into one register. Read-modify-write is required so enabling `ATC_EN` or `ENABLE_L1_TLB` does not clobber `SYSTEM_ACCESS_MODE`, `MTYPE`, or ECO bits.
- `MC_SHARED_VIRT_RESET_REQ` can target VFs and PF state. Accidentally setting these bits in the wrong privilege context may reset virtual functions or affect PF-owned state.
- `MC_VM_LOCAL_HBM_ADDRESS_LOCK_CNTL` is a one-bit lock; once set, later writes to local HBM range fields may be ignored or require reset/firmware intervention depending on hardware behavior.
- Clock-gating override fields are not passive diagnostics. Forcing `SOFT_OVERRIDE`, `SOFT_STALL_OVERRIDE`, `MGLS_OVERRIDE`, or related UTCL2 controls can change power behavior and mask real idle/busy transitions.
- ATC L2 counter control has clear bits and global result controls. `CLEAR`, `CLEAR_ALL`, and stop-on-saturate operations can lose performance evidence if used by concurrent debug code.
- Macro names do not reveal access type. Full-width masks such as `0xFFFFFFFFL` and single-bit control masks have the same shape, so code review must rely on hardware docs and offset context, not naming alone.

## Test And Validation Signals

There are no direct unit tests for this macro-only chunk. Useful validation signals are compile-time, static, and hardware-observation based:

- Build AMDGPU translation units that include `mmhub_9_1_sh_mask.h`, especially `vcn_v1_0.c`, to catch missing or renamed macros.
- Cross-check every register group in this chunk against `mmhub_9_1_offset.h` for a matching `mm*` offset and base index.
- Run static mask/shift checks: single-bit masks should match their shift, multi-bit masks should be contiguous, fields in each register should not overlap, and full-width fields should have shift zero.
- Compare the generated masks against the authoritative AMD MMHUB 9.1 register database, with special attention to address field widths, `MC_VM_MX_L1_TLB_CNTL__MTYPE_MASK` width, PF/VF reset bits, and ATC L2 counter clear/control semantics.
- On Raven/MMHUB 9.1 hardware or a simulator, inspect register dumps after GART/MMHUB initialization and after suspend/resume or GPU reset. Expected signals include correct FB/AGP/system aperture values, L1 TLB enabled during normal operation, and disabled/cleared VM context state during GART shutdown.
- For performance-counter users, validate that `ATC_L2_PERFCOUNTER*_CFG` enable/clear behavior, high/low counter reads, compare value, start/stop triggers, and stop-on-saturate behavior match the hardware specification.

## Chunk Notes For Merge Lane

This is the final chunk of `mmhub_9_1_sh_mask.h`; it closes the include guard after the ATC L2 performance-counter control definitions. The final per-file report should merge this with earlier chunks covering DAGB, VM context, VM L2, protection-fault, ATS, and other UTCL2 registers before making whole-file statements about all MMHUB 9.1 register families.
