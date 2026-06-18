# sources/distributed-fs/openafs/src/dir/salvage.c

This file validates and repairs AFS directory files. `DirOK` determines whether a directory is definitely corrupt, and `DirSalvage` builds a fresh directory containing recoverable entries from a suspect source.

Important functions are internal `ComputeUsedPages`, public `DirOK`, and public `DirSalvage`. `DirOK` reads page 0, checks magic tags, allocation map ranges and contiguity, used page count, page freebitmap counts, hash-chain bounds, entry flags, null/too-long names, correct hash buckets, `.` at entry 13, `..` at entry 14, loop limits, and consistency between computed and stored freebitmaps. It distinguishes logical corruption from physical I/O errors through `DReadWithErrno`/`afs_dir_GetBlobWithErrno`, logging and dying for uncertain physical failures.

`DirSalvage` creates a target directory with supplied self/parent fids, reads source hash chains within valid page bounds, skips `.`/`..`, and recreates other entries until a chain becomes unrecoverable. State is persistent directory pages in the target and reads from the source. Dependencies are `dir.h`, `AFSNAMEMAX`, `Log`, `Die`, and directory APIs. Risks include best-effort salvage losing entries after chain damage, duplicate name handling, and relying on name termination. Test signals are dtest `-c` and `-s`, plus fuzzed/corrupted directory images.
