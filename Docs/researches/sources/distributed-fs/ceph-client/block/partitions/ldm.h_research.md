<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/ldm.h -->
# sources/distributed-fs/ceph-client/block/partitions/ldm.h

## Purpose

`ldm.h` defines the constants and in-memory structures used by `ldm.c` to parse Microsoft Logical Disk Manager dynamic-disk metadata. It names magic values, VBLK types, VBLK flags, fixed offsets in the 1 MiB database, and cache structures for parsed database objects.

## Important APIs, Types, And Functions

There are no functions in this header. Important constants include `MAGIC_VMDB`, `MAGIC_VBLK`, `MAGIC_PRIVHEAD`, `MAGIC_TOCBLOCK`, `VBLK_VOL5`, `VBLK_CMP3`, `VBLK_PRT3`, `VBLK_DSK3`, `VBLK_DSK4`, `VBLK_DGR3`, `VBLK_DGR4`, `LDM_DB_SIZE`, `OFF_PRIV*`, `OFF_TOCB*`, `OFF_VMDB`, `LDM_PARTITION`, `TOC_BITMAP1`, and `TOC_BITMAP2`.

Important types are `struct frag`, `struct privhead`, `struct tocblock`, `struct vmdb`, the VBLK payload structs (`vblk_comp`, `vblk_dgrp`, `vblk_disk`, `vblk_part`, `vblk_volu`), `struct vblk_head`, `struct vblk`, and `struct ldmdb`.

## Control Flow

Control flow is supplied by `ldm.c`; this header shapes it by giving the parser fixed offsets and typed destinations. `struct ldmdb` is the central control object: validation fills `ph`, `toc`, and `vm`, then VBLK parsing populates the five `list_head` collections used by partition creation.

## State And Persistence Behavior

The structures here are in-memory normalized forms of on-disk LDM records. Numeric fields are stored in CPU-endian form after parsing. Lists are transient parser state and are not persisted. The persistent representation remains the disk database; the header deliberately does not define packed on-disk structs for most VBLKs because the format uses variable-width fields.

## Dependencies And Integration Points

The header includes Linux type, list, filesystem, unaligned-access, and byteorder headers. It forward-declares `struct parsed_partitions` for the parser integration. It is private to the partition parser implementation and is not a general LDM kernel API.

## Risks And Edge Cases

Constants in this file are format contracts. Incorrect VBLK fixed sizes, offsets, or flags would break parsing and could cause invalid range checks in `ldm.c`. The flexible-array `struct frag` assumes allocations size `sizeof(*f) + size * num`; callers must ensure `num` and `size` are bounded.

## Test Signals

Signals are indirect through `ldm.c`: valid Windows 2000/XP and Vista dynamic-disk images should parse, unsupported VBLK types should be ignored or rejected as designed, and structures should compile cleanly across 32-bit and 64-bit architectures with correct UUID and list alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/ldm.h -->
