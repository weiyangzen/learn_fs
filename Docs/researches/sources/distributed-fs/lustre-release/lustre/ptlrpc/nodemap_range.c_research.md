# sources/distributed-fs/lustre-release/lustre/ptlrpc/nodemap_range.c

## Purpose
`nodemap_range.c` implements regular and banned NID range storage and lookup. It uses generated Linux interval-tree helpers for NID4 address intervals and list-based `cfs_nidlist` matching for large-NID netmask ranges. The handler uses it for client classification, non-overlap enforcement, and dynamic sub-range nesting.

## Important APIs, types, and functions
Public APIs are `range_create()`, `ban_range_create()`, `range_find()`, `ban_range_find()`, `range_insert()`, `ban_range_insert()`, `range_delete()`, `ban_range_delete()`, `range_search()`, `ban_range_search()`, and `range_destroy()`. Internal helpers include generic create/find/insert/delete/search routines and recursive NID4 helpers. `INTERVAL_TREE_DEFINE()` creates `nm_range_*` functions over `struct lu_nid_range`.

## Control flow and behavior
Creation validates same network, range ordering for non-netmask ranges, and identical start/end plus prefix validity for netmask ranges. Netmask input is converted into a nidlist. Range IDs are preserved on load or allocated by incrementing the tree's highest ID.

NID4 find/search uses interval-tree iteration and recursively descends into `rn_subtree` to support dynamic child ranges. Large-NID netmask ranges live on setup lists and are matched with `cfs_match_nid()`. Insertion rejects overlap; dynamic insertion may recurse into an including parent range and return that parent. Deletion unlinks from the nodemap list and removes from either interval tree or netmask list before freeing.

## State and persistence
The file owns in-memory placement and range ID allocation, not storage. Persistence is performed by handler calls to `nodemap_idx_range_add()` and `nodemap_idx_range_del()`. Runtime state includes owner nodemap, per-nodemap list link, netmask nidlist, containing tree pointer, and nested subtree.

## Dependencies and integration points
Dependencies are LNet NID conversion/matching, libcfs nidlist parsing/freeing, Linux interval-tree generic helpers, rbtrees, and `nodemap_internal.h`. It is used by range/banlist mutation, member classification, test helpers, and config teardown.

## Risks and edge cases
NID4 macros must not be used for large NIDs outside checked paths. Netmask search is linear. Dynamic nesting correctness depends on handler-side parent validation and lock coverage. `range_destroy()` asserts the list node is non-empty by local convention, so direct destruction of never-linked ranges would violate expectations.

## Test signals
Cover NID4 create/find/search/insert/delete, overlap rejection, nested dynamic ranges and most-specific classification, exact versus including finds, ban range separation, large-NID netmask parsing/matching, invalid masks, network mismatch, reversed ranges, duplicate netmask insertion, deletion paths, and load-time range ID preservation.
