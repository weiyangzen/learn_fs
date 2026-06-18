<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/info_command.h -->
# sources/distributed-fs/lizardfs/src/admin/info_command.h

## Purpose
Declares the `InfoCommand` admin command.

## Important APIs, Types, and Functions
`InfoCommand` derives from `LizardFsProbeCommand` and overrides `name`, `supportedOptions`, `usage`, and `run`.

## Control Flow, State, and Persistence
The header carries no state or logic. It provides the command contract consumed by `main.cc`.

## Dependencies and Integration Points
Includes `admin/lizardfs_admin_command.h`; implementation supplies master protocol integration.

## Risks and Test Signals
Risk is declaration/implementation drift. Build and CLI dispatch tests for the `info` command are sufficient signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/info_command.h -->
