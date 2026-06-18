# sources/distributed-fs/coda/coda-src/smon2/rvmsizer.c

Purpose: estimates Coda RVM metadata requirements for a local file tree.

Important functions/constants: `scantree` walks roots with `fts_open` using physical, cross-device-limited traversal. It counts directories as large vnodes, files/symlinks/default entries as small vnodes, totals file and directory sizes, estimates directory pages based on padded directory entry sizes and page overhead (`DIRPAGE`, `DIRNONNAME`, `PAGELOSS`), warns if a directory would require at least 128 pages, and prints RVM estimates based on directory pages plus vnode constants (`FILERVMSIZE`, `DIRSIZE`) and the old 4% rule. `main` accepts `[-v] [--] dir`, though verbosity is parsed but unused.

State/persistence: read-only filesystem scan; no writes.

Dependencies, risks, tests: depends on Coda `coda_fts` wrappers and POSIX stat data. Risks include division by zero for empty/no-file or no-directory cases, continuing after `fts_read` errors with `errno` handling, unused verbosity, and heuristic constants that may drift from current on-disk structures. Test empty directories, large trees, unreadable directories, symlink handling, crossing filesystem boundary, and average calculations with zero small files.
