<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/run/run.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/run/run.go

## Purpose
Defines the cross-platform `ctr run` command, argument validation, mount parsing, IO setup, task start/wait, cleanup, and label merging.

## Important APIs, Types, And Functions
Exports `Command`; provides `withMounts`, `parseMountFlag`, and `buildLabels`.

## Control Flow
The action resolves image/rootfs/config arguments, rejects incompatible `--rm` and `--detach`, creates a container via platform `NewContainer`, optionally dumps the OCI spec, configures terminal/raw mode or null/log FIFO IO, creates and starts the task, optionally waits and propagates exit code, and cleans up CNI/container state for `--rm`.

## State And Persistence
Creates container metadata, snapshots, tasks, CNI metadata, FIFO paths, and optional dumped spec files. Cleanup removes task/container/snapshot when configured.

## Dependencies And Integration Points
Integrates console, cio, containerd client, task helpers, CNI metadata, OCI spec options, label validation, and platform-specific run files.

## Risks And Test Signals
Run is a high-blast-radius command: leaked containers/snapshots/FIFOs are possible on partial failure; terminal raw mode must reset. `parseMountFlag` relies on CSV parsing and rejects unknown keys. Tests are mainly in platform helper tests. Source size reviewed: 312 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/run/run.go -->
