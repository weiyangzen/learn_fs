<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_addrlist.c -->
# sources/distributed-fs/ceph-client/net/netlabel/netlabel_addrlist.c

## Purpose
`netlabel_addrlist.c` implements ordered IPv4 and IPv6 address-list helpers for NetLabel domain and protocol mappings. It supports longest-prefix-style search, exact search, add, remove, and audit formatting.

## Important APIs, Types, and Functions
IPv4 APIs are `netlbl_af4list_search()`, `netlbl_af4list_search_exact()`, `netlbl_af4list_add()`, `netlbl_af4list_remove_entry()`, `netlbl_af4list_remove()`, and `netlbl_af4list_audit_addr()`. IPv6 equivalents are compiled when `CONFIG_IPV6` is enabled: `netlbl_af6list_search()`, `netlbl_af6list_search_exact()`, `netlbl_af6list_add()`, `netlbl_af6list_remove_entry()`, `netlbl_af6list_remove()`, and `netlbl_af6list_audit_addr()`.

## Control Flow, State, and Persistence
Search walks RCU-protected lists and returns the first valid entry whose masked address matches; ordering by mask width makes the first hit the most specific. Add first checks for an exact duplicate, then inserts before the first less-specific entry or at the tail. Remove marks an entry invalid and unlinks with `list_del_rcu()`, leaving memory reclamation to callers after RCU safety. Audit helpers format address and prefix length into an audit buffer.

## Dependencies and Integration Points
The file depends on Linux list/RCU primitives, IPv4/IPv6 address helpers, and audit logging. It is used by NetLabel domain and unlabeled/CIPSO/CALIPSO management code that owns list locks and entry lifetimes.

## Risks and Test Signals
Risks include caller lock/RCU misuse, invalid entries remaining visible to unsafe iteration, duplicate detection relying on search ordering, non-contiguous mask prefix reporting, IPv6 conditional compilation, and memory lifetime after removal. Tests should cover longest-prefix lookup ordering, exact duplicate rejection, removal under RCU readers, IPv4 and IPv6 masks, empty lists, audit output with full and partial masks, and caller-side `synchronize_rcu()` before freeing removed entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_addrlist.c -->
