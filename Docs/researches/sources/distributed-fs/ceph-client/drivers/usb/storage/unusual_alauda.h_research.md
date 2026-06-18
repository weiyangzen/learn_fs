# sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_alauda.h

## Purpose

`unusual_alauda.h` is a specialized usb-storage device table for Alauda-based card readers that are handled by the `USB_PR_ALAUDA` transport rather than by the generic mass-storage path.

## Important APIs, Types, and Functions

The file contributes two `UNUSUAL_DEV()` rows for Olympus and related Alauda devices. Each row sets `USB_SC_SCSI`, `USB_PR_ALAUDA`, and `init_alauda` with no extra flags.

## Control Flow

`usual-tables.c` includes this file in its ignore table so the standard usb-storage driver can decline these devices. The specialized Alauda subdriver includes the same macro-style data in its own match table and initializer path. At probe time, matching by VID/PID/bcdDevice chooses the Alauda-specific protocol and initializer.

## State and Persistence Behavior

The header has no state. It influences probe-time matching and initializer selection; any persistent media state belongs to the card-reader device and subdriver.

## Dependencies and Integration Points

It depends on the includer defining `UNUSUAL_DEV`, the `USB_SC_SCSI` and `USB_PR_ALAUDA` constants, and the `init_alauda` initializer symbol. Its integration point is the libusual/usb-storage split between generic and specialized drivers.

## Risks and Edge Cases

VID/PID/bcd ranges are exact compatibility gates. A firmware revision outside the listed range may bind to the wrong driver, while an overly broad range could steal unrelated devices. The standard driver ignore table must remain aligned with the specialized subdriver table.

## Test Signals

Build with Alauda support enabled, verify the entries appear in the intended USB ID table, attach matching readers, and confirm the generic driver ignores them while the Alauda transport initializes and scans media.
