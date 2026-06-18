# sources/distributed-fs/beegfs/common/source/common/storage/StorageErrors.cpp

## Purpose
Defines the `FhgfsOpsErr` string/system-error mapping and conversion helpers.

## Important APIs, Types, And Functions
`__FHGFSOPS_ERRLIST`, `operator<<`, `FhgfsOpsErrTk::toSysErr()`, and `FhgfsOpsErrTk::fromSysErr()` are implemented.

## Control Flow
Conversions index the table when the enum value is in range. Unknown values log a critical error and backtrace; stream output prints an unknown marker, while `toSysErr()` falls back to `EPERM`. `fromSysErr()` returns the first table entry with a matching system errno, otherwise internal error.

## State, Persistence, And Dependencies
The mapping table is static const process data. Depends on POSIX errno values, logging, and Boost ios state saver.

## Integration Points
Used across storage, metadata, network response handling, and syscall translation paths.

## Risks
The mapping from sys errno back to BeeGFS error is not one-to-one and first-match based. Table order must remain synchronized with the enum. A former error slot remains as "Removed" with code 999.

## Test Signals
Verify every enum maps in range, table size matches enum, unknown-value logging/fallback, `fromSysErr()` expected first matches, and stream formatting.
