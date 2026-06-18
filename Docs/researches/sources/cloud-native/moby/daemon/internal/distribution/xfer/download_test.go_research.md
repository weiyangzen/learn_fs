# sources/cloud-native/moby/daemon/internal/distribution/xfer/download_test.go

## Purpose
Tests the layer download manager's success path, cancellation, concurrency guard, deduplication, and retry limits.

## APIs, Control Flow, and Integration
Mocks implement `layer.Layer`, `layer.Store`, and `DownloadDescriptor`. `TestSuccessfulDownload` pre-registers the first layer, downloads a descriptor set with a duplicate key and one retrying descriptor, verifies progress states, rootfs DiffIDs, and `Registered` callbacks. `TestCancelledDownload` cancels context shortly after start and expects `context.Canceled`. `TestMaxDownloadAttempts` table-tests success/failure based on simulated retry count and configured max attempts.

## State, Dependencies, and Risks
State is an in-memory mock layer store and progress channel. The success test skips on Windows. Tests do not cover descriptor `Close` ordering, `DoNotRetry`, describable layer registration, or parent failure propagation in every branch.
