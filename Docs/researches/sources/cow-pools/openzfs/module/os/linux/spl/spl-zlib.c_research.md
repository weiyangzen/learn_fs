# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-zlib.c

## Purpose

Provides SPL zlib compression and decompression wrappers using the Linux kernel zlib API and a reusable workspace kmem cache.

## Main State

- `zlib_workspace_cache`: cache for deflate/inflate workspaces, avoiding repeated vmalloc/vfree behavior.

## Functions

- `zlib_workspace_alloc()` / `zlib_workspace_free()`: allocate/free cached workspaces, clearing `__GFP_FS` from allocation flags.
- `z_compress_level(dest, destLen, source, sourceLen, level)`: compresses a buffer using `zlib_deflateInit`, `zlib_deflate(..., Z_FINISH)`, and `zlib_deflateEnd`.
- `z_uncompress(dest, destLen, source, sourceLen)`: decompresses a buffer using inflate APIs and maps some stream failures to `Z_DATA_ERROR`.
- `spl_zlib_init()`: creates `spl_zlib_workspace_cache` sized to the max deflate/inflate workspace requirement.
- `spl_zlib_fini()`: destroys the workspace cache.

## Exports

- `z_compress_level`
- `z_uncompress`

## Notes

The functions are adapted from zlib’s `compress2()` / `uncompress()` semantics but wired to kernel zlib and SPL allocation. Destination sizes are checked for truncation to zlib’s `uInt`.
