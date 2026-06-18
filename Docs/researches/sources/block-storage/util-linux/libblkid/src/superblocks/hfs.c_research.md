# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/hfs.c

HFS and HFS+ detector. The HFS path reads the master directory block, rejects embedded HFS+ volumes, validates allocation block size alignment, derives a UUID from Finder info using the HFS MD5 namespace algorithm, and sets the Pascal-style HFS label.

The HFS+ path handles both native HFS+ and HFS+-embedded-in-HFS layouts. It validates signatures, computes embedded offsets from HFS allocation metadata when needed, checks HFS+ block size, emits UUID and block size, then reads the catalog B-tree header and first leaf node to recover the UTF-16BE volume label from the catalog key.

HFS is marked tolerant because it can coexist as a wrapper around embedded HFS+. The HFS+ catalog walk is partial but defensive: it validates node size, leaf count, extent coverage, leaf type, record count, parent id, and Unicode length before using label data.
