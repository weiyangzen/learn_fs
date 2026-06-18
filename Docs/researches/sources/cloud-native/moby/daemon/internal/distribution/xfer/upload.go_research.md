## sources/cloud-native/moby/daemon/internal/distribution/xfer/upload.go

Purpose: Provides `LayerUploadManager`, a blocking push helper that schedules layer uploads, deduplicates layers by descriptor key, reports progress, retries transient failures, and records remote descriptors back onto all input descriptors.

Important APIs and types: `maxUploadAttempts` is 5. `LayerUploadManager` wraps `transferManager` and `waitDuration`. `UploadDescriptor` supplies `Key`, display `ID`, `DiffID`, `Upload(ctx, progress)`, and `SetRemoteDescriptor`. `uploadTransfer` embeds `transfer` plus the uploaded remote descriptor and final error.

Control flow: `Upload` marks each descriptor as "Preparing", skips duplicate keys in a per-call map, starts or joins transfer-manager work with `makeUploadFunc`, defers watcher release, waits for all unique upload transfers or caller context cancellation, then copies remote descriptors to every original layer entry. `makeUploadFunc` creates an `uploadTransfer`, waits for the concurrency `start` channel, emits "Waiting" if queued, calls `descriptor.Upload` with the transfer context, and retries failures unless the transfer context was cancelled, the error is `DoNotRetry`, or `maxUploadAttempts` is reached. Retry delay counts down in five-second increments scaled by attempt number and uses the configurable tick duration.

State and persistence: Runtime-only state includes remote descriptors, errors, retry counters, and transfer-manager slots. Persistence is delegated to registries through `UploadDescriptor.Upload`; this file does not write disk.

Dependencies and integration: Integrates with Docker distribution descriptors, daemon layer IDs, progress output, containerd logging, and `transfer.go`.

Risks: Direct type assertion `err.(DoNotRetry)` misses wrapped `DoNotRetry`; `IsDoNotRetryError` would handle wrapping. Retry countdown messages rely on a small pluralization map. The caller context only controls the blocking wait; actual upload cancellation comes from transfer context cancellation triggered by watcher release.

Test signals: `upload_test.go` covers successful concurrent uploads, deduplication by repeated diff ID, retry success, and caller cancellation returning `context.Canceled`.
