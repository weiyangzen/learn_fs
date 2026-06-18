# sources/compression/zlib/test/minigzip.c

`minigzip.c` is a small gzip-like command-line example and test utility. It demonstrates gzip file APIs, stdio/file-descriptor integration, pipe mode, file replacement, compression level/strategy selection, platform binary mode, and optional memory-mapped compression.

Key functions are `string_copy()`, optional `Z_SOLO` replacements for `gzopen()`, `gzdopen()`, `gzwrite()`, `gzread()`, `gzclose()`, and `gzerror()`, `gz_compress_mmap()`, `gz_compress()`, `gz_uncompress()`, `file_compress()`, `file_uncompress()`, and `main()`. Options include `-c`, `-d`, `-f`, `-h`, `-r`, and `-1` through `-9`; executable basenames `gunzip` and `zcat` imply decompression modes.

File mode creates destination files and unlinks originals after successful compression/decompression; pipe mode leaves inputs untouched. Integration points include zlib `gz*` APIs, `deflateInit2()`/`inflateInit2()` in solo mode, platform headers, and build scripts. Risks are intentionally limited error handling, non-atomic replacement, fragile suffix handling for nonstandard `GZ_SUFFIX`, simplified solo behavior, and large-file casts in the mmap path. Test signals are byte-equivalent round trips and nonzero exit on I/O or zlib errors.
