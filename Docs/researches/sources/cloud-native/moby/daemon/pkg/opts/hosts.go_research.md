<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/hosts.go -->
# sources/cloud-native/moby/daemon/pkg/opts/hosts.go

## Purpose
Parses, validates, and normalizes daemon listener host addresses and extra-host entries.

## Important APIs, Types, And Functions
Constants define default ports, sockets, named pipe, and `HostGatewayName`. `ValidateHost`, `ParseDaemonHost`, `ParseTCPAddr`, `parseTCPAddr`, `parseSimpleProtoAddr`, and `ValidateExtraHost` are the core functions.

## Control Flow
`ParseDaemonHost` infers `tcp` when no scheme is present, dispatches to protocol-specific parsing, accepts `fd://` as-is, and rejects unknown protocols. TCP parsing validates URL scheme/path/port and fills missing host or port from a strict default. Extra-host validation splits on the first colon and validates IP unless the value is `host-gateway`.

## State, Dependencies, And Integration Points
No persistence. It depends on `net`, `net/url`, and the broader `opts.ValidateIPAddress`. It feeds daemon `-H` listener configuration and container host aliases.

## Risks And Test Signals
`ValidateHost` returns the original untrimmed value for later TLS handling. TCP ports are only parsed for numeric syntax and zero, so very large integers may pass. `hosts_test.go` provides broad edge-case coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/hosts.go -->
