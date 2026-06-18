# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/gaudi2_blocks_linux_driver.h lines 13500-18084

## Purpose

This chunk is a generated Gaudi2 ASIC block-address map for the HabanaLabs Linux driver. It contains only preprocessor constants: each hardware sub-block is represented by a base address macro, a maximum offset macro, and a section-size/stride macro. The driver includes this file through `gaudi2_regs.h`, so these constants become the common compile-time address vocabulary for Gaudi2 MMIO, queue-manager, SRAM, TPC, MME, router, HIF, HMMU, decoder, and DMA logic.

The selected range starts in the middle of the `DCORE1_SRAM0_DBG_CNT` definitions and ends in the middle of the `DCORE2_EDMA0_QM_QMAN_WR64_BASE_ADDR` table. Within those boundaries it covers the tail of DCORE1 SRAM0, all DCORE1 SRAM1-7, DCORE1 EDMA0/EDMA1, DCORE1 decoder/video-decoder bridge areas, a large DCORE2 compute/interconnect slice, all DCORE2 SRAM0-7, and the beginning of DCORE2 EDMA0 QM.

The file header marks this as auto-generated and says not to edit below the header. The research implication is that human changes should normally happen in the generator or source register database, not by hand-editing these literal addresses.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or runtime APIs in this chunk. The public interface is the macro namespace it contributes to every C file that includes `gaudi2_regs.h`.

The macro pattern is consistent:

- `mm<block>_BASE`: absolute Gaudi2 MMIO offset for the start of a block or sub-region, written as an unsigned long long literal such as `0x43CA000ull`.
- `<block>_MAX_OFFSET`: maximum valid offset span used by range-oriented code, register dump code, protection logic, or generated validation tables.
- `<block>_SECTION`: generated section size or spacing value for the block family. In repeated blocks this is often the stride to the next logical section, while for "special" windows it marks the special aperture size.

Important block families in this range include:

- `DCORE1_SRAM[0-7]`: bank, router, debug-counter, high-bandwidth and low-bandwidth request/response/stat-counter regions. SRAM1-7 are complete in this chunk; SRAM0 starts mid debug-counter group.
- `DCORE1_EDMA[0-1]`: queue-manager DCCM, ARC auxiliary, QM base, 16 WR64 base-address entries, AXUSER secured/non-secured windows, debug HBW/LBW windows, CGM, core, context, KDMA CGM, and master-interface regions.
- `DCORE1_DEC[0-1]` and `DCORE1_VDEC[0-1]`: decoder command/L2C/VSI blocks and video-decoder bridge/control/master-interface windows.
- `DCORE2_TPC[0-5]`: TPC queue-manager and configuration windows, including DCCM, ARC auxiliary, QM base, WR64 base-address slots, AXUSER, debug windows, CGM, kernel tensor descriptors, kernel and QM tensor descriptor arrays, CFG QM, EML CFG, master-interface blocks, and special regions.
- `DCORE2_HMMU[0-3]`: MMU, STLB, scrambler, and master-interface windows.
- `DCORE2_MME`: MME QM and ARC windows, MME control low/high and middle controls, tensor/AGU descriptor regions, SBTE0-4, accumulator, EU, writeback blocks, and master interfaces.
- `DCORE2_SYNC_MNGR`, `DCORE2_HIF[0-3]`, and `DCORE2_RTR[0-7]`: synchronization-manager objects/global/master-interface ranges, host-interface windows, router control/stat/add-dec/debug regions.
- `DCORE2_SRAM[0-7]`: complete bank/router/debug-counter maps for DCORE2 SRAM.
- `DCORE2_EDMA0_QM`: starts at the end of the chunk with DCCM, ARC auxiliary, QM base, and WR64 base-address entries 0 through 11. Entries 12-15 and the rest of EDMA0 continue after line 18084.

## Control Flow

This header has no executable control flow. Its effect is entirely at preprocessing and compilation time:

1. `gaudi2_regs.h` includes `gaudi2_blocks_linux_driver.h`.
2. Gaudi2 driver C files include `gaudi2_regs.h`.
3. The compiler substitutes the generated constants into static tables, register calculations, MMIO reads/writes, firmware CPU address tables, queue-manager mappings, interrupt handling, reset flows, and debug/range logic.

Representative integration in `gaudi2.c` shows how these macros are consumed. Queue ID tables map DCORE queue identifiers to QM base macros such as `mmDCORE1_TPC*_QM_BASE`, `mmDCORE2_TPC*_QM_BASE`, `mmDCORE2_EDMA0_QM_BASE`, and `mmDCORE2_MME_QM_BASE`. ARC CPU tables map firmware CPU IDs to QM ARC auxiliary and DCCM base macros such as `mmDCORE1_EDMA0_QM_ARC_AUX_BASE`, `mmDCORE2_EDMA0_QM_ARC_AUX_BASE`, and `mmDCORE2_EDMA0_QM_DCCM_BASE`. Event handling also selects QM base constants for HDMA events, including DCORE1 and DCORE2 EDMA queue managers.

Because the chunk is a linear list of constants, apparent "flow" is the hardware address-space ordering: DCORE1 SRAM gives way to DCORE1 EDMA and VDEC, then DCORE2 TPC/HMMU/MME/sync/HIF/router/SRAM, then the beginning of DCORE2 EDMA0.

## State And Persistence Behavior

The chunk stores no runtime software state and performs no persistence. It defines immutable compile-time literals. The persistent behavior is indirect: any compiled driver binary that used these constants will issue MMIO accesses to the encoded hardware offsets until rebuilt with different generated headers.

The macros describe hardware address state rather than owning it. Consumers may read or write SRAM bank registers, router counters, QM state, ARC DCCM/AUX windows, tensor configuration windows, MME controls, or synchronization-manager objects using these addresses. Incorrect literals can therefore persist as incorrect hardware behavior across every driver execution built from the bad header.

Boundary state matters for reconciliation. The first line in this chunk is not the first macro for `DCORE1_SRAM0`; it starts after earlier `DCORE1_SRAM0_BANK`, `RTR`, and initial debug-counter entries. The last line is not the end of `DCORE2_EDMA0_QM`; it stops after `DCORE2_EDMA0_QM_QMAN_WR64_BASE_ADDR11_SECTION`.

## Dependencies

This chunk depends on the generated Gaudi2 register-map source used by HabanaLabs tooling. Local code should treat the file as generated output.

Compile-time dependencies and consumers include:

- `include/gaudi2/asic_reg/gaudi2_regs.h`, which directly includes this header before the per-block register headers.
- Gaudi2 driver implementation files such as `gaudi2.c`, which use the block base macros in queue-base tables, ARC DCCM/AUX address tables, and event-specific queue-manager selection.
- Per-block generated register headers included by `gaudi2_regs.h`; those headers provide offsets inside many of the blocks whose base addresses are defined here.
- Kernel/HabanaLabs MMIO helpers such as register read/write macros, which combine these constants with offsets and device BAR mappings.
- Firmware and hardware contracts for Gaudi2 DCORE numbering, SRAM layout, QM/ARC windows, DCCM/AUX sizes, TPC/MME topology, and router/interconnect block placement.

The file uses the `ull` suffix for base literals because several generated addresses are 64-bit-style constants even when stored into narrower driver tables in specific consumers. Refactors need to preserve type expectations at use sites.

## Integration Points

This header is a low-level integration layer between the generated ASIC map and the Linux driver.

Queue management integration is especially visible. TPC, MME, and EDMA QM base constants from this chunk are used to build queue ID to QM base mappings. WR64 base-address sub-region constants identify the 16 address slots within a QM register area. ARC auxiliary and DCCM constants support driver-to-firmware access to embedded ARC processors attached to TPC, MME, and EDMA queue managers.

Compute integration is represented by the DCORE2 TPC0-5 and MME maps. TPC configuration blocks expose kernel tensor, synchronization object, kernel descriptor, and QM tensor windows. MME blocks expose QM/ARC state, control-low/control-high descriptor regions, middle controls, SBTEs, accumulator/EU windows, and writeback interfaces.

Memory and interconnect integration is represented by SRAM, HMMU, router, sync-manager, and HIF regions. SRAM bank/router/debug counters and HBW/LBW request/response stat counters support memory-path diagnostics. HMMU blocks provide MMU/STLB/scrambler windows. Router blocks expose control, H3, master-interface, address-decoder, transaction-stat, MFIFO, E2E, and debug-address windows. Sync-manager and HIF constants integrate DCORE2 synchronization and host-interface MMIO surfaces.

Security and diagnostics code can also consume the `SPECIAL`, `AXUSER`, `MSTR_IF`, `DBG_HBW`, `DBG_LBW`, and `E2E_CRDT` sub-block definitions when building protected access rules, register dumps, or error isolation coverage.

## Risks And Edge Cases

- A wrong generated base address can redirect MMIO to another hardware block. In this driver layer that can cause queue corruption, firmware access failures, false debug data, or destructive writes to unrelated Gaudi2 registers.
- The chunk is mechanically repetitive. Copy/generator drift across DCORE instances is hard to notice by review alone; for example DCORE1 and DCORE2 SRAM layouts are mostly isomorphic but intentionally offset by DCORE base address.
- The source range begins and ends mid-family. A chunk-level consumer must not infer that `DCORE1_SRAM0` or `DCORE2_EDMA0_QM` are complete from this document alone.
- Some generated section values are not identical to max offsets and are not always simple block sizes. Consumers that reinterpret `_SECTION` as a byte length without matching the generator contract can overrun or under-cover register windows.
- There are duplicate-looking macro lines in the broader generated file, including repeated special-section names around TPC CFG/QM boundaries. Because this is generated hardware data, apparent duplication should be checked against the generator and hardware database before "cleanup".
- Constants are untyped macros, so the compiler provides little domain validation. Passing a DCORE1 base where a DCORE2 table entry is expected can compile cleanly.
- Static driver arrays may store selected base macros in `u32` tables. Current addresses in this range fit in 32 bits, but the source literals are `ull`; future map growth or tooling changes should be checked for truncation risk.
- This header is included broadly through `gaudi2_regs.h`; modifying any macro can have a wide rebuild and runtime blast radius even if only one local use is obvious.

## Test Signals

Useful validation for this chunk is mostly static generation validation plus hardware bring-up:

- Build the Gaudi2 driver with `gaudi2_regs.h` included and ensure there are no duplicate macro, overflow, or initializer warnings from the changed/generated block map.
- Run a generator consistency check that every block in this range has matching `_BASE`, `_MAX_OFFSET`, and `_SECTION` definitions, except where the chunk intentionally starts or ends mid-block.
- Compare repeated DCORE1/DCORE2 SRAM and DCORE2 TPC layouts against the authoritative hardware database for expected strides and address deltas.
- Exercise Gaudi2 initialization paths that populate queue-base tables, ARC DCCM/AUX tables, and HDMA event handling for DCORE1 EDMA, DCORE2 EDMA0, DCORE2 TPC0-5, and DCORE2 MME.
- On hardware or simulation, read representative registers from each covered family: SRAM debug counters, EDMA QM/ARC/DCCM, TPC QM and CFG, HMMU, MME control/SBTE/writeback, sync-manager, HIF, router, and DCORE2 SRAM.
- Validate register dump, error reporting, and security/protection tooling against representative `SPECIAL`, `AXUSER`, `DBG_*`, `MSTR_IF`, and `E2E_CRDT` sub-blocks.
- Confirm that queue submission, firmware communication, DMA event handling, tensor processing, MME execution, synchronization-manager operation, and memory/router diagnostics still address the expected DCORE2 blocks after any regeneration.
