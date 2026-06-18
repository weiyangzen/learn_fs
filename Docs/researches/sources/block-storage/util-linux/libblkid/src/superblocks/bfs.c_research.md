# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/bfs.c

Minimal BFS filesystem descriptor. It declares `bfs_idinfo` with filesystem usage and a single four-byte magic value. There is no custom probe function; libblkid’s generic superblock magic matching is enough.

The comment notes BFS has two short labels in the superblock, but this detector intentionally ignores them because their meaning is unclear. As a result, detection only reports type and usage, not label, UUID, version, or block geometry.
