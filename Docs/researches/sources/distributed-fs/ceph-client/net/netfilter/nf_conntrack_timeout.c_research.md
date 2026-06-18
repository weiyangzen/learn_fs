<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_timeout.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_timeout.c

## Purpose
Provides the runtime glue for named conntrack timeout policies. It attaches timeout policy objects to conntracks, removes references when policies are deleted or connections die, and exposes an RCU hook table implemented by the timeout subsystem.

## Important APIs, Types, and Functions
Exports `nf_ct_timeout_hook`, `nf_ct_untimeout()`, `nf_ct_set_timeout()`, and `nf_ct_destroy_timeout()`. Internal helpers are `untimeout()` and `__nf_ct_timeout_put()`. State is stored in the `struct nf_conn_timeout` extension with an RCU pointer to `struct nf_ct_timeout`.

## Control Flow
`nf_ct_set_timeout()` enters RCU, finds the hook table, looks up a named policy, validates L3 and L4 protocol match, attaches a timeout extension with `nf_ct_timeout_ext_add()`, and returns errors for missing hooks/policies, protocol mismatch, or allocation failure. `nf_ct_untimeout()` iterates conntracks in a net namespace and clears matching timeout pointers. Destroy releases the referenced policy through `timeout_put()`.

## State and Persistence
The global hook pointer is RCU-published by another module. Per-connection timeout policy references persist until cleared by policy deletion, connection destruction, or explicit replacement. Reference counts are owned by hook callbacks.

## Dependencies and Integration Points
Depends on conntrack core iteration, extension storage, L4 protocol descriptors, timeout policy hooks, and callers such as `xt_CT`, conntrack netlink, OVS conntrack, and BPF conntrack helpers.

## Risks
RCU and policy reference lifetimes must stay balanced, especially on validation failure after `timeout_find_get()`. Protocol mismatch checks prevent attaching an incompatible timeout array. Iterating all conntracks for policy deletion can be expensive but avoids stale pointers.

## Test Signals
Configure named timeout policies, attach through CT target/OVS/netlink, verify L3/L4 mismatch errors, delete a policy and confirm existing conntracks clear references, destroy conntracks with policies, and test no-hook/no-policy error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_timeout.c -->
