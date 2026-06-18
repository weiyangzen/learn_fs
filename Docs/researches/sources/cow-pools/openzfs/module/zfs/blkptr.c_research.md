# File Research: sources/cow-pools/openzfs/module/zfs/blkptr.c

## Scope

Implements encoding and decoding of embedded-data block pointers, where small compressed payloads are stored directly inside a `blkptr_t`.

## APIs And Behavior

- `encode_embedded_bp_compressed()` clears the block pointer, sets embedded/compression/byteorder/size fields, and packs payload bytes into permitted payload words using bitfield macros.
- `decode_embedded_bp_compressed()` reverses that packing and extracts the compressed payload bytes from payload words.
- `decode_embedded_bp()` validates output length, decodes the compressed payload, and either returns it directly for uncompressed data or wraps source/destination buffers in stack ABDs and calls `zio_decompress_data()`.

## State And Dependencies

Uses `blkptr_t` layout macros, embedded BP size/compression fields, `zio_decompress_data()`, and transient ABD wrappers around stack/local buffers.

## Risks And Invariants

Only payload words may be used; the encoder/decoder skip non-payload words in the block pointer. Payload size must not exceed `BPE_PAYLOAD_SIZE`, and logical size must fit the caller buffer exactly. Decompression assumes embedded payloads are byte streams and relies on ABD wrappers being freed after use even though they do not own external buffers.
