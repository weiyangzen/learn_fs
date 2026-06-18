# sources/distributed-fs/ceph-client/fs/afs/addr_prefs.c

## Purpose
`addr_prefs.c` implements `/proc/fs/afs/addr_prefs`, allowing administrators to assign priorities to IPv4/IPv6 address or subnet matches and apply those priorities to server address lists.

## Important APIs, types, and functions
Public functions are `afs_proc_addr_prefs_write()`, `afs_get_address_preferences_rcu()`, and `afs_get_address_preferences()`. Internal helpers include `afs_split_string()`, `afs_parse_address()`, `afs_cmp_address_pref()`, `afs_insert_address_pref()`, `afs_add_address_pref()`, `afs_delete_address_pref()`, and `afs_del_address_pref()`.

## Control flow
Proc writes are parsed into line commands such as `add udp IP[/mask] priority` or `del udp IP[/mask]`. A candidate preference list is copied from the old RCU list, modified in sorted IPv4-then-IPv6 order, versioned, published through RCU, and paired with release-store version updates. Address-list application checks versions, walks peers, compares exact/subnet matches, and writes per-address priorities.

## State and persistence
State is runtime per-network-namespace RCU data: `address_prefs`, `address_pref_version`, and each address list's `addr_pref_version` plus per-address `prio`. Preferences do not persist across module/netns lifetime.

## Dependencies and integration points
It depends on procfs seq-file netns mapping, RxRPC remote-address access, Linux IP parsers, RCU, and AFS server rotation using address priorities.

## Risks and test signals
Risks include command parser ambiguity, subnet comparison ordering, version memory-ordering mistakes, list growth to 255 entries, and missed priority updates. Test signals include add/delete exact and subnet IPv4/IPv6 rules, malformed masks, multiple commands per write, RCU readers during updates, version no-op paths, and route selection with priorities.
