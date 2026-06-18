# sources/distributed-fs/openafs/src/kauth/kaauxdb.c

## Purpose
Maintains the auxiliary authentication database file `auxdb`, which stores failed-authentication counters and last-failure timestamps outside the main Ubik KA database.

## Important APIs, Types, And Functions
Functions are `kaux_opendb`, `kaux_closedb`, `kaux_read`, `kaux_write`, `kaux_inc`, and `kaux_islocked`. Static state is the process-wide file descriptor `fd`. The record key is derived from a main-database `kaentry` offset and the fixed `ENTRYSIZE`/`kaheader` layout.

## Control Flow
`kaux_opendb` builds `<path>/auxdb` by appending `auxdb` to the provided path and opens it read/write with mode 0600. `kaux_read` and `kaux_write` translate a main-database entry offset into an auxiliary file offset and read or write `{nfailures,lasttime}`. `kaux_inc` expires old failures based on locktime and increments the counter. `kaux_islocked` scales allowed attempts across Ubik servers, gives the sync site the remainder, and returns 0 for unlocked, -1 for indefinite/fully locked, or an unlock timestamp.

## State And Persistence
Persistent state lives in the sidecar `auxdb` file. It is not replicated by Ubik and is maintained independently on each server. Runtime state is only the open descriptor.

## Dependencies And Integration Points
It depends on Ubik beacon state (`ubeacon_Debug`, `ubeacon_AmSyncSite`) and kauth database layout from `kaserver.h`. `kaprocs.c` calls it for failed-login lockout checks, increments, unlock, lock-status, and cleanup when deleting users.

## Risks And Test Signals
Risks include non-replicated lockout counters, no explicit file locking, host-endian on-disk integers, path concatenation assumptions, no reset of `fd` after close, and offset coupling to fixed `kaentry` positions. Test signals include failed-login accumulation, lock expiry, sync-site remainder behavior, delete/unlock counter reset, no-limit attempts behavior, and operation when `auxdb` is missing or truncated.
