<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progresswriter/writer.go -->
# sources/cloud-native/buildkit/util/progress/progresswriter/writer.go

Purpose: defines the common progress writer contract and a helper for emitting a one-step vertex around a function.

Important APIs and types: `Writer` interface with `Done`, `Err`, and `Status`; helper `Write`.

Control flow: `Write` generates a digest, sends a started vertex, invokes the optional function, then sends a completed vertex with any error message captured from the function.

State and persistence: no persistent state; writes directly to the writer status channel.

Dependencies and integration: depends on BuildKit client types, identity IDs, OCI digests, and `time.Now`. Used by code that needs simple progress spans without full logger nesting.

Risks: `Write` ignores the writer `Done` channel and can block forever if the status receiver is not reading. It discards the callback error after embedding it in progress status.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progresswriter/writer.go -->
