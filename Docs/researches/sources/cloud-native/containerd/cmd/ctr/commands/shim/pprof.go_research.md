<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/shim/pprof.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/shim/pprof.go

## Purpose
Adds `ctr shim pprof` subcommands that reuse generic pprof helpers against a shim debug socket.

## Important APIs, Types, And Functions
Defines shim pprof CLI commands and `getPProfClient`.

## Control Flow
Each subcommand delegates to the pprof package with a shim-specific HTTP client. The client resolves the shim socket from namespace, daemon address, and task ID, then installs it as the transport dialer.

## State And Persistence
Read-only live diagnostics; streams profile bytes/text to stdout.

## Dependencies And Integration Points
Integrates `cmd/ctr/commands/pprof`, namespace context, shim socket address calculation, Unix sockets, and net/http.

## Risks And Test Signals
Requires `--id` or address context that resolves to a live shim. Time-based profiles block. No direct tests in file. Source size reviewed: 165 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/shim/pprof.go -->
