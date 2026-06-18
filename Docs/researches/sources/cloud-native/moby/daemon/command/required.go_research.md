<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/required.go -->
# sources/cloud-native/moby/daemon/command/required.go

## Purpose
Provides Cobra argument validation for commands that accept no positional arguments.

## Important APIs, Types, And Functions
`NoArgs` checks `args` and returns either nil, usage text for commands with subcommands, or a formatted no-arguments error.

## Control Flow
Empty args succeed. Commands with subcommands receive trimmed usage as the error. Leaf commands receive a message with command path, help hint, use line, and short description.

## State And Persistence Behavior
No state or persistence.

## Dependencies And Integration Points
Uses Cobra command metadata and `pkg/errors`. Installed as `Args` for `dockerd` in `docker.go`.

## Risks And Test Signals
Risk is user-facing error format drift. It is indirectly tested by CLI parsing behavior rather than direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/required.go -->
