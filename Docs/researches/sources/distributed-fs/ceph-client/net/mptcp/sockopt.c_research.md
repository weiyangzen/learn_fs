# sources/distributed-fs/ceph-client/net/mptcp/sockopt.c

## Purpose

`sockopt.c` implements MPTCP-aware `setsockopt`, `getsockopt`, socket-option synchronization to subflows, diagnostic information export, and MPTCP-specific receive-low-water handling. It decides which options are MPTCP-level only, which are mirrored to all subflows, which apply only to the first subflow before establishment, and which pass through to TCP after fallback.

## Important APIs, types, and functions

- Public entry points: `mptcp_setsockopt()`, `mptcp_getsockopt()`, `mptcp_sockopt_sync_locked()`, `mptcp_set_rcvlowat()`, `mptcp_diag_fill_info()`.
- Sequencing helpers: `sockopt_seq_reset()`, `sockopt_seq_inc()`, `setsockopt_seq` in `mptcp_sock` and `mptcp_subflow_context`.
- SOL_SOCKET handlers: integer option sync, timestamp/timestamping, linger, reuse/bind device, buffer sizes, mark, priority, keepalive, incoming CPU.
- SOL_TCP handlers: congestion control, cork, nodelay, keepalive timers/counts, maxseg, notsent low-water, INQ, fastopen options, and first-subflow-only options.
- SOL_IP/SOL_IPV6 handlers: bind/freebind/transparent/local-port-range/TOS and selected IPv6 socket flags.
- Diagnostics: `MPTCP_INFO`, `MPTCP_FULL_INFO`, `MPTCP_TCPINFO`, `MPTCP_SUBFLOW_ADDRS`.

## Control flow

`mptcp_setsockopt()` handles SOL_SOCKET first, rejects unsupported options through `mptcp_supported_sockopt()`, checks TCP fallback, then dispatches by level. Fallback sockets pass the option directly to the underlying TCP socket. Non-fallback sockets either update MPTCP-level fields, mirror values to all existing subflows under locks, or apply an option to the initial subflow before connection establishment.

`mptcp_getsockopt()` similarly passes through after fallback, otherwise reports MPTCP-level mirrors or first-subflow TCP values. Diagnostic getters validate user-provided buffer headers, walk the subflow list under the MPTCP lock, copy `tcp_info` and address data into user arrays, and report how much was copied. `mptcp_sockopt_sync_locked()` is called when new subflows join; it suppresses latency-related subflow settings that would confuse scheduling, and syncs only when the subflow sequence differs from `msk->setsockopt_seq`.

## State and persistence

Option state persists primarily in `mptcp_sock`: `setsockopt_seq`, congestion-control name, cork/nodelay flags, keepalive values, maxseg, notsent lowat, receive INQ mode, socket-level marks/buffers/userlocks inherited from `struct sock`, and PM counters used by diagnostics. Subflows cache their last `setsockopt_seq` and `cached_sndbuf`. Fallback state redirects option semantics from MPTCP-level handling to TCP-level passthrough.

## Dependencies and integration points

This file integrates with generic socket option helpers, TCP option APIs, IPv4/IPv6 inet option state, UAPI MPTCP diagnostic structures, PM limit helpers, core write-space/readability helpers, and subflow iteration from `protocol.h`. It is called from `mptcp_prot` hooks in `protocol.c`, and `mptcp_sockopt_sync_locked()` is called when a subflow finishes joining.

## Risks and edge cases

Unsupported options are intentionally rejected or no-op; incorrectly broadening support can break multi-subflow semantics. Lock ordering matters because options are mirrored while holding the MPTCP socket and taking subflow locks. `setsockopt_seq` uses high bits from socket state so listener and accepted socket sync states do not collide. Diagnostic copy paths must validate user sizes to avoid ABI regression. Receive-low-water changes may force receive-buffer growth and must be mirrored to subflows without disturbing user-locked buffers.

## Test signals

Test signals include socket-option selftests before connect, after connect, after MP_JOIN, on listeners and accepted sockets, and after TCP fallback. Useful cases are cork/nodelay flushing, congestion-control propagation, keepalive propagation, buffer userlocks, `TCP_INQ`, `TCP_IS_MPTCP`, first-subflow fastopen options, MPTCP diagnostics with short and full buffers, and `SO_RCVLOWAT` readiness behavior.
