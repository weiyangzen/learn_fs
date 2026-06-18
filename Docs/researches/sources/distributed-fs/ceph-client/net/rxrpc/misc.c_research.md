<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/misc.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/misc.c

## Purpose
`misc.c` centralizes AF_RXRPC runtime tunables and protocol defaults used by receive windows, delayed ACK scheduling, backlog sizing, jumbo packet handling, and optional receive-delay injection.

## Important APIs, Types, And Functions
The file exports global variables: `rxrpc_max_backlog`, `rxrpc_soft_ack_delay`, `rxrpc_idle_ack_delay`, `rxrpc_rx_window_size`, `rxrpc_rx_mtu`, `rxrpc_rx_jumbo_max`, and, when enabled, `rxrpc_inject_rx_delay`.

## Control Flow
There is no executable control flow. Other rxrpc subsystems read these variables to decide how many calls can be queued, when DELAY or IDLE ACKs should be scheduled, how many unconsumed packets may be retained, and what jumbo/PMTU capacity should be advertised.

## State And Persistence
The variables are process-global kernel module state rather than per-network namespace state. Defaults persist for the module lifetime. Some are marked `__read_mostly`; optional injection state exists only for builds with `CONFIG_AF_RXRPC_INJECT_RX_DELAY`.

## Dependencies And Integration Points
Receive-side ACK logic uses the delay/window values, ACK trailers in `output.c` advertise MTU/window values, PMTU handling uses `rxrpc_rx_mtu` and jumbo limits, socket listen paths use the backlog limit, and test/fault-injection paths use the delay knob.

## Risks And Edge Cases
Because the values are global, tuning one namespace affects all namespaces. Oversized receive windows or jumbo MTUs increase memory pressure; too-small windows or ACK delays can harm throughput. Fault-injection variables must not leak into production behavior unless explicitly configured.

## Test Signals
Useful signals include sysctl/module-parameter style coverage if wired elsewhere, ACK delay behavior under partial receives, receive-window overflow ACKs, jumbo advertisement correctness, and builds with and without receive-delay injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/misc.c -->
