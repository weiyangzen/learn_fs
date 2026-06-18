# sources/distributed-fs/ceph-client/net/ipv6/calipso.c

## Purpose
Implements the IPv6 CALIPSO security label option from RFC 5570 for NetLabel. It manages Domain of Interpretation (DOI) definitions, maps MLS levels/categories to CALIPSO hop-by-hop options, validates and parses packet labels, attaches/removes labels from sockets, request sockets, and skbs, and provides a small label mapping cache.

## Important APIs, Types, and Functions
Important global state includes `calipso_doi_list`, `calipso_doi_list_lock`, `calipso_cache`, `calipso_cache_enabled`, and `calipso_cache_bucketsize`. DOI APIs are `calipso_doi_add()`, `calipso_doi_remove()`, `calipso_doi_getdef()`, `calipso_doi_putdef()`, and `calipso_doi_walk()`. Cache APIs include `calipso_cache_check()`, `calipso_cache_add()`, and `calipso_cache_invalidate()`. Option helpers include `calipso_validate()`, `calipso_genopt()`, `calipso_opt_insert()`, `calipso_opt_del()`, `calipso_opt_getattr()`, and skb/socket/request accessors. `struct netlbl_calipso_ops ops` binds the file to NetLabel.

## Control Flow
Initialization allocates cache buckets and registers NetLabel ops. DOI add/remove updates an RCU list and emits audit records. Option generation aligns CALIPSO at 4n+2, writes DOI/level/category bitmap, pads to IPv6 option alignment, and computes CRC-CCITT. Receive validation verifies CRC and DOI existence, then decodes level/categories through DOI mapping, optionally using the cache. Socket/request setters rebuild IPv6 hop options with CALIPSO inserted or replaced. SKB setters grow or shrink packet header space, update payload length, add/remove hop-by-hop headers when needed, and preserve surrounding options.

## State and Persistence
Runtime state is DOI definitions with refcounts and RCU lifetime, mapping-cache buckets with activity-based list ordering, socket/request `ipv6_txoptions`, and mutated skb hop options. Cache invalidation happens on DOI final put and exit. There is no persistent storage.

## Dependencies and Integration Points
Depends on NetLabel LSM security attributes, audit logging, IPv6 option helpers, CRC-CCITT, RCU/spinlocks, skb copy-on-write, TCP request sockets, and `ipv6_renew_options()`. `exthdrs.c` calls `calipso_validate()` when parsing hop-by-hop options.

## Risks and Test Signals
Risks include option length/alignment errors, stale cache entries after DOI changes, duplicate cache keys, checksum/CRC mismatches, skb header growth/shrink corner cases, and partial SYN-cookie request-socket limitations. Test signals include DOI add/remove audit logs, cache hit/miss behavior, valid/invalid CRC packets, large category maps near option limits, socket label set/get/delete, request-socket inheritance, skb label insertion/removal, and NetLabel policy tests.
