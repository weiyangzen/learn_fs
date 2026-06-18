<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/go-buildtag/main.go -->
# sources/cloud-native/containerd/cmd/go-buildtag/main.go

## Purpose
Command-line utility for adding or checking Go build tags on source files.

## Important APIs, Types, And Functions
Defines `main` and `handle`.

## Control Flow
Parses flags for write/check/tag list, reads each file, uses build constraint parsing/editing logic, optionally rewrites files or reports needed changes.

## State And Persistence
May rewrite Go source files when write mode is enabled; otherwise read-only/check output.

## Dependencies And Integration Points
Go build constraint APIs, filesystem reads/writes, flag parsing.

## Risks And Test Signals
Incorrect tag insertion can affect build selection; should be run in CI/check mode to detect drift. Source size reviewed: 96 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/go-buildtag/main.go -->
