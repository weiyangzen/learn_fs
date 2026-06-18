<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/tasks.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/tasks/tasks.go

## Purpose
Registers the `ctr tasks` command group and its subcommands.

## Important APIs, Types, And Functions
Exports `Command` with aliases `task`, `t` and subcommands attach/checkpoint/delete/exec/kill/list/metrics/pause/ps/resume/start.

## Control Flow
No action itself; dispatch is handled by urfave/cli to child command handlers.

## State And Persistence
No direct state changes.

## Dependencies And Integration Points
urfave/cli and sibling task command files.

## Risks And Test Signals
Registration omissions hide commands; no direct tests besides command tree generation/manpages. Source size reviewed: 47 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/tasks.go -->
