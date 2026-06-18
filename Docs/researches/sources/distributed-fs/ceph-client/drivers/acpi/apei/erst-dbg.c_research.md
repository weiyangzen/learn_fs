# sources/distributed-fs/ceph-client/drivers/acpi/apei/erst-dbg.c

## Purpose
Implements `/dev/erst_dbg`, a misc-device test and debugging interface for ACPI ERST persistent error records.

## Important APIs, Types, And Functions
File operations are `erst_dbg_open()`, `erst_dbg_release()`, `erst_dbg_read()`, `erst_dbg_write()`, and `erst_dbg_ioctl()`. Ioctls support `APEI_ERST_CLEAR_RECORD` and `APEI_ERST_GET_RECORD_COUNT`. It uses ERST core APIs such as `erst_get_record_id_begin()`, `erst_get_record_id_next()`, `erst_read_record()`, `erst_write()`, and `erst_clear()`.

## Control Flow
Open starts an ERST record-ID iteration. Reads walk record IDs, skip records removed by other users, resize a kernel buffer up to `ERST_DBG_RECORD_LEN_MAX`, and copy one complete CPER record to user space. Writes require `CAP_SYS_ADMIN`, copy a user-supplied CPER record, verify `record_length`, and persist it through ERST. Release ends the ID iterator.

## State And Persistence
`erst_dbg_buf` and length are process-shared module state guarded by `erst_dbg_mutex`. Persistent storage is owned by firmware through ERST core, not this debug layer.

## Dependencies And Integration Points
Depends on the ERST core, CPER record layout, miscdevice infrastructure, user-copy helpers, and the global `erst_disable` switch.

## Risks
Risks include user-provided malformed CPER records, records disappearing during iteration, large record memory allocation, and privileged writes modifying platform persistent error storage.

## Test Signals
Exercise open/read EOF behavior on empty stores, ioctl count/clear, write permission checks, oversized writes, dynamic buffer resizing, and read retry when a record disappears.
