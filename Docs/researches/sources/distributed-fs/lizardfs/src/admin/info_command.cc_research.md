<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/info_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/info_command.cc

## Purpose
Implements `lizardfs-admin info`, printing high-level master statistics for a LizardFS installation.

## Important APIs, Types, and Functions
Defines `InfoCommand::name`, `supportedOptions`, `usage`, and `run`. It sends legacy packet `CLTOMA_INFO`, expects `MATOCL_INFO`, and deserializes `LizardFsStatistics`.

## Control Flow, State, and Persistence
`run` validates host/port, opens `ServerConnection`, serializes a MooseFS packet, deserializes the statistics payload, and prints either a space-separated porcelain line or a human-readable report. No state is persisted; it is a read-only snapshot.

## Dependencies and Integration Points
Depends on `human_readable_format`, `lizardfs_statistics`, `lizardfs_version`, `server_connection`, and packet serialization helpers. It integrates with master info protocol compatibility inherited from MooseFS.

## Risks and Test Signals
Risks include duplicated `chunkCopies` as deprecated regular copies, porcelain output lacking field names/versioning, and protocol structure drift. Test signals are master info response decoding, human-readable IEC/SI formatting, porcelain field count stability, zero/large statistics, and connection error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/info_command.cc -->
