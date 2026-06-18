# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nswalk.c

## Purpose
`nswalk.c` implements internal namespace iteration and a generic depth-first namespace walker. It supports public walking APIs, device discovery, debugging, and ACPICA subsystems that need callbacks over namespace nodes.

## Important APIs, types, and functions
`acpi_ns_get_next_node()` returns a parent's first child or a child's next peer. `acpi_ns_get_next_node_typed()` skips peers until it finds a requested object type or returns any type. `acpi_ns_walk_namespace()` is the main tree walker with descending and ascending callbacks, maximum depth, temporary-node policy, and optional namespace unlock around callbacks.

## Control flow
The walker normalizes `ACPI_ROOT_OBJECT` to `acpi_gbl_root_node`, rejects null starts, then enters a modified depth-first loop starting at the first child. For each node it optionally filters by type and temporary-node flag. Matching nodes invoke the descending callback on the first visit and ascending callback on the revisit. If `ACPI_NS_WALK_UNLOCK` is set, the namespace mutex is released before calling the callback and reacquired afterward. Callback statuses control traversal: `AE_CTRL_DEPTH` prunes children, `AE_CTRL_TERMINATE` ends successfully, and other failures propagate. The loop descends to children while below `max_depth`, revisits nodes after children, advances to peers, and bubbles to parents until it returns past the start.

## State and persistence behavior
The walker itself does not mutate namespace nodes. It maintains transient traversal state: parent, child, current level, child type, and whether the current node is being revisited. Callback code may mutate system state, which is why the unlock flag and temporary-node filtering matter.

## Dependencies and integration points
The implementation depends on child/peer/parent links in `struct acpi_namespace_node`, namespace mutex helpers, node flags such as `ANOBJ_TEMPORARY`, and callback status conventions. The public `acpi_walk_namespace()` wrapper in `nsxfeval.c` adds read locking and handle validation before calling this internal walker.

## Risks and edge cases
Unlocking around callbacks is necessary for clients that call back into ACPICA but exposes race risks from temporary method-created nodes, so default filtering is important. `max_depth` handling and revisit state are easy to regress because ascending callbacks are tied to the same node after child traversal. Callback errors must not leave the namespace mutex released.

## Test signals
Tests should check depth-limited traversal, type-filtered traversal, callbacks on descent and ascent, pruning with `AE_CTRL_DEPTH`, termination with `AE_CTRL_TERMINATE`, temporary-node exclusion and inclusion, root-object handling, and mutex release/reacquire behavior when callbacks invoke ACPICA APIs.
