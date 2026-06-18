# Research: subset-b-009176

This grouped report covers rsync's vendored zlib deflate/inflate core files under `sources/sync-backup/rsync/zlib`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/zlib/deflate.c -->
# sources/sync-backup/rsync/zlib/deflate.c

Purpose: implements zlib 1.2.8 compression using the DEFLATE algorithm. It owns stream initialization, wrapper emission, LZ77 match finding, block flush policy, dictionary loading, pending-output movement, and cleanup for the compressor side. In rsync this is part of the bundled zlib copy used when the build does not rely on a system zlib or when rsync-specific integration selects the bundled tree.

Important APIs and functions: public zlib entry points are `deflateInit_`, `deflateInit2_`, `deflate`, `deflateEnd`, `deflateCopy`, `deflateReset`, `deflateResetKeep`, `deflateSetDictionary`, `deflateSetHeader`, `deflatePending`, `deflatePrime`, `deflateParams`, `deflateTune`, and `deflateBound`. Internal helpers include `fill_window`, `longest_match`, `lm_init`, `read_buf`, `flush_pending`, and the strategy engines `deflate_stored`, `deflate_fast`, `deflate_slow`, `deflate_rle`, and `deflate_huff`. The `configuration_table` maps levels to match-search limits and a compressor function.

Control flow: `deflateInit2_` validates version, wrapper, method, window, memory level, compression level, and strategy, then allocates `deflate_state`, sliding window, hash chains, and the overlaid pending/symbol buffer. `deflate()` is a resumable driver: it emits zlib or gzip headers, flushes any pending bytes, rejects invalid flush/input states, dispatches to the selected block compressor, emits empty stored blocks for sync/full flushes, and writes the Adler-32 or CRC32 trailer on `Z_FINISH`. The strategy engines fill lookahead, insert strings into hash chains, tally literals or length/distance pairs through `trees.c`, and request block flushing when the symbol buffer fills or a flush is requested.

State and persistence: all persistent compressor state is in `deflate_state` through `strm->state`: window positions, hash heads, previous links, pending buffer cursors, gzip-header substate, checksum, match parameters, and tree/tally state. No filesystem persistence exists. `deflateCopy` deep-copies active buffers and fixes internal pointers. `deflateResetKeep` preserves allocations but resets stream counters and tree state; `deflateReset` also clears match/window state.

Dependencies and integration points: depends on `deflate.h`, `zutil.h`, checksum functions, allocator macros, and tree writers `_tr_*` from `trees.c`. It consumes public constants and stream structures from `zlib.h`/`zconf.h`. The file includes rsync-visible behavior through the non-upstream `Z_INSERT_ONLY` flush mode present in this vendored zlib, which updates dictionary state without emitting compressed symbols in the strategy loops.

Risks: this file is sensitive to buffer accounting, hash-chain bounds, bit-buffer availability, wrapper state transitions, and legacy 16-bit portability paths. Changes to `pending_buf`/`sym_buf` overlay sizing can corrupt symbols while output is being written. Match routines intentionally read initialized guard bytes beyond real lookahead, so `fill_window` high-water zeroing is part of memory-safety behavior. Flush semantics are subtle: repeated flushes, finishing with pending output, and full-flush hash clearing all affect interoperability.

Test signals: exercise zlib, gzip, and raw deflate modes; all compression levels and strategies; preset dictionaries; `deflateCopy`; small output buffers; repeated `Z_SYNC_FLUSH`, `Z_FULL_FLUSH`, `Z_BLOCK`, `Z_FINISH`; and `Z_INSERT_ONLY` if rsync uses it. Round-trip tests should compare against a known-good inflater and include sanitizer/fuzzer runs for boundary-heavy inputs and dictionaries near the 32 KiB window size.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/zlib/deflate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/zlib/deflate.h -->
# sources/sync-backup/rsync/zlib/deflate.h

Purpose: private compressor-state header for the vendored zlib implementation. It is not an application API; it defines DEFLATE constants, tree descriptor types, the full `deflate_state` layout, and inline tally/output helpers shared by `deflate.c` and `trees.c`.

Important APIs/types/functions: key constants include `LENGTH_CODES`, `LITERALS`, `L_CODES`, `D_CODES`, `BL_CODES`, `HEAP_SIZE`, `MAX_BITS`, `Buf_size`, stream status values, `MIN_LOOKAHEAD`, `MAX_DIST`, and `WIN_INIT`. Important types are `ct_data`, `tree_desc`, `Pos`, `IPos`, and `deflate_state`. It declares internal tree functions `_tr_init`, `_tr_tally`, `_tr_flush_block`, `_tr_flush_bits`, `_tr_align`, and `_tr_stored_block`. Non-debug builds inline `_tr_tally_lit` and `_tr_tally_dist` to append three-byte symbols and update frequency trees.

Control flow: there is no runtime control flow beyond macros. The header shapes the control flow in `deflate.c`: stream status values drive wrapper/header states, `put_byte` appends pending bytes, distance-code mapping routes matches to `_dist_code`, and the tally macros decide when a block must flush by comparing `sym_next` to `sym_end`.

State and persistence: `deflate_state` is the persistent compression object. It stores the public stream back-pointer, pending output, wrapper/header fields, LZ77 window/hash structures, match-search cursors, compression tuning values, Huffman trees, heap/work arrays, symbol buffer cursors, debug counters, bit buffer, and `high_water` memory-initialization marker. No external persistence exists; state survives across calls until reset or end.

Dependencies and integration points: includes `zutil.h` and therefore pulls in public zlib types, allocation macros, checksum helpers, and portability configuration. It exposes the contract between compressor match generation and Huffman block emission in `trees.c`; changes to structure layout or macros must be synchronized with both files.

Risks: this header is a blast-radius multiplier. Field order and meanings are assumed by copy/reset logic and tree code. The overlaid `pending_buf`/`sym_buf` model depends on `lit_bufsize`, `sym_end`, and three-byte symbols. Changing constants like `MAX_BITS`, `MIN_LOOKAHEAD`, or distance coding breaks RFC1951 compatibility and table sizes. Inline macros evaluate some arguments multiple times and require side-effect-free inputs where documented.

Test signals: compile with debug and non-debug modes, `FASTEST`, optional gzip disablement, and representative platform defines. Compression tests should verify block flushes, distance/length tallying, and `deflateCopy` after partially filled buffers because these paths depend directly on this header's state layout.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/zlib/deflate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/zlib/dummy.in -->
# sources/sync-backup/rsync/zlib/dummy.in

Purpose: tiny build-system placeholder. Its content states that it exists to ensure the library directory is created by `configure` when a VPATH build is used. It is not part of compression or decompression logic.

Important APIs/types/functions: none. The file contains no code, declarations, macros, or data structures.

Control flow: none at runtime. Its only behavior is indirect through packaging/configure machinery that includes or copies placeholder files when constructing build directories.

State and persistence: no program state. It is a source-tree artifact whose presence can affect whether an otherwise empty generated library directory appears in VPATH or out-of-tree builds.

Dependencies and integration points: integrates with configure/build scripts rather than C code. It may be referenced by distribution manifests or makefile rules that expect the zlib lib directory to be non-empty before generated files are placed there.

Risks: deleting it can cause build-directory creation regressions in VPATH scenarios even though normal in-tree builds may not notice. Editing its text has little code risk but may confuse build scripts if they rely on exact filenames or source distribution contents.

Test signals: perform an out-of-tree/VPATH configure and build, then confirm the expected zlib library directory is created. Source distribution or packaging tests should verify the placeholder remains included.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/zlib/dummy.in -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/zlib/gzguts.h -->
# sources/sync-backup/rsync/zlib/gzguts.h

Purpose: private header for zlib `gz*` file I/O internals. It centralizes portability includes, large-file setup, stdio/error adapters, default gzip buffer sizes, gzip read/write mode constants, and the internal `gz_state` object used by gzlib/gzread/gzwrite-style modules.

Important APIs/types/functions: defines `ZLIB_INTERNAL` visibility when hidden symbols are available, `local`, `GZBUFSIZE`, mode constants `GZ_NONE`, `GZ_READ`, `GZ_WRITE`, `GZ_APPEND`, and read-state constants `LOOK`, `COPY`, `GZIP`. The key type is `gz_state`, which embeds the public `gzFile_s` prefix and stores fd/path, buffers, transparent/direct flag, read header state, compression settings, seek state, error state, and an in-place `z_stream`. It declares shared helpers `gz_error`, optionally `gz_strwinerror`, and `gz_intmax`.

Control flow: this header does not implement algorithms, but it defines the state machine vocabulary used by gzip file readers: `LOOK` searches for a gzip header, `COPY` passes transparent input through, and `GZIP` inflates compressed data. It also maps Windows/CE/POSIX file functions and snprintf/vsnprintf availability so the gz modules compile on many targets.

State and persistence: `gz_state` persists for an open gzip file handle. It owns heap buffers, fd position metadata, eof/past flags, deferred seek information, error messages, and an embedded inflate/deflate stream. The `x` member is intentionally first/exposed for `gzgetc()` macro access to `have`, `next`, and `pos`.

Dependencies and integration points: includes `zlib.h`, stdio/string/stdlib/limits/fcntl/io headers depending on platform, and relies on zlib allocator and stream APIs. It is consumed by gz file implementation files, not by the deflate/inflate bit-level core directly.

Risks: platform preprocessor branches are high risk because small changes can alter ABI/export visibility, large-file offsets, Windows function mapping, or availability of safe formatting functions. `gz_state` layout matters for macros that treat the beginning as `gzFile_s`. Error-message ownership must stay consistent with `gz_error` cleanup.

Test signals: build on POSIX and Windows-like configurations, with and without large-file flags, hidden visibility, and `NO_GZCOMPRESS`. Runtime tests should cover gzopen/gzdopen, transparent reads, gzip reads/writes, seeks, errors, and files larger than 2 GiB when large-file support is enabled.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/zlib/gzguts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/zlib/inffast.c -->
# sources/sync-backup/rsync/zlib/inffast.c

Purpose: optimized inner loop for inflate literal/length/distance decoding. `inflate()` enters this routine when there are at least six input bytes and 258 output bytes available, allowing most boundary checks to be removed from the hottest decompression path.

Important APIs/types/functions: exports one internal function, `inflate_fast(z_streamp strm, unsigned start)`, unless `ASMINF` selects an assembler implementation. It uses `struct inflate_state`, `code` decode-table entries, length and distance tables generated by `inftrees.c` or fixed tables, and stream fields `next_in`, `next_out`, `avail_in`, and `avail_out`.

Control flow: the function copies stream and inflate state into locals, then loops while input and output remain above safety thresholds. It pulls enough bits for a literal/length code, follows second-level table links when needed, emits literals, decodes length extra bits, decodes distance extra bits, and copies matches either from the current output buffer or from the circular sliding window. End-of-block sets mode `TYPE`; invalid length/distance codes or impossible distances set mode `BAD`.

State and persistence: it mutates only the active inflate stream/state: input/output pointers and counts, `hold`, `bits`, and `state->mode`. Window metadata is read but not updated here; `inflate()` updates the window on leave. No external persistence exists.

Dependencies and integration points: called from `inflate.c` in mode `LEN` after dynamic or fixed tables are ready. Depends on `zutil.h`, `inftrees.h`, `inflate.h`, and `inffast.h`. Optional `INFLATE_STRICT` enforces zlib header distance maximums; optional invalid-distance compatibility can synthesize zero bytes if enabled.

Risks: this routine is performance- and memory-safety-critical. The entry assumptions must remain matched to `inflate.c`; otherwise it can read past input or write past output. Overlapped match copying, wrapped window copies, and bit roll-back at exit are easy to break. Error messages and mode transitions must match the slower decoder for identical behavior.

Test signals: differential tests should force both fast and slow inflate paths by varying buffer sizes. Include fixed and dynamic Huffman blocks, matches copied from output and from window, wrapped window distances, invalid distance/code streams, strict distance mode, and sanitizers/fuzzers for malformed compressed data.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/zlib/inffast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/zlib/inffast.h -->
# sources/sync-backup/rsync/zlib/inffast.h

Purpose: private declaration header for the optimized inflate decoder in `inffast.c`.

Important APIs/types/functions: declares `void ZLIB_INTERNAL inflate_fast OF((z_streamp strm, unsigned start));`. The declaration uses zlib's `OF` compatibility macro and hidden/internal export convention.

Control flow: no runtime logic. Its role is to let `inflate.c` call the fast path when the state machine has enough input and output space.

State and persistence: no state. The declared function mutates `z_stream` and `inflate_state`, but this header only provides the signature.

Dependencies and integration points: relies on `z_streamp` and `ZLIB_INTERNAL` being defined before inclusion, as they are through `zutil.h`/`zlib.h` in the including source. Included by both `inflate.c` and `inffast.c` to keep the prototype consistent.

Risks: signature drift would break ABI-internal calls or assembler replacement compatibility. The `start` parameter is essential for computing the beginning of the output buffer inside `inflate_fast`; removing or changing it would break distance calculations.

Test signals: compilation is the main direct signal. Runtime fast-path coverage in inflate tests indirectly validates that this declaration matches the implementation and call site.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/zlib/inffast.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/zlib/inffixed.h -->
# sources/sync-backup/rsync/zlib/inffixed.h

Purpose: generated static decode tables for RFC1951 fixed Huffman blocks. It is included directly inside `fixedtables()` in `inflate.c` when `BUILDFIXED` is not used.

Important APIs/types/functions: defines two `static const code` arrays: `lenfix[512]` for literal/length decoding with 9 root bits and `distfix[32]` for distance decoding with 5 root bits. The entries encode `op`, `bits`, and `val` according to `inftrees.h`.

Control flow: no active control flow. Inclusion initializes local static tables that `fixedtables()` assigns to `state->lencode` and `state->distcode`. The decode loops in `inflate.c` and `inffast.c` then index these tables for fixed-code blocks.

State and persistence: tables are immutable static data with translation-unit scope because the file is included inside a function. No dynamic state or persistence exists.

Dependencies and integration points: depends on the `code` struct from `inftrees.h` and on `inflate.c`'s include context. It is generated by `makefixed()` in `inflate.c` when building with `MAKEFIXED`, so table contents must match that generator and the fixed-code specification.

Risks: manual edits can silently corrupt fixed-block decoding. The table sizes and root bits are coupled to `fixedtables()` assignments (`lenbits = 9`, `distbits = 5`). Because the file is an include fragment rather than a complete header with guards, including it elsewhere could create duplicate or context-dependent symbols.

Test signals: decompress streams that force fixed Huffman blocks, compare against dynamic/stored block round trips, and regenerate with `MAKEFIXED` to verify table stability. Fuzzing should include fixed-code malformed streams to ensure invalid markers are handled.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/zlib/inffixed.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/zlib/inflate.c -->
# sources/sync-backup/rsync/zlib/inflate.c

Purpose: main zlib decompressor implementation. It parses zlib, gzip, or raw deflate streams, builds dynamic Huffman tables, decodes stored/fixed/dynamic blocks, maintains the sliding window, validates trailers, supports dictionaries, sync recovery, header extraction, copying, and reset/end operations.

Important APIs and functions: public entry points include `inflateInit_`, `inflateInit2_`, `inflate`, `inflateEnd`, `inflateReset`, `inflateReset2`, `inflateResetKeep`, `inflatePrime`, `inflateSetDictionary`, `inflateGetDictionary`, `inflateGetHeader`, `inflateSync`, `inflateSyncPoint`, `inflateCopy`, `inflateUndermine`, and `inflateMark`. Internal helpers are `fixedtables`, `updatewindow`, optional `makefixed`, and `syncsearch`. Macros such as `LOAD`, `RESTORE`, `PULLBYTE`, `NEEDBITS`, `BITS`, `DROPBITS`, and `BYTEBITS` implement the resumable bit accumulator.

Control flow: `inflate()` is a large resumable state machine over `inflate_mode`. It starts in `HEAD`, accepts raw/zlib/gzip headers, optionally records gzip metadata, requests preset dictionaries, reads block type bits, handles stored blocks, builds dynamic code tables through `inflate_table`, decodes literals and matches, delegates to `inflate_fast` when buffers are large enough, validates checksum/length trailers, and returns `Z_STREAM_END`, `Z_OK`, `Z_BUF_ERROR`, or an error. `goto inf_leave` centralizes counter updates, checksum updates, window maintenance, and progress-based return selection.

State and persistence: persistent state is `struct inflate_state` allocated in `inflateInit2_`. It stores mode, wrapper flags, checksum, gzip header target, window allocation and cursors, bit accumulator, current length/distance, dynamic table scratch arrays, decode tables, and diagnostic mark fields. `updatewindow` lazily allocates the circular window only when back-references across calls require it or a dictionary is installed.

Dependencies and integration points: includes `zutil.h`, `inftrees.h`, `inflate.h`, and `inffast.h`. Uses `adler32`, `crc32`, `ZSWAP32`, `ZALLOC`/`ZFREE`, and decode tables from `inftrees.c`/`inffixed.h`. It is the decompression backend used by zlib APIs and by gzip-file read code.

Risks: state transitions are security-sensitive because malformed compressed input is attacker-controlled in many applications. High-risk areas include bit-buffer rollback, table length validation, distance-too-far handling, checksum/trailer byte order, dictionary ID validation, and window wrap copying. `BUILDFIXED` uses static first-call initialization and is documented as not thread-safe.

Test signals: run zlib's inflate conformance vectors, gzip header/trailer cases, raw deflate, preset dictionaries, small input/output chunking, sync recovery after data errors, `inflateCopy`, `inflatePrime`, `inflateMark`, and strict invalid-distance cases. Fuzz compressed input under ASan/UBSan and compare output/errors against a known-good zlib.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/zlib/inflate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/zlib/inflate.h -->
# sources/sync-backup/rsync/zlib/inflate.h

Purpose: private header defining the inflate state machine and persistent decompressor state. It is internal to zlib and should not be consumed by applications.

Important APIs/types/functions: defines `GUNZIP` unless `NO_GZIP` is set, undefines conflicting `BAD` on AIX, declares the `inflate_mode` enum, and defines `struct inflate_state`. Modes include wrapper/header states, block states, decode states, trailer states, and terminal/error states. `struct inflate_state` holds mode flags, wrapper selection, checksum totals, gzip header pointer, circular window, bit accumulator, copy/decode variables, dynamic table arrays, `codes[ENOUGH]`, invalid-distance policy, and `inflateMark` tracking fields.

Control flow: the enum documents the intended transitions: header parsing to `TYPE`, stored/dynamic/fixed block handling to code decode states, literal/match loops back to `LEN`, and trailer validation to `DONE`. `inflate.c` implements the transitions directly in a switch and relies on enum ordering in a few comparisons such as update-window decisions before `BAD`.

State and persistence: this header is the canonical layout of decompressor state preserved between `inflate()` calls. It enables partial input/output operation by saving every variable needed to resume: current mode, bit buffer, pending length/distance, table-building progress, window history, and gzip header-copy progress.

Dependencies and integration points: requires `code` and `ENOUGH` from `inftrees.h`, public `gz_headerp` and zlib types, and `FAR` portability macros. It is included by `inflate.c` and `inffast.c`; the fast path reads fields directly, so layout and semantics are cross-file contracts.

Risks: adding modes or reordering terminal states can change comparisons in `inflate.c`. Changing array sizes (`lens`, `work`, `codes`) without corresponding table-builder changes can cause memory corruption. `sane` and invalid-distance compatibility are security-relevant because they decide whether malformed streams error or synthesize zero output.

Test signals: compile and run all inflate modes with gzip enabled/disabled, test partial-buffer resumption for every major state, and run malformed-stream fuzzers that interrupt during header, table, match, and trailer phases.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/zlib/inflate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/zlib/inftrees.c -->
# sources/sync-backup/rsync/zlib/inftrees.c

Purpose: builds canonical Huffman decode tables for inflate. It converts code-length arrays from fixed or dynamic deflate metadata into compact table entries used by the slow and fast decoders.

Important APIs/types/functions: exports `inflate_table(codetype type, unsigned short *lens, unsigned codes, code **table, unsigned *bits, unsigned short *work)`. Local static base/extra arrays map deflate length codes and distance codes to base values and extra-bit operations. Return values are `0` for success, `-1` for invalid code length sets, and `+1` when the caller-provided table space is insufficient.

Control flow: `inflate_table` counts lengths, clamps root bits between minimum and maximum actual lengths, rejects over-subscribed and most incomplete trees, sorts symbols by length into `work`, then fills root-table and sub-table entries using deflate's bit-reversed canonical code ordering. It replicates shorter-code entries across all matching table slots and creates sub-table links when code lengths exceed the root. Remaining incomplete slots are marked invalid.

State and persistence: the function is stateless except for writes through `table`, `bits`, and `work`. It advances `*table` to the next free entry so callers can place length and distance tables back-to-back in `state->codes`. It exposes a copyright string but no mutable globals.

Dependencies and integration points: includes `zutil.h` and `inftrees.h`. Called by `inflate.c` for gzip/zlib dynamic block code-length tables, literal/length tables, distance tables, and optional fixed-table generation. Table sizing must align with `ENOUGH_LENS`, `ENOUGH_DISTS`, and root bit choices in `inflate.c`.

Risks: incorrect validation can accept invalid compressed data or reject valid streams. Used-entry accounting protects against table overrun; any root-bit or `ENOUGH` mismatch is memory-safety critical. The `op` encoding must remain consistent with both `inflate.c` and `inffast.c`.

Test signals: table-builder unit tests should cover empty, single-symbol, complete, incomplete, and over-subscribed length sets for `CODES`, `LENS`, and `DISTS`. Full inflate tests should include dynamic blocks with repeat-code-heavy length sections and maximum table sizes. Fuzzing should target dynamic headers.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/zlib/inftrees.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/zlib/inftrees.h -->
# sources/sync-backup/rsync/zlib/inftrees.h

Purpose: private interface for inflate decode-table construction and representation.

Important APIs/types/functions: defines `code`, a four-byte table entry with `op`, `bits`, and `val`. Documents `op` encodings for literals, table links, length/distance bases with extra bits, end-of-block, and invalid-code markers. Defines sizing constants `ENOUGH_LENS`, `ENOUGH_DISTS`, and `ENOUGH`, plus enum `codetype` values `CODES`, `LENS`, and `DISTS`. Declares `inflate_table`.

Control flow: no runtime logic in the header, but the `code` layout drives decoder control flow. `inflate.c` and `inffast.c` inspect `op` bits to decide whether to emit a literal, follow a second-level table, read extra bits, end a block, or report invalid input.

State and persistence: no mutable state. The constants determine the size of `inflate_state.codes`, which persists between calls while a dynamic block is active.

Dependencies and integration points: included by `inflate.c`, `inflate.h`, `inffast.c`, `inffixed.h` through include context, and `inftrees.c`. The comments explicitly tie `ENOUGH_*` to exhaustive searches and to the root table sizes used in inflate calls (`9` for literal/length and `6` for distance dynamic tables).

Risks: changing `code` packing, `op` encoding, or `ENOUGH` sizes requires coordinated decoder/table-builder updates. Under-sizing `ENOUGH` can corrupt memory; over-sizing affects per-stream memory. The comment contains a typo in "distribution", but it has no behavior impact.

Test signals: compile-time size/layout assumptions should be checked across compilers. Dynamic-block fuzzing and maximum-table test vectors validate the constants and `op` interpretation.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/zlib/inftrees.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/zlib/trees.c -->
# sources/sync-backup/rsync/zlib/trees.c

Purpose: emits deflate blocks using stored, static Huffman, or dynamic Huffman coding. It consumes literal/match tallies from `deflate.c`, builds Huffman trees, serializes dynamic tree metadata, writes block bits into the pending buffer, and detects text/binary data type.

Important APIs and functions: internal exports are `_tr_init`, `_tr_tally`, `_tr_flush_block`, `_tr_flush_bits`, `_tr_align`, and `_tr_stored_block`. Major local helpers are `tr_static_init`, `init_block`, `pqdownheap`, `gen_bitlen`, `gen_codes`, `build_tree`, `scan_tree`, `send_tree`, `build_bl_tree`, `send_all_trees`, `compress_block`, `detect_data_type`, `bi_reverse`, `bi_flush`, `bi_windup`, and `copy_block`. It also defines fixed/static descriptor metadata and extra-bit tables.

Control flow: `_tr_init` prepares static tables and per-stream tree descriptors. Tallying appends symbols and frequency counts. `_tr_flush_block` builds literal and distance trees, builds the bit-length tree, computes byte costs for dynamic and static encodings, compares with stored-block cost, writes the selected block type, emits tree headers if dynamic, compresses symbol data, resets block state, and winds up bits for the final block.

State and persistence: mutates `deflate_state` tree arrays, heap, bit counts, symbol buffer cursor, match count, optimal/static bit lengths, bit buffer, and pending output. Static fixed tables are either generated once at runtime for non-ANSI/generation builds or included from `trees.h`.

Dependencies and integration points: includes `deflate.h` and optionally `trees.h`. It relies on `put_byte` and `deflate_state` from `deflate.h`; `deflate.c` relies on this file for all block emission. Output must match inflate's table builder and fixed-table expectations.

Risks: Huffman length overflow correction, dynamic tree repeat-code serialization, and stored/static/dynamic cost comparison are correctness-sensitive. Bit-buffer functions must preserve little-endian bit order required by deflate. The pending/symbol buffer overlay assertion protects against self-overwrite. Static initialization paths must remain thread-safe when using prebuilt `trees.h`; generation modes write `trees.h` as a build artifact.

Test signals: verify compression output round-trips through independent inflaters for stored, fixed, and dynamic blocks; force `Z_FIXED`; test high-frequency skew that causes bit-length overflow; test incompressible data that should become stored blocks; and compare generated `trees.h` under `GEN_TREES_H`. Sanitizers should cover block flushes near symbol buffer limits.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/zlib/trees.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/zlib/trees.h -->
# sources/sync-backup/rsync/zlib/trees.h

Purpose: generated static data include for `trees.c`. It precomputes fixed Huffman trees and length/distance lookup tables so normal builds do not need to generate them at runtime.

Important APIs/types/functions: defines `static_ltree`, `static_dtree`, `_dist_code`, `_length_code`, `base_length`, and `base_dist`. The arrays map literals, lengths, and distances to canonical fixed-tree codes and compact length/distance code indexes used by `_tr_tally_dist` and `compress_block`.

Control flow: no runtime control flow. When included by `trees.c`, these tables feed `_tr_init`, fixed-block emission, distance-code selection, and extra-bit base calculations.

State and persistence: immutable static/const table data. `_dist_code` and `_length_code` are exported with `ZLIB_INTERNAL` visibility for non-debug tally macros in `deflate.h`; other arrays are local to `trees.c` through include context.

Dependencies and integration points: generated by `gen_trees_header()` in `trees.c` when compiled with `GEN_TREES_H`. Depends on constants from `deflate.h` such as `L_CODES`, `D_CODES`, `DIST_CODE_LEN`, `MAX_MATCH`, and `MIN_MATCH`. Must remain synchronized with the generator and with RFC1951 fixed Huffman definitions.

Risks: corruption here causes compressor output incompatibility even if the algorithm code is unchanged. Because this is an include fragment, it lacks standalone include guards and assumes `local`, `ct_data`, `uch`, and code constants are already defined. The exported lookup arrays must keep constness/signature compatible with declarations in `deflate.h`.

Test signals: regenerate via `GEN_TREES_H` and diff against the checked-in file. Run fixed-block compression/decompression and length/distance-heavy dynamic compression tests. Compile in debug and non-debug modes to validate `_length_code`/`_dist_code` declarations.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/zlib/trees.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/zlib/zconf.h -->
# sources/sync-backup/rsync/zlib/zconf.h

Purpose: central portability and ABI configuration header for zlib. It defines optional symbol prefixing, platform detection, calling conventions, type aliases, large-file support, function prototype compatibility, memory/window limits, and exported/internal symbol macros.

Important APIs/types/functions: the `Z_PREFIX` block renames all public and internal linked symbols and typedefs. Platform sections define `MSDOS`, `OS2`, `WINDOWS`, `WIN32`, `SYS16BIT`, `MAXSEG_64K`, `UNALIGNED_OK`, `STDC`, and `STDC99`. Core configuration includes `MAX_MEM_LEVEL`, `MAX_WBITS`, `OF`, `Z_ARG`, `FAR`, `ZEXTERN`, `ZEXPORT`, `ZEXPORTVA`, `Byte`, `uInt`, `uLong`, `Bytef`, `charf`, `intf`, `uIntf`, `uLongf`, `voidp` variants, `z_crc_t`, `z_off_t`, and `z_off64_t`.

Control flow: no runtime code, but extensive preprocessor control flow selects ABI and type definitions per compiler/platform. Large-file logic maps `_LARGEFILE64_SOURCE`, `_LFS64_LARGEFILE`, and `_FILE_OFFSET_BITS=64` to zlib's 64-bit offset types. MVS pragmas map long external names to linker-safe short names.

State and persistence: no mutable state. It defines compile-time configuration that persists into every object file including `zlib.h`; inconsistent compile flags across objects can create ABI mismatches.

Dependencies and integration points: included by `zlib.h` and therefore almost every zlib source. It conditionally includes system headers such as `limits.h`, `sys/types.h`, `stdarg.h`, `stddef.h`, and `unistd.h`. `deflate.c`, `inflate.c`, gz modules, and utility code all depend on its typedefs and macros.

Risks: changes can break binary compatibility, symbol names, DLL import/export behavior, large-file offsets, or 16-bit/FAR pointer support. Reducing `MAX_WBITS` or `MAX_MEM_LEVEL` affects compression compatibility and memory use. `Z_PREFIX` must be applied consistently across all zlib users to avoid link failures.

Test signals: build matrix across POSIX, Windows, large-file enabled/disabled, `Z_PREFIX`, `ZLIB_DLL`, `ZLIB_WINAPI`, `Z_SOLO`, and reduced memory/window settings. ABI checks should verify exported names and type sizes. Runtime tests should include gz seek/tell offsets and normal deflate/inflate after configuration changes.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/zlib/zconf.h -->
