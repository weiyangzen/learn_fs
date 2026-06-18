<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/lib/lib.h -->
## sources/distributed-fs/ceph-client/fs/ntfs3/lib/lib.h

Purpose: declares the small public interface of the NTFS3 XPRESS and LZX decompression library used by system-compressed file handling.

Important APIs and types: forward-declares `struct xpress_decompressor` and `struct lzx_decompressor`; declares allocator/free pairs `xpress_allocate_decompressor`/`xpress_free_decompressor` and `lzx_allocate_decompressor`/`lzx_free_decompressor`; and declares `xpress_decompress` and `lzx_decompress`, each taking compressed input, compressed size, output buffer, and expected uncompressed size.

Control flow: callers allocate a reusable decompressor context, call the relevant format-specific decompressor for one buffer, then free the context. The header itself has no executable control flow.

State and persistence behavior: decompressor contexts are opaque to callers and hold reusable Huffman tables and scratch buffers. There is no persistent on-disk state here; persistence is in the NTFS file data streams that higher layers read.

Dependencies and integration points: includes Linux types and is included by the XPRESS and LZX implementations and by NTFS compression code that chooses the algorithm for WOF/system-compressed data.

Risks: return conventions are `0` success and `-1` decompressor failure for XPRESS/LZX, not Linux `-errno` values. Callers must not assume the opaque contexts are interchangeable, must pass exact uncompressed sizes, and must handle allocation failure with `GFP_NOFS` constraints.

Test signals: compile with and without `CONFIG_NTFS3_LZX_XPRESS`, allocation failure injection, API misuse checks in callers, and known XPRESS/LZX decompression vectors through the public prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/lib/lib.h -->
