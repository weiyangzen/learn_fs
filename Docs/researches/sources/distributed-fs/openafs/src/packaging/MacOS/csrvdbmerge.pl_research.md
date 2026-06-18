# sources/distributed-fs/openafs/src/packaging/MacOS/csrvdbmerge.pl

Purpose: Perl script to merge an updated master `CellServDB` into a local `CellServDB` while preserving locally modified cells.

Important APIs/types/functions: `doit` opens `CellServDB`, `CellServDB.master.last`, `CellServDB.master`, and writes `CellServDB.NEW`. It tracks `%cellstat` per cell: unchanged relative to last master, locally changed, or local-only.

Control flow: first pass scans the current file and compares each cell's server lines against the previous master. Cells missing from old master are local-only; line count or content differences mark local changes. Second pass rewrites the current file: unchanged cells are replaced from the new master, while changed/local cells are copied from the current file. Finally it renames `CellServDB.NEW` to `CellServDB` and copies the new master to `CellServDB.master.last`.

State and persistence: mutates files in the current directory and updates the saved master copy.

Dependencies/integration: uses `File::Copy`, `IO::File`, `Fcntl`, and the CellServDB text format. Included in Mac package resources by `buildpkg.sh.in`.

Risks and test signals: variable `$pos` is declared but never assigned before `setpos`, which may affect handling of cells with more servers than master. Parsing assumes cell header lines match `^>([-a-zA-Z0-9._]+)\s`. Tests should cover unchanged, changed, local-only, deleted, and server-count-different cells.
