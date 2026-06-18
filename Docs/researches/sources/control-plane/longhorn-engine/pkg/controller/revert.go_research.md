<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/revert.go -->
## sources/control-plane/longhorn-engine/pkg/controller/revert.go

Purpose: controller-side snapshot revert logic.

Important APIs/types/functions: `Revert` validates replica modes, verifies target snapshot exists and is not removed, opens clients for RW TCP replicas, refuses if frontend is up, then reverts each replica and marks failures ERR if at least one succeeds. `clientsAndSnapshot` builds replica clients and normalizes the requested snapshot name to disk name.

Control flow: revert is forbidden during rebuild (WO present), when all replicas are ERR, when frontend is up, or for non-TCP backends. It checks existence against replica disk metadata before performing revert. Actual revert operations run sequentially under controller lock.

State and persistence: persistent snapshot revert is performed by replica clients. Controller may mark failed replicas ERR.

Dependencies and integration points: depends on replica client API, disk utility naming, `GetReplicaDisksAndHead`, and frontend state.

Risks: only TCP backends support revert here; file backend cannot. Sequential revert under lock can block other operations. If some replicas fail and one succeeds, the volume proceeds degraded. Caller must ensure frontend shutdown before invoking.

Test signals: integration tests should cover frontend-up rejection, WO rejection, missing/removed snapshot rejection, partial replica failure, and non-TCP backend rejection.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/revert.go -->
