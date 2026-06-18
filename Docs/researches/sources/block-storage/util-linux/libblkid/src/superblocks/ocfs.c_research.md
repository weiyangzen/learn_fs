# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/ocfs.c

## Scope

Implements probes for OCFS1/NTOCFS, OCFS2, and Oracle ASM disk labels.

## Behavior

- OCFS reads volume header and label structures at the magic offset and plus 512 bytes.
- Exports secondary type (`ocfs1` or `ntocfs`), label, mount name, UUID, and major/minor version.
- OCFS2 reads the superblock, exports label, UUID, version, and block size from `s_blocksize_bits`.
- Oracle ASM exports `dl_id` as the label when `ORCLDISK` is found.

## Dependencies And Risks

- Length fields for OCFS label and mount are checked against fixed array sizes before export.
- OCFS2 block-size shift is guarded below 32 to avoid invalid shifts.
- The three idinfos share one file but represent distinct libblkid signatures and usages.
