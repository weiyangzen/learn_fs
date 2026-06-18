# sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_isd200.h

## Purpose

`unusual_isd200.h` lists ISD200-based USB-to-ATA bridges that require the ISD200 initialization/protocol path.

## Important APIs, Types, and Functions

The file contributes six `UNUSUAL_DEV()` entries for Sony, In-System/ISD, and related bridges. Rows select `USB_SC_ISD200`, `USB_PR_BULK`, `isd200_Initialization`, and usually no extra flags.

## Control Flow

Macro expansion routes matching devices away from generic usb-storage and into the ISD200 subdriver. The initializer runs before the usb-storage control thread starts, allowing ATA bridge setup before SCSI scanning.

## State and Persistence Behavior

No state is stored in the header. The rows influence in-memory protocol and initializer fields in `struct us_data`; bridge state is programmed by the initializer.

## Dependencies and Integration Points

It depends on ISD200 subclass support and `isd200_Initialization`. It integrates with the usb-storage unusual-device infrastructure, USB ID matching, and SCSI scan setup.

## Risks and Edge Cases

All listed rows use a narrow bcd range (`0x0100` to `0x0110`). Devices outside that range may not bind to the specialized path even if they need it. Conversely, broadening the range without hardware evidence could affect unrelated bridge firmware.

## Test Signals

Compile with ISD200 enabled, attach represented bridges, verify initializer execution, check ATA identify/translation behavior, and exercise reset plus media read/write paths.
