# sources/distributed-fs/ceph-client/include/net/netns/xfrm.h

Purpose: Defines per-network-namespace IPsec/XFRM state and policy databases.

Important APIs/types/functions: `xfrm_policy_hash` and `xfrm_policy_hthresh` describe policy hash tables and threshold updates. `struct netns_xfrm` stores all state lists, state hash tables by destination/source/SPI/sequence, per-cpu input cache, hash masks/counts/work, policy lists/index hashes/destination hashes/counts/work, inexact bins, netlink socket pointers, sysctls, default policies, dst ops, locks, generation seqcounts, config mutex, and NAT keepalive work.

Control flow: XFRM state/policy add/delete/lookup paths mutate protected tables and generation counters. Netlink operations use namespace netlink sockets and config mutex. Hash resize work updates state/policy tables. Packet paths consult state caches and policy hashes.

State and persistence: Runtime per-net security association and policy state. Protected by spinlocks, mutex, seqcount, RCU, workqueues, and delayed work.

Dependencies/integration: Depends on XFRM core/uapi, dst ops, netlink, workqueues, rhashtable/list infrastructure, IPv6 optional dst ops, sysctl, and NAT keepalive.

Risks/test signals: Test concurrent SA/policy add/delete/lookup, hash resize, generation seqcount readers, netlink socket teardown, namespace cleanup with delayed work, default policy sysctls, IPv6 config, and NAT keepalive cancellation.
