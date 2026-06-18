<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/kill.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/tasks/kill.go

## Purpose
Signals tasks or exec processes and removes CNI networking when terminating primary task paths.

## Important APIs, Types, And Functions
Defines `defaultSignal`, `RemoveCniNetworkIfExist`, and `killCommand`.

## Control Flow
Parses signal name with platform map, loads container/task, optionally removes CNI network for non-exec primary task, then sends signal either to all task processes, a named exec process, or the main task.

## State And Persistence
Mutates live process state and may tear down CNI network namespace/configuration.

## Dependencies And Integration Points
containerd task/process APIs, CNI helpers, command signal map, errdefs, log.

## Risks And Test Signals
Removing CNI before signal completion can affect still-running processes if kill fails; `--all` is broad. Test signal is integration-level. Source size reviewed: 138 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/kill.go -->
