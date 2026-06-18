# sources/distributed-fs/ceph-client/arch/s390/kernel/diag/diag324.c

## Purpose
Implements `/dev/diag` ioctl support for DIAG 0x324 power information blocks. It discovers PIB availability and length, periodically refreshes readings, caches the last block, and copies it to userspace with a sequence number.

## Important APIs, Types, And Functions
Public ioctl handlers are `diag324_piblen()` and `diag324_pibbuf()`. Internal state is `struct pibdata` containing a PIB pointer, expiry time, sequence, length, and last rc. Helpers include `diag324()`, `pib_update()`, `pibwork_handler()`, and `diag324_init()`.

## Control Flow
Init checks SCLP support, queries installed subcodes, verifies subcodes 1 and 2, and records PIB length. `diag324_pibbuf()` allocates a cached PIB if needed, refreshes it on first use or after expiry, updates sequence/expiry from the firmware interval, schedules delayed cleanup, then copies the PIB and sequence to userspace. A delayed work item frees the cached PIB after it remains expired for an additional delay.

## State And Persistence
State is protected by `pibmutex` and stored in global `pibdata`. The PIB cache is volatile and freed when idle. Sequence increments on refresh.

## Dependencies And Integration Points
Depends on SCLP feature bits, DIAG 324 response formats, vmalloc, delayed work, TOD-to-ns conversion, UAPI `diag324_pib`, and `/dev/diag`.

## Risks And Edge Cases
PIB length is a 16-bit firmware value stored as bytes; invalid or zero length disables support. `-EBUSY` still allows copying the previous PIB. Copy length uses `data->pib->len`, so firmware-filled length must be sane within allocated size.

## Test Signals
Signals include ioctl tests for unsupported systems, PIB length, buffer copy, sequence increments, busy return handling, delayed cache cleanup, and firmware interval expiry behavior.
