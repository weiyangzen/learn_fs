# sources/distributed-fs/ceph-client/drivers/misc/mei/bus-fixup.c

## Purpose
`bus-fixup.c` applies policy and firmware-specific setup before MEI firmware clients are exposed on the MEI bus. It blacklists, whitelists, renames, or initializes special clients.

## Important APIs, Types, and Functions
Important hooks are `number_of_connections()`, `blacklist()`, `whitelist()`, `mei_mkhi_fix()`, `mei_gsc_mkhi_ver()`, `mei_gsc_mkhi_fix_ver()`, `mei_wd()`, `mei_nfc()`, `vt_support()`, `pxp_is_ready()`, and `mei_cl_bus_dev_fixup()`. It defines UUIDs for NFC, watchdog, MKHI, IGSC MKHI, HDCP, PAVP, and wildcard matching.

## Control Flow
`mei_cl_bus_dev_fixup()` iterates the `mei_fixups[]` table and runs hooks whose UUID matches the client or wildcard. Generic hooks reject multi-connection clients and enable vtag clients. MKHI hooks enable a client temporarily to fetch firmware version, report OS version, or send GSC memory-ready. NFC connects to an info GUID, reads radio version, derives a radio name, and updates the client device name. PXP exposure depends on bus `pxp_mode`.

## State and Persistence
It mutates `cldev->do_match`, `cldev->name`, watchdog protocol version, `bus->fw_ver[]`, `bus->fw_ver_received`, and `bus->pxp_mode`. No filesystem persistence.

## Dependencies and Integration Points
Uses MEI client send/recv/connect helpers, MKHI message formats, NFC message protocol, PCI IDs for watchdog version quirks, and MEI bus enumeration in `bus.c`.

## Risks
Fixups run during bus enumeration, so blocking firmware requests can delay device exposure. Incorrect UUID policy can hide valid clients or expose unsafe ones. NFC lock/unlock sequencing intentionally drops `device_lock` around I/O.

## Test Signals
Signals include filtered multi-connection clients, hidden NFC info client, renamed NFC HCI device, watchdog protocol correction on selected PCI IDs, populated firmware version fields, successful OS-version and GSC memory-ready commands, vtag-client matching, and PXP client exposure only when ready/default.
