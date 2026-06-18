# sources/distributed-fs/ceph-client/net/netlabel/netlabel_cipso_v4.c

## Purpose
CIPSO/IPv4 NetLabel administration layer. It registers the CIPSOv4 Generic Netlink family and translates userspace DOI mapping requests into `cipso_v4_doi` definitions for the IPv4 CIPSO engine.

## Important APIs, Types, And Functions
Local walk-argument structs support DOI dumps and domain-hash cleanup. `netlbl_cipsov4_genl_policy` defines DOI, mapping type, tag list, MLS level, and category attributes. Key handlers are `netlbl_cipsov4_add_common()`, `netlbl_cipsov4_add_std()`, `netlbl_cipsov4_add_pass()`, `netlbl_cipsov4_add_local()`, `netlbl_cipsov4_add()`, `netlbl_cipsov4_list()`, `netlbl_cipsov4_listall()`, and `netlbl_cipsov4_remove()`. `netlbl_cipsov4_genl_init()` registers the family.

## Control Flow
`ADD` validates DOI/type, then dispatches by mapping type. Standard translated mappings parse nested tag, level, and optional category lists twice: first to size local/remote arrays and then to fill bidirectional mappings initialized to invalid sentinels. Pass and local mappings only need common DOI/tag parsing. `LIST` builds a reply from the current DOI definition under RCU and retries larger skbs for translated maps. `REMOVE` removes matching domain mappings before removing the DOI.

## State And Persistence Behavior
Persistent DOI definitions are owned by the CIPSO engine. This file mutates global protocol state only through `netlabel_mgmt_protocount` after DOI add/remove. Netlink dump cursors are stored in callback args. Domain mapping cleanup persists in the domain hash and drops DOI references there.

## Dependencies And Integration Points
Depends on Generic Netlink, RCU, audit helpers, `net/cipso_ipv4.h`, `netlabel_domainhash`, and management counters. It integrates with KAPI and management code indirectly through the shared CIPSO DOI registry and domain hash.

## Risks And Test Signals
Risks include malformed nested netlink attributes, memory sizing mistakes for translated MLS arrays, retry exhaustion in `LIST`, mismatched DOI reference lifetime during removal, and policy looseness from deprecated non-strict validation. Test signals should include add/list/remove for all mapping types, invalid tag/level/category bounds, multipart dumps, domain-map cleanup on DOI removal, and leak/refcount checks on failure paths.
