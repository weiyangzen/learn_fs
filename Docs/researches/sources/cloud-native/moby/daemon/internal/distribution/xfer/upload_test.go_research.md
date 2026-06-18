## sources/cloud-native/moby/daemon/internal/distribution/xfer/upload_test.go

Purpose: Tests `LayerUploadManager` behavior against mocked upload descriptors.

Important APIs and helpers: `mockUploadDescriptor` implements `UploadDescriptor`, tracks current uploads with `atomic.Int32`, returns display/key data from `diffID`, and can fail a configurable number of times through `simulateRetries`. `uploadDescriptors` returns six descriptors including a duplicate key and one descriptor that fails once before succeeding.

Control flow: Mock `Upload` increments/decrements the active counter, errors if concurrency exceeds `maxUploadConcurrency`, emits progress from 0 to 10 with delays, honors context cancellation, optionally simulates a retry, and returns an empty distribution descriptor on success. `TestSuccessfulUpload` sets a millisecond retry tick and expects the complete upload call to return nil while draining progress. `TestCancelledUpload` cancels the caller context shortly after start and expects `context.Canceled`.

State and persistence: No persistent state. The test checks in-memory concurrency and progress behavior.

Dependencies and integration: Uses Docker distribution descriptors, daemon `layer.DiffID`, daemon progress output, Go atomics, and context cancellation.

Risks covered: Over-concurrency, retry path, duplicate descriptor keys, and cancellation while uploads are in progress. The mock `SetRemoteDescriptor` is a no-op, so descriptor propagation is not asserted.
