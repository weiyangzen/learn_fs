# sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_freecom.h

## Purpose

`unusual_freecom.h` maps the Freecom USB-ATAPI bridge to its specialized Freecom transport.

## Important APIs, Types, and Functions

The file contains one `UNUSUAL_DEV()` row for VID `0x07ab`, PID `0xfc01`, all revisions. It selects `USB_SC_QIC`, `USB_PR_FREECOM`, and `init_freecom`.

## Control Flow

The row is expanded into ignore or specialized subdriver tables. When matched by the Freecom subdriver, probe uses the QIC subclass, Freecom transport, and initializer before SCSI scanning.

## State and Persistence Behavior

The header has no state. It controls transport selection and initializer invocation at probe time.

## Dependencies and Integration Points

It depends on `init_freecom`, Freecom transport support, and the `UNUSUAL_DEV` macro. It integrates with usb-storage's subdriver split and SCSI command routing for the device.

## Risks and Edge Cases

An all-revision range may capture devices that do not need the Freecom path. The initializer and transport must match the protocol override or commands may be padded/transferred incorrectly.

## Test Signals

Build Freecom support, verify USB ID matching, attach the bridge, and test media inquiry, read/write, reset, and disconnect through the specialized transport.
