# sources/cloud-native/nydus/builder/src/core/layout.rs

Purpose: computes the order in which file nodes are dumped into data blobs.

Important APIs/types/functions: `BlobLayout::layout_blob_simple(prefetch)` returns `(Vec<TreeNode>, usize)`, where the vector contains prefetch-selected nodes first followed by non-prefetch nodes, and the usize marks how many leading entries came from the prefetch lane. `should_dump_node` accepts only nodes with overlay state `UpperAddition` or `UpperModification`.

Control flow: it asks `Prefetch::get_file_nodes()` for prefetch and non-prefetch node collections, filters both through `should_dump_node`, records the count of prefetch nodes, appends non-prefetch nodes, and returns the final dump order.

State and persistence: no persistent state is stored. The returned order affects subsequent blob writes and prefetch byte accounting in `Blob::dump`.

Dependencies and integration points: depends on `Prefetch`, `TreeNode`, `Node`, and `Overlay`. It is called by `core/blob.rs` during `DirectoryToRafs` conversion.

Risks: lower-layer or unchanged nodes are intentionally skipped; correctness depends on overlay classification before layout. The routine is simple and does not account for size, locality, or dependency ordering beyond prefetch grouping.

Test signals: the unit test constructs a one-node tree, inserts it into prefetch, and verifies the layout returns one dumpable node and the expected prefetch count.
