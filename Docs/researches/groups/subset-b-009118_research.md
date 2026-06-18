# subset-b-009118 research

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/caencoder.c -->
# sources/sync-backup/casync/src/caencoder.c

## Purpose
Implements `CaEncoder`, the streaming archive encoder for casync. It walks a base regular file, block device, or directory tree and emits the casync archive format defined in `caformat.h`: `ENTRY` metadata records, optional metadata subrecords, file payload bytes, directory `FILENAME` records, and directory `GOODBYE` lookup tables. It also exposes current-file metadata, seekable `CaLocation` checkpoints, and optional archive/payload/hardlink digests.

## Important APIs, Types, and Functions
The public lifecycle is `ca_encoder_new`, `ca_encoder_unref`, `ca_encoder_set_base_fd`, `ca_encoder_step`, and `ca_encoder_get_data`. `CaEncoderState` drives the stream: `INIT`, `ENTERED`, `ENTRY`, `IN_PAYLOAD`, directory entry states, `GOODBYE`, `FINALIZE`, and `EOF`. `CaEncoderNode` caches the current stack of filesystem nodes, including fds, stat data, sorted dirents, symlink targets, xattrs, ACLs, capabilities, btrfs flags, SELinux labels, quota project IDs, mount IDs, and `CaNameTable` state. Metadata accessors such as `ca_encoder_current_mode`, `ca_encoder_current_xattr`, `ca_encoder_current_location`, and digest getters mirror the current state.

## Control Flow
`ca_encoder_set_base_fd` validates and seeds the root node. Each `ca_encoder_step` advances buffered/skipped byte accounting and dispatches to `ca_encoder_step_node`. Naked top-level regular files or block devices go straight to payload streaming; directory trees begin with an `ENTRY`. For directories, sorted `scandirat` output creates deterministic traversal, `.caexclude`, nodump, submount, unsupported type, and virtual filesystem filters decide whether children are serialized, then each child is preceded by a `FILENAME` record. Directory finalization emits a BST-ordered `GOODBYE` table derived from name-table offsets.

`ca_encoder_get_data` materializes bytes for the state reported by `step`: metadata in `ca_encoder_get_entry_data`, payload via `pread`, filename records, or goodbye tables. If the caller requests no data and no digest needs payload bytes, the encoder can skip payload ranges while still advancing offsets.

## State and Persistence Behavior
Encoder state is in memory, but it serializes stable on-disk archive records. `archive_offset`, `payload_offset`, `skipped_bytes`, node-stack indexes, and per-node caches determine resumability. `ca_encoder_current_location` records relative path, designator, stream offset, stat freshness markers, feature flags, archive offset, and optional name-table chains. `ca_encoder_seek_location` reconstructs node stack state from that location and deliberately invalidates digest/name-table guarantees when resuming mid-object. UID/GID shifting and feature flags alter emitted metadata, so cached locations include feature flags.

## Dependencies and Integration Points
Depends on Linux/POSIX filesystem APIs, ACL, xattr, SELinux when enabled, btrfs ioctls, FAT and chattr flags, quota project ID helpers, `CaMatch` exclude matching, `CaNameTable`, `CaLocation`, `CaDigest`, and `ReallocBuffer`. It is consumed by higher-level sync/archive code and must match decoder expectations for `caformat.h`.

## Risks
High-risk areas are traversal determinism, race handling while files change, Linux-specific metadata fallbacks, and offset accounting across skipped payloads. `GOODBYE` generation requires valid archive offsets and name tables, so seeks can produce `-ENOLINK`. ACL/xattr/capability serialization has variable-sized unaligned records. Digest APIs are state-sensitive: archive digest is only final at EOF, payload/hardlink digests only at finalize and can be stale after partial seeks.

## Test Signals
Test regular-file naked archives, directory trees with sorted entries, empty dirs, symlinks, devices, FIFOs/sockets gating, block-device sizing, xattrs, file capabilities, ACLs, SELinux labels, chattr/FAT flags, btrfs subvolumes, project quotas, `.caexclude`, nodump, submount exclusion, seek/resume from all location designators, digest validity after full and partial reads, and archive equality against decoder round trips.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/caencoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/caencoder.h -->
# sources/sync-backup/casync/src/caencoder.h

## Purpose
Declares the opaque `CaEncoder` API used to turn filesystem input into a casync archive stream. It is the public contract for encoder setup, stepping, data retrieval, metadata inspection, seek/resume, and digest reporting.

## Important APIs, Types, and Functions
`CaEncoder` is opaque. Step result constants distinguish stream completion, file boundaries, payload availability, and generic data availability. Setup functions configure feature flags, UID shift/range, and the base fd. `ca_encoder_step` drives the state machine; `ca_encoder_get_data` returns archive bytes. Current metadata accessors expose path, mode, target, mtime, size, uid/gid/name/group, device, chattr/FAT flags, xattrs, quota project ID, offsets, and `CaLocation`. Digest controls enable and retrieve archive, payload, and hardlink digests.

## Control Flow
Callers create an encoder, set feature flags/base fd, repeatedly call `ca_encoder_step`, and fetch data when the step result indicates payload or archive data. Metadata accessors are valid around current-file states. `ca_encoder_seek_location` repositions the stream to a prior `CaLocation`.

## State and Persistence Behavior
The header exposes no structure fields, but the API preserves offsets and locations across streaming and allows digest state to be queried only at specific lifecycle points. The base fd remains owned externally but is used as the root for traversal.

## Dependencies and Integration Points
Includes `cachunkid.h`, `cacommon.h`, and `calocation.h`. Used by casync synchronization and archiving layers that need source-tree serialization and resumable addressing.

## Risks
The API is order-dependent: calling data, metadata, digest, or seek functions in the wrong state returns errors. Consumers must respect ownership of returned pointers and only rely on digest values after complete relevant reads.

## Test Signals
Compile-time ABI coverage, null-argument/error-state checks, step/data loop integration, location seek round trips, and digest enable/disable behavior are the key signals.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/caencoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/cafileroot.c -->
# sources/sync-backup/casync/src/cafileroot.c

## Purpose
Implements the tiny reference-counted `CaFileRoot` object that anchors a `CaLocation` to either a filesystem path, an fd, or both. It lets cached locations reopen origin files without embedding ownership of the original root directly in each location.

## Important APIs, Types, and Functions
`ca_file_root_new` validates that either `path` or `fd` is present and allocates a root with `n_ref = 1`. `ca_file_root_ref` and `ca_file_root_unref` implement manual reference counting. `ca_file_root_invalidate` marks a root stale and clears path/fd fields without freeing the object.

## Control Flow
Construction stores the fd and optionally duplicates the path. References are incremented by users such as `CaLocation`. Unref decrements and frees path/object when the count reaches zero. Invalidation clears reopen data and sets `invalidated`, causing later `ca_location_open` to fail with an unattached/stale root.

## State and Persistence Behavior
The object is in-memory state only. It does not close the stored fd on unref or invalidation; it sets `fd = -1`, so fd ownership is external. The persisted meaning is indirect: locations that reference an invalidated root can no longer be trusted to reopen files.

## Dependencies and Integration Points
Depends on `util.h` helpers (`new0`, `mfree`, `assert_se`). Integrated by `calocation.c` for root attachment and reopen validation.

## Risks
External fd ownership must be clear because this code does not close the fd. Invalidation is broad and permanently disables all attached locations. Reference counting is not atomic and is not thread-safe.

## Test Signals
Test path-only, fd-only, and path+fd roots; invalid constructor arguments; ref/unref lifetime; invalidation effects through `ca_location_open`; and leak checks for duplicated paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/cafileroot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/cafileroot.h -->
# sources/sync-backup/casync/src/cafileroot.h

## Purpose
Defines `CaFileRoot`, a small reference-counted root descriptor used by locations to reopen files relative to a stable root path or fd.

## Important APIs, Types, and Functions
`struct CaFileRoot` contains `n_ref`, `path`, `fd`, and `invalidated`. Public functions are `ca_file_root_new`, `ca_file_root_ref`, `ca_file_root_unref`, and `ca_file_root_invalidate`.

## Control Flow
No runtime logic lives in the header. It declares the lifecycle that `calocation.c` uses for root ownership.

## State and Persistence Behavior
The fields represent in-memory attachment state. `invalidated` is the signal that cached file origins should no longer be opened.

## Dependencies and Integration Points
Requires `<stdbool.h>`. It is included by `calocation.h`, making root attachment part of the public location API.

## Risks
The struct is public rather than opaque, so callers can mutate fields directly and bypass reference/invalidation rules. Reference counts are plain integers.

## Test Signals
ABI compile checks and location-open tests with valid and invalidated roots cover the header contract.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/cafileroot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/caformat-util.c -->
# sources/sync-backup/casync/src/caformat-util.c

## Purpose
Provides utility conversions for casync archive/index format constants and feature flags. It maps record type IDs to names, parses and formats `--with=` feature names, normalizes feature masks, determines timestamp granularity, maps filesystem attributes to feature bits, derives likely supported features from filesystem magic, and converts digest feature flags.

## Important APIs, Types, and Functions
`ca_format_type_name` names `CA_FORMAT_*` record types. `with_feature_map` backs `ca_with_feature_flags_parse_one` and `ca_with_feature_flags_format`. `ca_feature_flags_normalize`, `ca_feature_flags_are_normalized`, and `ca_feature_flags_normalize_mask` enforce canonical masks. Attribute conversion functions cover Linux chattr flags and FAT attrs. `ca_feature_flags_from_magic` maps FAT, ext, XFS, btrfs, tmpfs, FUSE, and default filesystems to supported metadata. Digest helpers map `CA_FORMAT_SHA512_256` to/from `CaDigestType`.

## Control Flow
Most functions are straight-line table scans or switch statements. Normalization removes redundant mutually exclusive bits: 32-bit UIDs supersede 16-bit, finer time granularity supersedes coarser options, ACL supersedes permissions/read-only, exclude-nodump removes stored nodump, and read-only subvolume implies subvolume.

## State and Persistence Behavior
No mutable state is stored. The output feature mask directly affects persisted archive/index headers and cache compatibility, so canonicalization is part of the on-disk contract.

## Dependencies and Integration Points
Depends on Linux `fs.h` and `msdos_fs.h`, `caformat.h`, `cadigest.h`, and utility helpers. Called by encoder, index reader/writer, FUSE warning code, and option parsing paths.

## Risks
Feature-mask mistakes can create archives that decoders reject or interpret with different metadata semantics. Filesystem magic support is heuristic, especially for FUSE. Formatting uses aggregate names like `best`, `unix`, and `all`, so consumers must understand that the formatted string may not be a minimal list of primitive bits.

## Test Signals
Round-trip parse/format for named features, rejection of unknown bits, normalization idempotence, time granularity selection, chattr/FAT conversions, digest type mapping, and representative filesystem magic cases are the useful tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/caformat-util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/caformat-util.h -->
# sources/sync-backup/casync/src/caformat-util.h

## Purpose
Declares the format utility API for translating casync feature flags, record types, filesystem attributes, and digest choices.

## Important APIs, Types, and Functions
Exports type naming, feature parse/format, normalization, mask normalization, time granularity lookup, chattr/FAT attr conversions, filesystem magic feature detection, normalized-mask validation, and digest feature conversion.

## Control Flow
The header has no implementation flow; it is a shared utility contract used before writing or after reading format headers.

## State and Persistence Behavior
No state is declared. Return values determine canonical feature masks persisted in archive and index records.

## Dependencies and Integration Points
Includes `cadigest.h` and `util.h`, particularly for `CaDigestType` and `statfs_f_type_t`. Integrated by encoder, index, FUSE, and command-line feature handling.

## Risks
Because normalization errors propagate into persisted metadata, callers should check all negative returns. `ca_feature_flags_to_digest_type` treats absence of the SHA512/256 bit as SHA-256.

## Test Signals
Header compile coverage and API-level unit tests for each conversion function are sufficient.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/caformat-util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/caformat.h -->
# sources/sync-backup/casync/src/caformat.h

## Purpose
Defines the casync archive and index wire format: record type IDs, feature flag bits, default/composite masks, and little-endian C structures for every serialized object.

## Important APIs, Types, and Functions
Archive types include `ENTRY`, `USER`, `GROUP`, `XATTR`, ACL records, `FCAPS`, `QUOTA_PROJID`, `SELINUX`, `SYMLINK`, `DEVICE`, `PAYLOAD`, `FILENAME`, and `GOODBYE`. Index types are `INDEX` and `TABLE`. Feature masks cover UID/name/time/mode/file-type support, DOS and chattr flags, btrfs subvolumes, xattrs, ACLs, SELinux, capabilities, quota IDs, excludes, submount handling, nodump handling, and digest type. Structures include `CaFormatHeader`, `CaFormatEntry`, variable-length metadata payloads, `CaFormatGoodbyeItem/Tail`, `CaFormatIndex`, `CaFormatTableItem`, and `CaFormatTableTail`.

## Control Flow
The header has no executable flow. Its opening comment defines archive record ordering: entry metadata, optional metadata records, payload/symlink/device data, recursive directory children in sorted name order, then a goodbye lookup table.

## State and Persistence Behavior
All structs are persisted with explicit `le64_t` fields and variable-length trailing arrays. `GOODBYE` and `TABLE` tails contain repeated size/marker fields for validation. Composite masks such as `CA_FORMAT_DEFAULT`, `CA_FORMAT_WITH_BEST`, `CA_FORMAT_WITH_UNIX`, `CA_FORMAT_WITH_FUSE`, and `CA_FORMAT_FEATURE_FLAGS_MAX` define compatibility policy.

## Dependencies and Integration Points
Depends on `cachunkid.h` and `util.h`. It is the shared ABI for encoder, decoder, index, feature utilities, and FUSE exposure.

## Risks
Changing constants or layout breaks archive/index compatibility. Variable-length records must be bounds-checked against the provided maximum macros. `CaFormatTable` deliberately uses `UINT64_MAX` table size while being written incrementally, so readers must validate the tail rather than trusting the table header size.

## Test Signals
Golden archive/index fixtures, endian/layout static assertions, max-size validation, decoder rejection of bad markers/sizes, and feature-mask compatibility tests are the key signals.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/caformat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/cafuse.c -->
# sources/sync-backup/casync/src/cafuse.c

## Purpose
Implements the optional read-only FUSE frontend for casync archives. It mounts a `CaSync` instance as a filesystem and translates FUSE operations into `ca_sync_*` seek, step, metadata, and payload calls.

## Important APIs, Types, and Functions
`ca_fuse_run` mounts and runs the FUSE loop. Static callbacks implement `getattr`, `readlink`, `readdir`, `open`, `read`, `statfs`, `ioctl`, `getxattr`, and `listxattr`. Helpers include `iterate_until_file`, `seek_to_path`, `fill_stat`, `feature_flags_warning`, and a signal handler that forwards quit requests to FUSE.

## Control Flow
FUSE callbacks operate on a single global `CaSync *instance`. Path-based operations seek to the requested path and step until `CA_SYNC_NEXT_FILE`. Reads enable payload mode, seek to path+offset, then copy `CA_SYNC_PAYLOAD` chunks until the requested size or EOF. `readdir` disables payload, seeks to the directory, skips the directory itself, emits child basenames, and uses `ca_sync_seek_next_sibling` to stay at one level. `ca_fuse_run` builds read-only mount options, optionally creates the mountpoint, installs signal handling, warns about unsupported feature flags, notifies readiness, runs `fuse_loop`, then unmounts and destroys state.

## State and Persistence Behavior
The mounted view is transient and read-only. Kernel cache is enabled through FUSE options, while all backing state is fetched from the `CaSync` archive/index/store pipeline. `statfs` derives block count from archive size, not from expanded payload size.

## Dependencies and Integration Points
Requires libfuse API version 26 and Linux ioctls for chattr/FAT attribute exposure. Integrates with `casync-tool.c` when built with `HAVE_FUSE`, with `CaSync` public accessors, notify/signal handling, and format feature utilities.

## Risks
The global `instance`/`fuse` design assumes one mount per process and no concurrent independent sessions. FUSE may issue concurrent callbacks, so mutable `CaSync` seek state is a concurrency-sensitive integration point unless FUSE is effectively single-threaded in this configuration. `fsname=` is noted as needing escaping. Unsupported archive features are only warned about, not blocked.

## Test Signals
Mount/unmount, mkdir-on-demand, signal shutdown, stat/readlink/readdir/read behavior, random read offsets, xattr list/get, chattr and FAT ioctl paths, feature warning output, read-only open rejection for write flags, and archive sources requiring polling are important tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/cafuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/cafuse.h -->
# sources/sync-backup/casync/src/cafuse.h

## Purpose
Declares the optional FUSE entry point for mounting a `CaSync` archive view.

## Important APIs, Types, and Functions
`ca_fuse_run(CaSync *s, const char *what, const char *where, bool do_mkdir)` runs the read-only FUSE mount for the provided synchronizer, optional filesystem name, mount path, and mkdir flag.

## Control Flow
The header has no logic. Consumers call `ca_fuse_run` after configuring `CaSync`; the implementation owns the mount loop until exit.

## State and Persistence Behavior
No state is declared. The implementation uses the supplied `CaSync` as transient process state and does not persist data.

## Dependencies and Integration Points
Includes `casync.h` for `CaSync`. Consumed by `casync-tool.c` under `HAVE_FUSE`.

## Risks
The header is tiny, so the main risk is build-configuration mismatch: callers must only link this when FUSE support is compiled.

## Test Signals
Compile with and without `HAVE_FUSE`, and command-line mount path coverage through `casync-tool.c`.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/cafuse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/caindex.c -->
# sources/sync-backup/casync/src/caindex.c

## Purpose
Implements `CaIndex`, the casync chunk index reader/writer. It writes and validates `.caidx`-style indexes containing an `INDEX` header followed by a `TABLE` of monotonically increasing chunk end offsets and chunk IDs, and supports both normal cooked operation and incremental raw streaming for uploads/downloads.

## Important APIs, Types, and Functions
Constructors select mode: `ca_index_new_write`, `ca_index_new_read`, `ca_index_new_incremental_write`, and `ca_index_new_incremental_read`. Setup includes fd/path/mode, feature flags, and chunk size bounds. Main operations are `ca_index_open`, `ca_index_write_chunk`, `ca_index_write_eof`, `ca_index_read_chunk`, incremental raw write/read/eof, size/count getters, and `ca_index_seek`.

## Control Flow
Opening lazily opens an fd. Writers use a temporary path when a final path is supplied, write the header once, append table items for each chunk, and finish with `CaFormatTableTail`; `ca_index_install` renames the temporary file after EOF. Readers validate the header, read table items sequentially, detect the tail marker, verify no trailing garbage, and reject non-monotonic or too-large chunk ranges. Incremental-read mode accepts raw bytes through `ca_index_incremental_write` while cooked reads return `-EAGAIN` until enough bytes are available. Incremental-write mode exposes newly written raw bytes via `ca_index_incremental_read`.

## State and Persistence Behavior
Persistent state is the index file: feature flags, chunk size min/avg/max, chunk end offsets, chunk IDs, and table tail marker/size. In-memory offsets (`start_offset`, `cooked_offset`, `raw_offset`, `item_position`, `previous_chunk_offset`) track raw/cooked progress. Blob size is cached from the final table item, and file size is cached for regular read mode.

## Dependencies and Integration Points
Depends on `caformat.h`, `caformat-util.h`, `cachunk.h`, `ReallocBuffer`, and utility I/O helpers. It connects chunking/storage code to archive data by mapping payload offsets to chunk IDs and skip amounts.

## Risks
Index correctness relies on offset monotonicity, tail validation, and matching chunk-size limits. The first chunk's returned size can be `UINT64_MAX` because there is no previous end offset in sequential reads, so callers must handle that convention. Temporary install is not complete until EOF and rename. Incremental modes are stateful and return `-EAGAIN` for legitimate partial data.

## Test Signals
Write/read round trips, zero-chunk index tails, malformed headers/tails/trailing bytes, non-monotonic offsets, chunk-size-limit rejection, temporary install behavior, incremental upload/download partial feeds, bisection seek at first/middle/last chunk boundaries, and overflow checks are important.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/caindex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/caindex.h -->
# sources/sync-backup/casync/src/caindex.h

## Purpose
Declares the opaque chunk-index API used by casync to create, stream, read, seek, and query chunk indexes.

## Important APIs, Types, and Functions
`CaIndex` is opaque. Constructors encode allowed operation modes. Setters configure fd/path, creation mode, feature flags, and chunk size bounds. The API supports opening/installing, writing chunk entries and EOF, reading cooked chunks, raw incremental write/read, position management, size/count getters, and blob-offset seeking.

## Control Flow
Typical writers configure chunk sizes/features then write chunks and EOF before install. Readers open and call `ca_index_read_chunk` until EOF or use `ca_index_seek` to position at the chunk containing a blob offset.

## State and Persistence Behavior
The header exposes index persistence through getters for index size, blob size, total chunks, available chunks, and chunk sizing. It intentionally hides internal fd/path/temp-file state.

## Dependencies and Integration Points
Includes `cachunkid.h` and `realloc-buffer.h`. Integrated with chunk store upload/download paths and archive payload readers.

## Risks
Mode-specific APIs return errors when used on the wrong constructor. Callers must set chunk sizes before writing and handle `-EAGAIN` in incremental modes.

## Test Signals
Mode matrix tests, wrong-mode error coverage, seek behavior, and incremental buffer API tests cover the public contract.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/caindex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/calocation.c -->
# sources/sync-backup/casync/src/calocation.c

## Purpose
Implements `CaLocation`, an immutable/reference-counted descriptor for a position within a serialized filesystem tree or a void blob. Locations support cache keys, archive seek/resume, origin reopening for reflinks, string formatting/parsing, range advancement/merge, and stale-file validation.

## Important APIs, Types, and Functions
Core lifecycle is `ca_location_new`, `ca_location_copy`, `ca_location_ref`, and `ca_location_unref`. `ca_location_format_full` and `ca_location_parse` convert between objects and strings. Patch/update helpers include `ca_location_patch_size`, `ca_location_patch_root`, `ca_location_advance`, and `ca_location_merge`. `ca_location_open` reopens the origin and validates freshness. `ca_location_id_make` hashes a location into a `CaChunkID`, and `ca_location_equal` compares selected fields.

## Control Flow
Construction rejects absolute paths, invalid designators, `UINT64_MAX` offsets, zero sizes, invalid void paths, and overflow. Formatting emits `<path>+<designator><offset>[:size][@inode.mtime[.generation]][%features][#archive-offset][$name-table]`. Parsing strips optional suffixes in reverse order and recreates name-table state when present. Patch/advance/merge functions preserve immutability by modifying in place only when `n_ref == 1`, otherwise copying first.

## State and Persistence Behavior
Locations store relative path, designator, offset, optional size/root, mtime/inode/generation freshness markers, feature flags, archive offset, optional name table chain, and cached formatted string. `ca_location_open` uses either root fd plus `openat` or root path plus `open`, refuses invalidated roots, and returns `-ESTALE` if inode, max(mtime, ctime), or generation no longer match.

## Dependencies and Integration Points
Depends on `CaFileRoot`, `CaNameTable`, `CaDigest`, `ReallocBuffer`, Linux `FS_IOC_GETVERSION`, and utility/time helpers. Used by encoder, sync cache management, and reflink/origin tracking.

## Risks
String parsing is delimiter-sensitive, so path rules forbid absolute paths but still rely on `+` as the final separator. Reopen validation cannot catch every mutation if generation is unavailable and timestamp/inode resolution is insufficient. `ca_location_merge` only merges adjacent ranges with identical root/path/designator/freshness fields.

## Test Signals
Format/parse round trips with all optional suffixes, invalid input rejection, copy-on-write behavior under shared refs, advance and merge boundaries, root fd/path open, invalidated roots, stale detection after file replacement/modification, and location ID stability are key tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/calocation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/calocation.h -->
# sources/sync-backup/casync/src/calocation.h

## Purpose
Defines the public `CaLocation` model used to identify positions in casync archive serialization and to track the filesystem origin of data.

## Important APIs, Types, and Functions
`CaLocationDesignator` distinguishes entry, payload, filename, goodbye, and void locations. `CaLocationWith` selects optional comparison/format fields. `struct CaLocation` stores reference count, path/designator/offset, optional size/root, freshness metadata, feature flags, archive offset, name table, and cached formatting. Public functions cover create/copy/ref/unref, format/parse, size/root patching, advancing, merging, opening, ID hashing, and equality.

## Control Flow
The header declares immutable-style operations: modifications take `CaLocation **` so implementations can copy when shared.

## State and Persistence Behavior
The struct is public and can represent both persisted string form and in-memory root/name-table attachments. `UINT64_MAX` marks unspecified optional numeric fields.

## Dependencies and Integration Points
Includes `cachunkid.h`, `cadigest.h`, `cafileroot.h`, `canametable.h`, and `util.h`. It is the bridge between encoder seek points, cache keys, and source-file reopening.

## Risks
Public mutable fields can bypass copy-on-write invariants. Callers must treat relative path and optional-field sentinels consistently with parser/formatter rules.

## Test Signals
ABI compile checks, designator validation, formatter/parser tests, equality masks, and integration through encoder seek locations cover this header.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/calocation.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/camakebst.c -->
# sources/sync-backup/casync/src/camakebst.c

## Purpose
Builds an array-backed binary-search-tree permutation from a sorted input array. casync uses this layout for lookup tables such as directory goodbye/name tables so searches can proceed with monotonically increasing array indexes.

## Important APIs, Types, and Functions
The public function is `ca_make_bst(input, n, size, output)`. Static helpers `pow_of_2`, `log_of_2`, and `make_bst_inner` compute the root index and recursively copy left/right subtrees into heap-style positions `2*i+1` and `2*i+2`.

## Control Flow
`ca_make_bst` computes tree height from `log_of_2(n) + 1` and starts recursion at output index 0. `make_bst_inner` chooses a balanced root `k` based on the subtree size and power-of-two thresholds, copies that element, then recurses into the lower and upper sorted ranges.

## State and Persistence Behavior
No persistent state exists. The output permutation is persisted indirectly when callers serialize the resulting table.

## Dependencies and Integration Points
Depends on `util.h` for assertions and `memcpy`. Integrated by name-table/goodbye table generation.

## Risks
`ca_make_bst` assumes `n > 0`; if `n == 0`, `log_of_2(0)` would be invalid. Input must be sorted and output must be large enough for `n` elements. Overlapping input/output is not explicitly handled.

## Test Signals
Test zero handling at caller boundaries, one/two/many elements, odd/even sizes, sorted-search correctness, output bounds under sanitizers, and integration with goodbye table lookup.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/camakebst.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/camakebst.h -->
# sources/sync-backup/casync/src/camakebst.h

## Purpose
Declares the binary-search-tree permutation helper used for sorted table serialization.

## Important APIs, Types, and Functions
`ca_make_bst(const void *input, size_t n, size_t size, void *output)` copies `n` fixed-size sorted elements into array-backed BST order.

## Control Flow
No implementation is in the header. Callers provide sorted input and consume permuted output.

## State and Persistence Behavior
No state is declared. The function affects persisted layout only through caller-owned output buffers.

## Dependencies and Integration Points
Includes `<sys/types.h>` for `size_t`. Used by name-table/goodbye construction paths.

## Risks
The contract does not document behavior for `n == 0`, overlapping buffers, or invalid sizes; callers must enforce those preconditions.

## Test Signals
Compile coverage and table-search tests through `camakebst.c` callers are sufficient.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/camakebst.h -->
