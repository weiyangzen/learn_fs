# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/ext_caps.c

## Purpose

`ext_caps.c` parses the MIPI I3C HCI extended capability area. It records vendor identity, validates master-mode support, logs optional transfer mode/rate capabilities, captures base pointers for auto-command and debug sections, handles known standard capability IDs, and supports a small vendor-specific parser table.

## Important APIs, Types, and Functions

- Capability header fields `CAP_HEADER_LENGTH` and `CAP_HEADER_ID` drive table walking.
- Standard parsers include hardware ID, master config, multi-bus, transfer modes, transfer rates, auto-command, debug, scheduled command, non-current master, CCC response config, global DAT, and multilane capability handlers.
- `struct hci_ext_caps` and `EXT_CAP()` define standard capability metadata and minimum lengths.
- `hci_extcap_hardware_id()` stores vendor MIPI/version/product IDs and sets the raw CCC quirk for NXP.
- `hci_extcap_vendor_specific()` dispatches vendor capabilities, currently NXP cap `0xc0`.
- `i3c_hci_parse_ext_caps()` is the exported parser called by core initialization.

## Control Flow

The parser starts at `hci->EXTCAPS_regs` and walks until a zero ID/length or a fixed 0x1000-byte guard limit. Each header is decoded and checked so `curr_cap + cap_length * 4` stays under the guard. Vendor IDs `0xc0..0xcf` are matched against the vendor-specific table. Standard IDs are looked up in `ext_capabilities`; unknown capabilities are ignored with debug logging, too-short known capabilities fail with `-EINVAL`, and recognized parsers may record state or reject unsupported modes.

## State and Persistence Behavior

The parser persists vendor identity in `hci->vendor_mipi_id`, `vendor_version_id`, and `vendor_product_id`, may set `hci->quirks`, and stores MMIO base pointers in `AUTOCMD_regs`, `DEBUG_regs`, and `vendor_data`. Most other capabilities are only logged.

## Dependencies and Integration Points

It depends on HCI core state, `ext_caps.h` vendor IDs, transfer mode/rate bit definitions, MMIO reads/writes, and device logging. Core calls it before selecting descriptors and I/O mode so quirks can affect initialization.

## Risks and Edge Cases

The 0x1000-byte limit is arbitrary. Some parsers are placeholders and do not enforce all advertised capability constraints. The NXP vendor parser writes `0xdeadbeef` to a vendor register to reset an FPGA, which is highly device-specific. Operation mode accepts any mode with bit 0 set and rejects target-only operation.

## Test Signals

Feed synthetic ext-cap blocks with zero terminators, unknown IDs, too-short lengths, vendor IDs before/after hardware ID, master-only and target-only modes, rate/mode tables, and bounds at the 0x1000 limit. Hardware tests should verify NXP raw CCC quirk behavior and auto-command/debug base capture.
