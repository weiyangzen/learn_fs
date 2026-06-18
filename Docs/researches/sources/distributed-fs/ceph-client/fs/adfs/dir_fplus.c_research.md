<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/dir_fplus.c -->
# sources/distributed-fs/ceph-client/fs/adfs/dir_fplus.c

## Purpose
`dir_fplus.c` implements ADFS F+ large-directory support with variable directory size, separate entry/name tables, validation, iteration, update, and commit logic.

## Important APIs, types, and functions
Important helpers are `adfs_fplus_offset`, `adfs_fplus_validate_header`, `adfs_fplus_validate_tail`, `adfs_fplus_checkbyte`, `adfs_fplus_read`, `adfs_fplus_setpos`, `adfs_fplus_getnext`, `adfs_fplus_iterate`, `adfs_fplus_update`, and `adfs_fplus_commit`. It exports `adfs_fplus_dir_ops`.

## Control flow
Read loads the first block, validates header version/magic/size/name/entry bounds, loads the full directory size, validates tail and check byte, and records parent ID. Iteration uses an entry index, copies each bigdir entry, then copies the variable-length name from the names area. Update locates by indirect address and rewrites metadata fields; commit increments sequence counters and recomputes the check byte.

## State and persistence
Runtime state is buffer_heads plus `bighead`, `bigtail`, and entry index. Persistent state is the F+ header, entry table, names area, tail, and check byte.

## Dependencies and integration points
It depends on `dir_fplus.h`, common ADFS directory buffer helpers, endian conversion, and generic object fixup.

## Risks and test signals
Risks include malformed size fields, entry/name table bounds, checkbyte coverage over multi-block directories, integer overflow in offset computation, and partial update persistence. Test signals include large F+ directories, corrupt headers/tails, long names, update/commit cycles, and ctx position overflow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/dir_fplus.c -->
