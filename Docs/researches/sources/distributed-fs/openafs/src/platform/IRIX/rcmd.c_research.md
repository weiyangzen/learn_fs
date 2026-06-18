# sources/distributed-fs/openafs/src/platform/IRIX/rcmd.c

## Purpose
Implements BSD-compatible `rcmd`, `rresvport`, `ruserok`, and helper host/user validation routines with AFS remote-authentication support. It is used by IRIX/legacy remote shell integration to obtain reserved-port connections and optionally transfer AFS token authentication before falling back to classic rsh protocol behavior.

## Important APIs, Types, And Functions
Main APIs are `rcmd` (or `rmcd` on HP-UX 10.2), `rresvport`, `ruserok`, `_validuser`, and static `_checkhost`. `rcmd` coordinates `gethostbyname`, reserved-port sockets, `ta_rauth`, `connect`, secondary stderr-channel setup, and command/user string transmission. `ruserok` checks `/etc/hosts.equiv` and user `.rhosts` with ownership and mode validation.

## Control Flow
`rcmd` resolves the host, blocks `SIGURG`, creates a reserved local port, attempts AFS token remote auth via `ta_rauth` when a TCP service name exists, and otherwise connects to the requested remote service with retry/backoff for connection refusal and address-list fallback. If `fd2p` is requested, it opens another reserved port, sends that port number, accepts the reverse stderr connection, and verifies the peer uses a reserved port. It then writes local user, remote user, and command NUL-terminated strings and waits for the remote status byte. `ruserok` lowercases hosts, checks global and per-user trust files, temporarily switches effective uid/gid for `.rhosts`, and restores credentials.

## State And Persistence
State is mostly transient sockets and effective credential changes. `_check_rhosts_file` controls whether user `.rhosts` is consulted. `_checkhost` caches the local domain suffix.

## Dependencies And Integration Points
Depends on BSD sockets, reserved ports, resolver APIs, syslog, passwd/group APIs, and the OpenAFS `ta_rauth` token-transfer function. It plugs AFS token authentication into existing rsh/rlogin-style flows.

## Risks And Test Signals
Major risks are the inherent insecurity of r-commands, reserved-port trust assumptions, global resolver storage, credential-switch restoration on error paths, fixed-size buffers, and platform-specific signal-mask construction. Test signals are successful authenticated and fallback rsh connections, bad-host/address fallback behavior, stderr-channel validation, `.rhosts` permission rejection, and no leaked effective uid/gid after failures.
