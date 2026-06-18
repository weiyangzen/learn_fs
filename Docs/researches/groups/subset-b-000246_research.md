# subset-b-000246 research

Grouped research report for the requested OSTree libostree repository finder, archive import/export, OS metadata, private repo state, prune, and pull verification files. Each section is keyed by original source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-finder-avahi.c -->
# sources/cloud-native/ostree/src/libostree/ostree-repo-finder-avahi.c

Purpose: implements the Avahi/DNS-SD `OstreeRepoFinder` backend, discovering OSTree repositories advertised on the local network and resolving requested `OstreeCollectionRef` values to dynamic HTTP remotes.

Important APIs/types/functions: exports `ostree_repo_finder_avahi_new`, `ostree_repo_finder_avahi_start`, and `ostree_repo_finder_avahi_stop`; implements the finder interface through `ostree_repo_finder_avahi_resolve_async/finish`. Internal types include `OstreeAvahiService`, `UriAndKeyring`, and `ResolveData`. Key helpers parse Avahi TXT records, evaluate Bloom filters, fetch and validate remote summaries, map refs to checksums, and build `OstreeRepoFinderResult` instances.

Control flow: construction stores a `GMainContext` and, when compiled with Avahi, initializes the Avahi GLib poll object and caches. `start` creates an Avahi client and service browser for `_ostree_repo._tcp`. Browser callbacks create resolvers; resolver callbacks cache successful services. Resolve requests are marshalled into the Avahi context, queued in `resolve_tasks`, and completed only once the browser is quiescent and all resolvers have finished. For each cached service, TXT attributes `v`, `rb`, `st`, and `ri` are validated; possible refs from the Bloom filter are grouped by URI/keyring; summaries are fetched to replace Bloom hits with actual checksums before returning results.

State and persistence: state is in memory only: pending tasks, Avahi handles, resolver map, found service cache, cancellable, and client/browser flags. It temporarily registers dynamic remotes in the parent repo while fetching summaries, then removes them if they were not already configured.

Dependencies/integration: depends on optional Avahi, `ostree-bloom-private`, TXT record parsing in `ostree-repo-finder-avahi-private.h`, remote/keyring resolution, summary parsing constants, and the shared `OstreeRepoFinder` interface. `ostree-repo-pull.c` creates it for the configured `lan` repo finder and starts it before `ostree_repo_finder_resolve_all_async`.

Risks: behavior is compile-time optional; without Avahi, resolve and start return not-supported errors. Network discovery is asynchronous and requires the supplied main context to be iterated. Bloom filters can produce false positives, so summary download and validation are required. Dynamic remote names are derived from escaped URI/keyring strings with an acknowledged weak `_` separator. TXT parsing rejects malformed or non-normal `GVariant` values, but bad peers can still cause repeated summary fetch failures. `stop` cancels all pending resolves and clears Avahi handles from the Avahi context.

Test signals: `tests/test-repo-finder-avahi.c` covers construction and TXT record parsing edge cases. Full live Avahi discovery is not exercised there; integration is indirectly covered by pull/find-remotes paths when the `lan` finder is enabled.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-finder-avahi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-finder-avahi.h -->
# sources/cloud-native/ostree/src/libostree/ostree-repo-finder-avahi.h

Purpose: declares the public final `OstreeRepoFinderAvahi` type and its lifecycle API for LAN repository discovery using Avahi.

Important APIs/types/functions: `OSTREE_TYPE_REPO_FINDER_AVAHI`, `G_DECLARE_FINAL_TYPE`, `ostree_repo_finder_avahi_new(GMainContext *context)`, `ostree_repo_finder_avahi_start`, and `ostree_repo_finder_avahi_stop`. The type is also an `OstreeRepoFinder` implementation through the `.c` interface registration.

Control flow: callers create an instance with an optional main context, start network monitoring, use the generic `ostree_repo_finder_resolve_async()` API inherited from the finder interface, then stop monitoring. The header intentionally exposes lifecycle only, not the internal cache or TXT record details.

State and persistence: no state is declared in the header; object internals are private to the `.c` file. Runtime state is transient and tied to the main context and Avahi connection.

Dependencies/integration: includes GLib/GIO/GObject, `ostree-repo-finder.h`, and `ostree-types.h`. It is exported as unstable public API and appears in the released symbol list. Pull code uses it as the default `lan` finder when configured.

Risks: users must understand the main-context requirement documented in the implementation; the header itself cannot enforce that `start` is called before resolving. Builds without Avahi still expose the type but runtime methods return not-supported errors.

Test signals: construction is directly covered by `tests/test-repo-finder-avahi.c`; lifecycle behavior with a real Avahi daemon is environment-dependent.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-finder-avahi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-finder-config.c -->
# sources/cloud-native/ostree/src/libostree/ostree-repo-finder-config.c

Purpose: implements the configured-remote `OstreeRepoFinder` backend, resolving collection refs against remotes already configured in a parent repository.

Important APIs/types/functions: defines final `OstreeRepoFinderConfig`, implements `resolve_async` and `resolve_finish`, and exports `ostree_repo_finder_config_new`. The main routine is `ostree_repo_finder_config_resolve_async`; `results_compare_cb` sorts with `ostree_repo_finder_result_compare`.

Control flow: resolution lists all remotes in `parent_repo`, skips remotes without a valid `collection-id`, loads each remote's collection refs, intersects them with the requested refs, and accumulates a `remote_name -> ref/checksum map`. It then looks up each inherited `OstreeRemote` and emits `OstreeRepoFinderResult` objects with priority `100` and no summary timestamp.

State and persistence: the object carries no persistent fields. It reads repository configuration, remote refs, and inherited remote definitions but does not mutate repository state. Result maps borrow requested ref keys and duplicate checksum values.

Dependencies/integration: depends on remote configuration helpers, `ostree_repo_remote_list`, `ostree_repo_remote_list_collection_refs`, collection/ref validation, inherited remote lookup, and the shared finder result type. `ostree-repo-pull.c` creates this backend for the default `config` finder.

Risks: stale or incorrect configured remote refs are trusted at this stage; later pull/find-remotes code must verify summaries and commit availability. Remotes lacking `collection-id` are ignored by design. Errors loading one remote are logged and skipped, so a partially broken configuration can silently reduce result quality.

Test signals: `tests/test-repo-finder-config.c` covers initialization, empty configs, mixed valid/invalid configs, and integration through `ostree_repo_find_remotes_async`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-finder-config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-finder-config.h -->
# sources/cloud-native/ostree/src/libostree/ostree-repo-finder-config.h

Purpose: declares the public final `OstreeRepoFinderConfig` type, the finder backend that resolves refs using locally configured remotes.

Important APIs/types/functions: exposes `OSTREE_TYPE_REPO_FINDER_CONFIG`, `G_DECLARE_FINAL_TYPE`, and `ostree_repo_finder_config_new`. All resolution methods are used through the base `OstreeRepoFinder` interface.

Control flow: callers instantiate the type and pass it to `ostree_repo_finder_resolve_async` or `ostree_repo_finder_resolve_all_async`. The header has no custom properties or lifecycle calls.

State and persistence: no public state. Implementation is stateless beyond the `GObject` instance and reads parent repository configuration on each resolve.

Dependencies/integration: includes GLib/GIO/GObject, `ostree-repo-finder.h`, and `ostree-types.h`; exported in libostree symbols and used by default pull remote discovery.

Risks: the compact API leaves all behavior to implementation docs; callers must supply a parent repo with configured remotes and valid collection refs.

Test signals: API construction and behavior are covered by `tests/test-repo-finder-config.c`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-finder-config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-finder-mount.c -->
# sources/cloud-native/ostree/src/libostree/ostree-repo-finder-mount.c

Purpose: implements the removable-volume `OstreeRepoFinder` backend, scanning mounted volumes for OSTree repositories and resolving requested collection refs to local `file://` remotes.

Important APIs/types/functions: defines final `OstreeRepoFinderMount` with construct-only `monitor` property and exports `ostree_repo_finder_mount_new`. Core helpers include `scan_repo`, `scan_and_add_repo`, `RepoAndRefs`, `UriAndKeyring`, and `ostree_repo_finder_mount_resolve_async/finish`.

Control flow: resolution enumerates mounts from a `GVolumeMonitor`, skips shadowed/system mounts, opens mount roots, and records the mount device. It scans `.ostree/repos.d` in lexical order, then well-known fallback paths `.ostree/repo`, `ostree/repo`, and `var/lib/flatpak/repo`. Each candidate is opened with `ostree_repo_open_at`, rejected if it resolves outside the mounted filesystem or equals the parent repo, and queried for local collection refs. For each requested ref, the first matching repo on a mount is grouped by canonical `file://` URI plus keyring remote, then emitted as a dynamic remote result with priority `50`.

State and persistence: instance state is only the owned `GVolumeMonitor`. Resolution opens repositories and builds temporary result maps; it does not alter repository configuration. Dynamic remotes carry URL, keyring, `gpg-verify=true`, and `gpg-verify-summary=false`.

Dependencies/integration: depends on GIO volume/mount APIs, GLib Unix mount filtering, libglnx fd helpers, OSTree repo open/list refs APIs, remote keyring resolution, and the shared finder interface. `ostree-repo-pull.c` creates it for the configured `mount` finder, and `tests/test-create-usb.sh` exercises mount-discovery behavior.

Risks: symlinks are followed, so the same-device check is critical to prevent repos outside the removable volume from being used. Canonicalization uses `realpath`; missing paths or permission errors simply skip candidates. System mount filtering depends on GLib availability/version. The “first repo per ref per mount” rule trades completeness for avoiding redundant parallel pulls.

Test signals: integration is referenced by `tests/test-create-usb.sh`; broader finder behavior is also exercised through pull/find-remotes tests. Unit coverage for mount edge cases is limited because it depends on system mount state.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-finder-mount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-finder-mount.h -->
# sources/cloud-native/ostree/src/libostree/ostree-repo-finder-mount.h

Purpose: declares the public final `OstreeRepoFinderMount` type for repository discovery on mounted removable volumes.

Important APIs/types/functions: exposes `OSTREE_TYPE_REPO_FINDER_MOUNT`, `G_DECLARE_FINAL_TYPE`, and `ostree_repo_finder_mount_new(GVolumeMonitor *monitor)`.

Control flow: callers optionally inject a volume monitor for tests or specialized environments, then resolve through the generic `OstreeRepoFinder` methods. The implementation fills in the default system monitor during construction when `NULL` is passed.

State and persistence: no public state; the private object stores only the volume monitor and builds results on each resolve. No repo configuration is persisted.

Dependencies/integration: includes GIO/GObject and finder/type headers. Used by default pull remote discovery when `mount` is included in the repo-finders configuration.

Risks: the header exposes only construction, so monitor lifetime and mount filtering details are implementation concerns. Consumers must handle zero results on systems without suitable mounts.

Test signals: behavior is integration-tested through USB/mount scenarios rather than this header directly.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-finder-mount.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-finder-override.c -->
# sources/cloud-native/ostree/src/libostree/ostree-repo-finder-override.c

Purpose: implements a user/test override `OstreeRepoFinder` that searches an explicit list of repository URIs instead of configured remotes or discovery mechanisms.

Important APIs/types/functions: final `OstreeRepoFinderOverride`, `ostree_repo_finder_override_new`, `ostree_repo_finder_override_add_uri`, `ostree_repo_finder_override_resolve_async/finish`, `repo_remote_list_collection_refs`, and `uri_and_keyring_to_name`.

Control flow: callers append override URIs. On resolve, each URI is temporarily represented as an `OstreeRemote` so `ostree_repo_remote_list_collection_refs` can fetch/list its collection refs. For every requested ref advertised by that URI, the code resolves a local keyring remote for the ref's collection, creates a dynamic remote named from URI plus keyring, enables GPG verification, disables summary GPG verification, groups refs per remote, and emits priority `20` results.

State and persistence: the object owns an array of URI strings. During listing, it may temporarily add a remote to the parent repo and removes it afterwards if it did not already exist. Results are transient dynamic remotes.

Dependencies/integration: depends on remote add/remove/list helpers, collection keyring resolution, dynamic remote construction, and the shared finder interface. Intended for user overrides and tests; production code is expected to prefer configured remotes.

Risks: results are only returned when a keyring can be resolved for the collection, preventing unverifiable override pulls. Dynamic name generation has the same escaped URI/keyring separator caveat as other finders. URI listing errors are logged and skipped per URI, so one bad override does not fail the entire resolve. Summary timestamps are unknown and left as zero.

Test signals: used by find-remotes/pull code paths; direct dedicated tests are less visible than config finder tests. Behavior should be validated with explicit override URI tests, missing keyring cases, and duplicate URI/keyring grouping.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-finder-override.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-finder-override.h -->
# sources/cloud-native/ostree/src/libostree/ostree-repo-finder-override.h

Purpose: declares the public final `OstreeRepoFinderOverride` type for resolving refs from caller-supplied repository URIs.

Important APIs/types/functions: exposes `OSTREE_TYPE_REPO_FINDER_OVERRIDE`, `G_DECLARE_FINAL_TYPE`, `ostree_repo_finder_override_new`, and `ostree_repo_finder_override_add_uri`.

Control flow: construct the finder, add one or more URIs, then resolve using the base `OstreeRepoFinder` async API. The URI list is mutable through repeated `add_uri` calls before or between resolves.

State and persistence: the header exposes no fields; implementation stores owned URI strings and creates dynamic remotes per resolve. It does not persist remote configuration.

Dependencies/integration: includes GIO/GObject, `ostree-repo-finder.h`, and `ostree-types.h`; exported in libostree symbols for applications that need controlled remote discovery.

Risks: callers must add valid reachable URIs and ensure parent repo keyring configuration can verify any matching collections. The API does not expose removal or clearing of override URIs.

Test signals: should be covered through resolve behavior and pull-from-remotes tests; the header itself only contributes ABI/type coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-finder-override.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-finder.c -->
# sources/cloud-native/ostree/src/libostree/ostree-repo-finder.c

Purpose: defines the shared `OstreeRepoFinder` interface, the parallel multi-finder orchestration helpers, and the boxed `OstreeRepoFinderResult` type used by remote discovery and pull selection.

Important APIs/types/functions: `ostree_repo_finder_resolve_async/finish`, `ostree_repo_finder_resolve_all_async/finish`, `OstreeRepoFinderResult`, `ostree_repo_finder_result_new`, `dup`, `compare`, `free`, and `freev`. Internal validation helpers check collection refs, checksum maps, and result array ordering.

Control flow: single-finder resolution is a thin wrapper around `resolve_all` with a one-element finder array. `resolve_all_async` validates inputs, starts every finder implementation in parallel, collects successful result arrays, logs individual finder errors without failing the whole operation, waits for all pending finders using `ResolveAllData`, sorts results, and returns a single `GPtrArray`. Result construction refs the remote/finder and ref/checksum maps; comparison orders by priority, then summary last-modified when both nonzero, then count of non-NULL checksums, then remote name.

State and persistence: interface objects are external. This file manages only per-operation `GTask` state and boxed-result ownership. No repository state is changed here.

Dependencies/integration: finder implementations register `resolve_async`/`resolve_finish` vfuncs. `ostree-repo-pull.c` and public find-remotes APIs consume sorted result arrays and result metadata to choose pull sources.

Risks: `resolve_all` ignores individual finder failures and returns whatever other finders produced, which is resilient but can hide a broken discovery backend unless debug logs are inspected. `ostree_repo_finder_result_new` rejects empty ref maps, even though higher-level comments discuss zero-ref results. `compare` currently orders lower numeric priority first and has a FIXME about zero-ref results and “usefulness” semantics.

Test signals: `tests/test-repo-finder-config.c` exercises interface calls and `ostree_repo_find_remotes_async`. Additional tests should cover result ordering, validation failures, multi-finder partial failures, and boxed ownership.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-finder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-finder.h -->
# sources/cloud-native/ostree/src/libostree/ostree-repo-finder.h

Purpose: declares the public repository finder interface and result data model used to locate remotes that may provide requested collection refs.

Important APIs/types/functions: `OstreeRepoFinderInterface` with `resolve_async` and `resolve_finish` vfuncs; public wrappers for single and multi-finder resolution; `OstreeRepoFinderResult` with `remote`, `finder`, `priority`, `ref_to_checksum`, `summary_last_modified`, and nullable `ref_to_timestamp`; boxed type and free helpers; `OstreeRepoFinderResultv`.

Control flow: implementers supply async resolution vfuncs returning `GPtrArray` results. Consumers can run one finder or a NULL-terminated array of finders in parallel, then pass results to pull APIs. Result maps indicate which requested refs a remote can provide and the commit checksum/timestamps available for prioritization.

State and persistence: the header defines immutable result objects after construction; maps are ref-counted hash tables and remote/finder references are owned by each result.

Dependencies/integration: includes GIO/GObject, `ostree-ref.h`, `ostree-remote.h`, and `ostree-types.h`. Finder implementations in this group and `ostree-repo-pull.c` are the primary integration points.

Risks: the API relies on pointer-keyed `OstreeCollectionRef` maps with custom hash/equal semantics, so ownership and lifetime must match implementation expectations. Documentation permits `NULL` checksums for advertised-but-not-provided refs; downstream code must handle those.

Test signals: ABI symbols are listed in `libostree-released.sym`; behavior is covered by config finder and find-remotes tests, with more specialized coverage in each backend.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-finder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-libarchive.c -->
# sources/cloud-native/ostree/src/libostree/ostree-repo-libarchive.c

Purpose: bridges libarchive archives and OSTree mutable trees/repo objects, supporting archive import into an `OstreeMutableTree` and export of an `OstreeRepoFile` tree back to a libarchive writer.

Important APIs/types/functions: public functions are `ostree_repo_import_archive_to_mtree`, `ostree_repo_write_archive_to_mtree`, `ostree_repo_write_archive_to_mtree_from_fd`, and `ostree_repo_export_tree_to_archive`. Internal import context `OstreeRepoArchiveImportContext`, `DeferredHardlink`, path normalization helpers, xattr/SELinux helpers, hardlink deferral, and recursive export helpers do most work.

Control flow: import reads archive headers, accepting `ARCHIVE_WARN` while validating UTF-8 path and symlink data itself. Paths are made relative, optionally translated or converted with the OSTree `/etc -> /usr/etc` convention, parent directories are created when requested, commit modifiers can skip/modify entries and xattrs, file content is written as OSTree content objects, directory metadata is written separately, and hardlinks are resolved after all entries are seen. Export recursively enumerates an `OstreeRepoFile` tree, writes directory/file/symlink archive entries, emits xattrs unless disabled, streams regular content from the repo, and uses checksum tracking to emit hardlinks for duplicate content.

State and persistence: import persists new OSTree content and directory metadata objects and mutates the provided mutable tree. Export is read-only against repo objects and stores only per-export checksum state. Builds without libarchive return not-supported errors.

Dependencies/integration: depends on libarchive, `ostree-libarchive-input-stream`, repo content APIs, mutable-tree APIs, commit modifiers, SELinux policy lookup, xattr callbacks, GLib file info, and core object serialization. Tests in `tests/test-libarchive-import.c` exercise import behavior.

Risks: path handling is security-sensitive; `path_relative` rejects `.`/`..` after normalizing absolute paths. UTF-8 handling was explicitly hardened to avoid locale conversion failures. Hardlink reconstruction is subtle because archive formats differ in ordering and size semantics. Unsupported file types either fail or are ignored depending on options. There is a duplicated `archive_read_close()` call in `write_archive_to_mtree`, which appears harmless but is worth regression testing.

Test signals: `tests/test-libarchive-import.c` covers import paths and options. Export should be tested for xattrs, symlinks, hardlinks by checksum, path prefixes, and content streaming errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-libarchive.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-os.c -->
# sources/cloud-native/ostree/src/libostree/ostree-repo-os.c

Purpose: derives standard metadata for bootable OSTree commits from a root filesystem tree.

Important APIs/types/functions: implements `ostree_commit_metadata_for_bootable(GFile *root, GVariantDict *dict, GCancellable *cancellable, GError **error)`.

Control flow: the function opens `usr/lib/modules` under the supplied root, iterates child directories, and looks for a `vmlinuz` file inside each directory. If exactly one kernel module directory with `vmlinuz` is found, it inserts `ostree.bootable=true` and `ostree.linux=<kernel release>` into the caller's `GVariantDict`. It errors if no kernel is found or if multiple kernels are present.

State and persistence: no repository state is touched. The caller-owned metadata dictionary is updated in memory; later commit code persists those keys into commit metadata.

Dependencies/integration: depends on GIO file enumeration, `OSTREE_GIO_FAST_QUERYINFO`, libglnx error prefixing, and constants declared in `ostree-repo-os.h`. Intended for commit/build code that wants to mark bootable OS commits.

Risks: the heuristic assumes bootable commits have exactly one kernel in `/usr/lib/modules/<release>/vmlinuz`. Multi-kernel images fail deliberately. Missing `usr/lib/modules` or permission errors surface as open failures. The check uses `g_file_query_exists` without passing the caller cancellable for the nested `vmlinuz` query.

Test signals: no direct test appeared in the searched subset. Useful coverage would include no-kernel, one-kernel, multi-kernel, non-directory children, and metadata dictionary assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-os.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-os.h -->
# sources/cloud-native/ostree/src/libostree/ostree-repo-os.h

Purpose: declares metadata keys and the helper API for marking OSTree commits as bootable OS commits.

Important APIs/types/functions: defines `OSTREE_METADATA_KEY_BOOTABLE` (`ostree.bootable`, type `b`), `OSTREE_METADATA_KEY_LINUX` (`ostree.linux`, type `s`), and `ostree_commit_metadata_for_bootable`.

Control flow: callers provide a root `GFile` and mutable `GVariantDict`; the implementation inspects the filesystem and inserts the two keys when a kernel is found.

State and persistence: the header defines metadata contract only. Persistence occurs when the caller writes the updated dictionary into commit metadata.

Dependencies/integration: includes GIO, `ostree-types.h`, and `sys/stat.h`. The constants are public API since 2021.1 and should remain stable for consumers inspecting bootable commit metadata.

Risks: changing key names or variant types would break consumers. The API returns errors rather than silently omitting metadata, so callers must decide whether bootable metadata is mandatory.

Test signals: direct tests should assert both keys and types; current coverage is not obvious from nearby test search.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-os.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-private.h -->
# sources/cloud-native/ostree/src/libostree/ostree-repo-private.h

Purpose: central private header for `OstreeRepo`, repository transaction state, locks, feature flags, configuration constants, and internal helper declarations shared across libostree implementation files.

Important APIs/types/functions: defines summary/cache constants, commit metadata keys, `OstreeRepoCommitModifier`, `OstreeRepoSysrootKind`, `OstreeRepoTxn`, `OstreeRepoLock`, feature-support enums, bootloader option enums, and the private `struct OstreeRepo`. It declares internal helpers for tmpdir allocation/locking, loose object checks, directory metadata writes, ref updates, repo file creation, traversal, commit modifier application, remote add/remove/get, GPG verification, object import, fs-verity, composefs, auto transactions, and object listing.

Control flow: this header has no executable flow, but it shapes the control flow of most repo operations by exposing fd-based repo internals, transaction fields, cache locks, remotes/config state, repo mode, object dirs, and feature flags to implementation units.

State and persistence: `struct OstreeRepo` holds persistent repository descriptors and cached configuration: repo/cache/object fds, remotes hash table, `GKeyFile` config, collection ID, repo mode, payload link threshold, default repo finders, sysroot/boot settings, fs-verity/composefs support, transaction state, and mutable caches. Many fields mirror on-disk repo layout or config and must stay synchronized with open/init code.

Dependencies/integration: included by nearly every libostree repo implementation in this group, including finders, libarchive, prune, and pull verification. It bridges public headers with internal subsystems such as remotes, refs, object storage, commit traversal, GPG, fs-verity, composefs, and sysroot configuration.

Risks: because it exposes the full private instance layout, unrelated implementation files can become tightly coupled to fields like `device`, `inode`, `repo_finders`, `payload_link_threshold`, and fd members. ABI is private but source churn can be high. Concurrency-sensitive fields are protected by different mutexes/locks, so callers must respect comments and established locking conventions.

Test signals: no single test covers this header; coverage is distributed across repo open/config, pull, commit, checkout, prune, finder, and storage tests. Changes here require broad build and integration testing.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-prune.c -->
# sources/cloud-native/ostree/src/libostree/ostree-repo-prune.c

Purpose: implements repository garbage collection for loose objects, static deltas, and stale summary cache files, with APIs for standard pruning and pruning from a caller-provided reachable set.

Important APIs/types/functions: public APIs are `ostree_repo_prune_static_deltas`, `ostree_repo_traverse_reachable_refs`, `ostree_repo_prune`, and `ostree_repo_prune_from_reachable`. Internal pieces include `OtPruneData`, `maybe_prune_loose_object`, `_ostree_repo_prune_tmp`, `repo_prune_internal`, and `traverse_reachable_internal`.

Control flow: pruning builds or receives a reachable-object set, lists candidate objects, then visits each serialized object key. Reachable objects update counters; unreachable objects have storage size queried, commit partial markers cleared when applicable, payload-link targets checked against `payload_link_threshold`, and the object deleted unless `NO_PRUNE` is set. Static deltas targeting missing commits are removed, and summary-cache entries for removed remotes are unlinked. Standard `ostree_repo_prune` either traverses all commit objects or only refs depending on flags and depth.

State and persistence: deletes loose objects, static delta directories, and stale summary cache files under repo/cache dirs. It updates output counters for total/pruned objects and bytes. It uses exclusive repo locks for pruning and static-delta deletion; reachable traversal uses shared locks.

Dependencies/integration: depends on object listing/traversal APIs, loose object path helpers, payload-link constants, repo object deletion, storage-size queries, static delta listing/path helpers, refs and collection refs enumeration, and repo lock helpers.

Risks: pruning is destructive unless `OSTREE_REPO_PRUNE_FLAGS_NO_PRUNE` is set. Reachability correctness is critical; wrong refs/depth/flags can delete history or content. Payload-link handling must not remove useful links for large target payloads. Commit-only mode keeps non-commit objects but still reports logs differently. Static delta pruning runs after object traversal and can remove deltas independently of object counts.

Test signals: prune behavior is typically covered by repository and pull tests that create unreachable objects/deltas. Strong tests should assert `NO_PRUNE`, refs-only depth, commit-only behavior, static delta deletion, stale summary cache cleanup, and payload-link threshold behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-prune.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-pull-private.h -->
# sources/cloud-native/ostree/src/libostree/ostree-repo-pull-private.h

Purpose: declares private pull-state types and verification helper prototypes shared by OSTree pull implementation files.

Important APIs/types/functions: defines `OstreeFetcherSecurityState` and the large `OtPullData` struct. Declares `_signapi_init_for_remote`, `_sign_verify_for_remote`, `_verify_unwritten_commit`, and `_process_gpg_verify_result`.

Control flow: `OtPullData` is the shared mutable state machine for pull operations: remote identity, fetcher/mirrorlists/local caches, main context/cancellable/progress, HTTP options, phases, verification settings, summary metadata, ref maps, static delta state, object request/pending sets, counters, timestamp/depth limits, import flags, signapi verifier arrays, queued object scans, and async error handling.

State and persistence: the struct itself is transient pull runtime state, but it coordinates persistent writes to the target repo, object imports, verification caches, and summary/ref decisions in other files. `verified_commits` and `signapi_verified_commits` avoid duplicate verification.

Dependencies/integration: includes fetcher utilities, remote/private repo headers, and is consumed by `ostree-repo-pull.c`, `ostree-repo-pull-verify.c`, and related static delta/fetch code. Verification helpers declared here are implemented in `ostree-repo-pull-verify.c`.

Risks: the struct is broad and mutable, so field initialization and cleanup must stay synchronized with pull code. Counters and pending sets drive async completion and progress; mistakes can deadlock or prematurely complete pulls. Security fields (`gpg_verify`, `signapi_*`, `trusted_http_direct`, `disable_verify_bindings`) must be interpreted consistently across fetch and verify stages.

Test signals: pull shell tests, signed pull tests, mirrorlist tests, and pre-signed pull tests exercise subsets of this state. Field-level changes need broad pull regression coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-pull-private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-pull-verify.c -->
# sources/cloud-native/ostree/src/libostree/ostree-repo-pull-verify.c

Purpose: implements signature verification support for pulls and public detached commit verification, covering GPG and OSTree signapi backends.

Important APIs/types/functions: `_signapi_init_for_remote`, `_sign_verify_for_remote`, `_process_gpg_verify_result`, `ostree_repo_signature_verify_commit_data`, and `_verify_unwritten_commit`. Internal helpers include `get_signapi_remote_option`, `_signapi_load_public_keys`, `string_is_gkeyfile_truthy`, `verifiers_from_config`, and `validate_metadata_size`.

Control flow: signapi initialization reads remote options `sign-verify` and `sign-verify-summary`. Boolean true means all compiled sign types with optional configured keys; a list means explicit required sign types whose keys must load from `verification-<type>-file` and/or `verification-<type>-key`. Verification scans configured signers, looks up each signer's metadata key in detached metadata, and accepts the first valid signature. Public commit verification validates metadata sizes, requires detached metadata, checks remote GPG/signapi configuration, runs enabled verifiers, and returns textual results. Pull-time `_verify_unwritten_commit` verifies GPG and/or signapi before writing a commit and records verified checksums.

State and persistence: verification itself is read-only, but pull verification updates `verified_commits` and `signapi_verified_commits` caches and emits the repo `gpg-verify-result` signal. It consumes remote config and detached metadata.

Dependencies/integration: depends on `OstreeSign`, GPGME-backed repo verification when enabled, remote option readers, pull state in `OtPullData`, metadata variant formats, and fetch/pull code that calls verification before object import.

Risks: commit metadata is mandatory for signapi and public verification; missing detached metadata fails. If both GPG and signapi are enabled, both must succeed. Boolean/list parsing follows GKeyFile truthiness and list semantics, so config mistakes can change enforcement strength. Error reporting preserves only the first signapi verification error with a count of other invalid signatures. GPG code is excluded when `OSTREE_DISABLE_GPGME` is defined.

Test signals: `tests/test-signed-pull.sh`, `tests/test-signed-pull-summary.sh`, `tests/test-pre-signed-pull.sh`, and `tests/test-commit-sign-sh-ext.c` cover signapi/GPG configuration, missing metadata, invalid keys/signatures, public verification, and pull failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo-pull-verify.c -->
