# sources/distributed-fs/ceph-client/arch/alpha/kernel/gct.c

**Purpose:** Implements recursive search over Alpha Generic Configuration Tree version 6 nodes. It validates node magic, compares node type/subtype against a caller-provided search table, invokes matching callouts, and traverses sibling and child links.

**Important APIs/types/functions:** Exposes `gct6_find_nodes(gct6_node *node, gct6_search_struct *search)`. It uses `gct6_node`, `gct6_search_struct`, `GCT_NODE_MAGIC`, and `GCT_NODE_PTR()` from `<asm/gct.h>`.

**Control flow:** The function first verifies `node->magic`; if invalid it logs an error and returns `-EINVAL`. It then walks the search array until a zero type/subtype sentinel, calling `wanted->callout(node)` for each matching type/subtype. It recurses to `node->next` first, then to `node->child`, ORing return statuses.

**State and persistence behavior:** No owned state. It reads firmware-provided GCT memory and calls external callbacks that may mutate platform setup state. The traversal result is an aggregate status, not a stored cursor.

**Dependencies and integration points:** Used by platform discovery code that parses HWRPB/GCT firmware tables. Depends on valid firmware offsets that `GCT_NODE_PTR()` can translate into kernel addresses.

**Risks:** Recursive traversal trusts firmware tree structure; cycles or corrupt offsets could recurse indefinitely or fault. ORing negative statuses can obscure exact error codes. Callouts have no return channel, so callback failures cannot be propagated unless they mutate external state.

**Test signals:** Feed small synthetic GCT trees with valid siblings/children, multiple matching entries, sentinel termination, invalid magic, and absent callouts. Firmware-boot validation should check expected platform nodes are discovered exactly once.
