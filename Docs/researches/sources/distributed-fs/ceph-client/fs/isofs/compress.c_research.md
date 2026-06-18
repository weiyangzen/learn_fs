## sources/distributed-fs/ceph-client/fs/isofs/compress.c

Purpose: implements zisofs transparent decompression for compressed ISOFS regular files.

Important APIs and state: exports `zisofs_aops` with `.read_folio = zisofs_read_folio`, plus `zisofs_init` and `zisofs_cleanup`. Global `zisofs_zlib_workspace` is allocated with `vmalloc` at module init and protected by `zisofs_zlib_lock` because zlib inflate workspace is shared. `zisofs_sink_page` discards decompressed output for cache pages that could not be allocated for readahead.

Control flow: `zisofs_read_folio` determines the compression block containing the requested page, allocates an array of cache pages for the compression block, opportunistically grabs neighboring pages, and calls `zisofs_fill_pages`. `zisofs_fill_pages` reads the zisofs block-pointer table, then repeatedly calls `zisofs_uncompress_block` for compressed chunks. The decompressor pre-reads all block buffers, locks zlib, inflates into page mappings or the sink page, marks completed pages uptodate, zero-fills partial tail pages, and reports only whether the critical requested page succeeded.

State and persistence: no on-disk writes occur. Persistent state is the Rock Ridge ZF metadata parsed elsewhere into `ISOFS_I(inode)->i_format_parm` and `i_size`. Runtime state includes page-cache uptodate bits and decompressed folio contents.

Dependencies and integration points: depends on `isofs_get_blocks`, `isofs_bread`, zlib inflate, buffer heads, page cache, and Rock Ridge ZF parsing in `rock.c`. It intentionally has no bmap support for compressed files.

Risks and test signals: risks are malicious or corrupt compressed block tables, block_start/block_end inversion, compressed size exceeding deflate bounds, shared zlib serialization, pages outside EOF, and partial success semantics for readahead pages. Test with valid zisofs media, empty compressed blocks, truncated pointer tables, corrupt compressed streams, large compression blocks, OOM while grabbing readahead pages, and reads near EOF.
