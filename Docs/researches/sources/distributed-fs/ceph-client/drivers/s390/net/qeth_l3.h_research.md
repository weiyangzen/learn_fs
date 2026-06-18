# sources/distributed-fs/ceph-client/drivers/s390/net/qeth_l3.h

Purpose: declares the layer 3 qeth address model and L3 sysfs/main cross-file interfaces.

Important APIs and types: `enum qeth_ip_types` distinguishes normal IPs, VIPA, and RXIP. `struct qeth_ipaddr` represents IPv4/IPv6 addresses, multicast flag, disposition flag, IP takeover status, reference count, masks/prefix lengths, and hash linkage. `struct qeth_ipato_entry` stores takeover prefix entries. Inline helpers initialize, compare, and hash addresses. Exports include routing setters, IPATO add/delete/update, HSUID modification, and RXIP/VIPA modification.

Control flow: inline matching separates by-IP matching from full matching. Full matching requires equal type and mask/prefix and is used after locating an address by hash. The hash chooses IPv4 or IPv6 hash helpers by protocol.

State and persistence: describes runtime address state in `card->ip_htable`, multicast state in `card->rx_mode_addrs`, and takeover entries in `card->ipato.entries`. Refcounts allow duplicate normal-address notifier events without duplicate hardware registrations.

Dependencies and integration: depends on `qeth_core.h`, Linux hashtables, IPv6 helpers, and L3 main/sysfs users. It is the shared contract for inet notifier, sysfs VIPA/RXIP/IPATO, and online recovery paths.

Risks: comparing only by IP for lookup means full-match validation is mandatory before deleting or coalescing normal addresses with different masks. Any new address type must preserve takeover and refcount semantics.

Test signals: unit-style checks for IPv4/IPv6 hash/match behavior, duplicate normal address refcounts, VIPA/RXIP duplicate rejection, and IPATO prefix matching against masks and inversion.
