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
