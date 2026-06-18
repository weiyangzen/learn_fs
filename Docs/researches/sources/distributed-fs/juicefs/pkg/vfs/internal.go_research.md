# sources/distributed-fs/juicefs/pkg/vfs/internal.go

Purpose: defines special internal VFS nodes and implements binary control-message handlers for management operations such as remove, clone, info, summary, compact, and cache fill.

Important APIs and types: special inode constants, `internalNode`, `IsSpecialNode`, `IsSpecialName`, `GetInternalNodeByName`, `CollectMetrics`, `writeProgress`, `CalcObjects`, response structs (`InfoResponse`, `SummaryReponse`, `CacheResponse`), and `VFS.handleInternalMsg`.

Control flow and state: init stamps internal node attributes with current uid/gid/time. Control handles are per-pid in `controlHandlers`. `CollectMetrics` flattens Prometheus metrics into text. `writeProgress` emits `meta.CPROGRESS` frames every 300 ms until a background operation completes. `CalcObjects` maps a slice ID/range to object keys based on format hash-prefix and block size. `handleInternalMsg` decodes command payloads, runs metadata operations in goroutines for long tasks, streams progress, and writes either errno bytes or `meta.CDATA` JSON/text frames.

Persistence and integration: internal nodes expose `.control`, `.accesslog`, `.stats`, `.config`, and trash. Commands integrate with `meta.Meta`, object storage head for restore status, cache filler, compaction, and invalidation callbacks.

Risks and test signals: binary protocol parsing assumes valid buffer layout. Some operations continue in background. Object restore status lookup uses `context.Background`, not the control context. Cancellation tests cover InfoV2 and OpSummary.
