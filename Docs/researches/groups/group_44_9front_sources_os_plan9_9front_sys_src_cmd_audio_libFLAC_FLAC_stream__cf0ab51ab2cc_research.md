# Group Research: group_44_9front_sources_os_plan9_9front_sys_src_cmd_audio_libFLAC_FLAC_stream__cf0ab51ab2cc

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/9front`.

This grouped report covers a Plan 9/9front copy of libFLAC encoder support files: the public stream encoder API header plus internal bit I/O, CPU feature detection, CRC, fixed predictor, fixed-point logarithm, and format validation helpers. Each file below was read completely and is wrapped in the exact marker block expected by the finalizer.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/stream_encoder.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/stream_encoder.h

## Purpose

This header is the public libFLAC stream encoder interface. It defines the opaque `FLAC__StreamEncoder` type, encoder state and initialization status enums, callback status enums, callback function pointer types, constructor/destructor prototypes, configuration setters/getters, initialization entry points, finishing, and sample submission functions.

## Public API Surface

It exposes encoder lifecycle functions, native/Ogg/file initialization variants, configuration setters for stream parameters and compression behavior, state/query getters, and process calls for channel-separated or interleaved signed samples.

## Important Contracts

Setters are only valid while uninitialized. Metadata blocks supplied by callers must outlive `FLAC__stream_encoder_finish()`. Seek/tell support lets the encoder rewrite STREAMINFO and seektable data after encoding.

## Risks and Notes

The API permits many invalid setting combinations until init-time validation. Callback implementations must avoid reentrant state-changing encoder calls and must report accurate seek/tell behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/stream_encoder.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/bitmath.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/bitmath.c

## Purpose

Implements `FLAC__bitmath_silog2()`, a signed integer bit-width/log helper.

## Behavior

It returns `0` for zero, `2` for `-1`, and otherwise transforms negatives with `-(v + 1)` before calling `FLAC__bitmath_ilog2_wide(v) + 2`.

## Risks and Notes

The `-(v + 1)` form avoids overflow on the minimum signed value and preserves FLAC’s signed coding width semantics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/bitmath.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/bitreader.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/bitreader.c

## Purpose

Implements libFLAC’s internal buffered bit reader for parsing FLAC bitstreams from a callback source.

## Core Data Structures

`FLAC__BitReader` stores a word buffer, complete/incomplete word counts, consumed word/bit cursor, CRC16 bookkeeping, read limits, remembered framesync location, callback, and client data. Word size is 32 or 64 bits depending on `ENABLE_64_BIT_WORDS`.

## Main Operations

The reader refills via `bitreader_read_from_client_()`, compacting unconsumed data and byte-swapping partial tail words on little-endian hosts. It reads raw uint/int values, little-endian metadata integers, byte-aligned blocks, unary codes, Rice signed residual blocks, and UTF-8-style frame/sample numbers.

## CRC and Limits

CRC16 tracking is tied to consumed byte-aligned positions. Read limits are decremented by raw and block reads and invalidated when exceeded.

## Risks and Notes

High-risk areas are partial-word endian handling, CRC cursor alignment, and the optimized Rice decoder’s local cursor state. Several paths require word sizes of at least 32 bits.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/bitreader.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/bitwriter.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/bitwriter.c

## Purpose

Implements libFLAC’s internal buffered bit writer for encoder metadata and frame output.

## Core Data Structures

`FLAC__BitWriter` stores a growable word buffer, an accumulator for partial words, completed word count, and used accumulator bit count.

## Main Operations

It grows buffers in 4 KiB increments, writes zeroes, raw signed/unsigned 32/64-bit values, little-endian metadata integers, byte blocks, unary values, Rice-coded signed residuals, UTF-8-style frame/sample numbers, and byte-boundary padding.

## CRC Support

`FLAC__bitwriter_get_write_crc8()` and `_crc16()` serialize byte-aligned output and compute CRCs through `private/crc.h`.

## Risks and Notes

Correctness depends on accumulator invariants, byte alignment before buffer extraction, and swapping completed words exactly once.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/bitwriter.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/cpu.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/cpu.c

## Purpose

Populates `FLAC__CPUInfo` with runtime CPU feature data for selecting optimized code paths.

## Behavior

On x86, it detects CPUID support, vendor, CMOV/MMX/SSE family features, AVX/FMA/AVX2, and verifies OS AVX support with XGETBV. On PowerPC, it checks Linux/FreeBSD auxiliary vectors for ISA levels 2.07 and 3.00.

## Public Entry Point

`FLAC__cpu_info()` zeroes the info struct, sets compile-time CPU type, and dispatches to x86, PowerPC, or conservative no-assembly behavior.

## Risks and Notes

AVX is cleared unless both CPU and OS support are present. On 9front, platform-specific detection may compile out, yielding `use_asm = false`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/cpu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/crc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/crc.c

## Purpose

Provides FLAC CRC-8 and CRC-16 primitives.

## Contents

Defines `FLAC__crc8_table[256]` for frame headers and `FLAC__crc16_table[8][256]` for sliced CRC-16 frame data checks.

## Functions

`FLAC__crc8()` processes bytes one at a time. `FLAC__crc16()` processes eight-byte chunks plus tail bytes. `FLAC__crc16_update_words32()` and `_words64()` update CRCs from big-endian logical word buffers.

## Risks and Notes

Word update functions assume caller buffers are already in the logical byte order used by bitreader/bitwriter.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/crc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/fixed.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/fixed.c

## Purpose

Implements FLAC fixed predictor helpers for orders 0 through 4.

## Predictor Selection

Computes absolute residual totals for fixed predictor orders, chooses the lowest-error order with lower-order tie preference, and estimates residual bits per sample. Wide variants use 64-bit totals; limit variants reject orders whose residual magnitudes exceed signed 32-bit limits.

## Residual and Restore Operations

Provides residual computation and signal restoration for normal int32, wide intermediate, and 33-bit int64 paths.

## Integration Points

Used by encoder analysis for fixed subframes and decoder restoration for fixed-predictor subframes. Integer-only builds use fixed-point log helpers from `float.c`.

## Risks and Notes

Callers must provide warm-up samples before the data pointer for orders greater than zero. The file includes explicit Plan 9 `kencc` register-pressure workarounds in 33-bit order-4 paths.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/fixed.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/float.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/float.c

## Purpose

Provides fixed-point constants and fixed-point `log2` support for `FLAC__INTEGER_ONLY_LIBRARY` builds.

## Main Function

`FLAC__fixedpoint_log2()` computes a base-2 logarithm using Knuth’s algorithm and lookup tables for fractional precisions divisible by four.

## Integration Points

Used by `fixed.c` when estimating residual bits per sample without floating point.

## Risks and Notes

Callers must pass supported `fracbits` values. Non-integer-only builds compile out the active implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/float.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/format.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/format.c

## Purpose

Defines FLAC format constants, string tables, validation helpers, seektable utilities, Rice partition helpers, and partitioned Rice contents allocation helpers.

## Constants and Strings

Exports version/vendor strings, stream sync values, metadata/frame/subframe field lengths, seekpoint placeholder, entropy constants, and user-facing type string arrays.

## Validation

Checks sample rates, subset block sizes, seektable monotonicity, Vorbis comment names/values/entries, cue sheets including optional CD-DA constraints, and picture MIME/description fields. UTF-8 validation rejects invalid, overlong, surrogate, and selected noncharacter encodings.

## Helpers

Sorts and uniquifies seektables, computes maximum Rice partition orders from block size and predictor order, and manages `FLAC__EntropyCodingMethod_PartitionedRiceContents` arrays.

## Risks and Notes

`ensure_size()` can leave partially updated allocation state if the second realloc fails. UTF-8 validation relies on callers providing enough accessible bytes for the inspected metadata buffer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/format.c -->