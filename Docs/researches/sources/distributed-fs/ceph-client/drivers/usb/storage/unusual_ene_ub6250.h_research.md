# sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_ene_ub6250.h

## Purpose

`unusual_ene_ub6250.h` contains the device table entry for ENE UB6250 card-reader hardware that has a specialized driver path and should not be claimed as plain usb-storage.

## Important APIs, Types, and Functions

The file contributes one `UNUSUAL_DEV()` row for VID `0x0cf2`, PID `0x6250`, all revisions, using device-reported subclass/protocol and no initializer or flags.

## Control Flow

`usual-tables.c` includes this file in the ignore list. Probe matching by VID/PID/bcdDevice returns `-ENXIO` from `usb_usual_ignore_device()`, allowing the specialized ENE driver to bind instead.

## State and Persistence Behavior

There is no state. The row only affects match-time binding policy.

## Dependencies and Integration Points

It depends on the `UNUSUAL_DEV` macro contract and the specialized ENE UB6250 driver existing elsewhere in the storage tree. It integrates with libusual's generic-driver ignore list.

## Risks and Edge Cases

The all-revision range assumes every UB6250 revision needs the specialized path. If future firmware becomes standards-compliant, this row may unnecessarily prevent generic binding.

## Test Signals

Compile the ignore table, attach UB6250 hardware, and confirm the generic usb-storage driver declines it while the ENE driver handles media enumeration.
