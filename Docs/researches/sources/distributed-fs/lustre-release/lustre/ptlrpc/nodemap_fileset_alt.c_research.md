# sources/distributed-fs/lustre-release/lustre/ptlrpc/nodemap_fileset_alt.c

## Purpose
`nodemap_fileset_alt.c` manages alternative fileset mappings for Lustre nodemaps. It owns allocation, destruction, insertion, deletion, lookup, prefix matching, and memory resizing for `struct lu_fileset_alt` entries stored in a red-black tree keyed by fileset id.

## Important APIs, types, and functions
The exported API is `fileset_alt_init()`, `fileset_alt_create()`, `fileset_alt_destroy()`, `fileset_alt_destroy_tree()`, `fileset_alt_add()`, `fileset_alt_delete()`, `fileset_alt_search_id()`, `fileset_alt_search_path()`, `fileset_alt_path_exists()`, and `fileset_alt_resize()`. The local helper `get_first_free_id()` finds the lowest unused nonzero id, and `compare_by_id()` adapts id lookup to `rb_find()`.

Entries are `struct lu_fileset_alt` objects with `nfa_path`, `nfa_path_size`, `nfa_id`, `nfa_ro`, and `nfa_rb`. The containing nodemap stores `nm_fileset_alt` and `nm_fileset_alt_sz`; locking is external via `nm_fileset_alt_lock` in callers.

## Control flow
Creation allocates the struct, records the requested path buffer size, initializes id to zero and read-only false, then allocates the path buffer. `fileset_alt_create()` sizes the buffer to `strlen(path) + 1`, copies the path, and sets read-only state.

Insertion assigns the first free id when `nfa_id` is zero, rejects ids greater than `LUSTRE_NODEMAP_FILESET_NUM_MAX - 1`, walks the rb tree by id, rejects duplicates with `-EEXIST`, links/rebalances the node, and increments `nm_fileset_alt_sz`. Deletion erases the rb node, decrements the size, destroys the entry, and returns the deleted id or `-EINVAL` for null input.

Exact id lookup uses `rb_find()`. Path lookup walks the whole tree because the tree is ordered by id, not path. Exact lookup uses `strcmp()`. Prefix lookup accepts entries where the searched path begins with the alternate fileset path and is followed by `/` or `\0`, and returns the longest matching prefix. Tree destruction postorder-frees every entry, resets the root, and clears the size. Resize walks entries, allocates a smaller path buffer when the preallocated size exceeds `strlen(path) + 1`, copies the path, frees the old buffer, and keeps the old allocation if shrinking fails.

## State and persistence behavior
The file only mutates in-memory nodemap fileset-alt trees. Persistence is handled by callers in nodemap storage/config code; this file is used when storage reads preallocated fragments and later shrinks them. The assigned `nfa_id` values are stable while entries remain in the tree, and id zero is reserved for the primary fileset outside this alternate tree.

## Dependencies and integration points
It depends on Linux rb-tree helpers, Lustre allocation macros, `lustre_net.h`, and `nodemap_internal.h`. Callers in `nodemap_handler.c`, `nodemap_storage.c`, and `nodemap_lproc.c` hold `nm_fileset_alt_lock`, validate nodemap policy constraints, persist mapping changes, and query prefix matches during path/fileset handling.

## Risks and edge cases
The implementation assumes callers provide locking; none of the exported functions take locks themselves. Path lookup is O(n), so many alternate filesets increase lookup cost, though the configured max bounds it. Prefix matching repeatedly calls `strlen(tmp->nfa_path)` and uses `strstr(fileset_path, tmp->nfa_path) == fileset_path`; this requires null-terminated validated paths and treats only slash or end-of-string as a boundary. `fileset_alt_delete()` returns an `int` but returns an unsigned id on success, so ids must remain within signed range; the configured max check supports that. Allocation failure in resize leaves the larger buffer in place and logs an error.

## Test signals
Tests should cover allocation failure cleanup, automatic id assignment with gaps, explicit id insertion, max-id rejection, duplicate id rejection, delete-null and delete-existing behavior, tree destruction size/root reset, exact path lookup, longest-prefix lookup with boundary checks, read-only flag preservation, resize shrink success and allocation failure, and caller-side locking around concurrent nodemap reads/writes.
