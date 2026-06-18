# sources/cloud-native/composefs-rs/crates/composefs/src/progress.rs

## Purpose
This module defines a small progress-reporting abstraction for pull and download operations. It lets library code emit structured events without depending on a specific UI and provides an async reader wrapper that reports byte progress out of the hot I/O path.

## Important APIs, Types, and Functions
`ComponentId` identifies a layer, object, or stream and supports `as_str()`, `into_inner()`, `From<S>`, `Display`, `Eq`, and `Hash`. `ProgressUnit` distinguishes bytes from item counts. `ProgressEvent` variants are `Started`, `Progress`, `Skipped`, `Done`, and `Message`. `ProgressReporter` is the `Send + Sync` trait implemented by renderers. `NullReporter` discards events, and `SharedReporter` is `Arc<dyn ProgressReporter>`. `ProgressRead<R>` wraps an `AsyncRead` and exposes `new()` plus an `AsyncRead` implementation. Test support provides `RecordingReporter`.

## Control Flow
Callers emit lifecycle events to a reporter. For byte streams, `ProgressRead::new()` creates a Tokio watch channel initialized to zero and returns both the wrapped reader and a driver future. Each successful `poll_read()` computes the newly filled byte count and updates the watch value with `send_modify()`. The driver awaits watch changes and emits `ProgressEvent::Progress` with the component id and total. The driver completes when the reader is dropped and the watch sender closes.

## State and Persistence Behavior
Progress state is in memory only. `ProgressRead` keeps the wrapped reader and a watch sender containing cumulative bytes. Slow renderers do not backpressure reads because watch channels coalesce intermediate values. `RecordingReporter` stores events behind a `Mutex` for test inspection.

## Dependencies and Integration Points
The module depends on Tokio `AsyncRead` and `watch`, `Arc`, and standard task/pin traits. It is intended for higher-level pull/download paths and UI crates such as `cfsctl` renderers. Placement before decompressors is documented so fetched bytes match compressed transfer totals.

## Risks and Edge Cases
A caller must run the driver future concurrently; otherwise no `ProgressEvent::Progress` events are emitted even though byte counts update. Watch coalescing means renderers may not observe every intermediate count, only monotonic snapshots. Zero-length streams emit no progress events because the watch value never changes. If a read returns `Ok(())` with zero bytes before EOF semantics are complete, no progress is sent.

## Test Signals
Tests cover `NullReporter`, `ComponentId` conversion/display/hash behavior, `ProgressEvent` debug and clone behavior, `RecordingReporter` ordering and thread safety, `ProgressUnit`, non-empty `ProgressRead` progress emission, zero-length no-event behavior, and single-byte event count.
