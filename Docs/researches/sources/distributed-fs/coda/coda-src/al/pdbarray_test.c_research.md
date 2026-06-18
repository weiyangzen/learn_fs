# sources/distributed-fs/coda/coda-src/al/pdbarray_test.c

Purpose: Small standalone smoke test for `pdb_array` behavior.

Important APIs/functions: `print_array` and `main`, which call `pdb_array_init`, `pdb_array_add`, `pdb_array_del`, `pdb_array_merge`, `pdb_array_size`, and `pdb_array_free`.

Control flow: The program creates array `a`, inserts values out of order, prints expected sorted forms, deletes values, merges a second array `b`, and frees both arrays.

State and persistence: All state is in process heap memory. No filesystem or database persistence is touched.

Dependencies and integration: Includes only `pdbarray.h`; it is a direct unit-level sanity check for the sorted-list primitive.

Risks and test signals: The test is print-based and has no assertions, exit-status validation, duplicate insertion case, pack/unpack case, or allocation failure coverage. Still useful as a quick visual regression.
