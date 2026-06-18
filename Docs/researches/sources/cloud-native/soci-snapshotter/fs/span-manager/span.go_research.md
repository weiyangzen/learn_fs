# sources/cloud-native/soci-snapshotter/fs/span-manager/span.go

Purpose: defines the per-span state machine used by `SpanManager` to coordinate lazy compressed-span fetches, background prefetches, decompression, and cache reads.

Important APIs and flow: `spanState` has four states: `unrequested`, `requested`, `fetched`, and `uncompressed`. `stateTransitionMap` only permits `unrequested -> requested`, `requested -> unrequested|fetched|uncompressed`, and `fetched -> uncompressed`. `span` stores compressed and uncompressed offset ranges, an atomic state value, and a mutex used by the manager to serialize fetch/decompress transitions. `checkState`, `setState`, and `validateStateTransition` are the local state helpers.

State and persistence: state is process-local and stored in `atomic.Value`; span content is not stored here but in the manager's blob cache. The mutex prevents duplicate remote fetch or decompression work for the same span.

Dependencies and integration: depends on the compression package for `SpanID` and `Offset`, and is consumed by `span_manager.go`. The retry constant `defaultSpanVerificationFailureRetries` is also defined here for manager construction.

Risks and test signals: invalid transitions return `errInvalidSpanStateTransition`, so callers must only move through the documented sequence. There is no terminal transition out of `uncompressed`; invalid regression to earlier states is intentionally blocked. Tests in `span_manager_test.go` exercise valid and invalid transition combinations and state outcomes for background and on-demand fetches.
