# sources/distributed-fs/ceph/src/rgw/rgw_compression_types.h

## Purpose
`rgw_compression_types.h` defines the persistent metadata format for RGW object compression. The metadata lets RGW map logical object offsets to compressed storage offsets and reconstruct the original object during reads.

## Important APIs, Types, And Functions
`compression_block` stores one compressed block mapping: `old_ofs` is the original logical offset, `new_ofs` is the compressed object offset, and `len` is the compressed block length. It has versioned Ceph encode/decode and `dump()`.

`RGWCompressionInfo` stores `compression_type`, `orig_size`, optional `compressor_message`, and a vector of `compression_block`s. It encodes version 2, preserving compatibility with version 1 metadata that did not include `compressor_message`. The default constructor represents no compression with type `"none"` and size zero. `generate_test_instances()` supplies encode/decode coverage data.

## Control Flow
PUT compression code builds a block vector as chunks are compressed and then persists an `RGWCompressionInfo` attr. GET code decodes this attr, uses the block map to project ranges, and passes `compressor_message` back to the compressor for algorithms that need side-channel state.

## State And Persistence Behavior
This is a persisted wire/storage contract. `RGWCompressionInfo` is stored under `RGW_ATTR_COMPRESSION` by object write paths and later decoded by read paths, admin dump paths, and SAL drivers. Version changes must be additive and compatible with old objects.

## Dependencies And Integration Points
The file depends on Ceph `include/encoding.h`, `bufferlist`, optional/string/vector, and formatter declarations. `rgw_compression.cc`, object operation code, SAL drivers, and admin decode/dump code consume these types.

## Risks And Edge Cases
A block vector with zero entries is rejected by `rgw_compression_info_from_attr()` even if the type says compressed, so writers must not persist empty compressed metadata. The block map does not by itself encode decompressed block lengths; consumers infer range behavior from ordered `old_ofs` and compressed lengths, making ordering and offset consistency important. Optional `compressor_message` must remain compatible with the chosen compressor type.

## Test Signals
Tests should include encode/decode for v1 and v2 metadata, formatter dumps with and without `compressor_message`, empty block rejection at decode time, and range projection against multi-block maps.
