## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utownerid.c

Purpose: `utownerid.c` allocates and releases ACPICA owner IDs, which tag namespace objects created by a table or method so they can be cleaned up when the table unloads or the method exits.

Important APIs and functions: `acpi_ut_allocate_owner_id` takes a pointer to an `acpi_owner_id`, rejects double allocation to a nonzero slot, scans global owner-ID bit masks for a free bit, marks it allocated, and returns an encoded one-based ID. `acpi_ut_release_owner_id` clears the caller's slot first, validates nonzero input, decodes ID to mask index/bit, and clears the allocation bit if set.

Control flow: allocation is serialized by `ACPI_MTX_CACHES`, begins at `acpi_gbl_last_owner_id_index` and `acpi_gbl_next_owner_id_offset`, wraps around the mask array, and may scan the starting mask twice. The final possible bit is reserved to prevent one-based overflow. Release also uses `ACPI_MTX_CACHES`, normalizes the ID to zero-based form, and reports attempts to release unallocated IDs.

State and dependencies: persistent global state includes `acpi_gbl_owner_id_mask[]`, the last index, and next offset. It depends on internal mutex services and ACPI division/modulo macros for bit-index decoding.

Integration points: table load/unload, namespace deletion, and control method execution use owner IDs to identify which objects are owned by the current table or method invocation.

Risks: leaked owner IDs eventually hit `AE_OWNER_ID_LIMIT`. Clearing the caller's ID before validation prevents repeated release attempts but can hide the original value from later callers. Correct lock initialization is required before use.

Test signals: allocation from a zero slot, double allocation detection, full-mask exhaustion, wraparound reuse after release, invalid zero release, and release of an unallocated nonzero ID are key cases.
