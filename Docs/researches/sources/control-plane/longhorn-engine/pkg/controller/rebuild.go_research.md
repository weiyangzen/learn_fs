<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/rebuild.go -->
## sources/control-plane/longhorn-engine/pkg/controller/rebuild.go

Purpose: controller-side logic for preparing and verifying replica rebuilds.

Important APIs/types/functions: `getCurrentAndRWReplica` finds target and healthy source. `VerifyRebuildReplica` compares disk chains, copies revision counter from RW source when enabled, and promotes WO to RW. `syncFile` launches a receiver on the target replica and sends a file from source. `PrepareRebuildReplica` resets target revision counter, computes snapshot/meta file sync list from source disks, removes extra target disks, and syncs head metadata under lock. `removeExtraDisks` deletes target disks not present in source. Rebuild sync limit setters/getters manage concurrency configuration.

Control flow: rebuild preparation and verification hold controller lock to block writes during critical metadata operations. Disk-chain comparison intentionally ignores head child differences. File sync uses replica clients and HTTP receiver/send path.

State and persistence: updates replica revision counters, removes extra snapshot disks, syncs metadata files, and changes in-memory replica mode.

Dependencies and integration points: depends on replica client APIs, disk utility naming, controller util `GetReplicaDisksAndHead`, and sync-agent/file-send infrastructure.

Risks: errors during verification mark target ERR even for some possibly recoverable conditions. Holding the controller lock during head metadata sync blocks I/O. Instance name is required for target validation but omitted for source as best effort. Extra disk removal is destructive for target rebuild state.

Test signals: rebuild integration tests should cover chain equality, extra disk cleanup, revision counter copy, sync list correctness, and failure-to-ERR behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/rebuild.go -->
