# Research: subset-b-000240

Grouped research for the OSTree Rust bindings files listed in `subset-b-000240`. Each section is bounded with reconciliation markers and preserves the original source path in its title.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/repo.rs -->
## sources/cloud-native/ostree/rust-bindings/src/auto/repo.rs

Generated GIR binding for `OstreeRepo`, exposed as the crate's main repository object. It wraps the C `OstreeRepo` GObject with constructors such as `new`, `new_default`, `for_sysroot_path`, `create_at`, `open_at`, and `mode_from_string`, then maps a broad libostree repository surface into Rust methods returning `Result<_, glib::Error>` where the C API reports `GError`.

Important APIs cover repository lifecycle (`create`, `open`, `reload_config`, `write_config_and_reload`), transaction flow (`prepare_transaction`, `commit_transaction`, `abort_transaction`, `transaction_set_ref*`, `transaction_set_collection_ref`), checkout and object IO (`checkout_at`, `checkout_tree`, `read_commit`, `load_variant`, `load_object_stream`, `write_commit`, `write_content_trusted`, `write_metadata_trusted`, `write_mtree`), remotes (`remote_add`, `remote_change`, `remote_fetch_summary`, `remote_gpg_import`, `remote_list`, option accessors), pulls (`pull`, `pull_one_dir`, `pull_with_options`), signatures/GPG (`sign_commit`, `sign_delta`, `verify_commit*`, `verify_summary`, `signature_verify_commit_data`), static deltas, pruning, and state accessors such as `path`, `mode`, `parent`, `dfd`, `collection_id`, and `min_free_space_bytes`.

Control flow is almost entirely FFI marshaling: inputs are converted with `ToGlibPtr`, output pointers are initialized, C functions are called, and null `GError` means success. State and persistence live in the libostree repo on disk; this wrapper only observes or triggers mutations. Feature gates track libostree version availability. Integration points include `gio::File`, `gio::InputStream`, `glib::Variant`, `AsyncProgress`, `RepoFile`, `RepoCommitModifier`, `CollectionRef`, `Sign`, and `Sysroot`.

Risks are typical generated-binding risks: several GIR-unhandled hash table/archive/traversal methods remain commented, successful C calls are trusted to initialize outputs, and methods that mutate remotes, refs, commits, signatures, or config directly affect repository persistence. Test signals are mostly indirect through handwritten `repo.rs` and crate tests; this generated file has no local tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/repo.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/repo_commit_modifier.rs -->
## sources/cloud-native/ostree/rust-bindings/src/auto/repo_commit_modifier.rs

Generated shared-wrapper binding for `OstreeRepoCommitModifier`, used when writing directory trees or archives into a repo. The primary constructor `RepoCommitModifier::new` accepts `RepoCommitModifierFlags` and an optional Rust closure that maps `(Repo, path, FileInfo)` to `RepoCommitFilterResult`.

The file also exposes `set_devino_cache`, `set_sepolicy`, `set_sepolicy_from_commit`, and `set_xattr_callback`. These APIs connect commit creation to hardlink/device-inode caching, SELinux relabeling, and xattr synthesis. Control flow boxes Rust callbacks, passes them as `user_data`, and installs destroy notifiers so libostree can release the closures. State is held in the underlying shared C object; the Rust value is ref-counted via generated `ref`/`unref` hooks.

Dependencies are `Repo`, `RepoDevInoCache`, `SePolicy`, `gio::FileInfo`, and GLib translation traits. Risks center on callback lifetime and FFI unwinding: the generated commit-filter trampoline does not catch panics, so panics crossing into C would be unsafe. Feature gates limit newer cache and SELinux-from-commit helpers. Test coverage is indirect through commit/write paths; no local tests exist.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/repo_commit_modifier.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/repo_dev_ino_cache.rs -->
## sources/cloud-native/ostree/rust-bindings/src/auto/repo_dev_ino_cache.rs

Tiny generated shared-wrapper binding for `OstreeRepoDevInoCache`. It exposes `RepoDevInoCache::new` and implements `Default`, delegating allocation and lifetime to `ostree_repo_devino_cache_new`, `ref`, and `unref`.

The cache is an integration helper for commit modifiers and checkout options, mapping device/inode pairs to checksums so libostree can detect already-known file content. There is no local control flow beyond creation and GLib pointer conversion. All state lives in the C shared object and is consumed by APIs such as `RepoCommitModifier::set_devino_cache` or `RepoCheckoutAtOptions`.

The main dependency is `ffi`; no filesystem persistence happens in this file directly. Risk is low but version-sensitive because consumers are feature-gated in other modules. There are no local tests; behavior is verified only when higher-level commit/checkout paths use the cache.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/repo_dev_ino_cache.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/repo_file.rs -->
## sources/cloud-native/ostree/rust-bindings/src/auto/repo_file.rs

Generated GObject binding for `OstreeRepoFile`, implementing `gio::File` for files rooted in OSTree repository trees. The wrapper exposes tree and metadata helpers such as `ensure_resolved`, `checksum`, `repo`, `root`, `xattrs`, `tree_find_child`, `tree_get_contents`, `tree_get_contents_checksum`, `tree_get_metadata`, `tree_get_metadata_checksum`, `tree_query_child`, and `tree_set_metadata`.

Control flow is direct FFI marshaling. Query methods return `glib::Variant`, `glib::GString`, `gio::FileInfo`, or `RepoFile`; mutating `tree_set_metadata` updates the in-memory repo-file tree node metadata reference. Persistence is indirect: `RepoFile` instances represent OSTree object trees and are later consumed by repo write/checkout operations.

Integration points include `Repo`, `gio::File`, `gio::Cancellable`, file-info attributes, and variant-encoded dirtree/dirmeta objects. Risks are around tree resolution and variant shape: callers must call the right tree APIs for the object type and handle optional checksums or metadata. There are no local tests, but `Repo::read_commit`, checkout, and write helpers depend on this wrapper.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/repo_file.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/repo_finder.rs -->
## sources/cloud-native/ostree/rust-bindings/src/auto/repo_finder.rs

Generated interface wrapper for `OstreeRepoFinder`. It provides the marker object/interface and an empty `RepoFinderExt` trait implemented for all `IsA<RepoFinder>` types. The imported `RepoFinderResult` signals the intended integration surface, while concrete behavior is supplied by specific finder implementations.

There is no local persistence or algorithmic control flow here. State and discovery mechanics live in implementations such as config, mount, override, or Avahi finders and in libostree itself. Dependencies are GLib object/interface glue and the crate-level `ffi` module.

The risk is mostly API-completeness: as generated, this file does not expose active finder methods, so users rely on concrete finder constructors and repo APIs. There are no local tests; behavior is covered only by consumers of concrete finder wrappers.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/repo_finder.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/repo_finder_avahi.rs -->
## sources/cloud-native/ostree/rust-bindings/src/auto/repo_finder_avahi.rs

Generated object wrapper for `OstreeRepoFinderAvahi`, a concrete `RepoFinder` implementation for network discovery via Avahi. It exposes `RepoFinderAvahi::new` and implements the `RepoFinder` interface.

Control flow is constructor-only: Rust calls `ostree_repo_finder_avahi_new` and wraps the full pointer. Runtime discovery state, network interaction, and result production are delegated to libostree and Avahi. This file does not persist state itself; it creates an object intended to be passed into repo-finder orchestration elsewhere.

Dependencies are `ffi`, GLib translation traits, and `RepoFinder`. Risks are environmental rather than local: Avahi availability, network visibility, and feature support determine usefulness. There are no local tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/repo_finder_avahi.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/repo_finder_config.rs -->
## sources/cloud-native/ostree/rust-bindings/src/auto/repo_finder_config.rs

Generated object wrapper for `OstreeRepoFinderConfig`, a concrete `RepoFinder` that discovers remotes from repository/system configuration. It exposes `new` and `Default`.

There is no custom control flow beyond object construction. The persistent behavior is external: the finder reads libostree configuration when used, but this Rust file neither reads nor writes the config directly. Integration is through the `RepoFinder` interface and repository remote configuration APIs.

Dependencies are minimal (`ffi`, `RepoFinder`, GLib translation). The main risk is silent dependence on repository/system config contents and libostree version behavior. Local test coverage is absent.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/repo_finder_config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/repo_finder_mount.rs -->
## sources/cloud-native/ostree/rust-bindings/src/auto/repo_finder_mount.rs

Generated object wrapper for `OstreeRepoFinderMount`, a concrete `RepoFinder` implementation for locating OSTree repositories on mounted media. It exposes `new(mount_root: Option<&gio::File>)`.

Control flow only converts the optional `gio::File` mount root and calls `ostree_repo_finder_mount_new`. Discovery, mount traversal, and result creation live in libostree. State is object configuration plus external mounted filesystems; this file does not persist anything.

Dependencies include `gio::File`, `RepoFinder`, and GLib translation traits. Risks are environmental: mount visibility, permissions, removable media layout, and object lifetime. No local tests are present.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/repo_finder_mount.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/repo_finder_override.rs -->
## sources/cloud-native/ostree/rust-bindings/src/auto/repo_finder_override.rs

Generated object wrapper for `OstreeRepoFinderOverride`, a concrete `RepoFinder` intended to use caller-specified overrides. It provides `new`, `Default`, and property accessors for `substitutions`.

The control flow is basic GObject construction and property get/set through `ObjectExt`. State is held on the GObject property and then consumed by libostree finder logic. This file does not write disk state; it configures runtime discovery behavior.

Dependencies are `RepoFinder`, GLib object property APIs, and `ffi`. Risks include variant/property shape correctness and callers assuming substitutions are validated locally; validation is deferred to libostree. There are no local tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/repo_finder_override.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/repo_finder_result.rs -->
## sources/cloud-native/ostree/rust-bindings/src/auto/repo_finder_result.rs

Generated boxed/shared wrapper for `OstreeRepoFinderResult`. It exposes comparison ordering by delegating `PartialEq`, `PartialOrd`, and `Ord` to `ostree_repo_finder_result_compare`.

The type represents finder output produced by libostree discovery mechanisms. This Rust file mainly manages ownership and ordering semantics; it has no constructors or direct persistence. State is the underlying C result object and any associated remote metadata carried by libostree.

Dependencies are `ffi` and GLib translation. Risks are around opaque semantics: Rust ordering reflects C comparison behavior, so consumers should not infer more than libostree guarantees. No local tests exist.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/repo_finder_result.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/se_policy.rs -->
## sources/cloud-native/ostree/rust-bindings/src/auto/se_policy.rs

Generated GObject binding for `OstreeSePolicy`, exposing SELinux policy lookup and relabeling helpers. Constructors include `new`, `new_at`, and `from_commit`; accessors include `csum`, `label`, `name`, `path`, and `rootfs_dfd`; mutating helpers include `restorecon`, `setfscreatecon`, and the version-gated global `set_null_log`.

Control flow follows the generated GError pattern and converts `gio::File`, modes, labels, and variants through GLib. Persistence is external: policy is loaded from a root filesystem or commit, while `restorecon` and `setfscreatecon` influence filesystem labels or process filesystem-creation context through libostree/SELinux APIs.

Integration points are `Repo`, `gio::FileInfo`, `gio::File`, `SePolicyRestoreconFlags`, and commit/write paths that install policies on `RepoCommitModifier`. Risks include rootfs file-descriptor validity, SELinux availability, global process context side effects, and platform/version gating. Test signals are indirect; handwritten `se_policy.rs` adds cleanup but this generated file has no tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/se_policy.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/sign.rs -->
## sources/cloud-native/ostree/rust-bindings/src/auto/sign.rs

Generated interface binding for `OstreeSign`. Static helpers expose `Sign::NONE`, `all`, and `by_name`; the `SignExt` trait provides operations for public-key management, commit signing and verification, arbitrary data signing and verification, metadata format lookup, name lookup, and newer blob-reader/data APIs behind feature gates.

Control flow is pure interface dispatch into libostree with GError conversion. State is held by concrete sign implementations and their configured keys; persistence may occur inside the implementation or through repo commit metadata, but this wrapper only calls the interface. Integration points include `Repo`, `glib::Bytes`, `glib::Variant`, `BlobReader`, and static delta/signature APIs in `Repo`.

Risks are security-sensitive: key loading, signature validation semantics, and optional success messages are delegated to backends; users must choose the correct backend and trust model. Feature gates matter because signature APIs evolved over libostree releases. No local tests are present.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/sign.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/sysroot.rs -->
## sources/cloud-native/ostree/rust-bindings/src/auto/sysroot.rs

Generated GObject binding for `OstreeSysroot`, the object managing bootable OSTree deployment state under a sysroot. Constructors include `new` and `new_default`. APIs cover initialization/loading (`ensure_initialized`, `initialize`, `initialize_with_mount_namespace`, `load`, `load_if_changed`, `unload`), locking (`lock`, `try_lock`, `unlock`, `lock_async`, `lock_future`), cleanup, repository access, deployment creation/staging/writing, kernel argument mutation, mutable/unlocked/pinned states, boot metadata, origin files, soft reboot and kexec features, and a `journal-msg` signal.

Control flow mirrors libostree sysroot operations and uses GLib main-context checks for async locking. State and persistence are central: methods read and mutate deployment directories, bootloader configuration, origin files, staged/pending/rollback deployment records, and cleanup state. This wrapper converts `Deployment`, `Repo`, `SysrootDeployTreeOpts`, `SysrootWriteDeploymentsOpts`, `glib::KeyFile`, and string arrays.

Risks are high because operations change bootable system state; callers must lock where required, respect cancellables, and handle feature-gated behavior. Some GIR-unhandled prune options remain commented. Tests are indirect through `sysroot.rs` builder tests and option-struct tests rather than this generated file itself.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/sysroot.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/sysroot_upgrader.rs -->
## sources/cloud-native/ostree/rust-bindings/src/auto/sysroot_upgrader.rs

Generated binding for `OstreeSysrootUpgrader`, a helper object that pulls and deploys upgrades for a sysroot. Constructors include `new`, `new_for_os`, and version-gated `new_for_os_with_flags`; methods expose `check_timestamps`, `deploy`, `dup_origin`, `pull`, `pull_one_dir`, `pull_only`, `repo`, and `sysroot`.

Control flow delegates upgrade sequencing to libostree, with Rust handling GLib pointer conversion and GError results. State is held in the sysroot, repo, origin config, and upgrade object; persistent effects include pulling commits and writing new deployments when deploy methods run.

Dependencies include `Sysroot`, `Repo`, `AsyncProgress`, `RepoPullFlags`, `SysrootUpgraderFlags`, and pull flags. Risks include network/pull failure, origin mismatch, deployment side effects, and cancellation handling. Local tests are absent.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/sysroot_upgrader.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/checksum.rs -->
## sources/cloud-native/ostree/rust-bindings/src/checksum.rs

Handwritten safe wrapper around a binary SHA-256 OSTree checksum. `Checksum` owns a `g_malloc`/`g_free`-compatible 32-byte buffer and offers `from_bytes`, `from_hex`, `from_base64`, `to_hex`, `to_base64`, `Display`, `Clone`, equality via `ostree_cmp_checksum_bytes`, and GLib pointer conversion implementations. `ChecksumError` distinguishes invalid hex and invalid OSTree-modified-base64 input.

Control flow allocates zeroed GLib memory, decodes or copies exactly `OSTREE_SHA256_DIGEST_LEN` bytes, and frees on `Drop`. The base64 engine uses OSTree's modified alphabet with `_` instead of `/` and no required padding. State is only the owned checksum bytes; persistence occurs when repo write functions return or consume checksums.

Dependencies are `base64`, `hex`, `once_cell`, GLib allocation APIs, and `ffi`. Risks include raw pointer ownership contracts in `FromGlibPtrFull`, null-pointer assumptions in private constructors, and exact length validation. Tests cover owned pointer adoption, hex/base64 round trips, invalid lengths/input, equality, display, and clone behavior, giving strong coverage for this low-level type.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/checksum.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/collection_ref.rs -->
## sources/cloud-native/ostree/rust-bindings/src/collection_ref.rs

Handwritten accessors for generated `CollectionRef` internals. `collection_id` returns `Option<&CStr>` because the underlying pointer can be null and bytes may not be valid UTF-8; `ref_name` returns `&CStr` for the required ref field.

Control flow obtains the raw `OstreeCollectionRef` pointer via `ToGlibPtr`, checks null collection IDs with a small `AsNonnullPtr` helper, and borrows C strings without copying. There is no persistence; this is read-only access to a boxed/ref-counted libostree struct used by collection-ref resolution and remote discovery.

Dependencies are the generated `CollectionRef`, `ffi`, GLib translation, and `CStr`. Risks include borrowed lifetime correctness and caller conversion from `CStr` to UTF-8. Local unit tests cover present/absent collection IDs and ref-name retrieval.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/collection_ref.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/commit_sizes_entry.rs -->
## sources/cloud-native/ostree/rust-bindings/src/commit_sizes_entry.rs

Handwritten convenience accessors for generated `CommitSizesEntry`. It exposes `checksum`, `objtype`, `unpacked`, and `archived`, reading fields directly from `OstreeCommitSizesEntry`.

Control flow borrows the raw struct pointer with `ToGlibPtr`, then converts the checksum C string and object-type enum while returning numeric size fields. There is no persistence; the type represents size metadata usually produced by libostree commit-size calculations.

Dependencies are `auto::CommitSizesEntry`, `auto::ObjectType`, `ffi`, and GLib conversion traits. Risks are low but tied to C layout compatibility. Tests instantiate an entry and verify all accessor values.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/commit_sizes_entry.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/constants.rs -->
## sources/cloud-native/ostree/rust-bindings/src/constants.rs

Small handwritten constants module. It exports `COMMIT_META_CONTAINER_CMD`, the OSTree commit metadata key `"ostree.container-cmd"`.

There is no control flow or state. The constant integrates callers with commit metadata dictionaries used when storing container command metadata in OSTree commits. The only dependency is downstream code that imports it from `lib.rs`.

Risks are limited to string-key drift if libostree changes conventions; no tests are present because the file is a fixed constant.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/constants.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/core.rs -->
## sources/cloud-native/ostree/rust-bindings/src/core.rs

Handwritten type aliases and parsing helpers for OSTree core variant formats. It defines `CommitVariantType`, `TreeVariantType`, `DirmetaVariantType`, and `DirMetaParsed`.

The important function is `DirMetaParsed::from_variant`, which tries to decode a GLib variant as `(uuua(ayay))`, then converts UID, GID, and mode from big-endian to host order while retaining xattrs. State is purely decoded data; persistence remains in libostree object variants stored in the repository.

Dependencies are `glib::Variant` and `VariantDict`. Integration points include `Repo::read_dirmeta`, metadata object loading, and callers that parse commit/tree variants. Risks are variant-shape mismatches and endianness mistakes; the explicit `try_get` result helps surface wrong types. There are no local tests in this file, but `Repo::read_dirmeta` relies on it.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/core.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/deployment.rs -->
## sources/cloud-native/ostree/rust-bindings/src/deployment.rs

Tiny handwritten extension for generated `Deployment`. It adds `stateroot`, currently an alias for `osname`, to expose OSTree deployment stateroot naming in Rust terms.

There is no control flow beyond forwarding, no persistence, and no independent state. Integration is with sysroot deployment APIs that return or accept `Deployment` objects.

Risk is semantic drift: if libostree's deployment terminology diverges from `osname`, this alias would need revisiting. No local tests are present.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/deployment.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/functions.rs -->
## sources/cloud-native/ostree/rust-bindings/src/functions.rs

Handwritten top-level checksum helpers wrapping libostree file checksum APIs. It exposes synchronous `checksum_file`, async callback `checksum_file_async`, future adapter `checksum_file_async_future`, stream-based `checksum_file_from_input`, and directory-fd relative `checksum_file_at`.

Control flow allocates output checksum pointers, calls the corresponding C function, and funnels return/error/output handling through a helper that returns either a `Checksum` or boxed error. Async paths box `FnOnce` callbacks, finish with `ostree_checksum_file_async_finish`, and provide a `gio::GioFuture` facade. State is transient; no persistence is written, though file contents are read from `gio::File`, `InputStream`, or `dfd/path`.

Dependencies include `Checksum`, `ObjectType`, `ChecksumFlags`, `gio`, `glib`, and FFI functions. Risks include correctly handling the C convention where checksum may be null, ensuring callbacks are consumed once, and main-context/cancellable behavior. Tests are mostly indirect through checksum and repo IO paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/functions.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/kernel_args.rs -->
## sources/cloud-native/ostree/rust-bindings/src/kernel_args.rs

Handwritten boxed binding for `OstreeKernelArgs`, gated on newer libostree features. It supports creating/parsing kernel argument sets, appending individual or array args, filtering by prefixes, appending `/proc/cmdline`, deleting args or key entries, replacing args, querying the last value for a key, converting to string or string vector, and `Default`, `Display`, and `From<T: AsRef<str>>`.

Control flow delegates mutation to libostree's boxed type. The wrapper marks copy as unimplemented and uses libostree free, so callers should treat it as an owned mutable boxed object rather than a trivially cloneable Rust collection. State is in the boxed kernel-argument object and later feeds sysroot deploy/stage APIs; persistence happens only when deployments are written.

Dependencies are GLib boxed translation, `gio::Cancellable`, `GString`, and `ffi`. Risks include feature gating, unimplemented copy behavior, command-line parsing semantics delegated to libostree, and mutation through shared boxed references. Dedicated tests cover creation/fill, string-vector conversion, last-value lookup, parsing from string, append/filter/replace array behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/kernel_args.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/lib.rs -->
## sources/cloud-native/ostree/rust-bindings/src/lib.rs

Crate root for the safe Rust `ostree` bindings. It documents libostree's purpose, enables docs cfg when requested, denies unused must-use values, warns on missing docs and broken links, re-exports `ffi`, `gio`, `glib`, and `libc::AT_FDCWD`, includes generated GIR bindings under `auto`, and layers handwritten modules on top.

Important integration behavior is the public export surface: generated functions/types are re-exported first, then handwritten extensions such as `Checksum`, core variant aliases, `SysrootBuilder`, repo helpers, checkout options, transaction stats, SELinux cleanup, and option structs. Feature gates mirror libostree version gates so downstream code can compile against selected API levels. The `prelude` re-exports generated traits plus `gio`/`glib` preludes.

State and persistence are not implemented here, but this file controls which APIs callers see and how generated and handwritten modules compose. Risks are export conflicts, feature-gate mismatches, and public API stability. Test integration is through `#[cfg(test)] mod tests`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/mutable_tree.rs -->
## sources/cloud-native/ostree/rust-bindings/src/mutable_tree.rs

Handwritten extensions for generated `MutableTree`. It exposes `copy_files` and `copy_subdirs`, intentionally copying libostree's internal hash tables into Rust `HashMap`s instead of exposing mutable borrowed table access.

Control flow obtains C hash tables via `ostree_mutable_tree_get_files` or `_get_subdirs`. `copy_files` uses GLib container conversion, while `copy_subdirs` manually iterates with `g_hash_table_foreach` and converts keys to `String` and values to `MutableTree`. State is a snapshot copy of the mutable-tree contents; repository persistence happens later when a mutable tree is written by repo APIs.

Dependencies include `glib`, `ffi`, and `HashMap`. Risks are conversion correctness and the fact that returned maps are copies, not live views. This design reduces use-after-free risk compared with exposing the original C tables. No local tests are present.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/mutable_tree.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/object_details.rs -->
## sources/cloud-native/ostree/rust-bindings/src/object_details.rs

Handwritten representation for metadata returned by repo object-listing APIs. `ObjectDetails` stores whether an object is loose and the pack/checksum list where it appears, with constructors/parsers from GLib variants and a `Display` implementation.

Control flow decodes a variant emitted by libostree's object listing into Rust fields. State is read-only metadata; persistence is the underlying repository object store. Integration is with `repo.rs` `list_objects`, which returns `HashMap<ObjectName, ObjectDetails>`.

Dependencies are GLib variant extraction and formatting traits. Risks include variant-shape mismatch and lossy interpretation if libostree changes object-list detail layout. Tests are not local in this file; behavior is exercised by repo object listing consumers.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/object_details.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/object_name.rs -->
## sources/cloud-native/ostree/rust-bindings/src/object_name.rs

Handwritten object-name wrapper around an OSTree checksum plus `ObjectType`. It provides constructors from checksum/type or from serialized variants, serialization/deserialization helpers through crate functions, `Display` via `object_to_string`, and custom `Hash`/`PartialEq` using libostree's variant hash/equality.

Control flow stores checksum as `GString` and object type as an enum, while conversions to/from `glib::Variant` preserve libostree's canonical object-name representation. State is value-level only; persistence occurs when object names index repo contents or traversal results.

Dependencies include `ObjectType`, generated object serialization functions, `glib::Variant`, and Rust hashing/display traits. Risks are canonicalization and hash/equality alignment with C semantics. Local tests cover equality, display/serialization, and hash behavior for object names.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/object_name.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/repo.rs -->
## sources/cloud-native/ostree/rust-bindings/src/repo.rs

Handwritten extensions for `Repo`, filling gaps that GIR could not convert ergonomically. It adds path/dirfd constructors, RAII transactions, hash-table conversions for refs/objects/traversals, required revision resolution, file metadata/content helpers, trusted and untrusted content/metadata writes returning `Checksum`, async write wrappers and futures, dirmeta parsing, and commit-object prefix listing.

Important types/functions include `TransactionGuard`, `auto_transaction`, `dfd_as_file`, `dfd_borrow`, `traverse_commit`, `list_refs`, `list_objects`, `list_refs_ext`, `require_rev`, `load_file`, `query_file`, `write_content`, `write_metadata`, `write_content_async_future`, `write_metadata_async_future`, `read_dirmeta`, and `list_commit_objects_starting_with`. Control flow frequently calls C APIs that return `GHashTable`s, then iterates or converts them into Rust `HashSet`/`HashMap` and unrefs where appropriate. `TransactionGuard::drop` aborts uncommitted transactions, while `commit` consumes the guard and disables the abort.

State and persistence are central: these helpers read and write repository object storage, refs, metadata, and transactions. Dependencies include `Checksum`, `ObjectName`, `ObjectDetails`, `RepoTransactionStats`, `gio`, `glib`, raw fd traits, futures, and libostree FFI. Risks include unsafe hash-table conversion, assuming output initialization on success, abort errors being ignored in `Drop`, async callback ownership, and persistent side effects of write/list operations. Test signals are indirect plus dedicated repo mode tests in `tests/repo.rs`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/repo.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/repo_checkout_at_options/mod.rs -->
## sources/cloud-native/ostree/rust-bindings/src/repo_checkout_at_options/mod.rs

Handwritten Rust representation for `OstreeRepoCheckoutAtOptions`. The struct exposes checkout mode, overwrite mode, fsync and whiteout controls, hardlink/copy behavior, optional subpath, devino cache, SELinux policy, and a feature-gated checkout filter.

Control flow is in `Default` and `ToGlibPtr`: it builds a zeroed C `OstreeRepoCheckoutAtOptions` in boxed storage, converts optional path/string/callback fields, assigns flags, and returns a stable pointer stash for the duration of the FFI call. State is per-call checkout configuration; filesystem persistence happens in `Repo::checkout_at`.

Dependencies include `RepoCheckoutMode`, `RepoCheckoutOverwriteMode`, `RepoDevInoCache`, `SePolicy`, `RepoCheckoutFilter`, `libc::c_char`, and GLib conversion traits. Risks include keeping all nested storage alive, C struct layout/version compatibility, and feature-gated fields matching the linked libostree. Tests validate default and non-default C conversion, including pointer/string fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/repo_checkout_at_options/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/repo_checkout_at_options/repo_checkout_filter.rs -->
## sources/cloud-native/ostree/rust-bindings/src/repo_checkout_at_options/repo_checkout_filter.rs

Handwritten callback wrapper for checkout filtering. `RepoCheckoutFilter` stores a boxed closure `Fn(&Repo, &Path, &libc::stat) -> RepoCheckoutFilterResult`; `new` returns it pre-wrapped in `Some` for convenient option assignment.

Control flow converts the wrapper to a raw `gpointer` for libostree and defines a trampoline that borrows the repo, converts the path to `PathBuf`, borrows `libc::stat`, calls the closure, and converts the result enum. `filter_trampoline_unwindsafe` catches panics, prints a short diagnostic directly to stderr, and aborts to avoid unwinding through C. State is the closure pointer owned by checkout options for the FFI call.

Dependencies are `Repo`, `RepoCheckoutFilterResult`, GLib translation, `libc::stat`, `Path`, and panic handling. Risks include raw pointer validity and process abort on callback panic, which is deliberate for FFI safety. Tests cover null-pointer panics and successful closure invocation/result conversion.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/repo_checkout_at_options/repo_checkout_filter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/repo_transaction_stats.rs -->
## sources/cloud-native/ostree/rust-bindings/src/repo_transaction_stats.rs

Handwritten/newtype support around generated `RepoTransactionStats`. It provides `uninitialized` construction for passing an output stats struct to `ostree_repo_commit_transaction`, plus field accessors for transaction counters such as metadata/content objects written and bytes written.

Control flow is low-level GLib struct ownership: the value is prepared as an output target, then populated by libostree and returned from `Repo::commit_transaction` or `TransactionGuard::commit`. State is summary data for a completed repo transaction; persistence has already happened in the repository.

Dependencies are GLib pointer conversion traits and `ffi`. Risks are uninitialized-memory correctness and keeping the Rust accessor layout aligned with C. There are no dedicated tests, but transaction paths rely on this type.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/repo_transaction_stats.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/se_policy.rs -->
## sources/cloud-native/ostree/rust-bindings/src/se_policy.rs

Handwritten extension for `SePolicy`. It exposes `fscreatecon_cleanup`, a safe-looking wrapper around `ostree_sepolicy_fscreatecon_cleanup(NULL)` to reset SELinux filesystem creation context.

Control flow is a single unsafe FFI call with a null cleanup location. State affected is process/global SELinux creation context rather than Rust-owned data. This integrates with generated `SePolicy::setfscreatecon` and commit/checkout code that may set file labels.

Risk is global side effect: callers need to use it after setting fscreatecon so subsequent file creation is not mislabeled. There are no local tests, likely because behavior depends on SELinux runtime state.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/se_policy.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/sysroot.rs -->
## sources/cloud-native/ostree/rust-bindings/src/sysroot.rs

Handwritten builder and file-descriptor helpers for `Sysroot`. `SysrootBuilder` can be configured with `path`, `mount_namespace`, and `flags`, then opened through `open` using newer libostree APIs. `Sysroot` also gets helpers such as `new_for_path`, `fd_as_file`, and `fd_borrow`.

Control flow constructs `gio::File` paths, calls the generated or FFI sysroot open/initialize path, and duplicates or borrows the sysroot directory fd safely enough for Rust callers. State and persistence are the sysroot's on-disk deployment repository and boot state; builder flags influence how libostree opens it.

Dependencies include `gio`, `Sysroot`, `BorrowedFd`, and `PathBuf`. Risks are raw fd ownership boundaries, feature availability, and opening/mount-namespace semantics that affect host system state. Local tests focus on builder defaults and path configuration rather than full sysroot mutation.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/sysroot.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/sysroot_deploy_tree_opts.rs -->
## sources/cloud-native/ostree/rust-bindings/src/sysroot_deploy_tree_opts.rs

Handwritten options struct for `ostree_sysroot_deploy_tree_with_options` and staging equivalents. `SysrootDeployTreeOpts<'a>` contains `locked`, optional `override_kernel_argv`, and optional `overlay_initrds`.

Control flow in `ToGlibPtr` zeroes an `OstreeSysrootDeployTreeOpts`, converts optional string slices into null-terminated C arrays, stores the backing conversions in the stash, and returns a stable pointer. State is per-deploy configuration only; persistence happens when sysroot deploy/stage methods write deployments.

Dependencies are `ffi::OstreeSysrootDeployTreeOpts`, GLib translation traits, and C string pointers. Risks include keeping nested array storage alive, zeroed C struct compatibility, and lifetime correctness for borrowed string slices. Tests validate default zero/null conversion and non-default string-array/locked conversion.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/sysroot_deploy_tree_opts.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/sysroot_write_deployments_opts.rs -->
## sources/cloud-native/ostree/rust-bindings/src/sysroot_write_deployments_opts.rs

Handwritten options struct for `ostree_sysroot_write_deployments_with_options`. `SysrootWriteDeploymentsOpts` currently exposes `do_postclean`.

Control flow zeroes an `OstreeSysrootWriteDeploymentsOpts`, sets the GLib boolean, boxes it for pointer stability, and returns a `ToGlibPtr` stash. State is per-call configuration; persistent effects are in the generated sysroot deployment-writing method.

Dependencies are `ffi::OstreeSysrootWriteDeploymentsOpts` and GLib translation traits. Risks are low but include C layout/version compatibility and interpreting cleanup side effects. Tests verify default `GFALSE` and non-default `GTRUE` conversion.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/sysroot_write_deployments_opts.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/tests/collection_ref.rs -->
## sources/cloud-native/ostree/rust-bindings/src/tests/collection_ref.rs

Unit tests for `CollectionRef` equality, hashing, optional collection IDs, and cloning. The tests are gated on `v2018_6`, matching collection-ref API availability.

Control flow creates `CollectionRef` values with the same and different collection/ref components, hashes them with `DefaultHasher`, and asserts equality or inequality. There is no persistence or external IO. Dependencies are `CollectionRef`, `Hash`, and `Hasher`.

The test signals protect value semantics used by repo collection-ref resolution and remote discovery. They reduce risk that generated boxed equality/hash behavior changes silently, especially for absent collection IDs.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/tests/collection_ref.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/tests/kernel_args.rs -->
## sources/cloud-native/ostree/rust-bindings/src/tests/kernel_args.rs

Unit tests for `KernelArgs`. They cover creating and filling argument sets, converting to string vectors, retrieving last key values, parsing from strings, appending arrays, filtered append, and replacing arrays.

Control flow is entirely in-memory against the boxed libostree kernel-args type. There is no persistence; the tests validate the values that would later be passed into sysroot deployment APIs. Dependencies are the crate `KernelArgs` wrapper and libostree's parsing/replacement behavior.

These tests are important because `KernelArgs` is a handwritten mutable boxed wrapper with unimplemented copy semantics. They verify practical command-line manipulation and guard against regressions in feature-gated kernel-argument support.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/tests/kernel_args.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/tests/mod.rs -->
## sources/cloud-native/ostree/rust-bindings/src/tests/mod.rs

Test module aggregator for the Rust bindings crate. It includes `collection_ref`, `kernel_args`, and `repo`.

There is no runtime control flow beyond Rust test discovery. State and persistence are absent. The integration point is `lib.rs`, which includes this module under `#[cfg(test)]`.

The file's risk is organizational: tests omitted here will not run as part of the crate test module. It currently wires the subset of handwritten behavior covered by local unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/tests/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/tests/repo.rs -->
## sources/cloud-native/ostree/rust-bindings/src/tests/repo.rs

Unit tests for `Repo::mode_from_string`. They verify a valid mode string (`"bare"`) converts to `RepoMode::Bare` and an invalid string returns an error.

Control flow is direct invocation of the generated static wrapper; there is no repository creation or disk persistence. Dependencies are `Repo` and `RepoMode`.

The test signal is narrow but useful because repo mode parsing crosses the FFI error boundary and is used when creating/opening repositories. Broader repo transaction and object IO behavior is not covered by this test file.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/tests/repo.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/sys/Cargo.toml -->
## sources/cloud-native/ostree/rust-bindings/sys/Cargo.toml

Manifest for the low-level `ostree_sys` FFI crate. It declares build dependency `system-deps`, runtime dependencies on `libc`, `gio-sys`, `glib-sys`, and `gobject-sys`, dev dependencies `shell-words` and `tempfile`, package metadata, library name, and a long chain of libostree version features from `v2014_9` through `v2025_3` plus `dox`.

Control flow is Cargo feature resolution rather than code execution. Each newer feature generally depends on the previous feature, allowing consumers to opt into a minimum libostree API level and letting generated bindings conditionally compile symbols. Persistence is Cargo/build metadata only.

Integration points are `build.rs`, `system-deps`, docs.rs, and the safe wrapper crate's feature gates. Risks include feature-chain mistakes, version ordering issues (`v2025_1` depends on `v2024_7` after declaration), and mismatch between available system libostree and enabled Rust features. Tests are not in the manifest, but dev dependencies support build/test scripts.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/sys/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/sys/build.rs -->
## sources/cloud-native/ostree/rust-bindings/sys/build.rs

Build script for the `ostree_sys` crate. For docs.rs it defines an empty `main` to avoid linking system libraries during documentation builds. In normal builds it calls `system_deps::Config::new().probe()`, prints any probe error, and exits with status `1` on failure.

Control flow is intentionally minimal: docs builds skip probing/linking, while local/package builds require system dependency discovery to succeed. State is Cargo build-script output and linker metadata emitted by `system-deps`; no repository files are modified.

Dependencies are `system-deps` and `std::process`. Integration points are Cargo, pkg-config/system dependency metadata, and docs.rs. Risks include environment-sensitive failures when libostree development files are missing, and docs.rs hiding link problems by design. There are no local tests for the build script.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/sys/build.rs -->
