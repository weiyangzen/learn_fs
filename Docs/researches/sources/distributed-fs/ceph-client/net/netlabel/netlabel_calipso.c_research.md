# sources/distributed-fs/ceph-client/net/netlabel/netlabel_calipso.c

## Purpose
CALIPSO/IPv6 NetLabel glue. It exposes the Generic Netlink family for CALIPSO DOI administration and provides wrapper entry points used by the rest of NetLabel to call the actual CALIPSO packet engine registered through `netlbl_calipso_ops_register()`.

## Important APIs, Types, And Functions
Important local types are `netlbl_calipso_doiwalk_arg` for multipart DOI dumps and `netlbl_domhsh_walk_arg` for removing domain mappings tied to a DOI. The exported registration API is `netlbl_calipso_ops_register()`. Netlink handlers implement `ADD`, `REMOVE`, `LIST`, and `LISTALL` through `netlbl_calipso_add()`, `netlbl_calipso_remove()`, `netlbl_calipso_list()`, and `netlbl_calipso_listall()`. Public wrappers include `calipso_doi_add/remove/getdef/putdef/walk`, socket/request/sk_buff label operations, option parsing, and cache operations.

## Control Flow
`ADD` requires DOI and mapping type, currently accepts `CALIPSO_MAP_PASS`, allocates `struct calipso_doi`, then delegates to `calipso_doi_add()`. `LIST` gets a referenced DOI definition, emits type data into a reply skb, and releases the reference. `LISTALL` streams DOI/type pairs using the packet engine walk cursor stored in `cb->args[0]`. `REMOVE` first walks the domain hash and removes all CALIPSO mappings for the DOI, then removes the DOI itself and decrements `netlabel_mgmt_protocount` on success.

## State And Persistence Behavior
The only local persistent state is the global `calipso_ops` pointer and the `__ro_after_init` Generic Netlink family. DOI state, label caches, and references live in the IPv6 CALIPSO engine. Mapping persistence is coordinated through `netlabel_domainhash.c`; protocol enablement is reflected in `netlabel_mgmt_protocount`.

## Dependencies And Integration Points
Depends on Generic Netlink, audit helpers, `net/calipso.h`, domain hash walking/removal, and the management protocol count. The file is compiled only when IPv6 CALIPSO support is relevant, while `netlabel_calipso.h` provides a no-op init when IPv6 is disabled.

## Risks And Test Signals
Risks include a missing or late CALIPSO ops registration, limited netlink support for only pass-through mappings, stale mappings if domain-hash removal partially fails, and refcount misuse around DOI get/put wrappers. Test signals should cover netlink add/list/listall/remove, remove with attached domain mappings, no-ops when IPv6/CALIPSO ops are absent, and cache/socket/sk_buff wrapper delegation.
