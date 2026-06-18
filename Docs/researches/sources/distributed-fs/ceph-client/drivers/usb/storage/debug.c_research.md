# sources/distributed-fs/ceph-client/drivers/usb/storage/debug.c

## Purpose

`debug.c` implements verbose debug output helpers for the USB Mass Storage core when `CONFIG_USB_STORAGE_DEBUG` is enabled. It prints readable SCSI command names, command bytes, and sense descriptions.

## Important APIs, Types, and Functions

`usb_stor_show_command()` maps many SCSI and ATAPI opcodes to strings and prints up to 16 command bytes. `usb_stor_show_sense()` uses SCSI library helpers to format sense key, ASC, and ASCQ. `usb_stor_dbg()` is the exported variadic debug printer using `dev_vprintk_emit(LOGLEVEL_DEBUG, &us->pusb_dev->dev, ...)`. `EXPORT_SYMBOL_GPL(usb_stor_dbg)` exposes the debug printer inside the USB_STORAGE namespace context.

## Control Flow

Debug callers invoke the helpers around command dispatch, error handling, or protocol-specific paths. The functions perform table/switch formatting and emit kernel debug logs; they do not affect transport results.

## State and Persistence Behavior

The file stores no state. Output persists only as kernel log messages subject to normal log buffering and dynamic log-level handling.

## Dependencies and Integration Points

It depends on SCSI opcode definitions, SCSI debug formatting helpers, the usb-storage `struct us_data`, and the declarations/macros in `debug.h`. It integrates with core and subdriver `usb_stor_dbg()`/`US_DEBUG()` call sites.

## Risks and Test Signals

Risks are low for device behavior because code is diagnostic, but command-name tables can become stale and debug logging can be noisy or reveal command data. Test signals include successful builds with `CONFIG_USB_STORAGE_DEBUG=y`, representative opcode name formatting, sense formatting for known and unknown ASC/ASCQ values, and vendor modules resolving `usb_stor_dbg`.
