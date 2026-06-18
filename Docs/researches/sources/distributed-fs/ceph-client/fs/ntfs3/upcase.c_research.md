# sources/distributed-fs/ceph-client/fs/ntfs3/upcase.c

## Purpose
`upcase.c` provides NTFS name comparison and hashing using the volume `$UpCase` table. It supports case-sensitive tie-breaking and case-insensitive ordering for directory indexes and dcache operations.

## Important APIs and Functions
`upcase_unicode_char()` uppercases ASCII directly and otherwise indexes the upcase table. `ntfs_cmp_names()` compares little-endian UTF-16 names. `ntfs_cmp_names_cpu()` compares CPU-endian and little-endian NTFS strings. `ntfs_names_hash()` hashes upcased UTF-16 units for dcache use.

## Control Flow
Comparison starts with direct code-unit comparison unless the caller requested case-insensitive comparison. If a difference appears while `bothcase` and an upcase table are enabled, the code switches to a case-insensitive pass. If the upcased names compare equal, the saved direct difference is the tie-breaker.

## State and Persistence Behavior
The file has no state of its own. It consumes the mount-loaded `sbi->upcase` table. Its results affect persistent directory-index ordering and VFS dentry hashing.

## Dependencies and Integration Points
It depends on `ntfs_fs.h` and Linux hashing helpers. Record insertion, directory lookup, rename, and dentry operations depend on these comparisons. The `nocase` mount option changes how dentry operations use them.

## Risks
Callers must supply a valid upcase table. Incorrect tie-breaking can unsort directory indexes or mishandle duplicate names. The code follows NTFS code-unit semantics, not locale normalization.

## Test Signals
Test ASCII folding, non-ASCII table mappings, equal-insensitive/different-sensitive names, prefix ordering, mixed-endian inputs, `nocase` dcache lookup, and Windows-created directory images.
