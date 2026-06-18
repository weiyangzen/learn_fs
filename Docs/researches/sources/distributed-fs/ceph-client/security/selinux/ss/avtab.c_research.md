<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/avtab.c -->
# sources/distributed-fs/ceph-client/security/selinux/ss/avtab.c

## Purpose
Implements SELinux access vector tables, the hashed policy structures that store type enforcement access vectors, type transition/member/change rules, and extended permission rules. It provides allocation, insertion, search, destruction, policy binary read/write, debug statistics, and slab cache setup.

## Important APIs, Types, and Functions
Public functions include `avtab_init()`, `avtab_alloc()`, `avtab_alloc_dup()`, `avtab_destroy()`, `avtab_insert_nonunique()`, `avtab_search_node()`, `avtab_search_node_next()`, `avtab_read_item()`, `avtab_read()`, `avtab_write_item()`, `avtab_write()`, and `avtab_cache_init()`. Internal helpers include `avtab_hash()`, `avtab_insert_node()`, `avtab_node_cmp()`, `avtab_insert()`, and `avtab_insertf()`.

## Control Flow
Allocation sizes the hash as a power-of-two bucket count based on rule count. Insert walks the sorted bucket chain and rejects duplicate non-extended-permission rules, while conditional-policy callers may use nonunique insertion. Search uses the same ordering to stop early. Policy read supports pre-`POLICYDB_VERSION_AVTAB` legacy encoding and modern 16-bit key encoding, validates type/class values and specifier exclusivity, then inserts decoded data. Write serializes each node with little-endian key and either data word or extended-permission payload.

## State and Persistence
State is `struct avtab` with bucket array, element count, slot count, and mask. Nodes and extended-permission payloads come from dedicated kmem caches. Persisted form is the binary SELinux policy stream read and written through `policy_file`.

## Dependencies and Integration Points
Depends on `policydb` validation, binary policy I/O helpers, `hash.h` `av_hash()`, bitops/hweight, policy version constants, and conditional policy code that stores enabled flags in `specified`.

## Risks
`avtab_node_cmp()` masks conditional enabled bits and treats overlapping specifier masks as equality, so changes can break duplicate detection and search iteration. Policy-version gates for xperms and conditional xperms are compatibility-sensitive. `avtab_write_item()` sizes its local buffer using the xperms union member even for non-xperms nodes, which is currently safe due to compile-time layout but subtle.

## Test Signals
Load policies with AV, type, and xperm rules; reject duplicate nonconditional rules; accept conditional nonunique rules; verify legacy policy decoding; fuzz truncated/overflow/invalid type/class/specifier encodings; dump/reload policies; and inspect hash stats in debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/avtab.c -->
