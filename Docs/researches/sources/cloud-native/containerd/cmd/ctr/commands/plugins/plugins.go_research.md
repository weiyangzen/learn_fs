<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/plugins/plugins.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/plugins/plugins.go

## Purpose
Implements `ctr plugins` and `ctr plugins inspect-runtime` for introspecting containerd plugin registrations and runtime metadata.

## Important APIs, Types, And Functions
Exports `Command`; defines `listCommand`, `inspectRuntimeCommand`, and `prettyPlatforms` for deduplicating and sorting platform strings.

## Control Flow
The list action opens a containerd client, calls `IntrospectionService().Plugins`, then chooses quiet, detailed, or tabular output. Runtime inspection resolves runtime options, calls `client.RuntimeInfo`, and emits indented JSON.

## State And Persistence
Read-only against containerd daemon state; output is written to stdout/app writer only.

## Dependencies And Integration Points
Uses containerd introspection and runtime info APIs, OCI platform formatting, gRPC error codes, tabwriter, and `containerd/plugin` skip detection.

## Risks And Test Signals
Status classification relies on substring matching the skip-plugin error text; detailed output exposes plugin exports and init errors. No local unit tests in this file; covered indirectly by CLI/integration tests. Source size reviewed: 197 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/plugins/plugins.go -->
