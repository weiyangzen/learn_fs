<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/save_metadata_command.h -->
# sources/distributed-fs/lizardfs/src/admin/save_metadata_command.h

## Purpose
Declares the save-metadata admin command.

## Important APIs, Types, and Functions
`SaveMetadataCommand` overrides `name`, `usage`, `supportedOptions`, and `run`.

## Control Flow, State, and Persistence
No state is defined in the header.

## Dependencies and Integration Points
Includes the base command. Implementation uses authenticated metadata persistence protocol.

## Risks and Test Signals
Risk is declaration drift and async option compatibility. Build and live save tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/save_metadata_command.h -->
