# sources/distributed-fs/ceph/src/rgw/rgw_compression.h

## Purpose
`rgw_compression.h` declares the RGW compression/decompression filter interfaces used by object PUT and GET paths. It connects persistent compression metadata to the runtime data processor/filter pipeline.

## Important APIs, Types, And Functions
`rgw_compression_info_from_attr()` and `rgw_compression_info_from_attrset()` expose metadata decoding and a `need_decompress` decision to callers that have object attrs. `RGWGetObj_Decompress` derives from `RGWGetObj_Filter` and overrides `handle_data()` plus `fixup_range()` to transform compressed storage bytes into logical object bytes. Its state includes the compressor, compression metadata, partial-content mode, selected first/last blocks, requested output offset/length, current compressed offset, and a `waiting` buffer for incomplete blocks.

`RGWPutObj_Compress` derives from `rgw::putobj::Pipe` and overrides `process()` to compress incoming data before passing it to the next `DataProcessor`. It exposes `is_compressed()`, `get_compression_blocks()`, and `get_compressor_message()` so higher-level PUT code can persist `RGWCompressionInfo`.

## Control Flow
Callers insert `RGWPutObj_Compress` into the PUT pipeline when a compression policy selected a `CompressorRef`. After all data is processed, the caller inspects whether compression actually occurred and persists the resulting block map. For reads, callers decode attrs, construct `RGWGetObj_Decompress` when needed, call `fixup_range()` before fetching data, and pass fetched compressed chunks through `handle_data()`.

## State And Persistence Behavior
The header itself declares transient filter state. The persistent representation is `RGWCompressionInfo` from `rgw_compression_types.h`; `RGWPutObj_Compress` exposes the pieces needed to build that attr. `RGWGetObj_Decompress` holds a raw pointer to `RGWCompressionInfo`, so the metadata object must outlive the filter.

## Dependencies And Integration Points
The declarations depend on `compressor/Compressor.h`, `rgw_putobj.h`, `rgw_op.h`, and `rgw_compression_types.h`. This couples compression to both the PUT data processor pipeline and the GET object filter abstraction.

## Risks And Edge Cases
`RGWGetObj_Decompress` stores iterators into `cs_info->blocks`; mutating or destroying `cs_info` while the filter is active would invalidate them. The PUT filter assumes logical offsets are supplied consistently by upstream processors. API consumers must not persist compression metadata unless `is_compressed()` is true and the block vector is valid.

## Test Signals
Header-level integration tests should instantiate filters in realistic GET/PUT chains, verify lifetime expectations for `RGWCompressionInfo`, and assert that callers persist block metadata only after successful compressed writes.
