# sources/control-plane/mayastor/io-engine/src/coredump.rs

## Purpose
Enables Linux core dumps for the io-engine process by raising `RLIMIT_CORE`.

## Important APIs, Types, and Functions
- `DEFAULT_CORE_LIMIT` is 5 GiB, matching SPDK app default behavior.
- `enable(limit)` calls `setrlimit(RLIMIT_CORE, ...)` and returns `nix::Error` on failure.

## Control Flow and State
The caller chooses a limit, constructs a libc `rlimit` with current and max equal to that limit, and applies it through `setrlimit`. The effect is process resource-limit state.

## Dependencies and Integration Points
Used by CLI/startup coredump option handling. Depends on `libc` and `nix`.

## Risks and Test Signals
Raising `rlim_max` may require privileges or be capped by the parent environment. Tests should cover success under permissive limits, failure propagation, and CLI default/debug-build behavior around the enable option.
