# sources/distributed-fs/ceph-client/drivers/usb/storage/usb.h

## Purpose

`usb.h` is the central header for the classic usb-storage core. It defines the unusual-device metadata shape, dynamic state flags, `struct us_data`, common callback typedefs, host conversion helpers, exported probe/PM/disconnect APIs, and the module registration macro used by storage subdrivers.

## Important APIs, Types, and Functions

`struct us_unusual_dev` stores short inquiry names, protocol override, transport override, and initializer callback. `struct us_data` holds all per-device runtime state: USB device/interface, quirk flags, dynamic flags, pipes, protocol/transport names and function pointers, current SCSI command, tag, coherent I/O buffer, current URB/SG request, control thread, completions, waitqueue, delayed scan work, subdriver private data/destructor, PM hook, and capacity-hack counters. Typedefs include `trans_cmnd`, `trans_reset`, `proto_cmnd`, `extra_data_destructor`, and `pm_hook`.

## Control Flow

The header has no executable flow, but its definitions drive the driver lifecycle. Probe allocates `struct us_data` as SCSI host private data, transport/protocol setup fills function pointers, the command thread consumes `us->srb`, transfer code uses `current_urb` and `current_sg`, and disconnect/PM/reset paths use the exported functions. `module_usb_stor_driver()` wraps module init/exit by initializing a SCSI host template and registering/deregistering a USB driver.

## State and Persistence Behavior

All state defined here is in memory and scoped to a USB storage device or module. Dynamic flags record URB active, SG active, aborting, disconnecting, resetting, timed out, scan pending, redo READ(10), and prior READ(10) success. There is no filesystem persistence.

## Dependencies and Integration Points

It depends on Linux USB, usb usual quirks, block layer, completions, mutexes, workqueues, and SCSI host APIs. It is included by the core, transports, protocol handlers, and subdrivers and is the main ABI inside the usb-storage subsystem.

## Risks and Edge Cases

`struct us_data` is shared by many asynchronous paths, so lock/flag contracts documented in C files must be respected by any new subdriver. The small coherent `US_IOBUF_SIZE` is sized for known control/BOT/Freecom needs; new protocols must not overrun it. `scsi_lock` and `scsi_unlock` macros directly use host spinlocks and should not be mixed casually with sleeping operations.

## Test Signals

Compile all usb-storage subdrivers, verify host/private-data conversion, exercise module registration, and use lockdep/runtime tests around abort, reset, scan, PM, and subdriver init/destructor paths.
