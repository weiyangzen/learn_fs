<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/lmdb/midl.c -->
# sources/distributed-fs/orangefs/src/common/lmdb/midl.c

Purpose: implements LMDB's internal ID-list primitives, imported from OpenLDAP/LMDB, for sorted page-ID arrays (`MDB_IDL`) and ID-to-pointer arrays (`MDB_ID2L`). These are not OrangeFS management APIs directly; they support the embedded LMDB backend when `WANT_INTERNAL_LMDB` is enabled.

Important functions: `mdb_midl_search()` binary-searches descending IDLs and returns the matching or insertion position. Allocation and capacity management are handled by `mdb_midl_alloc()`, `mdb_midl_free()`, `mdb_midl_shrink()`, the private `mdb_midl_grow()`, and `mdb_midl_need()`. Append paths are `mdb_midl_append()`, `mdb_midl_append_list()`, and `mdb_midl_append_range()`. `mdb_midl_sort()` performs an iterative quicksort with insertion sort for small partitions, sorting IDs in descending order. `mdb_midl_xmerge()` merges a descending source list into a destination list that must already be large enough. `mdb_mid2l_search()`, `mdb_mid2l_insert()`, and `mdb_mid2l_append()` manage ascending `MDB_ID2L` arrays.

Control flow is array-centric and allocation-aware. IDLs store the live count in `ids[0]` and the allocation length in `ids[-1]`, so every grow/shrink/free path adjusts the pointer by one slot. There is no persistence here; state is caller-owned heap memory that LMDB later serializes or uses internally. Dependencies are standard C allocation/string routines, `errno`, and `midl.h`.

Risks: callers must preserve the unusual pointer contract or `free(ids-1)` and `ids[-1]` become unsafe. `mdb_midl_xmerge()` assumes sufficient destination capacity and compatible descending order. The disabled insert routine hints that append/sort is the intended safe path. Tests should cover empty/singleton lists, duplicate ID2 insert rejection, allocation growth, range append, descending sort/search invariants, and boundary lengths near `MDB_IDL_UM_MAX`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/lmdb/midl.c -->
