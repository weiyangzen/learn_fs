<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/Makefile -->
# sources/distributed-fs/ceph-client/fs/erofs/Makefile

## Purpose
The EROFS Makefile assembles the core filesystem and optional feature objects based on Kconfig selections.

## Important APIs, types, and functions
The base `erofs.o` includes `super.o`, `inode.o`, `data.o`, `namei.o`, `dir.o`, and `sysfs.o`. Optional additions cover xattrs, compressed mapping/decompression, LZMA/DEFLATE/ZSTD algorithms, crypto acceleration, file-backed I/O, fscache, and inode sharing.

## Control flow
No runtime flow exists. Kbuild composes the module or built-in object with only the selected feature units.

## State and persistence
No state is stored here. It controls which runtime feature implementations are present.

## Dependencies and integration points
It mirrors the Kconfig feature split and determines which symbols must be stubbed by headers versus provided by compiled objects.

## Risks and test signals
Risks are unresolved symbols in uncommon feature combinations and missing objects for new features. Test signals are allmodconfig-style builds and targeted matrices for ZIP, FILEIO, ONDEMAND, and PAGE_CACHE_SHARE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/Makefile -->
