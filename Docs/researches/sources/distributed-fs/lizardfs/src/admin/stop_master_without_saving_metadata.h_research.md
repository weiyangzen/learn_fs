<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/stop_master_without_saving_metadata.h -->
# sources/distributed-fs/lizardfs/src/admin/stop_master_without_saving_metadata.h

## Purpose
Declares the stop-without-saving-metadata admin command.

## Important APIs, Types, and Functions
`MetadataserverStopWithoutSavingMetadataCommand` overrides `name`, `usage`, and `run`.

## Control Flow, State, and Persistence
No state is defined in the header.

## Dependencies and Integration Points
Includes `common/server_connection.h` and the base command; implementation uses authenticated admin protocol.

## Risks and Test Signals
Risk is the destructive operational semantics behind a small interface. Authenticated integration tests and recovery drills are signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/stop_master_without_saving_metadata.h -->
