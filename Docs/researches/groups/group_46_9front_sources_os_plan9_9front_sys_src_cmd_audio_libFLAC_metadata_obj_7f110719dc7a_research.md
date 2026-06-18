# Group Research: group_46_9front_sources_os_plan9_9front_sys_src_cmd_audio_libFLAC_metadata_obj_7f110719dc7a

Scope checked against `Docs/research_subset_a.md`: all files are inside `sources/os/plan9/9front`, which is included in subset A. Each listed source file was read completely. These files are codec/audio support code rather than filesystem code, but they are part of the covered 9front source tree.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/metadata_object.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/metadata_object.c

## Role

`metadata_object.c` implements libFLAC's in-memory metadata object API. It creates, clones, deletes, compares, validates, and mutates `FLAC__StreamMetadata` blocks for STREAMINFO, APPLICATION, SEEKTABLE, VORBIS_COMMENT, CUESHEET, PICTURE, and unknown metadata.

## Major Functions

- `FLAC__metadata_object_new()` allocates and initializes metadata blocks, including default vendor strings and empty picture strings.
- `FLAC__metadata_object_clone()` performs deep copies of variable-sized fields.
- `FLAC__metadata_object_delete_data()` and `FLAC__metadata_object_delete()` release block-owned allocations.
- `FLAC__metadata_object_is_equal()` dispatches to block-type-specific comparators.
- APPLICATION, SEEKTABLE, VORBIS_COMMENT, CUESHEET, and PICTURE setter APIs resize arrays, insert/delete elements, copy or take ownership, and recalculate metadata block lengths.
- Cuesheet helpers calculate CDDB IDs and delegate legality checks to `FLAC__format_cuesheet_is_legal()`.
- Picture legality is delegated to `FLAC__format_picture_is_legal()`.

## Important Implementation Details

The file has a strong copy-first pattern: setters usually allocate or copy new data before freeing old storage so allocation failure leaves objects unchanged. APIs support both `copy=true` and ownership-transfer mode, with Vorbis comments using a const-stripping workaround when taking ownership because the public API source pointer is const.

Length fields are maintained manually after every structural mutation. Seektable length is `num_points * FLAC__STREAM_METADATA_SEEKPOINT_LENGTH`; Vorbis comments include vendor length, comment count, per-comment lengths, and payloads; cuesheets sum fixed track/index fields; picture setters adjust length by old/new string or data lengths.

The resize helpers use `realloc()` and explicit overflow checks against `UINT32_MAX / sizeof(type)`. Growing seektables initializes new seek points as placeholders; growing Vorbis comments creates empty NUL-terminated entries; growing cuesheet arrays zeroes new tracks/indices.

## Risks / Edge Cases

- Many public APIs rely on `FLAC__ASSERT()` for correct object type, bounds, non-null inputs, and pointer/length consistency.
- Ownership-transfer mode mutates source Vorbis comment entries to ensure NUL termination, which is subtle because the formal source pointer is const.
- `FLAC__metadata_object_vorbiscomment_resize_comments()` can leave a partially grown comments array if allocating one of the new empty entries fails; it adjusts `num_comments` to cover allocated entries for later cleanup.
- Some checks compare against `UINT32_MAX` while allocation sizes are `size_t`; this follows FLAC metadata length limits but should be reviewed on unusual platforms.
- `FLAC__metadata_object_picture_set_mime_type()` and description setters use `strlen()`, so caller-provided strings must be valid C strings.

## Dependencies

Uses `private/metadata.h`, `private/memory.h`, `FLAC/assert.h`, `share/alloc.h`, and `share/compat.h`. It depends heavily on public format validators and constants from `FLAC/format.h` via `FLAC/metadata.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/metadata_object.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/ogg_decoder_aspect.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/ogg_decoder_aspect.c

## Role

`ogg_decoder_aspect.c` adapts libogg page/packet decoding to libFLAC's pull-style decoder read callback. It keeps Ogg stream/sync state, extracts packets from pages, validates the Ogg FLAC mapping header, and feeds FLAC bytes back to the native decoder in bounded chunks.

## Major Functions

- `FLAC__ogg_decoder_aspect_set_defaults()` defaults to using the first observed Ogg serial number.
- `FLAC__ogg_decoder_aspect_init()` initializes `ogg_stream_state` and `ogg_sync_state`, marks mapping version unknown, and resets page/packet state.
- `finish()`, `flush()`, and `reset()` clear or reset Ogg state.
- `set_serial_number()` forces a caller-specified stream serial.
- `FLAC__ogg_decoder_aspect_read_callback_wrapper()` is the core bridge from client reads to FLAC decoder bytes.

## Important Implementation Details

The read wrapper loops until it fills the FLAC-requested byte count, hits end-of-stream, or returns an error. It preserves a working Ogg page and packet across calls so packets can be split across libFLAC read buffers. It reads client data into `ogg_sync_buffer()` in chunks of at least 8192 bytes or the remaining FLAC request size.

On the first Ogg FLAC header packet, it checks packet type `0x7f`, magic `"FLAC"`, mapping version major/minor, and rejects non-major-version-1 streams. After validating the mapping prefix, it advances the packet pointer so libFLAC sees the embedded native `fLaC` stream bytes.

## Risks / Edge Cases

- `working_packet.packet` is advanced in place while bytes are consumed; code using the same packet later must respect the shortened view.
- Lost sync and unsupported mapping versions are surfaced as distinct aspect statuses.
- If `use_first_serial_number` is active, the first page serial is written directly into `stream_state.serialno`.
- Ogg pages from another stream are ignored when `ogg_stream_pagein()` rejects them.
- The wrapper can read more from the client than the immediate FLAC byte request to obtain complete Ogg pages.

## Dependencies

Uses libogg, `private/ogg_decoder_aspect.h`, `private/ogg_mapping.h`, `private/macros.h`, and `FLAC/assert.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/ogg_decoder_aspect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/ogg_encoder_aspect.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/ogg_encoder_aspect.c

## Role

`ogg_encoder_aspect.c` adapts libFLAC stream encoder write callbacks into Ogg FLAC packets and pages. It recognizes the native `fLaC` magic callback, combines it with STREAMINFO into the required first Ogg FLAC header packet, then packetizes metadata and audio frames.

## Major Functions

- `FLAC__ogg_encoder_aspect_set_defaults()` initializes default serial number and metadata count.
- `init()` initializes libogg stream state and packet bookkeeping.
- `finish()` clears libogg stream state.
- `set_serial_number()` and `set_num_metadata()` configure stream serial and header packet count.
- `FLAC__ogg_encoder_aspect_write_callback_wrapper()` converts FLAC write callback buffers into Ogg packets and invokes the client write callback for page header/body output.

## Important Implementation Details

The implementation depends on encoder behavior where the `fLaC` magic arrives as one metadata write callback, followed by STREAMINFO as a separate callback. The first actual Ogg packet is synthetic: packet type, `"FLAC"` mapping magic, version 1.0, two-byte metadata header count, native `fLaC`, and STREAMINFO header/data.

Metadata packets are flushed with `ogg_stream_flush()` so metadata lands promptly in pages. Audio packets use `ogg_stream_pageout()`. `packet.granulepos` is set to `samples_written + samples`; `samples_written` is updated after each wrapper call.

## Risks / Edge Cases

- If encoder callback ordering changes, the wrapper asserts and returns fatal error.
- `set_num_metadata()` rejects values that do not fit the 16-bit Ogg FLAC header count field.
- Page header and body are written with separate client write callback invocations.
- The function passes `samples=0` to the downstream write callback for Ogg page output because page-level sample accounting is not directly mapped.
- `finish()` notes an unresolved comment about the stored page object, though libogg owns stream state cleanup.

## Dependencies

Uses libogg, `private/ogg_encoder_aspect.h`, `private/ogg_mapping.h`, and public stream encoder status definitions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/ogg_encoder_aspect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/ogg_helper.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/ogg_helper.c

## Role

`ogg_helper.c` provides helpers for reading, validating, clearing, and rewriting "simple" Ogg pages during seekable Ogg FLAC encoding. A simple page here means a page containing one complete packet, no continuation, zero granule position, and valid checksum.

## Major Functions

- `full_read_()` repeatedly calls the encoder read callback until a requested byte count is satisfied or an error/status transition occurs.
- `simple_ogg_page__init()` zeroes an `ogg_page`.
- `simple_ogg_page__clear()` frees page header/body allocations and reinitializes.
- `simple_ogg_page__get_at()` seeks to a position, reads an Ogg page header/table/body, validates simple-page structure, and checks CRC.
- `simple_ogg_page__set_at()` seeks to a position, updates page checksum, and rewrites header/body.

## Important Implementation Details

`simple_ogg_page__get_at()` reads the 27-byte fixed Ogg header, uses byte 26 to determine segment table length, and computes body length from lacing values. It verifies `"OggS"`, rejects continued packets, requires zero granule position, and rejects zero-sized packets. The final lacing byte may be less than 255, and all prior lacing bytes must be 255 to represent one packet.

CRC validation saves the four checksum bytes, calls `ogg_page_checksum_set()`, and compares the computed checksum against the saved bytes. Error states are reported through `encoder->protected_->state`.

## Risks / Edge Cases

- On read failures after allocating `page->header` or `page->body`, the caller must clear the page to avoid leaks.
- It only accepts simple one-packet pages and intentionally rejects valid but more complex Ogg pages.
- Callback `END_OF_STREAM` with zero bytes while more bytes are required is treated as Ogg error.
- Seek callback absence or non-OK seek status causes failure; seek errors set client error state.

## Dependencies

Uses libogg, `share/alloc.h`, `private/ogg_helper.h`, and `protected/stream_encoder.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/ogg_helper.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/ogg_mapping.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/ogg_mapping.c

## Role

`ogg_mapping.c` defines the constants for the Ogg FLAC mapping shared by encoder and decoder aspect code.

## Contents

It exports:

- `FLAC__OGG_MAPPING_PACKET_TYPE_LEN = 8`
- `FLAC__OGG_MAPPING_FIRST_HEADER_PACKET_TYPE = 0x7f`
- `FLAC__OGG_MAPPING_MAGIC = "FLAC"`
- `FLAC__OGG_MAPPING_VERSION_MAJOR_LEN = 8`
- `FLAC__OGG_MAPPING_VERSION_MINOR_LEN = 8`
- `FLAC__OGG_MAPPING_NUM_HEADERS_LEN = 16`

The byte-length macros live in the paired header.

## Risks / Edge Cases

The mapping constants must stay consistent with `private/ogg_mapping.h` and with the Ogg FLAC specification. Encoder/decoder aspect code relies on these values to build and strip the first header packet.

## Dependencies

Includes only `private/ogg_mapping.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/ogg_mapping.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/all.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/all.h

## Role

`private/all.h` is an umbrella include for libFLAC private headers. It aggregates internal declarations for bit I/O, CPU detection, CRC, predictors, floating/fixed-point support, metadata, memory, and encoder framing.

## Contents

It includes `bitmath.h`, `bitreader.h`, `bitwriter.h`, `cpu.h`, `crc.h`, `fixed.h`, `float.h`, `format.h`, `lpc.h`, `md5.h`, `memory.h`, `metadata.h`, and `stream_encoder_framing.h`.

## Risks / Edge Cases

As an umbrella header, it increases compile-time coupling. Any header added here becomes broadly visible to private implementation files that include `private/all.h`.

## Dependencies

Depends on all listed private headers and their transitive public FLAC/share headers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/all.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/bitmath.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/bitmath.h

## Role

`private/bitmath.h` provides inline bit-counting utilities used throughout codec parsing and coding-cost logic. It covers count-leading-zero operations, integer log2, wide log2, and declares signed integer log2.

## Major Functions

- `FLAC__clz_soft_uint32()` uses a 256-entry table to count leading zeroes in a 32-bit word.
- `FLAC__clz_uint32()` and `FLAC__clz_uint64()` select compiler intrinsics or software fallbacks.
- `FLAC__clz2_uint32()` and `FLAC__clz2_uint64()` are zero-safe wrappers.
- `FLAC__bitmath_ilog2()` computes floor log2 for 32-bit values.
- `FLAC__bitmath_ilog2_wide()` computes floor log2 for 64-bit values, using intrinsics or a de Bruijn fallback.
- `FLAC__bitmath_silog2()` is declared for signed magnitude bit-width calculations.

## Important Implementation Details

The non-`clz2` helpers assert that input is nonzero. GCC/Clang builtins are used when available; MSVC and Intel paths use bit-scan intrinsics. The de Bruijn fallback normalizes the 64-bit value to the next power form and indexes a static table.

## Risks / Edge Cases

- Calling `FLAC__clz_uint32()`, `FLAC__clz_uint64()`, or log2 helpers with zero violates asserted preconditions.
- Compiler feature paths must match the platform's builtin semantics; builtins for zero input are intentionally avoided.
- `FLAC__bitmath_ilog2_wide()` relies on correct `FLAC__U64L()` macro definition from `share/compat.h`.

## Dependencies

Uses `FLAC/ordinals.h`, `FLAC/assert.h`, `share/compat.h`, and optional MSVC intrinsics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/bitmath.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/bitreader.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/bitreader.h

## Role

`private/bitreader.h` declares libFLAC's opaque buffered bit reader API. It is used by decoders to read FLAC bitstream fields, residual coding, byte-aligned metadata, frame numbers, and CRC-protected data.

## API Surface

The header declares lifecycle functions (`new`, `delete`, `init`, `free`, `clear`, `dump`), framesync bookmarking/rewind, CRC reset/get, alignment and limit introspection, and raw read operations.

Read operations include unsigned/signed 32-bit and 64-bit fields, little-endian 32-bit metadata values, skipped bits/bytes without CRC, byte-block reads, unary values, Rice-signed scalar/block values, and UTF-8-style uint32/uint64 reads.

## Important Contracts

`FLAC__BitReader` is opaque. Data arrives through `FLAC__BitReaderReadCallback`, which fills a byte buffer and updates a byte count. Several APIs explicitly do not update CRC when skipping or reading byte blocks, and callers must choose them only where appropriate.

## Risks / Edge Cases

- CRC APIs assume callers understand byte alignment and the implementation's read cursor behavior.
- Read limits can invalidate future reads if exceeded.
- UTF-8 frame-number decoders expose invalid encodings through output sentinel behavior in the implementation rather than only via return status.

## Dependencies

Includes `FLAC/ordinals.h` and `private/cpu.h`; implementation depends on bitmath, CRC, endian, and buffer management internals.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/bitreader.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/bitwriter.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/bitwriter.h

## Role

`private/bitwriter.h` declares libFLAC's opaque buffered bit writer API. Encoders use it to serialize metadata, frame headers, subframes, residuals, UTF-8-style numbers, and CRC-covered frame data.

## API Surface

The header declares lifecycle functions, CRC generation for CRC16 and CRC8, byte-alignment and unconsumed-bit introspection, direct buffer access with get/release, and bit-level write functions.

Write functions cover zero padding, raw signed/unsigned 32-bit and 64-bit values, little-endian 32-bit values, byte blocks, unary values, Rice bit estimation, Rice-signed scalar/block encoding, UTF-8-style uint32/uint64 encoding, and zero-padding to a byte boundary.

## Important Contracts

`FLAC__BitWriter` is opaque. Direct buffer access requires byte alignment, and no intervening bitwriter calls are allowed between `get_buffer()` and `release_buffer()`. CRC functions are non-const because they may materialize the buffer.

## Risks / Edge Cases

- The caller must respect buffer ownership; the returned direct buffer remains owned by the bitwriter.
- Bit-width arguments must match FLAC field constraints; enforcement is mostly in implementation and assertions.
- Rice/Golomb unused declarations are left disabled with `#if 0`.

## Dependencies

Includes `FLAC/ordinals.h` and standard `stdio.h` for dump output.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/bitwriter.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/cpu.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/cpu.h

## Role

`private/cpu.h` defines CPU architecture detection macros, compiler intrinsic support macros, target attributes, and the `FLAC__CPUInfo` structures used to select optimized codec routines.

## Major Contents

- Detects x86_64 and IA32 from compiler predefined macros.
- Defines `FLAC__SSE_TARGET()` and `FLAC__FAST_MATH_TARGET()` for compilers with target attributes.
- Sets support macros for SSE, SSE2, SSSE3, SSE4.1, AVX, AVX2, and FMA depending on compiler and `FLAC__USE_AVX`.
- Defines CPU info enums and structures for x86 and PowerPC capabilities.
- Declares `FLAC__cpu_info()` plus IA32 CPUID assembly helpers.

## Important Implementation Details

The header separates compile-time support for intrinsics from runtime CPU feature detection. Runtime selection uses `FLAC__CPUInfo`, while the compile-time macros decide which optimized functions can be compiled and declared elsewhere.

## Risks / Edge Cases

- Feature availability depends on build-system macros such as `FLAC__HAS_X86INTRIN`, `FLAC__USE_AVX`, and compiler version.
- MSVC, GCC, Clang, and Intel compiler branches differ in target attribute support.
- On non-x86 builds most SIMD macros remain undefined or zero and generic C paths are expected.

## Dependencies

Includes `FLAC/ordinals.h` and optionally `config.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/cpu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/crc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/crc.h

## Role

`private/crc.h` declares CRC helpers for FLAC frame/header integrity checks.

## API Surface

- `FLAC__crc8()` computes the FLAC 8-bit CRC using polynomial `x^8 + x^2 + x + 1`.
- `FLAC__crc16_table[8][256]` is the exported lookup table for CRC16.
- `FLAC__CRC16_UPDATE(data, crc)` updates a CRC16 one byte at a time.
- `FLAC__crc16()` computes CRC16 over byte data.
- `FLAC__crc16_update_words32()` and `FLAC__crc16_update_words64()` update CRC16 over word buffers.

## Important Implementation Details

CRC16 uses polynomial `x^16 + x^15 + x^2 + 1`, MSB-shifted first, initial value zero. The macro masks to 16 bits after shifting.

## Risks / Edge Cases

Callers must feed bytes in stream order. Word-update helpers depend on the implementation's interpretation of word buffers and are intended for bitreader/bitwriter hot paths.

## Dependencies

Includes `FLAC/ordinals.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/crc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/fixed.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/fixed.h

## Role

`private/fixed.h` declares fixed-predictor analysis, residual generation, and signal restoration routines for FLAC fixed subframes.

## API Surface

The best-predictor functions estimate residual bits per sample for orders 0 through `FLAC__MAX_FIXED_ORDER`, with normal, wide, limit-residual, and 33-bit variants. Non-integer-only builds return floating estimates; integer-only builds use `FLAC__fixedpoint`.

Residual functions compute fixed-predictor residuals from original samples. Restore functions reconstruct samples from residuals and historical samples. Optional SSE2, SSSE3, and NASM IA32 declarations expose optimized predictor selection variants.

## Important Contracts

Residual computation takes `data[-order, data_len-1]`; restoration requires `data[-order,-1]` historical samples already available before the output pointer. This negative-index convention is central to FLAC fixed predictor code.

## Risks / Edge Cases

- Callers must pass sufficient warm-up/history samples before the data pointer.
- Wide and 33-bit variants are required when sample depth plus blocksize can overflow narrower accumulators.
- Assembly/intrinsic declarations are conditional on CPU/build macros and must match compiled implementation availability.

## Dependencies

Includes `private/cpu.h`, `private/float.h`, and `FLAC/format.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/fixed.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/float.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/float.h

## Role

`private/float.h` centralizes libFLAC's floating-point or fixed-point analysis type definitions.

## Contents

For normal builds, `FLAC__real` is typedefed to `float`. Comments warn that changing it affects many function signatures and assembly-equivalent routines.

For `FLAC__INTEGER_ONLY_LIBRARY`, it defines `FLAC__fixedpoint` as `FLAC__int32`, declares fixed-point constants, provides truncation/multiply/divide macros using 16 fractional bits, and declares `FLAC__fixedpoint_log2()`.

## Important Implementation Details

The fixed-point convention uses upper 16 bits as integer part and lower 16 bits as fractional part. `FLAC__fixedpoint_log2()` takes an input fixed-point value, caller-specified fractional bits, and precision control.

## Risks / Edge Cases

- Floating and integer-only builds expose different signatures in predictor headers.
- Fixed-point division can divide by zero if callers do not validate inputs.
- Changing `FLAC__real` would break ABI/assembly assumptions.

## Dependencies

Includes `config.h` when available and `FLAC/ordinals.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/float.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/format.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/format.h

## Role

`private/format.h` declares internal helpers for FLAC format calculations and partitioned Rice coding contents management.

## API Surface

It declares functions to compute maximum Rice partition order from blocksize, predictor order, and optional limits. It also declares init, clear, and ensure-size helpers for `FLAC__EntropyCodingMethod_PartitionedRiceContents`.

## Risks / Edge Cases

The partition-order helpers encode FLAC format constraints that must stay consistent with encoder residual partitioning. Incorrect limits can produce invalid subframes or inefficient encoding.

## Dependencies

Includes public `FLAC/format.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/format.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/lpc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/lpc.h

## Role

`private/lpc.h` declares linear predictive coding support for FLAC encoding and decoding: windowing, autocorrelation, LPC coefficient calculation, quantization, residual generation, residual bit-depth estimation, restore, expected coding cost, and best-order selection.

## API Surface

Non-integer-only builds expose windowed-data routines for 32-bit and 64-bit samples, autocorrelation, LPC coefficient generation, coefficient quantization, residual computation, limit-residual checks, expected bits-per-residual-sample, and best-order choice.

All builds expose max prediction/residual bit-depth helpers and LPC restore functions. Numerous conditional declarations expose SSE2, SSE4.1, AVX2, FMA, Power VSX, ARM64 NEON, and IA32 assembly variants.

## Important Contracts

Residual computation uses `data[-order, data_len-1]`, and restore requires historical samples in `data[-order,-1]`. `order` must be greater than zero for LPC paths and no more than `FLAC__MAX_LPC_ORDER`.

Quantization returns status codes: success, shift too large for header representation, or all-zero coefficients. Comments document that negative shifts may occur conceptually even though FLAC decoder-side shift representation is constrained.

## Risks / Edge Cases

- Callers must pass valid history before the current data pointer.
- Assembly/intrinsic declarations are tightly coupled to build macros and CPU feature detection.
- Residual limit variants are important for rejecting values not representable as legal 32-bit FLAC residuals.
- Floating LPC analysis is excluded under integer-only builds, but restore/bit-depth helpers remain.

## Dependencies

Includes `private/cpu.h`, `private/float.h`, and `FLAC/format.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/lpc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/macros.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/macros.h

## Role

`private/macros.h` provides internal `flac_min` and `flac_max` macros with safer single-evaluation variants where compiler support exists.

## Implementation Details

For GCC 4.3 and newer, it uses statement expressions and `__typeof__` to evaluate each argument once. `flac_min` uses `__COUNTER__` and token pasting to avoid local-name collisions. Other branches use `MIN`/`MAX` from `sys/param.h`, MSVC `__min`/`__max`, or fallback ternary macros.

## Risks / Edge Cases

- GCC statement expressions are non-standard C; fallback macros may evaluate arguments multiple times.
- Header behavior depends on platform headers defining `MIN` and `MAX`.
- The fallback ternary macros are less safe for expressions with side effects.

## Dependencies

May include `sys/param.h` or `stdlib.h` depending on platform macros.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/macros.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/md5.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/md5.h

## Role

`private/md5.h` declares libFLAC's MD5 context and functions. FLAC uses MD5 to verify decoded audio stream integrity, not for cryptographic security.

## Contents

It defines `FLAC__multibyte`, a union of byte, int16, and int32 pointers for reusable sample formatting buffers. `FLAC__MD5Context` stores MD5 input block words, state words, byte counters, an internal conversion buffer, and buffer capacity.

It declares `FLAC__MD5Init()`, `FLAC__MD5Final()`, and `FLAC__MD5Accumulate()`.

## Important Contracts

`FLAC__MD5Accumulate()` consumes channel-separated sample arrays and formats them into the canonical byte stream before updating the digest.

## Risks / Edge Cases

The internal buffer is owned by the context and freed during finalization in the implementation. Contexts should be reinitialized before reuse after `Final()`.

## Dependencies

Includes `FLAC/ordinals.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/md5.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/memory.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/memory.h

## Role

`private/memory.h` declares libFLAC memory allocation helpers, especially aligned array allocation for SIMD-friendly buffers.

## API Surface

It declares generic `FLAC__memory_alloc_aligned()` plus typed aligned array allocators for signed/unsigned 32-bit and 64-bit integers, unsigned integers, and `FLAC__real` when floating-point analysis is enabled. It also declares `safe_malloc_mul_2op_p()`.

## Important Contracts

Aligned allocation returns both the original unaligned pointer and an aligned pointer. The original pointer must be used for `free()`. Typed array helpers replace caller-managed old buffers only after successful allocation in the implementation.

## Risks / Edge Cases

- Callers must keep unaligned and aligned pointer variables distinct.
- Zero-element allocation is not the intended typed-array contract in the implementation.
- `safe_malloc_mul_2op_p()` differs from raw `malloc()` by guarding multiplication overflow and avoiding zero-byte allocation.

## Dependencies

Includes `private/float.h` and `FLAC/ordinals.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/memory.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/metadata.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/metadata.h

## Role

`private/metadata.h` exposes internal metadata cleanup helpers that are not part of the normal public API.

## API Surface

It declares:

- `FLAC__metadata_object_delete_data()`
- `FLAC__metadata_object_cuesheet_track_delete_data()`

These free malloc-owned data inside metadata objects or cue sheet tracks without necessarily returning the object to the exact state created by public constructors.

## Risks / Edge Cases

The warning is important: after deleting embedded data, the containing object may be inconsistent for normal public use unless the caller reinitializes fields. This is a low-level cleanup primitive.

## Dependencies

Includes public `FLAC/metadata.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/metadata.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/ogg_decoder_aspect.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/ogg_decoder_aspect.h

## Role

`private/ogg_decoder_aspect.h` defines the Ogg decoder aspect state and status API used to add Ogg FLAC support around the native stream decoder.

## Data Structures

`FLAC__OggDecoderAspect` stores API-configurable serial behavior, libogg stream and sync state, parsed mapping version, serial-number discovery state, end-of-stream state, current working page, and current working packet. The packet pointer and byte count are intentionally mutable as packet data is consumed.

## API Surface

The header declares serial/default/init/finish/flush/reset functions and `FLAC__ogg_decoder_aspect_read_callback_wrapper()`.

`FLAC__OggDecoderAspectReadStatus` distinguishes OK, end-of-stream, lost sync, not-FLAC, unsupported mapping version, abort, generic error, and memory allocation error.

## Risks / Edge Cases

This stateful adapter is sensitive to correct reset behavior. If callers reuse a decoder with first-serial-number mode, `reset()` re-enables serial discovery.

## Dependencies

Includes libogg, `FLAC/ordinals.h`, and `FLAC/stream_decoder.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/ogg_decoder_aspect.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/ogg_encoder_aspect.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/ogg_encoder_aspect.h

## Role

`private/ogg_encoder_aspect.h` defines the Ogg encoder aspect state and callback wrapper used to package native FLAC encoder output into Ogg FLAC streams.

## Data Structures

`FLAC__OggEncoderAspect` stores serial number, metadata header count, libogg stream state, a reusable page, whether native `fLaC` magic has been seen, whether the next packet is first, and accumulated samples written.

## API Surface

It declares serial and metadata-count setters, defaults/init/finish functions, a write callback proxy type, and `FLAC__ogg_encoder_aspect_write_callback_wrapper()`.

## Risks / Edge Cases

`num_metadata` must fit in the Ogg FLAC 16-bit header count field. State fields assume a specific sequence of native FLAC encoder write callbacks.

## Dependencies

Includes libogg, `FLAC/ordinals.h`, and `FLAC/stream_encoder.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/ogg_encoder_aspect.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/ogg_helper.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/ogg_helper.h

## Role

`private/ogg_helper.h` declares helper functions for working with simple Ogg pages in seekable encoder paths.

## API Surface

It declares page lifecycle helpers `simple_ogg_page__init()` and `simple_ogg_page__clear()`, plus `simple_ogg_page__get_at()` and `simple_ogg_page__set_at()` for reading/writing an Ogg page at a stream position using encoder seek/read/write callbacks.

## Important Contracts

The caller supplies an `ogg_page` whose header/body fields are managed by these helpers. `get_at()` expects an initially empty page; `clear()` frees allocated header/body memory.

## Dependencies

Includes libogg and `FLAC/stream_encoder.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/ogg_helper.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/ogg_mapping.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/ogg_mapping.h

## Role

`private/ogg_mapping.h` declares constants and byte-length macros for the Ogg FLAC mapping header.

## Contents

It defines byte lengths for packet type, mapping magic, version major/minor, and number-of-header-packets fields. It declares bit-length constants, first header packet type, and mapping magic defined in `ogg_mapping.c`.

## Important Details

Encoder code uses these constants to construct the synthetic first Ogg FLAC packet. Decoder code uses the same constants to validate and strip the Ogg mapping prefix before handing native FLAC bytes to the decoder.

## Dependencies

Includes `FLAC/ordinals.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/ogg_mapping.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/stream_encoder.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/stream_encoder.h

## Role

`private/stream_encoder.h` declares internal encoder support constants and SIMD entry points for residual partition precomputation.

## Contents

It defines `FLAC__MAX_EXTRA_RESIDUAL_BPS` as `4`, used to avoid overflow in unusual signals when precomputing partition sums with 32-bit accumulators.

For x86/x86_64 builds with intrinsics, it declares SSE2, SSSE3, and AVX2 versions of `FLAC__precompute_partition_info_sums_*()`.

## Risks / Edge Cases

The optimized declarations are gated by CPU and build macros. Encoder dispatch must only call implementations that were compiled and are supported on the runtime CPU.

## Dependencies

Conditionally includes `private/cpu.h` and `FLAC/format.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/stream_encoder.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/stream_encoder_framing.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/stream_encoder_framing.h

## Role

`private/stream_encoder_framing.h` declares encoder serialization helpers that write FLAC metadata, frame headers, and subframes into a `FLAC__BitWriter`.

## API Surface

It declares:

- `FLAC__add_metadata_block()`
- `FLAC__frame_add_header()`
- `FLAC__subframe_add_constant()`
- `FLAC__subframe_add_fixed()`
- `FLAC__subframe_add_lpc()`
- `FLAC__subframe_add_verbatim()`

The subframe functions take subframe-specific data, sample counts or residual counts, bits per sample, wasted-bit count, and a bitwriter.

## Risks / Edge Cases

These helpers are format-critical. Caller-provided frame/subframe structures must already satisfy FLAC constraints, including valid residual sample counts and wasted-bit metadata.

## Dependencies

Includes `FLAC/format.h` and `private/bitwriter.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/stream_encoder_framing.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/window.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/window.h

## Role

`private/window.h` declares apodization window generation functions used by LPC analysis in non-integer-only FLAC encoder builds.

## API Surface

It declares Bartlett, Bartlett-Hann, Blackman, Blackman-Harris, Connes, flattop, Gauss, Hamming, Hann, Kaiser-Bessel, Nuttall, rectangle, triangle, Tukey, partial Tukey, punchout Tukey, and Welch window functions.

Each writes `window[0, L-1]` for a requested length `L`. Some take parameters such as Gaussian standard deviation or Tukey shape/start/end.

## Risks / Edge Cases

The entire API is disabled for `FLAC__INTEGER_ONLY_LIBRARY`. Parameter constraints such as `0.0 < stddev <= 0.5` for Gauss are documented here and must be enforced by callers or implementation.

## Dependencies

Includes `private/float.h` and `FLAC/format.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/window.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/protected/all.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/protected/all.h

## Role

`protected/all.h` is an umbrella include for protected stream decoder and encoder state headers.

## Contents

It includes `stream_decoder.h` and `stream_encoder.h`.

## Risks / Edge Cases

This header exposes protected internals to source files that need access to libFLAC object state beyond the public API. It increases coupling to internal structure layouts.

## Dependencies

Depends on the protected decoder and encoder headers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/protected/all.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/protected/stream_decoder.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/protected/stream_decoder.h

## Role

`protected/stream_decoder.h` defines the internal/protected state visible to libFLAC decoder implementation files and declares an input-buffer introspection helper.

## Data Structure

`FLAC__StreamDecoderProtected` stores decoder state, init status, channel count, channel assignment, bits per sample, sample rate, current blocksize, MD5 checking flag, and optional Ogg decoder aspect state when `FLAC__HAS_OGG` is enabled.

## API Surface

It declares `FLAC__stream_decoder_get_input_bytes_unconsumed()`, returning the number of input bytes still buffered but unconsumed.

## Risks / Edge Cases

This is not public ABI. Any layout change affects internal files that access `decoder->protected_`. Ogg support conditionally changes the structure layout.

## Dependencies

Includes `FLAC/stream_decoder.h` and conditionally `private/ogg_decoder_aspect.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/protected/stream_decoder.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/protected/stream_encoder.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/protected/stream_encoder.h

## Role

`protected/stream_encoder.h` defines the internal/protected encoder state used by libFLAC implementation files.

## Data Structures

When floating-point analysis is enabled, it defines `FLAC__ApodizationFunction` and `FLAC__ApodizationSpecification`, covering supported window families and their parameters.

`FLAC__StreamEncoderProtected` stores encoder state and configuration: verification, subset mode, MD5, stereo mode flags, channel/sample parameters, apodization specs, LPC/QLP settings, residual partition settings, Rice search distance, total sample estimate, min-bitrate flag, metadata pointers/count, stream offsets, and optional Ogg encoder aspect state.

## Risks / Edge Cases

- The structure is internal but widely used by implementation code via `encoder->protected_`.
- Ogg and integer-only build macros change layout.
- `metadata` is an array of metadata pointers; lifetime management must be coordinated with public encoder APIs.

## Dependencies

Includes `FLAC/stream_encoder.h`, optionally `private/ogg_encoder_aspect.h`, and `private/float.h` for apodization specs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/protected/stream_encoder.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/share/alloc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/share/alloc.h

## Role

`share/alloc.h` provides shared safe allocation helpers for libFLAC and related tools. It avoids zero-byte allocation ambiguity, checks arithmetic overflow for allocation sizes, and includes fuzzing hooks for allocation-failure testing.

## Major Helpers

- `safe_malloc_()` and `safe_calloc_()` convert zero-size requests to at least one byte.
- `safe_malloc_add_*()` check additive overflow.
- `safe_malloc_mul_2op_()` is declared externally; `safe_malloc_mul_3op_()`, `safe_malloc_mul2add_()`, and `safe_malloc_muladd2_()` check multiplication or combined multiplication/addition.
- `safe_realloc_()` wraps realloc and frees the old pointer on nonzero-size failure.
- `_nofree_` realloc variants preserve the old pointer on failure.
- Multiplication realloc helpers either free on overflow/failure or preserve depending on the `_nofree_` name.
- Fuzzing mode can force allocation failures through global counters.

## Important Implementation Details

The header defines `SIZE_MAX` if missing, with MSVC-specific fallbacks. It distinguishes POSIX `realloc(ptr, 0)` semantics in realloc helpers from libFLAC's safe malloc convention of never requesting zero bytes.

## Risks / Edge Cases

- `safe_realloc_()` and several non-`nofree` helpers free the old pointer on failure; callers must not assume old storage remains valid.
- Some zero-size paths intentionally call `malloc(1)`, while realloc zero-size paths preserve POSIX free-like behavior.
- Fuzzing hooks are compiled only under `FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION`.

## Dependencies

Includes `limits.h`, optional `stdint.h`, `stdlib.h`, and `share/compat.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/share/alloc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/share/compat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/share/compat.h

## Role

`share/compat.h` centralizes portability macros and wrappers needed to build FLAC across Unix, Windows, MSVC, MinGW, Android, and other C environments.

## Major Contents

- Defines `FLAC__off_t` and maps `fseeko`/`ftello` to 64-bit Windows equivalents where needed.
- Provides C99/inttypes compatibility for MSVC versions.
- Defines `flac_restrict`, `FLAC__U64L()`, and case-insensitive string comparison macros.
- Maps file and console functions to UTF-8 Windows wrappers on `_WIN32`, otherwise standard C/POSIX functions.
- Defines `flac_stat_s`, `flac_fstat`, math constants `M_LN2` and `M_PI` if absent.
- Declares `flac_snprintf()` and `flac_vsnprintf()` wrappers.

## Important Implementation Details

Windows paths use `share/win_utf8_io.h` to ensure `char *` filenames are treated as UTF-8. POSIX `flac_utime` maps to `utimensat()` when `_POSIX_C_SOURCE >= 200809L`, otherwise `utime()`.

There is a specific MSVC Windows XP toolset warning and workaround note around broken `_wstat64`/`_fstat64` behavior in some `/MT` builds.

## Risks / Edge Cases

- Feature behavior depends on build macros such as `HAVE_FSEEKO`, `_POSIX_C_SOURCE`, `_WIN32`, and compiler version.
- The `flac_utime` macro has different call expectations between `utimensat` and `utime` branches.
- Platform wrapper changes can affect metadata iterator file preservation and command-line tools.

## Dependencies

Includes standard headers conditionally and `share/win_utf8_io.h` on Windows.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/share/compat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/share/endswap.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/share/endswap.h

## Role

`share/endswap.h` defines endian byte-swap macros and host-to-little-endian conversions used by FLAC internals.

## Contents

It selects `ENDSWAP_16`, `ENDSWAP_32`, and `ENDSWAP_64` from compiler builtins, MSVC `_byteswap_*`, Linux `<byteswap.h>`, or portable bit-shift fallbacks. It also defines `H2LE_16` and `H2LE_32` for MD5 sample formatting, swapping only on big-endian CPUs.

## Risks / Edge Cases

- `CPU_IS_BIG_ENDIAN` must be defined accurately by configuration for `H2LE_*`.
- The portable `ENDSWAP_64` macro composes 32-bit swaps and assumes unsigned-style shift behavior on supplied values.
- This header assumes `config.h` has already supplied feature macros.

## Dependencies

May use compiler builtins, `<stdlib.h>`, or `<byteswap.h>` depending on platform macros.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/share/endswap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/share/macros.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/share/macros.h

## Role

`share/macros.h` defines `FLAC_CHECK_RETURN()`, a shared diagnostic macro for checking unlikely system-call failures.

## Contents

The macro evaluates an expression, and if the result is negative, prints the expression text and `strerror(errno)` to `stderr`.

## Important Notes

The file comments acknowledge that libraries ideally should not print directly, but this macro is intended for operations that are extremely unlikely to fail, such as restoring a saved owner/group.

## Risks / Edge Cases

- The macro uses `fprintf()`, `strerror()`, and `errno` but the header only includes `<errno.h>`; callers must have declarations for stdio/string functions in scope.
- It evaluates the expression once.
- Direct stderr output from library code can surprise embedders.

## Dependencies

Includes `<errno.h>` and relies on surrounding includes for `fprintf`, `stderr`, and `strerror`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/share/macros.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/share/private.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/share/private.h

## Role

`share/private.h` declares unpublished debug/control routines from libFLAC. It is intended only for code shipped with FLAC, not external clients.

## API Surface

It declares APIs to disable instruction-set dispatch, constant subframes, fixed subframes, and verbatim subframes on a stream encoder. It also declares setters/getters for the encoder's MD5 behavior.

## Risks / Edge Cases

Although marked `FLAC_API`, these are explicitly unpublished private routines. External consumers using them would couple to unstable internals.

## Dependencies

The header assumes `FLAC_API`, `FLAC__bool`, and `FLAC__StreamEncoder` are already declared by included public FLAC headers in the translation unit.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/share/private.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/share/safe_str.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/share/safe_str.h

## Role

`share/safe_str.h` provides small bounded string helpers that guarantee NUL termination for copy and concatenation operations.

## API Surface

- `safe_strncat(dest, src, dest_size)` appends with `strncat()` using the available destination size and then forces the final byte to NUL.
- `safe_strncpy(dest, src, dest_size)` copies up to `dest_size - 1` bytes and forces the final byte to NUL.

## Important Implementation Details

Both functions no-op for `dest_size < 1` and return `dest`. The comments state that truncation is allowed when the destination is too short.

## Risks / Edge Cases

- `safe_strncat()` calls `strlen(dest)` and assumes `dest` is already NUL-terminated within `dest_size`.
- The header uses `strncat`, `strlen`, and `strncpy` but does not include `<string.h>` itself, so callers must include it first.
- These helpers do not report truncation.

## Dependencies

Relies on C string library declarations supplied by including translation units.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/share/safe_str.h -->