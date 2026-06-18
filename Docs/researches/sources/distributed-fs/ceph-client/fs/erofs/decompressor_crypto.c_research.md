<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/decompressor_crypto.c -->
# sources/distributed-fs/ceph-client/fs/erofs/decompressor_crypto.c

## Purpose
`decompressor_crypto.c` adds optional hardware/crypto API decompression engines for EROFS compressed data, currently wiring named crypto acomp engines such as `qat_deflate`.

## Important APIs, types, and functions
Important functions are `z_erofs_crypto_decompress`, `z_erofs_crypto_enable_engine`, `z_erofs_crypto_disable_all_engines`, and `z_erofs_crypto_show_engines`. Internal state is `struct z_erofs_crypto_engine` arrays indexed by EROFS compression algorithm and guarded by `z_erofs_crypto_rwsem`.

## Control flow
Decompression takes a read lock, locates an enabled engine for the request algorithm, fills any missing output pages from the pagepool, builds source and destination scatterlists from page arrays and offsets, allocates an acomp request, submits `crypto_acomp_decompress`, waits synchronously, converts failures to `-EIO`, and frees tables/requests. Engine enable scans the configured names, allocates the crypto transform, and stores it; disable frees all enabled transforms.

## State and persistence
State is runtime-only: enabled crypto transform pointers and their names. No on-disk state changes; the same compressed bytes remain readable through software fallback if acceleration is unavailable.

## Dependencies and integration points
It depends on Linux crypto acomp, scatterlist helpers, EROFS pagepool, and the algorithm wrappers that attempt crypto acceleration before software decode.

## Risks and test signals
Risks include scatterlist construction over invalid page arrays, output gap allocation failures, transform lifetime races, name-prefix matching surprises, and synchronous wait latency. Test signals include enabling/disabling engines via sysfs or module controls, deflate reads with QAT available/unavailable, concurrent compressed reads during disable, partial decoding fallback, and crypto error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/decompressor_crypto.c -->
