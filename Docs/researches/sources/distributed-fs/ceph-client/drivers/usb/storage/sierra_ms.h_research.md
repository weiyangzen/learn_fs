# sources/distributed-fs/ceph-client/drivers/usb/storage/sierra_ms.h

## Purpose

`sierra_ms.h` is the tiny declaration header for the Sierra USB mass-storage initializer used by the generic `usb-storage` probe path when matching Sierra modem/storage devices. It lets `usb.c` include the initializer without depending on the implementation body.

## Important APIs, Types, and Functions

The only API is `int sierra_ms_init(struct us_data *us)`, which receives the per-device `struct us_data` allocated by the usb-storage core. The header relies on `struct us_data` being visible or forward-declared by the including translation unit.

## Control Flow

There is no executable control flow in this header. `usb.c` includes it before expanding `unusual_devs.h`; matched device entries can then name `sierra_ms_init` as an `initFunction`, and `usb_stor_acquire_resources()` calls that initializer before the usb-storage control thread is started.

## State and Persistence Behavior

The header stores no state. Any state changes happen in the initializer implementation through `struct us_data`, device transport hooks, or extra destructor/private data attached by the subdriver. There is no filesystem persistence.

## Dependencies and Integration Points

It integrates with the usb-storage unusual-device table and the standard probe sequence in `usb.c`. It depends on the mass-storage core's `struct us_data` contract and on the implementation being linked when Sierra support is built.

## Risks and Edge Cases

Because this is only a prototype, the risk is interface drift: a signature mismatch between the initializer implementation and this header would break builds, and missing inclusion would break `unusual_devs.h` entries that name the initializer. Runtime risks belong to the initializer body.

## Test Signals

Compile coverage with Sierra mass-storage support enabled is the primary signal. Runtime validation should attach a Sierra device that matches the unusual table and confirm the initializer is invoked before SCSI scanning begins.
