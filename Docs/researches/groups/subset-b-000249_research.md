# subset-b-000249 Research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-refs.c -->
# sources/cloud-native/ostree/src/libostree/ostree-repo-refs.c

## Purpose

This file implements OSTree ref resolution, ref enumeration, remote summary ref listing, collection-ref handling, and ref persistence. It is the repository layer that maps human-readable ref names, remote refspecs, and collection refs to commit checksums stored on disk or advertised by remote summaries.

## Important APIs, Types, and Functions

- `ostree_repo_resolve_rev()` and `ostree_repo_resolve_rev_ext()` resolve a checksum, abbreviated checksum, parent suffix refspec, local ref, or remote ref into a full commit checksum.
- `ostree_repo_resolve_collection_ref()` resolves `OstreeCollectionRef` keys and honors local-only flags, transaction state, mirrors, remotes, and parent repositories.
- `ostree_repo_list_refs()`, `ostree_repo_list_refs_ext()`, and `_ostree_repo_list_refs_internal()` enumerate `refs/heads` and optionally `refs/remotes`.
- `ostree_repo_remote_list_refs()` and `ostree_repo_remote_list_collection_refs()` parse a fetched remote summary and expose summary refs as checksum maps.
- `ostree_repo_list_collection_refs()` enumerates collection-aware refs from `refs/heads`, `refs/mirrors`, and configured remote collection IDs.
- `_ostree_repo_write_ref()`, `_ostree_repo_update_refs()`, and `_ostree_repo_update_collection_refs()` persist new ref values or aliases.
- Helpers such as `add_ref_to_set()`, `write_checksum_file_at()`, `find_ref_in_remotes()`, `enumerate_refs_recurse()`, and `relative_symlink_to()` hold most filesystem-specific behavior.

## Control Flow

Resolution first accepts full checksums directly, then tries a unique abbreviated commit checksum with `ostree_repo_list_commit_objects_starting_with()`. A trailing `^` resolves the parent commit by recursively resolving the base ref and loading the commit variant. Otherwise, `ostree_parse_refspec()` splits a remote/ref pair and `resolve_refspec()` checks transaction-pending refs, on-disk local refs, remote refs, fallback remote search, and finally the parent repo if configured.

Listing builds hash tables by recursively walking ref directories. Ref fragments are validated before use, so extra files from mirroring tools are ignored. Local listing reads `refs/heads`; remote listing reads `refs/remotes/<remote>` or all remote subdirectories unless excluded. Collection listing additionally maps local refs to the repository collection ID, maps mirror refs under `refs/mirrors/<collection-id>`, and maps remote refs only when the remote has a valid configured `collection-id`.

Ref writes validate remote names, collection IDs, ref names, and checksums, choose a directory based on local/remotes/mirrors semantics, then either unlink, replace a checksum file, or atomically install a symlink alias. After a successful write, repository mtime is updated and the summary may be regenerated outside transactions.

## State and Persistence Behavior

Persistent state is ordinary filesystem state under the repository directory: `refs/heads`, `refs/remotes`, and `refs/mirrors`. Ref values are checksum text files with trailing newlines. Aliases are symlinks with relative targets. In-memory transaction refs in `self->txn.refs` and `self->txn.collection_refs` shadow disk until transaction commit; access is guarded by `self->txn_lock`. Parent repositories are read-only fallback sources for resolution. Remote summaries are fetched through `ostree_repo_remote_fetch_summary()` and parsed as `OSTREE_SUMMARY_GVARIANT_FORMAT`.

The write path handles a file/directory conflict by listing refs below the candidate name, rejecting conflicting descendants, removing the directory, and retrying the file replacement. This protects against replacing a ref namespace that contains unrelated refs.

## Dependencies and Integration Points

The file depends heavily on libglnx fd-relative filesystem helpers, GLib `GVariant`, `GHashTable`, and repo-private helpers for summary regeneration, temporary symlink creation, checksum validation, and remote configuration. It integrates with commit object storage for abbreviated checksum lookup and parent resolution, with transaction machinery, and with remote summary metadata including collection maps.

## Risks and Edge Cases

Important risks are ref namespace conflicts, invalid remote collection configuration, accidental fallback to a remote when local-only semantics were intended, stale transaction state, and symlink alias handling. Partial checksum resolution returns an error when ambiguous but deliberately returns success with `NULL` when no match exists so regular ref parsing can continue. Collection-ref conflict detection is called out as incomplete for a directory/file replacement case.

## Test Signals

Useful tests include resolving full and partial checksums, ambiguous partial checksums, parent suffix resolution, local-only versus remote-fallback behavior, transaction-pending refs, parent-repo fallback, invalid ref fragment filtering during list, alias symlink listing through `OSTREE_REPO_LIST_REFS_EXT_ALIASES`, remote summary parsing, collection map parsing, and write conflict cases where a directory already exists at the desired ref path.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-refs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-static-delta-compilation-analysis.c -->
# sources/cloud-native/ostree/src/libostree/ostree-repo-static-delta-compilation-analysis.c

## Purpose

This file analyzes two commits to find regular-file content objects that are likely good static-delta candidates. It builds size/name indexes over commit contents and returns a map from newly reachable target checksums to similar source checksums, which the delta compiler can use for rollsum or bsdiff optimization.

## Important APIs, Types, and Functions

- `OstreeDeltaContentSizeNames` stores a content checksum, file size, and all observed basenames for that content object.
- `_ostree_delta_content_sizenames_free()` releases the checksum string and basename array.
- `build_content_sizenames_recurse()` walks a commit dirtree recursively through `OstreeRepoCommitTraverseIter`.
- `build_content_sizenames_filtered()` creates a sorted array of size/name records, optionally restricted to an include-only checksum set.
- `string_array_nonempty_intersection()` checks exact or fuzzy basename overlap.
- `sizename_is_delta_candidate()` filters out empty content and known compressed file extensions such as `xz` and `bz2`.
- `_ostree_delta_compute_similar_objects()` is the exported internal analysis entry point.

## Control Flow

The analysis builds a complete source-side sorted size list from the `from_commit` and a target-side sorted size list from `to_commit`, filtered to newly reachable regular-file content. Traversal visits files, loads `GFileInfo`, keeps only regular files, and records every basename that points to a given checksum. Directory entries load dirtree variants and recurse.

Candidate selection then iterates target records sorted by size. For each target it computes a size window from the supplied similarity percentage, advances a lower bound in the source array because both arrays are sorted, skips source and target records that are unsuitable for delta compression, and checks basename overlap. It tries exact name matching first and fuzzy matching second, where fuzzy mode compares the portion before the first dot when both names have extensions. The first match becomes the only candidate for that target checksum.

## State and Persistence Behavior

This code does not write persistent repository state. It loads commit, dirtree, and file metadata objects from the repository and constructs temporary in-memory `GHashTable` and `GPtrArray` indexes. The output map owns duplicated checksum strings and is consumed by static delta compilation.

## Dependencies and Integration Points

It depends on commit traversal from `ostree-repo-traverse.c`, object loading through `ostree_repo_load_file()` and `ostree_repo_load_variant()`, and the private static delta header for the `OstreeDeltaContentSizeNames` type. Its output feeds `generate_delta_lowlatency()` in the static delta compiler, which attempts rollsum or bsdiff only for entries returned here.

## Risks and Edge Cases

The comparator returns `sn_a->size - sn_b->size` as an `int`, which is compact but worth watching for very large size differences. Candidate choice is intentionally heuristic and single-match; a poor first match can prevent a better delta base from being considered. Empty files and pre-compressed extensions are filtered out. Fuzzy basename matching can match related library names but may also overmatch unrelated files with shared prefixes.

## Test Signals

Tests should cover duplicate content with multiple basenames, include-only filtering, nested directory recursion, exact and fuzzy name matches, size threshold boundaries, excluded compressed extensions, zero-length files, and the no-match path. Integration tests can compare generated deltas with and without analysis to confirm rollsum/bsdiff candidate counts.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-static-delta-compilation-analysis.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-static-delta-compilation.c -->
# sources/cloud-native/ostree/src/libostree/ostree-repo-static-delta-compilation.c

## Purpose

This file generates OSTree static deltas. A static delta packages the objects needed to recreate a target commit from an optional source commit, using compressed parts, rollsum copy operations, bsdiff patches, plain object payloads, and optional HTTP fallback entries. It can write deltas into the repository layout or to a caller-provided filename, and can wrap the superblock in a signature container.

## Important APIs, Types, and Functions

- `OstreeStaticDeltaPartBuilder` accumulates one part: object list, payload bytes, operation stream, mode and xattr dictionaries, temp file, header, and sizes.
- `OstreeStaticDeltaBuilder` owns all parts and fallback objects plus thresholds and counters.
- `finish_part()` builds the part payload variant, compresses it with LZMA, writes it to a linkable tmpfile, computes its checksum, and creates the meta-entry header.
- `allocate_part()` finalizes the previous part and starts a new one.
- `process_one_object()` encodes a full metadata, regular-file, or symlink object using `OPEN_SPLICE_AND_CLOSE`.
- `try_content_rollsum()`, `process_one_rollsum()`, `try_content_bsdiff()`, and `process_one_bsdiff()` implement optimized content deltas against existing source objects.
- `generate_delta_lowlatency()` is the main object-selection and part-building algorithm.
- `get_fallback_headers()` serializes objects that should be fetched separately.
- `ostree_repo_static_delta_generate()` is the public generation API.

## Control Flow

Generation starts by reading parameters such as fallback threshold, bsdiff limit, chunk size, endianness, inline-parts, output filename, verbosity, and signing settings. It loads the target commit and opens the output directory. `generate_delta_lowlatency()` then reads source and target commits, traverses reachable objects, subtracts objects already reachable from the source, and partitions new objects into metadata, regular content, and symlink content.

For regular content, it calls `_ostree_delta_compute_similar_objects()` to find possible source objects. Each candidate must be world-readable before the compiler attempts rollsum, because clients may apply deltas using different privileges or parent repositories. Rollsum is preferred when at least half the target chunks can be copied from the source. If rollsum fails and bsdiff is enabled and below the size threshold, bsdiff is selected. Large remaining regular files may be placed in fallback entries. Metadata is packed first, followed by rollsum objects, bsdiff objects, plain regular content, and symlinks. Parts are split when payload size crosses the configured chunk size.

After part generation, `ostree_repo_static_delta_generate()` creates the superblock with metadata, timestamp, from/to checksums, the target commit object, an empty recursion array, part headers, and fallback headers. Parts are either linked as files named `0`, `1`, etc. or embedded in metadata when inline-parts is enabled. Detached commit metadata is included if present. If signing parameters are supplied, the superblock bytes are signed by each configured key and written in `OSTREE_STATIC_DELTA_SIGNED_FORMAT`; otherwise the raw superblock is linked atomically.

## State and Persistence Behavior

Persistent outputs are stored under the repository static delta path, normally below `deltas/`, or under the directory of a supplied filename. Part files and the superblock are first written as linkable tmpfiles, chmodded to `0644`, and atomically linked into place. The compiler does not alter refs. It reads repository object content, file metadata, xattrs, detached commit metadata, and object storage sizes. It records fallback object metadata in the superblock rather than copying those object bytes.

## Dependencies and Integration Points

The file integrates with traversal, static delta private wire-format definitions, LZMA compression, rollsum matching, bsdiff generation, OSTree raw file conversion, object storage-size queries, detached metadata, and the `OstreeSign` abstraction. Generated operations are consumed by `ostree-repo-static-delta-processing.c`, and generated superblocks are read by `ostree-repo-static-delta-core.c`.

## Risks and Edge Cases

The generator has multiple size and endianness boundaries. Wrong byte swapping would make deltas unreadable on opposite-endian systems. Rollsum and bsdiff are deliberately limited by readability and size checks; relaxing those checks can create deltas clients cannot apply. Fallback entries make deltas unsuitable for offline execution. Inline parts skip external part checksums during offline execution because they are covered by the metadata blob. Signature generation only runs when both a sign name and key IDs are provided.

## Test Signals

Useful tests include from-scratch and from-parent delta generation, chunk splitting, inline versus external parts, fallback threshold behavior, bsdiff disabled mode, world-readable gating for optimized source objects, symlink encoding, metadata/detached metadata inclusion, big- and little-endian output, signed superblock generation, and applying generated deltas through the offline executor.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-static-delta-compilation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-static-delta-core.c -->
# sources/cloud-native/ostree/src/libostree/ostree-repo-static-delta-core.c

## Purpose

This file provides static delta core operations: checksum-array parsing, delta listing, index listing, offline execution, part opening and decompression, human-readable dumping, signature verification, deletion, existence checks, superblock digest calculation, and delta index regeneration.

## Important APIs, Types, and Functions

- `_ostree_static_delta_parse_checksum_array()` validates packed object type/checksum arrays.
- `ostree_repo_list_static_delta_names()` and `ostree_repo_list_static_delta_indexes()` enumerate repository delta and index layouts.
- `_ostree_repo_static_delta_part_have_all_objects()` checks whether a part can be skipped.
- `_ostree_repo_static_delta_is_signed()` and `_ostree_repo_static_delta_verify_signature()` parse and verify signed superblocks.
- `ostree_repo_static_delta_execute_offline_with_signature()` applies an already-downloaded delta directory or superblock file.
- `_ostree_static_delta_part_open()` verifies, decompresses, and parses a part payload.
- `_ostree_delta_get_endianness()` and `_ostree_delta_needs_byteswap()` interpret delta endianness metadata or historical heuristics.
- `_ostree_repo_static_delta_dump()`, `_ostree_repo_static_delta_delete()`, `_ostree_repo_static_delta_query_exists()`, `ostree_repo_static_delta_verify_signature()`, and `ostree_repo_static_delta_reindex()` expose maintenance behavior.

## Control Flow

Offline execution opens either a delta directory or a direct superblock file. It detects signed containers, optionally enforces `core.sign-verify-deltas`, verifies with the supplied `OstreeSign`, and extracts the raw superblock. It validates from/to checksum fields, ensures the source commit exists when specified, writes detached target commit metadata if present, and writes the target commit object if missing. It rejects offline execution when fallback entries are present. For each part header, it checks the part version, skips execution if every object already exists, opens inline or external part data, validates external checksums unless skipped, and invokes `_ostree_static_delta_part_execute()`.

Part opening reads the first byte as a compression type. Uncompressed parts can be memory-mapped or sliced from inline bytes. LZMA parts are decompressed into anonymous tmpfile-backed bytes and parsed as `OSTREE_STATIC_DELTA_PART_PAYLOAD_FORMAT_V0`. If checksum validation is enabled, the checksum input stream covers the bytes consumed and is compared with the expected part checksum.

Reindexing takes a shared repo lock, ensures `core.indexed-deltas` is true in config, enumerates deltas and old indexes, groups deltas by target commit, computes each superblock digest, writes reproducible sorted index variants, and removes stale indexes. Existing identical index content is left untouched to reduce write and sync load.

## State and Persistence Behavior

Core operations read and write repository files under `deltas/` and `delta-indexes/`. Offline execution writes metadata, content, and detached metadata objects into object storage through normal repo write APIs. Delete removes an entire delta directory. Reindex writes or unlinks index files under their content-addressed paths and may update repo config to enable indexed deltas.

## Dependencies and Integration Points

This file sits between generated delta artifacts and the low-level part executor. It depends on static delta private formats, checksum input streams, LZMA decompression, GLib variants, fd-relative filesystem helpers, repo object storage APIs, and the signing abstraction. Pull/summary logic can consume the delta indexes generated here through the `ostree.static-deltas` metadata key.

## Risks and Edge Cases

Signed and unsigned superblocks share entry points, so mis-detecting signatures can produce confusing errors. Inline parts intentionally skip part checksum validation, relying on metadata integrity and outer signatures where applicable. Historical deltas may lack endianness metadata, so heuristic byteswap detection remains a compatibility risk. Offline deltas with fallback entries are rejected because they require network object fetching. Reindex must handle stale indexes and deltas disappearing under prune, hence the shared lock.

## Test Signals

Tests should cover signed and unsigned offline execution, mandatory signature verification, missing source commit failure, fallback rejection, already-have-all-objects part skipping, compressed and uncompressed part opening, checksum mismatch detection, inline part handling, dump output across endian variants, delta deletion and existence checks, stale index removal, reproducible sorted indexes, and no-op index rewrite when content is unchanged.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-static-delta-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-static-delta-private.h -->
# sources/cloud-native/ostree/src/libostree/ostree-repo-static-delta-private.h

## Purpose

This private header defines static delta constants, wire-format strings, opcodes, shared helper prototypes, execution stats, analysis structs, and endian helpers used by static delta generation, parsing, execution, dumping, and indexing.

## Important APIs, Types, and Functions

- `OSTREE_STATIC_DELTA_PART_MAX_SIZE_BYTES` and `OSTREE_STATIC_DELTA_OBJTYPE_CSUM_LEN` define part sizing and packed object entry width.
- `OSTREE_STATIC_DELTA_PART_PAYLOAD_FORMAT_V0`, `OSTREE_STATIC_DELTA_META_ENTRY_FORMAT`, `OSTREE_STATIC_DELTA_FALLBACK_FORMAT`, `OSTREE_STATIC_DELTA_SUPERBLOCK_FORMAT`, and `OSTREE_STATIC_DELTA_SIGNED_FORMAT` define serialized `GVariant` layouts.
- `OSTREE_STATIC_DELTA_SIGNED_MAGIC` marks signed static delta containers.
- `OstreeStaticDeltaOpenFlags` controls checksum skipping and trusted variant parsing.
- `OstreeStaticDeltaOpCode` enumerates the bytecode consumed by the executor: open-splice-close, open, write, set/unset read source, close, and bspatch.
- `OstreeDeltaExecuteStats` records operation counts.
- `OstreeDeltaContentSizeNames` represents content similarity analysis records.
- Prototypes connect compilation analysis, part opening/execution, object-existence checks, dump/delete/reindex helpers, and endian detection.

## Control Flow

The header does not implement control flow, but it defines the contracts shared by the `.c` files. The compiler emits payloads using the part payload format and opcode enum. The core reader validates meta-entry and fallback layouts from the superblock. The processing layer interprets the opcodes in the same order they are declared here. Endian helper functions are used when generating or displaying non-native-endian numeric fields.

## State and Persistence Behavior

The formats declared here are persistent ABI for static delta artifacts on disk and in summaries. A superblock includes metadata, timestamp, source and target checksums, target commit object, recursive delta references, part metadata, and fallback entries. A signed delta stores magic, raw superblock bytes, and signature metadata. Any change to these strings affects compatibility with existing delta files.

## Dependencies and Integration Points

The header depends on public OSTree core types and is included by static delta core, compilation, compilation analysis, and processing sources. It also exposes `_ostree_repo_static_delta_reindex()` and related internals used by repo summary and command code. The `OSTREE_SUMMARY_STATIC_DELTAS` key links static delta indexes to summary metadata.

## Risks and Edge Cases

Format strings are dense and easy to break. Numeric fields in historical deltas may be non-canonical endian, so callers must use `maybe_swap_endian_u32()` and `maybe_swap_endian_u64()` when appropriate. `OSTREE_STATIC_DELTA_N_OPS` must remain in sync with the opcode enum and stats indexing. The signed format intentionally signs raw superblock bytes; any transformation before verification would invalidate signatures.

## Test Signals

Format compatibility tests should parse old and new superblocks, signed containers, fallback entries, empty object arrays, and cross-endian deltas. Opcode tests should verify the stats index remains aligned with `OSTREE_STATIC_DELTA_N_OPS`. ABI tests should ensure generated artifacts can be opened by the core reader and executed by the processing layer.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-static-delta-private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-static-delta-processing.c -->
# sources/cloud-native/ostree/src/libostree/ostree-repo-static-delta-processing.c

## Purpose

This file executes a parsed static delta part. It interprets the compact operation stream emitted by the compiler, reconstructs metadata and file objects, writes them into the repository, supports rollsum-style copy from existing source objects, applies bsdiff patches, and exposes asynchronous execution wrappers.

## Important APIs, Types, and Functions

- `StaticDeltaExecutionState` holds interpreter state: object checksum array, op stream, mode/xattr dictionaries, payload bytes, current output object, bare-content writer, read-source fd, and stats/error flags.
- `_ostree_static_delta_part_execute()` is the synchronous interpreter.
- `_ostree_static_delta_part_execute_async()` and `_ostree_static_delta_part_execute_finish()` wrap execution in a `GTask`.
- `read_varuint64()`, `validate_ofs()`, `open_output_target()`, and `do_content_open_generic()` decode common operands and validate payload bounds.
- Dispatch functions implement each opcode: `dispatch_open_splice_and_close()`, `dispatch_open()`, `dispatch_write()`, `dispatch_set_read_source()`, `dispatch_unset_read_source()`, `dispatch_close()`, and `dispatch_bspatch()`.

## Control Flow

Execution parses the packed object list from the part header, extracts the mode dictionary, xattr dictionary, payload, and operation bytes from the part payload, then loops until the op stream is exhausted. Each opcode consumes varint operands from `state->opdata`. Unknown opcodes fail with an invalid-argument error. Optional stats count operations using the opcode-to-index mapping.

`OPEN_SPLICE_AND_CLOSE` is the one-shot path. For metadata objects it copies bytes from the payload into an aligned `GBytes`, parses the correct metadata variant type, and writes metadata. For content objects it reads mode/xattr offsets and content payload coordinates, then either uses a bare-repo fast path or constructs a raw file content stream for symlinks and non-bare modes before writing content. It always closes afterward.

`OPEN`, `WRITE`, `SET_READ_SOURCE`, `UNSET_READ_SOURCE`, `BSPATCH`, and `CLOSE` support optimized content reconstruction. `OPEN` starts a bare-content writer unless the object already exists. `WRITE` copies either from the part payload or from the current read-source fd. `SET_READ_SOURCE` reads a checksum from the payload and opens the corresponding bare file object. `BSPATCH` maps the source file, allocates a target buffer, reads patch bytes from payload through a bspatch stream, and writes the result. `CLOSE` commits the bare content and asserts the resulting checksum.

## State and Persistence Behavior

The interpreter writes metadata and content objects to the repository through `ostree_repo_write_metadata()`, `ostree_repo_write_content()`, and private bare-content helpers. It skips writes for objects already present. It opens source objects from the repository for copy/patch operations and closes the fd when the read source is unset or the object closes. Temporary state is cleaned through `_ostree_repo_bare_content_cleanup()`.

## Dependencies and Integration Points

This file depends on opcode and format definitions from the private header, varint utilities, bspatch, GLib/GIO streams, bare repo write internals, checksum conversion helpers, and raw file conversion helpers. It is invoked by offline execution and dump/stat paths in `ostree-repo-static-delta-core.c`.

## Risks and Edge Cases

Offset validation is critical because payload coordinates come from external delta data. The code checks overflow and payload bounds before payload reads, but read-source fd reads also need EOF handling, which `dispatch_write()` performs. `dispatch_open()` asserts bare-family repository modes for multi-op reconstruction, so archive mode relies on the one-shot path. `BSPATCH` allocates the full output size in memory. Stats-only mode must consume operands while avoiding writes and cleaning partial state.

## Test Signals

Tests should execute every opcode, include stats-only dumping, validate checksum mismatch on close, reject bad offsets and malformed varints, handle existing objects without rewriting, copy from read-source objects, apply bsdiff patches, reconstruct symlinks, run against bare and bare-user modes, exercise cancellation, and verify async finish propagates errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-static-delta-processing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-traverse.c -->
# sources/cloud-native/ostree/src/libostree/ostree-repo-traverse.c

## Purpose

This file implements commit and dirtree traversal for OSTree repositories. It exposes an iterator over commit tree entries and higher-level functions that collect all objects reachable from a commit, optionally across parent commits and with parent-object backreferences.

## Important APIs, Types, and Functions

- `_OstreeRepoRealCommitTraverseIter` stores iterator state, current directory variant, current entry name, result state, index, and content/meta checksums.
- `ostree_repo_commit_traverse_iter_init_commit()` initializes traversal from a commit root.
- `ostree_repo_commit_traverse_iter_init_dirtree()` initializes traversal from a dirtree variant.
- `ostree_repo_commit_traverse_iter_next()`, `ostree_repo_commit_traverse_iter_get_file()`, and `ostree_repo_commit_traverse_iter_get_dir()` implement file-first then directory iteration.
- `ostree_repo_traverse_new_reachable()` and `ostree_repo_traverse_new_parents()` allocate hash tables with the correct key semantics.
- `ostree_repo_traverse_commit_with_flags()`, `ostree_repo_traverse_commit_union_with_parents()`, `ostree_repo_traverse_commit_union()`, and `ostree_repo_traverse_commit()` collect reachable objects.
- `ostree_repo_traverse_parents_get_commits()` resolves parent-map entries back to owning commits.

## Control Flow

Iterator initialization from a commit reads child indexes 6 and 7 to obtain root dirtree and dirmeta checksums. The first call to `next()` for a commit loads the root dirtree and returns a directory result. Subsequent calls read file entries first from child 0 of the dirtree variant, then directory entries from child 1. File results expose a content checksum. Directory results expose content and metadata checksums.

Reachability traversal serializes object names as `(checksum, object type)` variants. For each file, it adds the file object and optional parent reference. For each directory, it adds the dirmeta object, then adds and recursively traverses the dirtree object if it has not already been seen. Commit traversal adds the commit object itself, optionally skips non-commit traversal under `OSTREE_REPO_COMMIT_TRAVERSE_FLAG_COMMIT_ONLY`, then follows parent commits until `maxdepth` is reached or no parent exists.

Partial commits are handled by loading commit state and allowing missing dirtree/dirmeta errors when the commit is marked partial. In that case the missing subtree is skipped rather than treated as fatal.

## State and Persistence Behavior

This file does not write repository state. It loads commit and dirtree variants and returns in-memory reachable-object and parent maps. The iterator refs the repo and variants until cleared. Parent maps store either a single parent variant or an array of parent variants to reduce memory use in the common single-parent case.

## Dependencies and Integration Points

Traversal is a shared service for static delta generation, pruning, object enumeration, and any feature that needs to know which objects belong to a commit. It depends on `ostree_repo_load_variant()`, `ostree_repo_load_variant_if_exists()`, `ostree_repo_load_commit()`, checksum variant validation, and object-name serialization helpers.

## Risks and Edge Cases

Iterator getters return borrowed pointers into iterator-owned storage and are only valid for the current result. Parent maps can contain nested parent chains, so callers need `ostree_repo_traverse_parents_get_commits()` to resolve final owning commits. Partial commit behavior intentionally suppresses missing subtree errors, which is correct for partial repositories but can hide corruption if commit state is wrong. Traversal avoids infinite recursion by checking the reachable set before descending into a dirtree.

## Test Signals

Tests should cover iterator ordering, root commit traversal, nested directory traversal, commit-only traversal, maxdepth parent traversal, duplicate shared dirtrees, parent map construction with multiple parents, missing parent commits in partial repositories, missing dirtrees in non-partial repositories, and borrowed-pointer lifetime assumptions.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-traverse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-verity.c -->
# sources/cloud-native/ostree/src/libostree/ostree-repo-verity.c

## Purpose

This file handles repository fs-verity configuration and enabling. It parses repo config into desired support levels, enables fs-verity on temporary files before they become objects, and ensures fs-verity on existing regular files when requested.

## Important APIs, Types, and Functions

- `_ostree_repo_parse_fsverity_config()` reads modern `[integrity]` `composefs` and `fsverity` tristate keys, plus legacy `[ex-fsverity]` boolean keys.
- `_ostree_fsverity_enable()` is the low-level `FS_IOC_ENABLE_VERITY` ioctl wrapper.
- `_ostree_tmpf_fsverity_core()` reopens a tmpfile read-only and attempts fs-verity based on requested support.
- `_ostree_tmpf_fsverity()` applies repo-level wanted/supported caching and required-versus-opportunistic behavior.
- `_ostree_ensure_fsverity()` enables fs-verity on an existing path if it is a regular file.

## Control Flow

Config parsing sets compile-time support to maybe or no depending on `HAVE_LINUX_FSVERITY_H`. Composefs implies a default fs-verity setting of maybe unless explicitly disabled. If modern fsverity is not enabled, legacy required/opportunistic booleans are used. Requiring fs-verity while compiled without support fails early.

The ioctl wrapper prepares `struct fsverity_enable_arg` with SHA256, block size 4096, optional signature bytes, and no salt. `ENOTTY` and `EOPNOTSUPP` mean unsupported and are not fatal. `EEXIST` is allowed only when the caller requested `allow_existing`.

Temporary-file enabling first checks the repo desired state. Required mode fails if cached support is known no. Maybe mode attempts the ioctl; if unsupported, it caches `fs_verity_supported` as no under `txn_lock` to avoid repeated ioctls. Success caches yes. Existing-file ensuring stats the path, optionally ignores missing files, skips non-regular files, opens regular files read-only, calls the ioctl allowing existing verity, and fails if required support is unavailable.

## State and Persistence Behavior

The persistent effect is the filesystem fs-verity flag and Merkle tree metadata maintained by the kernel for regular files. Repo in-memory fields `fs_verity_wanted` and `fs_verity_supported` cache policy and observed filesystem support. Config is read but not written here. Optional signatures can be passed into the ioctl for signed fs-verity files.

## Dependencies and Integration Points

The file depends on Linux `fsverity.h` when available, `ioctl()`, libglnx tmpfile helpers, OSTree repo-private feature support enums, config parsing helpers, and fd-relative filesystem utilities. It integrates with object writing paths that operate on `GLnxTmpfile` and with composefs/integrity policy.

## Risks and Edge Cases

Support can vary by filesystem and kernel, so caching unsupported status is important but also means a repo object path moving across filesystems would need careful handling. Required mode must fail closed. Opportunistic mode should not turn unsupported ioctls into hard errors. Block size and hash algorithm are currently fixed. Non-regular files are skipped. Build configurations without `HAVE_LINUX_FSVERITY_H` must never reach required runtime enabling.

## Test Signals

Tests should cover config precedence between composefs, modern fsverity, and legacy ex-fsverity keys; build-without-header behavior; required versus maybe versus no policy; unsupported ioctl handling; existing verity with `EEXIST`; missing path handling with `allow_enoent`; non-regular-file skipping; signature pointer plumbing; and support-cache transitions under repeated tmpfile writes.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-verity.c -->
