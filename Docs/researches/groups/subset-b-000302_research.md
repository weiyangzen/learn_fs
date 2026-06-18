# subset-b-000302 Research

Grouped research for the listed zlib deflate implementation and gzip example utilities. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/deflate.c -->
# sources/compression/zlib/deflate.c

## Purpose
Implements zlib's DEFLATE compressor: public `deflate*()` entry points, stream initialization/reset/copy/destruction, wrapper generation for raw/zlib/gzip formats, LZ77 match finding, block selection, flush handling, and the level/strategy-specific compression loops. This is the main producer side of the `z_stream` API declared in `zlib.h`, with internal state supplied by `deflate.h` and Huffman emission delegated to `trees.c`.

## APIs, Types, And Functions
The public API surface includes `deflateInit_()`, `deflateInit2_()`, `deflate()`, `deflateEnd()`, `deflateReset()`, `deflateResetKeep()`, `deflateCopy()`, `deflateSetDictionary()`, `deflateGetDictionary()`, `deflateSetHeader()`, `deflatePending()`, `deflateUsed()`, `deflatePrime()`, `deflateParams()`, `deflateTune()`, `deflateBound_z()`, and `deflateBound()`. Internally, `block_state` represents compressor progress and `compress_func` dispatches to `deflate_stored()`, `deflate_fast()`, `deflate_slow()`, `deflate_rle()`, or `deflate_huff()`. `configuration_table` maps compression levels to lazy-match and chain-search parameters. Important helpers include `slide_hash()`, `read_buf()`, `fill_window()`, `lm_init()`, `longest_match()`, `flush_pending()`, and `putShortMSB()`.

## Control Flow
Initialization validates ABI version and stream size, installs allocators, normalizes level/window/mem/strategy options, allocates the sliding window, hash chains, head table, and pending/symbol buffer, then calls reset logic. `deflate()` validates state and flush mode, drains pending bytes, emits the selected wrapper header, then dispatches to the configured compressor loop. Stored mode copies data as uncompressed blocks, fast mode greedily emits matches/literals, slow mode performs lazy matching, RLE mode emits distance-one runs, and Huffman-only mode emits literals without match search. At flush boundaries `deflate()` emits alignment or empty stored blocks as required, and at `Z_FINISH` it writes the zlib Adler-32 or gzip CRC/ISIZE trailer.

## State And Persistence
All persistent compressor state lives in `deflate_state` behind `strm->state`: pending output, wrapper status, gzip header index, checksums, window/hash tables, match positions, lookahead, block start, Huffman buffers, bit buffer state, and tuning knobs. The state is memory-only and owned by the caller's `z_stream`; there is no filesystem persistence. `deflateCopy()` deep-copies allocated buffers and fixes tree descriptor pointers. `deflateSetDictionary()` seeds the window/hash history and updates the zlib preset dictionary checksum. `deflateParams()` can force a block boundary before changing strategy or compressor function.

## Dependencies And Integration
Depends on `deflate.h`, `zutil.h` utilities/macros, checksum routines (`adler32`, `crc32`, `crc32_z`), allocator hooks (`ZALLOC`, `ZFREE`), and tree functions `_tr_init()`, `_tr_tally*()`, `_tr_flush_block()`, `_tr_align()`, `_tr_stored_block()`, and `_tr_flush_bits()`. It integrates with public zlib callers through `z_stream` counters and buffers, and with gzip metadata through `gz_headerp` when `GZIP` is enabled. Compile-time options such as `FASTEST`, `LIT_MEM`, `NO_GZIP`, `UNALIGNED_OK`, `MAXSEG_64K`, and `ZLIB_DEBUG` materially change code paths.

## Risks And Test Signals
High-risk areas are bit-level wrapper/trailer transitions, pending-buffer overlap with symbol buffers, 16-bit portability branches, hash sliding, dictionary seeding, `deflatePrime()` buffer-space checks, and `deflateParams()` transitions after bytes have already been consumed. Match routines intentionally read guarded bytes past lookahead, relying on `high_water` zeroing for memory-checker cleanliness. Useful tests include zlib's compression/decompression round trips across all flush modes, raw/zlib/gzip wrapper tests, preset dictionary compatibility, tiny `avail_out` streaming, `deflateCopy()` equivalence, `deflateBound()` upper-bound checks, sanitizer runs, and gzip header/trailer validation.
<!-- END_FILE_RESEARCH: sources/compression/zlib/deflate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/deflate.h -->
# sources/compression/zlib/deflate.h

## Purpose
Defines the private compressor state and constants shared by `deflate.c` and `trees.c`. Applications are explicitly told not to include it; public users should use `zlib.h`. The header is the structural contract for zlib's compressor internals, including LZ77 window state, hash chains, Huffman trees, pending output, bit buffer accounting, gzip header progress, and compile-time layout variants.

## APIs, Types, And Macros
The file defines code-count constants (`LENGTH_CODES`, `LITERALS`, `L_CODES`, `D_CODES`, `BL_CODES`, `HEAP_SIZE`, `MAX_BITS`, `Buf_size`), stream status constants (`INIT_STATE`, optional `GZIP_STATE`, `EXTRA_STATE`, `NAME_STATE`, `COMMENT_STATE`, `HCRC_STATE`, `BUSY_STATE`, `FINISH_STATE`), `ct_data`, `tree_desc`, `Pos`, `IPos`, and the central `deflate_state`. Macros such as `put_byte()`, `MIN_LOOKAHEAD`, `MAX_DIST()`, `WIN_INIT`, `d_code()`, `_tr_tally_lit()`, and `_tr_tally_dist()` encode performance-critical assumptions. It declares tree integration functions `_tr_init()`, `_tr_tally()`, `_tr_flush_block()`, `_tr_flush_bits()`, `_tr_align()`, and `_tr_stored_block()`.

## Control Flow Role
The header has no executable control flow, but it defines the state machine values consumed by `deflate()` and the buffer layout consumed by both compressor and tree emitters. `deflate.c` advances `status` through wrapper/header, busy compression, and finish states. `trees.c` consumes the dynamic tree arrays, symbol buffers, heap, bit buffer, and pending buffer fields when constructing and emitting compressed blocks.

## State And Persistence
`deflate_state` is memory-resident stream state. It stores the caller back-pointer, pending output buffer and pointer, wrapper mode, gzip header pointer/index, compression parameters, sliding window, hash `head` and `prev` chains, match/lazy-match fields, Huffman trees, frequency/count heaps, symbol buffers (`sym_buf` or split `d_buf`/`l_buf` under `LIT_MEM`), debug counters, bit accumulator fields, `high_water` zeroing watermark, and the `slid` flag used for hash-copy correctness. There is no persistence outside the allocated `z_stream` state.

## Dependencies And Integration
Depends on `zutil.h` for zlib internal types, memory macros, and constants such as `MAX_MATCH` and `MIN_MATCH`. It conditionally enables gzip support unless `NO_GZIP` is defined. Its `_tr_tally_*` macros depend on `_length_code` and `_dist_code` exported by `trees.c` in non-debug builds. Because buffer overlays and symbol buffer offsets are encoded here, changes must be coordinated with `deflate.c` allocation and `trees.c` emission logic.

## Risks And Test Signals
Risks are structural: changing field order, buffer sizes, code constants, or tally macros can break ABI assumptions inside the library even though the header is private. The pending/symbol buffer overlay, `LIT_MEM` alternative layout, distance-code mapping, and `MAX_DIST()` limit are especially sensitive. Test signals should include full compressor/decompressor round trips at all levels and strategies, debug builds that route through `_tr_tally()`, builds with `NO_GZIP`, `FASTEST`, and `LIT_MEM`, and sanitizer coverage for window high-water behavior.
<!-- END_FILE_RESEARCH: sources/compression/zlib/deflate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/examples/enough.c -->
# sources/compression/zlib/examples/enough.c

## Purpose
Command-line analysis tool that exhaustively determines the maximum number of inflate Huffman table entries required for all valid complete prefix codes under a symbol count, root table width, and maximum code length. Defaults model the deflate literal/length code (`286`, root `9`, max `15`); `enough 30 6` models deflate distance codes.

## APIs, Types, And Functions
The program is standalone C using standard I/O and allocation. Core types are `big_t` for code counts, `code_t` for bit-pattern counts, `struct tab` for visited-state bit vectors, and `string_t` for accumulating printed maximum cases. Global `g` holds max/root/large/total, arrays for current code counts, memoized `num` counts, visited `done` states, and output text. Main helpers are `map()`, `cleanup()`, `count()`, `been_here()`, `examine()`, `enough()`, and the small `string_*` allocation helpers.

## Control Flow
`main()` parses optional numeric arguments, clamps unconstrained max length to `syms - 1`, validates integer-capacity limits, allocates memo tables, counts valid prefix codes for all symbol counts from two through `syms`, allocates visited-state tables, and runs `enough()`. `count()` recursively enumerates possible distributions of code lengths with memoization. `enough()` starts examination from reachable `root + 1` states, and `examine()` recursively tracks table memory (`mem`) and remaining entries (`rem`) to find and print all sub-codes that reach a new maximum.

## State And Persistence
All state is process-local heap memory referenced from the global `g`. `cleanup()` frees variable-size bit vectors, memo arrays, current code vectors, and output strings before exit. The tool persists no files and only writes human-readable counts and maximum cases to stdout; invalid arguments or impossible code spaces write diagnostics to stderr.

## Dependencies And Integration
Uses only libc headers and `assert()`. Its integration point with zlib is conceptual: it validates the table-size constants used by inflate's Huffman decode table builder, rather than linking against zlib. Results are used as engineering evidence for safe static table limits in the inflater.

## Risks And Test Signals
The main risks are combinatorial blow-up, unsigned overflow, and incorrect pruning. The code intentionally aborts on arithmetic or allocation failure via assertions and explicit checks. Test signals include running defaults, running `30 6`, comparing printed maxima to documented inflate table limits, testing boundary arguments (`2`, root greater than max, impossible symbol/max pairs), and compiling with sanitizers to catch `va_list`, allocation, and shift-bound issues.
<!-- END_FILE_RESEARCH: sources/compression/zlib/examples/enough.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/examples/fitblk.c -->
# sources/compression/zlib/examples/fitblk.c

## Purpose
Demonstrates how to produce a zlib stream that fits within a caller-specified compressed byte budget. It reads uncompressed data from stdin and writes a compressed stream to stdout, using multiple compression/decompression passes to land close to, but not over, the requested size.

## APIs, Types, And Functions
The program uses public zlib APIs `deflateInit()`, `deflate()`, `deflateReset()`, `deflateEnd()`, `inflateInit()`, `inflate()`, `inflateReset()`, and `inflateEnd()`. `partcompress()` compresses stdin into a bounded output buffer until either the buffer fills or input ends. `recompress()` inflates from an existing compressed buffer and recompresses into another bounded buffer. Constants `RAWLEN`, `EXCESS`, and `MARGIN` control intermediate buffering, the first-pass overrun allowance, and final completion slack.

## Control Flow
`main()` parses the target size, allocates `blk`, initializes a deflate stream, and performs a first compression pass into `size + EXCESS`. If all input already fits with at least `EXCESS` bytes spare, it writes the result directly. Otherwise it initializes inflate, resets deflate, recompresses the first overfilled stream into `tmp`, resets both streams, then recompresses only `size - MARGIN` bytes of that second stream into the final `size` buffer and asserts that the stream reaches `Z_STREAM_END`.

## State And Persistence
State is limited to stack buffers, two heap buffers (`blk`, `tmp`), and zlib stream state. There is no file persistence beyond stdin/stdout. `def.total_in` is used for reporting how much uncompressed input made it into the final stream. The program exits on errors via `quit()`.

## Dependencies And Integration
Depends on libc and `zlib.h`. It is an example of using zlib's streaming reset APIs and validates that zlib streams can be treated as intermediate bounded artifacts. It assumes the final consumer accepts a valid zlib-wrapped stream, not raw deflate or gzip.

## Risks And Test Signals
Risks include fragile empirical constants (`EXCESS`, `MARGIN`), assertion-based internal error handling, memory allocation failures, and poor results for very small requested sizes or unusual data. It does not guarantee exact fill, only `<= size`. Test signals are round-tripping the emitted stream with `inflate`, checking output length for many target sizes and data distributions, verifying behavior when input fits early, and running with read/write error injection.
<!-- END_FILE_RESEARCH: sources/compression/zlib/examples/fitblk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/examples/gun.c -->
# sources/compression/zlib/examples/gun.c

## Purpose
Implements a small gunzip/uncompress-style utility demonstrating `inflateBack()`. It decompresses gzip files, concatenated gzip members, and Unix `compress` LZW streams, optionally testing integrity only. It also copies metadata from compressed input files to decompressed output files and deletes source files on successful decompression.

## APIs, Types, And Functions
The gzip path uses `inflateBackInit()`, `inflateBack()`, `inflateBackEnd()`, and `crc32()`. `struct ind` and `in()` provide pull input callbacks. `struct outd` and `out()` provide push output callbacks with optional CRC/length accounting. The LZW path uses global prefix/suffix/match buffers and `lunpipe()`. `gunpipe()` parses gzip or LZW headers and trailers, `copymeta()` copies mode/ownership/timestamps, `gunzip()` opens/closes files and interprets zlib-style return codes, and `main()` handles suffix stripping and options.

## Control Flow
`main()` initializes a reusable `inflateBack` window, parses `-h` or `-t`, derives output names by removing gzip/compress suffixes, and invokes `gunzip()` for each file or stdin/stdout. `gunpipe()` scans for gzip magic bytes, branches to `lunpipe()` on Unix compress magic, otherwise parses gzip flags, inflates deflate payloads through callbacks, verifies CRC and length trailers, and loops for concatenated gzip members. `lunpipe()` decodes variable-width LZW codes, handles clear codes, rebuilds strings through prefix/suffix tables, and streams output through `out()`.

## State And Persistence
The program has large static buffers for input, output, LZW tables, and the inflateBack window. It persists decompressed files, may unlink original compressed files after success, and may unlink incomplete output files on failure. Metadata copy is best-effort. `strm->msg`, `strm->next_in`, `errno`, and return codes are used to distinguish data, read, write, and EOF failures.

## Dependencies And Integration
Depends on POSIX file APIs (`open`, `read`, `write`, `close`, `unlink`, `stat`, `chmod`, `chown`, `utime`) and `zlib.h`. It demonstrates low-level callback-driven inflate rather than `gz*` convenience APIs, and it intentionally supports concatenated gzip streams consistent with gzip behavior.

## Risks And Test Signals
Risks include destructive behavior on success/failure, suffix handling that assumes names are long enough for direct suffix comparisons, platform dependence on POSIX metadata calls, and LZW parser complexity around chunk boundaries and invalid codes. Test signals include gzip round trips, concatenated member tests, corrupt CRC/ISIZE tests, truncated input, trailing garbage behavior, `-t` no-write mode, LZW sample files, metadata preservation checks, and large-output files exceeding 4 GiB modulo trailer semantics.
<!-- END_FILE_RESEARCH: sources/compression/zlib/examples/gun.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/examples/gzappend.c -->
# sources/compression/zlib/examples/gzappend.c

## Purpose
Command-line utility that appends new uncompressed data to an existing gzip file by continuing the original raw deflate stream instead of creating another gzip member. It demonstrates `inflate(..., Z_BLOCK)`, unused-bit reporting, `deflateSetDictionary()`, and `deflatePrime()` for bit-exact deflate continuation.

## APIs, Types, And Functions
Uses public zlib APIs `inflateInit2(-15)`, `inflate(..., Z_BLOCK)`, `inflateEnd()`, `deflateInit2(-15)`, `deflateSetDictionary()`, `deflatePrime()`, `deflate()`, and `deflateEnd()`, plus `crc32()`. Local helpers include `gcd()` and `rotate()` for dictionary rotation, buffered `file` input helpers (`readin()`, `readmore()`, `skip()`, `read4()`), `gzheader()` for gzip header parsing, `gzscan()` to locate and clear the original final-block bit, and `gztack()` to append compressed data and write the new trailer.

## Control Flow
`main()` parses an optional compression level and target gzip file, calls `gzscan()` to validate and internally decompress the original gzip file, then appends named files or stdin through `gztack()`. `gzscan()` reads the gzip header, inflates raw deflate blocks while tracking block-boundary metadata from `data_type`, verifies the original trailer, warns that trailing junk will be overwritten, clears the final block bit in place, builds a dictionary from the last 32 KiB of uncompressed output, primes a new raw deflate stream with leftover bits, and returns the seeked file descriptor. `gztack()` compresses appended input and writes a new CRC/ISIZE trailer.

## State And Persistence
The utility mutates the target gzip file in place, overwriting its trailer and any trailing junk. It keeps the rolling CRC in `strm->adler` and total uncompressed size in `strm->total_in`. Failure after in-place modification can corrupt the target file, a limitation explicitly documented in the source. Temporary state is heap buffers plus zlib stream state.

## Dependencies And Integration
Depends on POSIX read/write/lseek APIs and `zlib.h`. It integrates with gzip format internals directly, not with zlib's `gzFile` abstraction. It requires zlib features introduced around 1.2.x: `Z_BLOCK` block-boundary return data and `deflatePrime()`.

## Risks And Test Signals
Risks are severe because writes are in-place and non-transactional. Bit-position handling (`lastbit`, `left`, `lastoff`, `end`) and dictionary rotation are correctness-critical. Tests should append to gzip files ending at different bit offsets, with and without extra/name/comment/header CRC fields, compare decompressed output to concatenated plaintext, validate CRC/ISIZE, test stdin and missing appended files, and simulate read/write errors to document corruption behavior.
<!-- END_FILE_RESEARCH: sources/compression/zlib/examples/gzappend.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/examples/gzjoin.c -->
# sources/compression/zlib/examples/gzjoin.c

## Purpose
Joins multiple gzip files into one gzip file whose decompressed data is the concatenation of the inputs, avoiding recompression and avoiding recalculating a full CRC over all uncompressed bytes. It demonstrates raw deflate block copying, clearing intermediate final-block bits, adding empty blocks for bit alignment, and `crc32_combine()`.

## APIs, Types, And Functions
Uses `inflateInit2(-15)`, `inflate(..., Z_BLOCK)`, `inflateEnd()`, `crc32()`, and `crc32_combine()`. `bin` wraps buffered input with `bopen()`, `bload()`, `bget()`, `bskip()`, and `bget4()`. `gzhead()` validates/skips gzip headers, `put4()` emits little-endian trailer words, `zpull()` feeds inflate, `gzinit()` writes a canonical output gzip header, and `gzcopy()` copies one gzip member's compressed payload into the joined output.

## Control Flow
`main()` writes a minimal gzip header with `gzinit()` and calls `gzcopy()` for each argument, passing `clr` true except for the final file. `gzcopy()` opens and header-skips an input gzip file, raw-inflates it using `Z_BLOCK` while writing consumed compressed bytes to stdout, clears the last-block bit on intermediate members, detects the next block's final bit at byte or bit offsets, inserts empty blocks to reach a byte boundary when needed, combines the input trailer CRC with the running CRC using the measured uncompressed length, and writes the final trailer only for the last input.

## State And Persistence
State is streaming and process-local: buffered input, a discard output buffer, zlib inflate state, running CRC, and modulo-32-bit total length. The only persistent output is stdout. Input files are read-only. The utility assumes input trailers are present and structurally usable but does not perform a full integrity check beyond header parsing and successful decompression.

## Dependencies And Integration
Depends on POSIX file reads/seeks and `zlib.h`. It integrates with gzip and raw deflate format details directly. `crc32_combine()` is the key zlib integration that avoids rereading or rechecksumming all already-compressed uncompressed data.

## Risks And Test Signals
Risks include incomplete input validation, bit-boundary mistakes when clearing final bits, empty-block insertion errors, unchecked stdout write failures in some paths, and reliance on trailer CRC/length fields from inputs. Test signals include joining one file, many files, files with stored/fixed/dynamic final blocks, files ending at every bit offset, corrupt/truncated inputs, and comparing output decompression and CRC to `cat plain... | gzip`.
<!-- END_FILE_RESEARCH: sources/compression/zlib/examples/gzjoin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/examples/gzlog.c -->
# sources/compression/zlib/examples/gzlog.c

## Purpose
Implements the crash-recoverable gzipped log object declared in `gzlog.h`. It optimizes frequent short appends by writing them as uncompressed deflate stored blocks in a valid gzip file, then periodically recompressing accumulated stored data with a 32 KiB dictionary to preserve compression ratio. It also recovers interrupted append, compress, and dictionary-replacement operations.

## APIs, Types, And Functions
External APIs are `gzlog_open()`, `gzlog_write()`, `gzlog_compress()`, and `gzlog_close()`. Internal `struct log` stores the magic id, open `.gz` descriptor, path buffer, offsets to first/last stored blocks, bit-back offset, stored length, compressed and total CRC/lengths, and lock timestamp. Major helpers include lock management (`log_lock()`, `log_touch()`, `log_check()`, `log_unlock()`), gzip extra-field parsing and marking (`log_head()`, `log_mark()`), stored-block repair (`log_last()`), operations (`log_append()`, `log_compress()`, `log_replace()`), recovery logging (`log_log()`), `log_recover()`, `log_close()`, and `log_open()`.

## Control Flow
`gzlog_open()` allocates a log object, creates/acquires `path.lock`, initializes `path.gz` if empty, reads the custom gzip extra field, and recovers any marked operation. `gzlog_write()` writes the new payload to `path.add`, marks `APPEND_OP`, appends stored-block data, updates trailer and extra field to `NO_OP`, deletes `.add`, then triggers `gzlog_compress()` when stored data reaches `TRIGGER`. `gzlog_compress()` reads stored blocks into memory, writes `.add` and `.temp`, marks `COMPRESS_OP`, recompresses stored data over the previous stored region using `.dict` if available, writes a valid trailer, marks `REPLACE_OP`, replaces `.dict` with `.temp`, and finally marks `NO_OP`. `log_recover()` resumes based on the operation bits in the extra field.

## State And Persistence
Persistence spans several files sharing the path prefix: `path.gz` is always intended to be a valid gzip log after successful public calls; `path.add` stores append/compress payload for recovery; `path.dict` stores the previous 32 KiB dictionary; `path.temp` stores the next dictionary during compression; `path.lock` gates exclusive access and stale-lock handling; `path.repairs` records recovery events. The gzip extra field is the transaction marker and contains offsets, CRCs, lengths, stored-block length, bit-back position, and operation code. The code assumes the extra-field rewrite is effectively atomic due to its small fixed location near the file start.

## Dependencies And Integration
Depends on POSIX file APIs (`open`, `read`, `write`, `lseek`, `ftruncate`, `fsync`, `rename`, `unlink`, `stat`, `utimes`, `sleep`), libc time/reporting routines, and zlib `crc32`, raw `deflateInit2(-15)`, `deflateSetDictionary()`, `deflatePrime()`, `deflate()`, and `deflateEnd()`. The custom gzip header includes an `ap` extra subfield; non-gzlog gzip files are rejected by header comparison.

## Risks And Test Signals
Critical risks are transaction ordering, stale lock races, partial writes despite `fsync`, large in-memory compression of stored data, path suffix mutation through a shared buffer, and correctness of raw deflate bit priming/replacement. Missing `.add` during recovery can intentionally lose the interrupted append/compress data while restoring a valid gzip. Test signals include interruption injection via `GZLOG_DEBUG`, concurrent writer lock contention, stale lock expiry, disk-full behavior, recovery from each operation state, verification that `gunzip path.gz` succeeds after every public call, repeated compression thresholds, and dictionary replacement with missing `.temp` or `.dict`.
<!-- END_FILE_RESEARCH: sources/compression/zlib/examples/gzlog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/examples/gzlog.h -->
# sources/compression/zlib/examples/gzlog.h

## Purpose
Public header for the gzlog example library. It defines an opaque `gzlog` object and documents an append-oriented gzip log abstraction that remains decompressible after successful writes and can recover from interrupted operations on the next open.

## APIs, Types, And Functions
The only type is `typedef void gzlog`, intentionally opaque to callers. Declared functions are `gzlog_open(char *path)`, `gzlog_write(gzlog *log, void *data, size_t len)`, `gzlog_compress(gzlog *log)`, and `gzlog_close(gzlog *log)`. Return conventions are documented: open returns `NULL` on error; write/compress return `0`, `-1` for file I/O, `-2` for allocation, or `-3` for invalid log; close returns `0` or `-3`.

## Control Flow Role
This header has no executable flow, but it defines the lifecycle contract: open creates/locks/recovers the log, write appends data and may trigger compression, optional compress forces stored data recompression, and close releases the lock and frees the object. It also documents that `gzlog_open()` followed by `gzlog_close()` is enough to recover a previously interrupted operation.

## State And Persistence
The header documents all persistent side files: `path.gz`, `path.dict`, `path.temp`, `path.add`, `path.lock`, and `path.repairs`. It promises that successful writes leave the gzip file valid and that stored uncompressed data is compressed after about 1 MiB. The opaque handle is freed by `gzlog_close()` and must not be reused.

## Dependencies And Integration
Consumers include this header and link with `gzlog.c` and zlib. The declaration uses `size_t` but does not include `<stddef.h>` itself, so callers must include a header that defines `size_t` before or through their compilation context. The API is C-style and mutable; `path` is a prefix for generated files, not necessarily the final `.gz` path.

## Risks And Test Signals
Risks are mostly contract-level: callers may misunderstand the prefix path, reuse a closed object, pass invalid pointers, or force compression too frequently and harm ratio/performance. Header-level tests are compile tests from a minimal C consumer, invalid-handle return-code checks, and lifecycle tests that validate every documented auxiliary file behavior through `gzlog.c`.
<!-- END_FILE_RESEARCH: sources/compression/zlib/examples/gzlog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/examples/gznorm.c -->
# sources/compression/zlib/examples/gznorm.c

## Purpose
Normalizes a gzip stream from stdin to stdout into a single gzip member with a canonical header. It removes original names, timestamps, comments, extra fields, and per-member headers/trailers while preserving compressed deflate blocks without recompressing. It also makes repeated normalization idempotent by excising an existing final empty fixed block when present.

## APIs, Types, And Functions
Uses public zlib APIs `inflateInit2(15 + 16)`, `inflate(..., Z_BLOCK)`, `inflateReset()`, `inflateEnd()`, and `crc32_combine()`. `aprintf()` allocates formatted error strings, `BYE` centralizes cleanup/error return, and `gzip_normalize()` performs all transformation. `main()` sets binary mode where needed and calls `gzip_normalize(stdin, stdout, &err)`.

## Control Flow
`gzip_normalize()` writes a fixed ten-byte gzip header, then drives `inflate()` in `Z_BLOCK` mode over chunks of input. A small state machine moves through `BETWEEN`, `HEAD`, `BLOCK`, and `TAIL`. Headers are discarded. In `BLOCK`, consumed compressed bytes are copied to output while a bit buffer clears last-block bits, aligns stored-block headers to byte boundaries, strips final empty fixed blocks, and carries trailing bits between members. In `TAIL`, the member CRC and length are accumulated; CRCs are combined with `crc32_combine()` using the actual uncompressed member length. At EOF it verifies state, writes a terminating empty fixed block, writes the combined trailer, flushes output, and reports I/O errors.

## State And Persistence
State is streaming and local: inflate state, gzip state enum, accumulated CRC/length, bit buffer (`buf`/`num`), per-member uncompressed length, and partial trailer state. The utility persists only stdout output. It handles empty input by emitting an empty canonical gzip stream.

## Dependencies And Integration
Depends on libc I/O/allocation/error reporting and zlib gzip-aware inflate. On DOS/Windows-style platforms it switches stdin/stdout to binary mode. It operates on gzip and deflate bitstream internals directly rather than using `gzFile`; the output is intended to be accepted by standard gzip decompressors.

## Risks And Test Signals
Risks include subtle bit-buffer bugs across member boundaries, incorrect `data_type` interpretation, CRC combination overflow checks, partial trailer handling across input chunks, and I/O error reporting after buffered writes. Test signals include normalizing empty input, one-member and multi-member gzip streams, streams with all optional header fields, every deflate block type, members ending at varied bit offsets, idempotence (`gznorm | gznorm` unchanged), corrupt/truncated inputs, and binary-mode smoke tests on Windows-like platforms.
<!-- END_FILE_RESEARCH: sources/compression/zlib/examples/gznorm.c -->
