# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/gpmi-nand/gpmi-regs.h

## Purpose
Defines GPMI NAND controller register offsets and bitfield helpers used to build PIO words and timing/control register values. It covers command modes, chip select, address space selection, transfer counts, ECC control, payload/auxiliary pointers, controller mode bits, timing registers, busy timeout, data window, and ready/busy status/debug bits.

## Important APIs, Types, And Functions
The file is macro-only. Important groups are `HW_GPMI_CTRL0*`, `BF_GPMI_CTRL0_*()` command-chain fields, `HW_GPMI_ECCCTRL*` and ECC buffer masks, `HW_GPMI_PAYLOAD`, `HW_GPMI_AUXILIARY`, `HW_GPMI_CTRL1*` mode/timing-delay bits, `HW_GPMI_TIMING0/1`, and SoC-specific ready bits in `HW_GPMI_STAT` and `HW_GPMI_DEBUG`. `BF_GPMI_CTRL0_CS(v, x)` branches on `GPMI_IS_MX23()` because chip-select field width differs.

## Control Flow
No code executes here. `gpmi-nand.c` uses the macros when resetting and configuring GPMI, applying timings, building DMA PIO descriptors for command/address/data/wait operations, enabling BCH encode/decode, and selecting NAND mode, write-protect behavior, BCH mode, and ready/busy routing.

## State And Persistence
The header stores no state, but its constants describe volatile hardware state. Some register settings indirectly affect persistent flash content because ECC encode/decode mode, transfer count, and payload/auxiliary placement define how NAND pages are read or programmed.

## Dependencies And Integration Points
Depends on GPMI SoC predicate macros from `gpmi-nand.h`. Integrated with `gpmi_init()`, `gpmi_nfc_apply_timings()`, `gpmi_chain_command()`, `gpmi_chain_wait_ready()`, `gpmi_chain_data_read()`, and `gpmi_chain_data_write()`.

## Risks
Incorrect field masks can corrupt DMA PIO commands or select the wrong chip, address latch, transfer length, or ECC mode. `BF_GPMI_CTRL0_LOCK_CS()` currently expands to zero despite comments about SoC differences, so any future reliance on lock-CS behavior needs hardware validation. Timing fields are tightly coupled to ONFI timing calculations.

## Test Signals
Generated PIO words should be inspected for representative command/address/data/wait operations on MX23 and MX28-plus variants. Hardware tests should verify ready/busy waits, ECC encode/decode transfers, timing register application, data transfer lengths, and NAND mode/write-protect configuration after reset and resume.
