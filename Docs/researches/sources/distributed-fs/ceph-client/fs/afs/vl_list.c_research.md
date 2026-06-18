<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/vl_list.c -->
# sources/distributed-fs/ceph-client/fs/afs/vl_list.c

## Purpose
Allocates, refcounts, parses, sorts, updates, and frees VL server records and weighted VL server lists from DNS resolver payloads.

## Important APIs, Types, And Functions
Exports `afs_alloc_vlserver()`, `afs_put_vlserver()`, `afs_alloc_vlserver_list()`, `afs_put_vlserverlist()`, and `afs_extract_vlserver_list()`. Internal helpers parse little-endian DNS server-list fields and extract IPv4/IPv6 address lists into `afs_addr_list`.

## Control Flow
`afs_extract_vlserver_list()` validates DNS server-list v1 payloads, snapshots the previous VL list, parses each server record, reuses matching prior VL server objects by name/port, extracts addresses, updates server address RCU pointer when nonempty, drops empty new records without old addresses, and insertion-sorts entries by lower priority then higher weight.

## State And Persistence
VL servers and lists are refcounted and RCU-freed. Server address pointers are replaced under `vlserver->lock`; list entries track DNS source/status, priority, weight, and preferred index. State is memory-only and refreshed from DNS/config.

## Dependencies And Integration Points
Uses DNS resolver server-list ABI, address merge helpers, RxRPC peer-backed address lists, cell `vl_servers`, VL probing/rotation, and procfs VL diagnostics.

## Risks And Edge Cases
Malformed DNS payloads trigger debug dumps. Empty address lists must preserve existing addresses when possible. Protocol must be UDP or unspecified. Duplicate handling is TODO, so duplicate records can affect ordering/probing.

## Test Signals
Parse AFSDB/SRV/NSS/config payloads with IPv4, IPv6, empty, malformed, duplicate, non-UDP, weighted, and priority-varied records; verify previous-server reuse and RCU address replacement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/vl_list.c -->
