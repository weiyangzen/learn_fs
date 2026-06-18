# sources/distributed-fs/ceph-client/fs/cramfs/internal.h

Purpose: declares the small internal decompression interface shared by Cramfs implementation files.

Important APIs: `cramfs_uncompress_block(void *dst, int dstlen, void *src, int srclen)`, `cramfs_uncompress_init()`, and `cramfs_uncompress_exit()`.

Control flow: `inode.c` calls init before registering the filesystem, calls block decompression from `cramfs_read_folio()`, and calls exit during module unload or registration failure.

State and persistence: no direct state in the header; `uncompress.c` owns the global zlib stream/workspace.

Dependencies/integration: used only inside `fs/cramfs`; abstracts zlib details away from inode/read logic.

Risks: because the implementation uses a single global zlib stream, callers must preserve serialization around `cramfs_uncompress_block()`; `inode.c` does this with `read_mutex`.

Test signals: compile inclusion by both Cramfs objects, init/decompress/exit ordering, and failure injection for decompressor init.
