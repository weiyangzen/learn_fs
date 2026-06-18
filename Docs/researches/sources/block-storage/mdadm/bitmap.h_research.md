# File Research: sources/block-storage/mdadm/bitmap.h

## Purpose
`bitmap.h` defines md bitmap superblock constants and the on-disk bitmap superblock layout.

## Contents
It declares bitmap major versions, including clustered and lockless versions, `BITMAP_MAGIC`, bitmap state bit values, and `bitmap_super_t`.

The superblock stores magic, version, UUID, event counters, sync size, state, chunk size, daemon sleep interval, write-behind count, reserved sectors, clustered node count, cluster name, and padding to 256 bytes.

## Integration Notes
Fields are documented as little-endian on disk and are converted by `bitmap.c`. The layout is shared with kernel md bitmap expectations.
