# sources/distributed-fs/coda/coda-src/al/pdbpack.c

Purpose: Serializes and deserializes `PDB_profile` records to the binary blob stored by `pdbdb.c`.

Important APIs/functions: `pdb_pack`, `pdb_unpack`, and the local `ALIGN` macro. Fields packed are ID, name length/name bytes, owner ID, owner name length/name bytes, and three packed `pdb_array` lists.

Control flow: `pdb_pack` computes an int32-sized record length, allocates it, writes numeric fields in network order, copies strings without trailing NUL, appends packed arrays, asserts the computed offset, and returns buffer/size. `pdb_unpack` handles zero-size records by setting `id=0`, otherwise allocates NUL-terminated strings, unpacks arrays, asserts bounds, and frees the input blob.

State and persistence: This is the stable on-disk record format for PDB profiles. A comment notes the current `ALIGN(x) (x)` string padding is inefficient but preserved for compatibility.

Dependencies and integration: Called by `PDB_writeProfile`, `PDB_readProfile`, and name-in-use checks. Depends on `pdb_array_pack/unpack` and network byte order.

Risks and test signals: Deserialization trusts blob structure after minimal zero-size handling and can allocate based on corrupt lengths before the final assert. It allocates empty strings even for absent owner names. The `ALIGN` compatibility choice is format-sensitive and should not be changed without migration tooling.
