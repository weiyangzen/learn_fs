<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_state.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_state.c

## Purpose
`xt_state.c` implements the legacy `state` match for conntrack state. It is a smaller predecessor to `conntrack`.

## Important APIs, Types, and Functions
`state_mt()` consumes `struct xt_state_info`, calls `nf_ct_get()`, maps the conntrack info to state bits, and compares with `statemask`. `state_mt_check()` and `state_mt_destroy()` pin and release conntrack support.

## Control Flow, State, and Persistence
The matcher classifies packets as tracked conntrack state, untracked, or invalid. It returns whether the configured state mask contains the resulting bit. It does not inspect tuple fields or status beyond state and persists no state itself.

## Dependencies and Integration Points
The module depends on conntrack namespace enablement and x_tables. It registers an NFPROTO_UNSPEC match with IPv4 and IPv6 aliases.

## Risks and Test Signals
Risks include legacy semantics differing from `conntrack`, untracked versus invalid classification, and conntrack support reference management. Tests should cover NEW, ESTABLISHED, RELATED, INVALID, UNTRACKED, no conntrack, IPv4/IPv6, and unload after rules are removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_state.c -->
