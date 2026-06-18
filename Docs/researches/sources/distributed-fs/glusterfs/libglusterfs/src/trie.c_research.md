# sources/distributed-fs/glusterfs/libglusterfs/src/trie.c

## Purpose

`trie.c` implements a simple byte-indexed trie with edit-distance measurement. It stores dictionary words, walks trie nodes, reconstructs words from nodes, computes dynamic-programming edit distance against a query word, and collects closest matching end-of-word nodes.

## Important APIs, Types, and Functions

Public functions include `trie_new()`, `trie_add()`, `trie_destroy()`, `trie_destroy_bynode()`, `trienode_get_word()`, `trienode_get_dist()`, `trie_measure()`, `trie_measure_vec()`, and `trie_reset_search()`. `struct trienode` contains byte id, end-of-word flag, depth, per-search data row, trie pointer, parent pointer, and 255 child pointers. `struct trie` contains the root node, node count, and current search word length.

## Control Flow and Data Flow

Insertion starts at the root, creates subnodes for each byte with `trie_subnode()`, links parent/trie metadata, increments node count, and marks the terminal node as end-of-word. Walking recursively visits nodes and can call only end-of-word nodes or all nodes. `trienode_get_word()` allocates a depth-sized buffer and recursively prints parent ids into it.

Search sets `trie->len`, clears the output vector, and walks all nodes. `calc_dist()` allocates a DP row for each node, initializes the root row, and for children computes edit/insert/delete costs from the parent row and current node id. `collect_closest()` keeps nodes with the lowest distance among end-of-word nodes, clearing previous results when a better distance appears and filling free vector slots for ties. `trie_reset_search()` frees per-node DP rows and clears `len`.

## State and Persistence Behavior

Dictionary nodes persist until `trie_destroy()`. Search state is stored temporarily in each node's `data` pointer and must be reset by `trie_reset_search()` to avoid accumulating DP rows across searches. There is no disk persistence.

## Dependencies and Integration Points

The file depends on Gluster allocation helpers, `min()`, and `glusterfs/trie.h`. It is suitable for command suggestion, option matching, or other small dictionary fuzzy-match use cases inside libglusterfs.

## Risks and Edge Cases

Child indexing uses `char` values into a 255-element array; signed char or byte value 255 can lead to invalid indexing. `trie_destroy()` casts the trie object to a node and frees through `trienode_free()`, relying on the root being the first struct member. Search allocates one row per visited node and requires `trie_reset_search()` for cleanup. Empty query words make `trienode_get_dist()` access `row[len - 1]`, so they need guarding. The code intentionally avoids pruning because edit-distance pruning was shown incorrect in comments.

## Test Signals

Tests should add and retrieve words, measure exact matches, insertions, deletions, substitutions, ties within limited node vectors, reset-search cleanup, empty and non-ASCII byte inputs, and repeated searches under allocation-failure injection. Address-sanitizer tests are useful for child-index bounds.
