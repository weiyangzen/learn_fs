# Group Research: Plan 9 Ghostscript zlib gzip/inflate/deflate internals

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/plan9` is included. These files are vendored zlib sources under Plan 9 Ghostscript, not Plan 9 filesystem code directly; their filesystem relevance is through gzip/zlib stream handling over `FILE *` and file descriptors used by tools.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/gzio.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/gzio.c

## Purpose
Implements zlib’s `gz*` file API for reading and writing gzip streams through stdio. It wraps raw deflate/inflate streams with gzip header/trailer handling, CRC maintenance, transparent passthrough for non-gzip input, and limited uncompressed-position seeking.

## Main API Surface
Exports:
- `gzopen(path, mode)` and `gzdopen(fd, mode)` for path/file-descriptor backed gzip streams.
- `gzread`, `gzgetc`, `gzungetc`, `gzgets` for reads.
- `gzwrite`, `gzprintf`, `gzputc`, `gzputs`, `gzflush` for writes when compression is enabled.
- `gzseek`, `gzrewind`, `gztell`, `gzeof`, `gzclose`, `gzerror`, `gzclearerr`.
- Internal helpers include `gz_open`, `get_byte`, `check_header`, `destroy`, `putLong`, `getLong`, and `do_flush`.

## Internal State
`gz_stream` owns:
- Embedded `z_stream`.
- Input/output buffers sized by `Z_BUFSIZE`.
- `FILE *file`, path/debug string, mode, transparent flag, gzip CRC, byte counters, and one-byte pushback state.
- `start`, `in`, and `out` offsets for compressed-data start and logical byte positions.

## Behavior
Read mode initializes raw inflate via `inflateInit2(..., -MAX_WBITS)` and then parses gzip headers manually. If the magic header is absent, the stream becomes transparent and `gzread` copies bytes without decompression. For gzip members, `gzread` verifies CRC32 and consumes the stored original length, then detects concatenated gzip members and resets inflate for the next member.

Write mode initializes raw deflate and emits a minimal 10-byte gzip header. `gzclose` finishes deflate, emits CRC32 and uncompressed input size in little-endian order, then releases all state.

`gzseek` on read streams is replay-based: backward seeks rewind and re-decompress forward, while forward seeks read and discard output. On write streams, seeking forward writes zero bytes.

## Error Handling and Risks
Errors are tracked in `s->z_err` and exposed through `gzerror`. Filesystem errors use `Z_ERRNO` and `errno`. `gzprintf` protects against formatted-output overflow by checking the fixed-size buffer and terminating byte, but non-ANSI fallback paths depend on `snprintf` availability macros. `gzdopen` does not duplicate the descriptor, matching `fdopen` behavior.

## Dependencies
Depends on `zutil.h`, deflate/inflate APIs, CRC32, stdio, allocation helpers, and zlib portability macros. It is a user-space compression file wrapper, not a Plan 9 kernel/VFS implementation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/gzio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/infback.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/infback.c

## Purpose
Provides zlib’s callback-oriented inflate interface: `inflateBackInit_`, `inflateBack`, and `inflateBackEnd`. It is designed for callers that provide input and output callbacks and a caller-owned sliding window/output buffer.

## Main API Surface
- `inflateBackInit_(strm, windowBits, window, version, stream_size)` validates ABI/version, installs allocators, allocates `inflate_state`, and records the caller-provided window.
- `inflateBack(strm, in, in_desc, out, out_desc)` performs raw deflate block decoding using callback refill/flush.
- `inflateBackEnd(strm)` frees the inflate state.

## Implementation Notes
The file is largely copied from `inflate.c`, but it skips zlib/gzip wrapper parsing and works directly on deflate blocks. It supports stored blocks, fixed Huffman blocks, and dynamic Huffman blocks.

The state machine uses modes such as `TYPE`, `STORED`, `TABLE`, `LEN`, `DONE`, and `BAD`. Macros manage the bit accumulator, callback input pulls, and output-window flushing. When sufficient input and output are available, it calls `inflate_fast()` for optimized literal/length/distance decoding.

## Fixed Tables
`fixedtables()` either includes generated `inffixed.h` tables or builds them once when `BUILDFIXED` is defined. The built-on-demand path is explicitly not thread-safe because of static table initialization.

## Error Handling
Input callback failure or output callback failure returns `Z_BUF_ERROR`; `strm->next_in == Z_NULL` distinguishes input-denied cases. Invalid block structure returns `Z_DATA_ERROR` with `strm->msg` set. Invalid stream/state parameters return `Z_STREAM_ERROR`.

## Dependencies
Uses `zutil.h`, `inftrees.h`, `inflate.h`, and `inffast.h`. It shares the same decode table representation and inflate state as regular inflate.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/infback.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/inffast.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/inffast.c

## Purpose
Implements `inflate_fast()`, the optimized inner loop for deflate decoding. It handles the common hot path where enough input and output space are available to decode without frequent boundary checks.

## Entry Conditions
The caller must ensure:
- `state->mode == LEN`.
- `strm->avail_in >= 6`.
- `strm->avail_out >= 258`.
- `start >= strm->avail_out`.
- `state->bits < 8`.

These constraints let the loop decode the maximum possible length/distance pair without checking for more input or output on every step.

## Core Behavior
The routine copies stream and inflate-state fields into local variables, decodes literal/length codes and distance codes from the current Huffman tables, and writes output bytes. It handles:
- Literals.
- Length/distance matches copied from current output.
- Matches copied from the sliding window, including wraparound.
- Second-level Huffman decode table entries.
- End-of-block and invalid-code transitions.

On return, it updates `next_in`, `next_out`, `avail_in`, `avail_out`, `state->hold`, and `state->bits`.

## Portability/Optimization
`POSTINC` controls whether pointer increments are pre- or post-increment, based on historical CPU performance testing. `ASMINF` can disable the C implementation for assembly replacements.

## Error Handling
Invalid distance or literal/length codes set `strm->msg` and move `state->mode` to `BAD`; end-of-block moves to `TYPE`; otherwise the function returns with `LEN` when input/output thresholds are no longer met.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/inffast.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/inffast.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/inffast.h

## Purpose
Internal declaration header for `inflate_fast()`.

## Contents
Declares:
```c
void inflate_fast OF((z_streamp strm, unsigned start));
```

## Notes
The header warns that applications must not include it directly; public users should include `zlib.h`. It is consumed by `inflate.c` and `infback.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/inffast.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/inffixed.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/inffixed.h

## Purpose
Generated static decode tables for fixed-Huffman deflate blocks.

## Contents
Defines:
- `static const code lenfix[512]`: literal/length fixed-code decode table.
- `static const code distfix[32]`: fixed distance-code decode table.

## Generation
The file is generated by `makefixed()` in `inflate.c` when built with `MAKEFIXED`. Normal builds include this file directly from `fixedtables()` in `inflate.c` and `infback.c`.

## Usage
The tables provide fast lookup entries for fixed Huffman blocks without constructing tables at runtime. Entries use the `code` structure from `inftrees.h`, with `op`, `bits`, and `val` fields.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/inffixed.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/inflate.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/inflate.c

## Purpose
Implements zlib decompression: stream initialization/reset, zlib/gzip/raw wrapper handling, deflate block decoding, dictionary support, synchronization recovery, state copying, and cleanup.

## Main API Surface
Exports:
- `inflateReset`
- `inflateInit2_`
- `inflateInit_`
- `inflate`
- `inflateEnd`
- `inflateSetDictionary`
- `inflateSync`
- `inflateSyncPoint`
- `inflateCopy`

Internal helpers:
- `fixedtables`
- `updatewindow`
- `syncsearch`
- Optional `makefixed` generator.

## Wrapper Handling
`inflateInit2_` interprets `windowBits`:
- Negative values request raw deflate with no zlib/gzip wrapper.
- Positive values enable zlib wrapping.
- With `GUNZIP`, larger encoded values can enable gzip header/trailer handling.

The `HEAD` state validates zlib headers or gzip magic. Gzip-specific states parse flags, timestamp, OS byte, extra field, original name, comment, and header CRC. Trailer validation checks Adler-32 for zlib or CRC32 plus length for gzip.

## Deflate State Machine
The main `inflate()` switch handles:
- Stored blocks: length/complement validation and byte copy.
- Fixed-Huffman blocks: precomputed fixed tables.
- Dynamic-Huffman blocks: code-length table parsing and `inflate_table()` table construction.
- Literal, match length, distance, and copy states.
- End-of-block, checksum, done, bad, memory, and sync states.

For large enough buffers, `LEN` delegates to `inflate_fast()`.

## Sliding Window
`updatewindow()` lazily allocates the sliding window only when needed. It records the last `2^wbits` output bytes in circular form, enabling future distance references and dictionary injection.

## Dictionary and Sync
`inflateSetDictionary()` validates the dictionary Adler-32 and loads dictionary bytes into the window. `inflateSync()` scans for the byte pattern `00 00 ff ff` to recover at flush points, preserving total counters across reset. `inflateSyncPoint()` identifies a state useful for PPP-style sync flush handling.

## Error Handling
The implementation sets `strm->msg` for malformed headers, bad block types, invalid code lengths, bad distance references, checksum mismatches, and length mismatches. Lack of progress or `Z_FINISH` without completion yields `Z_BUF_ERROR`.

## Dependencies
Uses `zutil.h`, `inftrees.h`, `inflate.h`, and `inffast.h`. It is central to `gzio.c`, `uncompr.c`, and other zlib consumers in this Ghostscript tree.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/inflate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/inflate.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/inflate.h

## Purpose
Internal header defining inflate modes and the persistent `inflate_state` structure.

## Key Definitions
Enables gzip decoding by defining `GUNZIP` unless `NO_GZIP` is set.

Defines `inflate_mode`, including:
- Header modes: `HEAD`, gzip-specific `FLAGS`, `TIME`, `OS`, `EXLEN`, `EXTRA`, `NAME`, `COMMENT`, `HCRC`.
- Dictionary modes: `DICTID`, `DICT`.
- Block modes: `TYPE`, `TYPEDO`, `STORED`, `COPY`, `TABLE`, `LENLENS`, `CODELENS`.
- Decode modes: `LEN`, `LENEXT`, `DIST`, `DISTEXT`, `MATCH`, `LIT`.
- Trailer/done/error modes: `CHECK`, gzip `LENGTH`, `DONE`, `BAD`, `MEM`, `SYNC`.

## `inflate_state`
Stores:
- Current mode and wrapper flags.
- Checksum and total output counters.
- Sliding window fields.
- Bit accumulator fields.
- Current copy length, match offset, and extra-bit count.
- Active literal/length and distance decode tables.
- Dynamic table-building arrays: `lens[320]`, `work[288]`, and `codes[ENOUGH]`.

## Usage
Included by `inflate.c`, `infback.c`, and `inffast.c`. It is an internal ABI and is explicitly not intended for application use.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/inflate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/inftrees.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/inftrees.c

## Purpose
Builds canonical Huffman decode tables for inflate. The single exported function is `inflate_table()`.

## Main API
```c
int inflate_table(codetype type,
                  unsigned short FAR *lens,
                  unsigned codes,
                  code FAR * FAR *table,
                  unsigned FAR *bits,
                  unsigned short FAR *work);
```

Returns:
- `0` on success.
- `-1` for invalid code sets.
- `+1` if the supplied table capacity is insufficient.

## Algorithm
The function:
1. Counts the number of symbols at each bit length.
2. Determines minimum, maximum, and root table bit widths.
3. Checks for over-subscribed or invalid incomplete trees.
4. Sorts symbols by length into `work`.
5. Builds root and sub-tables using bit-reversed deflate canonical-code order.
6. Emits invalid-code markers for unfilled decode entries.
7. Advances `*table` to the next free table slot and updates `*bits`.

## Code Types
Supports:
- `CODES`: code-length alphabet.
- `LENS`: literal/length alphabet with length bases and extra bits.
- `DISTS`: distance alphabet with distance bases and extra bits.

## Important Data
Static base/extra tables define deflate length and distance semantics. The implementation uses `ENOUGH` and `MAXD` from `inftrees.h` to guard dynamic table space.

## Consumers
Used by `inflate.c`, `infback.c`, and fixed-table generation paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/inftrees.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/inftrees.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/inftrees.h

## Purpose
Internal header for inflate Huffman decode table construction and representation.

## Key Types
Defines `code`:
- `op`: operation, extra-bit count, table-link bit count, end marker, or invalid marker.
- `bits`: number of bits consumed by this table entry.
- `val`: literal byte, base length/distance, or sub-table offset.

Defines `codetype`:
- `CODES`
- `LENS`
- `DISTS`

## Constants
- `ENOUGH 1440`: decode table capacity for dynamic trees.
- `MAXD 154`: maximum distance-table reserve used in capacity checks.

## API
Declares `inflate_table()`, used by inflate implementations to build decode tables from code lengths.

## Notes
The file documents the exact `op` encoding, which is central to `inflate.c`, `infback.c`, and `inffast.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/inftrees.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/minigzip.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/minigzip.c

## Purpose
Small example/test implementation of a gzip-like command using zlib’s `gz*` API. It is explicitly not intended as a full gzip replacement.

## Main Functions
- `error(msg)`: prints program-prefixed error and exits.
- `gz_compress(in, out)`: streams input `FILE *` to `gzFile`.
- Optional `gz_compress_mmap(in, out)`: compresses an mmap’d file when `USE_MMAP` is enabled.
- `gz_uncompress(in, out)`: streams `gzFile` to output `FILE *`.
- `file_compress(file, mode)`: writes `<file>.gz`, then unlinks the original.
- `file_uncompress(file)`: expands `.gz` input or appends `.gz` to locate input, then unlinks compressed input.
- `main(argc, argv)`: parses `-d`, `-f`, `-h`, `-r`, and `-1`..`-9`.

## Behavior
With no file arguments, it reads stdin and writes stdout, using `gzdopen()` over the existing descriptors. With file arguments, it creates/removes files similarly to basic gzip behavior.

## Portability
Contains platform branches for binary mode on DOS/Windows/Cygwin, VMS/RISC OS suffix behavior, optional mmap, and compiler-specific `fileno` handling.

## Limitations and Risks
The source comments warn that error checking is limited and filesystem naming constraints are not handled. `file_compress` and `file_uncompress` use fixed `MAX_NAME_LEN` buffers with `strcpy`/`strcat`, making it test/demo code rather than hardened utility code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/minigzip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/trees.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/trees.c

## Purpose
Implements deflate-side Huffman tree generation and compressed block emission. It turns literal/match tallies from the deflater into stored, static-Huffman, or dynamic-Huffman deflate blocks.

## Main Exported/Internal API
Exports zlib-internal tree routines:
- `_tr_init`
- `_tr_stored_block`
- `_tr_align`
- `_tr_flush_block`
- `_tr_tally`

Internal helpers include:
- `tr_static_init`
- `init_block`
- `pqdownheap`
- `gen_bitlen`
- `gen_codes`
- `build_tree`
- `scan_tree`
- `send_tree`
- `build_bl_tree`
- `send_all_trees`
- `compress_block`
- `set_data_type`
- `bi_reverse`
- `bi_flush`
- `bi_windup`
- `copy_block`

## Static Data
Defines or includes:
- Extra-bit tables for lengths, distances, and bit-length codes.
- Bit-length-code send order.
- Static literal and distance trees.
- Distance-code and length-code lookup tables.
- Base length and distance tables.

When `GEN_TREES_H` is defined, it can regenerate `trees.h`.

## Algorithm
`_tr_tally()` records literals or length/distance matches and increments tree frequencies. `_tr_flush_block()` then:
1. Builds literal and distance Huffman trees when compression is enabled.
2. Builds the bit-length tree used to describe those trees.
3. Estimates stored/static/dynamic block sizes.
4. Emits the cheapest legal encoding, unless forced by compile-time options.
5. Resets per-block tallies and aligns the bit buffer on EOF.

Dynamic tree construction uses a heap ordered by frequency with depth tie-breaking. `gen_bitlen()` corrects bit-length overflow to satisfy max code lengths. `gen_codes()` assigns canonical bit-reversed deflate codes.

## Bit Output
`send_bits`, `put_short`, `bi_flush`, and `bi_windup` manage the deflate bitstream in LSB-first order. Stored blocks are byte-aligned and include length plus one’s complement.

## Data Type Guessing
`set_data_type()` marks the stream as ASCII or binary using a simple frequency heuristic over literal bytes.

## Dependencies
Includes `deflate.h` and relies on deflate-state buffers such as `pending_buf`, `dyn_ltree`, `dyn_dtree`, `bl_tree`, `l_buf`, and `d_buf`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/trees.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/trees.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/trees.h

## Purpose
Generated static table header for deflate tree support. It is created by building `trees.c` with `-DGEN_TREES_H`.

## Contents
Defines:
- `static_ltree[L_CODES+2]`: fixed literal/length tree codes and lengths.
- `static_dtree[D_CODES]`: fixed distance tree codes and lengths.
- `_dist_code[DIST_CODE_LEN]`: lookup table mapping normalized distances to distance-code numbers.
- `_length_code[MAX_MATCH-MIN_MATCH+1]`: lookup table mapping normalized match lengths to length-code numbers.
- `base_length[LENGTH_CODES]`: base normalized length per length code.
- `base_dist[D_CODES]`: base normalized distance per distance code.

## Usage
Included by `trees.c` for ANSI C builds instead of generating static tables at runtime. The tables speed deflate block construction and static-Huffman emission.

## Notes
This is generated data, not hand-written logic. Its correctness is tied to `tr_static_init()` and `gen_trees_header()` in `trees.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/trees.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/uncompr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/uncompr.c

## Purpose
Implements zlib’s one-shot `uncompress()` helper for decompressing a complete memory buffer into a caller-provided destination buffer.

## API
```c
int uncompress(Bytef *dest,
               uLongf *destLen,
               const Bytef *source,
               uLong sourceLen);
```

## Behavior
Initializes a local `z_stream`, checks that source and destination sizes fit in `uInt`, calls `inflateInit`, then calls `inflate(..., Z_FINISH)` once. On success, it stores `stream.total_out` in `*destLen` and ends the stream.

## Error Mapping
If inflate does not end with `Z_STREAM_END`, the function cleans up and maps `Z_NEED_DICT` or an exhausted-input `Z_BUF_ERROR` to `Z_DATA_ERROR`. Other inflate errors are returned directly.

## Use Case
Useful when the caller already knows the full uncompressed size and has a sufficiently large destination buffer, such as decompressing an mmap’d file or in-memory resource.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/uncompr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/zconf.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/zconf.h

## Purpose
Public zlib configuration header controlling symbol prefixing, compiler/platform detection, calling conventions, core typedefs, and portability defaults.

## Major Features
- `Z_PREFIX` remaps public symbols and core typedef names to `z_*` names.
- Detects DOS, OS/2, Windows, 16-bit memory models, C standard support, and selected platform quirks.
- Defines `MAX_MEM_LEVEL` and `MAX_WBITS` defaults.
- Defines prototype macro `OF(args)`.
- Defines `FAR`, `ZEXTERN`, `ZEXPORT`, and `ZEXPORTVA`.
- Defines zlib basic types: `Byte`, `uInt`, `uLong`, `Bytef`, `charf`, `intf`, `uIntf`, `uLongf`, `voidpc`, `voidpf`, `voidp`.
- Defines `z_off_t`, defaulting to `long` because the `HAVE_UNISTD_H` block is disabled with `#if 0`.
- Provides `SEEK_SET`, `SEEK_CUR`, and `SEEK_END` fallbacks.

## Platform Branches
Contains DLL import/export handling for Windows and BeOS, `ZLIB_WINAPI` support, MVS `#pragma map` aliases for short external names, and `NO_vsnprintf` settings for OS/400 and MVS.

## Plan 9 Relevance
There is no Plan 9-specific branch here. In this vendored tree, Plan 9 builds likely use the generic C path: no special DLL/export decorations, `FAR` empty, and `z_off_t long`.

## Relationship to `zconf.in.h`
This is the configured header used by the source tree. In this repository it is effectively the same as `zconf.in.h` except for the RCS identifier line.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/zconf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/zconf.in.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/zconf.in.h

## Purpose
Template/configuration-source version of `zconf.h`. It contains the same portability and type-definition logic, intended to be processed or copied by zlib configuration workflows.

## Major Features
Matches `zconf.h` in:
- Optional `Z_PREFIX` symbol/type renaming.
- Platform/compiler detection.
- `MAX_MEM_LEVEL` and `MAX_WBITS` defaults.
- Function prototype and calling convention macros.
- Basic zlib typedefs.
- `z_off_t` selection and seek constant fallbacks.
- Windows, BeOS, OS/400, and MVS branches.

## Difference from `zconf.h`
The observed content is functionally identical to `zconf.h`; the visible difference is the source identification comment:
- `zconf.h` identifies itself as `zconf.h`.
- `zconf.in.h` identifies itself as `zconf.in.h`.

## Usage
Kept as an input/template header for generated or configured builds. In this repository’s vendored Ghostscript zlib copy, it documents the same portability assumptions as the active `zconf.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/zconf.in.h -->