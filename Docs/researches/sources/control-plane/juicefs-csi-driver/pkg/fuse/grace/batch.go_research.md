# sources/control-plane/juicefs-csi-driver/pkg/fuse/grace/batch.go

Purpose: coordinates batch graceful upgrades of JuiceFS mount pods on the current node.

Important APIs and types: `BatchUpgrade` tracks a batch config name/index, Kubernetes client, recreate flag, selected `PodUpgrade` objects, and success/failure maps protected by a mutex. `NewBatchUpgrade` builds the object from an `upgradeRequest`. `fetchPods` loads upgrade config, lists mount pods on the local node, filters to names in the requested batch, checks upgrade eligibility, builds `PodUpgrade` records, and reports already-upgraded pods over the client connection. `BatchUpgrade` runs `gracefulShutdown` concurrently for each selected pod. `TriggerBatchUpgrade` is the CLI/client entry point that sends a `BATCH` request over a Unix socket and prints responses until a current-batch terminal message is seen.

Control flow: fetch phase narrows the global batch plan to this node, then upgrade phase uses a wait group to run pod upgrades in parallel. Each pod failure records status, sends messages, and removes upgrade-process annotations when needed.

State and persistence behavior: process-local state includes `podsToUpgrade`, `successSum`, and `failSum`. External state is Kubernetes pod annotations/events/jobs and socket output; actual pod recreation is handled by `PodUpgrade` and resource helpers.

Dependencies and integration points: integrates config batch loading, Kubernetes pod listing by label/field selectors, resource eligibility/hash helpers, `PodUpgrade` from `grace.go`, and the shutdown Unix socket protocol.

Risks and test signals: the goroutine loop closes over `p` from the range; with modern Go range semantics this is safe, but older compilers would risk all goroutines using the same pod. The file assumes `batchIndex` is valid for `batchConfig.Batches[u.crtBatchIndex-1]`; malformed requests can panic. No listed test covers batch behavior directly.
