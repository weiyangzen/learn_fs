# sources/distributed-fs/ceph-client/drivers/base/firmware_loader/sysfs_upload.h

## Purpose
`sysfs_upload.h` defines private state for sysfs firmware upload workers and progress tracking.

## Important APIs, Types, And Functions
It defines `enum fw_upload_prog` values `IDLE`, `RECEIVING`, `PREPARING`, `TRANSFERRING`, `PROGRAMMING`, and `MAX`. `struct fw_upload_priv` stores the public `fw_upload`, owner module, name, ops, mutex, worker, data pointer, remaining size, current progress, error progress, and error code.

## Control Flow, State, And Persistence
The upload implementation transitions progress from idle to receiving when sysfs data is accepted, then through preparing, transferring, and programming in the worker. Error state records the phase where an operation failed and remains readable once progress returns to idle. Remaining size is intentionally preserved on failures until the next upload begins.

## Dependencies, Integration Points, Risks, And Test Signals
The header depends on `sysfs.h` and public firmware upload ops/types. Risks include progress enum/string table drift, insufficient locking around fields, and stale data pointer lifetime if the worker/reset path changes. Test signals include enum coverage in string arrays, error reporting format, remaining-size semantics, and concurrent status/error/cancel reads while the worker updates progress.
