<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/main.go -->
# sources/cloud-native/containerd/cmd/ctr/main.go

## Purpose
Entrypoint for the `ctr` binary and command registration.

## Important APIs, Types, And Functions
Defines `pluginCmds` and `main`.

## Control Flow
Constructs the urfave/cli app from common command package metadata, registers built-in command groups plus optional plugin commands, and runs with process args.

## State And Persistence
No persistent state beyond invoking commands; exits through cli error handling.

## Dependencies And Integration Points
All `cmd/ctr/commands/...` packages, urfave/cli app setup.

## Risks And Test Signals
Command registration order and omissions affect CLI surface. Manpage generation is a secondary test signal. Source size reviewed: 36 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/main.go -->
