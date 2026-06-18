# Research: subset-b-009121

Grouped research for casync synchronization, utility, compression, GC, and hashmap sources. Each section is delimited for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/casync.c -->
# sources/sync-backup/casync/src/casync.c

## Purpose

`casync.c` is the high-level orchestration layer for casync encode and decode sessions. It owns the opaque `CaSync` object exposed by `casync.h`, wires encoders/decoders to local and remote chunk stores, indexes, archives, seeds, caches, and pollable remotes, and presents a cooperative state-machine API via `ca_sync_step()`. In encode mode it serializes a base tree/file/block device through `CaEncoder`, optionally emits an archive stream/file, chunks payload data into content-addressed chunks, writes chunk index records, pushes remote archive/index/chunk data, and uses `CaCache` to skip re-reading unchanged source regions. In decode mode it drives `CaDecoder`, supplies requested chunks from seeds/stores/remotes or raw archive data, supports seeking, installs temporary output files atomically, and exposes current-entry metadata.

## Important APIs, Types, and Functions

`CaDirection` distinguishes encode and decode sessions. `CaCacheState` models the encode-side cache validation flow: off, check, verify, failed, succeeded, idle. `struct CaSync` stores almost all session state: encoder/decoder, chunker and original chunker copy, index and remote index, remote archive, local/remote writable and readable stores, seed list, cache/cache-store, fds and paths for base/boundary/archive, output temp paths, mode options, feature flags, chunk counters, cache counters, digest toggles, uid mapping, compression type, and timing counters.

Construction and lifetime are handled by `ca_sync_new_encode()`, `ca_sync_new_decode()`, private `ca_sync_new()`, and `ca_sync_unref()`. Setters configure chunk sizes, decode features (`punch_holes`, `reflink`, `hardlink`, deletion, payload, immutable handling), uid shift/range, feature flags/masks, archive/index/base/boundary/store/cache locators, seed inputs, log level, rate limiting, make/base modes, and compression type. Many setters reject invalid direction or already-started/busy state using `-ENOTTY`, `-EBUSY`, `-EINVAL`, or `-EUNATCH`.

`ca_sync_start()` is the deferred initializer. It creates temporary archive/base files when needed, constructs the encoder or decoder, transfers configured fds into them, applies feature flags and decode options, opens indexes, initializes incremental indexes for remotes, prepares same-server remote index/store optimization through a cache store, propagates digest toggles, configures seeds, stores, remotes, cache digest type, and sets `start_nsec`.

Encode path helpers include `ca_sync_step_encode()`, `ca_sync_write_chunks()`, `ca_sync_write_one_chunk()`, `ca_sync_write_final_chunk()`, `ca_sync_write_one_cached_chunk()`, `ca_sync_write_archive()`, `ca_sync_write_remote_archive()`, `ca_sync_install_archive()`, and `ca_sync_cache_get()`. Decode path helpers include `ca_sync_step_decode()`, `ca_sync_process_decoder_request()`, `ca_sync_process_decoder_seek()`, `ca_sync_process_decoder_skip()`, `ca_sync_try_hardlink()`, and `ca_sync_install_base()`.

Remote integration is split across `ca_sync_remote_prefetch()`, `ca_sync_remote_push_index()`, `ca_sync_remote_push_chunk()`, `ca_sync_remote_step_one()`, `ca_sync_remote_step()`, `ca_sync_n_remotes()`, and `ca_sync_current_remote()`. `ca_sync_poll()` exposes the remote fds/events for callers that receive `CA_SYNC_POLL`.

Chunk access APIs are `ca_sync_get_local()`, `ca_sync_get()`, `ca_sync_has_local()`, and `ca_sync_make_chunk_id()`. Metadata/stat APIs forward to the active seed, encoder, or decoder: current path/mode/target/mtime/size/uid/gid/user/group/rdev/chattr/FAT attrs/xattrs/quota project id, archive offset/chunk counts, seek operations, payload access, archive size, digest enable/get, request counters, runtime and decode timing, compression type, and cache counters.

## Control Flow

The external loop calls `ca_sync_step()` until `CA_SYNC_FINISHED` or an error. On every step the function first starts the session, then tries decode-specific prerequisites in priority order: propagate index flags to stores/seeds/remotes/decoder, advance seed indexing, prefetch remote chunks, push incremental index, push chunks requested by the remote peer, decode available data, process remote IO, and finally generate encode data. This ordering lets decode consume already available bytes before reading more remote input and lets remotes drain before the encoder generates more archive/index data.

Encode mode calls `ca_encoder_step()` and reacts to encoder statuses. Data-bearing statuses (`NEXT_FILE`, `PAYLOAD`, `DATA`) are optionally cache-checked, read through `ca_encoder_get_data()`, chunked through the rolling `CaChunker`, written to stores/index/cache, and copied to local/remote archive streams. `CA_ENCODER_FINISHED` flushes the final partial chunk, writes index EOF and installs the index, renames any temporary archive path, sends remote archive EOF, and either finishes or lets remote outputs drain.

The encode cache path is a multi-step verifier. `CA_SYNC_CACHE_CHECK` probes `CaCache` for the current source `CaLocation`. `VERIFY` compares stored origin locations against generated encoder locations and buffered origin data, consuming matching bytes without storing duplicate chunks. `SUCCEEDED` writes only the cached chunk ID/index record. `FAILED` removes the stale cache entry, seeks the encoder back to the saved location, clears buffers, restores the original chunker state, and resumes uncached generation.

Decode mode asks `ca_decoder_step()` what it needs. `REQUEST` reads the next index chunk, waits for seed indexing when required, resolves the chunk from seeds/local stores/cache store/remote stores, applies any seek skip, and feeds bytes plus origin to `ca_decoder_put_data()`. Without an index, local archive fd reads are converted to payload origins and fed directly. `SEEK` uses either `ca_index_seek()` or archive `lseek()`, and `SKIP` advances chunk skip or archive fd. `DONE_FILE` can attempt seed-based hardlink reconstruction before reporting completion. `FINISHED` installs any temporary base file.

Remote control is cooperative. Incremental remote index reads go into `ca_index_incremental_write()`, remote archive reads go to the decoder, encode-side index bytes are read from the incremental index and pushed, and same-server push-index/chunks mode handles remote missing-chunk requests.

## State and Persistence Behavior

Persistent outputs can include local archive files, local index files, local chunk stores, cache directories, and decoded base trees/files/devices. Encode archive and decode regular-file base outputs use random temporary paths and `rename()` for atomic install. `ca_sync_unref()` unlinks temporary paths if the session is destroyed before install. Open fds passed into the session are consumed by encoder/decoder or closed on unref if still owned.

The chunker is persistent in session memory and reset from `original_chunker` after cache verification failure. `buffer`, `index_buffer`, `archive_buffer`, and `compress_buffer` are reusable dynamic buffers. `buffer_origin` tracks source location provenance for data currently waiting to become a chunk. Counters track generated/reused/prefetched chunks, cache hit/miss/invalidated/added totals, and request byte totals obtained from store/seed/remote layers.

Feature flags determine digest type and supported archive features. Encode defaults to `CA_FORMAT_DEFAULT & SUPPORTED_FEATURE_MASK`; decode accepts a feature mask and later propagates index-discovered flags. Remote/index/cache/store digest types are kept aligned with the active feature flags.

## Dependencies and Integration Points

This file is central to the casync library. It depends on `CaEncoder`, `CaDecoder`, `CaIndex`, `CaRemote`, `CaStore`, `CaSeed`, `CaCache`, `CaChunker`, `CaDigest`, `CaOrigin`, `CaLocation`, `ReallocBuffer`, feature-format utilities, protocol flags, and POSIX filesystem APIs. Locator classification comes from `cautil.c` through `ca_classify_locator()`. Constants such as `BUFFER_SIZE` and supported feature masks come from `def.h`. Compression is delegated to store/remote/`ca_compress()` paths.

`casync.h` exposes the public surface. Callers are expected to configure locators/options before the first `ca_sync_step()` or seek operation starts the session. `ca_sync_poll()` integrates with event loops by collecting read/write fds from all configured remotes.

## Risks and Edge Cases

The state machine is sensitive to ordering. Starting the session freezes many options; setters must be called before `start_nsec` or before encoder/decoder creation where required. Cache verification has several correctness conditions around matching `CaLocation` metadata, buffer origins, generated byte counts, and chunker reset. A stale cache entry must be removed and the encoder must be seekable to the saved location.

Remote reuse of index/store connections depends on `ca_remote_set_*_url()` returning `-EBUSY` only for non-matching or already-fixed remote cases; misinterpreting that contract can leak partially configured remotes. Decode with remote/index data may return `CA_SYNC_POLL` while internal queues are waiting for IO or seed completion. Chunk size mismatches from stores/indexes are treated as `-EBADMSG`.

Temporary install relies on `rename()` and correct cleanup on unref. Base and boundary path mode interactions are strict and can return `-EUNATCH` if decode has no known output type. Some getters return `-ENODATA`, `-ENOTTY`, or `-ENOMEDIUM` depending on direction, feature enabled state, and whether the encoder/decoder has started.

`ca_sync_poll()` counts remote_wstore separately even when it may alias `remote_index`; `ca_sync_n_remotes()` avoids aliasing for stepping, but the poll fd array may include duplicated fds if aliases exist. This should be tested against remote reuse behavior.

## Test Signals

Useful tests include encode/decode round trips with local archive+index+store, decode from raw archive without index, remote index/store/archive combinations, same-server remote index/chunk push optimization, cache hit/miss/invalidation flows after modifying source files, atomic temp-file install and cleanup, seek by offset/path/next sibling, seed-based chunk reuse and hardlink reconstruction, digest toggles, feature-flag propagation, uid shift/range behavior, and `CA_SYNC_POLL` integration with a fake remote. Error-path tests should cover missing base mode, unsupported direction setters, chunk-size mismatch, remote failures, non-regular archive seek size acquisition, and stale cache origin metadata.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/casync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/casync.h -->
# sources/sync-backup/casync/src/casync.h

## Purpose

`casync.h` is the public API for the opaque `CaSync` synchronization object. It defines the cooperative status codes returned by `ca_sync_step()`, construction/destruction functions, configuration setters for encode/decode sessions, locator setup for archives/indexes/stores/seeds/cache, state-machine polling, metadata accessors, low-level chunk retrieval, seeking, digest control, and statistics getters.

## Important APIs, Types, and Functions

The header forward-declares `CaSync` and includes chunk, chunk-id, common compression/iteration types, and origin definitions. The status enum maps internal encoder/decoder/seed/remote statuses to public values: `CA_SYNC_FINISHED`, `CA_SYNC_STEP`, `CA_SYNC_PAYLOAD`, file boundary events, seed file events, `CA_SYNC_POLL`, and seek-found/not-found events.

Creation is split by direction with `ca_sync_new_encode()` and `ca_sync_new_decode()`. `ca_sync_unref()` integrates with the local cleanup macro. Configuration APIs include log level, rate limiting, feature flags/mask, decode output behavior (`punch_holes`, `reflink`, `hardlink`, deletion, payload, immutable handling), compression type, uid mapping, output creation mode, index/base/boundary/archive/store locators, additional stores, seeds, and cache.

Runtime APIs are `ca_sync_step()` and `ca_sync_poll()`. Metadata APIs expose current path, mode, target, uid/gid, user/group, mtime, size, rdev, chattr, FAT attrs, xattrs, quota project id, archive size, archive chunk counters, archive offset, payload bytes, punch/reflink/hardlink counters, and cache counters. Low-level chunk APIs expose local/all-store lookup, existence checks, and chunk ID generation. Seeking APIs allow offset, path, path+offset, and next sibling navigation in decode mode. Digest APIs enable and retrieve archive, payload, and hardlink digests. Statistics APIs report seed/local/remote request counts, bytes, seeding time, decoding time, and total runtime.

## Control Flow

The intended call pattern is configure a new object, repeatedly call `ca_sync_step()`, call `ca_sync_poll()` when `CA_SYNC_POLL` is returned and remotes exist, inspect metadata on file/payload events, optionally call seek methods in decode mode, then unref the object. Many getters are meaningful only after the underlying encoder/decoder/seed has reached a state where the requested data exists.

## State and Persistence Behavior

The header hides `struct CaSync`; callers interact only through setter/getter side effects. Fd setters transfer ownership to the object implementation. Path/remote locators are stored internally until start, when local files may be opened or created and remote objects initialized. The cleanup macro encourages scoped ownership.

## Dependencies and Integration Points

The API integrates with the rest of casync through `CaChunkID`, `CaChunkCompression`, `CaCompressionType`, `CaIterate`, and `CaOrigin`. Higher-level CLI or library users build sync workflows from this header. Event loops use `ca_sync_poll()` with `sigset_t`.

## Risks and Edge Cases

Because the object is direction-specific, callers must expect `-ENOTTY` for encode-only or decode-only operations used incorrectly. Several options must be set before start; late calls can fail. Fd ownership needs clear caller discipline to avoid double close. Return values are mixed status codes and negative errno-style errors, so callers must not treat every nonzero as failure.

## Test Signals

Compile-time tests should include API availability for C users and cleanup macro use. Behavioral tests should cover each status code, setter validation by direction, ownership of fd/path locators, `CA_SYNC_POLL` with and without remotes, metadata getters before and after file events, digest enable/get combinations, and stats getters before start and after completion.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/casync.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/cautil.c -->
# sources/sync-backup/casync/src/cautil.c

## Purpose

`cautil.c` provides small casync-specific utility functions for classifying locators, normalizing file URLs, checking locator suffixes, filtering xattr names, selecting the compressed chunk suffix, and replacing the last path component of path/SSH/URL locators. These utilities are used by higher-level code that accepts path-like, SSH-like, or URL-like user inputs.

## Important APIs, Types, and Functions

`ca_is_definitely_path()` is private and treats absolute paths plus `.`, `..`, and `./...` as filesystem paths. `ca_is_url()` recognizes restricted RFC3986-style URLs that contain `://`, a protocol character set, and a non-empty host/path separator, while excluding definite paths. `ca_is_ssh_path()` recognizes `host:path` and `user@host:path` forms while excluding definite paths and empty remote path components. `ca_classify_locator()` returns `CA_LOCATOR_URL`, `CA_LOCATOR_SSH`, `CA_LOCATOR_PATH`, or invalid for empty input.

`ca_strip_file_url()` converts `file:///...` and `file://localhost/...` to local paths and percent-decodes hex escapes defensively; other inputs are duplicated unchanged. `ca_locator_has_suffix()` checks suffixes for URLs before query/parameter delimiters and for paths/SSH locators only against the final path component, requiring the suffix not to be the entire component. `ca_xattr_name_is_valid()` enforces non-empty, contains-dot, no leading/trailing dot, and `<=255` length. `ca_xattr_name_store()` permits only valid `user.` and `trusted.` xattrs for generic storage. `ca_compressed_chunk_suffix()` returns `CASYNC_COMPRESSED_CHUNK_SUFFIX` or `.cacnk` and caches the returned pointer. `ca_locator_patch_last_component()` replaces the basename component for URL, SSH, and path locators while preserving URL scheme/host and SSH prefix.

## Control Flow

Locator classification first rejects empty strings, then checks URL syntax before SSH syntax, defaulting to path. Last-component patching switches on that class: URLs skip protocol/host and query/parameter suffixes before finding the final slash; SSH paths split at `:` and use `dirname_malloc()` if the remote path has slashes; filesystem paths use `dirname_malloc()` when there is a slash or else replace the whole locator.

## State and Persistence Behavior

Most functions are pure string transforms that allocate new strings for callers to free. `ca_compressed_chunk_suffix()` has one static cached pointer and observes the environment only on first call. `ca_strip_file_url()` and `ca_locator_patch_last_component()` allocate results with `strdup`, `new`, or `strjoin`.

## Dependencies and Integration Points

This file depends on `util.h` for helpers such as `startswith`, `endswith`, `isempty`, `unhexchar`, `strjoin`, `strndupa`, `dirname_malloc`, and character sets. `casync.c` uses locator classification to route archive/index/store inputs to local or remote setters. Store and archive code likely use the compressed chunk suffix and xattr filters.

## Risks and Edge Cases

The URL parser is intentionally restrictive and may classify unusual but valid URLs as paths. The SSH parser treats any `host:path` with allowed host characters and non-empty suffix as SSH, so Windows-style drive letters can be ambiguous unless they are definite paths. `ca_strip_file_url()` decodes percent escapes byte-wise without validating UTF-8 and leaves non-localhost file URLs unchanged. The compressed suffix cache means changing the environment after first use has no effect. URL suffix handling ignores text after `?` or `;`, which must match remote URL conventions.

## Test Signals

Tests should cover absolute paths, `.`, `..`, relative names, `./x`, `http://host/path`, URL queries/parameters, `file:///tmp/a%20b`, `file://localhost/tmp`, non-local file URLs, `host:path`, `user@host:path`, empty remote components, Windows-like strings if supported, suffix checks for final components and URLs with query strings, xattr namespace filtering, and last-component patching for each locator class.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/cautil.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/cautil.h -->
# sources/sync-backup/casync/src/cautil.h

## Purpose

`cautil.h` declares casync locator and xattr utility functions implemented in `cautil.c`. It is a small shared interface for code that needs to distinguish local paths, SSH paths, and URLs or apply casync-specific name policies.

## Important APIs, Types, and Functions

The header declares `ca_is_url()`, `ca_is_ssh_path()`, `CaLocatorClass`, `ca_classify_locator()`, `ca_strip_file_url()`, `ca_locator_has_suffix()`, `ca_xattr_name_is_valid()`, `ca_xattr_name_store()`, `ca_compressed_chunk_suffix()`, and `ca_locator_patch_last_component()`.

`CaLocatorClass` has path, SSH, URL, and invalid states. The invalid value is negative to fit errno-style validation patterns.

## Control Flow

The header does not implement control flow, but it establishes a two-stage calling pattern: classify a locator, then dispatch to path or remote handling; validate/filter xattrs before storing; optionally rewrite or strip locators before opening.

## State and Persistence Behavior

Most declarations return booleans or allocated strings. Callers are responsible for freeing returned strings from strip/patch functions. The suffix function returns a pointer that may reference process environment storage.

## Dependencies and Integration Points

The header includes `<stdbool.h>` only and is consumed by `casync.c` and storage/archive helpers. It depends on `util.h` only through the implementation, keeping the public include lightweight.

## Risks and Edge Cases

Consumers must not assume `ca_is_url()` accepts every RFC-valid URL or that `ca_is_ssh_path()` is safe for every platform path syntax. Returned allocated strings need ownership handling. `ca_compressed_chunk_suffix()` is process-global through its cached implementation.

## Test Signals

Integration tests should assert consistent classification between this interface and all auto-locator setters in `casync.c`, plus memory-safety checks for returned strings under allocation-failure instrumentation.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/cautil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/chattr.c -->
# sources/sync-backup/casync/src/chattr.c

## Purpose

`chattr.c` wraps Linux filesystem attribute ioctls for generic `FS_IOC_*FLAGS` attributes and FAT-specific attributes. It normalizes unsupported filesystems/node types so reading unsupported attributes yields zero and writing zero attributes succeeds.

## Important APIs, Types, and Functions

`read_attr_fd()` calls `ioctl(fd, FS_IOC_GETFLAGS, ret)` and returns `1` when supported, `0` with `*ret = 0` when unsupported, or negative errno. `write_attr_fd()` calls `FS_IOC_SETFLAGS`; unsupported zero writes return `0`, other failures are negative errno, and supported writes return `1`. `mask_attr_fd()` reads current flags, merges `(old & ~mask) | (value & mask)`, and writes only if changed.

`read_fat_attr_fd()`, `write_fat_attr_fd()`, and `mask_fat_attr_fd()` provide the same pattern for `FAT_IOCTL_GET_ATTRIBUTES` and `FAT_IOCTL_SET_ATTRIBUTES` using `uint32_t`.

## Control Flow

The mask functions are read-modify-write helpers with a fast path for `mask == 0` and no-op when computed attributes match existing attributes. Unsupported handling is centralized in the read/write helpers through `ERRNO_IS_UNSUPPORTED()`.

## State and Persistence Behavior

The only persistent behavior is kernel-level mutation of inode/FAT attributes through ioctls. No process-global state is stored.

## Dependencies and Integration Points

The file includes Linux ioctl definitions and `util.h` for `ERRNO_IS_UNSUPPORTED()`. It integrates with encoder/decoder metadata preservation for chattr and FAT attributes.

## Risks and Edge Cases

Unsupported filesystems are silently treated as zero attributes, which is intentional but can hide missing metadata preservation. Writes of nonzero attributes to unsupported filesystems fail. Race conditions are possible between read and masked write if attributes change concurrently. The functions assert valid fds/ret pointers instead of returning errors for those programming mistakes.

## Test Signals

Tests should cover supported filesystems when available, unsupported node types/filesystems, writing zero to unsupported targets, writing nonzero unsupported attributes, mask no-op, mask changed value, and FAT-specific paths if the test environment can mount or mock FAT ioctl behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/chattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/chattr.h -->
# sources/sync-backup/casync/src/chattr.h

## Purpose

`chattr.h` declares Linux attribute ioctl wrappers for generic and FAT filesystem attributes.

## Important APIs, Types, and Functions

The header exposes `read_attr_fd()`, `write_attr_fd()`, `mask_attr_fd()`, `read_fat_attr_fd()`, `write_fat_attr_fd()`, and `mask_fat_attr_fd()`. It includes `<inttypes.h>` for `uint32_t`.

## Control Flow

Callers typically read attributes during encoding, write attributes during decoding, or use mask functions when applying only a subset of preserved flags.

## State and Persistence Behavior

The API operates on caller-provided file descriptors and persists changes through kernel ioctls.

## Dependencies and Integration Points

This header is consumed by archive encoder/decoder metadata code. It hides Linux ioctl details behind errno-style helper functions.

## Risks and Edge Cases

The implementation is Linux-specific. Callers need to understand that `0` means unsupported/no-op and `1` means supported/action, not simple boolean success.

## Test Signals

API tests should validate return-value interpretation and build behavior on Linux configurations with the expected ioctl constants.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/chattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/compressor.c -->
# sources/sync-backup/casync/src/compressor.c

## Purpose

`compressor.c` is the streaming compression/decompression adapter for xz, gzip, and zstd chunk/archive handling. It normalizes optional library support and differing stream APIs into one `CompressorContext` interface with small status codes for EOF, more-output/more-input, and good progress.

## Important APIs, Types, and Functions

`detect_compression()` recognizes xz, gzip, and zstd magic bytes. It returns a `CaCompressionType`, `-EAGAIN` when the provided prefix is too short to decide, or `-EBADMSG` when enough bytes are present and no known signature matches. `compressor_is_supported()` maps compression enum values to compile-time `HAVE_LIBLZMA`, `HAVE_LIBZ`, and `HAVE_LIBZSTD`.

`compressor_start_decode()` and `compressor_start_encode()` validate compressor enum values, initialize the correct stream (`lzma_stream_decoder`, `inflateInit2`, `ZSTD_createDStream`, `lzma_easy_encoder`, `deflateInit2`, `ZSTD_createCStream`), set operation mode, and return `-ENOSYS` if the library was not compiled in.

`compressor_finish()` releases library stream state according to compressor and operation. `compressor_input()` stores the caller's input buffer in the selected stream. `compressor_decode()` and `compressor_encode()` write output into caller buffers, set `ret_done`, and return `COMPRESSOR_EOF`, `COMPRESSOR_MORE`, or `COMPRESSOR_GOOD`, or negative errno-style errors.

## Control Flow

The required sequence is initialize `CompressorContext` with `COMPRESSOR_CONTEXT_INIT`, start encode/decode, repeatedly call `compressor_input()` with available input, call encode/decode with output buffers until it reports good/more/eof, then finish. Decode paths reject trailing bytes after stream EOF as `-EBADMSG`. Encode paths use a `finalize` flag to select final stream operations (`LZMA_FINISH`, `Z_FINISH`, `ZSTD_endStream`) once input is exhausted.

## State and Persistence Behavior

All persistent state is in `CompressorContext`: current operation, compressor type, and the active library stream union. The adapter does not own the caller input/output buffers. `compressor_finish()` currently releases library resources but does not reset `operation` back to uninitialized, so contexts should not be reused without reinitialization discipline.

## Dependencies and Integration Points

The file depends on `compressor.h`, `cacompression.h`, optional liblzma/zlib/zstd headers, and `util.h` for assertions/macros. It is used by chunk/store/archive compression helpers such as `ca_compress()` and decompression readers.

## Risks and Edge Cases

The code asserts positive input/output availability in several decode paths; callers must not invoke decode with empty input or zero output size. zstd input/output buffer `.pos` fields are preserved across calls and must be correctly reset by `compressor_input()` and output setup. Missing optional libraries produce `-ENOSYS`; callers must handle unsupported configured compression. `compressor_is_supported()` uses `assert("Unknown compression type")`, which is a non-null string and therefore not an effective assertion failure; invalid enum handling relies more on start functions.

## Test Signals

Tests should round-trip xz/gzip/zstd when compiled in, detect magic prefixes including short buffers, reject trailing bytes after compressed streams, exercise zero/invalid arguments, compile with each optional library disabled, check `COMPRESSOR_MORE` for small output buffers, and validate finalize semantics for zstd streams with no pending input.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/compressor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/compressor.h -->
# sources/sync-backup/casync/src/compressor.h

## Purpose

`compressor.h` declares the unified streaming compression context and operations for xz, gzip, and zstd.

## Important APIs, Types, and Functions

`CompressorOperation` tracks uninitialized, encode, or decode mode. `CompressorContext` stores the operation, selected `CaCompressionType`, and a union of optional library stream structs. `COMPRESSOR_CONTEXT_INIT` initializes a safe empty context. Public functions include support detection, start encode/decode, finish, input assignment, encode/decode streaming, and magic-byte detection. The status enum defines `COMPRESSOR_EOF`, `COMPRESSOR_MORE`, and `COMPRESSOR_GOOD`.

## Control Flow

The header defines a single context lifecycle: initialize, start for a compression type and direction, feed input, drain output with status-driven loops, finish. Callers branch on status enum values rather than library-specific return codes.

## State and Persistence Behavior

The context contains library-owned allocations for zstd streams and library internal state for zlib/lzma. It should be finished before being discarded. Buffer pointers passed through `compressor_input()` remain caller-owned.

## Dependencies and Integration Points

It includes optional compression headers only when build macros are enabled and uses `cacompression.h` for the shared compression enum. Store/archive code can include this header without directly depending on every compression library when disabled.

## Risks and Edge Cases

Because the union fields only exist under compile-time macros, code must guard access through the adapter. Context reuse after `compressor_finish()` is not guaranteed by the interface. The misspelled include guard name is harmless but should not be copied into new code.

## Test Signals

Build matrix tests should cover all combinations of compression library macros. API tests should verify that disabled compressors compile and return unsupported errors through the implementation.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/compressor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/copy.c -->
# sources/sync-backup/casync/src/copy.c

## Purpose

`copy.c` implements `copy_bytes()`, an optimized fd-to-fd byte copier that tries in-kernel copy mechanisms first and falls back to buffered read/write. It supports copying until EOF or a caller-specified byte limit.

## Important APIs, Types, and Functions

When libc/kernel headers lack `copy_file_range()`, the file defines syscall numbers for common architectures and provides a local wrapper. `try_copy_file_range()` caches whether the syscall exists using a static `have` flag and returns negative errno-style results. `copy_bytes(int fdf, int fdt, uint64_t max_bytes)` tries `copy_file_range`, then `sendfile`, then `splice`, then manual read and `loop_write()`.

## Control Flow

The copy loop maintains `m`, the maximum per-call copy size, capped by `max_bytes` when finite. Unsupported or unsuitable errors from each optimized mechanism disable only that mechanism and fall through to the next option. A zero-byte result from a mechanism means EOF and terminates. After each successful copy, finite `max_bytes` is decremented; when it reaches zero the function returns `1`. EOF before the limit returns `0`.

## State and Persistence Behavior

The only process state is `try_copy_file_range()`'s static availability cache. Persistent effects are bytes written to the target fd and advancement of the fds' current offsets. No explicit fsync is performed.

## Dependencies and Integration Points

The file includes `copy.h`, uses `BUFFER_SIZE` from shared headers, and relies on utility helpers/macros such as `IN_SET`, `MIN`, `MAX`, and `loop_write()`. It likely supports decoder extraction or store/archive file copying.

## Risks and Edge Cases

The manual fallback declares `uint8_t buf[MIN(m, BUFFER_SIZE)]`; very large or dynamic stack allocation behavior depends on compiler support for VLAs and `m` staying bounded. The final update `m = MAX(MIN(BUFFER_SIZE, max_bytes), m - n)` behaves oddly when `max_bytes == (uint64_t)-1`, because `MIN(BUFFER_SIZE, max_bytes)` is still `BUFFER_SIZE`, but this mainly keeps a lower bound. Kernel copy operations may fail with filesystem-specific errors and fall back only for selected errno values. `splice()` between arbitrary fds may not be valid.

## Test Signals

Tests should copy regular files with exact limit, EOF before limit, unlimited copy, zero limit, pipes where `sendfile` or `splice` behavior differs, forced `copy_file_range` `ENOSYS` fallback, cross-filesystem `EXDEV`, and short writes in `loop_write()` using a pipe or fault-injection wrapper.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/copy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/def.h -->
# sources/sync-backup/casync/src/def.h

## Purpose

`def.h` centralizes small global constants for casync's source tree: node limits, buffer size, and supported feature masks based on build-time SELinux support.

## Important APIs, Types, and Functions

`NODES_MAX` is `64`. `BUFFER_SIZE` is `64U*1024U`. `SUPPORTED_FEATURE_MASK` is either `CA_FORMAT_FEATURE_FLAGS_MAX` when `HAVE_SELINUX` is true or that mask with `CA_FORMAT_WITH_SELINUX` removed. `SUPPORTED_WITH_MASK` intersects `CA_FORMAT_WITH_MASK` with the supported feature mask.

## Control Flow

There is no runtime control flow. Preprocessor branches select feature support at compile time.

## State and Persistence Behavior

The header stores no state. Its macros affect runtime behavior in files like `casync.c` by controlling default encode features and accepted decode feature masks.

## Dependencies and Integration Points

It depends on format feature macros being visible before or through users that include it. `casync.c` uses it for default encode feature flags and buffer sizes. `copy.c` uses `BUFFER_SIZE` through its include chain.

## Risks and Edge Cases

Build configurations without SELinux intentionally reject or mask SELinux metadata support. If format constants change, this header must stay aligned. Broad macros in a small global header can silently affect many call sites.

## Test Signals

Build tests should compare feature masks with and without `HAVE_SELINUX`, and runtime archive compatibility tests should verify SELinux metadata is included only when supported.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/def.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/dirent-util.c -->
# sources/sync-backup/casync/src/dirent-util.c

## Purpose

`dirent-util.c` provides directory-entry helpers derived from systemd utilities. It filters regular/link/unknown non-hidden entries by suffix and wraps `readdir()` to skip `.` and `..`.

## Important APIs, Types, and Functions

`dirent_is_file_with_suffix()` accepts `DT_REG`, `DT_LNK`, and `DT_UNKNOWN`, rejects names beginning with `.`, accepts any suffix when suffix is `NULL`, and otherwise tests `endswith(de->d_name, suffix)`. `readdir_no_dot()` loops over `readdir()` until it sees an entry that is not `.` or `..` or reaches EOF/error.

## Control Flow

Both functions are simple filters around libc `readdir()` and `struct dirent`. `readdir_no_dot()` preserves libc error signaling through `errno` exactly as `readdir()` does; callers need to clear/check errno if they need to distinguish EOF from error.

## State and Persistence Behavior

No persistent state is stored. `readdir_no_dot()` advances the directory stream.

## Dependencies and Integration Points

It includes `dirent-util.h` and uses `IN_SET`, `endswith`, and `dot_or_dot_dot()` from `util.h`. Store/index directory scanners and GC are likely consumers.

## Risks and Edge Cases

Rejecting all dot-prefixed names may be correct for chunk files but is not a generic file predicate. Accepting `DT_UNKNOWN` means callers may need `stat()` later. Suffix matching does not require the suffix to be a true extension boundary.

## Test Signals

Tests should cover visible/hidden files, symlinks, directories, unknown d_type if mockable, null suffix, positive/negative suffixes, and `readdir_no_dot()` behavior on empty directories and errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/dirent-util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/dirent-util.h -->
# sources/sync-backup/casync/src/dirent-util.h

## Purpose

`dirent-util.h` declares directory-entry helper functions and a macro for safe directory iteration with errno handling.

## Important APIs, Types, and Functions

It declares `dirent_is_file_with_suffix()` as `_pure_` and `readdir_no_dot()`. `FOREACH_DIRENT_ALL(de, d, on_error)` expands to a loop that clears `errno` before each `readdir()`, runs `on_error` when EOF is accompanied by an errno, and otherwise exposes every returned entry.

## Control Flow

The macro provides structured iteration where caller-supplied `on_error` can return, break, or otherwise handle the directory error. `readdir_no_dot()` gives a function form for skipping dot entries.

## State and Persistence Behavior

The API advances caller-owned `DIR *` streams and stores no state.

## Dependencies and Integration Points

It includes `<dirent.h>`, `<errno.h>`, `<stdbool.h>`, and `util.h`. Files scanning stores or filesystem trees can use these helpers for consistent dot-entry handling.

## Risks and Edge Cases

Macros with embedded control flow can be misused if `on_error` has side effects or declarations that do not fit the expansion context. The header uses `#pragma once` unlike some local headers that use include guards; this is acceptable for supported compilers.

## Test Signals

Tests should compile macro users in different statement contexts and validate errno behavior on mocked `readdir()` failure.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/dirent-util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/fssize.c -->
# sources/sync-backup/casync/src/fssize.c

## Purpose

`fssize.c` detects the logical size of filesystem/image formats by reading known superblock/header layouts from an fd. It supports squashfs, Android boot images, FAT, and ext2/3/4.

## Important APIs, Types, and Functions

`read_file_system_size(int fd, uint64_t *ret)` reads a union large enough for the supported headers with `pread(fd, ..., 0)`. It returns negative errno on read failure, `0` when the image is too short or unrecognized, and `1` with `*ret` set when a supported format is recognized.

The local packed union contains FAT boot sector fields, squashfs superblock fields, Android boot image header fields, and an ext2/3/4 superblock located after a 1024-byte skip. FAT uses signature `0xaa55`; Android boot image magic is split across `_ANDROID_BOOTIMG_MAGIC_1` and `_ANDROID_BOOTIMG_MAGIC_2`.

## Control Flow

After a full header read, detection checks squashfs first, Android boot image second, FAT third, and ext2/3/4 last. Squashfs size is `bytes_used` aligned to 4096. Android size is a sum of page-aligned header, kernel, initrd, second stage, and dtb sizes when page size is a power of two. FAT size uses 16-bit sector count first, then 32-bit total sectors. Ext size multiplies block count by `1 << (10 + s_log_block_size)` if the shift is below 64.

## State and Persistence Behavior

The function is read-only and does not change file offset because it uses `pread()`. No process state is stored.

## Dependencies and Integration Points

It includes `fssize.h` and `util.h`, relying on endian typedefs/converters, `_packed_`, `ALIGN_TO`, `IS_POWER_OF_TWO`, and filesystem magic constants. It likely helps decide sparse/block image payload sizes during encode/decode.

## Risks and Edge Cases

There is a likely bug in `if (le32toh(superblock.squashfs.s_magic == SQUASHFS_MAGIC))`: the comparison is performed before endian conversion, so this does not actually convert the magic value. This may still work by accident on little-endian if the boolean result is passed through unchanged, but it is semantically wrong and can miss or mis-handle big-endian cases. The function requires reading the full union size, so valid shorter headers could be unrecognized. Android header size is hard-coded as 608. FAT signature alone is a weak signal without stronger validation.

## Test Signals

Tests should use synthetic images for each supported format, too-short files, unknown data, big-endian simulation or static analysis for the squashfs magic expression, invalid Android page sizes, FAT 16-bit versus 32-bit sector counts, ext block-size shifts near overflow, and fd offset preservation.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/fssize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/fssize.h -->
# sources/sync-backup/casync/src/fssize.h

## Purpose

`fssize.h` declares the filesystem/image size detection helper.

## Important APIs, Types, and Functions

It exposes `read_file_system_size(int fd, uint64_t *ret)` and includes `<inttypes.h>` for `uint64_t`.

## Control Flow

Callers pass an open fd and interpret `1` as detected, `0` as unknown, and negative values as errors.

## State and Persistence Behavior

The API is read-only in the implementation and should not move the fd offset.

## Dependencies and Integration Points

It is a lightweight header for encoder or image handling code that wants to infer usable payload size from an image file rather than raw file length.

## Risks and Edge Cases

Consumers must not treat `0` as an error; it means no known filesystem signature. The helper is format-limited.

## Test Signals

Tests should assert return-value contract and fd-offset preservation through the implementation.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/fssize.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/gc.c -->
# sources/sync-backup/casync/src/gc.c

## Purpose

`gc.c` implements garbage collection support for casync stores. It builds a collection of chunk IDs referenced by index files and removes chunk files from a store that are not in that collection.

## Important APIs, Types, and Functions

`struct CaChunkCollection` stores `n_used`, the number of chunk references seen across indexes, and `used_chunks`, a `Set` of unique `CaChunkID` copies. `chunk_hash_ops` hashes and compares `CaChunkID` values by content with siphash and `memcmp`.

`ca_chunk_collection_new()` allocates the collection and creates the set. `ca_chunk_collection_unref()` frees the set and stored IDs. `ca_chunk_collection_usage()` returns total references added, including duplicates. `ca_chunk_collection_size()` returns unique chunk count. `gc_add_chunk_id()` duplicates an ID, increments usage, and inserts it into the set, treating `-EEXIST` as success after `set_consume()` frees duplicates.

`ca_chunk_collection_add_index()` opens a `CaIndex` for a path and reads chunk IDs until EOF, adding each to the collection. `ca_gc_cleanup_unused()` iterates a `CaStore`, parses chunk IDs from chunk filenames before the dot, skips IDs in `used_chunks`, and removes unused chunk files and empty subdirectories unless dry-run is set. Verbose mode prints actions or summary.

## Control Flow

The typical flow is create collection, add one or more index files, optionally inspect usage/size, then pass the collection and a store to cleanup. Cleanup loops through the store iterator, parses each chunk filename, checks membership, prints if requested, unlinks unused chunks, tries to remove the containing subdirectory, counts removed chunks/directories, and prints summary for dry-run or verbose mode.

## State and Persistence Behavior

The collection is in-memory. `ca_gc_cleanup_unused()` mutates the store on disk by unlinking unused chunk files and possibly removing now-empty subdirectories. Dry-run mode avoids mutation. The code allocates a reusable `ids` buffer for filename parsing.

## Dependencies and Integration Points

It depends on `CaIndex` for reading index references, `CaStore` and `CaStoreIterator` for walking chunk files, `Set`/hashmap infrastructure for membership, `CaChunkID` parsing/formatting, and Linux `unlinkat()` flags. `gc.h` exposes flags and lifecycle.

## Risks and Edge Cases

There is an odd fragment in `ca_chunk_collection_add_index()`: after `r = ca_index_read_chunk(...)`, it has `if (r < 0)` followed immediately by `assert_se(r >= 0);`. This means negative read errors trigger an assertion before the later error handling, which is likely unintended and can abort instead of returning a logged error. Cleanup assumes chunk filenames contain a dot due to store iterator filtering and asserts that condition. Parse failures are logged and ignored, leaving the file untouched. Directory removal errors are ignored, which is fine for non-empty dirs but can hide permission issues.

## Test Signals

Tests should cover duplicate chunks across indexes, missing/bad index paths, index read error handling, dry-run no mutation, verbose output, malformed chunk filenames, unused chunk deletion, used chunk preservation, empty subdir removal, permission-denied unlink behavior, and collection usage versus unique size counts.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/gc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/gc.h -->
# sources/sync-backup/casync/src/gc.h

## Purpose

`gc.h` declares the chunk collection and store cleanup API for casync garbage collection.

## Important APIs, Types, and Functions

It forward-declares `CaChunkCollection`, declares creation/unref helpers, an inline cleanup helper, index ingestion, usage/size getters, flags `CA_GC_VERBOSE` and `CA_GC_DRY_RUN`, and `ca_gc_cleanup_unused(CaStore *store, CaChunkCollection *coll, unsigned flags)`.

## Control Flow

Callers build a collection from indexes and then pass it with a store to cleanup, optionally in dry-run or verbose mode.

## State and Persistence Behavior

The collection owns duplicated chunk IDs. Cleanup can mutate the store unless dry-run is passed.

## Dependencies and Integration Points

It includes `cachunk.h` and `castore.h`, binding GC to chunk ID and store abstractions while hiding the set implementation.

## Risks and Edge Cases

The cleanup helper does not null-check the pointer-to-pointer argument before dereferencing. Callers must observe ownership and dry-run semantics carefully.

## Test Signals

Header-level tests should compile cleanup macro use and flag combinations, and integration tests should validate collection lifecycle with store cleanup.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/gc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/gcc-macro.h -->
# sources/sync-backup/casync/src/gcc-macro.h

## Purpose

`gcc-macro.h` centralizes compiler attribute and branch prediction macros used across the C codebase.

## Important APIs, Types, and Functions

It defines `_printf_`, `_sentinel_`, `_unused_`, `_likely_`, `_unlikely_`, `_malloc_`, `_pure_`, `_packed_`, `_const_`, `_alloc_`, and `_fallthrough_`. `_alloc_` expands to `alloc_size` on GCC and empty on clang. `_fallthrough_` is enabled for GCC 7+ and empty otherwise.

## Control Flow

There is no runtime control flow. `_likely_` and `_unlikely_` influence compiler branch prediction. `_fallthrough_` annotates intentional switch fall-through.

## State and Persistence Behavior

No state is stored.

## Dependencies and Integration Points

This header is consumed by `util.h` and many source files that use attributes such as `_packed_` for on-disk formats or `_pure_` for helper declarations.

## Risks and Edge Cases

`_unused_` is defined twice identically. Attribute support is compiler-specific; clang gets an empty `_alloc_`. The macros are unnamespaced except for underscores and could conflict if included alongside other portability layers.

## Test Signals

Build tests with GCC and clang should verify no warnings/errors for attributes, switch fall-through annotations, packed structs, and format-string checking.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/gcc-macro.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/hash-funcs.c -->
# sources/sync-backup/casync/src/hash-funcs.c

## Purpose

`hash-funcs.c` provides reusable hash and comparison operations for the local hashmap/set implementation: strings, pointer identity, and `uint64_t` values.

## Important APIs, Types, and Functions

`string_hash_func()` hashes the NUL-terminated string including the terminator; `string_compare_func()` uses `strcmp()`. `string_hash_ops` packages them. `trivial_hash_func()` hashes the pointer value itself by compressing the address variable; `trivial_compare_func()` orders pointer values directly. `trivial_hash_ops` packages pointer-identity behavior. `uint64_hash_func()` hashes eight bytes at the pointed-to value; `uint64_compare_func()` compares dereferenced `uint64_t` values; `uint64_hash_ops` packages them.

## Control Flow

Each hash function feeds data into an existing siphash state; each compare function returns the standard negative/zero/positive relation expected by `hashmap.c`.

## State and Persistence Behavior

No state is stored. Hash randomization state is owned by the hashmap implementation's siphash key.

## Dependencies and Integration Points

The file depends on `hash-funcs.h`, which includes `siphash24.h` and `util.h`. `hashmap.c`, `set.h`, and callers use these `hash_ops` objects to specialize key behavior.

## Risks and Edge Cases

String functions require valid NUL-terminated strings. Trivial pointer comparison uses relational operators on unrelated object pointers, which is common in system code but can be implementation-defined in strict C terms. `uint64_hash_func()` requires aligned enough memory for dereference in the compare function.

## Test Signals

Tests should verify equal strings/uint64 values collide to equal compare results, different values compare nonzero, trivial ops distinguish different pointer addresses, and hash ops work through `Hashmap` and `Set` insertion/lookup/removal.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/hash-funcs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/hash-funcs.h -->
# sources/sync-backup/casync/src/hash-funcs.h

## Purpose

`hash-funcs.h` declares the hash operation interface used by `hashmap.c` and predefined hash/comparison implementations.

## Important APIs, Types, and Functions

It defines `hash_func_t`, `compare_func_t`, and `struct hash_ops` with `.hash` and `.compare` callbacks. It declares string, trivial pointer, and `uint64_t` hash/compare functions plus their exported `hash_ops` instances. Attributes mark compare functions as pure/const where appropriate.

## Control Flow

The hashmap implementation initializes siphash state and calls the `.hash` callback, then uses `.compare` when scanning candidate buckets.

## State and Persistence Behavior

The header has no state. The external `hash_ops` objects are immutable.

## Dependencies and Integration Points

It includes `util.h` for attributes/macros and `siphash24.h` for the hash state type. `hashmap.h` includes this header to let callers choose key behavior.

## Risks and Edge Cases

Callers must select hash ops that match key ownership and representation. Using `trivial_hash_ops` for strings or `string_hash_ops` for non-NUL data will produce incorrect behavior or memory errors.

## Test Signals

Compile tests should verify callback signatures and const/pure attributes; runtime tests should use each ops object in maps and sets with representative keys.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/hash-funcs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/hashmap.c -->
# sources/sync-backup/casync/src/hashmap.c

## Purpose

`hashmap.c` is a systemd-derived open-addressed Robin Hood hashmap implementation with three public container shapes: `Hashmap` key/value maps, `OrderedHashmap` maps that preserve insertion order, and `Set` key-only containers. It provides allocation, lookup, insertion, replacement, removal, iteration, merge/move/copy, string-vector extraction, and set convenience helpers.

## Important APIs, Types, and Functions

The file defines bucket entry structs for plain maps, ordered maps, and sets. `HashmapBase` contains common hash ops, direct or indirect storage, type bits, direct-entry count, mempool flag, and optional debug fields. Direct storage keeps tiny maps allocation-light using bytes embedded in `HashmapBase`; indirect storage uses heap storage for buckets plus DIB bytes and per-table hash key. `hashmap_type_info` records head size, entry size, mempool, and direct bucket capacity per type.

Robin Hood state uses DIB (distance from initial bucket) bytes with sentinel values for overflow, rehash, and free. Special virtual indexes `IDX_PUT` and `IDX_TMP` are swap buckets used during insertion and resize. `IDX_FIRST` and `IDX_NIL` support iteration.

Allocation APIs are `internal_hashmap_new()`, `internal_ordered_hashmap_new()`, `internal_set_new()`, and ensure-allocated variants. Free/clear APIs include `internal_hashmap_free()`, `internal_hashmap_free_free()`, `hashmap_free_free_free()`, `internal_hashmap_clear()`, `internal_hashmap_clear_free()`, and `hashmap_clear_free_free()`.

Core helpers include `bucket_hash()`, `get_hash_key()`, `bucket_at()`, `dib_raw_ptr()`, `bucket_calculate_dib()`, `bucket_move_entry()`, `base_remove_entry()`, `hashmap_put_robin_hood()`, `hashmap_base_put_boldly()`, `resize_buckets()`, and `base_bucket_scan()`.

Public operations implemented here include `hashmap_put()`, `set_put()`, `hashmap_replace()`, `hashmap_update()`, `internal_hashmap_get()`, `hashmap_get2()`, `internal_hashmap_contains()`, `internal_hashmap_remove()`, `hashmap_remove2()`, `hashmap_remove_and_put()`, `set_remove_and_put()`, `hashmap_remove_and_replace()`, `hashmap_remove_value()`, first/steal-first helpers, size/bucket count, merge, reserve, move, move-one, copy, `internal_hashmap_get_strv()`, `ordered_hashmap_next()`, `set_consume()`, `set_put_strdup()`, and `set_put_strdupv()`.

## Control Flow

Insertion hashes the key with siphash and the container's hash ops, scans for an existing key with Robin Hood early termination, places the new key/value in `IDX_PUT`, resizes if needed, appends insertion-order links for ordered maps, and uses `hashmap_put_robin_hood()` to find or displace buckets until a free slot appears. Resizing upgrades direct storage to indirect storage when necessary, grows bucket storage, generates a new hash key, marks existing entries as needing rehash, then reinserts them using the same Robin Hood logic.

Lookup computes the initial bucket and linearly scans while DIB values show candidates can still exist. If a free bucket appears or the current DIB is smaller than the probe distance, the key cannot be present. Removal uses backward-shift deletion: it removes the bucket from ordered iteration links when applicable, shifts following displaced entries backward until a free or zero-DIB bucket, updates DIB values, marks the final bucket free, and decrements entry count.

Iteration is type-aware. Ordered maps traverse insertion links; plain maps/sets scan storage order. The iterator stores the next key pointer so removal of the current entry during iteration can be tolerated despite backward shifts. With `ENABLE_DEBUG_HASHMAP`, debug counters assert that new insertions or unrelated removals do not happen during iteration.

Move/merge/copy operations reuse lower-level insertion/removal. `internal_hashmap_move()` pre-reserves for the worst case to avoid partial moves on allocation failure. `set_consume()` transfers ownership of a heap value into a set and frees it if it already existed or insertion failed without needing the value.

## State and Persistence Behavior

Container state is in heap or mempool-allocated objects. Direct storage stores buckets and DIBs in the base object. Indirect storage stores heap memory containing all buckets followed by DIB bytes and an independent hash key. A process-global `shared_hash_key` is used for all tiny direct-storage maps; larger maps get randomized keys from `random_bytes()`. Debug builds maintain a global linked list protected by a mutex for GDB inspection.

No filesystem persistence exists. Ownership behavior depends on the free variant: plain free keeps keys/values, free_free frees values, free_free_free frees both keys and values for plain maps; set freeing through `set_free_free()` is implemented through the shared internal paths.

## Dependencies and Integration Points

The implementation depends on `hashmap.h`, `hash-funcs.h`, `set.h`, `mempool.h`, `list.h` in debug builds, siphash, random byte generation, allocation helpers, and utility macros from `util.h`. `gc.c` uses `Set` with custom chunk hash ops. Many casync/systemd utility structures likely depend on this hashmap API.

## Risks and Edge Cases

The implementation is performance-sensitive and invariant-heavy. Bugs in DIB calculation, resize rehashing, virtual swap indexes, or ordered link repair can produce hard-to-debug corruption. The direct-storage shared hash key is acceptable for tiny maps but reduces per-map hash isolation. `is_main_thread()` is hardcoded false, disabling mempool use despite `DEFINE_MEMPOOL()` declarations. Pointer-based trivial compare uses relational pointer comparison. Iteration permits only current-entry removal; debug builds catch more misuse than release builds.

Allocation failure during `hashmap_put()` can leave no insertion, but move operations explicitly pre-reserve to prevent partial migration. `hashmap_remove_and_replace()` has careful compensation for backward shift when removing a duplicate new key; this path deserves regression coverage. `internal_hashmap_get_strv()` assumes `h` is non-null and uses `n_entries(h)` directly. Ordered hashmap insertion links use virtual `IDX_PUT` before the bucket is finalized, so `bucket_move_entry()` must repair links correctly.

## Test Signals

Tests should cover direct-storage and indirect-storage thresholds for map, ordered map, and set; random-heavy insertion/deletion/lookup versus a reference map; ordered iteration after insert/remove/backward shifts; removal during iteration; resize from direct to indirect; DIB overflow via adversarial hash ops; replace/update/remove_and_put/remove_and_replace paths; duplicate set consume freeing; merge/move/copy semantics; `hashmap_get2()` key return; `steal_first` loops; null-map read operations; allocation-failure injection around resize; and debug iterator assertions in `ENABLE_DEBUG_HASHMAP` builds.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/hashmap.c -->
