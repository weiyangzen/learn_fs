<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/stop_master_without_saving_metadata.cc -->
# sources/distributed-fs/lizardfs/src/admin/stop_master_without_saving_metadata.cc

## Purpose
Implements `lizardfs-admin stop-master-without-saving-metadata`, a privileged fast-stop command that intentionally avoids saving metadata first.

## Important APIs, Types, and Functions
Defines methods for `MetadataserverStopWithoutSavingMetadataCommand`. It sends `cltoma::adminStopWithoutMetadataDump::build()` and deserializes status.

## Control Flow, State, and Persistence
`run` validates metadataserver host/port, authenticates, requests stop without metadata dump, prints status, and exits nonzero on failure. The server-side effect is stopping the metadata server without writing a fresh `metadata.mfs`.

## Dependencies and Integration Points
Depends on admin authentication, stop-without-metadata-dump protocol, and LizardFS error strings. It is related to HA migration and emergency operations.

## Risks and Test Signals
Risks are high: unsaved metadata may be lost if no current changelog/metalogger recovery path exists, and direct `exit(1)` bypasses main handling. Test signals are controlled stop in a test cluster, recovery from changelog/metalogger, bad password, server rejection, and behavior across master/shadow personalities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/stop_master_without_saving_metadata.cc -->
