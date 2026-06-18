<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/dir_f.h -->
# sources/distributed-fs/ceph-client/fs/adfs/dir_f.h

## Purpose
`dir_f.h` defines packed on-disk structures and constants for ADFS E/F format directories.

## Important APIs, types, and functions
Definitions include `ADFS_NEWDIR_SIZE`, `ADFS_NUM_DIR_ENTRIES`, `ADFS_F_NAME_LEN`, `struct adfs_dirheader`, `struct adfs_direntry`, `struct adfs_olddirtail`, and `struct adfs_newdirtail`.

## Control flow
No executable flow. `dir_f.c` interprets buffers using these layouts.

## State and persistence
The structures describe persistent disk bytes: header sequence/name, 26-byte directory entries, and old/new tail variants with parent ID, title, sequence, magic name, and check byte.

## Dependencies and integration points
It is included only by the F-format directory implementation and must match the ADFS disk layout exactly.

## Risks and test signals
Risks include packing/alignment changes, field-size mismatches, and old/new tail interpretation errors. Test signals are mounting known F-format images and validating directory checksum behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/dir_f.h -->
