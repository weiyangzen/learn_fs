<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/replicator.go -->
## sources/control-plane/longhorn-engine/pkg/controller/replicator.go

Purpose: internal backend multiplexer for controller reads, writes, unmaps, snapshots, expansion, close, and per-backend settings.

Important APIs/types/functions: `replicator` tracks backend wrappers by address, mode, reader/writer/unmapper index maps, selected readers, and next read index. `BackendError` aggregates per-address errors and written bytes. Methods include `AddBackend`, `RemoveBackend`, `ReadAt`, `WriteAt`, `UnmapAt`, `buildReaderWriterUnmappers`, `SetMode`, `Snapshot`, `Expand`, `Close`, metadata aggregators, and per-backend setters/getters.

Control flow: reads round-robin RW readers and fall through on error. Writes fan out through `MultiWriterAt` to all non-ERR backends, including WO. Unmaps fan out similarly. Snapshot and expand run concurrently across non-ERR backends. Expansion returns whether any replica succeeded plus separate errors for out-of-sync handling versus recording.

State and persistence: stores in-memory backend registry and mode/index maps. Persistent effects happen in backend methods. `RemoveBackend` asynchronously closes backends after stopping monitoring.

Dependencies and integration points: used only by controller. Depends on backend interface, `MultiWriterAt`, `MultiUnmapperAt`, and Longhorn error classification.

Risks: no internal locking, so caller must hold controller locks. Map iteration means writer/read order is not deterministic. `UnmapAt` appears to check `*MultiWriterError` instead of `*MultiUnmapperError`, reducing per-backend error attribution. `backendsAvailable` is based on RW readers, so write-only-only states cannot serve reads.

Test signals: controller tests exercise some write behavior indirectly. Dedicated replicator tests should cover read failover, write error mapping, unmap error mapping, snapshot/expand partial failures, and mode transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/replicator.go -->
