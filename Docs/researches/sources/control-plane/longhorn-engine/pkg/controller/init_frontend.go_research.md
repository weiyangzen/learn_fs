<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/init_frontend.go -->
## sources/control-plane/longhorn-engine/pkg/controller/init_frontend.go

Purpose: frontend factory and timeout helper functions for controller frontends.

Important APIs/types/functions: `NewFrontend` supports `rest`, `socket`, `tgt-blockdev`, and `tgt-iscsi`. `DetermineEngineReplicaTimeout` bounds configured engine-replica timeout to 8-30 seconds with default 8 seconds. `DetermineIscsiTargetRequestTimeout` derives iSCSI request timeout as `2*engineReplicaTimeout * queueDepth + 30s`.

Control flow/state: stateless factory and calculations.

Dependencies and integration points: integrates REST/socket/TGT frontend packages and go-iscsi-helper frontend constants. Used during controller start/frontend start.

Risks: unsupported frontend strings fail at runtime. Timeout formula encodes Longhorn issue-specific behavior; changing defaults impacts I/O failure timing and iSCSI session behavior.

Test signals: unit tests should cover supported/unsupported frontend names and timeout bounds/formula.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/init_frontend.go -->
