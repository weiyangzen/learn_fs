<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/signals_notlinux.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/signals_notlinux.go

## Purpose
Non-Linux fallback policy for signal forwarding.

## Important APIs, Types, And Functions
Implements `canIgnoreSignal` for non-Linux builds.

## Control Flow
Always returns false so no signal is filtered by the helper.

## State And Persistence
No persistence.

## Dependencies And Integration Points
`!linux` build tag.

## Risks And Test Signals
Non-Linux behavior may forward signals that should be filtered on specific platforms; coverage is integration/manual. Source size reviewed: 25 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/signals_notlinux.go -->
