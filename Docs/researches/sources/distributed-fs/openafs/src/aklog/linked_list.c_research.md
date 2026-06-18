# sources/distributed-fs/openafs/src/aklog/linked_list.c

## Purpose
`linked_list.c` implements a minimal doubly linked list package used by the `aklog` command to track cells, paths, host strings, and Zephyr subscription strings.

## Important APIs, types, and functions
The implementation exports `ll_init`, `ll_add_node`, `ll_delete_node`, and `ll_string`. `ll_add_data` is a macro in the header. `ll_string` supports `ll_s_check` and `ll_s_add` for duplicate-suppressed string lists.

## Control flow
`ll_init` aborts on null and zeroes the list. `ll_add_node` allocates a node and inserts it at the head or tail, maintaining `first`, `last`, and `nelements`; an invalid end selector aborts. `ll_delete_node` linearly scans for the node, relinks neighbors, frees the node, and decrements count. `ll_string` checks for string equality or appends a newly allocated string if absent.

## State and persistence
The list state is fully caller-owned in memory. Nodes are heap allocated; `ll_delete_node` frees only the node, not `node->data`. `ll_string(ll_s_add)` allocates duplicate string storage, so callers need a separate cleanup strategy if used outside short-lived commands.

## Dependencies and integration points
It uses roken/C library memory and string routines and the local `linked_list.h` types. `aklog.c` relies on this to preserve option order and avoid duplicate cells/hosts/subscriptions.

## Risks
`ll_string(ll_s_check)` initializes `status` to `LL_SUCCESS`, which is `0`, and uses it as a boolean false until a match; callers must understand that check returns true/1 on found and 0 on not found, not strictly `LL_SUCCESS`/`LL_FAILURE`. The API stores `char *` rather than `void *`, encouraging casts. No full-list free helper exists.

## Test signals
Cover head/tail insertion into empty and non-empty lists, deletion of first/middle/last/missing nodes, string duplicate suppression, allocation failure behavior, and caller-managed data freeing.
