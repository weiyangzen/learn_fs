<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/promote_shadow_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/promote_shadow_command.cc

## Purpose
Implements `lizardfs-admin promote-shadow`, a privileged command that promotes a HA-managed shadow metadata server to master.

## Important APIs, Types, and Functions
Defines command methods. It sends `cltoma::adminBecomeMaster::build()` and validates with a subsequent `cltoma::metadataserverStatus::build(1)`.

## Control Flow, State, and Persistence
`run` validates shadow host/port, authenticates with `RegisteredAdminConnection`, requests promotion, prints the status string, exits on non-OK, then double-checks the server reports `LIZ_METADATASERVER_STATUS_MASTER`. The server-side operation changes metadata server personality and HA state.

## Dependencies and Integration Points
Depends on admin password challenge/response, HA cluster-managed master mode, `matocl::adminBecomeMaster`, and metadataserver status protocol.

## Risks and Test Signals
Risks include operational split-brain if used outside correct HA context, direct `exit(1)`, connection reuse immediately after promotion, and limited diagnostics if the final status is not master. Test signals are successful promotion, rejection on non-HA personality, bad password, status double-check failure, and cluster behavior after promotion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/promote_shadow_command.cc -->
