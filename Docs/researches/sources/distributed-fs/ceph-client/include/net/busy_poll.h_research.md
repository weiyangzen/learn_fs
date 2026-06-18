# sources/distributed-fs/ceph-client/include/net/busy_poll.h

## Purpose
This header defines network busy-poll support helpers. It provides NAPI ID validation, sysctl and socket busy-loop gates, busy-loop timeout helpers, wrappers around NAPI busy-loop execution, interrupt suspend/resume declarations, and inline propagation of NAPI IDs from receive packets to sockets.

## Important APIs, Types, And Constants
- `MIN_NAPI_ID` reserves `0` for unset and `1..NR_CPUS` for sender CPU values; valid NAPI IDs start at `NR_CPUS + 1`.
- `napi_id_valid()` checks that an ID can be used for busy polling.
- `BUSY_POLL_BUDGET` is the default per-loop budget when a socket-specific budget is not set.
- Under `CONFIG_NET_RX_BUSY_POLL`, `sysctl_net_busy_read` and `sysctl_net_busy_poll` control socket and poll/select busy-poll duration.
- `net_busy_loop_on()`, `sk_can_busy_loop()`, `busy_loop_current_time()`, `busy_loop_timeout()`, and `sk_busy_loop_timeout()` gate and time busy loops.
- `napi_busy_loop()` and `napi_busy_loop_rcu()` perform the polling; `napi_suspend_irqs()` and `napi_resume_irqs()` coordinate IRQ behavior.
- `sk_busy_loop()` invokes busy polling for a socket's cached NAPI ID.
- `skb_mark_napi_id()`, `sk_mark_napi_id()`, `sk_mark_napi_id_set()`, and once-only variants propagate receive queue/NAPI identity to packets and sockets.

## Control Flow And State
NIC receive/GRO code marks sk_buffs with the cached NAPI ID. Protocol handlers call `sk_mark_napi_id()` or setup variants to copy that ID and RX queue mapping to the socket. A blocking socket read or poll path can then call `sk_busy_loop()`; if the socket has a valid NAPI ID, enabled low-latency timeout, no pending signal, and optional nonblocking behavior, the code runs `napi_busy_loop()` with a loop-end callback and budget. Timeout helpers compare microsecond-shifted `ktime_get_ns()` values against sysctl or socket time limits.

## State And Persistence Behavior
State is runtime-only. NAPI identity is cached in `skb->napi_id`, `napi->gro.cached_napi_id`, and `sk->sk_napi_id`; receive queue mapping is updated through `sk_rx_queue_update()` or `sk_rx_queue_set()`. Busy-poll enablement comes from global sysctls and per-socket fields (`sk_ll_usec`, `sk_prefer_busy_poll`, `sk_busy_poll_budget`). Config-disabled builds compile most helpers to false/zero/no-op behavior.

## Dependencies And Integration Points
The header depends on netdevice, scheduler clock/signal state, IP/socket helpers, and XDP headers. Integration points include NIC receive handlers, GRO, TCP/UDP protocol receive paths, TCP child socket setup, poll/select/read paths, and sysctl configuration.

## Risks
- NAPI ID validity is subtle because low values overlap sender CPU reservations; treating any nonzero ID as valid can busy-poll the wrong target.
- Busy polling trades latency for CPU burn; timeout and signal checks must remain correct.
- Socket fields are accessed with `READ_ONCE`/`WRITE_ONCE`; removing those could introduce races with sysctl/socket option updates and receive paths.
- Config stubs must preserve type compatibility for builds without busy-poll support.

## Test Signals
- Networking tests should verify NAPI ID marking on receive, socket NAPI propagation for TCP/UDP and passive opens, busy-poll timeout behavior, signal interruption, per-socket budgets, and disabled-config no-op behavior.
- Performance tests should measure latency and CPU cost with busy polling enabled and disabled.
