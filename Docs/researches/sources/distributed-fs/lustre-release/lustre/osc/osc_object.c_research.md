# sources/distributed-fs/lustre-release/lustre/osc/osc_object.c research

## Purpose
`osc_object.c` implements OSC `cl_object` and `lu_object` behavior. It initializes per-stripe object state, exposes attribute get/update/glimpse, manages LDLM AST data pruning, sends FIEMAP requests, populates request attributes for page RPCs, allocates objects, and invalidates objects during teardown or layout changes.

## Important APIs, Types, and Functions
Exports include `osc_object_init()`, `osc_object_free()`, `osc_lvb_print()`, `osc_object_print()`, `osc_attr_get()`, `osc_attr_update()`, `osc_object_glimpse()`, `osc_object_prune()`, and `osc_object_invalidate()`. The local operation tables are `osc_object_ops`, `osc_ops`, and `osc_lu_obj_ops`. `osc_object_alloc()` allocates from `osc_object_kmem` and wires CL/LU ops.

Observed `osc_object` state initialized here includes `oo_oinfo`, ready/read/write list items, red-black extent root, high-priority/urgent/full/read extent lists, pending read/write counters, object and page-tree locks, radix page tree and page count, lock-list spinlock/list, active IO counter, and IO wait queue.

## Control Flow
Object initialization copies `lov_oinfo` from the CL object config, initializes all cache/RPC and lock lists, sets counters to zero, initializes the radix tree, and calls `cl_object_page_init()` with `sizeof(struct osc_page)`. Free asserts that all object-owned lists, trees, counters, and lock lists are empty, then finalizes and frees the object.

Attribute flow is local LVB/KMS translation. `osc_attr_get()` copies `loi_lvb` to `cl_attr` and reports KMS only when valid. `osc_attr_update()` writes selected CL attrs back to the LVB and calls `loi_kms_set()` for `CAT_KMS`. `osc_object_glimpse()` reports KMS as size for LDLM glimpse callbacks.

`osc_object_prune()` iterates the LDLM resource and clears any lock `l_ast_data` that points at the object, first copying the current object LVB into the lock LVB and clearing `LDLM_FL_LVB_CACHED`. `osc_object_fiemap()` optionally matches or obtains server-side locking for sync FIEMAP, packs an `OST_GET_INFO` request, and copies the returned fiemap data. `osc_req_attr_set()` populates `obdo` identity, timestamps, group/id, and DLM handle for page RPCs, with a hard failure if a non-server-lock page is uncovered by a local DLM lock.

## State and Persistence Behavior
Object state is volatile but mirrors server object identity and attributes through `lov_oinfo`. LVB fields (`size`, `blocks`, timestamps) and KMS are updated locally and sent or exposed through lock/RPC paths. `osc_object_invalidate()` waits for active IOs to drain, truncates dirty cache to zero, discards cached pages, and prunes DLM AST data, making it the strong object cleanup path before the object can disappear.

## Dependencies and Integration Points
The file depends on CL object/page APIs, LDLM resource iteration and matching, OSTID resource naming, PTLRPC request capsules, FIEMAP structures, `lov_oinfo`, `obdo`, and local cache/lock functions declared in `osc_internal.h`. It integrates with `osc_page.c` through page initialization and `osc_cl_page_osc()`, with `osc_lock.c` through lock lookup/build resource functions, with `osc_cache.c` through invalidation and discard, and with request code through request attribute population.

## Risks
Risks include stale `l_ast_data` pointing to freed objects, incorrect KMS/LVB ordering, FIEMAP lock reference leaks, and uncovered-page failures in `osc_req_attr_set()`. The comment about atime reset in request attributes is an explicit maintainability warning. Object free assertions are strict; leaks in cache, LRU, lock, or active IO paths will surface here.

## Test Signals
Tests should cover object init/free with empty state, attr get/update for size/times/blocks/KMS, glimpse size from KMS, prune clearing lock AST data and copying LVB, FIEMAP with cached PR/PW lock and server-lock fallback, request attr handle lookup for normal and server-lock pages, object invalidation while IOs are active, and cleanup assertions after truncation/discard.
