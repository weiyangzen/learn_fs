## sources/distributed-fs/lizardfs/src/mount/write_cache_block.cc

Purpose: implements the movable block buffer used by write-cache/chunk-writer logic.

Important APIs: constructor allocates one `MFSBLOCKSIZE` buffer for a chunk/block/type and asserts `blockIndex < MFSBLOCKSINCHUNK`. Move constructor/assignment transfer or swap ownership. `expand(from, to, buffer)` initializes or extends the valid byte range if the new range overlaps/touches current data. `offsetInFile`, `offsetInChunk`, `size`, and `data` expose location and valid bytes.

State and dependencies: each block stores raw `blockData`, chunk index, block index, valid `[from, to)` range, and type. Depends on `MFSCommunication` constants and `massert`.

Risks: `expand` does not validate `to <= MFSBLOCKSIZE` or `from <= to`; callers must enforce bounds. Move assignment via swaps leaves the moved-from object owning the old destination buffer, which is valid but subtle. Raw buffer is always full block size even for small writes.

Test signals: construct/move/destruct, overlapping and non-overlapping expand, boundary offsets, parity/read-only type propagation, and invalid range assertions.
