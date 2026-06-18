# sources/distributed-fs/ceph-client/net/netlabel/netlabel_cipso_v4.h

## Purpose
Private declaration and userspace ABI description for the NetLabel CIPSOv4 Generic Netlink family.

## Important APIs, Types, And Functions
Defines command IDs for add, remove, list, and dump operations, and attribute IDs for DOI, mapping type, tag entries/lists, MLS level local/remote mappings, category local/remote mappings, and nested selector lists. Declares `netlbl_cipsov4_genl_init()`.

## Control Flow
The header documents the required payload shapes consumed by `netlabel_cipso_v4.c`: translated mappings require tag, level, and category lists; pass/local mappings require DOI, type, and tags only; list replies mirror the DOI mapping type.

## State And Persistence Behavior
No runtime state. It fixes the command and attribute numbers that userspace tools and kernel handlers must agree on, making it an ABI-sensitive file.

## Dependencies And Integration Points
Includes `net/netlabel.h` and references constants from `cipso_ipv4.h` in comments. It is consumed by the CIPSO netlink implementation and by global NetLabel netlink initialization.

## Risks And Test Signals
Risks include ABI drift, typo-prone nested attribute contracts, and mismatches with the netlink policy array. Test signals are userspace netlabelctl compatibility, attribute fuzzing, and build checks that `NLBL_CIPSOV4_A_MAX` matches the policy table.
