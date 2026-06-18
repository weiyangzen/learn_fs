<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/magic_recalculate_metadata_checksum_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/magic_recalculate_metadata_checksum_command.cc

## Purpose
Implements undocumented `magic-recalculate-metadata-checksum`, a privileged command that asks a metadata server to recalculate metadata checksum, synchronously or asynchronously.

## Important APIs, Types, and Functions
Defines command methods and supports `--async` and valued `--timeout=`. It sends `cltoma::adminRecalculateMetadataChecksum::build(async)` over `RegisteredAdminConnection`.

## Control Flow, State, and Persistence
`run` reads `--async`, computes timeout in milliseconds from seconds, creates an authenticated admin connection, sends the recalculation request, deserializes status, prints the error string to stderr, and exits nonzero on non-OK status. The operation can change server-side metadata checksum state or schedule work, but this client persists no local state.

## Dependencies and Integration Points
Depends on admin password challenge/response, `ServerConnection::kDefaultTimeout`, and master/metadataserver admin protocol. `main.cc` hides `magic-*` commands from the generic help list.

## Risks and Test Signals
Risks include no argument-count validation before `options.argument(0/1)`, timeout multiplication overflow for large values, direct `exit(1)`, and operational sensitivity of recalculating metadata checksums. Test signals are sync/async success, bad password, timeout behavior, invalid/missing arguments, server rejection status, and help hiding while still allowing explicit command usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/magic_recalculate_metadata_checksum_command.cc -->
