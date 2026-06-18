<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/version/version.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/version/version.go

## Purpose
Implements `ctr version`, reporting client and server version/revision/go runtime details.

## Important APIs, Types, And Functions
Exports `Command`.

## Control Flow
Prints client metadata from compiled version package, then connects to containerd and prints server version if reachable.

## State And Persistence
Read-only; stdout output only.

## Dependencies And Integration Points
containerd version service/client, Go runtime, tabwriter.

## Risks And Test Signals
Server connection failure returns an error after client info; useful health-check command with integration coverage. Source size reviewed: 67 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/version/version.go -->
