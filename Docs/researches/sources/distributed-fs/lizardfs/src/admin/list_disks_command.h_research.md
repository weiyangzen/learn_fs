<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_disks_command.h -->
# sources/distributed-fs/lizardfs/src/admin/list_disks_command.h

## Purpose
Declares the disk listing admin command.

## Important APIs, Types, and Functions
`ListDisksCommand` overrides `name`, `supportedOptions`, `usage`, and `run`.

## Control Flow, State, and Persistence
No state is stored in the header.

## Dependencies and Integration Points
Includes only `admin/lizardfs_admin_command.h`; implementation integrates chunkserver and disk protocols.

## Risks and Test Signals
Risk is minimal declaration drift. Build and CLI dispatch tests for `list-disks` and `--verbose`/`--porcelain` are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_disks_command.h -->
