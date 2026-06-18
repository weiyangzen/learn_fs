# sources/distributed-fs/openafs/src/util/ktime.h

Purpose: Defines the data structures and mask constants shared by absolute, relative, and periodic time utilities.

Important types and constants: `struct ktime_date` holds mask, year, month, day, hour, min, and sec. `struct ktime` holds periodic mask, time-of-day, and weekday. Defines `KTIMEDATE_*` field and special flags, `KTIMEDATE_NEVERDATE`, `KTIME_*` field/special flags, `KTIME_NEVERTIME`, and `KTIME_NOWTIME`.

Control flow and state: Header-only type contract; runtime logic is in `ktime.c` and `kreltime.c`.

Dependencies and integration: Requires AFS integer typedefs to be available. Included by date parsers, relative expiration logic, and command modules that need stable time encoding.

Risks and test signals: Comments note that `KTIMEDATE_NEVERDATE` differs from the value used by periodic parsing, so callers must not mix absolute and periodic sentinel values blindly. Field ranges are documented loosely but enforced in implementation. Tests should verify mask interpretation and sentinel handling.
