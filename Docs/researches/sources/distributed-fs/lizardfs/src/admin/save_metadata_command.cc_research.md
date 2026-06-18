<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/save_metadata_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/save_metadata_command.cc

## Purpose
Implements `lizardfs-admin save-metadata`, requesting a metadata server to save current metadata to `metadata.mfs`.

## Important APIs, Types, and Functions
Defines command methods and supports `--async`. It sends `cltoma::adminSaveMetadata::build(async)` and deserializes `matocl::adminSaveMetadata`.

## Control Flow, State, and Persistence
`run` validates host/port, determines async mode, authenticates, sends the request, prints status, and exits nonzero on failure. In synchronous mode the server is expected to report completion status; in async mode it only reports task start. Server-side metadata persistence is the core effect.

## Dependencies and Integration Points
Depends on admin authentication, save-metadata protocol, and LizardFS error strings. It interacts with task management because async saves may create background work visible to list/stop tasks.

## Risks and Test Signals
Risks include direct `exit(1)`, operational load or failure while saving metadata, async semantics depending on server task state, and no porcelain/status-code output. Test signals are sync success/failure, async start when no save is running, async failure when already in progress, bad password, and actual metadata file creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/save_metadata_command.cc -->
