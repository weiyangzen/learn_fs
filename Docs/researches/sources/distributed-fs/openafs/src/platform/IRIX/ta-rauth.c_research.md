# sources/distributed-fs/openafs/src/platform/IRIX/ta-rauth.c

## Purpose
Transfers an existing local AFS token to a remote authentication service before an r-command connection proceeds. It is the token-authentication companion for `rcmd.c`.

## Important APIs, Types, And Functions
Exports `ta_rauth(int s, char *svc_name, struct in_addr raddr)` and `outtoken`. `ta_rauth` opens the client configuration, discovers the local cell, retrieves the `afs` service token with `ktc_GetToken`, connects the provided socket to `RAUTH_PORT` (default 601), sends token material with `outtoken`, and reads a one-byte allow/deny result. Global `ta_debug` enables syslog/perror diagnostics.

## Control Flow
The function returns `0` when no token or refused authenticator means the caller should continue without remote auth, `1` for successful remote authentication, `-1` for remote denial, `-2` for local/internal failures, and `-3` for remote connection failures. `outtoken` serializes service name, version, cell, token start/end times, session key, kvno, ticket length, and ticket bytes into a stack buffer, then writes it to the socket.

## State And Persistence
Reads local AFS client configuration and token-cache state but writes no persistent state. Network output includes sensitive token/session-key data.

## Dependencies And Integration Points
Depends on `afsconf`, `ktc`, socket APIs, syslog, and the remote auth daemon protocol expected on port 601. Called from `rcmd` before classic rsh fallback.

## Risks And Test Signals
Risks are cleartext token transfer unless protected externally, `sprintf`/fixed 1024-byte buffer sizing against ticket length, exit-on-short-read behavior, and stale kauth-era token assumptions. Test signals include no-token fallback, ECONNREFUSED fallback, timeout/unreachable error mapping, remote allow/deny handling, and protocol compatibility with the authenticator.
