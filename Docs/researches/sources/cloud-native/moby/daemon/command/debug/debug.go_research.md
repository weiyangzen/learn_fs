<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/debug/debug.go -->
# sources/cloud-native/moby/daemon/command/debug/debug.go

## Purpose
Centralizes process-level debug mode toggling for daemon command code.

## Important APIs, Types, And Functions
`Enable` sets `DEBUG=1` and containerd log level to debug. `Disable` unsets `DEBUG` and restores info level. `IsEnabled` checks whether `DEBUG` is non-empty.

## Control Flow
The functions are direct setters/getters with no branching beyond environment lookup.

## State And Persistence Behavior
Mutates process environment and global logger level. No durable persistence exists, but changes affect subsequent tests and daemon execution in the same process.

## Dependencies And Integration Points
Uses `os` and `github.com/containerd/log`. Command startup and tests can use this as a coarse global debug switch.

## Risks And Test Signals
The API is intentionally global, so callers must restore state in tests. Tests verify environment and log level transitions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/debug/debug.go -->
