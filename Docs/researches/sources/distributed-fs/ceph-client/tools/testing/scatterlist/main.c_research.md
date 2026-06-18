# sources/distributed-fs/ceph-client/tools/testing/scatterlist/main.c

Purpose: table-driven userspace tests for scatterlist table allocation and segment coalescing from page arrays.

Important APIs/types/functions: `struct test` captures expected return, input PFNs, optional append PFNs, total size, maximum segment size, and expected segments; `set_pages()` maps PFN arrays to fake page pointers; `fail()` prints diagnostics; `VALIDATE` asserts conditions; `main()` iterates test cases.

Control flow: each case builds fake pages, calls either `sg_alloc_table_from_pages_segment()` or `sg_alloc_append_table_from_pages()`, checks return status, optionally appends a second range, validates `nents` and `orig_nents`, then frees the table. Cases cover contiguous, reversed, fragmented, appended, and max-segment-limited page sequences.

State and persistence: only stack/compound-literal test data and heap allocations inside scatterlist APIs; no files.

Dependencies/integration: includes generated/copied `linux/scatterlist.h` and uses fake page primitives from local Linux stubs.

Risks and test signals: expected segment counts are the core signal. The fake PFN model assumes `PAGE_SIZE`-aligned pointer arithmetic and does not model real memory attributes.
