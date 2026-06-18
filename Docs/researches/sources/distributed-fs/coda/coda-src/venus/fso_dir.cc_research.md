# sources/distributed-fs/coda/coda-src/venus/fso_dir.cc

Purpose: provides `fsobj` directory data helpers over Coda's directory-handle (`DH_*`) library, plus synchronization of Coda-format directory data to Unix-format container files used by the kernel.

Important APIs and flow: `dir_Rebuild` validates/prints corrupt Coda directory handles, converts them to Unix directory format with `DH_Convert`, and marks the UDCF valid. `dir_Create` and `dir_Delete` mutate Coda-format entries, invalidate the Unix-format container, and update directory data cache stats by block delta. `clear_dir_container_entry` patches the Unix-format directory container after unlink to avoid `rm -rf` loops caused by session semantics. `dir_MakeDir` allocates recoverable `VenusDirData`, initializes `.`/`..`, and updates `stat.Length`. Lookup helpers map names to same-volume `VenusFid`s, reverse-map fids to names, check emptiness/parentage, translate all references from an old fid to a new fid, and print debug state.

State and persistence: `data.dir`, `data.dir->dh`, `udcf`, `udcfvalid`, `stat.Length`, and directory cache stats are the central state. Mutation callers are expected to be in a transaction; the functions assert full data availability and use recoverable allocation for new directory data.

Dependencies and integration: depends on `codadir`/`DH_*`, `CacheFile`, Coda fid conversion helpers, `FSDB` cache stats, local repair fid translation, and open-path directory rebuild logic in `fso_cfscalls2.cc`.

Risks and test signals: risks include corrupt directory handles, cross-volume translation misuse, `clear_dir_container_entry` offset assumptions, stale UDCF data, and block-accounting signs on deletion. Tests should cover create/delete/rebuild sequences, lookup flags/case sensitivity, empty directory checks, fid translation for local repair, corrupt-dir diagnostics, and repeated unlink while a directory is open.
