# sources/distributed-fs/ceph-client/net/netlabel/netlabel_domainhash.c

## Purpose
Central NetLabel domain-to-protocol mapping table. It maps LSM domains and optional address selectors to unlabeled, CIPSOv4, or CALIPSO label definitions, with RCU lookup for packet/socket fast paths and audited update operations.

## Important APIs, Types, And Functions
`netlbl_domhsh_tbl` holds buckets. Global state includes `netlbl_domhsh`, default IPv4/IPv6 mappings, and `netlbl_domhsh_lock`. Helpers handle RCU freeing, hashing, family matching, exact/default search, auditing, and validation. Public APIs initialize, add, remove whole entries/defaults/address selectors, get domain/address matches, and walk the hash table.

## Control Flow
Initialization allocates power-of-two buckets. Add validates entry family/protocol consistency, rejects duplicates, then inserts either a named bucket entry or default family entry. Address-selector additions can merge new selectors into an existing address-select mapping after duplicate checks. Removal marks entries invalid under the spinlock, unlinks or clears default pointers, audits, drops DOI references, and frees after RCU. Lookups run under caller-held RCU read lock and fall back to defaults.

## State And Persistence Behavior
Mappings persist in RCU-protected global hash/default pointers until explicitly removed. Entries carry `valid` bits to make removal visible before memory reclamation. Named domains own copied strings; DOI-backed mappings hold references that are released on removal.

## Dependencies And Integration Points
Depends on address-list helpers, audit helpers, CIPSO/CALIPSO DOI refcount APIs, RCU lists, and spinlocks. It is used by management netlink, KAPI socket/packet paths, and DOI removal code that cleans dependent mappings.

## Risks And Test Signals
Risks include default AF_UNSPEC splitting semantics, duplicate selector merge handling, RCU lifetime mistakes, `synchronize_rcu()` latency for selector deletes, and validation gaps for mixed family/protocol entries. Test signals should include concurrent lookup while add/remove, default fallback, selector specificity, DOI put on removal, duplicate rejection, and hash walk cursor behavior.
