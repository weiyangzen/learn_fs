# sources/distributed-fs/openafs/src/comerr/error_table.h

Purpose: public data structures and constants for generated com_err tables.

Important APIs and types: defines `struct error_table` with message vector, base, and count; `struct et_list` for registered table linked lists; constants `ERRCODE_RANGE` and `BITS_PER_CHAR`; declarations for `afs_error_table_name`, `afs_add_to_error_table`, `afs_com_right`, and `afs_com_right_r`.

Control flow and state: no executable logic. Generated `.c` files instantiate `error_table` and `et_list` objects matching this layout.

Dependencies and integration: includes system types and errno. Installed with comerr headers and used by generated code from `compile_et`.

Risks and tests: `base` is an `int` while generated code may format as long constants; this is legacy-compatible but should be treated carefully on unusual platforms. Any layout change breaks generated object compatibility.
