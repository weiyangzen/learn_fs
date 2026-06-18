<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progresswriter/progress.go -->
# sources/cloud-native/buildkit/util/progress/progresswriter/progress.go

Purpose: offers a lightweight logger facade that turns arbitrary nested operations and log bytes into BuildKit `client.SolveStatus` messages.

Important APIs and types: `Logger`, `SubLogger`, `Wrap`, `subLogger.Wrap`, and `subLogger.Log`.

Control flow: top-level `Wrap` emits a new vertex with a generated digest and start time, invokes the callback with a `SubLogger`, then defers a completion vertex containing any error string. Nested `subLogger.Wrap` emits `VertexStatus` start/completion pairs under the parent digest. `Log` emits a `VertexLog` with stream, bytes, and timestamp.

State and persistence: no shared state; each wrapped operation gets an identity-derived digest and local timestamps.

Dependencies and integration: uses BuildKit client status structs, `identity.NewID`, OCI digests, and `time.Now`. It feeds any `Logger` function, including writers that send to progress UI.

Risks: if the logger is nil, `Wrap` returns nil without invoking the supplied callback, which is a subtle behavior and likely intentional for disabled progress but surprising to generic callers. The function does not recover panics.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progresswriter/progress.go -->
