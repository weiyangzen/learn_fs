<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/metadataserver_status_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/metadataserver_status_command.cc

## Purpose
Implements `lizardfs-admin metadataserver-status`, reporting whether a metadata server is master or shadow and its metadata version.

## Important APIs, Types, and Functions
Defines command methods and static `MetadataserverStatusCommand::getStatus(ServerConnection&)`. It maps `LIZ_METADATASERVER_STATUS_MASTER`, `LIZ_METADATASERVER_STATUS_SHADOW_CONNECTED`, and `LIZ_METADATASERVER_STATUS_SHADOW_DISCONNECTED` to strings.

## Control Flow, State, and Persistence
`run` validates host/port, opens `ServerConnection`, calls `getStatus`, and prints three fields in porcelain or labeled form. `getStatus` sends `cltoma::metadataserverStatus::build(1)`, deserializes message ID, status, and metadata version, and returns an unknown fallback for unrecognized status. It is read-only.

## Dependencies and Integration Points
Depends on `protocol/cltoma.h`, `protocol/matocl.h`, `ServerConnection`, and status constants. `list-metadataservers` reuses `getStatus`.

## Risks and Test Signals
Risks include ignoring message ID, unknown statuses losing the raw numeric code, and direct server query failures propagating to list commands. Test signals are all known statuses, unknown status fallback, metadata version formatting, porcelain field separators, and reuse from shadow listing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/metadataserver_status_command.cc -->
