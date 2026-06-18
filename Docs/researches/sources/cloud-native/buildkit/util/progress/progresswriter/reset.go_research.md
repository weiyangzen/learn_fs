<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progresswriter/reset.go -->
# sources/cloud-native/buildkit/util/progress/progresswriter/reset.go

Purpose: wraps a progress writer and shifts incoming timestamps so the first observed vertex start aligns with wrapper creation time.

Important APIs and types: `ResetTime` and internal `pw`.

Control flow: `ResetTime` creates a wrapper status channel and goroutine. The first status containing a started vertex establishes `diff = firstStarted - wrapperCreationTime`. Subsequent vertex, status, and log timestamps are copied and shifted backward by that diff before forwarding to the underlying writer. Closing the wrapper status channel closes the underlying status channel.

State and persistence: in-memory diff state only. The wrapper embeds the underlying writer and overrides `Status`.

Dependencies and integration: uses BuildKit client status structs and the package `Writer` interface.

Risks: until a vertex with `Started` appears, statuses pass through unchanged. The wrapper copies top-level status slices but preserves warning pointers as-is. The goroutine exits on underlying `Done` without closing wrapper status.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progresswriter/reset.go -->
