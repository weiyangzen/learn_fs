# sources/distributed-fs/ceph-client/include/net/netns/ieee802154_6lowpan.h

Purpose: Defines per-net namespace state for IEEE 802.15.4 6LoWPAN fragmentation/reassembly.

Important APIs/types/functions: `struct netns_ieee802154_lowpan` stores a fragment queue directory pointer `fqdir`.

Control flow: 6LoWPAN receive paths use `fqdir` for fragment queueing and reassembly within a namespace.

State and persistence: Runtime fragment queue directory state, cleaned during namespace teardown.

Dependencies/integration: Depends on inet fragment infrastructure and IEEE 802.15.4 6LoWPAN code.

Risks/test signals: Test reassembly under namespace isolation, queue timeout cleanup, memory pressure behavior, and teardown with outstanding fragments.
