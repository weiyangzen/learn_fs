# sources/distributed-fs/coda/coda-src/al/pdbprofile.c

Purpose: Profile-level lifecycle, read/write/delete, display, and CPS recomputation helpers for PDB records.

Important APIs/functions: `PDB_freeProfile`, `PDB_writeProfile`, `PDB_readProfile`, `PDB_readProfile_byname`, `PDB_deleteProfile`, `PDB_printProfile`, and `PDB_updateCps`.

Control flow: Read/write functions delegate to `PDB_db_read/write` and `pdb_pack/unpack`. Free clears IDs and releases strings and arrays only when the profile ID is nonzero. `PDB_printProfile` emits user/group metadata and array contents. `PDB_updateCps` rebuilds a record's CPS by merging all parent CPS arrays, adding self, writing the record, and recursively updating children when the record is a group.

State and persistence: Persists profiles through the shared PDB handle. `PDB_updateCps` is the main consistency mechanism for derived CPS state across the membership graph.

Dependencies and integration: Used by all high-level PDB operations and AL CPS retrieval. Depends on `pdbpack`, `pdbdb`, `pdbarray`, and `prs.h`.

Risks and test signals: Recursive CPS updates can be costly and require membership loops to be prevented elsewhere. `PDB_freeProfile` does nothing when `id == 0`, so callers must not expect it to sanitize partially unpacked corrupt records. Print buffers are fixed-size for array formatting.
