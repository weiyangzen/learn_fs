# Research Group: subset-b-009117

This grouped report covers the casync archive decoder and digest wrapper files. The decoder files implement the pull-style archive replay state machine used by higher-level casync restore/extract code, while the digest files provide the OpenSSL-backed hash abstraction used for chunk IDs, archive digests, payload digests, hardlink identity checks, cache validation, and store/remote validation.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/cadecoder.c -->
# sources/sync-backup/casync/src/cadecoder.c

## Purpose

`cadecoder.c` implements `CaDecoder`, the low-level reader/restorer for casync archive streams. It consumes serialized `CaFormat*` objects from `caformat.h`, validates them against feature flags and format ordering rules, exposes stream events to callers, optionally writes decoded filesystem objects under a configured base fd, supports archive and path seeking, and maintains optional digests for the full archive, current payload, and hardlink identity.

The file is the inverse of the encoder side and is driven by the high-level API in `casync.c`. Callers repeatedly invoke `ca_decoder_step()`, respond to request events by feeding bytes with `ca_decoder_put_data()` or `ca_decoder_put_eof()`, respond to seek/skip events with the requested input movement, and inspect current object metadata or payload data through the public accessors declared in `cadecoder.h`.

## Important APIs, Types, and Functions

The private `CaDecoder` object stores the replay state: current `CaDecoderState`, archive feature flags, replay mask, a fixed-depth `nodes[NODES_MAX]` path stack, a `ReallocBuffer` of unread input, optional `CaOrigin` tracking for reflinks, archive/payload offsets, seek target fields, delete/reflink/hardlink/payload booleans, UID shift/range configuration, digest objects, and counters for punch-hole, reflink, and hardlink bytes.

Each `CaDecoderNode` represents one path-stack entry. It caches the parsed entry object, name, temporary name, offsets for entry/payload/goodbye/end, mode and size for naked objects, user/group strings, symlink target, device number, SELinux label, xattrs, ACL lists, file capabilities, quota project ID, optional payload origin, directory child names used for deletion reconciliation, and realization flags such as `hardlinked`.

The central public functions are:

- Construction and configuration: `ca_decoder_new()`, `ca_decoder_unref()`, `ca_decoder_set_base_fd()`, `ca_decoder_set_boundary_fd()`, `ca_decoder_set_base_mode()`, `ca_decoder_set_archive_size()`, `ca_decoder_set_feature_flags_mask()`, `ca_decoder_set_expected_feature_flags()`, and boolean setters for punch holes, reflinks, hardlinks, deletion, payload delivery, and immutable-bit undo.
- Event loop: `ca_decoder_step()`, `ca_decoder_put_data()`, `ca_decoder_put_eof()`, `ca_decoder_get_request_offset()`, `ca_decoder_get_seek_offset()`, `ca_decoder_get_skip_size()`, and `ca_decoder_get_payload()`.
- Metadata accessors: `ca_decoder_current_path()`, mode/target/mtime/size/uid/gid/user/group/rdev/offset/chattr/FAT/xattr/quota helpers, and `ca_decoder_current_archive_offset()`.
- Seeking: `ca_decoder_seek_offset()`, `ca_decoder_seek_path()`, `ca_decoder_seek_path_offset()`, and `ca_decoder_seek_next_sibling()`.
- Digest and dedupe support: archive/payload/hardlink digest enable/get functions plus `ca_decoder_try_hardlink()`.

Key private functions include the validation helpers for every serialized object type, `ca_decoder_parse_entry()`, `ca_decoder_parse_filename()`, `ca_decoder_parse_goodbye_tail()`, `ca_decoder_do_seek()`, `ca_decoder_step_node()`, `ca_decoder_advance_buffer()`, `ca_decoder_realize_child()`, `ca_decoder_finalize_child()`, `ca_decoder_node_reflink()`, `ca_decoder_node_delete()`, ACL conversion helpers, UID/GID name resolution helpers, and `ca_decoder_install_file()`.

## Control Flow

The decoder starts in `CA_DECODER_INIT`. Once a base fd, boundary fd, or base mode is configured, the root node exists and `ca_decoder_step()` advances any previously consumed buffer with `ca_decoder_advance_buffer()`, then dispatches to `ca_decoder_step_node()`.

For directory-tree archives, `CA_DECODER_ENTERED` and `CA_DECODER_ENTERED_FOR_SEEK` parse an entry sequence with `ca_decoder_parse_entry()`. That parser accepts a strict order: one `ENTRY`, optional user/group names, sorted xattrs, ordered ACL records, SELinux/fcaps/quota metadata, and then one type-specific terminator such as `PAYLOAD`, `FILENAME`, `GOODBYE`, `SYMLINK`, or `DEVICE`. It returns `CA_DECODER_REQUEST` until complete objects are buffered, returns negative errors for malformed streams, and returns `CA_DECODER_NEXT_FILE` when a new file entry is available.

After `CA_DECODER_ENTRY`, the decoder realizes a child under the parent if filesystem output is enabled. Directories enter `CA_DECODER_IN_DIRECTORY`; regular files enter `CA_DECODER_IN_PAYLOAD`; symlinks, fifos, devices, and sockets move toward `CA_DECODER_FINALIZE`.

Payload handling computes a bounded `step_size`, updates enabled digests, returns `CA_DECODER_PAYLOAD` when bytes are available, writes data to the target fd during the following `ca_decoder_advance_buffer()` call, and increments payload/archive offsets. If payload delivery and local writing are not needed, the decoder can emit `CA_DECODER_SKIP` for known-size payloads. EOF is accepted only for root naked payloads of unknown size; otherwise premature EOF is an error.

Directory handling alternates between `FILENAME` records and child entries until a `GOODBYE` object is parsed. Child names are accumulated for optional deletion reconciliation unless seeking invalidated the directory listing. On `GOODBYE`, the node caches the goodbye table and later finalizes the directory.

Finalization walks back up the node stack. `ca_decoder_finalize_child()` performs reflink attempts, deletion of absent directory entries, ownership and permission replay, ACLs, xattrs, file capabilities, SELinux labels, timestamps, atomic installation from temporary names, chattr/FAT attribute replay, subvolume checks, and post-restore timestamp granularity verification. Once root finalization completes, the state becomes `CA_DECODER_EOF` and `CA_DECODER_FINISHED` is returned.

Seeking is a separate group of states. Naked-file offset seeking uses `CA_DECODER_PREPARING_SEEK_TO_OFFSET` and `CA_DECODER_SEEKING_TO_OFFSET`. Path seeking uses cached node offsets, loaded `GOODBYE` tables, known goodbye offsets, or archive end offsets to jump to filename, entry, payload, goodbye, or goodbye-tail positions. `format_goodbye_search()` uses SipHash over path components and handles hash collisions with `seek_idx`. On successful seek, digest state may be reset or invalidated, and a boundary node prevents iteration above the selected subtree.

## State and Persistence Behavior

Decoder state is in-memory and mutable. It owns buffered input, parsed object copies, path stack nodes, open file descriptors, cached NSS lookups, cached filesystem type information, optional digest contexts, and optional origin metadata. `ca_decoder_unref()` frees node allocations, closes owned fds at index 3 or above, releases origins, digest contexts, cached strings, and buffer storage.

Filesystem persistence is optional. With a base fd or boundary fd, the decoder creates directories, files, symlinks, fifos, devices, sockets, Btrfs subvolumes, attributes, xattrs, ACLs, labels, quota project IDs, timestamps, and deletion side effects under the target tree. Regular files are written through temporary names and installed with `renameat()`, `renameat2(RENAME_EXCHANGE)`, or remove-and-rename fallback. Directory deletion removes entries not present in the archive when deletion is enabled and directory names were collected without invalidation.

Digest state is persistent across steps but tied to stream position. Archive digests are available only at EOF. Payload and hardlink digests are available only while a current node is in finalization, and seeking into the middle of payloads marks them stale. `ca_digest_read()` finalizes the underlying OpenSSL context, so digest getters are terminal reads for the current digest context.

UID/GID shifting is applied when replaying numeric owners and ACL qualifiers. User/group names are resolved through `getpwnam_r()` and `getgrnam_r()` with a one-entry cache. Root names are specially synthesized by current accessors when user-name feature flags are active but root was suppressed in the archive.

## Dependencies and Integration Points

Internal dependencies include `cadecoder.h`, `caformat.h`, `caformat-util.h`, `cautil.h`, `chattr.h`, `quota-projid.h`, `realloc-buffer.h`, `reflink.h`, `rm-rf.h`, `siphash24.h`, `time-util.h`, and generic `util.h` helpers. It relies on `CaOrigin`/`CaLocation` for reflink provenance and on `cadigest.c` through `CaDigest`.

System dependencies include Linux file APIs, POSIX ACLs, xattrs, `statfs`, `renameat2`, Btrfs ioctls, Linux chattr/FAT attribute headers, optional SELinux APIs, NSS user/group lookup, and block/device helpers. Several replay paths are Linux-specific and intentionally return `-EOPNOTSUPP`, `-EEXIST`, or related errno values when the backing filesystem cannot represent archived metadata.

The main integration caller is `casync.c`, which configures decoder knobs, feeds local or remote archive bytes, satisfies request/seek/skip events, reads payloads for API clients, asks for hardlink digests, and invokes `ca_decoder_try_hardlink()` against seed roots. The decoder also shares digest semantics with `caencoder.c`, `cachunkid.c`, cache/store/remote code, and feature-flag digest selection from `caformat-util`.

## Risks and Edge Cases

The parser is intentionally strict. Small deviations in object order, duplicate metadata, feature-flag mismatch, invalid UID/GID ranges, unsorted xattrs or ACLs, invalid goodbye tail offsets, malformed names, unexpected object types, or impossible metadata/type combinations all fail with `-EBADMSG` or related errors. This is good for integrity but makes compatibility with future or alternate encoders sensitive.

Filesystem replay has a broad side-effect surface. Risks include replacing the wrong file when caller-provided fds or boundaries are wrong, non-atomic fallback when `RENAME_EXCHANGE` is unavailable, partial temporary files after errors, deletion of destination entries absent from the archive, privileged metadata operations failing after data writes, NSS lookup differences across hosts, filesystem timestamp granularity mismatches, SELinux/xattr/ACL capability differences, Btrfs-specific behavior, and immutable-bit handling requiring explicit enablement.

Seeking depends on known archive sizes, correct node end offsets, and valid goodbye tables. It returns `-ESPIPE` when insufficient offset information exists and marks payload/hardlink digests stale for mid-stream seeks. Hash collisions are handled by retrying `seek_idx`, but malformed goodbye offsets can still abort with integrity errors.

Digest and dedupe behavior has subtle ordering constraints. Payload and hardlink digests are reset at entry boundaries and are valid only for complete sequential reads. Hardlink optimization performs superficial metadata checks before linking; it can silently decline on cross-device, unsupported, changed, or incompatible files.

## Test Signals

High-value tests should drive `ca_decoder_step()` through complete archives and assert the expected sequence of `REQUEST`, `NEXT_FILE`, `PAYLOAD`, `DONE_FILE`, and `FINISHED` events for regular files, naked files, directories, symlinks, devices, and metadata-rich entries.

Parser tests should cover truncated headers, invalid sizes, repeated entries, unsupported feature flags, feature-flag mismatches, invalid names, bad UID/GID encodings, unordered xattrs/ACLs, missing required ACL masks, default ACLs on non-directories, invalid symlink targets, malformed device majors/minors, and broken goodbye tail offsets.

Replay tests should run on filesystems with and without xattr/ACL/SELinux/Btrfs/FAT support, verifying graceful unsupported errors, correct temporary-file installation, deletion behavior, immutable-bit undo, hole-punch counters, reflink counters, hardlink counters, UID/GID shifting, and timestamp granularity checks.

Seek tests should set archive size and exercise naked offset seeks, path seeks, path-plus-payload-offset seeks, next-sibling seeks, not-found paths, hash-collision retry behavior, stale digest results after mid-payload seeks, and boundary behavior after a successful path seek.

Integration tests through `casync.c` should confirm that remote/local archive feeding satisfies decoder request offsets, skip/seek events are honored exactly, archive/payload/hardlink digests match encoder output, and restore/extract operations preserve expected tree metadata.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/cadecoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/cadecoder.h -->
# sources/sync-backup/casync/src/cadecoder.h

## Purpose

`cadecoder.h` declares the public `CaDecoder` interface. It exposes an opaque decoder type, the event constants returned by `ca_decoder_step()`, configuration hooks for filesystem replay and stream behavior, input/output methods for archive bytes and payload bytes, current-entry metadata accessors, random-access seek controls, replay statistics, digest controls, and hardlink optimization entry points.

The header is the contract used by `casync.c` and any other decoder consumer. It hides the parser state machine and filesystem implementation details in `cadecoder.c` while documenting the caller-driven pull protocol through function names and comments.

## Important APIs, Types, and Constants

`typedef struct CaDecoder CaDecoder;` makes the decoder opaque. Consumers must allocate it with `ca_decoder_new()` and release it with `ca_decoder_unref()`.

The event enum defines stream progress, caller requests, and seek results:

- `CA_DECODER_FINISHED`, `CA_DECODER_STEP`, `CA_DECODER_NEXT_FILE`, `CA_DECODER_DONE_FILE`, and `CA_DECODER_PAYLOAD` describe internal progress and current archive objects.
- `CA_DECODER_REQUEST`, `CA_DECODER_SEEK`, and `CA_DECODER_SKIP` request more input bytes, an absolute input seek, or a relative input skip from the caller.
- `CA_DECODER_FOUND` and `CA_DECODER_NOT_FOUND` report completion or failure of a requested seek.

Configuration APIs include feature flag access/masking, mode booleans for punch holes, reflinks, hardlinks, deletion, payload delivery, immutable-bit undo, UID shifting/ranging, output base fd or boundary fd, base mode for metadata-only/no-filesystem output, and archive size for seekable streams.

Runtime APIs include `ca_decoder_step()`, `ca_decoder_put_data()`, `ca_decoder_put_eof()`, `ca_decoder_get_request_offset()`, `ca_decoder_get_seek_offset()`, `ca_decoder_get_skip_size()`, and `ca_decoder_get_payload()`.

Metadata APIs expose the current path, mode, symlink target, mtime, size, UID/GID, user/group names, device number, payload offset, chattr flags, FAT attributes, xattrs through `CaIterate`, quota project ID, and archive offset.

Digest APIs enable and retrieve archive, payload, and hardlink `CaChunkID` values. `ca_decoder_try_hardlink()` accepts a `CaFileRoot` and path for seed-based hardlink installation during finalization.

## Control Flow Contract

The intended caller loop is event driven. A caller creates a decoder, configures output and replay options, optionally sets archive size, then repeatedly calls `ca_decoder_step()`. On `CA_DECODER_REQUEST`, it asks `ca_decoder_get_request_offset()` for the current absolute input offset and appends bytes with `ca_decoder_put_data()`. On stream end, it calls `ca_decoder_put_eof()`. On `CA_DECODER_SEEK`, it obtains the absolute offset with `ca_decoder_get_seek_offset()`, moves the upstream input source, and feeds bytes from the new position. On `CA_DECODER_SKIP`, it obtains a byte count with `ca_decoder_get_skip_size()` and advances the upstream input source without feeding skipped bytes.

When `CA_DECODER_NEXT_FILE` is returned, current metadata accessors describe the newly parsed object. When `CA_DECODER_PAYLOAD` is returned, `ca_decoder_get_payload()` exposes the current payload span. When `CA_DECODER_DONE_FILE` is returned, payload or hardlink digests may be queried if enabled and valid. When `CA_DECODER_FINISHED` is returned, the archive digest may be queried if enabled.

Seek calls are separate control operations. `ca_decoder_seek_offset()` applies to naked regular/block payloads. `ca_decoder_seek_path()` and `ca_decoder_seek_path_offset()` apply to seekable directory archives with known archive size and goodbye offset information. `ca_decoder_seek_next_sibling()` uses the current path as a starting point.

## State and Persistence Behavior

The header itself has no storage, but it defines ownership and state boundaries. `ca_decoder_set_base_fd()` and `ca_decoder_set_boundary_fd()` transfer practical responsibility for writing under caller-provided fds; the implementation stores these fds and may close owned descriptors during unref. `ca_decoder_set_base_mode()` selects a no-output or metadata-only root mode instead of a filesystem fd.

The API allows persistent filesystem mutation through the decoder: file creation, metadata replay, deletion, hardlinking, reflinking, and hole punching are all controlled by the configuration setters. The current-entry accessors are stateful and meaningful only at the appropriate event positions; most return negative errno-style values such as `-ENODATA`, `-EUNATCH`, or `-EBUSY` when called at the wrong time.

Digest state is opt-in. Enabling digest calculation affects later stepping, and digest getters are constrained by decoder state: archive digest at finished state, payload/hardlink digests at current-file finalization.

## Dependencies and Integration Points

The header includes `cachunkid.h` for digest IDs, `cacommon.h` for shared enums such as `CaIterate`, `calocation.h` and `caorigin.h` for origin/location concepts, and standard integer, boolean, and type headers. It references `CaFileRoot` for hardlink seed roots and `CaOrigin` for input data provenance.

The primary integration point is `casync.c`, which wraps these functions in the higher-level `CaSync` API and CLI behavior. The event constants are also part of the implicit contract with any transport layer that can provide random access, skipping, or remote archive reads.

## Risks and Edge Cases

The enum values are unscoped integer constants. Callers must compare against the named constants and treat negative returns as errors; mixing event values and errno-style errors incorrectly can break restore loops.

The API requires strict state discipline. Feeding bytes after EOF, requesting payload data outside `CA_DECODER_PAYLOAD`, reading digests in the wrong state, seeking before archive size is known, or setting configuration after parsing has started can return errors or produce stale digest state.

File-descriptor ownership is not fully inferable from the declarations alone, so callers must follow implementation expectations and avoid reusing fds in surprising ways after handing them to the decoder. Boundary and base fd modes are mutually constrained.

The header exposes many filesystem replay toggles. Tests and callers need to understand that disabling payload delivery does not necessarily disable filesystem writes, and disabling replay feature bits via the mask changes which archived metadata is honored.

## Test Signals

Compile tests should include this header from C and C++-style consumers if applicable, verify all dependent headers resolve, and ensure the opaque type can be allocated and released without exposing internals.

API contract tests should assert that invalid `NULL` arguments produce negative errors, configuration setters reject invalid states, event returns are handled distinctly from errno values, and metadata/digest accessors return `-ENODATA` or `-EBUSY` outside their legal event windows.

Integration tests should exercise a full caller loop using only declarations in this header: configure decoder, feed bytes on requests, perform skip/seek handling, read payloads and metadata at event boundaries, and retrieve digests at the documented terminal states.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/cadecoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/cadigest.c -->
# sources/sync-backup/casync/src/cadigest.c

## Purpose

`cadigest.c` implements the `CaDigest` abstraction declared in `cadigest.h`. It wraps OpenSSL SHA-256 and SHA-512 contexts behind a small casync-specific API, normalizes digest sizes to `CaChunkID` length, supports the project default SHA-512/256 variant, and provides string conversion helpers for digest type selection.

The module is used anywhere casync needs stable content or metadata hashes: chunk ID generation, location IDs, archive/payload/hardlink digests in encoder and decoder code, cache validation, store validation, remote validation, and command-line digest option parsing.

## Important APIs, Types, and Functions

The private `struct CaDigest` stores a `CaDigestType`, a result buffer large enough for either SHA-256 or SHA-512 output, and a union of `SHA256_CTX` and `SHA512_CTX`.

`ca_digest_new()` validates the requested type, allocates the object, stores the type, and initializes the OpenSSL context via `ca_digest_reset()`. `ca_digest_free()` uses the project `mfree()` helper and accepts `NULL`.

`ca_digest_reset()` initializes the active hash context. SHA-256 uses `SHA256_Init()`. SHA-512/256 uses `SHA512_Init()` and then writes the SHA-512/256 initial hash values directly into the OpenSSL `SHA512_CTX` words because the code predates or avoids a native OpenSSL SHA-512/256 API.

`ca_digest_write()` updates the active context, ignoring `NULL` digest handles and zero-length writes but asserting a non-NULL buffer for positive lengths.

`ca_digest_read()` finalizes the active context into `result` and returns a pointer to that buffer. For SHA-512/256 it finalizes a full SHA-512 result but callers use `ca_digest_get_size()` or fixed `CaChunkID` copies to consume the first 32 bytes.

Query and conversion helpers include `ca_digest_get_size()`, `ca_digest_get_type()`, `ca_digest_get_name()`, `ca_digest_type_size()`, `ca_digest_type_to_string()`, `ca_digest_type_from_string()`, `ca_digest_ensure_allocated()`, and `ca_digest_set_type()`.

## Control Flow

A typical caller creates or ensures a digest object, writes byte ranges in deterministic order, finalizes with `ca_digest_read()`, and copies `ca_digest_get_size()` bytes or a `CaChunkID`-sized prefix. Reuse requires `ca_digest_reset()` before writing a new stream. Type changes go through `ca_digest_set_type()`, which validates the type and resets the new context.

`ca_digest_ensure_allocated()` is a lazy allocation helper used by encoder/decoder digest paths. If the pointer already contains a digest, it returns `0` without checking or changing the existing type. If the pointer is `NULL`, it allocates the requested type and returns `1`.

String conversion is table driven. `"default"` maps to `CA_DIGEST_DEFAULT`, and explicit names are `"sha256"` and `"sha512-256"`.

## State and Persistence Behavior

Digest state is fully in memory. The OpenSSL context accumulates bytes until reset or finalization. `ca_digest_read()` is destructive in the normal OpenSSL sense: it finalizes the current context, so additional writes after a read are not a valid continuation unless the context is reset first.

The result pointer returned by `ca_digest_read()` is owned by the `CaDigest` object and remains valid only until the next reset, read, type change, or free. The code does not persist digest output to disk.

The SHA-512/256 implementation mutates OpenSSL internal context fields after `SHA512_Init()`. That is stable only for OpenSSL versions exposing the same `SHA512_CTX` layout through the included headers.

## Dependencies and Integration Points

The direct dependency is OpenSSL `<openssl/sha.h>`. Project dependencies are `cadigest.h` for declarations and `util.h` for allocation, equality, and assertion helpers.

Integration points include `cachunkid.c` for one-shot chunk IDs, `calocation.c` for location hashing with little-endian integer writes, `caencoder.c` and `cadecoder.c` for archive/payload/hardlink digests, `caseed.c` for seed chunk hashes, `cacache.c`, `castore.c`, and `caremote.c` for validation digests, and `casync-tool.c` for user-facing digest type parsing and display.

## Risks and Edge Cases

`ca_digest_read()` finalizes the context but does not mark it finalized. A caller that reads twice or writes after reading without a reset relies on undefined or OpenSSL-specific behavior. Tests should treat digest objects as single-use between resets.

`ca_digest_ensure_allocated()` does not verify that an existing digest has the requested type. Callers that change feature flags or expected digest algorithms while reusing a pointer must call `ca_digest_set_type()` themselves.

The SHA-512/256 implementation depends on direct access to `SHA512_CTX.h[]`, which can break with OpenSSL API opacity or provider-only implementations. It also finalizes a 64-byte SHA-512 buffer while reporting a 32-byte digest size, so every caller must honor the reported size.

Digest functions generally return errno-style errors for allocation/type problems but `ca_digest_write()` and `ca_digest_reset()` are void and silently ignore `NULL` digest pointers. This is convenient for optional digests but can hide missed initialization when the caller expected hashing to be active.

## Test Signals

Unit tests should compare SHA-256 and SHA-512/256 results against known test vectors, including empty input and multi-write input. SHA-512/256 should specifically verify the 32-byte prefix returned by `ca_digest_get_size()`.

Lifecycle tests should cover invalid types, `NULL` return pointers, `ca_digest_ensure_allocated()` returning `1` on allocation and `0` on existing digest, `ca_digest_set_type()` resetting the stream, zero-length writes having no effect, and `ca_digest_type_from_string()` handling `"default"`, explicit names, unknown names, and `NULL`.

Integration tests should verify that `CaChunkID` generation, encoder/decoder archive digest, payload digest, hardlink digest, and location hashing all copy only the expected digest length and remain stable across architectures through the little-endian helpers in the header.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/cadigest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/cadigest.h -->
# sources/sync-backup/casync/src/cadigest.h

## Purpose

`cadigest.h` declares the public hash abstraction used throughout casync. It defines digest algorithm identifiers, exposes an opaque `CaDigest` handle, declares allocation/lifecycle/update/finalization helpers, and provides inline helpers for hashing fixed-width integers in little-endian byte order.

The header keeps callers independent from OpenSSL context details while preserving enough algorithm metadata for feature-flag negotiation, command-line parsing, and `CaChunkID` sizing.

## Important APIs, Types, and Constants

`CaDigestType` contains `CA_DIGEST_SHA256`, `CA_DIGEST_SHA512_256`, `_CA_DIGEST_TYPE_MAX`, `CA_DIGEST_DEFAULT = CA_DIGEST_SHA512_256`, and `_CA_DIGEST_TYPE_INVALID = -1`.

`typedef struct CaDigest CaDigest;` keeps implementation storage private to `cadigest.c`.

Lifecycle and allocation functions are `ca_digest_new()`, `ca_digest_free()`, `ca_digest_freep()`, and `ca_digest_ensure_allocated()`. The `ca_digest_freep()` inline helper is designed for the project cleanup attribute pattern, although it frees the pointed-to object without nulling the caller's slot.

Hash update and read APIs are `ca_digest_write()`, `ca_digest_write_u8()`, `ca_digest_write_u32()`, `ca_digest_write_u64()`, `ca_digest_read()`, and `ca_digest_reset()`. The integer helpers convert 32-bit and 64-bit values with `htole32()` and `htole64()` before hashing.

Metadata helpers are `ca_digest_get_size()`, `ca_digest_get_type()`, `ca_digest_get_name()`, `ca_digest_type_size()`, `ca_digest_type_to_string()`, `ca_digest_type_from_string()`, and `ca_digest_set_type()`.

## Control Flow Contract

Callers allocate a digest with a selected `CaDigestType`, write byte strings and integer fields in a stable order, then call `ca_digest_read()` to get the final result pointer. For reusable objects, callers call `ca_digest_reset()` before a new message or `ca_digest_set_type()` to change algorithms.

The integer helpers are part of the serialization contract: any cross-platform hash of structured numeric fields should use these helpers or equivalent little-endian encoding to avoid host-endian digest drift.

## State and Persistence Behavior

The header defines an in-memory handle only; it does not prescribe any on-disk format. Digest results are returned as borrowed pointers owned by the `CaDigest`.

The default algorithm is SHA-512/256. This default affects new digest users that select `CA_DIGEST_DEFAULT` directly or parse `"default"` through the implementation.

Because `ca_digest_freep()` does not clear `*d`, cleanup-style use is safe at scope exit, but manual calls followed by reuse of the same pointer would leave a dangling value unless the caller nulls it.

## Dependencies and Integration Points

The header includes `<stdbool.h>`, `<sys/types.h>`, and `<inttypes.h>`. The inline integer helpers require endian conversion macros such as `htole32()` and `htole64()` to be available through the platform or surrounding project headers.

It is included by `cachunkid.h`, `calocation.h`, `caformat-util.h`, cache/store/remote/seed code, encoder/decoder code, and the CLI. The digest type enum must remain aligned with feature-flag conversion helpers in `caformat-util` and with user-facing names in `cadigest.c`.

## Risks and Edge Cases

Changing `CA_DIGEST_DEFAULT` would affect chunk IDs and compatibility with existing archives, caches, remotes, and stores unless feature flags and migration logic are handled carefully.

The cleanup helper frees but does not null the pointer. That matches common cleanup-attribute usage but is a footgun for manual double-free-prone patterns.

The header exposes both raw byte writes and endian-normalized integer writes. Mixing host-endian raw integer writes with the helper-based format would create non-portable digests.

The digest read API returns `const void *` rather than a size-coupled object. Callers must pair it with `ca_digest_get_size()` or a known `CaChunkID` size and must not assume every supported algorithm returns the same length unless that remains an explicit project invariant.

## Test Signals

Header-level tests should compile translation units that include only `cadigest.h` and use all declared APIs and inline helpers. They should verify enum values for default and invalid cases where ABI or serialized behavior depends on them.

Behavioral tests should ensure `ca_digest_write_u32()` and `ca_digest_write_u64()` produce the same bytes on big-endian and little-endian hosts, either through cross-platform CI or explicit byte-order fixture tests.

Integration tests should verify that user-facing string names, feature-flag digest type mapping, `CaChunkID` size assumptions, and default digest selection remain synchronized across `cadigest.c`, `caformat-util`, and archive encoder/decoder paths.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/cadigest.h -->
