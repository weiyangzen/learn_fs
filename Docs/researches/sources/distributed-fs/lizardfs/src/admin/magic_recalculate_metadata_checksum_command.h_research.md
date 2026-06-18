<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/magic_recalculate_metadata_checksum_command.h -->
# sources/distributed-fs/lizardfs/src/admin/magic_recalculate_metadata_checksum_command.h

## Purpose
Declares the undocumented metadata checksum recalculation command.

## Important APIs, Types, and Functions
`MagicRecalculateMetadataChecksumCommand` overrides `name`, `usage`, `supportedOptions`, and `run`.

## Control Flow, State, and Persistence
The header has no state.

## Dependencies and Integration Points
Includes the base admin command. Implementation integrates authenticated admin protocol.

## Risks and Test Signals
Risk is declaration drift and the command being operationally powerful despite minimal type surface. Build and authenticated protocol tests are signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/magic_recalculate_metadata_checksum_command.h -->
