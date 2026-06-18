# sources/distributed-fs/openafs/src/kauth/kdb.c

## Purpose
Implements `kdb`, a diagnostic dumper for the KA DBM activity-log database when `AUTH_DBM_LOG` is enabled. In non-DBM builds it reports that the tool is unsupported.

## Important APIs, Types, And Functions
DBM builds define `cmdproc` and `main`, use global `dbmfile`, and read `kalog_elt` records from a DBM/GDBM file. Non-DBM builds define a simple `main(void)`.

## Control Flow
`main` builds a command syntax with optional `-dbmfile`, `-key`, `-long`, and `-numeric`. `cmdproc` opens the DBM file, either enumerates all keys or fetches specified keys, optionally reads values and prints last host/time information, closes the database, and returns success. Non-DBM mode prints `kdb not supported` and exits 1.

## State And Persistence
The tool reads but does not modify the KA activity-log DBM file. It keeps only local iteration state.

## Dependencies And Integration Points
It depends on `kalog.h` for DBM compatibility macros and `kalog_elt` layout, plus OpenAFS command and host utility helpers. It is a companion to `kalog.c` DBM mode.

## Risks And Test Signals
Risks include DBM backend portability, corrupted record handling, key enumeration semantics differing between NDBM and GDBM, and host formatting differences. Test signals include dumping all keys, fetching individual keys, long and numeric output, missing key behavior, corrupted value-size detection, and non-DBM build behavior.
