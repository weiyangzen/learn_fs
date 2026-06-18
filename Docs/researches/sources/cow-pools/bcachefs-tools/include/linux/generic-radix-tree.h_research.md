# File Research: sources/cow-pools/bcachefs-tools/include/linux/generic-radix-tree.h

This header implements typed wrappers for a generic radix-tree sparse array. `GENRADIX(_type)` stores a `struct __genradix` plus a zero-length typed marker used for casts and object sizing. Nodes are fixed at `GENRADIX_NODE_SIZE` bytes, with interior children or leaf data.

Public macros cover initialization/freeing, pointer lookup, pointer allocation with optional preallocated nodes, forward and reverse iteration, and preallocation: `genradix_init()`, `genradix_free()`, `genradix_ptr()`, `genradix_ptr_alloc*()`, `genradix_for_each*()`, and `genradix_prealloc()`.

The offset conversion logic handles object sizes that are not powers of two and uses overflow checks. A key constraint is that stored object size must not exceed `GENRADIX_NODE_SIZE`. The inline fast path reads the packed root/depth pointer and walks child indexes by byte offset; deeper allocation/free/search behavior is implemented externally.
