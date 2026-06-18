## sources/cloud-native/moby/daemon/internal/distribution/xfer/transfer.go

Purpose: Implements the shared transfer scheduler used by layer download/upload managers. It deduplicates in-flight work by key, fans progress to multiple watchers, limits active transfers, supports inactive jobs that should not consume a concurrency slot, and cancels orphaned transfers when all watchers release.

Important APIs and types: `DoNotRetry` and `IsDoNotRetryError` classify non-retriable failures. `watcher` owns release/signal/running channels. The internal `transfer` interface is implemented by `xfer`. `doFunc` is the non-blocking transfer factory contract. `transferManager` exposes `setConcurrency` and `transfer`.

Control flow: `newTransfer` creates a background context deliberately decoupled from client cancellation. `broadcast` drains the main progress channel, stores `lastProgress`, notifies watchers, handles sync pings, and closes `running` when progress ends. `watch` registers a watcher and starts a goroutine that writes the last progress event without duplicates until released or finished. `release` removes the watcher, cancels the transfer if no watchers remain, waits for the watcher goroutine, and closes `releasedChan` after manager closure. `transferManager.transfer` reuses an existing non-cancelled transfer, otherwise queues or starts work based on `concurrencyLimit`, launches broadcast, and removes the transfer from the map when done or inactive.

State and persistence: State is in memory only: maps of active transfers and watchers, last progress, active count, waiting start channels, and cancellation state. There is no disk persistence.

Dependencies and integration: Depends on daemon progress output, `context`, `sync`, `runtime.Gosched`, and `pkg/errors.As`. Upload/download managers build on this scheduler.

Risks: The correctness depends on channel ordering and watcher release pairing. A forgotten `release` leaks watcher references and can keep transfers tracked. The broadcaster sync channel avoids missing progress during detach, but any changes here risk subtle race regressions. `concurrencyLimit == 0` means unlimited, which callers must understand. Type assertions in callers assume factory-returned transfers have the expected concrete wrapper.

Test signals: `transfer_test.go` exercises basic progress delivery, concurrency limits, inactive slot release, watcher release cancellation, watching a finished transfer, and duplicate transfer deduplication.
