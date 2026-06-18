# sources/distributed-fs/ceph/src/rgw/rgw_compression.cc

## Purpose
`rgw_compression.cc` implements RGW object compression and decompression filters. It decodes persisted compression metadata, compresses incoming PUT data before handing it to the next data processor, and decompresses GET data while projecting requested logical ranges onto compressed storage ranges.

## Important APIs, Types, And Functions
`rgw_compression_info_from_attr()` decodes `RGWCompressionInfo` from a bufferlist attr, rejects malformed or empty block metadata, and sets `need_decompress` based on `compression_type != "none"`. `rgw_compression_info_from_attrset()` looks up `RGW_ATTR_COMPRESSION` in an attr map and treats absence as no decompression required.

`RGWPutObj_Compress::process()` receives logical object data, calls `Compressor::compress()`, tracks whether the stream remains compressed, appends `compression_block` entries mapping original offsets to compressed offsets/lengths, and forwards either compressed or original data to `Pipe::process()` at the correct physical offset.

`RGWGetObj_Decompress::handle_data()` accumulates partial compressed blocks in `waiting`, extracts complete compressed blocks, calls `compressor->decompress()`, and streams decompressed output to the next `RGWGetObj_Filter` in chunks capped by `rgw_max_chunk_size`. `fixup_range()` calls `project_compress_range()` to map the requested logical range onto compressed block indices and physical byte range.

`compression_block::dump()`, `RGWCompressionInfo::dump()`, and `generate_test_instances()` provide formatter and encoding test support.

## Control Flow
On PUT, the first non-empty chunk attempts compression. If first-part compression fails, the object is stored uncompressed. If a later chunk fails after compression already started, the operation fails with `-EIO` because mixed compressed/uncompressed continuation would invalidate the block map. Empty chunks only advance the compressed offset to the end of the last block.

On GET, callers first decode compression attrs and call `fixup_range()` so lower layers fetch the compressed byte range that contains all needed blocks. As data arrives, `handle_data()` merges any prior incomplete block, waits until the full compressed block is present, decompresses it, skips `q_ofs`, emits up to `q_len`, and updates `cur_ofs`.

## State And Persistence Behavior
`RGWCompressionInfo` and its `compression_block` vector are persisted as `RGW_ATTR_COMPRESSION` by higher-level PUT code. This file mutates only per-operation filter state: current compressed offset, compressor message, block vector, range projection iterators, pending bytes, and remaining output range. The compressor-specific optional message is preserved in metadata and passed back to decompression.

## Dependencies And Integration Points
The file depends on Ceph `Compressor`, `rgw_putobj` pipelines, `RGWGetObj_Filter`, `RGW_ATTR_COMPRESSION` from `rgw_common.h`, and `rgw_range_projection.h`. It is integrated by RGW operation and SAL paths that optionally install compression on PUT and decompression on GET or copy/read workflows.

## Risks And Edge Cases
Range projection and block iterator arithmetic are correctness-critical; invalid or empty block metadata returns `-EIO`, but corrupted offsets could still lead to bad seeks or output truncation if not validated upstream. `handle_data()` stores incomplete compressed block tails in memory and adjusts `cur_ofs` with `cur_ofs -= tail`, so unsigned/offset interactions deserve tests. Compression fallback is asymmetric: first-part failure stores uncompressed, later failure aborts. Missing compressor plugins make reads fail with `-EIO`.

## Test Signals
Tests should cover attr absence, malformed attr decode, `compression_type == "none"`, first-chunk compression failure fallback, later-chunk failure abort, block map offset generation, full and partial range decompression, multi-input chunks that split compressed blocks, and max-chunk-size output splitting.
