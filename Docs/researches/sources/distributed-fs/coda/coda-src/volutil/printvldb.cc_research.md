## sources/distributed-fs/coda/coda-src/volutil/printvldb.cc

Purpose: `printvldb.cc` is a standalone diagnostic program that reads the on-disk VLDB file and prints sorted volume location records. It filters duplicate hash entries and orders output by volume id.

Important APIs/types/functions: macros `VID` and `UNIQUE` derive ids from `struct vldb`. Sorting helpers are `heapify` and `heapsort`. `main` opens `VLDB_PATH`, reads batches of `struct vldb`, filters entries, grows an array, sorts, and prints volume id, key, type, and server numbers.

Control flow: records are read in chunks into a small stack buffer, converted to record counts by `LOG_VLDBSIZE`, filtered to skip numeric-key duplicates, appended to a dynamically grown array, then heap-sorted using 1-based indexing semantics and printed.

State and persistence behavior: read-only. It allocates a process-local VLDB array and prints to stdout; it does not update VLDB files.

Dependencies/integration points: depends on Coda `vldb.h`, `VLDB_PATH`, network byte order helpers, and volume/vnode headers. It is separate from RPC volutil lookup paths and operates directly on the local VLDB file.

Risks: `main` is declared `void`, old C/C++ style. The heap sort expects array elements from index 1, but population starts at index 0; this can leave element 0 unsorted and risks off-by-one behavior. Read sizes not aligned to full records are not explicitly rejected. Filtering by `VID(vldp) != atoi(vldp->key)` assumes numeric keys only represent duplicate id entries.

Test signals: run against synthetic VLDB files with name/id duplicate entries, multiple server counts, empty files, partial final reads, and enough entries to force array growth. Compare output ordering and filtering against expected records.
