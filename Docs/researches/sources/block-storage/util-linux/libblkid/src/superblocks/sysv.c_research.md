# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/sysv.c

## Scope

Implements Xenix and System V filesystem probing.

## Behavior

- Xenix uses static magic at known offsets and exports the short filesystem name as label.
- SysV manually probes four possible superblock positions and accepts either little-endian or big-endian magic.
- On SysV match, exports label and records the exact magic offset.

## Dependencies And Risks

- SysV uses `BLKID_NONE_MAGIC` because the offset/endian combinations are easier to express in code.
- Coherent FS is intentionally not probed because it lacks a reliable magic string.
