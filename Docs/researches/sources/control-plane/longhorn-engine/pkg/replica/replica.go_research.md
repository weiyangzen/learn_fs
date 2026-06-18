# sources/control-plane/longhorn-engine/pkg/replica/replica.go

Purpose: implements the core Longhorn replica: disk-chain metadata, snapshot/revert/remove/replace operations, volume IO, expansion, backing-file insertion, metadata recovery, and data layout export.

Important APIs/types/functions: `Replica` owns a `diffDisk`, metadata maps (`diskData`, `diskChildrenMap`, `activeDiskData`), revision counter state, read-only flag, unmap/snapshot limits, and `Info`. Constructors `New`, `NewReadOnly`, and `construct` create/open replicas. Public operations include `Snapshot`, `Revert`, `RemoveDiffDisk`, `MarkDiskAsRemoved`, `PrepareRemoveDisk`, `ReplaceDisk`, `Expand`, `WriteAt`, `ReadAt`, `UnmapAt`, `ListDisks`, `Preload`, and `GetDataLayout`. Internal helpers manage atomic metadata writes, new head creation, old-head linking, disk graph updates, live-chain opening, metadata read/recovery, and cleanup.

Control flow: construction creates the directory, recovers `volume.meta` if missing/empty, reads disk metadata, initializes revision counter, opens the live chain or creates initial disk, validates FIEMAP support, and inserts backing file if present. Snapshot/expand create a new head and optionally link the old head as a snapshot, with rollback functions around file and metadata operations. Revert creates a new head pointing at the chosen snapshot, updates `volume.meta`, removes old head, and reloads. Disk removal rewires parent/child metadata and removes active-chain indexes when applicable. IO delegates to `diffDisk` under locks and increments the revision counter asynchronously.

State and persistence: persists `volume.meta`, per-disk `.meta` files, snapshot/head sparse image files, checksum files, and `revision.counter`. In-memory state mirrors disk graph and sector locations. `Close` writes clean dirty state, while most mutations write dirty metadata first.

Dependencies and integration points: used by `replica.Server`, backup/status logic, sync-agent operations, and data servers. Depends on sparse-tools direct IO, FIEMAP, Longhorn backing files, disk utility naming, and Longhorn type/error helpers.

Risks: file operations are complex and rollback is best-effort; crashes mid-operation can leave metadata requiring recovery. `diskPattern` matches only one digit because `(\d)+` captures a single repeated digit group, which can break next-file parsing for multi-digit heads. Revision counter increments are not atomic with data writes and can overcount on failed writes by design. Location indexes are bytes. Many methods depend on process cwd indirectly through helpers. Expansion snapshot creation consumes snapshot count and metadata budget.

Test signals: `replica_test.go` provides broad coverage for create/snapshot/revert/remove/prepare-remove/read/write/backing/partial IO/unmap behavior. Some high-risk areas, such as crash recovery, multi-digit head parsing, revision counter races, and rollback failures, are not fully covered here.
