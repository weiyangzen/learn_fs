# sources/distributed-fs/ipfs-kubo/test/cli/shutdown_timeout_test.go

Purpose: tests daemon bounded-shutdown configuration through end-to-end daemon stop/start behavior.

Important APIs and constants: `testShutdownTimeout` is 10 seconds and `testShutdownCompletionBound` is 15 seconds. Tests update `cfg.Internal.ShutdownTimeout` with `config.NewOptionalDuration`, start daemons, call `node.StopDaemon`, and measure elapsed time.

Control flow: `TestShutdownTimeoutHonored` configures a nonzero timeout, starts a daemon, writes pinned data with `add`, creates an MFS directory, verifies `diag healthy`, stops the daemon and requires completion well under the bound, restarts it, and verifies the pin and MFS directory survived. `TestShutdownTimeoutDisabled` sets timeout zero to opt out of the watchdog/deadline logic, then still expects a clean stop within the same soft bound because no subsystem is hung.

State and persistence: pinned content and MFS state must persist across shutdown and restart in the bounded-shutdown case. ShutdownTimeout is a config value read by daemon lifecycle code.

Dependencies and integration points: integrates internal config, daemon lifecycle, health diagnostics, pin storage, MFS persistence, and harness stop escalation behavior.

Risks and test signals: wall-clock assertions can be noisy on overloaded systems but include a five-second cushion. Failures indicate shutdown timeout not honored, disabled mode hanging unexpectedly, or shutdown corrupting/flushing persistent pin/MFS state incorrectly.
