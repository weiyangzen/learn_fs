<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/io_limits_status_command.h -->
# sources/distributed-fs/lizardfs/src/admin/io_limits_status_command.h

## Purpose
Declares the I/O limits status admin command and exposes protected formatting helpers useful for tests.

## Important APIs, Types, and Functions
`IoLimitsStatusCommand` overrides the base command methods and declares `printStandard`, `printPorcelain`, `printPeriod`, and `isLimitingDisabled`.

## Control Flow, State, and Persistence
No state is stored in the class. The header defines helper signatures that operate on deserialized status values.

## Dependencies and Integration Points
Includes `protocol/matocl.h` for `IoGroupAndLimit` and `admin/lizardfs_admin_command.h`.

## Risks and Test Signals
Risks are mainly ABI drift with the protocol type and protected helpers becoming de facto test API. Unit tests can directly cover disabled detection and period formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/io_limits_status_command.h -->
