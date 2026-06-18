# Group Research: group_152_9front_sources_os_plan9_9front_sys_src_cmd_gs_zlib_gzio_c_sources_os_90e1205909cc

Scope verified against `Docs/research_subset_a.md`: this group is within `sources/os/plan9/9front`. Files are vendored zlib/Ghostscript compression sources, mostly compression/decompression infrastructure rather than filesystem logic.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/gzio.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/gzio.c

## Purpose
Implements zlib’s `gz*` stdio-style API for reading and writing gzip streams.

## Key Elements
Defines internal `gz_stream` state and implements `gzopen`, `gzdopen`, `gzread`, `gzwrite`, `gzprintf`, `gzseek`, `gzrewind`, `gztell`, `gzeof`, `gzclose`, `gzerror`, and `gzclearerr`. It parses gzip headers, writes simple gzip headers, maintains CRC32, handles trailers, and supports transparent reads for non-gzip inputs.

## Behavior/Risks
Reading uses raw inflate with `-MAX_WBITS` after manually consuming the gzip header. Concatenated gzip members are detected by checking the next header after trailer validation. Seeking in compressed input is emulated by rewinding/skipping uncompressed bytes and can be very slow. Write-mode seeking fills gaps by writing zero bytes. `gzprintf` is bounded by `Z_PRINTF_BUFSIZE`; old non-ANSI paths depend on `sprintf`/`snprintf` availability macros. Header parsing sets `transparent` when gzip magic is absent.

## Dependencies
Includes `zutil.h`, uses zlib inflate/deflate, `crc32`, stdio file I/O, allocation through local `malloc` wrappers, and portability macros from zlib configuration headers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/gzio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/infback.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/infback.c

## Purpose
Provides zlib’s callback-based raw deflate inflater: `inflateBackInit_`, `inflateBack`, and `inflateBackEnd`.

## Key Elements
`inflateBackInit_` validates version/stream size/window parameters and stores a caller-provided sliding window. `inflateBack` drives a block-level inflate state machine over callback input/output functions. It handles stored, fixed-Huffman, and dynamic-Huffman blocks, builds decode tables with `inflate_table`, and delegates fast decode to `inflate_fast` when enough input/output space exists. `inflateBackEnd` frees state.

## Behavior/Risks
This API does not parse zlib or gzip wrappers; callers are responsible for wrapping/checking if needed. Input callback failure and output callback failure both surface as `Z_BUF_ERROR`, with `strm->next_in == Z_NULL` helping distinguish input failure. Dynamic-table and distance validation errors set messages such as invalid block type, invalid bit length repeat, invalid distance code, or distance too far back. The fixed-table builder can be runtime-generated under `BUILDFIXED`, noted as not thread-safe.

## Dependencies
Includes `zutil.h`, `inftrees.h`, `inflate.h`, and `inffast.h`. Shares `struct inflate_state` and Huffman decode tables with the normal streaming inflater.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/infback.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/inffast.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/inffast.c

## Purpose
Implements the optimized inner loop for inflate literal/length/distance decoding.

## Key Elements
Exports `inflate_fast(z_streamp strm, unsigned start)` unless `ASMINF` supplies an assembler implementation. It caches stream pointers, bit buffer, window state, and decode tables in locals, then decodes literals and match copies until input/output space is no longer sufficient, an end-of-block is reached, or an error occurs.

## Behavior/Risks
Entry assumes `state->mode == LEN`, at least six bytes of input, at least 258 bytes output space, and `state->bits < 8`. It handles two-level Huffman decode table entries, copies matches either from current output or the sliding window, and reports invalid distance/literal codes through `state->mode = BAD` and `strm->msg`. Correctness relies on callers enforcing the buffer-size assumptions.

## Dependencies
Includes `zutil.h`, `inftrees.h`, `inflate.h`, and `inffast.h`. Used by both `inflate.c` and `infback.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/inffast.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/inffast.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/inffast.h

## Purpose
Declares the internal fast inflate decoder.

## Key Elements
Contains a single prototype: `void inflate_fast OF((z_streamp strm, unsigned start));`.

## Behavior/Risks
Explicitly warns applications not to include it directly. This is an internal ABI between inflate implementation files and can change with zlib internals.

## Dependencies
Requires `z_streamp` and `OF` macro definitions from the surrounding zlib headers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/inffast.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/inffixed.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/inffixed.h

## Purpose
Provides generated fixed Huffman decode tables for inflate.

## Key Elements
Defines static `lenfix[512]` and `distfix[32]` arrays of `code` entries. These encode the fixed literal/length and distance tables required by deflate fixed-code blocks.

## Behavior/Risks
Generated by `makefixed()` from `inflate.c`. Including this header avoids runtime table construction. It is implementation-private and depends on the exact `code` structure layout.

## Dependencies
Requires `code` from `inftrees.h`. Included inside `fixedtables()` in `inflate.c` and `infback.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/inffixed.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/inflate.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/inflate.c

## Purpose
Implements zlib decompression for zlib-wrapped, raw deflate, and optionally gzip-wrapped streams.

## Key Elements
Exports `inflateReset`, `inflateInit2_`, `inflateInit_`, `inflate`, `inflateEnd`, `inflateSetDictionary`, `inflateSync`, `inflateSyncPoint`, and `inflateCopy`. The main `inflate()` routine is a resumable state machine covering wrapper headers, optional dictionaries, stored blocks, fixed blocks, dynamic Huffman blocks, trailer checks, and sync recovery.

## Behavior/Risks
`windowBits` controls raw/zlib/gzip behavior. The sliding window is lazily allocated through `updatewindow()`. `inflate()` updates Adler-32 for zlib streams and CRC32 for gzip streams, validates gzip length trailers, and uses `inflate_fast()` when buffers are large enough. `flush` mostly influences return status; decompression still tries to consume/produce as much as possible. Error states are sticky until reset. `inflateCopy` deep-copies state and adjusts internal table pointers into the copied `codes` array.

## Dependencies
Includes `zutil.h`, `inftrees.h`, `inflate.h`, and `inffast.h`; optionally includes `inffixed.h`. Depends on checksum routines, zlib memory allocation hooks, and Huffman table generation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/inflate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/inflate.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/inflate.h

## Purpose
Defines internal inflate state and mode enumeration.

## Key Elements
Defines `GUNZIP` unless `NO_GZIP` is set, the `inflate_mode` enum, and `struct inflate_state`. State includes wrapper flags, check values, total output, sliding-window metadata, bit accumulator, copy length/distance fields, dynamic-code counters, temporary length arrays, work arrays, and `codes[ENOUGH]`.

## Behavior/Risks
This is not public API. The mode enum encodes resumable inflate progress across calls, including gzip header sub-states, dictionary wait, block decode states, trailer checks, and error/sync states. The structure is shared by normal and callback-based inflate, so layout coupling is strong.

## Dependencies
Requires `code` and `ENOUGH` from `inftrees.h`, plus zlib integer and pointer types from included configuration headers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/inflate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/inftrees.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/inftrees.c

## Purpose
Builds canonical Huffman decode tables for inflate.

## Key Elements
Exports `inflate_table(codetype type, unsigned short *lens, unsigned codes, code **table, unsigned *bits, unsigned short *work)`. It counts code lengths, validates over-subscribed/incomplete trees, sorts symbols by length, and fills root/sub-table decode entries. It contains base/extra tables for length and distance symbols.

## Behavior/Risks
Returns `0` on success, `-1` for invalid code lengths, and `+1` when the provided table space is insufficient. It assumes caller-provided lengths are in `0..MAXBITS`; that is not checked internally. For no-symbol cases it creates invalid-code table entries and lets decoding report the error. `ENOUGH` is considered conservatively safe but not exhaustively proven in comments.

## Dependencies
Includes `zutil.h` and `inftrees.h`. Used by `inflate.c` and `infback.c` for fixed and dynamic block table construction.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/inftrees.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/inftrees.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/inftrees.h

## Purpose
Defines internal Huffman decode table types for inflate.

## Key Elements
Defines `code` with `op`, `bits`, and `val` fields; `ENOUGH` and `MAXD`; `codetype` values `CODES`, `LENS`, and `DISTS`; and the `inflate_table` prototype.

## Behavior/Risks
The `op` encoding distinguishes literals, sub-table links, length/distance extra bits, end-of-block, and invalid-code entries. The header is private to zlib internals and tightly coupled to table generation and fast decode logic.

## Dependencies
Depends on zlib portability macros such as `FAR` and `OF`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/inftrees.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/minigzip.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/minigzip.c

## Purpose
Example utility that simulates a small subset of gzip using zlib’s `gz*` API.

## Key Elements
Implements `gz_compress`, optional `gz_compress_mmap`, `gz_uncompress`, `file_compress`, `file_uncompress`, and `main`. Supports `-d`, compression strategies `-f`, `-h`, `-r`, and levels `-1` through `-9`.

## Behavior/Risks
Intended for testing, not as a full gzip replacement. File mode compresses to `<file>.gz` and unlinks the original after success; decompress mode removes the input gzip file. Uses fixed `MAX_NAME_LEN` buffers with `strcpy`/`strcat`, so very long names are unsafe. Pipe mode wraps stdin/stdout using `gzdopen`. Error handling is intentionally limited and exits the process on failure.

## Dependencies
Includes `zlib.h`, stdio, optional mmap/stat headers, and platform-specific binary-mode/unlink handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/minigzip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/trees.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/trees.c

## Purpose
Implements deflate-side Huffman tree construction and compressed block emission.

## Key Elements
Initializes static trees and length/distance lookup tables, builds dynamic literal/distance/bit-length trees, selects stored/static/dynamic block encoding, emits Huffman-coded block data, tallies literals and matches, and manages the bit output buffer. Key exported internals are `_tr_init`, `_tr_stored_block`, `_tr_align`, `_tr_flush_block`, and `_tr_tally`.

## Behavior/Risks
`_tr_flush_block` compares stored, static, and dynamic costs and emits the cheapest unless forced by compile-time macros. Dynamic tree generation uses heap construction, bit-length limiting, canonical code generation, and run-length encoding of code lengths. Stored blocks are byte-aligned and include length/complement headers. `_tr_tally` flushes when the literal buffer is full. Correctness depends on `deflate_state` buffer layout and pending-buffer capacity assertions.

## Dependencies
Includes `deflate.h` and, for ANSI builds, generated `trees.h`. Uses constants/macros from deflate internals such as `L_CODES`, `D_CODES`, `BL_CODES`, `MAX_BITS`, `put_byte`, and `d_code`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/trees.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/trees.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/trees.h

## Purpose
Generated static data for deflate Huffman coding.

## Key Elements
Defines static literal tree `static_ltree`, static distance tree `static_dtree`, `_dist_code`, `_length_code`, `base_length`, and `base_dist`.

## Behavior/Risks
Generated by building `trees.c` with `GEN_TREES_H`. It avoids runtime generation for standard ANSI builds. The data is private to `trees.c` and depends on `ct_data`, deflate constants, and the exact deflate coding tables.

## Dependencies
Included by `trees.c`; requires deflate internal types and constants from `deflate.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/trees.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/uncompr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/uncompr.c

## Purpose
Implements the one-shot `uncompress()` memory-buffer decompression helper.

## Key Elements
Initializes a `z_stream`, points it at caller-provided source and destination buffers, calls `inflateInit`, runs `inflate(..., Z_FINISH)`, stores `stream.total_out` into `*destLen`, and ends the stream.

## Behavior/Risks
Rejects source or destination lengths that cannot fit into `uInt`, which matters on 16-bit targets. If inflate does not reach `Z_STREAM_END`, `Z_NEED_DICT` and a no-input `Z_BUF_ERROR` are normalized to `Z_DATA_ERROR`. Caller must provide a destination buffer large enough for the full uncompressed data.

## Dependencies
Defines `ZLIB_INTERNAL`, includes `zlib.h`, and depends on `inflateInit`, `inflate`, and `inflateEnd`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/uncompr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/zconf.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/zconf.h

## Purpose
Installed zlib configuration header for portability, symbol naming, calling conventions, and core zlib types.

## Key Elements
Defines optional `Z_PREFIX` symbol remapping, platform detection macros, `MAX_MEM_LEVEL`, `MAX_WBITS`, function prototype macro `OF`, calling/export macros `ZEXTERN`, `ZEXPORT`, `ZEXPORTVA`, `FAR`, core typedefs (`Byte`, `uInt`, `uLong`, `Bytef`, `voidpf`, etc.), `z_off_t`, and special mappings for Windows, BeOS, OS/400, and MVS.

## Behavior/Risks
This header is foundational: changing macros can alter public ABI, memory requirements, exported symbol names, and wrapper behavior. `HAVE_UNISTD_H` is represented by a configure-updated `#if 0` block in this copy, so `z_off_t` defaults to `long`. It is identical to `zconf.in.h` except for the source-control identification line.

## Dependencies
Included by `zlib.h` and other zlib headers. Supplies portability definitions used throughout this zlib subtree.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/zconf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/zconf.in.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/zconf.in.h

## Purpose
Template version of zlib’s configuration header, intended for configure-time generation of `zconf.h`.

## Key Elements
Contains the same portability content as `zconf.h`: symbol prefixing, platform detection, memory/window constants, prototype/calling-convention macros, core typedefs, seek/off_t handling, and platform-specific workarounds.

## Behavior/Risks
The only observed difference from `zconf.h` is the identification comment naming `zconf.in.h`. The `HAVE_UNISTD_H` block is still disabled by `#if 0`, marked as updated by `./configure`. As a template, edits here may affect regenerated `zconf.h`.

## Dependencies
Consumed by the zlib configure/build process and mirrors definitions required by `zlib.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/zconf.in.h -->