# sources/cloud-native/moby/daemon/internal/distribution/xfer/download.go

## Purpose
Manages concurrent, deduplicated layer downloads and ordered registration into the Moby layer store.

## APIs, Control Flow, and Integration
`LayerDownloadManager` owns a layer store, transfer manager, retry wait, and max attempts. `Download` walks descriptors bottom-up, skips already-present layers when DiffID is known, deduplicates repeated descriptor keys, schedules downloads with dependency-aware transfer functions, waits for the top layer, reconstructs rootfs DiffIDs, and returns a release function. `makeDownloadFunc` downloads with retry/backoff progress, waits for parent registration, decompresses content, registers with descriptor when supported, updates progress, calls `Registered`, and releases layers after watchers release. `makeDownloadFuncFromDownload` re-registers duplicate layer data atop a different parent.

## State, Dependencies, and Risks
State includes transfer manager slots/watchers, layer store references, descriptor cleanup, and rootfs chain reconstruction. Risks include complex release ownership, cancellation during retry/registration, duplicate-key re-registration semantics, and unexported `DoNotRetry` behavior from transfer package. Tests cover success, cancellation, concurrency, dedupe, and max attempts.
