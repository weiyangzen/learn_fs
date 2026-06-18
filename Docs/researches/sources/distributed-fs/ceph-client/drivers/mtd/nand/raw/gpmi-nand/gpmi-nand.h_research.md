# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/gpmi-nand/gpmi-nand.h

## Purpose
Declares the central data structures and SoC predicates for the GPMI NAND driver. It captures hardware resources, BCH geometry, boot ROM geometry, SoC capabilities, timing state, DMA transfer bookkeeping, and top-level driver state shared by `gpmi-nand.c` and register helper headers.

## Important APIs, Types, And Functions
`struct resources` stores mapped GPMI/BCH registers, DMA channel range metadata, and up to five clocks. `struct bch_geometry` describes GF length, ECC strength, BCH page size, metadata, chunk sizes/count, payload, auxiliary/status offsets, bad-block-marker bit position, and metadata ECC flag. `struct boot_rom_geometry` stores ROM search strides. `enum gpmi_type` and `struct gpmi_devdata` distinguish SoC family, max BCH strength, clock names, EDO support, and delay thresholds. `struct gpmi_nfc_hardware_timing`, `struct gpmi_transfer`, and `struct gpmi_nand_data` hold timing, DMA, NAND, BCH, and buffer state. Macros such as `GPMI_IS_MX6()` and `GPMI_IS_MXS()` provide SoC classification.

## Control Flow
The header has no executable flow, but its structures define the state transitions in `gpmi-nand.c`: resource acquisition fills `resources`, geometry setup fills `bch_geometry`, timing negotiation fills `hw`, DMA chain construction uses `transfers`, and probe/attach maintain the embedded NAND controller and chip.

## State And Persistence
All fields are runtime driver state except that `bch_geometry`, `swap_block_mark`, and boot ROM geometry determine persistent on-flash page/OOB interpretation. Changing these definitions or field meanings can break layout compatibility.

## Dependencies And Integration Points
Depends on raw NAND, platform device, DMA mapping, and DMAengine headers. Register helper headers rely on the SoC predicate macros. The C file relies on these structures for all driver subsystems: clocks, PM, DMA, ECC, bad-block handling, and MTD registration.

## Risks
This header centralizes ABI-like internal contracts. Incorrect geometry fields, stale clock limits, or wrong SoC predicates can produce invalid BCH layout registers. `GPMI_MAX_TRANSFERS` and `DMA_CHANS` constrain operation construction and resource assumptions.

## Test Signals
Compile coverage validates structure and macro consistency. Runtime validation comes from matching devdata to OF compatibles, successful geometry computation, correct register field generation from predicates, and DMA operation construction within transfer limits.
