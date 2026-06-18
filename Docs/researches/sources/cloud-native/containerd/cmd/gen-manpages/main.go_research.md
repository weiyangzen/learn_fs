<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/gen-manpages/main.go -->
# sources/cloud-native/containerd/cmd/gen-manpages/main.go

## Purpose
Utility that generates ctr/containerd manpages from CLI command definitions.

## Important APIs, Types, And Functions
Defines `main` and `run`.

## Control Flow
Builds the CLI app/commands, creates the target directory, and writes generated man pages for selected commands.

## State And Persistence
Writes manpage files to the filesystem.

## Dependencies And Integration Points
urfave/cli manpage support and ctr command tree.

## Risks And Test Signals
Generated docs can drift if command registration changes; failures surface in docs/release workflows. Source size reviewed: 67 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/gen-manpages/main.go -->
