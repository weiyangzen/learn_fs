# sources/distributed-fs/ceph-client/net/netlabel/netlabel_unlabeled.c

## Purpose
Unlabeled-packet support for NetLabel. It manages static fallback labels by interface and source address, exposes a Generic Netlink interface for those labels and the accept flag, and supplies receive-side security attributes when packets lack protocol labels.

## Important APIs, Types, And Functions
Local persistent types include `netlbl_unlhsh_tbl`, IPv4/IPv6 address entries with secids, and per-interface `netlbl_unlhsh_iface`. Public functions are `netlbl_unlabel_genl_init()`, `netlbl_unlabel_init()`, `netlbl_unlhsh_add()`, `netlbl_unlhsh_remove()`, `netlbl_unlabel_getattr()`, and `netlbl_unlabel_defconf()`. Netlink handlers cover accept/list, static add/remove/list, and default static add/remove/list.

## Control Flow
Static add resolves an interface in `init_net` or default interface, creates an interface bucket entry if needed, inserts an ordered address-list entry, audits, and increments the protocol count. Remove deletes the matching address entry, audits, conditionally removes now-empty interface entries, and decrements the count. Device-down notifications invalidate and RCU-free matching interface entries. Netlink parsing converts LSM security contexts to secids and enforces one address family per entry. Listing walks hash buckets, interface chains, and address-list cursors through `cb->args`.

## State And Persistence Behavior
State is global: RCU hash table `netlbl_unlhsh`, default interface pointer, `netlabel_unlabel_acceptflg`, netdevice notifier, address entries with secids, and Generic Netlink family metadata. The default boot configuration allows unlabeled packets and installs a default unlabeled domain mapping through the domain hash.

## Dependencies And Integration Points
Depends on address-list helpers, audit, LSM secctx/secid conversion, netdevice lookup/notifiers, Generic Netlink, domain-hash default configuration, and management protocol count. It is the final fallback used by `netlbl_skbuff_getattr()`.

## Risks And Test Signals
Risks include namespace limitations despite namespace-looking parameters, device-down cleanup races, IPv6 add helper returning 0 after nonzero add failures, accept-flag policy surprises, static-list cursor bugs, and protocol count imbalance on notifier cleanup. Test signals should cover static add/remove/list for interface/default and IPv4/IPv6, receive lookup by `skb_iif` and source address, accept flag off/on, device-down cleanup, and LSM context conversion failures.
