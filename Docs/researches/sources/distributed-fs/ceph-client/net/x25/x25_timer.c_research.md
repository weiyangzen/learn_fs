# sources/distributed-fs/ceph-client/net/x25/x25_timer.c

Purpose: owns per-socket X.25 timers: heartbeat, T2 acknowledgement holdback, T21 call request, T22 reset request, and T23 clear request.

Important APIs/functions: `x25_init_timers()`, `x25_start_heartbeat()`, `x25_stop_heartbeat()`, `x25_start_t2timer()`, `x25_start_t21timer()`, `x25_start_t22timer()`, `x25_start_t23timer()`, `x25_stop_timer()`, and `x25_display_timer()` are used by socket and state-machine code.

Control flow: heartbeat runs every five seconds, destroys dead listen children in state 0, and in connected state calls `x25_check_rbuf()` when the socket is not owned by userspace. The protocol timer interprets expiry by current X.25 state: T2 sends a pending RR/RNR enquiry response, T21/T22 send clear request and enter state 2 with T23 running, and T23 disconnects with `ETIMEDOUT`. If the socket is user-owned in state 3, T2 is restarted.

State and persistence: timers are in `x25_sock->timer` and `sk->sk_timer`; they mutate state, condition flags, queues, and socket errors indirectly through helper calls.

Dependencies and integration: integrates Linux timer APIs, socket BH locking, input/output/subroutine helpers, and sysctl-seeded timer durations.

Risks and test signals: timer expiry races with userspace socket locks and teardown. Tests should cover each state-specific expiry, heartbeat destruction of unaccepted dead sockets, user-owned restart behavior, timer display, stopping timers on disconnect/release, and no use-after-free during delayed destroy.
