# sources/distributed-fs/openafs/src/dir/dir.h

This header defines the AFS directory on-disk structures and public directory/buffer APIs. Constants define page size (`AFS_PAGESIZE` 2048), hash buckets (`NHASHENT` 128), old/new page limits (`MAXPAGES` 128, `BIGMAXPAGES` 1023), entries per page (`EPP` 64), and header-reserved entries (`DHE` 12).

Important types are `MKFid`, `PageHeader`, `DirBuffer`, `DirHeader`, `DirEntryFlex`, `DirEntry`, `DirXEntry`, `DirPage0`, `DirPage1`, and `dir_file_t` (kernel `struct dcache *`, userspace `struct DirHandle *`). It declares all `afs_dir_*` operations, buffer operations `DInit`/`DRead`/`DNew`/`DRelease`/flush/stat helpers, and userspace salvage `DirOK`/`DirSalvage`.

There is no runtime state in the header, but its layout is persistent on disk. Dependencies include `afs_int32`, `AFS_NORETURN`, and optional `HAVE_FLEXIBLE_ARRAY`. Integration is with directory library sources, fileserver, volserver, salvager, and tests. Risks are structure packing/layout changes, `DHE` needing coordinated changes in `MakeDir` and salvager, and flexible-array compatibility. Test signals are ABI/layout checks and round-trip directory operations across old/new directory formats.
