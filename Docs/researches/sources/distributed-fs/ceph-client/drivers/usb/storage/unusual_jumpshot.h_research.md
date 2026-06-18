# sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_jumpshot.h

## Purpose

`unusual_jumpshot.h` contains the Lexar JumpShot table entry for the `USB_PR_JUMPSHOT` transport.

## Important APIs, Types, and Functions

The single `UNUSUAL_DEV()` row matches VID `0x05dc`, PID `0x0001`, revisions `0x0000` to `0x0001`, selects `USB_SC_SCSI`, `USB_PR_JUMPSHOT`, no initializer, and `US_FL_NEED_OVERRIDE`.

## Control Flow

The entry is expanded into the usual ignore/specialized-driver tables. `US_FL_NEED_OVERRIDE` suppresses the usb-storage notice that a subclass/protocol override might be unnecessary, indicating this override is intentional.

## State and Persistence Behavior

The header has no state. It sets probe-time matching and flags only.

## Dependencies and Integration Points

It depends on the JumpShot transport implementation and the unusual-device macro contract. It integrates with usb-storage quirk logging through `US_FL_NEED_OVERRIDE`.

## Risks and Edge Cases

The revision range is tight; unlisted firmware may miss the JumpShot path. Removing `US_FL_NEED_OVERRIDE` would not change runtime behavior but would create misleading maintenance warnings.

## Test Signals

Build JumpShot support, verify the device is ignored by generic usb-storage, confirm the JumpShot transport binds, and test card detection and block I/O.
