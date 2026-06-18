<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/shim/shim.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/shim/shim.go

## Purpose
Implements direct low-level TTRPC interaction with containerd shim task services.

## Important APIs, Types, And Functions
Exports `Command`; defines start/delete/shutdown/state/exec subcommands plus `getTaskService`, `getTaskServiceV2`, and `getTTRPCClient`.

## Control Flow
Connection resolution tries explicit shim address, current socket scheme, and legacy abstract socket. Subcommands call task v2/v3 TTRPC methods; exec reads an OCI process spec, prepares FIFOs, sends Exec/Start, optionally attaches and resizes TTY.

## State And Persistence
Mutates live shim task/process state directly; reads process spec files and FIFO paths; does not go through containerd metadata APIs.

## Dependencies And Integration Points
Uses ttrpc, task v2/v3 APIs, typeurl/protobuf Any, console, namespaces, shim socket helpers, and runtime spec types.

## Risks And Test Signals
Bypasses higher-level client safety and can leak the TTRPC connection as noted in code. Wrong API version or socket can fail late. Integration/manual diagnostic command rather than unit-tested path. Source size reviewed: 373 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/shim/shim.go -->
