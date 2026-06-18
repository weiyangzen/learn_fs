<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/util.go -->
## sources/control-plane/longhorn-engine/pkg/controller/util.go

Purpose: helper to query replica disk chain information and identify the current head.

Important APIs/types/functions: `GetReplicaDisksAndHead` opens a replica client, gets replica metadata, requires a non-empty chain, sets `head` to `Chain[0]`, and returns all disks except the head and backing file.

Control flow: client creation and RPC call errors are wrapped with address context. Client close errors are logged.

State and persistence: read-only metadata query; no persistence.

Dependencies and integration points: used by rebuild and revert logic. Depends on replica client and `types.DiskInfo`.

Risks: assumes `Chain[0]` is current head. Filtering excludes backing file and head, which is correct for snapshot chain comparison but not full disk inventory. Instance name is sometimes unknown and passed as empty for best-effort validation.

Test signals: rebuild/revert tests should validate disk filtering and empty-chain error.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/util.go -->
