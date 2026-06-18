<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/multi_writer_at.go -->
## sources/control-plane/longhorn-engine/pkg/controller/multi_writer_at.go

Purpose: concurrent fan-out `io.WriterAt` for writing the same buffer to multiple replica backends.

Important APIs/types/functions: `MultiWriterAt` holds writers. `MultiWriterError` records writers, errors, and per-writer written bytes. `WriteAt` starts one goroutine per writer, waits, and returns `len(p)` if at least one writer succeeded, or aggregated errors with written-byte details if any failed.

Control flow: all writes run concurrently. Errors and short writes are recorded only when `err != nil`; successful short writes without error would be treated as full success.

State and persistence: no local persistence; writes persist in backend replicas.

Dependencies and integration points: used by `replicator.WriteAt`; `WrittenBytes` feeds ENOSPC consistency policy in `Controller.handleErrorNoLock`.

Risks: success return `n=len(p)` if any writer succeeds, even when others fail; this is intentional for degraded replica handling but must be paired with error handling. No locking around slice writes is safe because each goroutine writes a unique index. Successful short writes without error are not handled.

Test signals: unit tests should cover partial errors and written-byte propagation into `BackendError`.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/multi_writer_at.go -->
