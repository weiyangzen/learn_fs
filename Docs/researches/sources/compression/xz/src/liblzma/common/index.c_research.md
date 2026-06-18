<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/index.c -->
# sources/compression/xz/src/liblzma/common/index.c

Purpose: Implements the in-memory `.xz` Index and Stream metadata model, including append, concatenate, duplicate, size/memory queries, stream flags/padding, and iteration/location APIs.

Important APIs/types: Internal structures include `index_tree_node`, `index_tree`, `index_record`, `index_group`, `index_stream`, and `struct lzma_index_s`. Public APIs include `lzma_index_init/end/prealloc`, `lzma_index_memusage/memused`, block/stream/size queries, `lzma_index_stream_flags()`, `lzma_index_stream_padding()`, `lzma_index_append()`, `lzma_index_cat()`, `lzma_index_dup()`, `lzma_index_iter_init/rewind/next/locate()`, and internal `lzma_index_padding_size()`.

Control flow: Streams and groups are appended sequentially into AVL-like trees optimized for monotonic insert order. Record groups store cumulative uncompressed sums and cumulative padded compressed sums, enabling binary search by uncompressed offset. `lzma_index_append()` validates unpadded/uncompressed sizes, file size bounds, Index Backward Size bounds, allocates groups using `prealloc`, and updates both Stream and global totals. `lzma_index_cat()` validates combined limits, may shrink the final underfilled group, moves Stream nodes from source to destination with adjusted base offsets, updates check masks, and frees only the source base object. Iterators maintain internal pointers carefully so they do not hold a pointer to a group that `lzma_index_cat()` may reallocate.

State and persistence: `lzma_index` persists totals, tree roots, preallocation preference, and check masks. Each `index_stream` carries base offsets, numbering, record tree, stream flags, and Stream Padding. Records persist cumulative Block size data rather than raw per-Block starts.

Dependencies/integration: Depends on `index.h`, `stream_flags_common.h`, VLI helpers, allocation wrappers, and public `lzma_index_iter` layout. It is the shared metadata object used by Index encoder/decoder, file info decoding, stream buffer encoding, and applications.

Risks/tests: Overflow checks and iterator stability are the main risks. Tests should cover empty Streams, zero-size Blocks, many Records crossing group boundaries, concatenated Streams with padding, duplicate/cat interactions, locating offsets around empty Blocks, maximum VLI boundaries, and the fixed `lzma_index_prealloc(0)` behavior preventing later buffer overflow after decoding an empty Index.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/index.c -->
