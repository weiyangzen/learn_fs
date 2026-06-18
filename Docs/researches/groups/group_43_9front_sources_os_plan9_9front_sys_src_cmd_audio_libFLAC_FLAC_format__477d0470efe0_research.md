# Group Research: group_43_9front_sources_os_plan9_9front_sys_src_cmd_audio_libFLAC_FLAC_format__477d0470efe0

Scope: `Docs/research_subset_a.md`, specifically the bundled 9front `sys/src/cmd/audio/libFLAC/FLAC` public headers listed in this work item. All four source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/format.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/format.h

Public libFLAC format model header for in-memory FLAC stream, frame, subframe, and metadata structures.

Important contents:
- Defines FLAC format limits: metadata type range, block size range, channel count, bits per sample, sample rate, LPC order, Rice partition order, fixed predictor order, and FLAC subset limits.
- Declares library/version/vendor/sync constants such as `FLAC__VERSION_STRING`, `FLAC__VENDOR_STRING`, `FLAC__STREAM_SYNC_STRING`, and bit-length constants.
- Defines entropy coding structures for partitioned Rice and Rice2 residual coding.
- Defines subframe structures for constant, verbatim, fixed predictor, and LPC subframes, including warmup samples, residual pointers, QLP coefficients, and wasted-bit metadata.
- Defines frame structures: channel assignment, frame number/sample number union, frame header CRC-8, frame footer CRC-16, and `FLAC__Frame`.
- Defines all FLAC metadata block structures: STREAMINFO, PADDING, APPLICATION, SEEKTABLE, VORBIS_COMMENT, CUESHEET, PICTURE, UNKNOWN, and the polymorphic `FLAC__StreamMetadata`.
- Declares format validation/manipulation helpers for sample rates, FLAC subset constraints, Vorbis comments, seek tables, cue sheets, and picture blocks.

Implementation notes:
- This is a declaration-only API header. It does not implement parsing, decoding, allocation, or I/O.
- The file documents the local convention that `_LEN` constants are bit lengths while `_LENGTH` macros are byte lengths.
- Many structures intentionally expose raw pointers. The header describes representation, not ownership; object-level ownership helpers are declared in `metadata.h`.
- It includes `export.h` for public symbol visibility and `ordinals.h` for fixed-width FLAC integer aliases.
- The structures are ABI-facing public libFLAC data contracts, so field order and type choices are significant to users of this bundled library.

Filesystem relevance:
- No filesystem logic is present. Its relevance to this subset is indirect: it is vendored third-party audio codec API code under the 9front source tree, used by 9front audio commands rather than OS/VFS code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/format.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/metadata.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/metadata.h

Public libFLAC metadata API header, covering metadata reading, editing, chain iteration, callback I/O, and metadata object memory management.

Important contents:
- Includes `sys/types.h` for `off_t`, plus `export.h`, `callback.h`, and `format.h`.
- Documents three metadata access levels:
  - Level 0: filename-based read-only helpers for STREAMINFO, VORBIS_COMMENT, CUESHEET, and constrained PICTURE lookup.
  - Level 1: `FLAC__Metadata_SimpleIterator`, a direct file iterator for reading and editing metadata blocks in place where possible.
  - Level 2: `FLAC__Metadata_Chain` and `FLAC__Metadata_Iterator`, an in-memory full metadata chain interface for editing multiple blocks efficiently before writing.
- Defines status enums and status-string arrays for simple iterator and chain operations.
- Declares Level 1 operations for init, status, writability, traversal, block offset/type/length queries, APPLICATION ID retrieval, block replacement, insertion, and deletion.
- Declares Level 2 operations for reading native FLAC and Ogg FLAC metadata, reading via callbacks, checking whether a tempfile is required, writing via filename/callbacks/tempfile callbacks, and padding merge/sort operations.
- Declares metadata object helpers for allocation, clone, delete, equality, APPLICATION data, SEEKTABLE mutation/template generation/sort/legal checks, VORBIS_COMMENT field construction/search/replacement/removal, CUESHEET track/index mutation/legal checks/CDDB ID, and PICTURE MIME/description/data/legal checks.

Implementation notes:
- This is a declaration and API contract header; actual file rewriting, parsing, allocation, and callback dispatch live elsewhere.
- Metadata object setters use explicit `copy` semantics. If `copy` is false, ownership transfers to the object and the pointer must be compatible with `free()`.
- Returned Level 0 objects and simple-iterator `get_block()` results are caller-owned and must be deleted with `FLAC__metadata_object_delete()`.
- Level 2 iterator `get_block()` returns chain-owned objects; callers must not delete them directly.
- The API warns not to mutate `is_last`, `length`, or `type` on metadata blocks returned from iterator/chain interfaces because those fields are managed internally.
- Callback-based Level 2 reads must be paired with callback-based writes; filename reads must be paired with filename writes. The chain status enum explicitly reports read/write mismatch and wrong write-call cases.
- Ogg FLAC metadata is supported as read-only in this interface.

Filesystem relevance:
- This is not filesystem implementation code, but it has file-update semantics worth noting: metadata edits may rewrite an entire FLAC file, use padding to avoid rewriting, preserve file stats, rename/unlink temp files, or require caller-managed temp handles via callbacks.
- In the 9front tree, this supports bundled FLAC audio metadata tooling rather than kernel or filesystem behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/metadata.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/ordinals.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/ordinals.h

Public libFLAC fixed-width ordinal type header.

Important contents:
- Provides FLAC-specific integer typedefs: `FLAC__int8`, `FLAC__uint8`, `FLAC__int16`, `FLAC__uint16`, `FLAC__int32`, `FLAC__uint32`, `FLAC__int64`, and `FLAC__uint64`.
- Uses Microsoft-specific integer types for MSVC versions older than 2010, which lacked C99 `stdint.h`.
- Uses `<stdint.h>` for modern MSVC and all other platforms.
- Defines `FLAC__bool` as `int`.
- Defines `FLAC__byte` as `FLAC__uint8`.
- Undefines existing `true`/`false` macros and, for non-C++, defines `true` as `1` and `false` as `0`.

Implementation notes:
- This is a portability shim and contains no runtime logic.
- It intentionally creates libFLAC-owned type names rather than exposing raw C99 names throughout the public API.
- The `true`/`false` macro handling can affect translation units that include this header, but this is inherited libFLAC API behavior.

Filesystem relevance:
- No filesystem logic. It only supports portable public type definitions for the vendored libFLAC audio library in the 9front source tree.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/ordinals.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/stream_decoder.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/stream_decoder.h

Public libFLAC stream decoder API header for native FLAC and optional Ogg FLAC decoding.

Important contents:
- Includes `stdio.h` for `FILE`, plus `export.h` and `format.h`.
- Documents the decoder lifecycle: create with `FLAC__stream_decoder_new()`, configure with setters, initialize via stream/FILE/filename APIs, process data, finish/reset/flush, and delete.
- Defines decoder state enum values from metadata search through frame reading, end-of-stream, Ogg error, seek error, abort, allocation failure, and uninitialized state.
- Defines init status enum values for success, unsupported container, invalid callbacks, allocation failure, file-open failure, and already-initialized use.
- Defines callback status enums for read, seek, tell, length, write, and error callbacks, each with exported string tables.
- Defines opaque `FLAC__StreamDecoder` with protected/private implementation pointers.
- Declares callback typedefs for read, seek, tell, length, EOF, write decoded PCM, metadata, and error reporting.
- Declares constructor/destructor, configuration setters for Ogg serial number, MD5 checking, metadata response/ignore filters, and APPLICATION-specific metadata filters.
- Declares query functions for decoder state, resolved state string, MD5 setting, total samples, channels, channel assignment, bits per sample, sample rate, blocksize, decode byte position, and client data.
- Declares native and Ogg initialization variants for caller-supplied callbacks, open `FILE *`, and filenames.
- Declares processing/control functions: `finish`, `flush`, `reset`, `process_single`, `process_until_end_of_metadata`, `process_until_end_of_stream`, `skip_single_frame`, and sample-accurate `seek_absolute`.

Implementation notes:
- This is a public declaration header, not the decoder implementation.
- The callback API separates input transport from decoded output. Clients supply encoded bytes through read callbacks and receive decoded channel buffers through the write callback.
- Seeking requires a compatible set of seek, tell, length, and EOF callbacks; otherwise seeking is unsupported.
- FILE-based initialization transfers ownership of the supplied `FILE *` to the decoder, except for `stdin`; filename-based initialization uses `fopen()` semantics and allows `NULL` for stdin.
- Metadata callbacks receive temporary objects that must not be modified and do not live beyond the callback; clients needing persistence must clone them.
- MD5 checking is optional and is disabled automatically when no STREAMINFO signature exists or when seeking is attempted.
- Setter functions are only valid while the decoder is uninitialized.

Filesystem relevance:
- No filesystem implementation is present. The only file-facing behavior is decoder input initialization from filenames or `FILE *`, plus seek/tell/length callback contracts. Within 9front, this supports audio decoding in the vendored libFLAC library.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/stream_decoder.h -->