# Research: subset-b-009119

Grouped research report for the casync source files assigned to `subset-b-009119`. Each section is source-path aligned and wrapped for reconciliation splitting.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/camatch.c -->
# sources/sync-backup/casync/src/camatch.c

## Purpose
`camatch.c` implements the mutable and normalized representation of casync path match rules. It parses gitignore-like positive and negative glob patterns into a `CaMatch` tree, propagates unanchored rules into child directory subtrees, normalizes duplicate branches, and answers one-component match queries during archive tree traversal.

## Important APIs, Types, and Functions
The implementation revolves around `CaMatch` from `camatch.h`. `ca_match_new_from_file()` reads a pattern file via `openat()` and `read_line()`, ignoring blank lines and comments. `ca_match_new_from_strings()` builds the same structure from a string vector. `parse_line()` splits one rule into path components, rejects empty, `.` and `..` components, detects negation with `!`, marks patterns as anchored when they contain `/`, and sets `directory_only` when a component is followed by a slash. `ca_match_add_child()`, `ca_match_merge()`, `ca_match_make_writable()`, and `ca_match_normalize()` implement reference-counted tree mutation, copy-on-write, sorting, and duplicate subtree merging. `ca_match_test()` is the runtime matcher, returning positive match, negative match, no match, and optionally a subtree for recursion.

## Control Flow
Construction starts with `ca_match_alloc_subtree()`, creating an anchored directory-only inner root. Each input line is parsed into a chain of `CA_MATCH_INNER` nodes for intermediate directories and a `CA_MATCH_POSITIVE` or `CA_MATCH_NEGATIVE` leaf for the final component. Normalization recursively sorts children by type, name, anchoring, directory-only flag, and children, then attempts adjacent merges. Matching iterates direct children, carries unanchored directory rules forward into a returned subtree, applies `fnmatch(..., FNM_PERIOD)`, and gathers second-level children for matching directories. Negative matches override positives at the current level through the final `has_negative ? false : has_positive` decision.

## State and Persistence
State is entirely in-memory and reference-counted. The object is immutable by convention once shared; write operations reject shared nodes or copy before modification. File persistence is limited to reading match rules from a caller-supplied directory file descriptor and filename. No normalized representation is written back to disk.

## Dependencies and Integration Points
This file depends on `util.h` helpers for allocation, string vectors, cleanup attributes, line reading, and string predicates. It uses libc `fnmatch()` for glob evaluation. `caencoder.c` includes `camatch.h`, so these rules are integrated into archive encoding and filesystem traversal decisions.

## Risks
The parser accepts only a strict path-component grammar; escaped `!`, whitespace-sensitive patterns, and full gitignore semantics are not implemented. `fnmatch()` errors other than no-match become `-EINVAL`, so malformed patterns can surface late. Normalization is best-effort: failures can leave an equivalent but not fully normalized tree. The return value from `ca_match_test()` is easy to misuse because `0` means either no positive match or a negative match unless the caller tracks policy.

## Test Signals
`test/test-camatch.c` exercises string parsing, node attributes, normalization, subtree propagation, positive and negative matches, anchored paths, directory-only rules, and equality checks. Additional useful tests would cover invalid input lines, file-based parsing, repeated normalization after merge failures, and patterns with leading/trailing duplicate slashes.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/camatch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/camatch.h -->
# sources/sync-backup/casync/src/camatch.h

## Purpose
`camatch.h` declares the match-rule tree used by casync traversal code to include or exclude files and directories. It exposes the `CaMatch` structure, node type enum, lifecycle functions, tree mutation helpers, normalization, matching, dumping, and equality checks.

## Important APIs, Types, and Functions
`CaMatchType` has `CA_MATCH_POSITIVE`, `CA_MATCH_NEGATIVE`, and `CA_MATCH_INNER`. `struct CaMatch` contains a reference count, type, `anchored` and `directory_only` bitfields, a dynamically allocated child pointer array, allocation counters, and an inline `name[]`. Public constructors are `ca_match_new_from_file()` and `ca_match_new_from_strings()`. Public operations are `ca_match_ref()`, `ca_match_unref()`, `ca_match_add_child()`, `ca_match_merge()`, `ca_match_normalize()`, `ca_match_test()`, `ca_match_dump()`, and `ca_match_equal()`.

## Control Flow
The header reflects a tree API where callers build or parse a root, normalize it, then repeatedly call `ca_match_test()` while walking directories. If the caller supplies `ret` to `ca_match_test()`, the callee returns a new subtree representing rules to apply below a matched directory.

## State and Persistence
`CaMatch` objects are heap allocated and reference counted. Children are strong references. The structure deliberately exposes internals, which tests and nearby code use directly, but modification should still go through the declared helpers to preserve ownership rules.

## Dependencies and Integration Points
The header includes standard boolean, stdio, and sys/types headers. It is consumed by `camatch.c` and by encoder/traversal code that needs per-directory match state.

## Risks
The public structure makes ABI and invariant changes risky. Callers can bypass copy-on-write by mutating fields directly. `ca_match_children()` treats `NULL` as empty, which is convenient but can mask missing initialization.

## Test Signals
`test/test-camatch.c` directly validates several structure fields and API outcomes. Compile-time consumers also exercise this header through `caencoder.c`.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/camatch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/canametable.c -->
# sources/sync-backup/casync/src/canametable.c

## Purpose
`canametable.c` implements `CaNameTable`, a compact context object that records filename hashes and archive offsets for directory entries, plus parent directory context. It is used by location/archive metadata to reconstruct where entries were serialized and to support deterministic lookup structures.

## Important APIs, Types, and Functions
`ca_name_table_new_size()` allocates a flexible-array table with at least `START_ITEMS`. `ca_name_table_ref()` and `ca_name_table_unref()` manage ownership, including parent tables and cached formatted strings. `ca_name_table_make_writable()` implements copy-on-write and growth. `ca_name_table_add()` appends an item and invalidates the cached formatted representation. `ca_name_table_format_realloc_buffer()` and `ca_name_table_format()` serialize a table chain as `O<entry_offset>H<hash>S<start>X<end>...`. `ca_name_table_parse()` and `parse_one()` parse that representation recursively. `ca_name_table_make_bst()` sorts items and lays them out with `ca_make_bst()`. `ca_name_table_equal()` compares complete parent chains.

## Control Flow
Writers allocate or copy a table, append `CaNameItem` records, and optionally format the chain for embedding in a `CaLocation`. Parsing reads an `O` entry offset, then consumes zero or more `H/S/X` triples until another `O` begins a parent table or NUL terminates the string. BST conversion copies and sorts items by hash and start offset before placing them into a binary-search-tree array layout.

## State and Persistence
The table is in-memory, reference counted, and mostly immutable once shared. `formatted` caches the serialized string for reuse and is invalidated on append. Persistence is by embedding the formatted text in location strings rather than by a standalone file format.

## Dependencies and Integration Points
The module depends on `camakebst.h`, `realloc-buffer.h`, and utility parsing/allocation helpers. `calocation.h` includes `canametable.h`, and `test/test-calocation.c` validates name-table formatting and parsing through location round-trips.

## Risks
`ca_name_table_make_writable()` assumes `*t` is non-NULL in some copy paths even though it checks `if (!t)` only; callers currently pass initialized tables. Parsing accepts zero hex digits before numeric conversion, so behavior depends on `safe_atox64()`. Parent recursion can consume deeply nested strings and should be fuzzed. `ca_name_table_make_bst()` does not copy the source parent chain into the new table, which is correct only if callers want a single-level searchable table.

## Test Signals
`test/test-calocation.c` creates parent and child name tables, formats, parses, and checks equality as part of location ID testing. Additional tests should cover parse rejection, copy-on-write with shared references, BST ordering, and cached formatting invalidation after append.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/canametable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/canametable.h -->
# sources/sync-backup/casync/src/canametable.h

## Purpose
`canametable.h` declares the name-table data structures used to carry directory-entry archive context in `CaLocation` metadata. It defines a compact list of filename hashes and serialized archive offset ranges, optionally chained to a parent table.

## Important APIs, Types, and Functions
`CaNameItem` stores `hash`, `start_offset`, and `end_offset`. `CaNameTable` stores a reference count, parent pointer, `entry_offset`, item counts, a cached `formatted` string, and flexible-array `items[]`. Public functions allocate, reference, unreference, append, format, parse, convert to BST layout, dump, recursively dump, and compare tables. Inline accessors expose item counts, indexed lookup, and the last item.

## Control Flow
Callers normally allocate a table, append items as directory entries are serialized, attach parent context, then format it into a location string. Readers parse the string back into an equivalent table chain and may use the BST conversion for faster lookup.

## State and Persistence
State is heap-based and reference counted. `formatted` is a cached serialized representation owned by the table. Persistence is textual and embedded in higher-level metadata, not directly file-backed.

## Dependencies and Integration Points
The header depends on `util.h` and `realloc-buffer.h`. It is included by `calocation.h`, so it participates in location formatting, hardlink identity, and archive traversal metadata.

## Risks
Internals are public, so callers can mutate without invalidating `formatted` or respecting copy-on-write. Offset fields are unsigned 64-bit values; callers must avoid nonsensical ranges such as `end_offset < start_offset`.

## Test Signals
Indirectly tested by `test/test-calocation.c`. Header-level contract should be protected by tests for append/accessor behavior and parent-chain equality.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/canametable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/canbd.c -->
# sources/sync-backup/casync/src/canbd.c

## Purpose
`canbd.c` exposes a read-only Linux Network Block Device backed by data supplied from casync. It opens or finds `/dev/nbdN`, configures NBD ioctls, receives kernel read requests over a socketpair, and sends replies with caller-provided data.

## Important APIs, Types, and Functions
`struct CaBlockDevice` tracks the NBD device fd, socketpair, selected device path, helper ioctl process, last NBD request, exported size, friendly-name state, and device number. `ca_block_device_set_size()` enforces a positive 512-byte-aligned size. `ca_block_device_open()` opens a configured path or scans `/dev/nbd0` through `/dev/nbd1023`, attaches the socket with `NBD_SET_SOCK`, sets read-only block size and size, and forks a child blocked in `NBD_DO_IT`. `ca_block_device_step()` reads and validates one `struct nbd_request`. `ca_block_device_get_request_offset()`, `ca_block_device_get_request_size()`, and `ca_block_device_put_data()` implement request/response exchange. Friendly-name helpers create locked files under `/run/casync` for udev/tooling integration.

## Control Flow
The caller creates the object, sets size and optionally path/friendly name, then opens the device. After open, the caller polls `ca_block_device_get_poll_fd()` or `ca_block_device_poll()`, calls `ca_block_device_step()` until a request is available, fetches offset and size, reads bytes from the casync index/archive machinery, and completes the kernel request via `ca_block_device_put_data()`. Unref disconnects the NBD socket, clears it, kills the ioctl child, removes friendly-name files, and closes descriptors.

## State and Persistence
Runtime state is fd-heavy and process-backed. Persistent-ish side effects include `/run/casync/<device>` friendly-name files guarded by BSD locks. The object also mutates kernel NBD state and a block device read-only flag. No exported data is persisted by this module.

## Dependencies and Integration Points
This is Linux-specific, using `<linux/nbd.h>`, `<linux/fs.h>`, `ioctl()`, `socketpair()`, `poll()`, `flock()`, and `/dev/nbd*`. `casync-tool.c` includes `canbd.h`, and `test/test-nbd.sh.in` exercises `casync mkdev` against `/dev/nbd0` when root and NBD support are available.

## Risks
NBD setup requires privileges and loaded kernel support. Failure cleanup must keep kernel NBD devices from staying attached; the unref path is therefore critical. `ca_block_device_poll()` returns `1` even on timeout instead of the raw `ppoll()` result, so callers must still call `step()` to distinguish readiness. Friendly-name creation races are mitigated with locks and rename-noreplace, but failures can leave stale files if the process is killed at unfortunate points.

## Test Signals
`test/test-nbd.sh.in` covers an end-to-end mkdev readback digest when run as root with `/dev/nbd0`. Unit tests for invalid request headers, unaligned sizes, friendly-name replacement, and timeout behavior would strengthen coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/canbd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/canbd.h -->
# sources/sync-backup/casync/src/canbd.h

## Purpose
`canbd.h` declares the opaque `CaBlockDevice` API for serving casync data through Linux NBD. It lets higher-level code configure, open, poll, inspect, and answer block-device read requests.

## Important APIs, Types, and Functions
The enum return states are `CA_BLOCK_DEVICE_CLOSED`, `CA_BLOCK_DEVICE_REQUEST`, and `CA_BLOCK_DEVICE_POLL`. Public functions cover allocation/unref, size setup, device open, stepping, request offset/size getters, response writing, polling, path and friendly-name configuration, device-number retrieval, poll fd retrieval, and detection of `/dev/nbd*` paths.

## Control Flow
The expected sequence is allocate, configure size/path/name, open, poll/step, answer requests, and unref. The API exposes exactly one outstanding request at a time through `last_request` in the implementation.

## State and Persistence
The type is opaque to callers. State is held in file descriptors, a child process, kernel NBD attachment, and optional `/run/casync` friendly-name metadata.

## Dependencies and Integration Points
The header includes integer, signal, and sys/types definitions. `casync-tool.c` uses it to implement block-device presentation of archives.

## Risks
This API is Linux-specific despite the header not spelling out all kernel requirements. The caller must answer exactly the requested offset and size; `ca_block_device_put_data()` rejects mismatches.

## Test Signals
The shell NBD integration test is the main visible signal. Compile-time coverage comes through the `casync` tool build.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/canbd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/caorigin.c -->
# sources/sync-backup/casync/src/caorigin.c

## Purpose
`caorigin.c` tracks where a stream of bytes came from as a sequence of `CaLocation` objects. This is used by casync decode/cache paths to preserve provenance for reflinks and to describe sparse or void ranges.

## Important APIs, Types, and Functions
`ca_origin_new()`, `ca_origin_unref()`, and `ca_origin_flush()` manage the container. `ca_origin_put()` appends a `CaLocation`, merging with the previous location when `ca_location_merge()` allows it. `ca_origin_concat()` appends a full or byte-limited copy of another origin, including self-concat handling. `ca_origin_advance_items()` and `ca_origin_advance_bytes()` drop consumed leading provenance. `ca_origin_put_void()` appends or extends void ranges. `ca_origin_extract_bytes()` copies a prefix into a new origin. `ca_origin_dump()` prints formatted locations.

## Control Flow
The structure optimizes the first location separately from the `others` array. Appending first fills `first`; later appends attempt to merge into `first` or the last `others` item. Byte advancement first drops whole locations, then advances the first remaining location by patching its offset and size. Concatenation optionally snapshots self-references to avoid mutation while iterating.

## State and Persistence
State is in-memory only: strong references to `CaLocation` objects, count, capacity, and total byte count. Persistence occurs only through formatted `CaLocation` strings when dumped or stored elsewhere.

## Dependencies and Integration Points
The module depends on `calocation.h`. `cadecoder.h`, `casync.h`, `cacache.h`, and `caseed.h` include origin support, and `caseed.c` can return an origin for a served seed chunk.

## Risks
`ca_origin_advance_items()` assumes `origin->first` and sizes are valid and uses `assert(origin->n_bytes > drop_bytes)`, so corrupted state can abort. `ca_origin_concat()` returns `n > 0` even when a byte-limited concat consumed fewer items, so callers should not interpret positive values too specifically. The API rejects unknown-size locations in `ca_origin_put()`, while `ca_origin_put_void()` constructs known-size voids.

## Test Signals
`test/test-caorigin.c` covers append/merge behavior, byte advancement, self-concat, concat from another origin, and byte-limited concat. More edge tests should include exact-boundary advances, over-advances, void extension, and extraction.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/caorigin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/caorigin.h -->
# sources/sync-backup/casync/src/caorigin.h

## Purpose
`caorigin.h` declares the origin-provenance container used to describe the source locations for a byte stream. It is primarily useful for reflink-aware decoding and for reporting where returned seed data came from.

## Important APIs, Types, and Functions
`struct CaOrigin` stores `first`, `others`, item counts, allocation count, and total bytes. Public functions cover allocation, unref, flush, append, indexed lookup, concat, void insertion, item/byte advancement, prefix extraction, and dumping. Inline helpers return item and byte counts with `NULL` treated as empty.

## Control Flow
Callers append known-size locations as bytes are produced, then advance or extract prefixes as bytes are consumed by downstream readers.

## State and Persistence
All state is heap owned and references `CaLocation` instances. The header exposes internals, so invariants depend on disciplined callers.

## Dependencies and Integration Points
The header includes `calocation.h` and is consumed by decoder, cache, public sync, and seed APIs.

## Risks
Public structure mutation can break the byte count and merge invariants. Ownership of returned `CaLocation*` from `ca_origin_get()` remains with the origin; callers must ref it if retained.

## Test Signals
`test/test-caorigin.c` directly exercises the declared API.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/caorigin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/caprotocol-util.c -->
# sources/sync-backup/casync/src/caprotocol-util.c

## Purpose
`caprotocol-util.c` provides a small diagnostic helper that maps binary casync protocol frame type constants to human-readable names.

## Important APIs, Types, and Functions
`ca_protocol_type_name(uint64_t u)` switches over every frame type declared in `caprotocol.h`: hello, index, index-eof, archive, archive-eof, request, chunk, missing, goodbye, and abort. Unknown values return `NULL`.

## Control Flow
The function is a straight switch used by logging/debugging paths. It has no side effects.

## State and Persistence
No state or persistence.

## Dependencies and Integration Points
It includes `caprotocol-util.h` and `caprotocol.h`. `caremote.c` includes this helper and has commented debug logging that would print frame names.

## Risks
New protocol frame constants require updating this switch or diagnostics will lose names. Returning `NULL` requires callers to tolerate missing names.

## Test Signals
No direct test is visible. A low-cost unit test could assert all known constants map to non-NULL strings and unknown constants map to `NULL`.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/caprotocol-util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/caprotocol-util.h -->
# sources/sync-backup/casync/src/caprotocol-util.h

## Purpose
`caprotocol-util.h` declares the protocol type-name helper used for frame diagnostics.

## Important APIs, Types, and Functions
It includes `<inttypes.h>` and `caprotocol.h`, then declares `const char *ca_protocol_type_name(uint64_t u);`.

## Control Flow
There is no control flow in the header; it exposes the mapping function to users of the protocol definitions.

## State and Persistence
No state or persistence.

## Dependencies and Integration Points
Consumers include `caremote.c`. The header depends on protocol constants from `caprotocol.h`.

## Risks
The header has no include guard despite being tiny; repeated inclusion is harmless for this declaration but inconsistent with the rest of the source tree.

## Test Signals
Covered only by build success unless explicit tests are added for the implementation.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/caprotocol-util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/caprotocol.h -->
# sources/sync-backup/casync/src/caprotocol.h

## Purpose
`caprotocol.h` defines the binary frame protocol spoken between `CaRemote` and helper subprocesses such as `casync-http` or remote `casync` over ssh. It describes pull and push handshakes, frame type IDs, feature flags, and packed frame structures.

## Important APIs, Types, and Functions
The enum of frame type constants assigns fixed 64-bit magic values to hello, file streaming, request, chunk, missing, goodbye, and abort frames. `CaProtocolHeader` carries little-endian size and type fields; `CA_PROTOCOL_SIZE_MIN` and `CA_PROTOCOL_SIZE_MAX` bound frame size. Structures include `CaProtocolHello`, `CaProtocolFile`, `CaProtocolFileEOF`, `CaProtocolRequest`, `CaProtocolChunk`, `CaProtocolMissing`, `CaProtocolGoodbye`, and `CaProtocolAbort`. Feature flags distinguish services provided, such as readable/writable store/index/archive, from requested operations, such as pulling or pushing chunks/index/archive.

## Control Flow
The comment block documents the protocol: both sides send hello; pull sends index from server then client requests chunks and receives chunks; push sends index from client then server requests chunks and receives chunks or missing markers; goodbye and abort terminate flows.

## State and Persistence
This header defines wire state, not runtime state. Frames are serialized with little-endian integer fields and flexible payload arrays. The maximum frame size is 16 MiB.

## Dependencies and Integration Points
It includes `util.h` for endian types and `cachunkid.h` for chunk ID size. `caremote.c` validates and emits these frames, while `casync-http.c` feeds HTTP/FTP/SFTP data into the same frame stream.

## Risks
The protocol uses C structs with flexible arrays as wire overlays; all readers must validate sizes before access. Any change to constants or layout breaks compatibility. The comment says `CA_PROTOCOL_ABORTED` in one sentence, while the actual constant is `CA_PROTOCOL_ABORT`.

## Test Signals
Remote/protocol behavior is exercised indirectly by integration tests that set `CASYNC_PROTOCOL_PATH` and run casync script flows. Frame-level fuzz tests exist under `test/fuzz` generally, but no specific direct test was visible in this read.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/caprotocol.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/caremote.c -->
# sources/sync-backup/casync/src/caremote.c

## Purpose
`caremote.c` implements casync's remote transport engine. It manages feature negotiation, subprocess or fd-based I/O, framed protocol parsing/emission, disk-backed chunk request queues, local cache storage for received chunks, streamed index/archive files, chunk validation, and cooperative step/poll operation.

## Important APIs, Types, and Functions
`struct CaRemote` stores connection state, URL/callout configuration, cache configuration, input/output fds, input/output/chunk/validation buffers, queue cursors, feature flags, index/archive file state, last chunk, subprocess pid, digest/compression configuration, and request statistics. Public setters configure feature flags, URLs, cache, local files/fds, digest, compression, log level, and rate limit. The core engine is `ca_remote_step()` and `ca_remote_poll()`. Pull APIs include `ca_remote_request()`, `ca_remote_request_async()`, and `ca_remote_next_chunk()`. Push APIs include `ca_remote_next_request()`, `ca_remote_can_put_chunk()`, `ca_remote_put_chunk()`, and `ca_remote_put_missing()`. File streaming APIs cover index and archive read/write/eof. Termination APIs are `ca_remote_goodbye()` and `ca_remote_abort()`.

## Control Flow
`ca_remote_start()` validates local flags, starts an ssh/helper subprocess when fds were not injected, opens configured index/archive paths according to negotiated direction, and transitions after hello negotiation. `ca_remote_step()` clears transient file buffers, starts the remote, flushes output, sends hello, processes one input frame, sends queued requests, streams index, streams archive, and reads more input, returning status codes that tell callers whether to poll or react. `ca_remote_process_message()` validates frame size/type/state and dispatches to hello, index/archive, request, chunk, missing, goodbye, or abort handlers. Request sending batches IDs with matching priority into a single request frame while output is below a low watermark.

## State and Persistence
The remote cache is a directory, caller-provided or temporary, containing chunk files plus symlink queue directories `chunks/`, `low-priority/`, and `high-priority/`. Temporary caches are removed on unref; non-temporary caches have queue symlinks removed. Index/archive writes go through temporary paths and are renamed into place on completion/goodbye. Queue cursors are in memory, while symlink farms persist enough to check duplicate queued chunks. Request counters track successful chunk reads and bytes.

## Dependencies and Integration Points
The module depends on protocol definitions, chunk file helpers, compression/digest helpers, realloc buffers, rm-rf cleanup, process execution, poll, and utility code. `casync.c` and `casync-tool.c` include `caremote.h` for high-level sync operations. `casync-http.c` is one helper that speaks this protocol over stdio. The remote callout resolution uses `CASYNC_PROTOCOL_PATH`, `CASYNC_SSH_PATH`, and `CASYNC_REMOTE_PATH`.

## Risks
The state machine is sensitive to feature-flag compatibility and direction checks. Disk-backed queues use symlinks and in-memory cursors, so partial cache reuse or external mutation can produce stale or skipped entries. `ca_remote_set_archive_fd()` appears to call `ca_remote_file_set_fd(&rr->index_file, fd)` instead of `archive_file`, which would misdirect archive fd configuration. `ca_remote_abort()` calls `strlen(message)` without a NULL check. The subprocess child path has branches that call `return log_oom()` after fork instead of `_exit`, which is worth auditing. Digest autodetection is flexible but can hide mismatched expected algorithms unless callers set a digest explicitly.

## Test Signals
End-to-end script tests exercise remote helpers through `CASYNC_PROTOCOL_PATH`, especially make/extract flows and seed use. There is no focused unit test visible for frame validation, queue ordering, subprocess argument construction, or the archive fd setter. These are high-value test targets.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/caremote.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/caremote.h -->
# sources/sync-backup/casync/src/caremote.h

## Purpose
`caremote.h` declares the opaque remote transport API used by casync to pull or push chunks, indexes, and archive streams over helper protocols.

## Important APIs, Types, and Functions
The main status enum reports poll, finished, step, request, write-index, write-archive, chunk, read-index, index-eof, read-archive, and archive-eof conditions. Argument-position constants define how helper subprocesses receive operation, base URL, archive URL, index URL, and writable store URL. Public functions cover lifecycle, feature flags, digest/compression, logging/rate limiting, fds, URL/path/fd configuration, stepping/polling, chunk request/response, index/archive streaming, goodbye/abort, pending/unwritten/chunk queries, cache forgetting, and statistics.

## Control Flow
Callers configure a `CaRemote`, then repeatedly call `ca_remote_step()` and `ca_remote_poll()`. Status codes drive whether the caller should provide index/archive data, serve requested chunks, consume received data, or wait for I/O.

## State and Persistence
The `CaRemote` implementation is opaque. Persistent side effects may include cache directories and configured index/archive path writes.

## Dependencies and Integration Points
The header includes chunk and chunk ID types. It is consumed by `casync.c`, `casync-tool.c`, and helper implementations such as `casync-http.c`.

## Risks
The API has many direction-dependent operations that return `-ENOTTY`, `-EAGAIN`, `-EPIPE`, or status enums; callers must handle these carefully. The lack of visible type state in the header makes misuse possible until runtime.

## Test Signals
Integration tests provide broad coverage. Focused tests should target all status transitions and setter combinations.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/caremote.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/caseed.c -->
# sources/sync-backup/casync/src/caseed.c

## Purpose
`caseed.c` builds and serves a local seed cache from an existing filesystem tree or file. It runs a `CaEncoder`, chunk-splits emitted payload bytes, records chunk ID to source-location mappings, optionally records hardlink targets, and later serves matching chunks by seeking back into the encoder source and revalidating content.

## Important APIs, Types, and Functions
`struct CaSeed` stores the encoder, base/cache fds and path, chunker, digest, mode flags, pending chunk buffer and location, file root, feature flags, counters, and timing. `ca_seed_open()` initializes the encoder and cache directory. `ca_seed_cache_chunks()` scans encoder data through `ca_chunker_scan()`, buffers chunk spans across encoder data boundaries, and writes cache entries. `ca_seed_write_cache_entry()` computes the chunk ID, formats a full `CaLocation`, and stores it as a symlink or fallback file under `<first4>/<id>`. `ca_seed_cache_hardlink()` maps hardlink digests to entry locations. `ca_seed_step()` advances the encoder and updates the cache. `ca_seed_get()` looks up a chunk location, seeks the encoder, reconstructs the bytes, optionally builds a `CaOrigin`, and verifies the chunk ID before returning data.

## Control Flow
Callers configure base and cache, then call `ca_seed_step()` until `CA_SEED_READY`. During stepping, encoder events produce data, next-file, done-file, payload, or finished states. Data-bearing states feed chunk cache creation; done-file can add hardlink metadata; finished flushes a final partial chunk. Once ready or partially indexed, `ca_seed_get()` reads the cache entry, rejects unknown-size hardlink entries for normal chunk lookup, seeks the encoder, copies bytes until the requested chunk size is satisfied, validates the digest, and returns a buffer owned by the seed object.

## State and Persistence
The cache is a directory tree keyed by chunk ID prefix. Normal entries are symlinks to formatted `CaLocation` strings; too-long targets are stored as regular files. Temporary caches are removed on unref. Runtime buffers are reused, so returned data and origins must be consumed according to API ownership expectations. Timing fields record first and last seed step times.

## Dependencies and Integration Points
The module depends on chunking, digest, encoder, file root, format, location, origin, rm-rf, time, and realloc-buffer helpers. `casync.c` uses seeds to satisfy missing chunks from local data during extraction and to support hardlink/reflink optimizations.

## Risks
The seed cache can become stale if source files change; `ca_seed_get()` detects some cases via seek failures, premature EOF, and final digest mismatch returning `-ESTALE`. Cache entries stored as symlinks expose location strings in filesystem metadata and can hit `ENAMETOOLONG`, hence the regular-file fallback. `ca_seed_cache_final_chunk()` returns `0` even if `ca_seed_write_cache_entry()` fails, apparently swallowing the error. The shared `buffer` is used for both chunk assembly and serving, so reentrant use is unsafe.

## Test Signals
`test/test-nbd.sh.in` and script tests exercise seed extraction by extracting with `--seed` and comparing digests. No focused unit test for `CaSeed` internals was visible. Useful tests include stale source mutation, hardlink target lookup, long location fallback files, disabled chunk/hardlink modes, and final chunk error propagation.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/caseed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/caseed.h -->
# sources/sync-backup/casync/src/caseed.h

## Purpose
`caseed.h` declares the opaque seed API for indexing local data and serving chunks or hardlink targets from that seed.

## Important APIs, Types, and Functions
The status enum exposes `CA_SEED_READY`, `CA_SEED_STEP`, `CA_SEED_NEXT_FILE`, and `CA_SEED_DONE_FILE`. Public functions configure base/cache fd or path, step indexing, get or test chunks, get hardlink targets, inspect current path/mode during indexing, set feature flags and chunk sizes, enable hardlink/chunk caching, retrieve a `CaFileRoot`, and read request/time statistics.

## Control Flow
Callers configure the seed, step until ready while optionally displaying current file progress, then use `ca_seed_get()` or `ca_seed_has()` to satisfy chunk requests.

## State and Persistence
The object is opaque. Implementation state includes a cache directory, encoder state, chunk buffers, and request counters. Returned chunk data is owned by the seed object.

## Dependencies and Integration Points
The header includes chunk ID and origin types. It integrates with higher-level sync extraction and cache code.

## Risks
Consumers must handle `-EUNATCH`, `-ENOMEDIUM`, `-ESTALE`, and ownership of optional returned origins. The API does not advertise thread safety; implementation is stateful and single-consumer.

## Test Signals
Covered through end-to-end seed extraction scripts. Unit coverage would be valuable for status transitions and error codes.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/caseed.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/castore.c -->
# sources/sync-backup/casync/src/castore.c

## Purpose
`castore.c` implements a filesystem-backed chunk store. It can read, validate, write, test, and iterate `.cacnk` chunk files, with optional temporary-cache cleanup and configurable compression/digest behavior.

## Important APIs, Types, and Functions
`struct CaStore` stores the root path, cache/mkdir flags, reusable read buffer, validation digest/buffer, desired store compression, compression type, and request counters. `ca_store_new()` creates a normal compressed store; `ca_store_new_cache()` creates a temporary cache with as-is compression. `ca_store_get()` loads a chunk via `ca_chunk_file_load()`, decompresses for validation if needed, verifies the chunk ID using an explicit or autodetected digest, returns the stored representation, and updates counters. `ca_store_put()` lazily creates a cache root if needed and saves via `ca_chunk_file_save()`. `ca_store_has()` calls `ca_chunk_file_test()`. `CaStoreIterator` walks subdirectories and returns `.cacnk` file entries.

## Control Flow
Callers set a path or rely on cache auto-allocation, then call get/has/put. Reads always empty and reuse the internal buffer before loading. Writes create the root directory once, then delegate naming/compression details to chunk-file helpers. Iteration opens the root directory, then each subdirectory, skipping entries that are not regular chunk files with `.cacnk` suffix.

## State and Persistence
Normal stores persist under the configured root. Cache stores auto-create a random directory under `var_tmp_dir()` and delete it on unref. Reusable buffers mean returned chunk data remains valid only until the next store operation. Counters track successful read requests and bytes returned.

## Dependencies and Integration Points
The module depends on chunk helpers, digest/compression helpers, directory iteration utilities, rm-rf, and realloc buffers. It is used by `casync.c`, `casync-tool.c`, and `gc.h` for chunk storage and garbage collection.

## Risks
`ca_store_get()` returns `r` from the last digest operation, which is normally `0`, after successful load; callers expecting positive success need to follow the actual contract. Autodigest fallback can accept chunks written with any supported digest unless explicitly pinned. Iterator error handling appears suspicious: if `openat()` fails because an entry is not a directory, checking `errno == EISDIR` will not skip regular files; `ENOTDIR` would be expected. Returned data is invalidated by subsequent calls.

## Test Signals
`test/test-casync.c` exercises store put/get indirectly through full encode/decode. Additional tests should directly cover compressed/uncompressed read validation, digest pinning, cache cleanup, iterator traversal, and malformed chunks.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/castore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/castore.h -->
# sources/sync-backup/casync/src/castore.h

## Purpose
`castore.h` declares the chunk store API used to persist and retrieve casync chunk files.

## Important APIs, Types, and Functions
It declares opaque `CaStore` and `CaStoreIterator`. Public functions cover normal/cache construction, unref, path setup, compression setup, chunk get/has/put, request statistics, digest selection, iterator construction/unref, and iterator next.

## Control Flow
Callers configure a store path and compression policy, then use get/has/put. Iterators produce root fd, subdir name/fd, and chunk filename tuples until they return `0`.

## State and Persistence
Implementation state is opaque. Stores may persist data under configured roots or remove temporary cache roots when unreferenced.

## Dependencies and Integration Points
The header includes `cachunk.h`, `cachunkid.h`, and `cautil.h`. It is included by public sync and garbage-collection code.

## Risks
Returned chunk data from `ca_store_get()` is implementation-owned. Iterator outputs are only valid until the next iterator advancement or close.

## Test Signals
End-to-end encode/decode tests cover basic store operation. Direct iterator and compression policy tests would improve confidence.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/castore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/casync-http.c -->
# sources/sync-backup/casync/src/casync-http.c

## Purpose
`casync-http.c` is the HTTP/HTTPS/FTP/SFTP helper subprocess used by `CaRemote`. It speaks the casync remote frame protocol on stdin/stdout and uses libcurl to fetch archive, index, and chunk URLs from remote stores.

## Important APIs, Types, and Functions
Global arguments capture protocol, verbosity, log level, rate limit, and quit signals. `robust_curl_easy_perform()` retries transient `CURLE_COULDNT_CONNECT` failures with linear backoff. `process_remote()` drives a `CaRemote` until a requested condition is met, such as writable buffers, pending requests, unwritten output, or finish. `write_index()`, `write_index_eof()`, `write_archive()`, and `write_archive_eof()` bridge curl callbacks to remote file frames. `write_buffer()` accumulates curl data with protocol-size bounds. `chunk_url()` constructs `<store>/<first4>/<chunk>.cacnk`. `acquire_file()` fetches index/archive URLs and aborts the remote on protocol-level failures. `run()` configures `CaRemote`, configures curl, streams archive/index, then loops serving chunk requests from one or more stores.

## Control Flow
`main()` installs signal handlers, parses protocol from argv[0], parses options, and supports only the `pull` verb. `run()` converts dash placeholders to NULL URLs, advertises readable services based on provided URLs/stores, binds the remote to stdio, configures curl protocol limits and optional rate limiting, fetches archive and index first, then waits for chunk request frames. For each chunk request it builds a URL, fetches into a buffer, sends either `CA_PROTOCOL_CHUNK` with compressed data or `CA_PROTOCOL_MISSING`, flushes remote output, and repeats until no stores or remote EOF.

## State and Persistence
The helper itself persists nothing. It buffers downloaded data in memory up to frame limits and relies on `CaRemote` for protocol buffers. Curl may use `.netrc` optionally for credentials. Signal handlers set a global quit flag for graceful termination.

## Dependencies and Integration Points
The file depends on libcurl, `caprotocol.h`, `caremote.h`, `cautil.h`, `realloc-buffer.h`, and utility logging/parsing. `caremote.c` launches helpers named `casync-<scheme>` from `CASYNC_PROTOCOL_PATH` for URL-style remotes, so this binary is selected by executable name containing http, https, ftp, or sftp.

## Risks
Only `pull` is implemented; pushing via HTTP is not supported here. HTTP 404 maps to `ENOMEDIUM`, while other HTTP/FTP/SFTP failures abort or produce missing chunks depending on phase. `chunk_url()` strips query/semicolon suffixes and trailing slashes, so unusual store URLs need coverage. `write_buffer()` protects frame size but accumulates whole chunks/index fragments in memory. The store rotation variable `current_store` is not incremented in the visible loop, so fallback stores may not actually rotate.

## Test Signals
Script tests that use `CASYNC_PROTOCOL_PATH` can exercise helper-based pull paths when the helper binaries are built. Additional tests should cover HTTP status handling, SFTP status handling, multi-store fallback rotation, rate-limit option parsing, and graceful signal exit.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/casync-http.c -->
