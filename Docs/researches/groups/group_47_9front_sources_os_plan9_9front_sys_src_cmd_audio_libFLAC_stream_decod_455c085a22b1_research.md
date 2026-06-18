# Group Research: group_47_9front_sources_os_plan9_9front_sys_src_cmd_audio_libFLAC_stream_decod_455c085a22b1

Scope confirmed against `Docs/research_subset_a.md`. Full source file read: `sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/stream_decoder.c` (`3685` lines, `146646` bytes).

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/stream_decoder.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/stream_decoder.c

## Role

This file is the vendored libFLAC stream decoder implementation used by 9front's audio command library. It implements the public `FLAC__StreamDecoder` API, including native FLAC and optional Ogg FLAC initialization, metadata parsing, frame synchronization, frame/subframe decoding, residual Rice decoding, MD5 verification, seeking, and file-backed callback adapters.

It is third-party codec code, not Plan 9 filesystem code. Within this subset it matters as part of the complete `sources/os/plan9/9front` tree, specifically the user-space audio codec support under `sys/src/cmd/audio/libFLAC`.

## Main Interfaces

Public API implemented here includes:

- Construction/destruction: `FLAC__stream_decoder_new()` and `FLAC__stream_decoder_delete()` around lines `239` and `304`.
- Initialization: stream, Ogg stream, `FILE *`, Ogg `FILE *`, filename, and Ogg filename entry points around lines `405`, `433`, `505`, `517`, `562`, and `574`.
- Lifecycle: `FLAC__stream_decoder_finish()`, `FLAC__stream_decoder_flush()`, and `FLAC__stream_decoder_reset()` around lines `586`, `885`, and `912`.
- Configuration: MD5 and metadata-response filters around lines `655` to `786`.
- Query helpers: state, total samples, channels, channel assignment, bps, sample rate, blocksize, decode position, and client data around lines `798` to `880`.
- Processing controls: `process_single`, `process_until_end_of_metadata`, `process_until_end_of_stream`, `skip_single_frame`, and `seek_absolute` around lines `979` to `1108`.

The callback model is central: client code supplies read/write/error callbacks, and optionally seek/tell/length/eof callbacks for seekable streams. File-based initializers wrap `FILE *` using internal callbacks near lines `3615` to `3685`.

## Internal State

The core private state is `FLAC__StreamDecoderPrivate`, defined near the top of the file. It stores:

- Container mode and callbacks.
- `FLAC__BitReader *input`.
- Per-channel decoded output and residual buffers.
- A 64-bit `side_subframe` buffer for 32-bit-plus side-channel cases.
- STREAMINFO and SEEKTABLE metadata caches.
- Metadata filter settings and application-ID filters.
- Current and last frame metadata.
- Sync lookahead/caching fields.
- MD5 state and computed checksum.
- Seek state: first-frame offset, last seen frame sync, target sample, unparseable-frame count, and Ogg seek helpers.

The public/protected state is kept in `decoder->protected_`; this file updates it as the decoder moves through `SEARCH_FOR_METADATA`, `READ_METADATA`, `SEARCH_FOR_FRAME_SYNC`, `READ_FRAME`, terminal/error states, and seek/abort states.

## Decode Flow

The normal decode path is:

1. Initialization validates callbacks, configures Ogg support if requested, initializes the bitreader, stores callbacks, then calls reset while avoiding an initial input rewind.
2. Processing functions drive a state machine:
   - `find_metadata_()` searches for the FLAC marker, tolerates ID3v2 tags, and can detect frame sync if metadata is absent.
   - `read_metadata_()` parses metadata blocks and moves to frame sync after the last metadata block.
   - `frame_sync_()` scans byte-aligned input for the frame sync pattern and records the sync location for possible recovery.
   - `read_frame_()` reads the header, allocates output, reads subframes, checks padding and CRC, undoes channel coding, updates decoder-visible stream properties, and calls the client write callback.
3. Errors generally set the decoder state and route notifications through `send_error_to_client_()` unless the decoder is in seek mode.

## Metadata Parsing

`read_metadata_()` handles STREAMINFO and SEEKTABLE specially because they are cached for later decode and seeking. Other metadata types are either skipped or parsed according to the metadata filter settings.

Supported metadata parsing includes:

- STREAMINFO: block/frame sizes, sample rate, channels, bps, total samples, MD5.
- SEEKTABLE: seek point array with partial trailing bytes skipped.
- APPLICATION: ID is read first, with application-ID filters optionally inverting the skip decision.
- VORBIS_COMMENT: vendor string and comment entries, with defensive limits and truncated-block handling.
- CUESHEET: track and index arrays.
- PICTURE: MIME, description, dimensions, color metadata, and image data.
- Unknown blocks: read into `unknown.data` if the client asked to receive them.

The file uses bitreader limits around variable-length metadata payload parsing so malformed block lengths are detected instead of allowing parsers to consume following data.

## Frame and Subframe Decoding

Frame handling starts in `read_frame_()` around line `2028`.

Key behavior:

- CRC-16 is initialized with the saved sync bytes, then the frame header is parsed and CRC-8 checked.
- `read_frame_header_()` decodes blocksize, sample rate, channel assignment, bits-per-sample, variable/fixed frame numbering, UTF-8 frame/sample numbers, and optional blocksize/sample-rate hints.
- Output buffers are allocated by `allocate_output_()` with extra leading zero slots for optimized LPC restore routines.
- Channel assignment adjusts effective subframe bit depth for left-side, right-side, and mid-side stereo.
- Subframes are dispatched by `read_subframe_()`:
  - constant: `read_subframe_constant_()`
  - fixed predictor: `read_subframe_fixed_()`
  - LPC: `read_subframe_lpc_()`
  - verbatim: `read_subframe_verbatim_()`
- Fixed and LPC subframes share Rice residual parsing via `read_residual_partitioned_rice_()`.
- `undo_channel_coding()` reconstructs independent channel samples from side-channel modes.

The decoder supports full decode and skip-frame mode. `FLAC__stream_decoder_skip_single_frame()` calls the same frame parser with `do_full_decode=false`, avoiding client audio output.

## Recovery and Validation

The file contains several corruption defenses:

- Header sync scanning caches lookahead bytes so repeated `0xff` bytes can be reinterpreted as a possible next sync.
- Frame header CRC-8 and frame CRC-16 are checked unless fuzzing-specific macros disable production checks.
- Reserved frame-header/subframe patterns move the decoder back to frame-sync search.
- Output samples are checked after channel reconstruction to ensure decoded values fit the declared bits-per-sample.
- If corruption is detected after a frame sync, the bitreader tries to rewind to after the last seen sync; if that is no longer buffered and the input is seekable, it seeks back to `last_seen_framesync`.
- Missing sample ranges between valid frames can be filled with silence, bounded to at most 5 seconds or 50 frames, when adjacent frame headers are consistent.

## Seeking

`FLAC__stream_decoder_seek_absolute()` requires seek/tell/length/eof callbacks and disables MD5 checking after a seek attempt. If metadata has not yet been processed, it first reads metadata to discover STREAMINFO, SEEKTABLE, and first-frame offset.

Native FLAC seeking is implemented by `seek_to_absolute_sample_()`:

- Establishes lower/upper byte and sample bounds from stream length, first-frame offset, current decode position, total samples, and seek table points.
- Estimates bytes per frame from frame size metadata or stream parameters.
- Uses proportional positioning, then repeatedly decodes frames to narrow bounds until the target frame is found.
- Uses the write callback path in seek mode to emit only samples from the target offset within the target frame.

Ogg FLAC seeking, when compiled in, is implemented separately by `seek_to_absolute_sample_ogg_()` with proportional search, fallback binary search, and linear continuation near the target.

## I/O and Container Integration

`read_callback_()` is the bitreader-facing input adapter. It handles client reads, EOF behavior, aborts, Ogg-specific EOF handling, and a seek-mode guard against excessive consecutive unparseable frames.

When Ogg support is enabled:

- `read_callback_ogg_aspect_()` maps Ogg decoder aspect statuses to stream decoder read statuses.
- `read_callback_proxy_()` maps the client's FLAC read callback into the Ogg aspect callback shape.

File-backed decoding is implemented with small adapters:

- `file_read_callback_()` wraps `fread`.
- `file_seek_callback_()` wraps `fseeko`.
- `file_tell_callback_()` wraps `ftello`.
- `file_length_callback_()` wraps `fstat` or `_filelengthi64`.
- `file_eof_callback_()` wraps `feof`.

Filename initializers open with `flac_fopen`; passing `NULL` uses `stdin`. Reset is not supported for `stdin`.

## Memory Management

The file manually owns all decoder-private allocations:

- Decoder object, protected state, private state, bitreader, and metadata-filter ID storage are allocated in `FLAC__stream_decoder_new()`.
- `FLAC__stream_decoder_finish()` frees seek table points, bitreader buffers, per-channel output/residual buffers, side-subframe storage, Ogg aspect state, and owned file handles.
- `FLAC__stream_decoder_delete()` calls finish, frees metadata filter IDs, clears Rice partition contents, deletes the bitreader, and frees decoder structs.
- Metadata blocks parsed for callbacks are freed immediately after callback delivery.
- Safe allocation helpers are used for most size-derived allocations.

One notable local invariant: `output[i]` points four `FLAC__int32` elements after the actual allocation, so freeing uses `output[i] - 4`.

## Dependencies

Important local dependencies include:

- Public/protected FLAC headers: `FLAC/stream_decoder.h`, `protected/stream_decoder.h`.
- Bitstream and codec internals: `private/bitreader.h`, `private/fixed.h`, `private/lpc.h`, `private/format.h`.
- Integrity helpers: `private/crc.h`, `private/md5.h`.
- Allocation and portability helpers: `share/alloc.h`, `share/compat.h`, `private/memory.h`.
- Optional Ogg aspect support through compile-time `FLAC__HAS_OGG`.

## Research Notes

This is a large, self-contained codec implementation with no direct filesystem semantics beyond file-backed input callbacks and stream length/position support. For architecture mapping, classify it as vendored third-party user-space audio library code in the 9front source tree. Its highest-risk areas are malformed-input parsing, seek recovery, manual memory ownership, and integer-width edge cases in frame/sample calculations and 32-bit audio reconstruction.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/stream_decoder.c -->