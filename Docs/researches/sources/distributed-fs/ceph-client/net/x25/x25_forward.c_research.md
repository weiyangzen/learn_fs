# sources/distributed-fs/ceph-client/net/x25/x25_forward.c

Purpose: implements simple X.25 call/data forwarding between devices when no local listener accepts an incoming call.

Important APIs/functions: `x25_forward_call()` routes and records a forwarded LCI pair, `x25_forward_data()` forwards later packets by LCI, and `x25_clear_forward_by_lci()` / `x25_clear_forward_by_dev()` remove forwarding state.

Control flow: call forwarding finds a route for the destination, gets the outgoing neighbour, rejects loops where the route returns to the ingress device, checks for duplicate LCI entries, records device pairs in `x25_forward_list`, clones the call skb, and transmits it on the new neighbour. Data forwarding finds the opposite device for the LCI, gets its neighbour, copies the skb, and sends it.

State and persistence: forwarding state is a runtime global list of `x25_forward` entries protected by `x25_forward_list_lock`; entries are removed on clear confirmation, device removal, or neighbour kill.

Dependencies and integration: called from `x25_dev.c` and `af_x25.c`, gated by `sysctl_x25_forward`, and depends on route and neighbour lookup plus `x25_transmit_link()`.

Risks and test signals: forwarding keys only on LCI and device pair, so duplicate LCIs and loop avoidance are important. Tests should cover no-route, same-device route, allocation/clone failures, bidirectional data forwarding, clear-confirmation cleanup, device down cleanup, and proc display of active forwards.
