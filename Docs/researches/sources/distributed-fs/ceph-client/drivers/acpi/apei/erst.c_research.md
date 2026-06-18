# sources/distributed-fs/ceph-client/drivers/acpi/apei/erst.c

## Purpose
Implements ACPI APEI Error Record Serialization Table support. It exposes firmware persistent error storage as kernel ERST APIs and as a pstore backend for panic/dmesg/MCE data.

## Important APIs, Types, And Functions
Exports `erst_get_record_count()`, `erst_get_record_id_begin()`, `erst_get_record_id_next()`, `erst_get_record_id_end()`, `erst_write()`, `erst_read()`, `erst_read_record()`, and `erst_clear()`. `erst_ins_type[]` implements ERST-specific APEI instructions including variable operations, stalls, goto, base-address setup, and `MOVE_DATA`. `struct erst_erange` holds the firmware log address range, and `struct erst_record_id_cache` caches record IDs across iteration.

## Control Flow
`erst_init()` validates the ERST table, reserves and maps ERST resources, obtains the error log range, maps the range, and registers pstore if a backing buffer can be allocated. Read, write, and clear operations serialize through `erst_lock`, program ERST command inputs, execute firmware operations, poll busy/status, and translate firmware statuses to errno. pstore wraps payloads in CPER records and filters reads by the pstore creator GUID.

## State And Persistence
Persistent records live in firmware storage behind the ERST range. Kernel state includes the table pointer, mapped error range, pstore buffer, global disable flag, and a mutex/refcount-protected record-ID cache. `raw_spinlock_t erst_lock` protects interpreter and error range access, including contexts where sleeping is not acceptable.

## Dependencies And Integration Points
Integrates ACPI table access, APEI executor/resource helpers, CPER, pstore, vmalloc/kmalloc memory, NMI watchdog touch, and exported ERST APIs consumed by `erst-dbg.c`.

## Risks
Risks include firmware hangs, slow ERST timing interpretation, unsupported NVRAM ranges, `MOVE_DATA` in interrupt context, record-ID cache staleness, pstore buffer sizing, and lock constraints around panic/NMI paths.

## Test Signals
Check ERST table validation, log range mapping, pstore registration, read/write/clear status translation, record-ID iteration under deletion, unsupported NVRAM behavior, timeout warnings, and pstore CPER type decoding.
