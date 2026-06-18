# sources/distributed-fs/ceph-client/include/linux/kmsg_dump.h

## Purpose

`kmsg_dump.h` declares the printk crash/emergency message dumper interface. It allows dumpers to register callbacks and retrieve kernel log records during panic, oops, shutdown, or other dump reasons. The source was read as a complete 126-line file.

## Important APIs, Types, and Functions

Types include `enum kmsg_dump_reason`, `struct kmsg_dump_iter`, `struct kmsg_dump_detail`, and `struct kmsg_dumper`. APIs under `CONFIG_PRINTK` include `kmsg_dump_desc()`, `kmsg_dump_get_line()`, `kmsg_dump_get_buffer()`, `kmsg_dump_rewind()`, `kmsg_dump_register()`, `kmsg_dump_unregister()`, `kmsg_dump_reason_str()`, and inline `kmsg_dump()`.

## Control Flow

Crash or shutdown paths call `kmsg_dump_desc()`, which dispatches registered dumpers. A dumper's callback uses an iterator to retrieve lines or buffers from the printk ring and may rewind as needed.

## State and Persistence Behavior

Registered dumpers live on a global list and persist until unregistered. Iterators carry sequence positions for a single dump operation. The header owns no storage.

## Dependencies and Integration Points

It integrates with printk, panic/oops handling, pstore, crash dump backends, and any platform dumper that saves logs.

## Risks and Edge Cases

Dump callbacks may run in distressed contexts and must avoid blocking or allocation assumptions. `max_reason` filters lower-priority events. Without `CONFIG_PRINTK`, registration fails with `-EINVAL` and reads return false.

## Test Signals

Pstore/kmsg dump tests, panic/oops dump path tests, iterator rewind tests, unregister tests, reason filtering tests, and `CONFIG_PRINTK=n` build coverage are useful.
