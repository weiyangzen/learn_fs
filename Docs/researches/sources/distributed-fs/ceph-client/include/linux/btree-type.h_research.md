## sources/distributed-fs/ceph-client/include/linux/btree-type.h

**Purpose:** This template header generates typed B+Tree wrappers for one-word key types. It is included multiple times by `btree.h` after defining `BTREE_TYPE_SUFFIX`, `BTREE_TYPE_BITS`, `BTREE_TYPE_GEO`, and `BTREE_KEYTYPE`.

**Important APIs/types/functions:** The template creates `struct btree_head<SUFFIX>` and wrappers for `init_mempool`, `init`, `destroy`, `merge`, `lookup`, `insert`, `update`, `remove`, `last`, `get_prev`, `visitor`, and `grim_visitor`. It also declares a typed visitor trampoline `visitor<SUFFIX>` and typedef `visitor<SUFFIX>_t`.

**Control flow, state, persistence:** Wrappers forward into generic `btree_*` operations while adapting key storage. If `BITS_PER_LONG > BTREE_TYPE_BITS`, the key is widened into a local `unsigned long`; otherwise it is passed by pointer cast. Tree state is the embedded generic head and mempool-managed nodes.

**Dependencies/integration:** Depends on macro definitions from `btree.h`, generic B+Tree functions, and the appropriate geometry object. It emits variants such as `btree_l`, `btree_32`, and `btree_64`.

**Risks and test signals:** Risks are macro leakage, including the template directly without definitions, visitor trampoline name assumptions, key truncation, and aliasing/alignment issues on cross-width builds. Test signals are compile coverage for all generated variants, lookup/update/remove behavior on 32- and 64-bit architectures, and visitor callback key correctness.
