# Group Research: group_49_9front_sources_os_plan9_9front_sys_src_cmd_audio_libogg_bitwise_c_sou_2661436dc9a4

Scope confirmed against `Docs/research_subset_a.md`: `sources/os/plan9/9front` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libogg/bitwise.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libogg/bitwise.c

## Role

This is the libogg bit packing implementation vendored into 9front's audio command tree. It implements variable-width bitstream read/write operations over `oggpack_buffer`, in both least-significant-bit-first (`oggpack_*`) and most-significant-bit-first (`oggpackB_*`) variants.

This is codec/container infrastructure rather than filesystem code, but it is in scope through the included 9front source tree.

## Main Interfaces

The file implements the bitstream API declared in `ogg/ogg.h`:

- Write lifecycle: `oggpack_writeinit`, `oggpack_writecheck`, `oggpack_writetrunc`, `oggpack_writealign`, `oggpack_writecopy`, `oggpack_reset`, `oggpack_writeclear`.
- Read lifecycle: `oggpack_readinit`, `oggpack_look`, `oggpack_look1`, `oggpack_adv`, `oggpack_adv1`, `oggpack_read`, `oggpack_read1`.
- Position/buffer access: `oggpack_bytes`, `oggpack_bits`, `oggpack_get_buffer`.
- MSB-first mirrors: `oggpackB_*`.

The `mask[]` table provides bit masks from 0 to 32 bits; `mask8B[]` supports MSB truncation of partially filled bytes.

## Implementation Notes

`oggpack_write()` and `oggpackB_write()` accept up to 32 bits, expand storage in `BUFFER_INCREMENT` chunks, mask the input value, merge it into the current byte at `endbit`, and update `endbyte`, `endbit`, and `ptr`.

`oggpack_writecopy_helper()` supports copying arbitrary bit counts from a byte source. It uses direct `memmove` for byte-aligned copies and falls back to repeated 8-bit writes for unaligned copies. Trailing partial bytes are written with the selected bit order.

The read-side functions use `look` for non-advancing reads and `read` for advancing reads. On overflow or invalid bit counts they poison the buffer state by setting `ptr` to `NULL`, `endbyte` to `storage`, and `endbit` to `1`, then return `-1`.

## Error Handling and Risks

Allocation failures and oversized growth requests clear the write buffer with `oggpack_writeclear()`. Callers must treat a failed or cleared buffer as unusable until reinitialized.

The implementation relies on careful boundary checks before reading up to five bytes around `ptr`; these checks are central to avoiding overreads near the end of small buffers.

## Test Code

Under `_V_SELFTEST`, the file includes a large standalone test program covering:

- LSb and MSb packing.
- Fixed and inferred bit-width writes.
- Single-bit reads.
- Read-past-end behavior.
- Aligned and unaligned `writecopy` paths around allocation boundaries.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libogg/bitwise.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libogg/framing.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libogg/framing.c

## Role

This is the libogg framing layer. It turns raw packets into Ogg pages on encode and reconstructs packets from pages on decode. It also implements page metadata accessors, CRC calculation, sync/recovery scanning, logical stream state, and packet extraction.

It is user-space audio container code, not filesystem code.

## Page Helpers

The file provides simple accessors over `ogg_page` headers:

- `ogg_page_version`
- `ogg_page_continued`
- `ogg_page_bos`
- `ogg_page_eos`
- `ogg_page_granulepos`
- `ogg_page_serialno`
- `ogg_page_pageno`
- `ogg_page_packets`

`ogg_page_checksum_set()` computes the Ogg CRC using the static `crc_lookup[256]` table. It zeroes bytes 22-25 before checksumming and then writes the checksum back in little-endian order.

## Encoding Flow

`ogg_stream_init()` allocates an `ogg_stream_state` with body storage, lacing storage, and granule-position storage. `_os_body_expand()` and `_os_lacing_expand()` grow these internal FIFOs defensively.

Packets enter via `ogg_stream_iovecin()` or `ogg_stream_packetin()`:

1. Returned body bytes are compacted.
2. Packet body bytes are copied into `body_data`.
3. Packet length is split into 255-byte lacing values.
4. The first lacing segment is marked with `0x100` for beginning-of-packet.
5. Granule positions and EOS status are recorded.

Pages are produced through `ogg_stream_pageout()`, `ogg_stream_pageout_fill()`, `ogg_stream_flush()`, and `ogg_stream_flush_fill()`, all using `ogg_stream_flush_i()` internally. The flush logic builds the Ogg page header, writes flags for continued/BOS/EOS, serial number, page number, granule position, segment table, body pointer, and CRC.

## Decode and Sync Flow

`ogg_sync_state` buffers raw bytes from an application. The caller obtains writable space through `ogg_sync_buffer()`, fills it, then calls `ogg_sync_wrote()`.

`ogg_sync_pageseek()` searches for a complete valid Ogg page at the current returned offset:

- Validates the `OggS` capture pattern.
- Waits until the fixed header, segment table, and full body are buffered.
- Verifies the page CRC.
- Returns the page through pointers into `ogg_sync_state` storage.
- On sync failure, scans forward to the next possible `O` capture byte and returns a negative skip count.

`ogg_sync_pageout()` wraps this into the public `-1`, `0`, `1` sync API.

## Stream Page Input

`ogg_stream_pagein()` accepts a validated page for a matching serial number. It:

- Compacts returned lacing/body data.
- Rejects serial mismatches and future Ogg versions.
- Detects missing page numbers and inserts a `0x400` hole marker.
- Handles continued-packet pages by skipping orphaned leading segments when needed.
- Copies page body bytes into stream body storage.
- Appends lacing values and granule positions.
- Marks EOS on the final segment when present.

`ogg_stream_packetout()` and `ogg_stream_packetpeek()` share `_packetout()`, which groups lacing segments into complete packets, reports holes as `-1`, and advances or peeks according to the caller's mode.

## State Reset and Cleanup

The file implements `ogg_stream_clear`, `ogg_stream_destroy`, `ogg_stream_reset`, `ogg_stream_reset_serialno`, `ogg_stream_check`, `ogg_stream_eos`, `ogg_sync_clear`, `ogg_sync_destroy`, `ogg_sync_reset`, and `ogg_sync_check`.

`ogg_packet_clear()` frees packet memory and zeroes the packet object; most packets returned by stream APIs point into stream storage and should not be blindly freed unless ownership came from an allocating API.

## Risks and Edge Cases

The critical correctness areas are lacing FIFO accounting, page loss recovery, continued-packet handling, and CRC validation. The code uses sentinel bits in `lacing_vals`: `0x100` for BOS packet, `0x200` for EOS, and `0x400` for stream holes.

Large packets spanning many pages and pages at the 255-segment limit are explicitly handled and self-tested.

## Test Code

Under `_V_SELFTEST`, the file contains an extensive standalone framing test suite. It validates page headers, packet order, page loss behavior, continuation behavior, sync on partial input, recapture after garbage, checksum behavior, and very large packets.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libogg/framing.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libogg/ogg/ogg.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libogg/ogg/ogg.h

## Role

This is the public libogg header used by the vendored Ogg implementation and codec users in the 9front audio tree. It defines Ogg data structures and declares the bit packing, stream framing, sync, page, and packet APIs.

It also includes a Plan 9 `#pragma lib` for linking `/sys/src/cmd/audio/libogg/libogg.a$O`.

## Main Types

The header defines:

- `ogg_iovec_t`: base pointer plus length for vectorized packet input.
- `oggpack_buffer`: bitstream packing state, including current byte/bit offsets, buffer pointer, and storage size.
- `ogg_page`: header/body pointer pair for an Ogg page.
- `ogg_stream_state`: logical stream encode/decode state, including body FIFO, lacing FIFO, granule positions, page counter, packet counter, serial number, and BOS/EOS state.
- `ogg_packet`: packet pointer plus length, BOS/EOS flags, granule position, and packet number.
- `ogg_sync_state`: raw byte sync buffer and page-discovery state.

## API Surface

The declarations are grouped as:

- Bitstream primitives: `oggpack_*` and `oggpackB_*`.
- Encoding primitives: packet input and page output/flush.
- Decoding primitives: sync buffer/pageout, stream pagein, packetout/peek.
- General stream lifecycle: init, clear, reset, reset serial number, destroy, check, EOS.
- Page helpers: checksum, flags, granule position, serial number, page number, packet count.
- Packet cleanup: `ogg_packet_clear()`.

## Dependencies

The file includes `stddef.h` and `ogg/os_types.h`. Memory allocation is abstracted by macros in `os_types.h`, while integer aliases are defined there.

## Integration Notes

This header is consumed by `bitwise.c`, `framing.c`, libvorbis, and other audio code that needs Ogg packet/page handling. Its structures are public and ABI-sensitive; changes to layout affect all linked users.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libogg/ogg/ogg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libogg/ogg/os_types.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libogg/ogg/os_types.h

## Role

This small header provides libogg platform type aliases and allocator macros for the 9front vendored build.

## Definitions

It maps allocator hooks directly to libc:

- `_ogg_malloc` -> `malloc`
- `_ogg_calloc` -> `calloc`
- `_ogg_realloc` -> `realloc`
- `_ogg_free` -> `free`

It defines fixed-width-style integer names used by libogg:

- `ogg_int16_t`, `ogg_uint16_t`
- `ogg_int32_t`, `ogg_uint32_t`
- `ogg_int64_t`

## Integration Notes

The header assumes the included environment already provides declarations for the allocator functions through surrounding includes. It is included by `ogg.h`, which then exposes these types to libogg users.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libogg/ogg/os_types.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/437.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/437.c

## Role

This file converts Code Page 437 encoded metadata strings to UTF-8 for module/audio tag parsers.

## Main Interface

`cp437toutf8(uchar *o, int osz, const uchar *s, int sz)` converts up to `sz` input bytes into the output buffer, stopping at NUL, output exhaustion, or input exhaustion. It always NUL-terminates the output.

## Implementation Notes

Bytes below 127 are copied as ASCII. Bytes 127 and above are mapped through the static `Rune rh[129]` table and emitted with Plan 9 `runetochar()`.

The output buffer must be large enough for worst-case UTF-8 expansion; `tagspriv.h` documents `sz*4+1` as safe for CP437 conversion.

## Risks

The conversion stops if the next Rune would not fit in the output buffer. Callers use the return value as the number of source bytes consumed, not the number of output bytes written.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/437.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/8859.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/8859.c

## Role

This file converts ISO-8859-1 metadata strings to UTF-8 for ID3 and related tag parsers.

## Main Interface

`iso88591toutf8(uchar *o0, int osz, const uchar *s, int sz)` reads up to `sz` bytes, stops at NUL or output exhaustion, writes UTF-8, and NUL-terminates the output.

## Implementation Notes

ASCII is copied directly. Bytes `0xA0`-`0xBF` are emitted as `0xC2 xx`; bytes `0xC0` and above are emitted as `0xC3 (byte - 0x40)`.

If bytes in `0x7F`-`0x9F` appear, the function falls back to copying the original byte string as-is, with a FIXME noting that this can cut through UTF-8 character boundaries.

## Risks

The fallback path is intentionally permissive for unexpected control bytes but may preserve invalid text encoding. It is metadata-facing and not used for binary payloads.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/8859.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/flac.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/flac.c

## Role

This file extracts basic stream information, Vorbis comments, and embedded pictures from FLAC files.

## Main Interface

`tagflac(Tagctx *ctx)` is the FLAC parser called by `tagsget()`.

## Parsing Flow

The parser expects the FLAC marker and first metadata block at the beginning of the stream. It reads the STREAMINFO block, sets:

- `ctx->samplerate`
- `ctx->channels`
- `ctx->duration`

It then iterates FLAC metadata blocks until the last-block flag is seen.

For block type `6` PICTURE, it reads image type, MIME length, description length, image metadata, and image data size, then calls `tagscallcb()` with `Timage`, MIME type, file offset, and image size.

For block type `4` VORBIS_COMMENT, it skips the vendor string, reads the comment count, reads each `key=value` entry that fits in `ctx->buf`, trims a trailing carriage return, and dispatches through `cbvorbiscomment()`.

Other metadata blocks are skipped.

## Dependencies

The file uses endian helpers from `tagspriv.h`, the shared Vorbis comment mapper in `vorbis.c`, and the callback helpers from `tags.c`.

## Risks

The parser is intentionally small and mostly linear. It validates sizes against remaining block length and buffer size, but malformed metadata can still cause an early `-1` rather than partial recovery.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/flac.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/id3genres.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/id3genres.c

## Role

This file defines the ID3 genre lookup table used by ID3v1, ID3v2 genre parsing, and M4A numeric genre parsing.

## Main Data

`const char *id3genres[Numgenre]` contains 192 genre names. The table starts with the classic ID3v1 genres such as Blues, Classic Rock, Country, and Dance, and includes later Winamp-style extensions through entries such as Podcast, Indie Rock, G-Funk, Dubstep, Garage Rock, and Psybient.

## Integration

The table is declared in `tagspriv.h` and indexed by:

- `tagid3v1()` for byte 127 of an ID3v1 tag.
- `v2cb()` in `id3v2.c` for numeric `TCON`/genre values.
- `tagm4a()` for non-text `gnre` atoms.

## Risks

Callers must bounds-check indexes against `Numgenre`; the in-tree callers do so before indexing.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/id3genres.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/id3v1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/id3v1.c

## Role

This file parses ID3v1 tags from the last 128 bytes of MP3 files.

## Main Interface

`tagid3v1(Tagctx *ctx)` seeks to `-128` from EOF, verifies the `TAG` marker, and extracts title, artist, album, date, comment, track, and genre.

## Parsing Details

It requires `ctx->bufsz >= 189` so the 128-byte input and a 61-byte conversion output can coexist in `ctx->buf`.

Fields are decoded as ISO-8859-1:

- Title: bytes 3-32.
- Artist: bytes 33-62.
- Album: bytes 63-92.
- Date: bytes 93-96.
- Comment: starts at byte 97.
- Track: ID3v1.1 layout when byte 125 is zero and byte 126 is nonzero.
- Genre: byte 127, mapped through `id3genres`.

The parser respects tags already found by ID3v2 by checking `ctx->found` before emitting overlapping fields.

## Risks

The comment field handling is minimal and depends on NUL placement in the buffer. The parser is deliberately tolerant because ID3v1 data is often loosely formatted.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/id3v1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/id3v2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/id3v2.c

## Role

This file parses ID3v2 tags and derives MP3 stream duration/TOC metadata when possible.

## Main Interface

`tagid3v2(Tagctx *ctx)` is the ID3v2/MP3 parser called by `tagsget()`.

## Tag Mapping

`v2cb()` maps ID3 frame keys to libtags tag types. It recognizes album, artist, album artist, title, date/year, track, length, composer, genre, comment, and ReplayGain-style `TXXX` frames. Unknown text frames are emitted as `Tunknown`.

Genre parsing handles numeric parenthesized genre values by indexing `id3genres`, while also accepting plain-text genres.

## Text and Binary Frames

`text()` reads a text frame into the end of `ctx->buf`, applies unsynchronization removal when needed, decodes by encoding byte, and dispatches through `v2cb()`:

- `0`: ISO-8859-1.
- `1` and `2`: UTF-16.
- `3`: UTF-8.

`nontext()` handles:

- `APIC`: ID3v2 attached picture, reporting MIME type, image offset, size, and optional unsync read filter.
- `PIC`: ID3v2.2 picture frame, mapping `JPG` to JPEG and otherwise using PNG.
- `RVA2`: replay gain data via `rva2()`.

`resync()` and `unsyncread()` remove ID3 unsynchronization byte stuffing.

## Header and Frame Parsing

`isid3()` validates the ID3 header and synchsafe size bytes. `tagid3v2()` supports v2.2, v2.3, and v2.4 frame layouts:

- Handles global unsynchronization.
- Rejects unsupported v2.2 compression.
- Skips v2.3/v2.4 extended headers.
- Accounts for v2.4 footers.
- Skips compressed/encrypted frames.
- Skips v2.4 data length indicators.
- Stops on padding.

After one tag is parsed, it scans ahead up to 2048 bytes for chained ID3 headers and MP3 frame sync.

## MP3 Duration and TOC

`getduration()` reads an MPEG audio header, sets bitrate, sample rate, and channel count from static lookup tables, and estimates duration. It recognizes Xing/Info and VBRI headers. If a Xing TOC is present and `ctx->toc` is configured, it emits approximate millisecond-to-byte offsets.

As fallback, it estimates duration from file size and bitrate.

## Risks

ID3v2 is highly variable. This parser is defensive and compact, but not exhaustive. It ignores frames that do not fit in the working buffer, skips unsupported compression/encryption, and has FIXME notes around image unsync streaming and UTF-8 boundary handling in lower-level converters.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/id3v2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/it.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/it.c

## Role

This file extracts the title from Impulse Tracker module files.

## Main Interface

`tagit(Tagctx *ctx)` reads the `IMPM` signature plus the 26-byte song name. If the signature matches, it converts the title from ISO-8859-1 to UTF-8 and emits `Ttitle`.

## Risks

The parser only identifies the format and title. It does not parse duration, channels, instruments, or other module metadata.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/it.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/m4a.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/m4a.c

## Role

This file parses M4A/QuickTime-style atoms for audio metadata, stream parameters, duration, track number, genre, and cover art.

## Main Interface

`tagm4a(Tagctx *ctx)` is the M4A parser called by `tagsget()`.

## Container Traversal

The parser expects an `ftypM4A ` atom at the start. It then walks atoms by size and type. For container atoms such as `udta`, `ilst`, `trak`, `mdia`, `minf`, `moov`, and `stbl`, it descends by resetting the skip size to zero. For `meta`, it skips the four metadata flags/version bytes.

## Metadata Atoms

It maps common atoms to tag types:

- `©nam`: title.
- `©alb`: album.
- `©ART`: artist.
- `aART`: album artist.
- `©gen` and `gnre`: genre.
- `©day`: date.
- `covr`: image.
- `trkn`: track.
- `©wrt`: composer.
- `©cmt`: comment.

Text payloads with data type `1` are read into `ctx->buf` and emitted directly. Numeric genres are mapped through `id3genres`. JPEG and PNG covers are reported as `Timage` with file offset and size.

## Stream Metadata

For `stsd` sample descriptions, the parser reads `mp4a` entries and sets `ctx->channels` and `ctx->samplerate`.

For `mdhd`, it handles version 0 and a version-1-like path, reading timescale and duration fields and setting `ctx->duration` in milliseconds.

## Risks

The atom walker is simple and assumes atom sizes are sane. Some unsupported atoms are skipped silently. Large text atoms that do not fit in `ctx->buf` are skipped.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/m4a.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/mod.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/mod.c

## Role

This file detects ProTracker-style MOD module files and extracts their title.

## Main Interface

`tagmod(Tagctx *ctx)` seeks to offset 1080, reads the 4-byte module signature, compares it with a static list of known variants, then returns to the beginning and reads the 20-byte title.

## Format Detection

Recognized signatures include `M.K.`, `M!K!`, `M&K!`, `N.T.`, `NSMS`, `FLT4`, `FLT8`, `CD81`, `OCTA`, `OKTA`, `4CHN`, `6CHN`, `8CHN`, `10CH`, `16CN`, `32CN`, and a few NUL-padded variants.

## Output

The title is converted from CP437 to UTF-8 and emitted as `Ttitle`.

## Risks

This parser only checks a signature and title. It does not validate full module structure, so detection depends on the uniqueness of the signature at offset 1080.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/mod.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/opus.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/opus.c

## Role

This file parses Ogg Opus headers, OpusTags comments, and approximate stream duration.

## Main Interface

`tagopus(Tagctx *ctx)` is the Opus parser called by `tagsget()`.

## Header and Tag Parsing

The parser reads the first two Ogg pages manually. It validates the `OggS` capture pattern, reads segment counts and lacing bytes, and detects:

- `OpusHead`: validates version 1, sets channel count from byte 1, and reads the input sample rate field.
- `OpusTags`: records the end of the tag packet and breaks into comment parsing.

It then reads the vendor length, skips the vendor string, reads the comment count, and parses `key=value` strings through `cbvorbiscomment()`.

The file has a FIXME noting embedded pictures can make tags span multiple packets; it stops when a comment would exceed the recorded packet end.

## Duration

If sample rate was identified, the parser scans near the beginning to find the first Ogg page granule position and near EOF to find a later page granule position. It computes duration using Opus's fixed 48 kHz granule position clock.

## Risks

This is a lightweight parser and does not use libogg. It assumes the initial headers and tags are in the first few pages and does not fully support multi-packet embedded pictures.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/opus.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/s3m.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/s3m.c

## Role

This file extracts the title from Scream Tracker 3 module files.

## Main Interface

`tags3m(Tagctx *ctx)` reads the 28-byte title plus two signature/control bytes. It accepts byte 28 as `0x1a` or zero and requires byte 29 to be `0x10`.

## Output

Trailing spaces and NULs are trimmed. The title is converted from CP437 to UTF-8 and emitted as `Ttitle`.

## Risks

The parser performs minimal validation. It does not parse the `SCRM` marker later in the S3M header, so it relies on the initial byte checks used here.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/s3m.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/tags.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/tags.c

## Role

This file is the dispatcher and common callback wrapper for libtags.

## Parser Dispatch

`tagsget(Tagctx *ctx)` initializes output fields and tries each parser in order:

1. ID3v2 / MP3.
2. ID3v1.
3. Vorbis.
4. FLAC.
5. M4A.
6. Opus.
7. WAV.
8. IT.
9. XM.
10. S3M.
11. MOD.

If a parser returns success, `ctx->format` is set to that parser's format and the overall result becomes success. After each parser attempt, the input is seeked to `ctx->restart`.

This means multiple parsers may contribute, notably ID3v2 and ID3v1 for MP3.

## Callback Wrapper

`tagscallcb()` trims leading/trailing ASCII control/space characters for normal string tags, invokes `ctx->tag()`, and updates `ctx->found` plus `ctx->num` for known tag types.

Binary tags such as images pass offset/size and optional stream filter function and are not string-trimmed.

## Risks

The dispatcher assumes the caller-provided `read`, `seek`, and `tag` callbacks are valid. It uses `ctx->restart` to coordinate parser chaining; individual parsers are responsible for setting that correctly when they consume leading metadata.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/tags.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/tags.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/tags.h

## Role

This is the public libtags API header for 9front audio metadata parsing. It declares tag types, format identifiers, `Tagctx`, and `tagsget()`.

It includes a Plan 9 `#pragma lib` for `/sys/src/cmd/audio/libtags/libtags.a$O`.

## Public Types

`Tagctx` contains caller-provided callbacks:

- `read(ctx, buf, cnt)`
- `seek(ctx, offset, whence)`
- `tag(ctx, type, key, string, image_offset, image_size, filter)`
- optional `toc(ctx, ms, offset)`

It also carries caller auxiliary data, a working buffer, output stream fields, and private parser state.

`Tagread` is a filter callback type used for binary image payloads that require transformation while reading.

## Tag Types

Known tag types include artist, album, title, date, track, album/track gain and peak, genre, image, composer, comment, and album artist. `Tunknown` is `-1`.

The gain note warns that ReplayGain/R128 values may not always be simple `dB` strings; callback consumers must inspect the raw key.

## Format Types

Format identifiers include MP3, Vorbis, FLAC, M4A, Opus, WAV, IT, XM, S3M, MOD, plus unknown.

## Integration Notes

Callers must allocate `ctx->buf` with at least 256 bytes before calling `tagsget()`. After parsing, `channels`, `samplerate`, `bitrate`, `duration`, and `format` may be populated.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/tags.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/tagspriv.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/tagspriv.h

## Role

This private header centralizes libtags internal dependencies, endian helpers, charset converters, shared callbacks, and parser declarations.

## Main Definitions

It includes Plan 9 headers `<u.h>` and `<libc.h>`, then the public `tags.h`.

It defines:

- `Numgenre = 192`.
- `beuint(d)` and `leuint(d)` 32-bit endian macros.
- `id3genres` external table.

## Internal Helpers

Declared helpers include:

- `iso88591toutf8()`
- `utf16to8()`
- `cp437toutf8()`
- `cbvorbiscomment()`
- `tagscallcb()`
- `txtcb()` macro for normal text callbacks.

## Parser Declarations

It declares all format parser functions used by `tags.c`: FLAC, ID3v1, ID3v2, IT, M4A, Opus, S3M, Vorbis, WAV, XM, and MOD.

## Integration Notes

This header is the internal coupling point for all libtags implementation files. Changes to `Tagctx` public fields or helper semantics affect every parser.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/tagspriv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/utf16.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/utf16.c

## Role

This file converts UTF-16 metadata strings to UTF-8 for ID3v2 and related parsers.

## Main Interface

`utf16to8(uchar *o, int osz, const uchar *s, int sz)` converts up to `sz` input bytes and NUL-terminates output. It returns bytes consumed or `-1` on malformed surrogate pairs.

## Implementation Notes

The converter defaults to big-endian unless a BOM is present:

- `FE FF`: big-endian, skipped.
- `FF FE`: little-endian, skipped.

It decodes 16-bit code units, validates surrogate pairs, forms code points up to four-byte UTF-8, computes output width, and writes UTF-8 manually using the `mark[]` prefix table.

## Risks

The function assumes at least two input bytes when checking a BOM. In-tree callers use it with frame payloads large enough for text encoding markers. It stops before output overflow and leaves a valid NUL-terminated string.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/utf16.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/vorbis.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/vorbis.c

## Role

This file parses Vorbis comments from Ogg Vorbis files, maps Vorbis comment keys to libtags tag types, extracts basic stream parameters, and estimates duration.

## Shared Comment Mapping

`cbvorbiscomment(Tagctx *ctx, char *k, char *v)` maps case-insensitive keys such as `album`, `title`, `artist`, `tracknumber`, `date`, ReplayGain/R128 keys, `genre`, `composer`, `comment`, `albumartist`, and `album artist`.

Unknown non-empty keys are emitted as `Tunknown`.

This mapper is also used by FLAC and Opus parsers.

## Vorbis Parsing

`tagvorbis(Tagctx *ctx)` manually reads the first Ogg pages. It looks for:

- Identification packet (`type == 1`): reads channels, sample rate, and bitrate fields.
- Comment packet (`type == 3`): records packet end and breaks to comment parsing.

It validates the `"vorbis"` marker in the comment header, skips the vendor string, reads the number of tags, and parses `key=value` comment entries that fit in `ctx->buf`.

## Duration

If sample rate is known, it scans around the current position to find an initial Ogg page granule position, then scans backward near EOF for the last page with EOS set. Duration is `(last_granule - first_granule) * 1000 / samplerate`.

## Risks

The parser is deliberately lightweight and does not use libogg's full sync/page parser. FIXME comments note that embedded pictures can make tags span multiple packets; such oversized/multipacket comments are not fully supported.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/vorbis.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/wav.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/wav.c

## Role

This file parses RIFF/WAVE headers, basic audio properties, INFO metadata chunks, and optionally appended ID3v2 tags.

## Main Interface

`tagwav(Tagctx *ctx)` is the WAV parser called by `tagsget()`.

## Parsing Flow

The parser validates `RIFF` and `WAVE`, then iterates chunks. On the first `fmt ` chunk, it reads the PCM format header and sets:

- `ctx->channels`
- `ctx->samplerate`
- `ctx->duration`, estimated from remaining RIFF size and byte rate.

For `LIST` chunks it enters the list payload, and when inside `INFO`, it maps four-byte INFO keys:

- `IART`: artist.
- `ICRD`: date.
- `IGNR`: genre.
- `INAM`: title.
- `IPRD`: album.
- `ITRK`: track.
- `ICMT`: comment.
- fallback unknown key.

Values that fit in `ctx->buf` are read and emitted with `txtcb()`.

After RIFF parsing, it checks for an appended `id3 ` chunk and calls `tagid3v2()` when present.

## Risks

The parser has a simple chunk traversal model. It does not deeply handle all RIFF alignment/padding variants, but it validates chunk sizes against remaining RIFF size and skips unknown chunks.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/wav.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/xm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/xm.c

## Role

This file extracts the title from FastTracker XM module files.

## Main Interface

`tagxm(Tagctx *ctx)` reads the `Extended Module: ` signature and following 20-byte title. If the signature matches, it converts the title from CP437 to UTF-8 and emits `Ttitle`.

## Risks

The parser only validates the leading signature and title field. It does not parse full XM structure or duration.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libtags/xm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/analysis.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/analysis.c

## Role

This file implements single-block Vorbis analysis dispatch for encoding. It is part of the vendored libvorbis encoder.

## Main Interface

`vorbis_analysis(vorbis_block *vb, ogg_packet *op)` resets block bit counters and packet blobs, dispatches the block to mapping type 0 via `_mapping_P[0]->forward(vb)`, and optionally exposes the encoded packet through `ogg_packet`.

If bitrate management is active and the caller requests a packet directly, it returns `OV_EINVAL`; managed streams must use the bitrate manager interface.

## Packet Output

For unmanaged encoding, the output packet points at `vb->opb`'s buffer. It sets packet byte count, BOS/EOS flags, granule position, and sequence number.

## Analysis Debug Support

Under `ANALYSIS`, the file defines `_analysis_output_always()` and `_analysis_output()` to dump vectors to MATLAB-style `.m` files, optionally converting X-axis to Bark scale and values to dB.

## Dependencies

The file depends on libogg bit packing, Vorbis codec internals, mapping registry, scales, OS helpers, and misc helpers.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/analysis.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/backends.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/backends.h

## Role

This private libvorbis header defines backend function tables and static configuration structures for floors, residues, and mappings. It is needed by static mode headers and backend implementations.

## Floor Backend

`vorbis_func_floor` contains function pointers for packing, unpacking, lookup creation, cleanup, and inverse floor reconstruction.

Floor configuration structs include:

- `vorbis_info_floor0`: order, rate, Bark map, amplitude settings, codebook list, and encode-side threshold hints.
- `vorbis_info_floor1`: partition classes, subclass books, multiplier, post list, and encode-side fitting parameters.

## Residue Backend

`vorbis_func_residue` defines packing, unpacking, lookup, cleanup, classification, forward, and inverse callbacks.

`vorbis_info_residue0` describes block-partitioned vector-quantized residue coding, including begin/end, grouping, partition count, groupbook, second-stage flags, book list, and encode classification metrics.

## Mapping Backend

`vorbis_func_mapping` defines mapping pack/unpack/free plus forward and inverse processing.

`vorbis_info_mapping0` stores submap routing, channel muxing, floor/residue submap indexes, and channel coupling configuration.

## Integration Notes

This header is ABI-internal to libvorbis. It ties codec setup data to the runtime backend registries `_floor_P`, `_residue_P`, and `_mapping_P`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/backends.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/barkmel.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/barkmel.c

## Role

This is a small diagnostic utility for printing Bark-scale frequency mappings for common Vorbis block sizes and sample rates.

## Behavior

`main()` iterates block sizes from 64 to below 32000 and prints, for sample rates from 48 kHz down to 8 kHz:

- Frequency represented by bin 1.
- Bark value for that bin.
- Bark value for Nyquist.

It also prints Bark-to-Hz mappings for integer Bark values 0 through 27, including approximate bin positions for a 128-bin 44.1 kHz half-spectrum.

## Dependencies

It includes `scales.h` and uses `toBARK()` and `fromBARK()`.

## Integration Notes

This is not part of normal codec runtime. It is a development/analysis helper.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/barkmel.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/bitrate.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/bitrate.c

## Role

This file implements libvorbis encode-side bitrate tracking and management. It selects among alternate packet blobs, manages bitrate reservoirs, enforces min/max constraints, and flushes the chosen packet.

## Initialization

`vorbis_bitrate_init(vorbis_info *vi, bitrate_manager_state *bm)` reads `bitrate_manager_info` from codec setup. When `reservoir_bits > 0`, it enables managed mode, computes per-half-block average/min/max target bit counts, initializes short/long block scaling, starts `avgfloat` at the middle packet blob, and initializes reservoirs to the configured bias fill.

`vorbis_bitrate_clear()` zeroes state.

`vorbis_bitrate_managed()` reports whether a block's DSP state is in managed mode.

## Block Submission

`vorbis_bitrate_addblock(vorbis_block *vb)` stores the submitted block. For unmanaged streams, it simply buffers one block for the common flush path.

For managed streams it:

1. Starts from the middle packet blob.
2. Uses the average reservoir to slew `avgfloat` toward higher or lower quality packet choices.
3. Enforces minimum bitrate by choosing larger packets or padding.
4. Enforces maximum bitrate by choosing smaller packets or truncating.
5. Updates min/max and average reservoirs after final packet size is known.

Packet blobs are stored in `vorbis_block_internal->packetblob[]`, with `PACKETBLOBS/2` being the normal packet.

## Packet Flush

`vorbis_bitrate_flushpacket(vorbis_dsp_state *vd, ogg_packet *op)` exposes the selected packet as an `ogg_packet`, using the managed choice when active or the middle blob otherwise, then clears the pending block pointer.

## Risks

The manager can truncate packets when max constraints cannot be met by choosing a smaller blob. Correctness depends on mapping code producing valid alternate packet blobs and on callers using the add/flush API for managed streams.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/bitrate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/bitrate.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/bitrate.h

## Role

This private libvorbis header defines bitrate manager state/configuration and declares the bitrate management API.

## Main Structures

`bitrate_manager_state` stores runtime state:

- Managed-mode flag.
- Average and min/max reservoirs.
- Target bits per half block.
- Short-per-long scaling.
- Floating packet-blob choice.
- Pending `vorbis_block`.
- Final selected packet-blob index.

`bitrate_manager_info` stores setup configuration:

- Average, min, and max rates.
- Reservoir bit capacity.
- Reservoir bias.
- Slew damping.

## API

Declared functions are:

- `vorbis_bitrate_init`
- `vorbis_bitrate_clear`
- `vorbis_bitrate_managed`
- `vorbis_bitrate_addblock`
- `vorbis_bitrate_flushpacket`

## Integration Notes

The bitrate manager is encode-side only and depends on codec internals plus Ogg packet output semantics.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/bitrate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/block.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/block.c

## Role

This is the libvorbis block, DSP, PCM buffering, windowing, overlap/add, and analysis/synthesis state management implementation. It is one of the core runtime files for Vorbis encode and decode.

## Block Lifecycle

`vorbis_block_init()` initializes a `vorbis_block`. In analysis mode, it allocates `vorbis_block_internal` and initializes `PACKETBLOBS` bit buffers. The middle packet blob aliases `vb->opb`; others are separately allocated for bitrate management.

`_vorbis_block_alloc()` provides block-local aligned allocation. If the current local store cannot satisfy a request, it chains the old store for later cleanup and allocates a new one.

`_vorbis_block_ripcord()` frees chained stores, consolidates storage if needed, and resets local allocation state.

`vorbis_block_clear()` clears packet blobs, frees internal analysis data, reaps local allocation, and zeroes the block.

## Shared DSP Initialization

`_vds_shared_init()` initializes common encode/decode DSP state:

- Validates codec setup and block sizes.
- Allocates `private_state`.
- Initializes MDCT transforms for both block sizes.
- Computes window indexes.
- Allocates PCM buffers and return pointers.
- Initializes floor and residue backend lookups.
- For encode: initializes FFT lookups, encode codebooks, psychoacoustic lookups, and sets `analysisp`.
- For decode: initializes decode codebooks and destroys static book params after decode setup.

If decode codebook initialization fails, it cleans up via `vorbis_dsp_clear()`.

## Analysis Side

`vorbis_analysis_init()` calls shared init in encode mode, builds global psychoacoustic state, initializes envelope state, initializes bitrate management, and starts packet sequence numbering after the three Vorbis headers.

`vorbis_analysis_buffer()` returns writable channel buffers at `pcm_current`, expanding PCM storage when needed and freeing cached header packets.

`vorbis_analysis_wrote()` commits input samples or EOF. At EOF it extrapolates trailing samples using LPC where possible and appends several long blocks of padding/extrapolated data. For early stream starts it may reverse-extrapolate the beginning through `_preextrapolate_helper()`.

`vorbis_analysis_blockout()` determines when enough PCM exists for the next block, runs envelope search, sets next window size, classifies block type, copies delayed PCM into block-local storage, updates granule position, shifts the analysis buffer, and returns a ready `vorbis_block`.

## Synthesis Side

`vorbis_synthesis_init()` calls shared init in decode mode and resets synthesis state.

`vorbis_synthesis_restart()` resets decode center/window positions, PCM return state, granule position, sequence number, EOF flag, and backend sample count.

`vorbis_synthesis_blockin()` accepts a decoded block and performs overlap/add into the DSP PCM buffer. It handles all small/large window transitions, accumulates bit accounting, detects sequence holes, tracks granule position, trims extra samples from short final packets, and marks EOF.

`vorbis_synthesis_pcmout()` exposes pending decoded PCM channel pointers.

`vorbis_synthesis_read()` marks samples consumed.

`vorbis_synthesis_lapout()` exposes additional lapping/end-buffer data for vorbisfile use, including buffer unfragmentation when the two-fragment PCM arrangement wraps.

`vorbis_window()` returns the active window table for a block size.

## Cleanup

`vorbis_dsp_clear()` frees envelope state, MDCT transforms, floor/residue lookups, psychoacoustic state, global psy look, bitrate manager state, FFT lookups, PCM buffers, cached headers, and backend state.

## Risks

This file manages complex lifetime and overlap invariants. Key risks are PCM buffer shifting, granule-position correction for corrupt or unusual final packets, local block allocation lifetime, and encode/decode differences in shared initialization.

It includes explicit guards against malicious or corrupt frames that set EOS with a backdated granule position by limiting sample trimming to actually buffered samples.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/block.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/books/floor/floor_books.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/books/floor/floor_books.h

## Role

This header contains autogenerated static Huffman codebooks for Vorbis floor encoding/decoding support. The comment states it was generated by `huff/huffbuld`.

## Contents

The file includes `codebook.h` and defines many `static const char` length-list arrays plus matching `static const static_codebook` objects.

The codebooks are named by floor line configuration, for example:

- `line_256x7`
- `line_512x17`
- `line_128x4`
- `line_256x4`
- `line_128x7`
- `line_128x11`
- `line_128x17`
- `line_1024x27`
- `line_2048x27`
- `line_256x4low`

For each family, the header provides class books and subbooks such as `class0`, `class1`, `0sub0`, `0sub1`, `0sub2`, `0sub3`, and similar variants. Each `static_codebook` references its corresponding length list and uses scalar codebook parameters with no quantlist.

## Integration

These static codebook definitions are included by Vorbis mode/static setup code. They are data tables, not executable control flow. Runtime codebook initialization elsewhere consumes `static_codebook` definitions to build encode/decode lookup tables.

## Risks

The file is generated data. Manual edits are high risk because a single altered length list can break bitstream compatibility or codebook prefix properties. Validation should be done through codec tests or regeneration from the authoritative generator rather than hand editing.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/books/floor/floor_books.h -->