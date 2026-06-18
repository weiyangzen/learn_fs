<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/gc/gc.go -->
# sources/cloud-native/containerd/pkg/gc/gc.go

Purpose: experimental deterministic resource reachability and sweep helpers for containerd garbage collection.

Important APIs and types: `ResourceType`, `ResourceMax`, `Node`, `Stats`, `Tricolor`, `ConcurrentMark`, and `Sweep`.

Control flow and state: `Tricolor` performs single-thread depth-first marking from roots, calling `refs` for each gray node, de-duplicating via `seen`, stripping high bits from `ResourceType` before recording reachable. `ConcurrentMark` receives roots from a channel, fans out reference traversal goroutines, tracks outstanding work with a waitgroup, cancels on first error, and returns the seen set. `Sweep` calls `remove` for nodes absent from the reachable map.

Dependencies and integration: uses only `context`, `sync`, and `time`. Callers provide graph traversal and removal semantics.

Risks and test signals: `ConcurrentMark` mutates `seen` from a single goroutine receiving `grays`, but calls `wg.Add` inside callback goroutines before sending; this is subtle concurrency code. Correct usage requires graph stability until sweep completes. Tests cover basic graphs and benchmark tricolor.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/gc/gc.go -->
