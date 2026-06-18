<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progresswriter/printer.go -->
# sources/cloud-native/buildkit/util/progress/progresswriter/printer.go

Purpose: adapts `progressui.Display` into the generic progress `Writer` interface and provides a tee wrapper for duplicating solve status streams.

Important APIs and types: `printer`, `tee`, `Tee`, and `NewPrinter`.

Control flow: `NewPrinter` creates a status channel and done channel, resolves `BUILDKIT_PROGRESS` when requested mode is `auto`, constructs a progress UI display, and runs `Display.UpdateFrom` in a goroutine. `Tee` forwards every incoming status to both the wrapped writer and an external channel, then closes both downstream channels when its own channel closes.

State and persistence: `printer.err` captures the display loop result after the goroutine exits; callers observe completion via `Done`. No persistent storage.

Dependencies and integration: depends on `containerd/console.File`, BuildKit client status types, and `progressui.NewDisplay`. Used by CLI and solve paths that need terminal progress.

Risks: `Tee` writes sequentially to both outputs and can block if either receiver stalls. `NewPrinter` does not use a separate context; it passes the supplied context into display update so cancellation ends the display loop.

Test signals: no direct unit tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progresswriter/printer.go -->
