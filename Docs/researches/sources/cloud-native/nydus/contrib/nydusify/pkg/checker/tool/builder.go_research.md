# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/tool/builder.go

Purpose: wraps the external `nydus-image` binary for checker bootstrap inspection.

Important APIs and flow: `BuilderOption` carries `BootstrapPath` and `DebugOutputPath`. `NewBuilder(binaryPath)` initializes stdout/stderr to process stdout/stderr. `(*Builder).Check` executes `nydus-image check --log-level warn --output-json <debug> --bootstrap <bootstrap>` using `os/exec`, wiring configured output streams and returning the process error.

State and persistence: no internal persistence. External side effects are entirely delegated to `nydus-image`, which reads the bootstrap and writes the JSON debug output path.

Dependencies and integration: used by checker flows that need parsed bootstrap diagnostics. Depends only on `io`, `os`, and `os/exec`, making it easy to test with fake scripts.

Risks and test signals: command construction is deterministic but no validation is performed for empty paths. Failure mode is the raw `cmd.Run` error, so stderr context depends on configured `stderr`.
