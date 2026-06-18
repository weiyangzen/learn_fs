<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/dir_fplus.h -->
# sources/distributed-fs/ceph-client/fs/adfs/dir_fplus.h

## Purpose
`dir_fplus.h` defines packed on-disk structures and constants for ADFS F+ directories.

## Important APIs, types, and functions
It defines `ADFS_FPLUS_NAME_LEN`, `BIGDIRSTARTNAME`, `BIGDIRENDNAME`, `struct adfs_bigdirheader`, `struct adfs_bigdirentry`, and `struct adfs_bigdirtail`.

## Control flow
No executable flow. `dir_fplus.c` uses the definitions to validate and parse F+ directories.

## State and persistence
The structures represent persistent disk layout: directory header with size/count/name metadata, fixed-size big directory entries pointing into a names area, and an end marker/check byte tail.

## Dependencies and integration points
It is private to the F+ directory implementation and must remain packed/aligned to match disk format.

## Risks and test signals
Risks include endian mistakes, structure alignment changes, maximum name-length mismatches, and magic constant errors. Test signals include F+ image mount/iterate/update tests and corrupt directory validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/dir_fplus.h -->
