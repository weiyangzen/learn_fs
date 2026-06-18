<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_connmark.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_connmark.c

## Purpose
`xt_connmark.c` implements the x_tables `CONNMARK` target and `connmark` match. It copies, sets, saves, restores, and tests marks stored on `struct nf_conn`, allowing packet classification state to persist across packets in the same connection.

## Important APIs, Types, and Functions
The core target path is `connmark_tg_shift()`, wrapped by revision-specific `connmark_tg()` and `connmark_tg_v2()`. It consumes `struct xt_connmark_tginfo1` or `struct xt_connmark_tginfo2`, supports `XT_CONNMARK_SET`, `XT_CONNMARK_SAVE`, and `XT_CONNMARK_RESTORE`, and uses `ctmark`, `ctmask`, `nfmask`, `shift_dir`, and `shift_bits`. The match path is `connmark_mt()` using `struct xt_connmark_mtinfo1`. Registration happens through `connmark_tg_reg[]` and `connmark_mt_reg`.

## Control Flow, State, and Persistence
On each target invocation, `nf_ct_get()` retrieves the connection. Missing conntrack state leaves the packet untouched with `XT_CONTINUE`. SET rewrites `ct->mark` from the configured constant and mask, SAVE copies selected `skb->mark` bits into `ct->mark`, and RESTORE copies selected `ct->mark` bits back into `skb->mark`. Revision 2 optionally shifts the selected value before storage or restoration. Connection mark updates use `READ_ONCE()`/`WRITE_ONCE()` and emit `nf_conntrack_event_cache(IPCT_MARK, ct)` when the persistent conntrack mark changes.

## Dependencies and Integration Points
The module depends on conntrack namespace enablement through `nf_ct_netns_get()` and releases it through `nf_ct_netns_put()` in target and match destructors. It integrates with IPv4 and optional IPv6 iptables aliases and with conntrack event listeners that observe mark changes.

## Risks and Test Signals
Risks include mask/xor semantics being misunderstood as assignment, shifts losing bits before masks are applied, missing conntrack making targets no-ops, and concurrent readers observing only best-effort mark updates. Tests should cover SET/SAVE/RESTORE, all masks, both shift directions, IPv4 and IPv6 registration, no-conntrack packets, event emission on changed marks only, and inverted `connmark` matches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_connmark.c -->
