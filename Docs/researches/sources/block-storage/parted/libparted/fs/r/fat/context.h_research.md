# File Research: sources/block-storage/parted/libparted/fs/r/fat/context.h

Defines FAT resize operation state.

Important types:
- `FatDirection`: forward/backward cluster-start movement.
- `FatOpContext`: old/new filesystem pointers, fragment geometry, movement delta, buffered relocation map, remap table, duplicated-fragment counter, and FAT32 root-directory allocation list.

Exports:
- Context creation/destruction.
- Static and final fragment/cluster mapping helpers.
- Initial destination FAT creation.

Role:
- Central shared state between `resize.c`, `clstdup.c`, and FAT reconstruction code.
