# File Research: sources/cow-pools/bcachefs-tools/include/linux/zlib.h

Wraps system `<zlib.h>` with kernel-style names. Workspace-size macros return zero, and inflate/deflate names alias directly to zlib functions. `DEF_MEM_LEVEL` is set to 8.
