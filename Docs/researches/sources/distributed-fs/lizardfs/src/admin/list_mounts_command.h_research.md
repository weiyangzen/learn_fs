<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_mounts_command.h -->
# sources/distributed-fs/lizardfs/src/admin/list_mounts_command.h

## Purpose
Declares the mount/session listing command.

## Important APIs, Types, and Functions
`ListMountsCommand` overrides `name`, `supportedOptions`, `usage`, and `run`.

## Control Flow, State, and Persistence
No state is declared in the header.

## Dependencies and Integration Points
Includes the base admin command; implementation owns the local `MountEntry` protocol model.

## Risks and Test Signals
Risk is declaration drift. Build and CLI tests with `--verbose` and `--porcelain` are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_mounts_command.h -->
