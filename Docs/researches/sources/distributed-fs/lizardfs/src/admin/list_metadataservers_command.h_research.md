<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_metadataservers_command.h -->
# sources/distributed-fs/lizardfs/src/admin/list_metadataservers_command.h

## Purpose
Declares the metadata server listing command.

## Important APIs, Types, and Functions
`ListMetadataserversCommand` overrides `name`, `usage`, `supportedOptions`, and `run`.

## Control Flow, State, and Persistence
No runtime state is defined in the header.

## Dependencies and Integration Points
Includes the base admin command; implementation integrates metadata server list/status protocols.

## Risks and Test Signals
Risk is limited to declaration drift. Build tests and live cluster CLI tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_metadataservers_command.h -->
