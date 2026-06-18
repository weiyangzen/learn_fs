# sources/distributed-fs/ceph-client/drivers/usb/storage/transport.h

## Purpose

`transport.h` declares the usb-storage transfer and transport API shared between the core, protocol handlers, and device-specific subdrivers. It also defines the return-code taxonomy that separates USB transfer outcomes from higher-level SCSI transport outcomes.

## Important APIs, Types, and Functions

The header defines `USB_STOR_XFER_GOOD`, `USB_STOR_XFER_SHORT`, `USB_STOR_XFER_STALLED`, `USB_STOR_XFER_LONG`, and `USB_STOR_XFER_ERROR` for low-level transfers, plus `USB_STOR_TRANSPORT_GOOD`, `USB_STOR_TRANSPORT_FAILED`, `USB_STOR_TRANSPORT_NO_SENSE`, and `USB_STOR_TRANSPORT_ERROR` for command transports. It declares CBI and BOT entry points, reset helpers, transfer helpers, `usb_stor_invoke_transport()`, and `usb_stor_stop_transport()`.

## Control Flow

There is no executable logic here, but the constants define how control flows through `transport.c`: transfer helpers return `USB_STOR_XFER_*`, transport implementations convert those into `USB_STOR_TRANSPORT_*`, and `usb_stor_invoke_transport()` decides whether to autosense, complete, or reset. The comment documents that aborts are represented as generic errors and distinguished by checking dynamic flags rather than a separate return code.

## State and Persistence Behavior

The header stores no state. It exposes APIs that operate on per-device `struct us_data` and per-command `struct scsi_cmnd` state owned by the usb-storage core. There is no persistence.

## Dependencies and Integration Points

It includes block-device definitions for SCSI buffer handling and assumes `struct us_data` is declared by `usb.h` in includers. It is included by `usb.c`, `transport.c`, protocol implementations, and subdriver modules that need to submit transfers or reset devices.

## Risks and Edge Cases

The return code ordering is semantically important: transport code tests relative severity in some paths. Adding new codes or changing values could alter error handling. Callers must not confuse `USB_STOR_XFER_*` with `USB_STOR_TRANSPORT_*`; doing so would make failed commands look like dead transports or vice versa.

## Test Signals

Compile all usb-storage transports and subdrivers. Runtime tests should confirm each return class drives the expected autosense, retry, reset, and SCSI result behavior in `usb_stor_invoke_transport()`.
