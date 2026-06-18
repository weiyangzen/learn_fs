# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-method.c

## Purpose
This file implements EC matrix management and encode/decode execution for the disperse translator. It prepares Vandermonde-like normal matrices for encoding, builds inverse matrices for available-fragment decode masks, caches those matrices, and invokes generated Galois-field code functions.

## Important APIs, Types, And Functions
Public APIs are `ec_method_init`, `ec_method_fini`, `ec_method_update`, `ec_method_encode`, and `ec_method_decode`. Internal helpers include `ec_method_matrix_normal()`, `ec_method_matrix_inverse()`, `ec_method_matrix_init()`, `ec_method_matrix_get()`, `ec_method_matrix_put()`, and sorted cache helpers for lookup/insert/remove. `ec_method_setup()` creates the encode matrix and the `ec_code_t` code generator context.

## Control Flow
Initialization creates a matrix mem-pool, object array, Galois-field tables via `ec_gf_prepare()`, code generation context via `ec_code_create()`, and the encode matrix. Encoding walks input in `list->stripe` chunks and calls each linear row function, advancing each child output pointer by `EC_METHOD_CHUNK_SIZE`. Decoding looks up or builds an inverse matrix keyed by the surviving-brick mask, runs interleaved decode functions over `EC_METHOD_CHUNK_SIZE` slices, then unreferences the cached matrix. Unreferenced matrices sit on an LRU list and are evicted when `count > max`.

## State And Persistence Behavior
All state is in-memory within `ec_matrix_list_t`: cached decode matrices, one encode matrix, generated executable code spaces, GF tables, mem-pool, and lock. Nothing is persisted to disk. The cache key is a bitmask of available fragments; correctness depends on matching the rows array to that mask.

## Dependencies And Integration Points
The file depends on `ec-galois`, `ec-code`, `ec-types`, `ec-mem-types`, and `ec-helpers`. It is initialized from `ec.c` with data fragments as columns and total nodes as rows; `ec-inode-write.c` calls `ec_method_encode()` before writing fragments. Read/heal paths use `ec_method_decode()` to reconstruct missing data.

## Risks
Matrix inversion and cache lifecycle are correctness-critical. Pointer arithmetic advances `void *` values, relying on compiler extensions common in this codebase. The decode cache uses a sorted object array plus LRU list; reference-count or removal mistakes could lead to stale function pointers or leaks. `ec_method_update()` is currently a stub, so changing CPU extension options at runtime does not rebuild generated code.

## Test Signals
Tests should cover encode/decode for every legal redundancy/data count, all surviving-fragment masks at quorum, repeated decode to hit cache reuse and eviction, memory cleanup during translator fini, and CPU-extension option combinations (`none`, `auto`, SIMD variants). Fault injection on allocation and code generation should return clean errors.
