# sources/distributed-fs/openafs/src/kauth/kalog.c

## Purpose
Logs kaserver activity either to a DBM/GDBM-backed last-use database when `AUTH_DBM_LOG` is enabled or to the normal Vice text log otherwise.

## Important APIs, Types, And Functions
With DBM logging enabled, exports `kalog_Init` and `kalog_log` and uses global `kalog_db`. In all builds, `ka_log` formats text log events. It consumes operation constants from `kalog.h` and external `verbose_track`.

## Control Flow
`kalog_Init` opens a rotating server log and the DBM database. `kalog_log` builds a key from client principal, optional realm, optional service principal, and operation suffix, stores `kalog_elt {last_use,host}` with `DBM_REPLACE`, and logs through `ViceLog`. `ka_log` builds the same logical key using bounded `strl*` calls and sends it to `ViceLog`.

## State And Persistence
DBM mode persists one record per operation key in the configured KA log database, recording only the last host/time. Text mode persists through the server log file. The DBM handle is process-global.

## Dependencies And Integration Points
It is called from `kaprocs.c` after create, delete, authenticate, password-change, set-fields, unlock, and ticket operations. It depends on OpenAFS log rotation helpers and optional DBM/GDBM APIs.

## Risks And Test Signals
Risks include unbounded `strcpy`/`strcat` use in DBM mode despite fixed 512-byte `keybuf`, lack of DBM locking, and loss of event history because records are replaced. Test signals include all operation suffixes, DBM open failure fallback behavior, text log formatting, long principal/service names, and host address rendering.
