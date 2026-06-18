<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/multi_unmapper_at.go -->
## sources/control-plane/longhorn-engine/pkg/controller/multi_unmapper_at.go

Purpose: fan-out implementation of `types.UnmapperAt` across multiple replica backends.

Important APIs/types/functions: `MultiUnmapperAt` holds unmappers. `MultiUnmapperError` joins underlying errors. `UnmapAt` starts one goroutine per backend, collects errors, records one returned unmapped size, and warns if sizes differ.

Control flow: all unmap operations run concurrently; after `WaitGroup` completion the method returns first observed size and aggregated error if any backend failed.

State and persistence: no local persistence; unmap effects happen in backend replicas.

Dependencies and integration points: used by `replicator` for controller unmap fan-out. Depends on `types.UnmapperAt` and logrus.

Risks: if there are zero unmappers, returns size 0 nil. Size mismatch is only logged, not treated as error. Error type is distinct from `MultiWriterError`; `replicator.UnmapAt` currently checks for `MultiWriterError`, which looks like a bug because multi-unmap errors would not be decomposed per backend.

Test signals: should have unit tests for all-success, partial failure, zero unmappers, and mismatched sizes.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/multi_unmapper_at.go -->
