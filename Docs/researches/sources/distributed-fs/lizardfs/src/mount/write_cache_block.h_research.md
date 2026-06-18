## sources/distributed-fs/lizardfs/src/mount/write_cache_block.h

Purpose: declares `WriteCacheBlock`, the write cache's owned memory block plus metadata.

Important APIs/types: enum `Type` distinguishes writable, read-only-after-submit, parity, and read-for-parity blocks. Public fields expose `blockData`, chunk/block indexes, valid range, and type. Copy is deleted; move is supported. Methods expand data and compute file/chunk offsets, size, and data pointers.

Integration: used by write data/cache code to merge byte ranges within one filesystem block and pass buffers to chunk writers.

Risks and tests: public mutable fields permit invariant violations outside the class. Tests should assert callers cannot create out-of-bounds ranges and that moved blocks remain destructible.
