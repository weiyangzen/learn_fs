# sources/distributed-fs/openafs/src/dir/dir.c

This file implements the AFS on-disk directory format: 2 KiB pages, 64 32-byte directory blobs per page, page/free bitmaps, header allocation map, and 128 hash chains mapping names to fids.

Important public APIs are `afs_dir_NameBlobs`, `afs_dir_Create`, `afs_dir_Length`, `afs_dir_Delete`, `afs_dir_MakeDir`, `afs_dir_Lookup`, `afs_dir_LookupOffset`, `afs_dir_EnumerateDir`, `afs_dir_IsEmpty`, `afs_dir_GetBlobWithErrno`, `afs_dir_GetBlob`, `afs_dir_GetVerifiedBlob`, `afs_dir_DirHash`, `afs_dir_InverseLookup`, and `afs_dir_ChangeFid`. Internal helpers are `FindBlobs`, `AddPage`, `FreeBlobs`, `GetBlobWithLimit`, `FindItem`, and `FindFid`.

Control flow for create checks for duplicates, finds contiguous free blobs, writes a `DirEntry`, and links it into the hash table. Delete unlinks from a hash chain, clears the entry plus extension blobs, and updates free maps. Lookup and enumeration walk hash chains with loop bounds and verified blob reads. `MakeDir` formats page 0 and creates `.` and `..`. State persists in directory pages through `DNew`, `DRead`, and dirty `DRelease`. Risks include on-disk ABI fragility, bitmap/hash corruption, name termination validation, and caller ownership of locked buffers. Test signals are dtest create/delete/list/check/salvage workflows and salvager validation against corrupted directories.
