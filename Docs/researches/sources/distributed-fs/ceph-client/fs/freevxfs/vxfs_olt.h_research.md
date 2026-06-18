# sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_olt.h

## Purpose

`sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_olt.h` defines the on-disk FreeVxFS Object Location Table header and record types. The complete 120-line file was read for this report.

## Important APIs, Types, and Functions

Definitions include `VXFS_OLT_MAGIC`, OLT type constants (`VXFS_OLT_FREE`, `FSHEAD`, `CUT`, `ILIST`, `DEV`, `SB`), `struct vxfs_olt`, `struct vxfs_oltcommon`, `struct vxfs_oltfree`, `struct vxfs_oltilist`, `struct vxfs_oltcut`, `struct vxfs_oltsb`, `struct vxfs_oltdev`, and `struct vxfs_oltfshead`.

## Control Flow

There is no runtime flow. `vxfs_olt.c` uses the common record prefix to switch on record type and cast to specific record structures.

## State and Persistence Behavior

All structures describe persistent OLT metadata. The Linux driver currently consumes only fileset-header and initial-inode-list records, while the header also models free, current-usage-table, superblock/log/OLT, and device records.

## Dependencies and Integration Points

The header depends on `__fs32` from the FreeVxFS superblock header and is used during mount metadata discovery.

## Risks and Edge Cases

The common-prefix cast pattern depends on every record starting with type and size. Record size, alignment, and endian conversion must be handled by consumers; the header itself provides no validation.

## Test Signals

Signals include OLT parser fixtures for each record type, endian checks, size/alignment tests, and fuzzed record streams.
