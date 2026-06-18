# sources/distributed-fs/coda/coda-src/al/pdbarray.c

Purpose: Implements a small sorted dynamic array of `int32_t` IDs used by PDB profiles for membership, CPS, and ownership/member lists.

Important APIs/functions: `pdb_array_init`, `pdb_array_free`, `pdb_array_search`, `pdb_array_add`, `pdb_array_del`, `pdb_array_copy`, `pdb_array_merge`, `pdb_array_head`, `pdb_array_next`, `pdb_array_size`, `pdb_array_pack`, `pdb_array_unpack`, `pdb_array_to_array`, and `pdb_array_snprintf`.

Control flow: Insert grows capacity by 16 entries, finds the sorted insertion point, skips duplicates, shifts the tail, and inserts. Delete binary-searches, shifts the tail down, and zeroes the old last slot. Merge allocates a combined sorted buffer and de-duplicates overlaps. Pack/unpack store count followed by network-order entries.

State and persistence: Owns heap memory in `data`, with `size` and `memsize` tracking logical and allocated length. Persistent form is an `int32_t` count plus network-order data, embedded in packed PDB profiles.

Dependencies and integration: Used by `pdb.c`, `pdbprofile.c`, `pdbpack.c`, and tests. Depends on `netinet/in.h` for byte order and `coda_assert`.

Risks and test signals: Allocation return values are not consistently checked after `malloc`/`realloc`. `pdb_array_copy` allocates zero bytes when size is zero and does not special-case NULL, which is usually acceptable but brittle. `pdb_array_snprintf` repeatedly calls `strlen`, making it quadratic for long lists. `pdbarray_test.c` gives simple add/delete/merge coverage.
