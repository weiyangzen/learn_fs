# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/gaudi2_blocks_linux_driver.h lines 8832-13499

## Scope

This chunk is a generated Gaudi2 Linux-driver register block map. It contains only preprocessor constants: 4,668 `#define` lines, organized as 1,556 block-address triplets of `mm..._BASE`, `..._MAX_OFFSET`, and `..._SECTION` values. There are no C functions, structs, branches, or executable control flow in this range.

The covered address window starts at the tail of the DCORE0 router map around `DCORE0_RTR2_RTR_LBW_XACT_STAT_SECTION`, continues through DCORE0 router instances 3-7, DCORE0 SRAM banks 0-7, DCORE0 EDMA0/EDMA1, DCORE0 decoder and video decoder blocks, then enters DCORE1 with HIF0-HIF3, sync-manager, TPC0-TPC5, HMMU0-HMMU3, MME, router instances 0-7, and the beginning of DCORE1 SRAM0 debug-counter definitions. The first and last lines are chunk boundaries inside generated block groups: adjacent chunks carry the missing partner definitions for the first/last triplets.

This is accelerator driver hardware description data, not Ceph filesystem logic, despite being stored under the `sources/distributed-fs/ceph-client` source snapshot.

## Purpose

The header gives the Habana Labs Gaudi2 driver symbolic names for memory-mapped hardware block ranges. Driver code can use the macros to compute register addresses, validate block mmap ranges, iterate special blocks, program MMU/AXUSER/QMAN registers, diagnose RAZWI and fabric errors, and dump or clear status counters without hard-coding numeric addresses at each call site.

The macro naming convention carries most of the semantics:

- `mm<block>_BASE` is the absolute MMIO base address for the block or sub-block.
- `<block>_MAX_OFFSET` is the maximum register offset or range bound expected for that block class.
- `<block>_SECTION` is the spacing to the next repeated section, bank, engine, or logical slice when a block has generated instances.

The values use `ull` suffixes for base addresses so callers can safely hold them in 64-bit arithmetic before eventually using lower-level `RREG32`, `WREG32`, BAR mapping, or mmap helpers.

## Important Macro Families

DCORE0 router definitions:

- The range opens at the tail of `DCORE0_RTR2` transaction-status/debug-address definitions, then fully covers `DCORE0_RTR3` through `DCORE0_RTR7`.
- Each full router instance has control and H3 blocks; master-interface range-register, AXUSER, debug, E2E credit, and core HBW/LBW blocks; address decoder HBW/LBW blocks; router status blocks; link-layer statistics for HBW/LBW read/write request/response channels; MFIFO and E2E statistics; special blocks; and debug-address special ranges.
- Common section sizes encode hardware layout: many control/H3/debug blocks use `0xE800`, special blocks use `0x1800`, master RR lanes use `0x2000`, transaction statistics use `0x8000`, E2E router statistics often use `0x7800`, and debug-address special sections use `0x2180`.

DCORE0 SRAM definitions:

- `DCORE0_SRAM0` through `DCORE0_SRAM7` define bank and router bases, matching special ranges, and debug-counter groups.
- Each SRAM bank includes north/south/left HBW and LBW debug counters, left-bank0/left-bank1 HBW counters, HBW/LBW link-layer read/write request/response statistic counters, and a debug-counter special block.
- The banks are laid out at regular `0x8000` strides from `0x4180000` through `0x41B8000`, with per-bank internal offsets such as bank at `+0x0000`, router at `+0x1000`, debug counters at `+0x2000`, and special windows at `+0x0E80`, `+0x1E80`, or `+0x2E80`.

DCORE0 EDMA definitions:

- `DCORE0_EDMA0` and `DCORE0_EDMA1` each include queue-manager DCCM, ARC AUX, QMAN control, WR64 base-address registers 0-15, secured/non-secured AXUSER, debug HBW/LBW, CGM, special blocks, DMA core, core context, context AXUSER, KDMA CGM, and master-interface blocks.
- The QMAN WR64 base-address entries are eight-byte spaced register slots with large `0x8000` max-offset ranges and a shorter final section (`0x1880`) for the last entry in the group.
- These macros back EDMA initialization, queue tests, memory scrubbing, MMU-bypass setup, and DMA error/idle diagnostics in the Gaudi2 driver implementation.

DCORE0 decoder/video decoder definitions:

- `DCORE0_DEC0` and `DCORE0_DEC1` provide `CMD`, `L2C`, and `VSI` blocks.
- `DCORE0_VDEC0` and `DCORE0_VDEC1` provide control blocks, video bridge read/write request/response status and transaction-statistics blocks, bridge special blocks, and master-interface blocks.
- Decoder ranges are used by decoder init/stop paths, abnormal/normal interrupt handling, idle checks, and user-visible block mmap support.

DCORE1 HIF, sync-manager, HMMU, TPC, MME, router, and SRAM definitions:

- `DCORE1_HIF0` through `DCORE1_HIF3` define host-interface base and special windows.
- `DCORE1_SYNC_MNGR_OBJS`, `DCORE1_SYNC_MNGR`, and `DCORE1_SYNC_MNGR_RESERVED_*` cover sync-manager object space, reserved monitor/SOB/CQ style regions, AXUSER/debug/core windows, and special ranges.
- `DCORE1_TPC0` through `DCORE1_TPC5` repeat the TPC layout: QMAN DCCM/ARC AUX/QMAN/WR64/AXUSER/debug/CGM/special ranges, TPC config, 16 kernel tensor descriptors, kernel sync object, kernel config block, 16 QM tensor descriptors, QM sync object, QM config block, config AXUSER/special, and master-interface blocks.
- `DCORE1_HMMU0` through `DCORE1_HMMU3` define MMU, STLB, scramble-output, and master-interface windows for the four HBM MMU instances in this dcore.
- `DCORE1_MME` is the densest family in the chunk. It includes MME QMAN/ARC/DUP-engine ranges, QMAN WR64 entries, AXUSER/debug/CGM/special blocks, `CTRL_LO` and `CTRL_HI` architectural tensor/AGU/metadata ranges, accumulator and EU ranges, SBTE0-SBTE4 blocks, and WB0/WB1 blocks.
- `DCORE1_RTR0` through `DCORE1_RTR7` mirror the DCORE0 router pattern with bases beginning at `0x4340000` for RTR0 and ending near `0x437DE80` for RTR7 debug-address special.
- The chunk ends at `DCORE1_SRAM0_DBG_CNT_S_LBW_DBG_CNT_MAX_OFFSET`; the corresponding section macro is outside this chunk.

## Control Flow

There is no runtime control flow in this header chunk. The effective flow is compile-time substitution:

1. C source includes Gaudi2 register headers.
2. The preprocessor replaces symbolic block names with numeric constants.
3. Driver code combines base macros with register offsets or table indexes.
4. Register access helpers, mmap helpers, special-block iterators, firmware event handlers, and error-dump code use those computed addresses to read or write device MMIO.

The generated order is still operationally important. Many families are mechanically ordered by physical topology, for example router instance number, SRAM bank number, EDMA engine number, TPC number, HMMU number, MME sub-block, then DCORE1 router number. Code and generated tables in adjacent driver files often assume those families stay aligned with enum order, queue IDs, engine IDs, or special-block metadata.

## State And Persistence Behavior

The chunk itself stores no mutable state and creates no persistence. It is a static hardware-address contract compiled into the kernel driver.

Runtime state affected indirectly includes:

- Hardware MMIO registers addressed through these bases.
- Driver tables that hold block bases for QMANs, TPCs, MME, HMMUs, routers, SRAM debug counters, and user-mappable blocks.
- Kernel logs and debug dumps that name or traverse these blocks while diagnosing MMU faults, RAZWI captures, QMAN failures, link-layer errors, ECC, decoder issues, DMA state, and idle status.
- User-visible mmap validation where a block base and allowed extent determine which MMIO windows can be exposed.

Any value change in this header is persistent at the build-artifact level: the compiled driver will target different device addresses until rebuilt again.

## Dependencies And Integration Points

The direct dependency is the C preprocessor and any Gaudi2 source file that includes `gaudi2_blocks_linux_driver.h` directly or through broader generated register-map headers. The values integrate with the rest of the Habana Labs driver through:

- Gaudi2 implementation code in `drivers/accel/habanalabs/gaudi2/gaudi2.c`, which uses generated `mm...` names in register reads/writes, queue/engine initialization, MMU setup, event handlers, reset paths, idle checks, and block mmap.
- Generated register field/mask headers such as `gaudi2_masks.h` and block-specific register headers, which provide offsets and bit fields that are added to these bases.
- Common driver helpers such as `RREG32`, `WREG32`, `RMWREG32`, `hl_poll_timeout`, MMU helpers, firmware helpers, debugfs/state-dump paths, and user mmap paths.
- Hardware topology constants and tables for DCOREs, TPCs, EDMAs, HMMUs, MME engines, routers, SRAM banks, decoders, sync-manager objects, and queue managers.
- Firmware and diagnostic interfaces that report event IDs or engine IDs; handlers map those IDs to the relevant generated block base before reading cause, status, or address-capture registers.

## Risks And Edge Cases

The highest risk is silent address skew. A wrong base, section stride, or max offset will still compile but can make the driver program the wrong hardware block, read misleading fault state, expose the wrong mmap window, or fail to clear an interrupt.

Generated repetition makes off-by-one and copy-generation errors hard to spot manually. This chunk has several long repeated families whose only differences are dcore number, engine number, bank number, tensor index, or small base-address increments. Review should compare generated output against the ASIC register database, not against hand intuition.

Boundary handling matters for chunked research and reconciliation. The first line is only `DCORE0_RTR2_RTR_LBW_XACT_STAT_SECTION`; its base and max-offset definitions are above this range. The final visible block is only partially represented: `mmDCORE1_SRAM0_DBG_CNT_S_LBW_DBG_CNT_BASE` and its max offset are present, while the section macro is after line 13499.

There is a duplicate-looking `DCORE1_TPC4_QM_SPECIAL_SECTION 0x1800` near the transition from TPC4 QMAN special to TPC4 config definitions. Because this file is generated and this task is research-only, it should be treated as a signal for generator or reconciliation checks rather than edited here.

Max-offset and section values do not all match simple block sizes. Some are hardware-specific iteration spans, diagnostic-section distances, or special sentinel extents such as `0x8000`, `0xD400`, `0xA600`, `0x13180`, `0x15A00`, `0x1E000`, and `0x23180`. Callers must use the intended macro for range validation versus repeated-section stepping instead of assuming the fields are interchangeable.

Security and user-mapping risk is concentrated in AXUSER, secured/non-secured QMAN, special, and block-mmap-related ranges. If those bases are wrong, the driver can configure the wrong transaction attributes or expose registers that should remain inaccessible.

Router and RAZWI diagnostics are topology-sensitive. Router master-interface, address-decoder, transaction-stat, and debug-address bases must match dcore/router numbering and HBW/LBW/E2E lane semantics; otherwise RAZWI and fabric-fault logs can implicate the wrong initiator or address path.

## Test Signals

Useful validation signals for this generated header are compile-time and hardware-integration oriented:

- A full driver build succeeds with no missing macro references from Gaudi2 implementation files.
- Generated macro audits confirm every complete block in the range has exactly one `mm..._BASE`, one `..._MAX_OFFSET`, and one `..._SECTION`, allowing for documented chunk-boundary partial triplets.
- Address monotonicity checks pass for repeated families: DCORE0 routers 3-7, DCORE0 SRAM banks 0-7, EDMA0/EDMA1, TPC0-TPC5, HMMU0-HMMU3, and DCORE1 routers 0-7.
- Driver probe on Gaudi2 hardware completes MMU, QMAN, TPC, MME, EDMA, decoder, sync-manager, and HMMU initialization without invalid-register or timeout errors.
- Queue tests, EDMA memory scrub, context setup, and device idle checks reach the expected block instances, especially DCORE0 EDMA and DCORE1 TPC/MME ranges covered here.
- Injected or firmware-reported QMAN, MMU, MME, TPC, decoder, router, SRAM, and RAZWI events produce cause logs from the expected dcore/block instance.
- User block mmap attempts accept exactly the intended Gaudi2 blocks and reject offsets beyond the relevant `MAX_OFFSET` or mapped section extent.
- Special-block traversal and global-error scans do not access unmapped holes or skip intended `SPECIAL` windows.
- Register-dump comparisons against hardware documentation or firmware-provided maps show the same base addresses from `0x4154700` through the visible `0x4382500` range.
