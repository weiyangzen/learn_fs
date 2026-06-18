<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/io_limits_status_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/io_limits_status_command.cc

## Purpose
Implements `lizardfs-admin iolimits-status`, reporting current global I/O limiting configuration from the master.

## Important APIs, Types, and Functions
Defines `name`, `usage`, `supportedOptions`, `run`, `printStandard`, `printPorcelain`, `printPeriod`, and `isLimitingDisabled`. It consumes `IoGroupAndLimit` entries from `matocl::iolimitsStatus`.

## Control Flow, State, and Persistence
`run` validates host/port, sends `cltoma::iolimitsStatus::build(1)`, deserializes message/config IDs, period, accumulation window, subsystem, and group limits, then prints human or porcelain output. `isLimitingDisabled` treats limiting as disabled when there is no subsystem and no `unclassified` group. State is read-only and transient.

## Dependencies and Integration Points
Depends on `protocol/cltoma.h`, `protocol/matocl.h`, `ServerConnection`, iostream/iomanip formatting, and master-side I/O limit configuration.

## Risks and Test Signals
Risks include `printPeriod` labeling microsecond remainder as a three-digit millisecond fraction while using `period_us % 1000`, porcelain output omitting any disabled marker, and string-based detection of `unclassified`. Test signals are disabled, subsystem-only, group-only, and mixed configurations; period formatting boundaries; group limit conversion from bytes/s to KiB/s; and protocol version/message ID behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/io_limits_status_command.cc -->
