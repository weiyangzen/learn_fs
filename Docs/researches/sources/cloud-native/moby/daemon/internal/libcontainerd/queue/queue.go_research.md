<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/queue/queue.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/queue/queue.go

Purpose: serializes asynchronous callbacks by string ID, mainly container ID, while allowing different IDs to proceed concurrently.

Important APIs and types: `Queue` embeds `sync.Mutex` and holds `fns map[string]chan struct{}`. `Append(id string, f func())` is the only exported operation.

Control flow: `Append` creates a `done` channel, swaps it into the map for `id`, and launches a goroutine. If a previous channel existed, the goroutine waits for it before running `f`. After `f` returns, it closes `done` and removes the map entry if it is still the latest channel for that ID.

State and persistence: queue state is in-memory only. Channels encode dependency order. The map is lazily initialized and pruned when work drains.

Dependencies and integration: used by local and remote libcontainerd clients to deliver backend events in order per container.

Risks: `f` is not recovered; a panic would prevent close/delete and block later callbacks for the same ID. Long-running callbacks back up only their ID. There is no cancellation or bounded queue length.

Test signals: `queue_test.go` verifies same-ID callbacks observe serialized ordering.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/queue/queue.go -->
