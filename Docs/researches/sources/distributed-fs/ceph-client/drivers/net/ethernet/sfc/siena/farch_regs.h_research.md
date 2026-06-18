# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/farch_regs.h

## Purpose

`farch_regs.h` is the hardware ABI map for Falcon/Siena architecture devices. It defines MMIO register offsets, table base addresses, row counts, row strides, bitfield low-bit positions, bitfield widths, and enumerated values for Falcon A, Falcon B, and Siena C revisions. Driver code uses these constants with the bitfield and IO helpers to construct register values, descriptors, event decoders, and filter table entries.

The file is declarative: it contains no executable functions and no mutable state. Its correctness is foundational for all Falcon/Siena hardware access.

## Important APIs, Types, and Constants

The naming convention encodes object type and hardware revision: `FR_*` addresses, `FRF_*` register fields, `FSE_*`/`FFE_*` enumerated values, `FSF_*` host-memory structure fields, and `FPCR_*`/`FPCRF_*` PCIe core indirect registers. Suffixes such as `AZ`, `BZ`, `CZ`, `AA`, `BB`, and `AB` describe applicable hardware revisions.

Major groups include interrupt control/status, global reset/debug/GPIO/SRAM/parity registers, event queue registers and event fields, buffer table registers, RX/TX descriptor update and pointer tables, RX/TX datapath configuration, descriptor cache controls, RSS and pacing registers, MAC/GMAC/XGMAC/MDIO/XAUI definitions, RX/TX filter tables, MSI-X tables, and host-memory layouts for driver events, RX/TX events, and RX/TX descriptors.

Pseudo-registers and aliases near the end adapt awkward hardware layouts to driver use, including high-dword descriptor doorbell aliases, combined SRAM bank/size fields, split 48-bit MAC fields, generated-event magic fields, and RX prefix constants.

## Control Flow

There is no runtime control flow in this header. Its constants are consumed by `farch.c` for queue initialization, event decoding, filter table programming, RSS synchronization, interrupt handling, and reset behavior. `io.h` also uses the descriptor update aliases to constrain page-mapped write helpers to legal register offsets.

## State and Persistence Behavior

The header has no state and performs no persistence. It defines the address and bit layout of state that lives in device registers, SRAM tables, host-memory descriptors, event queues, and MSI-X tables. Any persistence behavior is implemented by caller code that rewrites these locations after reset.

## Dependencies and Integration Points

`farch_regs.h` is included by Falcon/Siena hardware-specific C files and assumes the bitfield macros can combine each `*_LBN` and `*_WIDTH` pair into extracts and populated words. It is tightly coupled to the hardware manuals and to compile-time checks in the C code that verify register aliases, table sizes, and descriptor formats.

## Risks and Edge Cases

A wrong offset, stride, row count, field position, or width can make the driver write unrelated hardware state or decode events incorrectly. Revision-overlapping definitions require callers to use the right NIC type data. Pseudo-register aliases depend on exact hardware layouts. Event and descriptor layout mistakes can show up as packet loss, checksum misclassification, spurious resets, or queue hangs.

## Test Signals

Meaningful signals are indirect: successful compilation of all bitfield macro uses, passing register self-tests, correct queue initialization, valid RX/TX event decoding, working filter insertion/removal, RSS table round trips, interrupt test delivery, and clean reset/reprobe cycles across supported revisions.
