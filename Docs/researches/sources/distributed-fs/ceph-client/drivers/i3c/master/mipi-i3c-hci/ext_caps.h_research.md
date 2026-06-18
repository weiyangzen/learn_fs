# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/ext_caps.h

## Purpose

`ext_caps.h` exposes the extended capability parser and shared vendor ID constants for the MIPI I3C HCI driver.

## Important APIs, Types, and Functions

- `MIPI_VENDOR_NXP` defines the NXP MIPI vendor ID used by the hardware-ID and vendor-specific capability parsers.
- `i3c_hci_parse_ext_caps()` parses `hci->EXTCAPS_regs` and updates `struct i3c_hci` capability-derived fields.

## Control Flow

Core initialization calls the parser after discovering the extended capability section and before final command/I/O mode setup.

## State and Persistence Behavior

The header has no storage. The parser it declares persists vendor IDs, quirk flags, and optional capability register bases in `struct i3c_hci`.

## Dependencies and Integration Points

It depends on `struct i3c_hci` from `hci.h` and is included by `core.c` and `ext_caps.c`.

## Risks and Edge Cases

Adding vendor-specific support requires keeping IDs and parser tables synchronized. Unknown vendors must remain harmless unless a parser explicitly claims them.

## Test Signals

Build coverage should catch parser signature drift. Ext-cap tests should validate that NXP hardware ID sets `HCI_QUIRK_RAW_CCC`.
