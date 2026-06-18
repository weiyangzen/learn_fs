# subset-b-000044 research

This grouped report covers the requested composefs library, build, and test files. Each section is wrapped with the required source-path markers for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/hash.c -->
# sources/cloud-native/composefs/libcomposefs/hash.c

## Purpose
`hash.c` is the bundled gnulib generic hash-table implementation used inside libcomposefs for small internal indexes, notably shared xattr deduplication and image-load inode tracking. It provides separate-chaining buckets, optional custom hash/comparator/free callbacks, load-factor-based growth, optional shrink behavior, and traversal helpers.

## Important APIs, Types, And Functions
The private `struct hash_entry` stores user data plus overflow links. `struct hash_table` owns bucket storage, counts, tuning, callbacks, and a recycled overflow-entry list. Public implementations include `hash_initialize`, `hash_free`, `hash_clear`, `hash_lookup`, `hash_insert`, `hash_insert_if_absent`, `hash_remove`, `hash_rehash`, `hash_get_entries`, and statistics helpers. `safe_hasher` aborts if a caller-provided hasher returns an out-of-range bucket. `hash_string` supplies the string hash used by composefs filters and xattr keys.

## Control Flow
Initialization validates tuning, chooses a prime bucket count, and allocates zeroed bucket heads. Lookup hashes to a bucket then compares the head and overflow chain. Insert checks for an existing equal entry, grows when used buckets exceed the threshold, and either fills an empty head or allocates/reuses an overflow entry. Remove unlinks matching data, recycles overflow nodes, and may shrink. Rehash transfers entries to a stack-local table and carefully rolls back on allocation failure.

## State And Persistence
All state is in-memory only. The table does not copy user data; ownership of stored data is defined by the caller and optional `data_freer`.

## Dependencies And Integration Points
It depends on `hash.h`, `bitrotate.h`, `xalloc-oversized.h`, libc allocation, and `config.h` compile flags. Meson forces `USE_OBSTACK=0`, `TESTING=0`, and `USE_DIFF_HASH=0`, so composefs uses malloc-backed buckets and the recode-style string hash.

## Risks
Hashers that return values outside the bucket range abort. NULL entries are unsupported and abort in insert-if-absent. Traversal is invalid across table mutation as documented in the header. Rehash rollback is complex and should be treated as high-risk for allocation-failure changes.

## Test Signals
There is no direct hash-table test in this subset. Coverage is indirect through EROFS writer shared-xattr tables, loader inode hash tables, and filtered toplevel entry hashing in `test-checksums.sh`, `test-random-fuse.sh`, and `test-lcfs.c`.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/hash.h -->
# sources/cloud-native/composefs/libcomposefs/hash.h

## Purpose
`hash.h` declares the gnulib hash-table API embedded in libcomposefs. It exposes the opaque `Hash_table`, tuning parameters, callback types, lookup/traversal APIs, allocation/free APIs, and insertion/removal functions consumed by internal composefs code.

## Important APIs, Types, And Functions
`Hash_tuning` controls shrink/growth thresholds, factors, and whether the initialization candidate is an entry count or bucket count. `Hash_hasher`, `Hash_comparator`, and `Hash_data_freer` define caller-provided behavior. Important functions are `hash_initialize`, `hash_free`, `hash_clear`, `hash_lookup`, `hash_get_entries`, `hash_do_for_each`, `hash_insert`, `hash_insert_if_absent`, `hash_remove`, `hash_rehash`, and `hash_string`.

## Control Flow
The header documents the caller contract: create a table with callbacks, insert non-NULL entries, look up by comparable key objects, optionally walk all entries, and release with `hash_free`. It also warns that mutation during traversal is restricted.

## State And Persistence
The header defines no persistent storage. It establishes that user entries are stored by pointer and that `data_freer` is invoked only during `hash_free`/`hash_clear`.

## Dependencies And Integration Points
It includes `config.h`, `stdio.h`, and `stdbool.h`, and uses GNU-style attributes. Composefs integrates it in `lcfs-writer-erofs.c` for xattr and inode maps.

## Risks
The declared `hash_xinitialize` and `hash_xinsert` are not implemented in `hash.c` in this subset; composefs does not use them. Callers must not pass NULL entries and must ensure hash/comparator consistency.

## Test Signals
No direct header tests exist. API compatibility is validated indirectly by successful libcomposefs build and tests that exercise writer/loader hash usage.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/lcfs-erofs-internal.h -->
# sources/cloud-native/composefs/libcomposefs/lcfs-erofs-internal.h

## Purpose
This private header bridges composefs node logic and EROFS on-disk structures. It defines inode helpers, xattr prefix conversions, ACL recognition, and the chunking API used by both writer validation and EROFS serialization.

## Important APIs, Types, And Functions
`erofs_inode` is a union over raw `i_format`, compact inode, and extended inode. Inline helpers decode inode version, datalayout, tailpacking, flat layout, xattr inode size, ACL xattrs, xattr prefix indexes, and full xattr names. `erofs_compute_chunking` is declared for non-inline regular-file stubs.

## Control Flow
Writer and loader code call these helpers while computing layout or parsing image data. Xattr prefix lookup scans `erofs_xattr_prefixes`, maps known EROFS indexes back to full names, and allocates reconstructed names for loader xattr handling.

## State And Persistence
The only static data is `erofs_xattr_prefixes`. It models EROFS xattr namespaces and affects persisted xattr names in images.

## Dependencies And Integration Points
It depends on `lcfs-internal.h`, public EROFS composefs header definitions, and `erofs_fs_wrapper.h`. It is central to `lcfs-writer-erofs.c` and also used by `lcfs-writer.c` validation.

## Risks
`erofs_get_xattr_name` allocates and returns NULL on invalid index or ENOMEM. Prefix ordering matters because broad prefixes such as `trusted.` must not shadow more specific entries incorrectly. Chunking limits feed `LCFS_MAX_NONINLINE_CHUNKS`.

## Test Signals
Covered indirectly by checksum fixtures, random FUSE/image round trips, should-fail oversized fixtures, and `test-lcfs.c` image-load regression.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/lcfs-erofs-internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/lcfs-erofs.h -->
# sources/cloud-native/composefs/libcomposefs/lcfs-erofs.h

## Purpose
`lcfs-erofs.h` defines the public composefs-on-EROFS image header. It is the magic/version/flags contract that lets readers identify composefs images before interpreting the embedded EROFS filesystem.

## Important APIs, Types, And Functions
`LCFS_EROFS_VERSION` is `1`, `LCFS_EROFS_MAGIC` is `0xd078629aU`, and `LCFS_EROFS_FLAGS_HAS_ACL` records whether ACL xattrs are present. `struct lcfs_erofs_header_s` stores magic, version, flags, composefs format version, and unused reserved words in a packed layout.

## Control Flow
Writers emit this header before the EROFS superblock. Loaders and mounters read it first, validate magic/version, inspect flags, and use `composefs_version` for compatibility reporting.

## State And Persistence
This header is persistent on disk at the beginning of every composefs EROFS image. Its packed layout and endian conversion in writer/reader paths are part of the image ABI.

## Dependencies And Integration Points
It is included by writer, loader, mounter, and tests. `lcfs-mount.c` uses flags to decide whether to mount EROFS with `noacl`; `lcfs-writer.c` uses the header to report image version.

## Risks
Changing field order, size, magic, or version breaks image compatibility. Reserved fields should remain zeroed until a documented extension consumes them.

## Test Signals
Image checksum fixtures, `lcfs_version_from_fd`, `test-lcfs.c` handcrafted image setup, and mount tests all validate this header path indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/lcfs-erofs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/lcfs-fsverity.c -->
# sources/cloud-native/composefs/libcomposefs/lcfs-fsverity.c

## Purpose
`lcfs-fsverity.c` computes fs-verity-compatible SHA-256 digests in userspace. It supports OpenSSL when available and includes a fallback SHA-256 implementation otherwise.

## Important APIs, Types, And Functions
`FsVerityContext` stores per-level 4096-byte Merkle buffers, positions, max level, file size, and optionally an OpenSSL `EVP_MD_CTX`. Public functions are `lcfs_fsverity_context_new`, `free`, `update`, and `get_digest`. Private helpers include fallback `sha256_sum_*`, `do_sha256`, level update/flush routines, and `struct fsverity_descriptor`.

## Control Flow
Updates append data to level 0. Full 4096-byte blocks are hashed lazily into 32-byte digests passed to the next level. Finalization zero-pads partial blocks, recursively flushes upper levels, hashes the root block into an fs-verity descriptor, and hashes that descriptor to produce the exported digest.

## State And Persistence
State is streaming and in-memory. The output digest is persisted by callers as overlay metacopy xattr data, digest store naming input, or image digest output.

## Dependencies And Integration Points
It depends on endian helpers from `lcfs-internal.h`, `lcfs-fsverity.h`, OpenSSL when `HAVE_OPENSSL`, and composefs constants `FSVERITY_BLOCK_SIZE` and digest length. `lcfs-writer.c` wraps it for fd/data/content digest APIs.

## Risks
The fallback SHA-256 uses 32-bit bit counters, so extremely large streams rely on existing logic and should be tested carefully. `get_digest` mutates/flushed context state; repeated calls are not a general reset. OpenSSL assertions abort on impossible EVP failures.

## Test Signals
`test-units.sh` verifies known `composefs-info measure-file` digests and compares kernel fs-verity measurements when available. Integration and mount digest tests exercise end-to-end digest behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/lcfs-fsverity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/lcfs-fsverity.h -->
# sources/cloud-native/composefs/libcomposefs/lcfs-fsverity.h

## Purpose
This header exposes the opaque streaming fs-verity digest context used by libcomposefs internals.

## Important APIs, Types, And Functions
It forward declares `FsVerityContext`, defines `LCFS_SHA256_DIGEST_LEN` as 32, and declares constructor, destructor, update, and final digest functions.

## Control Flow
Callers create a context, feed byte ranges in order, request the digest into a 32-byte buffer, and free the context.

## State And Persistence
No persistent state is defined here; persistence is through the returned digest consumed by writer and tooling paths.

## Dependencies And Integration Points
It includes `stdint.h` and `stddef.h`. `lcfs-internal.h` includes it so writer code can embed `FsVerityContext *` in `lcfs_ctx_s`.

## Risks
The API does not expose errors for update/get operations; allocation failure is only reported by `new` returning NULL. Callers must supply a valid 32-byte digest output buffer.

## Test Signals
Covered by writer digest output, measure-file tests, mount digest tests, and image checksum fixtures.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/lcfs-fsverity.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/lcfs-internal.h -->
# sources/cloud-native/composefs/libcomposefs/lcfs-internal.h

## Purpose
`lcfs-internal.h` defines libcomposefs private data structures, endian/align macros, overlay xattr constants, validation limits, and internal function prototypes shared by writer, EROFS, mount, and utility code.

## Important APIs, Types, And Functions
Key types are `errint_t`, `struct lcfs_xattr_s`, `struct lcfs_inode_s`, `struct lcfs_node_s`, and `struct lcfs_ctx_s`. The node holds refcount, parent/children, hardlink target, name, payload, inline content, xattrs, digest, inode metadata, and temporary EROFS layout fields. The context holds write options, root, queue/layout state, output callback, byte count, fs-verity context, and a format finalizer.

## Control Flow
This header does not execute control flow but codifies the phases used elsewhere: tree construction, compute-tree BFS, format-specific EROFS layout, serialization, digest computation, and cleanup. `cleanup_node` wraps `lcfs_node_unref` for local ownership.

## State And Persistence
In-memory node state maps to persisted EROFS inode metadata, xattrs, payload redirects, inline content, and digest xattrs. Temporary fields such as `next`, `in_tree`, `inode_num`, and `erofs_*` are recomputed during writes.

## Dependencies And Integration Points
It includes endian headers selected by Meson, public writer/fsverity/hash headers, and exposes prototypes implemented by `lcfs-writer.c` and `lcfs-writer-erofs.c`.

## Risks
This is the central ownership contract. Refcount, parent, hardlink, and child ownership mistakes can cause leaks, double unrefs, or cycles. Overlay xattr constants must match kernel overlayfs expectations.

## Test Signals
Most tests exercise this header indirectly. `test-lcfs.c` specifically covers ref/child ownership, invalid uninitialized nodes, xattr replacement, and hardlinked whiteout image-load handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/lcfs-internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/lcfs-mount.c -->
# sources/cloud-native/composefs/libcomposefs/lcfs-mount.c

## Purpose
`lcfs-mount.c` mounts composefs images by first mounting the embedded EROFS image and then overlaying it with one or more object directories as data lowerdirs. It supports digest verification, idmapped EROFS mounts, new Linux mount APIs, legacy mount fallback, and loop-device fallback.

## Important APIs, Types, And Functions
Public entry points are `lcfs_mount_fd` and `lcfs_mount_image`. Private state is `struct lcfs_mount_state_s`. Helpers wrap `fsopen`, `fsconfig`, `fsmount`, `move_mount`, and optionally `mount_setattr`. Major functions are `lcfs_validate_mount_options`, `lcfs_validate_verity_fd`, `setup_loopback`, `compute_lower`, `lcfs_mount_erofs`, `lcfs_mount_ovl`, `lcfs_mount_ovl_legacy`, and `lcfs_mount_erofs_ovl`.

## Control Flow
Options are validated first, including flags, objdirs, upper/workdir pairing, digest parsing, and idmap fd. If an expected digest is configured, the image fd is measured with kernel fs-verity and compared. The composefs header is read; valid EROFS images mount into a temporary image mountdir. Overlayfs is then mounted over the target with metacopy, redirect_dir, lowerdir/datadir entries, optional upper/workdir, optional verity, and readonly flags. New mount API failures caused by unsupported features fall back to legacy comma-escaped mount options.

## State And Persistence
It creates transient mounts, optional temporary directories, and loop devices with autoclear. It does not alter image contents. Digest expectations are parsed into `expected_digest`.

## Dependencies And Integration Points
It depends on Linux mount, loop, fsverity, and syscall interfaces; internal endian/header helpers; and `digest_to_raw`. CLI mount tooling wraps these APIs.

## Risks
Mount behavior is kernel-version-sensitive. Legacy overlay option construction depends on correct comma escaping. `expected_digest_len` can parse non-32-byte hex strings but comparison uses `LCFS_DIGEST_SIZE`, so callers should pass full SHA-256 strings. Temporary mount cleanup uses detached unmount and rmdir.

## Test Signals
`test-units.sh` checks digest mismatch and valid digest behavior. `integration.sh` mounts real images. Random FUSE tests cover a related user-space path, while kernel mount coverage depends on privileges and host support.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/lcfs-mount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/lcfs-mount.h -->
# sources/cloud-native/composefs/libcomposefs/lcfs-mount.h

## Purpose
`lcfs-mount.h` is the public libcomposefs mount API. It defines mount flags, option structure, public error aliases, and entry points for mounting from a path or fd.

## Important APIs, Types, And Functions
Error aliases are `ENOVERITY`, `EWRONGVERITY`, and `ENOSIGNATURE`. `enum lcfs_mount_flags_t` includes require-verity, readonly, idmap, and try-verity bits plus a mask. `struct lcfs_mount_options_s` contains object dirs, upper/work dirs, expected fs-verity digest, flags, idmap fd, image mount dir, and reserved ABI fields. Public functions are `lcfs_mount_image` and `lcfs_mount_fd`.

## Control Flow
Callers populate options, pass an image path or fd and mountpoint, and receive `0` or `-1` with `errno` set. Lower-level mount sequencing is implemented in `lcfs-mount.c`.

## State And Persistence
This header defines no state itself. Option fields drive mount creation and transient kernel mount state.

## Dependencies And Integration Points
It includes standard C and system stat headers and is installed by `libcomposefs/meson.build`. Tools such as `mount.composefs` use it.

## Risks
Reserved fields are part of ABI padding and should not be repurposed casually. Flags outside `LCFS_MOUNT_FLAGS_MASK` are rejected.

## Test Signals
Mount digest behavior in `test-units.sh` and integration mounting validate this API indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/lcfs-mount.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/lcfs-utils.c -->
# sources/cloud-native/composefs/libcomposefs/lcfs-utils.c

## Purpose
`lcfs-utils.c` implements digest string/raw conversion helpers shared by tools and mount code.

## Important APIs, Types, And Functions
`digest_to_string` converts a 32-byte composefs digest to lowercase hex plus NUL. `digest_to_raw` parses a hex string into bytes up to a caller-supplied maximum, returning byte count or `-1` on invalid hex, odd input, or overflow.

## Control Flow
String conversion iterates digest bytes and emits two hex digits each. Raw parsing consumes two chars at a time through `hexdigit`; a missing second nibble is rejected because `hexdigit('\0')` returns negative.

## State And Persistence
No persistent state. Outputs are caller-provided buffers used for display, file paths, and mount digest comparison.

## Dependencies And Integration Points
It includes `lcfs-utils.h` and `lcfs-writer.h` for `LCFS_DIGEST_SIZE`. `lcfs-mount.c` uses `digest_to_raw`; tools use these helpers for user-facing digest output.

## Risks
`digest_to_raw` accepts any even-length hex string up to `max_size`; callers that require exact SHA-256 length must validate the returned size. No errno is set on parse failures.

## Test Signals
Digest output and digest mount tests in `test-units.sh`, checksum tests, and integration scripts exercise these conversions indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/lcfs-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/lcfs-utils.h -->
# sources/cloud-native/composefs/libcomposefs/lcfs-utils.h

## Purpose
`lcfs-utils.h` provides small utility macros and inline helpers for libcomposefs: min/max, prefix checks, memory duplication, overflow-safe reallocarray fallback, hex parsing, cleanup attributes, fd cleanup, pointer stealing, basename extraction, and digest conversion declarations.

## Important APIs, Types, And Functions
Important helpers are `str_has_prefix`, `memdup`, `size_multiply_overflow`, fallback `reallocarray`, `hexdigit`, `str_join`, `PROTECT_ERRNO`, `cleanup_freep`, `cleanup_fdp`, `steal_pointer`, and `gnu_basename`. It also declares `digest_to_string` and `digest_to_raw`.

## Control Flow
Most helpers are inline single-purpose building blocks. Cleanup attributes close fds or free memory automatically at scope exit while preserving errno. `steal_pointer` transfers cleanup-managed ownership by nulling the source pointer.

## State And Persistence
No persistent state. It strongly affects local ownership and error preservation patterns across the library.

## Dependencies And Integration Points
Included by writer, EROFS writer, mount, and utility code. Meson config controls whether the fallback `reallocarray` is active.

## Risks
`max`/`min` macros evaluate arguments more than once. The type-safe `steal_pointer` macro shadows the inline function intentionally and can surprise static analysis. Cleanup helpers assume initialized pointers/fds.

## Test Signals
Indirectly covered everywhere. Error-path tests and valgrind setup in Meson are useful for validating cleanup behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/lcfs-utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/lcfs-writer-erofs.c -->
# sources/cloud-native/composefs/libcomposefs/lcfs-writer-erofs.c

## Purpose
`lcfs-writer-erofs.c` is the format-specific engine that serializes `lcfs_node_s` trees into composefs EROFS images and loads EROFS images back into node trees. It also rewrites trees for overlayfs semantics, including metacopy, redirects, whiteouts, shared xattrs, and synthetic `.`/`..` entries.

## Important APIs, Types, And Functions
Public/internal entry points are `lcfs_ctx_erofs_new`, `lcfs_write_erofs_to`, `lcfs_load_node_from_image_ext`, and `lcfs_load_node_from_image`. Important private groups include xxh32 xattr filtering; shared xattr hash helpers; `compute_erofs_*` layout functions; `write_erofs_*` serialization functions; overlay rewrite helpers; and loader helpers `lcfs_image_get_erofs_inode`, `erofs_readdir_block`, `lcfs_build_node_erofs_xattr`, and `lcfs_build_node_from_image`.

## Control Flow
Write flow clones the root, rewrites nodes for overlayfs, computes deterministic BFS tree order, deduplicates shared xattrs, computes inode sizes/padding/block addresses, writes composefs header and EROFS superblock, writes inode metadata and inline tails, writes shared xattrs, aligns, then writes out-of-band data blocks. Load flow validates composefs and EROFS headers, derives metadata/xattr regions, builds an inode hash to preserve hardlinks, recursively reads directories, reconstructs symlinks/inline content/non-inline stubs, interprets overlay xattrs back into payload/digest/whiteouts, and optionally filters toplevel entries.

## State And Persistence
The writer persists EROFS superblock, compact/extended inodes, xattr headers, inline and block data, chunk-based stubs, and composefs overlay xattrs. Temporary state lives in `lcfs_ctx_erofs_s` and per-node `erofs_*` fields.

## Dependencies And Integration Points
It depends on EROFS kernel-format wrappers, internal node model, hash table, fs-verity constants, Linux fsverity xattr encoding, and utility cleanup helpers. It is selected by `lcfs_write_to` for `LCFS_FORMAT_EROFS`.

## Risks
This is high-risk code: layout math, endian conversion, block alignment, shared xattr offsets, hardlink reconstruction, and overlay xattr escaping are correctness-critical. Non-inline regular files are represented as null chunk pointers and limited by `LCFS_MAX_NONINLINE_CHUNKS`. Loader bounds checks are partial and rely on image size validation plus format assumptions.

## Test Signals
Strong coverage comes from checksum fixtures, `fsck.erofs` validation when available, dump round trips, random FUSE/image tests, should-fail malformed fixtures, filtered dump tests, and `test-lcfs.c` hardlinked-whiteout regression.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/lcfs-writer-erofs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/lcfs-writer.c -->
# sources/cloud-native/composefs/libcomposefs/lcfs-writer.c

## Purpose
`lcfs-writer.c` implements the public node/tree API, filesystem tree ingestion, fs-verity helper wrappers, generic write context handling, and format dispatch for composefs images.

## Important APIs, Types, And Functions
Major public APIs include node lifecycle, cloning, loading from files/fds/images, building directory trees, child/xattr/payload/content accessors, fs-verity digest helpers, `lcfs_write_to`, and `lcfs_fd_enable_fsverity`. Important internals are `lcfs_compute_tree`, `follow_links`, `lcfs_write`, `lcfs_write_pad`, `lcfs_write_align`, `read_xattrs`, `lcfs_node_set_from_content`, `lcfs_node_validate`, and xattr set/unset/rename logic.

## Control Flow
Tree build starts with `lcfs_load_node_from_file`, records stat metadata, optional content digest/payload/inline content, symlink target, mtime, and xattrs, then recursively descends directories. Writing validates flags/version, may upgrade version for whiteouts, creates a format context, dispatches to the EROFS writer, captures digest output, and closes context. `lcfs_compute_tree` sorts xattrs, fixes directory nlink counts, forbids directory hardlinks, assigns BFS inode numbers, and verifies hardlink targets are in-tree.

## State And Persistence
Nodes own children, xattrs, payloads, inline content, digest, and inode metadata. Write contexts stream bytes to callbacks and optionally compute a fs-verity digest of the generated image. Persistent output is delegated to `lcfs-writer-erofs.c`.

## Dependencies And Integration Points
It depends on Linux stat/xattr/fsverity/ioctl APIs, EROFS chunking, internal hash/util helpers, and the public writer/mount headers. Tools use this as the main library surface.

## Risks
Ownership is subtle: `lcfs_node_add_child` takes ownership on success, children cannot be re-added, and hardlink refs can create invalid cycles caught lazily. Xattr size accounting limits external input. `lcfs_fd_get_fsverity` checks errno values after a helper that returns negative errno, which deserves care because the helper may canonicalize return codes and errno differently.

## Test Signals
`test-lcfs.c` covers basic writes, invalid uninitialized children, xattr add/remove/overwrite, fsverity absence, and a loader regression. Shell tests cover inline/object behavior, checksums, dump round trips, malformed input rejection, and random trees.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/lcfs-writer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/lcfs-writer.h -->
# sources/cloud-native/composefs/libcomposefs/lcfs-writer.h

## Purpose
`lcfs-writer.h` is the installed public API for constructing, inspecting, loading, and writing composefs node trees and fs-verity digests.

## Important APIs, Types, And Functions
It defines build flags, `LCFS_DIGEST_SIZE`, format/flags enums, version constants, inline/xattr limits, callback types, `struct lcfs_write_options_s`, `struct lcfs_read_options_s`, node lifecycle APIs, load APIs, xattr APIs, payload/content APIs, child/tree APIs, inode metadata APIs, digest APIs, `lcfs_build`, and `lcfs_write_to`.

## Control Flow
Users can build nodes manually or call `lcfs_build`, configure write options, then write an image through a callback. Image loading can use bytes, fd, or filtered read options.

## State And Persistence
The header defines the ABI contract for in-memory node manipulation and image generation options. Reserved fields preserve space for future ABI evolution.

## Dependencies And Integration Points
Installed by Meson under `libcomposefs`. It is included by tools, tests, internal headers, and potential external consumers.

## Risks
Some setters such as `lcfs_node_set_mode` do not validate; callers should prefer `lcfs_node_try_set_mode` or rely on write-time validation. Build flags have interactions such as skip-xattrs conflicting with user-xattrs.

## Test Signals
`test-lcfs.c` compiles directly against this header. All tool-based tests validate its ABI through libcomposefs.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/lcfs-writer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/meson.build -->
# sources/cloud-native/composefs/libcomposefs/meson.build

## Purpose
This Meson file builds libcomposefs and its small internal static utility library, declares source membership, applies composefs hash/visibility flags, links dependencies, generates pkg-config metadata, and installs public headers.

## Important APIs, Types, And Functions
It defines `internal_source_files`, `libcomposefs_internal`, `source_files`, `libcomposefs`, `pkg.generate`, and `install_headers`. Installed headers are `lcfs-writer.h`, `lcfs-erofs.h`, and `lcfs-mount.h`.

## Control Flow
Meson first builds `composefs-internal` from utils, then builds both shared and static `composefs` libraries from core sources, linking libcrypto and the internal library. It passes `composefs_hash_cflags` and hidden visibility flags from the top-level build.

## State And Persistence
Build outputs are libraries, pkg-config files, and installed headers. It does not generate runtime state.

## Dependencies And Integration Points
Consumes `config_inc`, `composefs_hash_cflags`, `hidden_visibility_cflags`, `libcrypto_dep`, and version variables defined in top-level `meson.build`.

## Risks
Adding a new public API source or header requires updating this file. Hash compile flags must remain consistent with the bundled gnulib implementation.

## Test Signals
Every Meson test depends on this target. ABI exposure is checked by compiling `tests/test-lcfs.c` against the library.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/meson.build -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/xalloc-oversized.h -->
# sources/cloud-native/composefs/libcomposefs/xalloc-oversized.h

## Purpose
This gnulib header provides `xalloc_oversized(n, s)`, a macro that detects multiplication sizes too large for reliable allocation.

## Important APIs, Types, And Functions
`__xalloc_oversized` implements the portable division check. `xalloc_oversized` selects compiler builtins for GCC configurations where they are safe, otherwise uses the portable macro.

## Control Flow
Callers evaluate the macro before allocating arrays. `hash.c` uses it while computing bucket array sizes.

## State And Persistence
No state. It only prevents invalid allocation size calculations.

## Dependencies And Integration Points
Includes `stddef.h` and `stdint.h`. Integrated by `hash.c`.

## Risks
It is macro-based, so callers must pass side-effect-free arguments as documented. Incorrect compiler feature conditions could misdetect overflow on unusual targets.

## Test Signals
No direct tests. Indirectly exercised by hash initialization/rehash under writer/loader hash-table usage.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/xalloc-oversized.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/man/meson.build -->
# sources/cloud-native/composefs/man/meson.build

## Purpose
This Meson file generates and installs man pages from Markdown sources using `go-md2man`.

## Important APIs, Types, And Functions
The `manuals` dictionary maps man sections to page base names. A nested `foreach` creates one `custom_target` per page with `go-md2man -in @INPUT@ -out @OUTPUT@`, installing into `mandir/man<section>`.

## Control Flow
The top-level build enters this subdir only when `go-md2man` is found according to the `man` feature option.

## State And Persistence
Generated man page files are build artifacts and install artifacts.

## Dependencies And Integration Points
Depends on the top-level `go_md2man` program variable and Meson install directories. Covers `mkcomposefs`, `composefs-info`, `composefs-dump`, and `mount.composefs`.

## Risks
Missing Markdown source files or a missing converter prevents man generation when the feature is required. Page lists must stay synchronized with tool names.

## Test Signals
No direct tests in this subset. Build success with `-Dman=enabled` validates the generation path.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/man/meson.build -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/meson.build -->
# sources/cloud-native/composefs/meson.build

## Purpose
The top-level Meson build defines the composefs project, compiler warnings, dependencies, feature probes, generated config header, subdirectories, library versioning, and subproject dependency export.

## Important APIs, Types, And Functions
It declares project version `1.0.8`, libcomposefs ABI version `1.4.0`, `composefs_hash_cflags`, dependency probes for fuse3 and libcrypto, `configuration_data` entries, visibility flags, `config_h`, `config_inc`, subdirs, and `composefs_dep`.

## Control Flow
Meson checks compiler flags, headers, required libc functions, optional endian/reallocarray/mount API features, visibility support, and optional dependencies. It configures `config.h`, enters `libcomposefs`, `tools`, `tests`, and conditionally `man`.

## State And Persistence
Build configuration state is emitted to `config.h`; build outputs include libraries, tools, tests, and optional man pages.

## Dependencies And Integration Points
This file coordinates the whole composefs source tree. `config.h` macros control OpenSSL use, FUSE support, endian includes, mount API paths, and symbol visibility.

## Risks
Feature detection affects runtime code paths in mount and fsverity logic. Warning flags are strict and may break builds on new compilers. `libcrypto_dep` is not feature-optional in this file even though fsverity has fallback SHA-256 code.

## Test Signals
All Meson tests rely on this configuration. Valgrind setup in tests depends on generated build targets.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/meson.build -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/meson_options.txt -->
# sources/cloud-native/composefs/meson_options.txt

## Purpose
This file declares user-visible Meson feature options for optional man-page generation and FUSE support.

## Important APIs, Types, And Functions
Options are `man` and `fuse`, both `feature` type with default `auto`. `man` controls use of `go-md2man`; `fuse` controls the `fuse3 >= 3.10.0` dependency and FUSE tool support.

## Control Flow
Top-level `meson.build` reads these options through `get_option`.

## State And Persistence
No runtime state. These options persist in Meson build configuration.

## Dependencies And Integration Points
`man/meson.build` is entered only when `go-md2man` is found according to the option. FUSE dependency status is exposed in `config.h` as `HAVE_FUSE3`.

## Risks
Setting either option to `enabled` makes missing dependencies fatal. Default `auto` can produce different build surfaces across machines.

## Test Signals
FUSE-dependent tests skip or reduce behavior when `/dev/fuse` and capabilities are unavailable; build option effects are mostly validated by target presence.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/meson_options.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/tests/dumpdir -->
# sources/cloud-native/composefs/tests/dumpdir

## Purpose
`dumpdir` is a Python test utility that prints a deterministic textual dump of a filesystem tree, including metadata, content digest, symlink target, and xattrs. It is used to compare source directories, mounted composefs views, and FUSE views.

## Important APIs, Types, And Functions
Core functions are `should_convert_whiteout`, `has_whiteout_child`, `dumpfile`, and `dumpdir`. CLI options control nlink normalization, user xattrs only, whiteout conversion, and escaped-overlay xattr filtering.

## Control Flow
The script dumps the root then walks directories top-down with sorted dirs and files. For each path it uses `lstat`, optionally converts whiteout chardevs to overlay-style regular-file markers, prints stat fields, regular-file SHA-256 or symlink target, then sorted xattrs.

## State And Persistence
It reads filesystem state but does not modify it. Output is a stable comparison artifact.

## Dependencies And Integration Points
Used by `integration.sh` and `test-random-fuse.sh`. Depends on Python `os`, `stat`, `hashlib`, `shlex`, and xattr support.

## Risks
Requires permissions to read files and xattrs. Whiteout conversion depends on test flags and kernel/device permissions. Full file reads can be expensive for large trees.

## Test Signals
This utility is itself a test oracle for mount/FUSE equivalence and random-tree round trips.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/tests/dumpdir -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/tests/fuzzing/run.sh -->
# sources/cloud-native/composefs/tests/fuzzing/run.sh

## Purpose
This shell script configures and runs honggfuzz against `tools/mkcomposefs` with sanitizers and a bubblewrap sandbox.

## Important APIs, Types, And Functions
It invokes `./configure` with `hfuzz-clang`, UBSan/ASan, static build flags, and sanitizer coverage flags; runs `make -j $(nproc)`; then launches `honggfuzz --verifier` against inputs under `tests/fuzzing`.

## Control Flow
The script is linear and uses `set -xeuo pipefail`: configure, build, sandbox, fuzz.

## State And Persistence
It creates build outputs and fuzzing runtime artifacts outside the Meson path. It does not alter source inputs.

## Dependencies And Integration Points
Depends on autotools-style `configure`, honggfuzz, hfuzz-clang, bubblewrap, and sanitizer runtime support. It targets `mkcomposefs` rather than library APIs directly.

## Risks
This path may be stale if the project is Meson-first. It requires privileged/sandbox tooling and can consume significant CPU.

## Test Signals
Fuzzing seeds include crash/regression assets referenced by Meson tests, such as honggfuzz-derived dump fixtures.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/tests/fuzzing/run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/tests/gendir -->
# sources/cloud-native/composefs/tests/gendir

## Purpose
`gendir` is a Python randomized filesystem tree generator for composefs round-trip and FUSE tests. It creates directories, files, symlinks, FIFOs, optional devices, optional whiteouts, and user xattrs.

## Important APIs, Types, And Functions
Important helpers include `Chance`, `gen_filename`, `gen_filenames`, `gen_hierarchy`, `set_user_xattr`, `make_regular_file`, `make_symlink`, `make_node`, `make_whiteout`, `make_fifo`, `make_file`, and `make_dir`.

## Control Flow
The script seeds Python randomness from `--seed` or os randomness, builds a random directory hierarchy, creates the root, then creates each directory and its random children. File content sizes are mostly small with occasional large files; some data is reused.

## State And Persistence
It mutates the target filesystem path and records no separate manifest. It may create xattrs and special files when permissions allow.

## Dependencies And Integration Points
Used by `test-random-fuse.sh` and `integration.sh`. Depends on Python filesystem APIs and optional privilege for `mknod`.

## Risks
Randomness can make failures hard to reproduce unless the printed seed is captured. The `--unreadable` byte-name mode can stress encoding assumptions. Special files and xattrs depend on host permissions/filesystem support.

## Test Signals
The generator feeds randomized coverage for writer ingestion, xattr handling, digest store object emission, whiteout conversion, FUSE equivalence, and dump reproducibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/tests/gendir -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/tests/integration.sh -->
# sources/cloud-native/composefs/tests/integration.sh

## Purpose
`integration.sh` is a privileged end-to-end test that builds composefs images from real and generated trees, mounts them with `mount.composefs`, and compares mounted output with source dumps.

## Important APIs, Types, And Functions
Main function `run_test` creates images with `mkcomposefs`, validates digest consistency, optionally runs `fsck.erofs`, mounts with `mount.composefs`, dumps source and mount with `dumpdir`, compares them, re-measures digest from mount, and unmounts.

## Control Flow
It optionally creates an ext4 verity loopback filesystem, initializes object/root/temp dirs, tests `/usr/bin`, checks fsverity support, generates a random privileged tree without whiteouts, and tests it with normalized root nlink.

## State And Persistence
It writes under `${cfsroot}` or `/composefs`, creates images, objects, temp dirs, mounts, and may create a temporary ext4 loopback disk.

## Dependencies And Integration Points
Depends on built tools, root/kernel mount permissions, optional `fsck.erofs`, `fsverity`, `mkfs.ext4`, and helper scripts.

## Risks
Destructive cleanup removes `${cfsroot}/tmp`; default `/composefs` must be safe in the test environment. Requires privileges and kernel features, so it is not a hermetic unit test.

## Test Signals
Strong end-to-end signal for digest stability, mount correctness, object store integration, and source/mount metadata equivalence.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/tests/integration.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/tests/meson.build -->
# sources/cloud-native/composefs/tests/meson.build

## Purpose
This Meson file registers composefs test assets, shell tests, the C unit test, and optional valgrind setup.

## Important APIs, Types, And Functions
It defines fixture lists `test_assets_small`, `test_assets_small_extra`, `test_assets_should_fail`, `test_assets`, `extra_dist`, `tools_dir`, and Meson `test()` calls for units, checksums, dump filtering, random FUSE, should-fail, and `test-lcfs`.

## Control Flow
Asset lists are assembled first, extra distribution entries are populated, shell tests are registered with appropriate args/timeouts, the C test executable links with `libcomposefs`, and valgrind setup is added if found.

## State And Persistence
No runtime state. It controls build/test graph and distributed test fixtures.

## Dependencies And Integration Points
Consumes built tools, `libcomposefs`, test scripts, fixture assets, and optional valgrind. It is entered by top-level Meson.

## Risks
The `test-checksums.sh` script expects four arguments but this Meson invocation passes three in the inspected file, while the script body does not use the fourth variable. Fixture lists must remain synchronized with asset files and expected checksums.

## Test Signals
This is the central test registration for the subset and maps implementation risks to automated checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/tests/meson.build -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/tests/test-checksums.sh -->
# sources/cloud-native/composefs/tests/test-checksums.sh

## Purpose
This shell test verifies that known dump fixtures produce byte-stable composefs images with expected SHA-256 checksums, pass optional `fsck.erofs`, and round-trip through dump tools reproducibly.

## Important APIs, Types, And Functions
It sources `test-lib.sh`, checks for `fsck.erofs`, maintains a `nonstrict` associative array, and loops over formats/assets. It invokes `mkcomposefs --from-file`, `sha256sum`, `composefs-dump`, and `composefs-info dump`.

## Control Flow
For each fixture, it detects `.gz`, optional version constraints, strict parse mode, builds an image, optionally runs fsck, checks dump reproduction via `composefs-dump`, checks text dump piped back to `mkcomposefs`, and compares the image checksum to the fixture `.sha256`.

## State And Persistence
Uses temporary image files and removes them via trap. Environment variable `CFS_PARSE_STRICT` is set/unset per fixture.

## Dependencies And Integration Points
Depends on built tools, assets, gzip, sha256sum, optional fsck.erofs, and `VALGRIND_PREFIX`.

## Risks
Checksum tests are intentionally brittle: any legitimate image-layout change requires fixture checksum updates. Non-strict fixture exceptions document tolerated legacy malformed inputs.

## Test Signals
High-value regression signal for deterministic serialization, loader/dumper reproducibility, parser strictness, and EROFS structural validity.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/tests/test-checksums.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/tests/test-dump-filtered.sh -->
# sources/cloud-native/composefs/tests/test-dump-filtered.sh

## Purpose
This shell test verifies `composefs-info dump` filtering behavior for selected file classes.

## Important APIs, Types, And Functions
It builds `special.dump` into an image using `mkcomposefs --from-file`, runs `composefs-info --filter=chardev --filter=inline --filter=whiteout dump`, counts output lines, and uses `assert_file_has_content`.

## Control Flow
Create tempdir, build image, dump with filters, assert exactly four lines, then match expected root, chardev, inline, and whiteout lines.

## State And Persistence
Only temporary files under a trap-managed tempdir.

## Dependencies And Integration Points
Depends on built tools, `special.dump`, and helpers from `test-lib.sh`.

## Risks
Regex expectations are coupled to dump textual format and fixture metadata.

## Test Signals
Validates filter semantics in tooling and correct preservation/classification of chardev, inline content, whiteout, and xattr metadata.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/tests/test-dump-filtered.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/tests/test-lcfs.c -->
# sources/cloud-native/composefs/tests/test-lcfs.c

## Purpose
`test-lcfs.c` is the C unit/regression test for public libcomposefs APIs and a handcrafted image-load security regression.

## Important APIs, Types, And Functions
Helpers are `cleanup_node`, `write_cb`, and `testwrite_node`. Test cases are `test_basic`, `test_xattr_addremove`, `test_xattr_doubleadd`, `test_add_uninitialized_child`, `test_hardlinked_whiteout_load`, and `test_no_verity`.

## Control Flow
Tests create nodes, set modes/xattrs, add children, write to an in-memory stream, assert success or expected failure, construct a minimal EROFS image in memory for a hardlinked whiteout, and call fsverity measure on a temp fd.

## State And Persistence
Uses in-memory image buffers and a temporary file for fsverity absence testing. Node refs are managed by cleanup attributes.

## Dependencies And Integration Points
Includes public headers plus EROFS wrapper details for the handcrafted image. Links against `libcomposefs`.

## Risks
Assertions abort on failure, so the executable is suitable for test harnesses but not diagnostic-rich. The hardcoded image layout must track EROFS struct definitions.

## Test Signals
Directly covers child ownership, write validation, xattr unset/set/overwrite semantics, kernel fsverity error canonicalization, and rejection of invalid hardlinked whiteouts that previously risked use-after-free.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/tests/test-lcfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/tests/test-lib.sh -->
# sources/cloud-native/composefs/tests/test-lib.sh

## Purpose
`test-lib.sh` provides common shell helpers and host capability probes for composefs tests.

## Important APIs, Types, And Functions
Helpers include `fatal`, `_fatal_print_file`, `assert_file_has_content`, `check_whiteout`, `check_fuse`, `check_erofs_fsck`, `check_fsverity`, and `assert_streq`. It initializes `can_whiteout`, `has_fuse`, `has_fsck`, and `has_fsverity`.

## Control Flow
On source, it defines helpers, runs probes unless variables already exist, and prints detected test options. Probes check `mknod`, FUSE tooling/capabilities, `fsck.erofs`, and fsverity enablement.

## State And Persistence
Creates temporary files for probes and deletes them. Exports shell variables in the caller context.

## Dependencies And Integration Points
Sourced by most shell tests. Depends on common Unix tools, `capsh`, `fusermount`, `/dev/fuse`, and `fsverity` when available.

## Risks
Capability detection is host-sensitive and can skip meaningful coverage. Probe output can affect test logs.

## Test Signals
It gates optional paths so tests can distinguish unsupported host features from composefs failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/tests/test-lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/tests/test-random-fuse.sh -->
# sources/cloud-native/composefs/tests/test-random-fuse.sh

## Purpose
This shell test generates random filesystem trees, builds composefs images, verifies dump reproducibility, and when possible checks FUSE-mounted views against source dumps.

## Important APIs, Types, And Functions
Main function `test_random` uses `gendir`, `dumpdir`, `mkcomposefs`, optional `fsck.erofs`, `composefs-dump`, `composefs-info dump`, `composefs-fuse`, and diff/cmp checks.

## Control Flow
It creates a temp workdir, sources `test-lib.sh`, configures generator flags based on whiteout support and optional `seed`, then runs once with a seed or ten times without. Each iteration generates a root, dumps it, builds an image/object store, checks reproducibility, optionally mounts through FUSE twice, and compares dumps.

## State And Persistence
All state is under a temporary workdir removed on exit. It creates and unmounts FUSE mounts.

## Dependencies And Integration Points
Depends on built tools, Python helpers, optional FUSE capability, optional fsck, and valgrind prefix support.

## Risks
Random coverage can be flaky if host filesystem semantics vary. FUSE paths depend on privileges and `/dev/fuse`. Generated seeds should be retained from logs for reproduction.

## Test Signals
Broad stress coverage for tree ingestion, inline/object split, xattrs, whiteouts, symlinks, special files, image dump/load, and FUSE behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/tests/test-random-fuse.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/tests/test-should-fail.sh -->
# sources/cloud-native/composefs/tests/test-should-fail.sh

## Purpose
This shell test verifies malformed dump fixtures are rejected by `mkcomposefs --from-file`.

## Important APIs, Types, And Functions
It sources `test-lib.sh`, loops over fixture paths, runs `mkcomposefs --from-file`, captures stderr, and asserts exit code `1`.

## Control Flow
For each fixture, successful image creation is a failure, non-1 failure exit is also a failure, and exit code 1 prints `ok`.

## State And Persistence
Uses one temporary directory removed by trap.

## Dependencies And Integration Points
Driven by `tests/meson.build` fixture list. Depends on built `mkcomposefs`.

## Risks
Only validates CLI exit code, not exact error messages. If CLI exit conventions change, this test needs updating.

## Test Signals
Important negative coverage for long links, invalid xattrs, oversized files, missing file types, empty or dot names, bad hardlinks, and oversized inline content.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/tests/test-should-fail.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/tests/test-units.sh -->
# sources/cloud-native/composefs/tests/test-units.sh

## Purpose
`test-units.sh` is a shell unit suite for common tool/library behaviors: inline-vs-object storage, mount digest validation, and file measurement digest output.

## Important APIs, Types, And Functions
Functions are `makeimage`, `countobjects`, `test_inline`, `test_objects`, `test_mount_digest`, `test_composefs_info_measure_files`, and `test_composefs_info_help` (defined but not included in `TESTS`). It loops over `TESTS` and reports per-test status.

## Control Flow
The script creates a temp workdir, sources capability helpers, then for each named test creates root/objects/mnt dirs. Inline test expects no objects for a small file; object test expects one digest-store object for a 1024-byte file; mount digest test checks no-verity and wrong-verity failures then valid digest progress; measure-file test asserts known fs-verity-compatible digests.

## State And Persistence
Uses temporary directories under `/var/tmp` by default to improve fsverity support, and removes the workdir on exit. It may enable fsverity on temp files/images.

## Dependencies And Integration Points
Depends on built tools, `fsverity` when available, `mount.composefs`, and helpers from `test-lib.sh`.

## Risks
Mount assertions allow permission/sandbox errors after digest validation, so it proves pre-mount digest gating more than full mount success. `test_composefs_info_help` references `composefs_info` with an underscore and is not run.

## Test Signals
High-value targeted coverage for inline threshold behavior, digest store object creation, fsverity measurement compatibility, and mount digest error mapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/tests/test-units.sh -->
