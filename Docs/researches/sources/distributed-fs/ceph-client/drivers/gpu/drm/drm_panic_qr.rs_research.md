# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_panic_qr.rs

## Purpose

`drm_panic_qr.rs` is a no-allocation QR encoder used by DRM panic QR mode. It generates QR-L images into caller-provided buffers, supporting raw binary payloads and a URL-plus-compressed-log mode that encodes binary data efficiently as numeric QR data.

## Important APIs, Types, and Functions

- `Version` encapsulates QR versions 1 through 40 and exposes width, capacity, block counts, ECC size, alignment pattern, polynomial, and version info.
- `VPARAM`, generator polynomial constants, alignment tables, version info, format info, Galois field tables, and padding constants define the QR-L encoding parameters.
- `Segment` represents binary and numeric segments; numeric mode converts every 7 bytes into 17 decimal digits to minimize URL-safe overhead.
- `DecFifo` and `SegmentIterator` stream decimal triples for numeric QR encoding without heap allocation. `div10()` avoids unavailable ARM 32-bit division helpers.
- `EncodedMsg` writes segment headers, data bits, padding, Reed-Solomon error correction, and exposes interleaved byte iteration.
- `QrImage` draws finder, alignment, timing, format, version, data, and mask modules into a 1-bit-per-module image.
- `drm_panic_qr_generate()` is the exported C ABI encoder.
- `drm_panic_qr_max_data_size()` reports the maximum payload size for a configured version and URL length.

## Control Flow

The C entry validates buffer sizes (`data_size >= 4071`, `tmp_size >= 3706`) and payload length. Without a URL, it builds one binary segment from `data[0..data_len]`. With a URL, it parses the nul-terminated URL as a C string, builds a binary URL segment and a numeric data segment, then asks `EncodedMsg::new()` for the smallest QR version that fits. Encoding clears the temp buffer, emits segment headers/length/data, writes stop bits and alternating padding bytes, computes Reed-Solomon ECC per QR block, and returns an interleaved data iterator.

`QrImage::new()` clears the output data buffer, draws reserved QR patterns, streams encoded bytes through the QR zig-zag placement order while skipping reserved modules, fills remaining modules, writes format info for low error correction and mask 0, then applies a checkerboard mask to non-reserved modules. The output buffer is overwritten with a packed 1-bit QR image, and the function returns the QR width in modules.

## State and Persistence

The Rust code keeps no global mutable state. All work uses static tables, stack arrays bounded by `MAX_BLK_SIZE + MAX_EC_SIZE`, and caller-provided mutable slices. The C caller owns and reuses the data and temporary buffers.

## Dependencies and Integration Points

It uses Rust-for-Linux `kernel::prelude`, `CStr`, and `#[export]` for C ABI exports consumed by `drm_panic.c`. The implementation is intentionally limited to QR low error correction and fixed mask 0 to keep panic-time code small and deterministic.

## Risks and Edge Cases

- Safety relies on C callers passing valid pointers and buffer lengths for the whole call.
- The encoder returns `0` on invalid size, invalid version, or data that cannot fit; `drm_panic.c` treats this as QR failure.
- Only low ECC and mask 0 are supported, so generated codes may be less robust than a fully optimized QR encoder.
- Numeric data conversion must match the decoder used by the configured QR URL endpoint.
- `drm_panic_qr_max_data_size()` is approximate for URL mode because it reserves headers and applies a 39/40 ratio for numeric conversion.
- ARM-specific division avoidance is important for kernel linkability on 32-bit ARM.

## Test Signals

Tests should validate generated widths for known payload sizes, raw binary and URL/numeric paths, max data size calculations for versions 1, 7, 40 and invalid versions, buffer-size rejection, Reed-Solomon/interleaving against known QR vectors, reserved module placement, and scanner readability for panic-generated images.
