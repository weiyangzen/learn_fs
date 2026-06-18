# sources/distributed-fs/ceph-client/fs/afs/addr_list.c

## Purpose
`addr_list.c` manages RxRPC peer address lists for AFS servers and VL servers, including allocation/refcounting, parsing textual address lists, DNS lookup results, merging IPv4/IPv6 peers, and updating peer appdata pointers.

## Important APIs, types, and functions
Key functions are `afs_alloc_addrlist()`, `afs_get_addrlist()`, `afs_put_addrlist()`, `afs_parse_text_addrs()`, `afs_dns_query()`, `afs_merge_fs_addr4()`, `afs_merge_fs_addr6()`, and `afs_set_peer_appdata()`.

## Control flow
Address lists are allocated with bounded capacity and freed by RCU after peer references are dropped. Text parsing counts delimited addresses, supports bracketed IPv6 and optional `+port`, parses addresses, creates RxRPC peers, and stores them in a single dummy VL-server list. DNS lookup queries AFSDB/SRV data and either extracts structured VL records or parses comma-delimited addresses. Merge functions de-duplicate and keep IPv4 and IPv6 peer ranges ordered by peer pointer.

## State and persistence
Runtime state includes refcounted `afs_addr_list` objects, RxRPC peer references, `nr_ipv4`, total address count, and per-peer appdata pointing back to an AFS server. No state persists beyond memory caches and DNS TTL consumers.

## Dependencies and integration points
It depends on DNS resolver, RxRPC peer lookup, VL server list allocation, net namespace sockets, `afs_fs.h`/VL constants, and address preferences applied elsewhere.

## Risks and test signals
Risks include parser corner cases, duplicate peer handling, peer pointer ordering assumptions, appdata clearing bugs, DNS malformed data, and address-list truncation at `AFS_MAX_ADDRESSES`. Test signals include IPv4/IPv6/bracket/port parsing, invalid inputs, DNS good/bad/empty results, duplicate addresses, peer appdata replacement, and RCU refcount lifetimes.
