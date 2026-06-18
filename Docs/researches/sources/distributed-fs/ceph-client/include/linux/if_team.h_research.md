# `sources/distributed-fs/ceph-client/include/linux/if_team.h`

Purpose: internal network team device API for port state, mode callbacks, options, per-CPU stats, queue override, netpoll forwarding, and mode registration.

Important APIs/types/functions: `struct team_pcpu_stats`, `struct team_port`, port enabled/txable helpers, `team_netpoll_send_skb`, `struct team_mode_ops`, `struct team_option`, `struct team_mode`, `struct team`, `team_dev_queue_xmit`, tx-port hash/index helpers, first-txable lookup, option register/unregister, mode register/unregister, and `MODULE_ALIAS_TEAM_MODE`.

Control flow and state: persistent team state owns port lists, tx-enabled hash buckets, option lists, selected mode operations, notification delayed work, multicast rejoin work, queue override lists, and mode-private storage. Inline TX path restores queue mapping, changes `skb->dev` to the selected port, and either netpoll-sends or calls `dev_queue_xmit`.

Dependencies/integration: depends on netpoll, qdisc control block, UAPI team options, RCU lists, delayed work, and netdevice LAG semantics.

Risks: RCU and list traversal must match port lifetime; tx index hashing assumes enabled-port count consistency; queue mapping uses qdisc skb CB layout asserted by `BUILD_BUG_ON`; mode callbacks must handle link/user state transitions; delayed work cleanup is critical on teardown.

Test signals: team mode module registration, port add/remove under traffic, failover/load-balance transmit, queue override mapping, netpoll transmit, option setter/getter change notifications, and lockdep/RCU stress.
