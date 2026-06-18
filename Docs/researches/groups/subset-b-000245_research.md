# Research: subset-b-000245

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-commit.c -->
## sources/cloud-native/ostree/src/libostree/ostree-repo-commit.c

### Purpose
This file is the main object writing, transaction, tree ingestion, commit creation, and local import implementation for libostree repositories. It turns file streams, filesystem trees, mutable trees, metadata variants, detached commit metadata, and source-repository objects into content-addressed OSTree objects under `objects/`, while honoring repository modes such as archive, bare, bare-user, and bare-user-only.

### Important APIs, Types, And Functions
Public and internal entry points include `ostree_repo_prepare_transaction()`, `ostree_repo_commit_transaction()`, `ostree_repo_abort_transaction()`, `ostree_repo_write_metadata()`, `ostree_repo_write_content()`, `ostree_repo_write_regfile_inline()`, `ostree_repo_write_symlink()`, `ostree_repo_write_regfile()`, `ostree_repo_write_commit()`, `ostree_repo_write_commit_with_time()`, `ostree_repo_write_directory_to_mtree()`, `ostree_repo_write_dfd_to_mtree()`, `ostree_repo_write_mtree()`, `ostree_repo_read_commit_detached_metadata()`, `ostree_repo_write_commit_detached_metadata()`, `_ostree_repo_import_object()`, `_ostree_repo_transaction_write_repo_metadata()`, and the `OstreeRepoCommitModifier`, `OstreeRepoDevInoCache`, and `OstreeRepoTransactionStats` boxed helpers.

Key internal helpers are `write_content_object()`, `write_metadata_object()`, `commit_loose_regfile_object()`, `_ostree_repo_commit_tmpf_final()`, `commit_path_final()`, `rename_pending_loose_objects()`, `fsync_object_dirs()`, `cleanup_tmpdir()`, `write_directory_to_mtree_internal()`, `write_dfd_iter_to_mtree_internal()`, `write_content_to_mtree_internal()`, `write_dir_entry_to_mtree_internal()`, `create_tree_variant_from_hashes()`, `get_final_xattrs()`, `_ostree_repo_commit_modifier_apply()`, and the direct import helpers around hardlinks, reflinks, and payload links.

### Control Flow
Object writes follow a staged content-addressed path. Metadata writes normalize and validate `GVariant` data, checksum it, skip existing objects when possible, then write a temporary file and link it into the loose object path. Content writes parse OSTree content streams into `GFileInfo`, payload stream, and xattrs, synthesize the canonical object header for checksumming, handle symlink and regular-file differences, and commit the object according to repo mode. Directory ingestion builds an `OstreeMutableTree`: it writes directory metadata, iterates children either through `GFileEnumerator` or `GLnxDirFdIterator`, applies commit modifiers and xattr/SELinux callbacks, writes content objects, and recursively processes subdirectories.

Transactions are explicit. `ostree_repo_prepare_transaction()` takes a shared repo lock, initializes transaction stats, computes free-space limits, and creates a locked staging directory. Object writes during a transaction usually land in the staging directory unless per-object fsync is configured. `ostree_repo_commit_transaction()` syncs filesystem state, renames staged loose objects into `objects/`, fsyncs object directories, deletes the staging directory, cleans temp files, updates queued refs and collection refs, optionally regenerates the summary, clears transaction state, and releases the lock. `ostree_repo_abort_transaction()` discards queued refs and staging state, runs cleanup with cancellation disabled, and releases locks.

Commit creation is layered on tree writing. `ostree_repo_write_mtree()` serializes dirtree variants from mutable-tree file and subdir checksum maps, returning an `OstreeRepoFile` root. `ostree_repo_write_commit_with_time()` adds automatic metadata such as object size indexes, then writes a commit variant containing parent, subject, body, timestamp, and root dirtree/dirmeta checksums. `ostree_repo_write_commit()` chooses the timestamp from UTC now or `SOURCE_DATE_EPOCH`.

### State And Persistence
Persistent state is primarily loose objects, transaction staging directories, ref files, collection-ref state, detached commit metadata objects, tombstone removal for rewritten commits, partial-commit marker files, and optional payload-link objects. The code carefully separates temporary object locations from final object paths. It supports delayed fsync, per-object fsync, fsverity hooks through `_ostree_tmpf_fsverity()`, min-free-space accounting through transaction block counters, and cleanup of stale transaction directories in `tmp/`.

The file also maintains in-memory transaction stats under `self->txn.stats`, transaction ref maps, collection-ref maps, a devino hardlink cache, object-size metadata accumulation, reflink capability cache, and temporary xattr/SELinux decisions. Mutexes protect transaction counters and queued ref maps in paths documented as multithread-safe; transaction start and commit remain single-active-transaction operations.

### Dependencies And Integration Points
The implementation depends heavily on GLib/GIO (`GFile`, `GFileInfo`, `GInputStream`, `GTask`, `GVariant`), libglnx fd and tmpfile helpers, OSTree core object formats, repo-private helpers, checksum streams, content stream parsing, mutable trees, SELinux policy helpers, varint encoding for size metadata, Linux syscalls and ioctls (`renameat`, `linkat`, `fsetxattr`, `futimens`, `statvfs`, `FICLONE`), and optional SMACK support. It integrates with checkout hardlink caches, static delta bare-content writers, pull/import logic, summary regeneration, ref storage, parent repositories, archive and bare repo modes, composefs metadata indirectly through commit metadata extension points, and repository locking.

### Risks And Edge Cases
Important risks are around crash consistency, partial transaction state, and non-atomic multi-ref updates. The code documents that objects and ref updates can be partially visible if interrupted. Filesystem-specific behavior matters for reflinks, hardlinks, xattrs, symlink metadata, fsync guarantees, fsverity, and free-space reporting. The `OSTREE_REPO_COMMIT_MODIFIER_FLAGS_CONSUME` and adoption path delete or rename source files, so filter/xattr errors must be handled before destructive steps. The devino cache can skip checksumming and therefore depends on correct hardlink cache ownership and mutation discipline. Bare-user and bare-user-only conversions are subtle because symlinks and metadata are represented differently. Async APIs run synchronous writers in tasks, so callers still need transaction lifetime discipline.

### Test Signals
High-value tests include transaction commit and abort with staged objects, power-failure style interruption around staged rename and ref update, min-free-space failures, duplicate object writes, archive versus bare versus bare-user content representation, xattr and SELinux labeling callbacks, canonical-permission modifiers, hardlink/devino cache hits, `CONSUME` source deletion behavior, reflink and payload-link fallbacks, detached metadata read/write/delete, commit timestamp reproducibility via `SOURCE_DATE_EPOCH`, import between repo modes with trusted and untrusted flags, async write finish paths, and summary/ref update behavior after transaction commit.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-commit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-composefs.c -->
## sources/cloud-native/ostree/src/libostree/ostree-repo-composefs.c

### Purpose
This file implements composefs support for libostree. It parses repo configuration, manages an in-memory `OstreeComposefsTarget`, checks out an `OstreeRepoFile` tree into libcomposefs nodes, writes composefs images, optionally computes fsverity digests, and can insert composefs digest metadata into commit metadata.

### Important APIs, Types, And Functions
The exported or repo-internal surface includes `_ostree_repo_parse_composefs_config()`, `ostree_composefs_target_new()`, `ostree_composefs_target_ref()`, `ostree_composefs_target_unref()`, the boxed `OstreeComposefsTarget` type, `ostree_composefs_target_write()`, `_ostree_repo_checkout_composefs()`, and `ostree_repo_commit_add_composefs_metadata()`. Important static helpers under `HAVE_COMPOSEFS` are `_composefs_read_cb()`, `_composefs_write_cb()`, `_ostree_composefs_set_xattrs()`, `checkout_one_composefs_file_at()`, `checkout_composefs_recurse()`, `checkout_composefs_tree()`, and `ensure_lcfs_dir()`.

### Control Flow
Configuration parsing reads `integrity.composefs` as an `OtTristate`, stores wanted and supported state on `OstreeRepo`, and errors when composefs is required but the build lacks libcomposefs. Target creation initializes a root libcomposefs directory node when support is compiled in. Checkout starts by querying the source `OstreeRepoFile` root as a directory, then recursively loads OSTree dirtree and dirmeta variants. For each file, it validates the destination name, loads file content/info/xattrs with `ostree_repo_load_file()`, creates a composefs node, fills mode, uid, gid, size, symlink payload or loose-object payload path, attaches xattrs, and optionally attaches fsverity digest data. For each directory, it validates child names, sets directory metadata, and recurses into subtrees.

Image writing chooses the `root` child if present, otherwise an empty directory, configures libcomposefs write options, writes to an fd if provided, and optionally returns a 32-byte fsverity digest. `_ostree_repo_checkout_composefs()` also ensures rootfs bind-mount anchor directories such as `usr`, `etc`, `boot`, `var`, and `sysroot`. Commit metadata generation builds a composefs target from a repo root, writes it without an output fd to compute the digest, and inserts `OSTREE_COMPOSEFS_DIGEST_KEY_V0` into a metadata dictionary.

### State And Persistence
`OstreeComposefsTarget` is refcounted and owns a libcomposefs node tree until written or unreffed. The checkout process does not materialize a traditional filesystem checkout; it records paths, metadata, xattrs, symlink targets, object payload paths, and fsverity digest hints in the composefs node graph. Persistence happens only when `ostree_composefs_target_write()` writes the image fd or when commit metadata receives the computed digest.

### Dependencies And Integration Points
This file depends on optional `libcomposefs`, optional Linux fsverity headers, GIO Unix streams, OSTree core loose object path helpers, `OstreeRepoFile`, repo-private memory cache helpers, and xattr/dirmeta variant formats. It integrates with checkout/deploy paths through `_ostree_repo_checkout_composefs()`, with commit metadata through `ostree_repo_commit_add_composefs_metadata()`, and with repo config through `_ostree_repo_parse_composefs_config()`.

### Risks And Edge Cases
The code is compiled into support and non-support paths; unsupported builds must consistently return `composefs_not_supported()`. Name validation is critical because file and subdirectory names become composefs paths. Duplicate file or directory targets are rejected. fsverity handling has several branches: it prefers kernel-measured digest from bare repo file fds, falls back to user-space content hashing only when verity is explicitly required, and otherwise may omit a digest. Large trees can be expensive when fsverity digest computation falls back to reading all content. Root checkout must be a directory, and root bind-mount directories are added even if absent from the original tree.

### Test Signals
Tests should cover config tristate behavior with and without compile-time support, empty target image writing, recursive checkout preserving uid/gid/mode/xattrs/symlinks, invalid path names, duplicate target names, fsverity digest selection and fallback, rootfs anchor directory creation, commit metadata digest insertion, and graceful unsupported-build errors for all public composefs entry points.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-composefs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-deprecated.h -->
## sources/cloud-native/ostree/src/libostree/ostree-repo-deprecated.h

### Purpose
This header preserves deprecated checkout API declarations and compatibility types for older libostree consumers. It defines the legacy `OstreeRepoCheckoutOptions` structure and declares `ostree_repo_checkout_tree_at()` as deprecated in favor of `ostree_repo_checkout_at()`.

### Important APIs, Types, And Functions
The central type is `OstreeRepoCheckoutOptions`, which carries checkout mode, overwrite mode, boolean bitfields for uncompressed cache, fsync disabling, whiteout processing, no-copy fallback, a `subpath`, a devino cache pointer, and reserved fields for ABI stability. The only function declaration is `_OSTREE_PUBLIC gboolean ostree_repo_checkout_tree_at(...) G_GNUC_DEPRECATED_FOR(ostree_repo_checkout_at)`.

### Control Flow
There is no executable control flow. The header contributes compile-time declarations, deprecation annotations, and scanner/deprecation macro compatibility for environments where `G_GNUC_DEPRECATED_FOR` may not be defined outside GI scanner processing.

### State And Persistence
The options struct carries transient checkout settings only. The reserved integer and pointer arrays are ABI padding so future or historical structure layout constraints do not break callers.

### Dependencies And Integration Points
It includes `ostree-core.h` and `ostree-types.h`, uses GLib declaration macros, and integrates with old callers that still invoke `ostree_repo_checkout_tree_at()` or allocate `OstreeRepoCheckoutOptions`. The `devino_to_csum_cache` field connects deprecated checkout flows with commit hardlink optimization used by repo commit code.

### Risks And Edge Cases
The major risk is ABI compatibility: field order, bitfield sizes, and reserved padding must not be casually changed. Because callers are expected to zero the struct before use, any additions would need to preserve zero-as-default behavior. Documentation says `ostree_repo_checkout_tree_at()` is superseded; new code should avoid this API.

### Test Signals
Useful signals are ABI/API compatibility checks, GI scanner behavior, compiler deprecation warnings, and build coverage for downstream code still including this header. Runtime behavior belongs to the checkout implementation, not this header.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-deprecated.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-file-enumerator.c -->
## sources/cloud-native/ostree/src/libostree/ostree-repo-file-enumerator.c

### Purpose
This file implements `OstreeRepoFileEnumerator`, a `GFileEnumerator` subclass used to enumerate children of an `OstreeRepoFile` directory backed by OSTree dirtree metadata rather than a native filesystem directory.

### Important APIs, Types, And Functions
The private instance stores an `OstreeRepoFile *dir`, requested attribute string, query flags, and a current child index. `_ostree_repo_file_enumerator_new()` constructs the enumerator. The class overrides `GFileEnumeratorClass.next_file` with `ostree_repo_file_enumerator_next_file()` and `close_fn` with `ostree_repo_file_enumerator_close()`. Dispose releases the directory and attributes.

### Control Flow
Construction references the directory, duplicates the attribute string, stores flags, and sets the `container` property to the directory. Each `next_file` call queries the child at the current index with `ostree_repo_file_tree_query_child()`. On success it increments the index and returns the `GFileInfo`. When the index is out of range, the underlying query returns success with a null info, matching GIO enumeration termination. Close is a no-op success.

### State And Persistence
The only state is in-memory enumeration position and references. No repository data is changed. The enumerator relies on `OstreeRepoFile` lazy resolution and cached tree variants for child data.

### Dependencies And Integration Points
It depends on `ostree-repo-file-enumerator.h`, `ostree-repo-file.h`, GObject, and GIO. It is plugged into the `GFileIface.enumerate_children` implementation in `ostree-repo-file.c`, allowing generic GIO consumers and commit tree walkers to enumerate committed OSTree trees.

### Risks And Edge Cases
Correct termination depends on `ostree_repo_file_tree_query_child()` returning true with `info == NULL` for out-of-range indexes. Errors during lazy resolution or metadata loading clear any partially returned info. The enumerator does not snapshot child variants itself; if the underlying `OstreeRepoFile` object were mutated through internal APIs during enumeration, behavior would follow that object state.

### Test Signals
Tests should enumerate empty and non-empty repo directories, verify ordering from dirtree files followed by directories, request different attribute sets, confirm clean termination, propagate missing-object errors, and verify `g_file_enumerator_get_child()` interoperation through the configured container.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-file-enumerator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-file-enumerator.h -->
## sources/cloud-native/ostree/src/libostree/ostree-repo-file-enumerator.h

### Purpose
This private header declares the `OstreeRepoFileEnumerator` GObject type and constructor used to enumerate children of `OstreeRepoFile` directories.

### Important APIs, Types, And Functions
It defines type macros for `OSTREE_TYPE_REPO_FILE_ENUMERATOR`, cast/check/get-class helpers, forward declarations for `OstreeRepoFileEnumerator` and its class, a class struct derived from `GFileEnumeratorClass`, `_ostree_repo_file_enumerator_get_type()`, and `_ostree_repo_file_enumerator_new()`.

### Control Flow
There is no runtime control flow in the header. It provides declarations consumed by `ostree-repo-file-enumerator.c` and `ostree-repo-file.c`.

### State And Persistence
No persistent state is defined here. The declared class is private/internal and carries instance state only in the C file.

### Dependencies And Integration Points
The header includes `ostree-repo-file.h`, which provides the `OstreeRepoFile` type accepted by the constructor. It integrates with the `GFile` interface implementation for committed OSTree trees.

### Risks And Edge Cases
Because this is an internal header, ABI risk is lower than public headers, but type macro consistency and constructor signature must match the implementation. Any change to the constructor affects `ostree_repo_file_enumerate_children()`.

### Test Signals
Build and type-registration tests are the main direct signals. Indirect coverage comes from `GFile` enumeration tests on `OstreeRepoFile`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-file-enumerator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-file.c -->
## sources/cloud-native/ostree/src/libostree/ostree-repo-file.c

### Purpose
This file implements `OstreeRepoFile`, a `GObject` that implements the `GFile` interface for files and directories inside an OSTree commit. It gives generic GIO code a read-only, lazy-resolved view over OSTree dirtree/dirmeta and content objects.

### Important APIs, Types, And Functions
The instance stores a repo reference, parent `OstreeRepoFile`, child index, name, cached file checksum, directory contents checksum/variant, and directory metadata checksum/variant. Constructors include `_ostree_repo_file_new_root()` and `_ostree_repo_file_new_for_commit()`, while children are produced internally by `ostree_repo_file_new_child()`. Public helpers include `ostree_repo_file_ensure_resolved()`, `ostree_repo_file_get_xattrs()`, tree checksum/content/metadata getters, `ostree_repo_file_tree_set_metadata()`, `ostree_repo_file_get_repo()`, `ostree_repo_file_get_root()`, `ostree_repo_file_get_checksum()`, `ostree_repo_file_tree_find_child()`, and `ostree_repo_file_tree_query_child()`.

The implemented `GFileIface` methods include duplicate, hash, equality, URI/path/name methods, parent lookup, prefix and relative path handling, relative path resolution, child display lookup, child enumeration, info query, settable/writable namespace query, and read. Mutating operations are intentionally null.

### Control Flow
A root object is created from known dirtree and dirmeta checksums or by loading a commit object and extracting its root tree checksums. Resolution is lazy. Root resolution loads the root dir tree and dir meta variants. Non-root resolution first resolves the parent, searches parent dirtree file and directory arrays by name, stores the child index, and, for directories, loads child dirtree/dirmeta variants and records their checksums. File checksums are computed from parent dirtree entries and cached.

`ostree_repo_file_tree_query_child()` resolves the directory, selects either the files array or directories array by numeric index, loads file info through `ostree_repo_load_file()` for files or dirmeta for directories, and sets standard GIO name/display/hidden attributes. `query_info` returns root dirmeta-derived info or delegates to the parent child query. `read` rejects directories, loads regular file streams by checksum, and resolves symlink targets relative to the parent before reading.

### State And Persistence
`OstreeRepoFile` is read-only from the perspective of `GFile`. It caches loaded `GVariant` tree metadata/content and computed file checksums in memory. It does not write repository state except for the specialized internal `ostree_repo_file_tree_set_metadata()`, which mutates the in-memory metadata/checksum pair for an existing object. Persistent content remains in the associated `OstreeRepo` object store.

### Dependencies And Integration Points
The implementation depends on GLib/GIO, `ostree-repo-private.h`, `ostree-repo-file-enumerator.h`, checksum conversion helpers, dirtree/dirmeta variant formats, `ostree_repo_load_variant()`, `ostree_repo_load_file()`, and utility path caches. It integrates with checkout, composefs, commit tree reuse, generic GIO traversal, and callers that treat committed OSTree content as a virtual filesystem.

### Risks And Edge Cases
Resolution assumes parent dirtree arrays are sorted for `ot_variant_bsearch_str()`. Child paths are represented by object parent/name links and do not perform native filesystem access until content is loaded from the repo. `get_parent()` returns a ref of `self->parent`, so callers should avoid requesting the parent of the root. `get_basename()` can return null for root because root has no name. Symlink `read` follows the symlink target recursively through the virtual tree, so loops or missing targets can surface as GIO read errors. `ostree_repo_file_get_checksum()` asserts the child exists and should only be called after resolution paths that guarantee existence.

### Test Signals
Useful tests include root creation from commits, lazy resolution of nested files and directories, missing child errors, xattr loading for files and directories, GIO path/URI/equality/hash behavior, relative path resolution including absolute paths and root, enumeration through `OstreeRepoFileEnumerator`, query info for requested attributes, hidden-file attribute handling, regular file reads, symlink reads, and tree reuse by commit-writing code.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-file.h -->
## sources/cloud-native/ostree/src/libostree/ostree-repo-file.h

### Purpose
This public header declares the `OstreeRepoFile` GObject/GFile type and helper APIs for inspecting OSTree commit tree nodes.

### Important APIs, Types, And Functions
It defines `OSTREE_TYPE_REPO_FILE` and cast/check/get-class macros, declares `OstreeRepoFileClass`, exposes `ostree_repo_file_get_type()`, and declares APIs for ensuring resolution, reading xattrs, accessing the owning repo and root, setting and getting directory metadata and contents checksums, accessing tree contents/metadata variants, retrieving a node checksum, finding a child in a tree, and querying child info.

### Control Flow
There is no executable control flow in the header. The declarations map to the lazy-resolution and GFile implementation in `ostree-repo-file.c`.

### State And Persistence
The header exposes functions that read in-memory or repository-backed tree state. `ostree_repo_file_tree_set_metadata()` is the notable mutating declaration, replacing the in-memory directory metadata checksum and variant on an `OstreeRepoFile`.

### Dependencies And Integration Points
It includes `ostree-types.h` and uses GLib/GIO types such as `GType`, `GVariant`, `GFileInfo`, `GFileQueryInfoFlags`, `GCancellable`, and `GError`. It is consumed by composefs checkout, repo file enumeration, commit tree writing, and any public API consumer that handles `OstreeRepoFile` values.

### Risks And Edge Cases
Because this is public API, signatures and type macros are ABI/API sensitive. Some getters can return null for unresolved or non-directory nodes as documented in the implementation. Callers need to understand ownership annotations: repo/root getters are transfer-none, while xattrs and query-child info transfer full through out parameters.

### Test Signals
Direct signals are header compilation, GI/API generation, and ABI checks. Indirect behavior should be covered through `ostree-repo-file.c` tests for resolution, metadata access, xattr access, and GIO interoperability.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-finder-avahi-parser.c -->
## sources/cloud-native/ostree/src/libostree/ostree-repo-finder-avahi-parser.c

### Purpose
This file parses Avahi/DNS-SD TXT records for OSTree repository discovery. It converts an `AvahiStringList` into a normalized `GHashTable` mapping lowercase TXT keys to optional `GBytes` values.

### Important APIs, Types, And Functions
The internal parser helper `parse_txt_record()` validates and splits one TXT item according to RFC 6763 section 6 constraints. The exported internal function `_ostree_txt_records_parse()` walks an `AvahiStringList`, parses each record, lowercases keys with `g_ascii_strdown()`, stores values as `GBytes`, and skips invalid or duplicate records with debug logging.

### Control Flow
For each TXT record, `_ostree_txt_records_parse()` gets text bytes and length from Avahi, calls `parse_txt_record()`, ignores invalid records, lowercases the key, ignores duplicate keys, and inserts the key/value pair into a hash table. `parse_txt_record()` rejects records over 8900 bytes, accepts printable ASCII key characters except `=`, treats the first `=` after a non-empty key as the key/value separator, distinguishes absent values from empty values, and requires a non-empty key.

### State And Persistence
The returned hash table owns allocated lowercase key strings and `GBytes` value objects. Values are created with `g_bytes_new_static()` and are only valid because the parser contract says the returned table is valid as long as the original Avahi TXT storage remains valid. There is no persistent repository state.

### Dependencies And Integration Points
The file depends on Avahi string-list APIs, GLib/GObject, libglnx, and the private Avahi finder header. It integrates with `ostree-repo-finder-avahi` discovery code, which can consume normalized TXT keys such as repo metadata advertised over DNS-SD.

### Risks And Edge Cases
The lifetime of `GBytes` values is tied to Avahi-provided memory because `g_bytes_new_static()` does not copy. Consumers must not outlive the `AvahiStringList`. Duplicate keys are ignored after the first parsed occurrence, so record ordering can affect which value is retained. The parser lowercases keys and accepts key-only records by storing a null value, distinct from `key=` which stores an empty `GBytes`.

### Test Signals
Tests should cover valid key/value, key-only, empty-value, uppercase key normalization, duplicate suppression, invalid characters, empty keys, oversized records, records with multiple `=` characters, binary values after the separator, and lifetime expectations when consuming returned `GBytes`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-finder-avahi-parser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-finder-avahi-private.h -->
## sources/cloud-native/ostree/src/libostree/ostree-repo-finder-avahi-private.h

### Purpose
This private header declares the Avahi TXT record parser used by OSTree repo finder Avahi support.

### Important APIs, Types, And Functions
It includes Avahi and GLib/GIO headers and declares `GHashTable *_ostree_txt_records_parse(AvahiStringList *txt);`.

### Control Flow
There is no runtime control flow in this header. It provides the parser declaration for Avahi finder implementation files and tests.

### State And Persistence
The declaration returns an owned `GHashTable` built by the parser implementation. No state is stored in the header.

### Dependencies And Integration Points
The header depends on `avahi-common/strlst.h`, `gio/gio.h`, `glib-object.h`, and `glib.h`. It integrates `ostree-repo-finder-avahi-parser.c` with the broader Avahi repository discovery implementation.

### Risks And Edge Cases
The main risk is keeping this private declaration synchronized with the parser implementation and ensuring all users understand the returned table's value lifetime constraints from the implementation.

### Test Signals
Build coverage for Avahi-enabled configurations and parser unit tests including this header provide the relevant signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-finder-avahi-private.h -->
