<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/reload_config_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/reload_config_command.cc

## Purpose
Implements `lizardfs-admin reload-config`, a privileged synchronous request for a metadata server to reload its configuration.

## Important APIs, Types, and Functions
Defines command methods. It sends `cltoma::adminReload::build()` and expects `LIZ_MATOCL_ADMIN_RELOAD`.

## Control Flow, State, and Persistence
`run` validates host/port, authenticates, sends reload, deserializes a status byte, prints the status string, and exits nonzero on failure. Server-side state changes by rereading configuration.

## Dependencies and Integration Points
Depends on `RegisteredAdminConnection`, admin reload protocol, and LizardFS error strings.

## Risks and Test Signals
Risks include a misleading wrong-usage message saying metadataserver while usage says master, deserializing the reload response via `matocl::adminStopWithoutMetadataDump::deserialize` rather than a reload-named function, direct `exit(1)`, and operational impact of reloading live configuration. Test signals are successful reload, rejected reload, bad password, malformed response, and config change taking effect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/reload_config_command.cc -->
