# sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_onetouch.h

## Purpose

`unusual_onetouch.h` lists Maxtor OneTouch devices that need an input-button side-channel initializer in addition to normal storage behavior.

## Important APIs, Types, and Functions

The file contains two `UNUSUAL_DEV()` rows for Maxtor OneTouch product IDs `0x7000` and `0x7010`. They keep device-reported subclass/protocol, use `onetouch_connect_input` as the initializer, and set no extra flags.

## Control Flow

When expanded into the usb-storage metadata table, a matching storage device receives `onetouch_connect_input` as its `initFunction`. `usb_stor_acquire_resources()` invokes that function before starting the control thread, allowing the side-button input device to be registered while storage continues through the normal protocol.

## State and Persistence Behavior

The header stores no state. The initializer may allocate input-device state and attach cleanup through `struct us_data` extra fields; storage media state is unaffected by this table alone.

## Dependencies and Integration Points

It depends on the OneTouch initializer symbol, usb-storage's initializer hook, and the unusual-device macro contract. It integrates with both USB storage and Linux input subsystems through the initializer.

## Risks and Edge Cases

Because the rows use all revisions, any product-ID reuse could register an inappropriate input device. If the initializer fails, usb-storage probe can fail before normal SCSI scanning depending on the initializer return.

## Test Signals

Attach both product IDs, verify the storage device scans normally, confirm the OneTouch input device is registered, test button events, and validate cleanup on disconnect.
