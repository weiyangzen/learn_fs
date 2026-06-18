<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/sandboxes/sandboxes.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/sandboxes/sandboxes.go

## Purpose
Implements `ctr sandboxes` for sandbox runtime lifecycle and metadata inspection.

## Important APIs, Types, And Functions
Exports `Command`; defines run/create, list, remove, and info subcommands.

## Control Flow
Run reads a JSON OCI sandbox spec, creates a sandbox with runtime and spec, starts it, and prints the ID. List queries the sandbox store with filters. Remove loads each sandbox, stops it, optionally ignores stop failures, and shuts it down. Info prints metadata JSON.

## State And Persistence
Creates, starts, stops, shuts down, and reads sandbox records in containerd; no local persistence beyond stdout/logging.

## Dependencies And Integration Points
Uses containerd sandbox client/store APIs, default runtime, OCI spec JSON, tabwriter, log, and errdefs.

## Risks And Test Signals
Remove logs and continues across IDs, so partial deletion is possible. Input spec validation is just JSON unmarshal into OCI spec. Test signal is integration-level only. Source size reviewed: 222 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/sandboxes/sandboxes.go -->
