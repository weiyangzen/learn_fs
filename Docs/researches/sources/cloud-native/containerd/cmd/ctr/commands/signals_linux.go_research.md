<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/signals_linux.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/signals_linux.go

## Purpose
Linux policy for signals that ctr should not forward to tasks.

## Important APIs, Types, And Functions
Implements `canIgnoreSignal` for Linux.

## Control Flow
Returns true for SIGURG because Go runtime uses it internally; all other signals are eligible for forwarding.

## State And Persistence
No persistence.

## Dependencies And Integration Points
Linux build tag and syscall constants.

## Risks And Test Signals
A too-small ignore list can forward unexpected runtime/control signals; SIGURG coverage protects Go runtime behavior. Source size reviewed: 27 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/signals_linux.go -->
