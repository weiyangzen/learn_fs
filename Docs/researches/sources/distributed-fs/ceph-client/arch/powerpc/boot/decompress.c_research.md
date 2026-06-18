# sources/distributed-fs/ceph-client/arch/powerpc/boot/decompress.c

## Purpose
Boot-wrapper adapter around kernel decompression code that can decompress all or part of a compressed kernel image while supporting output skipping.

## Important APIs, Types, And Control Flow
The file includes gzip or xz decompressor sources depending on kernel compression config. `partial_decompress(inbuf, input_size, outbuf, output_size, _skip)` initializes global progress state, adds skipped bytes to the decompression limit, calls `__decompress()`, and returns either decompressed bytes after skip or the decompressor error. `flush()` is the output callback: it tracks `decompressed_bytes`, discards blocks before `skip`, copies the wanted window into `output_buffer`, and returns `-1` after `limit` to intentionally abort once enough output is produced. `print_err()` suppresses that intentional abort.

## State, Dependencies, Risks, And Tests
State is global and single-threaded: `decompressed_bytes`, `limit`, `skip`, and `output_buffer`. Dependencies include copied/fixed kernel decompressor sources, `min`, boot-wrapper `printf`, and compression Kconfig. Risks include global non-reentrancy, treating intentional abort as success, off-by-one at skip/limit boundaries, and decompressor-specific negative returns. Test gzip/xz images, full and partial decompression, skip crossing flush block boundaries, zero output size, insufficient/corrupt input, and output buffer bounds.
