<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/signals.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/signals.go

## Purpose
Common signal forwarding helper used by interactive ctr task commands.

## Important APIs, Types, And Functions
Defines `killer`, `ForwardAllSignals`, and `StopCatch`.

## Control Flow
Registers for all signals, loops in a goroutine, skips ignorable signals via platform helper, logs forwarding, and calls task `Kill` for each signal until channel close.

## State And Persistence
Process-local signal subscription only; mutates target task by sending signals.

## Dependencies And Integration Points
Uses os/signal, syscall signal list, containerd log, and platform-specific `canIgnoreSignal`.

## Risks And Test Signals
Forwarding all signals is broad; platform helpers prevent forwarding signals that would break the CLI. Indirectly tested through task/run integration. Source size reviewed: 61 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/signals.go -->
