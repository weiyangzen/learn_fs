# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/gaudi2_blocks_linux_driver.h lines 37749-42833

## Purpose

This chunk is part of the generated Gaudi2 Linux-driver ASIC block map. It defines preprocessor constants that describe memory-mapped register apertures for hardware blocks, not executable driver logic. Each represented aperture is encoded as a `BASE` address macro plus paired `MAX_OFFSET` and `SECTION` metadata macros.

The assigned range covers 5,085 lines. It starts inside the tail of the `NIC9_UMR0_14` entry, finishes the `NIC9` register-block map, then defines the complete `NIC10` and `NIC11` maps in this address region. It then transitions into data-core address ranges, covering all visible `DCORE0` and `DCORE1` debug/trace/performance-monitor blocks and the beginning of `DCORE2`, ending at `mmDCORE2_VDEC0_USER_CTI_BASE`.

The constants give other Gaudi2 driver code a single source of truth for register block base addresses and block spans. Consumers can compute register-window membership, debug dump windows, MMIO allow-list/protection ranges, and hardware block layout without embedding raw physical offsets in C code.

## Important APIs, Types, And Functions

This chunk defines macros only. It declares no C functions, structs, enums, or callable APIs.

The important macro families are:

- `mm..._BASE`: 64-bit unsigned MMIO base addresses, using the `ull` suffix. Examples include `mmNIC10_QM0_BASE`, `mmNIC11_MAC_CH3_MAC_AN_BASE`, `mmDCORE0_MME_CTRL_ROM_TABLE_BASE`, and `mmDCORE2_EDMA1_QM_ARC_RTT_BASE`.
- `..._MAX_OFFSET`: block-local maximum offset metadata. Most debug/trace blocks use `0x1000`; NIC subwindows use values such as `0x8000`, `0x5000`, `0x5800`, `0x31C0`, `0xA400`, and `0x4400`.
- `..._SECTION`: encoded section/span metadata for the Linux driver block table. Values vary by block, with common sections such as `0x1000`, `0x1800`, `0x4000`, `0x8000`, and larger aggregate spans such as `0x610800` for the final `NIC11_MAC_CH3_MAC_AN` section in this chunk.

The visible top-level prefixes and base-macro counts are:

- `NIC9`: 341 base macros in this range, starting at `mmNIC9_UMR0_14_SPECIAL_BASE` and ending at `mmNIC9_MAC_CH3_MAC_AN_BASE`.
- `NIC10`: 415 base macros, from `mmNIC10_UMR0_0_UNSECURE_DOORBELL0_BASE` through `mmNIC10_MAC_CH3_MAC_AN_BASE`.
- `NIC11`: 415 base macros, from `mmNIC11_UMR0_0_UNSECURE_DOORBELL0_BASE` through `mmNIC11_MAC_CH3_MAC_AN_BASE`.
- `PRT9`, `PRT10`, `PRT11`: four base macros each for MAC AUX/core and their special regions.
- `DCORE0`: 175 base macros, from `mmDCORE0_ROM_TABLE_L_BASE` through `mmDCORE0_VDEC1_BMON_2_BASE`.
- `DCORE1`: 175 base macros, from `mmDCORE1_ROM_TABLE_L_BASE` through `mmDCORE1_VDEC1_BMON_2_BASE`.
- `DCORE2`: 162 base macros visible in this chunk, from `mmDCORE2_ROM_TABLE_L_BASE` through `mmDCORE2_VDEC0_USER_CTI_BASE`.

## Covered Register Areas

The `NIC9`, `NIC10`, and `NIC11` regions are highly regular. For complete NIC instances, the chunk covers:

- UMR doorbell and completion-consumer-index regions: `UMR0_0` through `UMR0_14` and `UMR1_0` through `UMR1_14`, with unsecure doorbell windows, completion queue CI windows, and special windows.
- Queue manager blocks: `QM_DCCM0/1`, `QM_ARC_AUX0/1`, `QM0`, `QM1`, sixteen `QMAN_WR64_BASE_ADDR*` entries per QM, AXUSER secured/nonsecured, HBW/LBW debug, CGM, and special windows.
- QPC blocks: `QPC0` and `QPC1`, thirty DBFIFO CI update-address windows, secure and privileged DBFIFO windows, AXUSER subwindows for congestion queue, RX/TX WQE, doorbell FIFO, event queue interrupts, error FIFO, and QPC request/response.
- NIC packet-path blocks: `TMR`, `RXB_CORE`, `RXE0`, `RXE1`, RXE AXUSER completion-queue windows `CQ0` through `CQ31`, `TXS0/1`, `TXE0/1`, `TXB`, master-interface windows, `TX_AXUSER`, `SERDES0/1`, and `PHY`.
- MAC and port blocks: `PRT*_MAC_AUX`, `PRT*_MAC_CORE`, `NIC*_MAC_RS_FEC`, MAC global-stat control, RX/TX statistic windows, RS-FEC statistics, and four MAC channels with PCS, 128-bit MAC, and auto-negotiation windows.

The `DCORE0`, `DCORE1`, and visible `DCORE2` areas cover trace/debug infrastructure around compute and media blocks:

- One low ROM table region per data core, such as `mmDCORE0_ROM_TABLE_L_BASE`.
- Four HMMU groups per visible data core, each with CoreSight ROM table, STM, CTI, ETF, SPMU, BMON CTI, user CTI, and BMON windows.
- MME control, SBTE0 through SBTE4, and MME accumulator debug groups, mostly using ROM table, STM, CTI, ETF, SPMU, CTI0/CTI1, BMON, and ARC RTT windows.
- Scalar monitor/debug blocks: `SM_CS_DBG_ROM_TBL`, `SM_STM`, `SM_CTI`, `SM_ETF`, `SM_SPMU`, `SM_BMON_CTI`, `SM_USER_CTI`, `SM_BMON`, and `SM_BMON1`.
- Trace funnels and router/MIF funnel topology: `XFT`, `TFT0` through `TFT2`, `RTR0` through `RTR7`, and `MIF0` through `MIF3`, with ordering differing between even and odd data cores.
- EDMA0/EDMA1 debug groups and video decoder groups. `DCORE0` and `DCORE1` include both `VDEC0` and `VDEC1`; this chunk reaches only the beginning of `DCORE2_VDEC0`.

## Control Flow

There is no runtime control flow in this chunk. All content is preprocessor data used at compile time. The only ordering semantics are table-layout semantics: macros are grouped by ascending address and by hardware subsystem. The order is useful to generated consumers and reviewers because it mirrors the Gaudi2 MMIO address space.

The macro pattern is deterministic:

1. A block base macro names a register aperture and gives its absolute Gaudi2 MMIO address.
2. A `MAX_OFFSET` macro follows, describing the highest relevant block-local offset or range class used by generated driver tables.
3. A `SECTION` macro follows, describing the section/span grouping used by the Linux driver block map.

Most logical blocks use this exact triple. Long array-like blocks use sequentially numbered triples, such as `QMAN_WR64_BASE_ADDR0` through `QMAN_WR64_BASE_ADDR15`, DBFIFO update-address windows `0` through `29`, and RXE AXUSER completion-queue windows `CQ0` through `CQ31`.

## State And Persistence Behavior

The macros do not create software state and do not directly change hardware state. Their persistent value is build-time: every object file that includes this header sees the same symbolic addresses for Gaudi2 blocks. At runtime, driver code that uses these macros may read or write persistent hardware state through MMIO, but that side effect occurs in the consumer code, not in this header.

Because the values are compile-time constants, changing one macro changes every downstream binary use after recompilation. There is no runtime discovery, validation, or fallback in this chunk. Correctness depends on the generated constants matching the Gaudi2 hardware address map and the rest of the generated register headers.

## Dependencies

This header fragment depends on the broader Gaudi2 ASIC register generation scheme:

- Consumers expect `mm`-prefixed names for absolute MMIO base addresses.
- Consumers expect the paired non-`mm` `MAX_OFFSET` and `SECTION` names to share the same logical block prefix as the base macro.
- The constants must align with register-offset headers for individual registers under the same Gaudi2 ASIC family.
- The values are likely consumed by HabanaLabs debug, block-dump, register-access, security, and address-range code that accepts `u64` base addresses.

The chunk itself has no include dependencies in the local range, but the full header is integrated through Gaudi2 driver code under `drivers/accel/habanalabs` and must remain compatible with the C preprocessor and kernel integer constant rules.

## Integration Points

The primary integration point is any Gaudi2 driver path that needs block-level MMIO metadata rather than individual register offsets. Likely consumers include register dump collection, MMIO range validation, debugfs register access, RAZWI/error decoding, security aperture setup, and hardware bring-up diagnostics.

The NIC block constants integrate with Gaudi2 networking support. Queue managers and QPC constants expose the address layout for doorbells, completion queues, DBFIFOs, AXUSER settings, transmit/receive engines, timers, PHY/SERDES, and MAC/statistics regions. A driver component can use these macros to refer to `NIC10_QPC1_DBFIFOSECUR_CI_UPD_ADDR` or `NIC11_MAC_GLOB_STAT_RX*` windows without recomputing offsets.

The data-core constants integrate with compute, DMA, media, and hardware trace/debug support. HMMU, MME, SBTE, EDMA, VDEC, SPMU, CTI, ETF, STM, BMON, funnel, router, and MIF windows are all represented as block apertures. Diagnostic tooling can use these block definitions to decide which trace components exist under each DCORE and what address ranges are safe to traverse.

For final per-file reconciliation, this chunk must be joined with adjacent chunks because it begins mid-`NIC9_UMR0_14` and ends mid-`DCORE2`. The complete source file likely includes earlier NIC instances and later data-core blocks outside this chunk.

## Risks And Edge Cases

- The file is generated-style data with thousands of near-duplicate names. Copy/generation drift is the main risk: a single wrong digit in `NIC10`, `NIC11`, DCORE number, queue number, or address can direct MMIO access to the wrong block.
- Chunk boundaries are not semantic boundaries. The first line is only `NIC9_UMR0_14_COMPLETION_QUEUE_CI_1_SECTION`, whose base and max-offset macros are in the previous chunk. The last visible DCORE2 VDEC0 group continues beyond this chunk with at least the section macro for `DCORE2_VDEC0_USER_CTI` and later VDEC/BMON entries.
- Array-like naming must remain contiguous. Missing entries in `QMAN_WR64_BASE_ADDR*`, DBFIFO, or `RXE*_AXUSER_CQ*` sequences can break code that assumes fixed counts or generated loops.
- `BASE`, `MAX_OFFSET`, and `SECTION` values are not self-validating. A malformed value still compiles and can fail only during hardware access, debug collection, or security validation.
- Some section values are much larger than the adjacent block's `MAX_OFFSET`, especially end-of-group sections such as `NIC11_MAC_CH3_MAC_AN_SECTION 0x610800`. Consumers need to know whether `SECTION` is a local aperture length, a grouping carry value, or a generator-specific stride marker.
- The address map uses 64-bit constants. Consumers should avoid truncating `mm..._BASE` values into 32-bit variables even though the values visible in this chunk fit below 4 GiB.
- Security-sensitive users of these macros, such as allow-list or protection-table code, inherit the correctness of the generated map. An overly broad section or wrong base could expose or block unrelated MMIO.
- Data-core router/MIF funnel order differs between DCORE0/DCORE2 and DCORE1 in this chunk. Reviewers should not mechanically sort or normalize the order without checking hardware topology.

## Test Signals

Useful validation for this chunk is mostly static and hardware-integration focused:

- A generated-header consistency check should verify every `mm..._BASE` macro in the range has matching `..._MAX_OFFSET` and `..._SECTION` macros, except where the chunk boundary intentionally cuts a triple.
- Address monotonicity checks should confirm the listed blocks progress through the expected Gaudi2 MMIO ranges: `NIC9` near `0x588EE80` to `0x58EF800`, `NIC10` near `0x5900000` to `0x596F800`, `NIC11` near `0x5980000` to `0x59EF800`, then `DCORE0` at `0x6000000`, `DCORE1` at `0x6200000`, and `DCORE2` at `0x6400000`.
- Sequence checks should verify the repeated counts for complete NICs: two UMR banks with indices `0..14`, two QMs, two QPCs, DBFIFO update windows `0..29`, secure/privileged DBFIFO windows, and RXE completion queues `CQ0..CQ31`.
- Cross-instance diffs should compare `NIC10` and `NIC11` names and relative offsets. They should be structurally identical aside from NIC number and base-address stride.
- Cross-core diffs should compare `DCORE0` and `DCORE1` groups and flag intentional topology differences, such as funnel/router/MIF ordering and section sizes.
- Runtime smoke tests should exercise driver paths that enumerate block maps for NIC debug dumps, MAC statistics, HMMU/MME/EDMA/VDEC trace blocks, and register-access validation.
- Hardware error and debug tests should confirm that register dumps using these block bases do not fault, do not skip expected blocks, and do not read outside allowed Gaudi2 MMIO apertures.
- Security tests should confirm that any protection or allow-list code consuming `SECTION` metadata treats the large group-ending section values correctly and does not grant unintended access to adjacent blocks.
