<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/progress.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/progress.go

## Purpose

Defines shared progress-bar rendering policy and the full progress template used by transfer commands.

## Important APIs, Types, and Functions

`ProgressBarFullTemplate` is the `pb/v3` template for counters, bar, speed, percent, and ETA. `ShouldShowProgress(req, flag)` resolves a boolean progress option or defaults to terminal detection on stderr.

## Control Flow

If the option map contains a boolean for the named flag, that explicit value wins. If the option is absent or non-boolean, the function calls `IsTerminal(os.Stderr)`.

## State and Persistence Behavior

Read-only. It inspects request options and stderr terminal state.

## Dependencies and Integration Points

Uses `go-ipfs-cmds` and `tty.go`. Called by `cat`, `get`, `dag export`, and `dag stat` post-run paths.

## Risks and Edge Cases

Non-boolean option values silently fall back to TTY detection, which is robust but can hide caller option bugs. Terminal detection depends on the process stderr file descriptor.

## Test Signals

`progress_test.go` covers explicit true, explicit false, unset TTY default, and non-bool fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/progress.go -->
