# Research: subset-b-000251

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo.h -->
# sources/cloud-native/ostree/src/libostree/ostree-repo.h

Purpose: public libostree repository API declaration surface. It defines the `OstreeRepo` GObject interface used to create/open repositories, configure remotes, transact object writes, resolve refs, commit trees, checkout trees, generate/apply deltas, traverse/prune reachability, pull remote content, verify signatures, regenerate summaries/metadata, and coordinate repository locks.

Important APIs/types/functions: repo construction and lifecycle are exposed through `ostree_repo_new`, `ostree_repo_new_for_sysroot_path`, `ostree_repo_new_default`, `ostree_repo_open`, `ostree_repo_open_at`, `ostree_repo_create`, and `ostree_repo_create_at`. Configuration and remotes include `ostree_repo_get_config`, `ostree_repo_copy_config`, `ostree_repo_reload_config`, `ostree_repo_write_config[_and_reload]`, `ostree_repo_remote_add/delete/change/list`, remote option getters, summary fetchers, collection-id accessors, parent repo access, and default finder APIs. Transactional write APIs include `OstreeRepoTransactionStats`, `ostree_repo_prepare_transaction`, `ostree_repo_commit_transaction`, `ostree_repo_abort_transaction`, transaction ref setters, immediate ref setters, partial-commit marking, object presence checks, metadata/content write APIs, trusted write variants, async write/finish pairs, inline regular-file and symlink writers, and `OstreeContentWriter` creation. Ref/object load APIs cover rev resolution, collection refs, ref listing, remote refs, variant/object/commit/file loading, object import/delete/fsck, object storage size, and static object listing. Commit APIs define `OstreeRepoCommitModifier`, commit filters, xattr callbacks, SELinux policy attachment, devino cache, archive import/export options, mtree writing, composefs metadata addition, commit writing, and detached commit metadata read/write. Checkout APIs define checkout modes, overwrite modes, checkout filters, `OstreeRepoCheckoutAtOptions`, devino cache helpers, `ostree_repo_checkout_at`, composefs checkout, checkout GC, and read-commit helpers. Reachability and cleanup APIs define list-object flags, static delta generation/reindex/execution/signature verification, traversal helpers, traversal iterators, prune flags, `OstreeRepoPruneOptions`, reachable-ref traversal, and prune-from-reachable. Pull/signature APIs define pull flags/options/async finders, keyring resolution, collection ref listing, default progress callback, GPG signing and verification, SignAPI verification flags, summary/metadata regeneration, and lock/auto-lock helpers. Constants include `OSTREE_REPO_METADATA_REF`, `OSTREE_META_KEY_DEPLOY_COLLECTION_ID`, GPG key variant format definitions, and the include handoff to `ostree-repo-deprecated.h`.

Control flow: this header does not implement control flow, but it encodes the expected call sequences. Typical write flow is open/create repo, prepare transaction, write metadata/content or commit mtree, set refs in the transaction, then commit or abort. Pull and import flows resolve refs/remotes, write trusted or checksum-verified objects, then update refs. Checkout flows build `OstreeRepoCheckoutAtOptions` and materialize a commit into a destination directory, optionally using SELinux and devino caches. Prune flows compute reachable objects from refs or caller-provided reachable sets and then prune according to flags. Signing flows either use legacy GPG APIs or the newer `OstreeSign` interface for commits, deltas, and summaries. Locking is explicit with push/pop or C auto-cleanup wrappers, and high-level callers such as sysroot cleanup use exclusive locks for mutation.

State/persistence: the API persists repository configuration, remotes, refs, collection refs, loose/packed objects, static deltas, commit detached metadata, summaries and `summary.sig`, GPG key imports, metadata commits on `ostree-metadata`, object pruning, checkout filesystem trees, and lock state. Transaction stats expose persisted object-count and content-byte changes. Many APIs accept `GCancellable` and `GError` because filesystem/network mutation is long-running and fallible.

Dependencies/integration: depends on GLib/GIO object, variant, async, stream, file, key-file, and hash-table types; OSTree core types, async progress, GPG verify results, refs, repo finders, SELinux policy objects, signing engines, and deprecated compatibility declarations. It is the central integration point for almost every libostree module, command-line admin/pull/sign/summary code, sysroot cleanup, commit code, bindings, and external users.

Risks: this is a very broad stable ABI surface with many extensible structs carrying reserved fields, so layout/API compatibility matters. Transaction/ref APIs can corrupt reachability if called out of order or without locks. Trusted write APIs rely on the caller's trust boundary and can bypass checksum verification. Prune flags and reachable-set handling can delete required objects if active deployment refs or caller reachability are wrong. Checkout options combine whiteout handling, xattrs, SELinux, hardlinks, composefs, and overwrite semantics, which creates compatibility and security risk. Signature verification flags can intentionally skip GPG or SignAPI verification and must be used only by callers that understand the trust implications.

Test signals: Makefile and test tree references show coverage for commit signing (`test-commit-sign.sh`, `test-signed-commit-*`, GPG signed commits), summary signatures (`test-pull-summary-sigs.sh`, `test-signed-pull-summary.sh`), deltas (`test-delta-sign.sh`, `test-delta-ed25519.sh`, static delta tests), pruning (`test-prune.sh`, `test-prune-collections.sh`, basic prune cases), SELinux commit/checkout paths (`basic-test.sh`, `test-libarchive-import.c`, installed SELinux label tests), checkout/import/export/bindings tests, and Rust binding ABI/layout coverage. Remaining risk is mainly cross-product interaction coverage rather than absence of direct API tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-repo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-rollsum.c -->
# sources/cloud-native/ostree/src/libostree/ostree-rollsum.c

Purpose: computes rolling-checksum chunk matches between two byte blobs for delta-style reuse analysis. It chunks both inputs with bupsplit bounded by `ROLLSUM_BLOB_MAX`, hashes chunks with CRC32, then confirms candidate matches by byte comparison.

Important APIs/types/functions: `ROLLSUM_BLOB_MAX` caps chunks at 32 KiB. `rollsum_chunks_crc32` returns a hash table keyed by CRC32, with values as arrays of `(crc,start,length)` `GVariant`s. `compare_matches` sorts final matches by destination offset. `_ostree_compute_rollsum_matches` is the exported private worker that produces `OstreeRollsumMatches`. `_ostree_rollsum_matches_free` releases hash tables, match array, and result struct.

Control flow: `rollsum_chunks_crc32` walks a `GBytes` buffer from `start` to EOF, asking `bupsplit_find_ofs` for a content-defined boundary until bupsplit returns 0, after which it switches to fixed-size chunks. It computes CRC32 over each chunk, stores a `GVariant` triple under that CRC, and advances by the chunk length. `_ostree_compute_rollsum_matches` builds chunk tables for `from` and `to`, iterates the destination table, finds source chunks sharing each CRC, skips mismatched lengths, then uses `memcmp` to confirm actual byte equality before appending `(crc,length,to_start,from_start)` to the match list. It updates `crcmatches`, `bufmatches`, `match_size`, and `total`, sorts matches, then transfers ownership of all allocated containers to the returned struct.

State/persistence: all state is transient and in-memory: source and target rollsum tables, counters, and match arrays. No filesystem, repository, or global state is changed. The caller owns the returned result and must free it with `_ostree_rollsum_matches_free` or the autoptr cleanup from the header.

Dependencies/integration: depends on `bupsplit.h` for content-defined boundaries, zlib `crc32`, GLib `GBytes`, `GHashTable`, `GPtrArray`, and `GVariant`, plus libglnx cleanup helpers. The Makefile builds `tests/test-rollsum` and `tests/test-rollsum-cli` directly with this C file and bupsplit/zlib dependencies, indicating use as a low-level utility rather than a public ABI.

Risks: CRC32 is used only as a prefilter and collisions are handled by `memcmp`, but the implementation still stores CRC keys through `GUINT_TO_POINTER`, which depends on GLib pointer-sized integer conventions. The chunking loop computes `crc32(crc, buf, offset)` against `buf` rather than `buf + start`, so review is warranted because every chunk appears to hash from the beginning of the buffer while match validation later uses correct offsets. `compare_matches` reads child 2 as a start offset from final `(uttt)` tuples; this sorts by target offset, but the helper name/variables are easy to misread. Very large inputs can create many `GVariant` allocations and quadratic candidate comparisons for repeated chunks.

Test signals: `tests/test-rollsum.c` exercises conflicting CRC-like data, identical and shifted buffers, random buffers, and manual free paths; `tests/test-rollsum-cli.c` prints match counters and match size for CLI/manual inspection. Useful additional signals would assert chunk CRCs use intended offsets and cover highly repetitive inputs where candidate explosion is likely.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-rollsum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-rollsum.h -->
# sources/cloud-native/ostree/src/libostree/ostree-rollsum.h

Purpose: private header for rollsum match computation, defining the result container and cleanup API used by the implementation and tests.

Important APIs/types/functions: `OstreeRollsumMatches` stores `from_rollsums`, `to_rollsums`, counters for CRC and byte matches, total destination chunk count, aggregate matched bytes, and an ordered `matches` array. `_ostree_compute_rollsum_matches` computes results for two `GBytes` inputs. `_ostree_rollsum_matches_free` releases a result. `G_DEFINE_AUTOPTR_CLEANUP_FUNC` enables `g_autoptr(OstreeRollsumMatches)`.

Control flow: the header declares a simple call/own/free contract: callers pass immutable byte blobs, receive an owned result with owned GLib containers, inspect counters and match tuples, then free through the cleanup function.

State/persistence: no persistent state. The struct exposes internal containers directly, so callers can observe and possibly mutate the result if they choose.

Dependencies/integration: depends on libglnx, GIO/GLib, and the private implementation in `ostree-rollsum.c`. Tests include this header directly. It is not marked `_OSTREE_PUBLIC`, so it is an internal support interface.

Risks: the struct is not opaque, which makes internal representation visible to any in-tree consumer and may complicate refactors. Match tuple formats are not named in the type system, so users must know that rollsum tables contain `(utt)` and matches contain `(uttt)`.

Test signals: direct test programs listed in `Makefile-tests.am` compile against this header, checking basic API linkage and behavior. ABI tests are unlikely because this is private.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-rollsum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sepolicy-private.h -->
# sources/cloud-native/ostree/src/libostree/ostree-sepolicy-private.h

Purpose: private SELinux helper declarations used by commit/checkout code that needs automatic filesystem create contexts and xattr filtering without exposing the details as stable public API.

Important APIs/types/functions: `OstreeSepolicyFsCreatecon` tracks whether an fscreatecon was initialized. `_ostree_sepolicy_fscreatecon_clear` resets a prepared context and is registered as an automatic clear function. `_ostree_sepolicy_preparefscreatecon` computes and sets the SELinux create context for a path/mode when a policy is active. `_ostree_filter_selinux_xattr` removes `security.selinux` from an xattr variant. `_ostree_sepolicy_host_enabled` reports whether host SELinux is enabled.

Control flow: users can declare `g_auto(OstreeSepolicyFsCreatecon)` and call `_ostree_sepolicy_preparefscreatecon`; cleanup will clear the context only if initialization occurred. Xattr filtering is a pure transform returning a newly built variant or `NULL`.

State/persistence: `OstreeSepolicyFsCreatecon` is stack/local state. The underlying implementation can mutate the process SELinux fscreate context temporarily through libselinux when compiled with SELinux support.

Dependencies/integration: depends on `ostree-types.h` for `OstreeSePolicy`. It is integrated by commit and checkout writers to avoid persisting source SELinux labels when target policy should compute labels.

Risks: create-context state is process-global in libselinux; failure to clear it can label subsequent files incorrectly. The helper's `initialized` bit is the guard against over-clearing or leaking state. Xattr variant type expectations are implicit and must match OSTree xattr serialization.

Test signals: SELinux-sensitive tests in `basic-test.sh`, `test-libarchive-import.c`, and installed payload label tests exercise commit modifier SELinux behavior and xattr handling. Direct unit coverage for the private cleanup helper is not apparent.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sepolicy-private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sepolicy.c -->
# sources/cloud-native/ostree/src/libostree/ostree-sepolicy.c

Purpose: implements `OstreeSePolicy`, a GObject/GInitable that loads SELinux policy from a root filesystem or from a commit checkout, then provides label lookup, restorecon, fscreatecon, checksum/name reporting, logging suppression, and SELinux xattr filtering.

Important APIs/types/functions: `struct OstreeSePolicy` stores a rootfs fd/path, optional tempdir, and under `HAVE_SELINUX` the policy root, `selabel_handle`, policy name, and policy checksum. GObject methods manage construct-only `path` and `rootfs-dfd` properties. `get_policy_checksum` finds the newest binary policy file and returns its SHA256. `ostree_sepolicy_set_null_log` disables libselinux logging. `ostree_sepolicy_new`, `ostree_sepolicy_new_at`, and `ostree_sepolicy_new_from_commit` construct policies from a root path, fd, or commit. `initable_init` parses `etc/selinux/config` or `usr/etc/selinux/config`, sets the libselinux policy root, opens the file-label database, validates lookup for `/`, and records policy metadata. Public query/mutation APIs include `ostree_sepolicy_get_path`, `get_name`, `get_csum`, `get_label`, `restorecon`, `setfscreatecon`, and `ostree_sepolicy_fscreatecon_cleanup`. Private helpers implement fscreatecon RAII, SELinux xattr filtering, and host-enabled detection.

Control flow: construction stores either a canonical `GFile` path or a root directory fd and then runs `GInitable.init`. With SELinux compiled in, initialization primes a cached host SELinux-enabled value, resolves the root path, locates the SELinux config, reads `SELINUX=` and `SELINUXTYPE=`, and only opens the policy if the target config is enforcing or permissive. Policy checkout from a commit reads the commit, creates a temp dir, optionally checks out `usr/etc/selinux` into that temp dir, constructs a fd-based policy, then transfers tempdir ownership to the policy object. Label lookup is a no-op success when no handle exists; otherwise it special-cases `/proc` as `/mnt`, calls `selabel_lookup_raw`, returns `NULL` for `ENOENT`, and propagates other errors. `restorecon` obtains file mode if needed, optionally preserves existing labels, computes the policy label, honors `ALLOW_NOLABEL`, and calls `lsetfilecon`. `setfscreatecon` ignores requests when host SELinux is disabled, otherwise computes the target label and calls `setfscreatecon_raw`. Cleanup resets fscreatecon to `NULL`.

State/persistence: the object holds policy handles and metadata until finalize, where tempdir cleanup, fd close, object unrefs, string frees, and `selabel_close` occur. `restorecon` persists labels on target filesystem objects. `setfscreatecon` mutates process SELinux create-label state until cleanup. `new_from_commit` creates temporary extracted policy state under an owned tempdir. `_ostree_filter_selinux_xattr` returns a new xattr variant without mutating input.

Dependencies/integration: conditional dependency on libselinux (`selinux/label.h`, `selinux/selinux.h`), plus GLib/GIO, libglnx fd/tmpdir helpers, OSTree repo checkout/read APIs, and utility checksum helpers. It is integrated by `OstreeRepoCommitModifier`, checkout paths, archive import, sysroot/deployment labeling, and tests that run only when SELinux relabeling is available.

Risks: libselinux policy root and fscreatecon are process-global concepts, so concurrent policy use and cleanup order deserve care. `initable_init` currently constructs a `GFile` for fd-based roots through `ot_fdrel_to_gfile`; fd-relative roots without global path access are only partially supported. Target SELinux enabled with host SELinux disabled silently skips `setfscreatecon`, which is intentional but can produce unlabeled files unless later relabeling occurs. `restorecon` can fail deployments if `ALLOW_NOLABEL` is not set and policy lacks a path label. The `/proc` workaround is narrowly targeted and should be kept with regression coverage. Builds without `HAVE_SELINUX` return success/null for most operations, so callers must treat absence of a policy as expected.

Test signals: `tests/test-libarchive-import.c` has a `/libarchive/selinux` test that creates a policy, attaches it to a commit modifier, imports archive content, and checks `security.selinux` labels. `basic-test.sh` has SELinux-relabeled sections and skips when unavailable. Installed/nondestructive tests such as bare-user-root and payload-link exercise host-policy commit paths. Additional direct tests should cover fd-based roots, `KEEP_EXISTING`, `ALLOW_NOLABEL`, xattr filtering with only `security.selinux`, and host-disabled/target-enabled behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sepolicy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sepolicy.h -->
# sources/cloud-native/ostree/src/libostree/ostree-sepolicy.h

Purpose: public header for `OstreeSePolicy`, exposing SELinux policy construction and file-label APIs used by repository commit/checkout code and external libostree consumers.

Important APIs/types/functions: type macros and `ostree_sepolicy_get_type` define the GObject. Constructors are `ostree_sepolicy_new`, `ostree_sepolicy_new_at`, and `ostree_sepolicy_new_from_commit`. Accessors expose root path, policy name, policy checksum, and per-path label lookup. `OstreeSePolicyRestoreconFlags` provides `ALLOW_NOLABEL` and `KEEP_EXISTING`. `ostree_sepolicy_restorecon`, `ostree_sepolicy_setfscreatecon`, and `ostree_sepolicy_fscreatecon_cleanup` provide labeling operations. `ostree_sepolicy_set_null_log` disables libselinux logging.

Control flow: callers construct a policy from a root or commit, query label/name/checksum as needed, pass it to commit modifiers or checkout options, or call restore/create-context APIs directly. The cleanup macro enables C scope-based reset of fscreatecon.

State/persistence: objects own policy handles and optional temp extraction state. `restorecon` persists file xattrs, while `setfscreatecon` alters process-global creation context until cleanup.

Dependencies/integration: depends on `ostree-types.h`, GLib/GIO types, and the implementation's optional libselinux support. `ostree-repo.h` includes this header because commit modifiers and checkout options accept `OstreeSePolicy`.

Risks: `ostree_sepolicy_get_path` is documented as effectively deprecated because fd-based policies may not have a globally accessible path. Callers must not assume non-NULL policy name/checksum, especially on non-SELinux builds or roots with disabled policy. Cleanup use is critical after `setfscreatecon`.

Test signals: integration and libarchive tests cover public construction and commit labeling paths under SELinux-capable environments. Header API shape is also indirectly covered by C and Rust binding compilation.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sepolicy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sign-dummy.c -->
# sources/cloud-native/ostree/src/libostree/ostree-sign-dummy.c

Purpose: implements a test-only `OstreeSign` backend named `dummy`. It stores ASCII strings as secret/public keys and treats the secret string bytes as the signature, allowing signing pipeline tests without cryptographic dependencies.

Important APIs/types/functions: `OstreeSignDummy` stores `sk_ascii` and `pk_ascii`. `check_dummy_sign_enabled` requires `OSTREE_DUMMY_SIGN_ENABLED=1`. Interface init wires `get_name`, `data`, `data_verify`, metadata key/format, `set_sk`, `set_pk`, and maps `add_pk` to `set_pk`. `ostree_sign_dummy_set_sk` and `set_pk` duplicate strings from `GVariant`. `ostree_sign_dummy_data` returns the secret string as `GBytes`. `ostree_sign_dummy_data_verify` checks metadata type `aay`, iterates signatures, and succeeds when any signature string equals the public key string.

Control flow: signing and verification first enforce the environment guard. Signing requires a secret key already set and creates bytes from the stored string. Verification rejects missing signatures or wrong variant type, converts each byte-array child to a string, logs candidate/stored values, and returns the first match; otherwise it reports incorrect or absent signatures.

State/persistence: key strings are stored in the GObject instance. Signatures are persisted by the generic signing layer into detached commit metadata or `summary.sig` under metadata key `ostree.sign.dummy`. The backend itself does not write files.

Dependencies/integration: depends on the generic `OstreeSign` interface, GLib/GObject/GVariant/GBytes, libglnx error helpers, and string utilities. It is always included in the `sign_types` table as the fallback/test engine and is used by test scripts when the environment variable enables it.

Risks: it is intentionally not secure; the environment guard is the only barrier against accidental production use. The implementation does not define finalize cleanup for key strings, so object destruction may leak small allocations unless handled by private data cleanup elsewhere. `data` assumes `sk_ascii` is non-NULL and will crash on `strlen(NULL)` if a caller signs before setting a key. Because `add_pk` replaces the key, multi-key semantics differ from real engines.

Test signals: `tests/test-signed-commit-dummy.sh` signs unsigned commits, verifies detached metadata, commits with `--sign-type=dummy`, and checks that verification without `OSTREE_DUMMY_SIGN_ENABLED` fails. Generic signing tests also exercise summary/commit metadata append paths through this backend.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sign-dummy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sign-dummy.h -->
# sources/cloud-native/ostree/src/libostree/ostree-sign-dummy.h

Purpose: private/public-internal declaration header for the dummy `OstreeSign` final type and its interface method implementations.

Important APIs/types/functions: defines `OSTREE_TYPE_SIGN_DUMMY`, declares `OstreeSignDummy` as a final `GObject`, and declares name, sign, verify, metadata key/format, secret-key, public-key, and add-public-key functions.

Control flow: the generic signing registry instantiates this type by GType and invokes these functions through the `OstreeSignInterface`; tests can include the header directly if needed.

State/persistence: no persistent state declared in the header; instance state is private to the implementation. Metadata key and format declarations imply detached metadata storage shape `ostree.sign.dummy: aay`.

Dependencies/integration: depends on `ostree-sign.h` and GObject type macros. Included by `ostree-sign.c` to register the backend.

Risks: the header exports method symbols even though the backend is test-only, so callers could misuse it if they bypass the higher-level guard. There is a declared `ostree_sign_dummy_add_pk` prototype, but the implementation maps `add_pk` to `set_pk` rather than defining a separate function body, so direct callers of the prototype would fail linkage if any exist.

Test signals: dummy signing shell tests and generic sign API tests are the main linkage/behavior signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sign-dummy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sign-ed25519.c -->
# sources/cloud-native/ostree/src/libostree/ostree-sign-ed25519.c

Purpose: implements the Ed25519 `OstreeSign` backend for commit, summary, and data signatures, including key loading from explicit variants or well-known trusted/revoked key files.

Important APIs/types/functions: `OstreeSignEd25519` stores backend state, one secret key buffer, trusted public key list, and revoked public key list. State values distinguish usable, unsupported, and failed crypto initialization. Constants define the engine name, seed size, secret-key size, and public/signature sizes from metadata macros. Interface init wires signing, verification, metadata, key clearing, key setting/adding, and key loading. `validate_length` enforces exact key/signature sizes. `_ostree_sign_ed25519_is_initialized` gates crypto operations. `ostree_sign_ed25519_data` signs with libsodium or OpenSSL. `ostree_sign_ed25519_data_verify` validates signatures against trusted, non-revoked keys. Key-management functions clear sensitive memory, decode base64 strings or bytestring variants, deduplicate keys, and add revoked keys. Loading helpers read blobs from streams/files and scan `trusted.ed25519`, `trusted.ed25519.d`, `revoked.ed25519`, and `revoked.ed25519.d` under `/etc/ostree`, `DATADIR/ostree`, or a caller-provided `basedir`.

Control flow: object init detects crypto support (`USE_OPENSSL` or `USE_LIBSODIUM`) and initializes the core crypto layer. Signing clears/sets secret key through `set_sk`, validates initialization and key presence, then signs raw `GBytes` with the compiled crypto backend and returns signature bytes. Verification rejects null data, missing signatures, or wrong metadata variant type; if no public keys were preloaded, it auto-loads default keyrings; then it iterates each signature and each trusted key, skips revoked keys, validates with `otcore_validate_ed25519_signature`, and succeeds on the first valid pair. If only invalid signatures were tried, it reports up to three key IDs; if none were attempted, it reports no signatures found. Loading with `filename` reads trusted keys from one file only; loading without it scans trusted keys first and revoked keys second, ignoring absence of revoked keys.

State/persistence: instance state contains secret material and keyrings. `ostree_sign_ed25519_clear_keys` explicit-bzeros the secret key before freeing and frees public/revoked lists. Signatures persist outside this backend through generic detached metadata key `OSTREE_SIGN_METADATA_ED25519_KEY` and variant type `OSTREE_SIGN_METADATA_ED25519_TYPE`. Default key discovery reads host/system files but does not write them.

Dependencies/integration: depends on `otcore` crypto wrappers, OpenSSL or libsodium conditionals, GLib/GObject/GVariant/GBytes/GList, libglnx error helpers, base64 decoding, `OstreeBlobReader` via `ostree_sign_read_pk`, and checksum hex utilities. Registered by `ostree-sign.c` only when `HAVE_ED25519` is defined. Used by CLI signing, composefs signed-commit validation, summary signing, delta signing, and pull/verify flows using SignAPI.

Risks: `set_sk` calls `clear_keys`, which also clears public and revoked keys; callers setting a signing key after loading verification keys will lose those verification keys. OpenSSL signing constructs the private key from only the seed portion, while validation expects the combined secret key length, so key format conversion must remain intentional. Verification is O(signatures * trusted keys * revoked keys), which is acceptable for small keyrings but can grow. Auto-loading default keyrings during verification makes host state part of validation behavior. Revoked key matching is exact public-key bytes; malformed or duplicate files are mostly ignored after debug logging. Builds without crypto support produce runtime errors for the engine rather than silently falling back.

Test signals: `tests/test-signed-commit-ed25519.sh`, `tests/test-delta-ed25519.sh`, composefs signed tests under installed/integration tests, and generic signed pull/commit paths cover signing, verification, metadata storage, default key loading, and failures. Additional useful coverage would include revoked-key precedence, `filename` vs `basedir`, set-key clearing semantics, and both OpenSSL/libsodium configurations.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sign-ed25519.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sign-ed25519.h -->
# sources/cloud-native/ostree/src/libostree/ostree-sign-ed25519.h

Purpose: declaration header for the Ed25519 final `OstreeSign` backend.

Important APIs/types/functions: defines `OSTREE_TYPE_SIGN_ED25519`, declares `OstreeSignEd25519`, and exposes backend method implementations for signing data, verifying data, returning engine name, metadata key/format, clearing keys, setting secret/public keys, adding public keys, and loading public keys.

Control flow: `ostree-sign.c` registers this type conditionally and invokes these methods through the generic interface. Direct users should normally use `ostree_sign_get_by_name(OSTREE_SIGN_NAME_ED25519)` and generic `OstreeSign` APIs instead of calling backend functions.

State/persistence: state is implementation-private. Public metadata declarations imply detached metadata stores arrays of Ed25519 signatures under the shared metadata key/type macros.

Dependencies/integration: depends on `ostree-sign.h`, GLib/GObject, and compile-time Ed25519 support flags in the implementation. It is included by the generic signing registry and build/test code.

Risks: backend symbols are callable directly, but doing so bypasses some generic API expectations and makes code depend on compile-time availability. Callers must respect exact key/signature formats documented by implementation/tests.

Test signals: shell tests for signed Ed25519 commits/deltas and composefs signed validation exercise the declared methods through generic API/CLI paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sign-ed25519.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sign-private.h -->
# sources/cloud-native/ostree/src/libostree/ostree-sign-private.h

Purpose: private declaration for signing summary files at an arbitrary directory fd, separating internal repo metadata signing support from the public `ostree_sign_summary` convenience API.

Important APIs/types/functions: `_ostree_sign_summary_at` signs `summary` and writes `summary.sig` in `dir_fd` using an `OstreeSign` engine, an `OstreeRepo`, and a variant array of secret keys.

Control flow: internal callers pass a directory fd rather than relying on `repo->repo_dir_fd`; the implementation reads existing `summary`/`summary.sig`, signs the summary for each provided key, appends signatures to metadata, normalizes the variant, and atomically replaces `summary.sig`.

State/persistence: persists `summary.sig` in the selected directory. Does not own key storage beyond temporarily setting keys on the backend while signing.

Dependencies/integration: depends on `ostree-sign.h` and `ostree-types.h`. Used by `ostree-sign.c`; useful for static delta or repository summary contexts that need fd-relative signing.

Risks: because it is private, there is no ABI stability guarantee. Callers must ensure `dir_fd` points at the intended repository-like directory and contains `summary`.

Test signals: summary signature tests (`test-pull-summary-sigs.sh`, signed-pull-summary tests, auto-summary tests) exercise the public path that delegates to this helper.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sign-private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sign-spki.c -->
# sources/cloud-native/ostree/src/libostree/ostree-sign-spki.c

Purpose: implements the SPKI `OstreeSign` backend using OpenSSL key/signature primitives. It signs arbitrary data with DER private keys and verifies signatures against DER SubjectPublicKeyInfo public keys loaded from explicit variants or trusted/revoked key files.

Important APIs/types/functions: `OstreeSignSpki` stores support state, a `GBytes` secret key, trusted public-key `GBytes` list, and revoked-key list. Interface init wires data signing/verification, name, metadata key/format, key clearing, key set/add, and key loading. `_ostree_sign_spki_is_initialized` gates operations based on OpenSSL availability/init. `ostree_sign_spki_data` decodes a private key with `d2i_AutoPrivateKey`, signs with `EVP_DigestSign`, and returns variable-length signature bytes. `ostree_sign_spki_data_verify` checks signatures against trusted non-revoked public keys using `otcore_validate_spki_signature`. Key setters accept base64 string or bytestring variants and store keys as `GBytes`. Loading helpers use `ostree_sign_read_pk`, file scanning, and trusted/revoked directories analogous to Ed25519 but with `spki` suffixes.

Control flow: init marks the engine unsupported unless `USE_OPENSSL` is compiled and `otcore_spki_init` succeeds. Signing validates initialization and secret key presence, decodes private key DER from stored bytes, performs a size-probing `EVP_DigestSign`, signs into an allocated buffer, and returns failure if no signature length is produced. Verification validates input and metadata type, auto-loads default keys if none are present, then nested-iterates signatures and keys, skipping revoked entries and returning success on the first valid signature. Key loading with `filename` reads one trusted file; otherwise it scans `/etc/ostree` and `DATADIR/ostree` for `trusted.spki`, `trusted.spki.d/*`, `revoked.spki`, and `revoked.spki.d/*`.

State/persistence: instance key state is in memory. `clear_keys` attempts to zero secret-key data by unref-to-data then explicit-bzero, and unrefs key lists. Signatures persist through generic detached metadata key `OSTREE_SIGN_METADATA_SPKI_KEY` with type `OSTREE_SIGN_METADATA_SPKI_TYPE`. Default keyrings are read-only inputs.

Dependencies/integration: depends on OpenSSL EVP and DER decoding, `otcore` SPKI validation/init, GLib/GObject/GBytes/GVariant/GList, libglnx errors, `OstreeBlobReader` PEM parsing through `ostree_sign_read_pk`, and checksum hex utilities. Registered by the generic signing layer when `HAVE_SPKI` is defined. Integrates with CLI SignAPI commit/summary verification and tests specific to SPKI.

Risks: no explicit key-length validation is possible for arbitrary SPKI DER, so invalid key material fails later during OpenSSL decode/verify. `_spki_add_revoked` constructs a `GBytes` wrapper but calls `g_list_find_custom(sign->revoked_keys, key, g_bytes_compare)` with the raw key pointer, which looks inconsistent with `g_bytes_compare` expecting `GBytes` values and deserves review. `clear_keys` calls `g_bytes_unref_to_data` but does not free the returned data after zeroing, which may leak secret material storage. Auto-loading host keyrings can make verification environment-dependent. Like Ed25519, verification is nested over signatures/keys/revocations and can become expensive with large key sets.

Test signals: `tests/test-signed-commit-spki.sh` is listed for SPKI builds and should cover signing, verification, metadata storage, and error paths. Generic summary/pull signature tests also apply when SPKI is selected. Additional targeted tests should cover revoked SPKI matching, malformed DER/PEM keys, duplicate keys, and clear-key memory handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sign-spki.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sign-spki.h -->
# sources/cloud-native/ostree/src/libostree/ostree-sign-spki.h

Purpose: declaration header for the SPKI final `OstreeSign` backend.

Important APIs/types/functions: defines `OSTREE_TYPE_SIGN_SPKI`, declares `OstreeSignSpki`, and exposes backend method implementations for data signing/verification, name, metadata key/format, key clearing, secret/public key setting, public key addition, and public key loading.

Control flow: the generic signing registry instantiates this backend conditionally and calls methods through `OstreeSignInterface`; direct callers should prefer the generic `OstreeSign` API.

State/persistence: state is private to the implementation. Detached metadata produced by this backend uses SPKI metadata key/type macros declared elsewhere.

Dependencies/integration: depends on `ostree-sign.h` and OpenSSL-enabled implementation support. Included by the generic signing layer.

Risks: direct use ties callers to optional compile-time support and backend-specific key formats. Because SPKI key material is DER/PEM based, callers must use the matching blob reader or variants.

Test signals: SPKI signed commit tests and generic signing/summary tests exercise this declaration surface through the public interface.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sign-spki.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sign.c -->
# sources/cloud-native/ostree/src/libostree/ostree-sign.c

Purpose: implements the generic `OstreeSign` interface and shared signing workflows for commits, summaries, key loading, backend discovery, and stream readers. It bridges backend-specific signing engines (`ed25519`, `spki`, `dummy`) with repository detached metadata and summary signature persistence.

Important APIs/types/functions: `sign_types` maps engine names to GTypes depending on compile flags, always including dummy. `OstreeSignInterface` default init is empty aside from debug logging. Generic wrappers include `ostree_sign_metadata_key`, `metadata_format`, `clear_keys`, `set_sk`, `set_pk`, `add_pk`, `load_pk`, `data`, `data_verify`, and `get_name`. `_sign_detached_metadata_append` appends a signature byte array to an existing metadata dictionary under the backend metadata key. `ostree_sign_commit_verify` loads commit object and detached metadata, extracts signatures of the backend type, and delegates to `data_verify`. `ostree_sign_commit` signs commit bytes and writes updated detached metadata. `ostree_sign_get_all` and `ostree_sign_get_by_name` instantiate available backends. `_ostree_sign_summary_at` signs `summary` for each key and writes normalized `summary.sig`; `ostree_sign_summary` binds that to the repo fd. `ostree_sign_read_pk` and `ostree_sign_read_sk` select base64, PEM, or raw blob readers based on backend type.

Control flow: generic methods assert `OSTREE_IS_SIGN`, check that the backend implemented the requested vfunc, and return "not implemented" otherwise. Commit signing loads the commit variant, reads existing detached metadata, signs the serialized commit bytes, appends the signature to metadata, then writes detached metadata. Commit verification loads the same serialized commit bytes and detached metadata, looks up the backend signature array, and asks the backend to verify. Summary signing opens `summary`, optionally reads existing `summary.sig`, rejects an empty key array, then for each key sets the backend secret key, signs summary bytes, appends signature metadata, and atomically replaces `summary.sig` through repo file replacement. Backend lookup lazily initializes GTypes and constructs a new GObject for the requested name.

State/persistence: generic interface state lives in backend instances. Persistent outputs are commit detached metadata and `summary.sig`, both as normalized `GVariant` dictionaries keyed by backend-specific metadata names. `ostree_sign_get_all` returns fresh engine instances, not shared state. Summary signing mutates the backend's secret key repeatedly when multiple keys are passed.

Dependencies/integration: depends on GLib/GObject/GVariant/GBytes, libglnx, fd/mmap utilities, OSTree core/repo-private APIs, blob readers, backend headers, and repository detached metadata/summary file helpers. Integrated by CLI signing commands, repository summary regeneration/signing, static delta signature paths, pull/verify code, and tests for GPG and SignAPI coexistence.

Risks: signature append relies on backend metadata format strings being valid `GVariantType`s and matching detached metadata contents. `ostree_sign_commit_verify` passes `NULL` signatures to backends when metadata is absent, so backend error messages drive user diagnostics. Summary signing sets secret keys sequentially; backends like Ed25519/SPKI clear all keys on `set_sk`, which is fine for signing but relevant if a caller expected retained verification keys. `ostree_sign_get_all` asserts backend construction success, so a bad sign_types entry is fatal. The dummy backend is always registered but self-guards via environment at operation time.

Test signals: `test-signed-commit-dummy.sh`, `test-signed-commit-ed25519.sh`, `test-signed-commit-spki.sh`, `test-commit-sign.sh`, `test-delta-sign.sh`, `test-delta-ed25519.sh`, `test-pull-summary-sigs.sh`, `test-signed-pull-summary.sh`, and composefs signed tests exercise commit metadata append/verify, summary signatures, backend selection, key readers, and failure diagnostics. Additional unit coverage should target `_sign_detached_metadata_append` with existing multi-engine metadata and empty-key summary signing.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sign.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sign.h -->
# sources/cloud-native/ostree/src/libostree/ostree-sign.h

Purpose: public header for the SignAPI abstraction, allowing callers to use named signing engines without depending on backend-specific implementation details.

Important APIs/types/functions: defines `OSTREE_TYPE_SIGN`, engine name constants `OSTREE_SIGN_NAME_ED25519` and `OSTREE_SIGN_NAME_SPKI`, and `G_DECLARE_INTERFACE(OstreeSign, ...)`. `struct _OstreeSignInterface` declares vfuncs for engine name, data sign/verify, metadata key/format, key clearing, secret/public key setting, public-key addition, and public-key loading. Public wrappers include data signing/verification, metadata introspection, commit signing/verification, key management, engine enumeration/lookup, summary signing, and public/secret key blob-reader creation.

Control flow: consumers instantiate an engine by name, configure keys through generic methods, then call data/commit/summary sign or verify. Verification returns an optional success message identifying the key used. `ostree_sign_read_pk/sk` lets CLIs parse backend-appropriate key encodings before passing variants to key setters.

State/persistence: the interface itself does not define storage, but backend instances hold keys and generic commit/summary operations persist signatures in repository metadata. Constants name the stable engine selectors exposed to users.

Dependencies/integration: depends on GLib/GObject, `ostree-blob-reader.h`, refs/remotes/types, and repository types. Used by `ostree-repo.h` static delta and signature APIs and by CLI/admin paths.

Risks: backend availability is compile-time dependent, so public constants do not guarantee runtime support. Callers must understand backend-specific key variant formats even though the API is generic. Skipping SignAPI verification through repo verify flags can bypass all engines declared here.

Test signals: backend-specific signed commit tests, summary signature tests, delta signature tests, and Rust binding sign modules exercise the interface. ABI/layout tests should catch accidental public header changes.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sign.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-soft-reboot.c -->
# sources/cloud-native/ostree/src/libostree/ostree-soft-reboot.c

Purpose: prepares a soft reboot target root at `/run/nextroot` for composefs-based OSTree systems, allowing systemd soft reboot into a new root without a full kernel reboot when supported.

Important APIs/types/functions: `_ostree_prepare_soft_reboot` is the sole function. It is compiled to real behavior under `HAVE_SOFT_REBOOT` and otherwise returns "soft reboot not supported". It uses `PREPARE_ROOT_CONFIG_PATH`, `read_proc_cmdline`, `otcore_load_rootfs_config`, `otcore_mount_rootfs`, `otcore_mount_boot`, `otcore_mount_etc`, `OTCORE_RUN_NEXTROOT`, `OTCORE_RUN_NEXTROOT_BOOTED`, and modern mount syscalls (`open_tree`, `mount_setattr`, `move_mount`).

Control flow: the function loads prepare-root config, reads kernel cmdline, loads rootfs config, and rejects non-composefs deployments. It creates `/run/nextroot`, bind-mounts `/sysroot` onto itself so references from the new composefs mount do not block systemd unmounting, refreshes cwd into the new mount, mounts the composefs root at `/run/nextroot`, mounts boot and etc, detaches the temporary sysroot bind mount, refreshes cwd again, clones `/sysroot`, marks the clone read-only with `mount_setattr`, moves it into `/run/nextroot/sysroot`, writes booted metadata including read-only sysroot state, and returns success.

State/persistence: mutates live mount namespace state, creates `/run/nextroot`, mounts root/boot/etc/sysroot into it, writes `OTCORE_RUN_NEXTROOT_BOOTED` metadata as serialized `GVariant`, and temporarily bind-mounts/detaches `/sysroot`. It does not alter repository objects or bootloader config.

Dependencies/integration: depends on Linux mount APIs, libglnx, OSTree core/sysroot private headers, mount utilities, keyfile utilities, and otcore prepare-root helpers. It integrates with rpm-ostree/OSTree soft reboot orchestration and systemd's `/run/nextroot` handoff. Destructive installed tests reference soft reboot behavior.

Risks: this is privileged Linux-only code with modern syscall requirements. Some error paths use `err(EXIT_FAILURE, ...)`, terminating the process rather than returning `GError`, which is risky if used from a library context. It hard-requires composefs and read-only sysroot assumptions. Mount namespace/cwd manipulation is delicate; failure to detach the temporary bind or restore cwd can interfere with systemd unmount behavior. Race conditions with concurrent mount changes are possible.

Test signals: `tests/kolainst/destructive/soft-reboot.sh` exercises soft reboot into staged/non-staged deployments, default soft reboot when `/run/nextroot` is mounted, and failures for kernel/kernel-arg changes. Composefs integration tests also exercise signed composefs deployment prerequisites. Additional low-level tests would need namespace isolation and syscall availability checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-soft-reboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sysroot-cleanup.c -->
# sources/cloud-native/ostree/src/libostree/ostree-sysroot-cleanup.c

Purpose: implements sysroot cleanup and post-copy repair operations: discovering deployment/boot directories, removing inactive boot/deployment state, cleaning bootfs overlays, regenerating deployment refs, pruning unreachable repository objects safely, and reapplying fs-verity to copied repositories/deployments.

Important APIs/types/functions: `_ostree_sysroot_list_deployment_dirs_for_os` appends deployment objects for one stateroot. `list_all_deployment_directories` scans `ostree/deploy/*/deploy`. `_ostree_sysroot_parse_bootdir_name` parses `osname-CHECKSUM`. `_ostree_sysroot_list_all_boot_directories` lists valid boot checksum directories. `cleanup_other_bootversions` removes inactive loader and bootversion directories. `_ostree_sysroot_rmrf_deployment` removes a specific inactive deployment plus origin/backing dirs after clearing immutable flags and guarding against deleting the booted root. `cleanup_old_deployments` compares filesystem deployments to active bootloader deployments. `_ostree_sysroot_cleanup_bootfs` removes boot checksum dirs and overlay initrds not referenced by active deployments. `cleanup_ref_prefix` clears stale deployment refs. `generate_deployment_refs` rewrites `ostree/<bootversion>/<subbootversion>/<index>` refs inside a repo transaction. `ostree_sysroot_cleanup_prune_repo` locks the repo, builds reachability from refs and active deployments, and calls `ostree_repo_prune_from_reachable`. `ostree_sysroot_cleanup`, `ostree_sysroot_prepare_cleanup`, and `_ostree_sysroot_cleanup_internal` orchestrate cleanup with or without pruning. `ostree_sysroot_update_post_copy` reapplies fs-verity to loose objects and deployment composefs files after file-level copy.

Control flow: cleanup starts from a loaded, writable sysroot. It removes inactive bootversion directories, removes deployment directories not referenced by the loaded active deployment list, cleans bootfs directories and overlay initrds not referenced by bootconfigs, regenerates deployment refs for the active bootversion/subbootversion while deleting refs for inactive versions, then optionally prunes the repository using a reachable set seeded from refs and every active deployment commit. Repository pruning is protected by an exclusive lock. Post-copy update first skips if fs-verity is not wanted, then lists loose objects and ensures fs-verity on each until unsupported, scans all deployments, and ensures fs-verity on each composefs file until unsupported.

State/persistence: deletes filesystem directories under `boot/loader.*`, `ostree/boot.*`, `ostree/deploy/*/deploy/*`, deployment origin/backing paths, bootfs `ostree/<os>-<checksum>` directories, and inactive overlay initrd files. It rewrites repository refs under `ostree/<bootversion>/<subbootversion>/`, prunes repository objects, logs freed space, and may set fs-verity metadata on object and composefs files. It deliberately avoids deleting the currently booted deployment by comparing device/inode to `root_device/root_inode`.

Dependencies/integration: depends on sysroot private state (`sysroot_fd`, `boot_fd`, loaded deployments, bootversion/subbootversion, root inode/device), deployment parsing/path helpers, bootconfig parser overlay initrd access, repo traversal/prune/transactions/locks, libglnx fd iteration and recursive removal, linuxfs immutable flag helper, fs-verity helper, journal logging, and OSTree object path serialization. It is called by `ostree admin cleanup`, deployment transactions, prepare cleanup, and system update flows.

Risks: cleanup is destructive, so correctness of active deployment lists and bootdir/ref parsing is critical. The code assumes higher layers prevent the booted deployment from becoming inactive, but still guards by inode. Orphaned origin/work dirs are only deleted when their deployment path is deleted; standalone orphan detection is noted as absent. Bootfs cleanup borrows overlay initrd basename pointers from bootconfig data into a hash table, so bootconfig lifetime must outlive the table. Ref regeneration and pruning must stay ordered; pruning before deployment refs/reachability are correct could delete live commits. Post-copy fs-verity stops after the first unsupported object/deployment, so mixed filesystem support may leave later files untreated.

Test signals: `tests/test-admin-deploy-2.sh` covers manual admin cleanup, installed destructive staged-deploy tests cover cleanup of staged deployments and refs, `test-prune.sh` and `test-prune-collections.sh` cover prune behavior including refs-only/commit-only/concurrent commit scenarios, basic tests include prune invocations, and installed composefs/fs-verity paths exercise post-copy expectations indirectly. Additional focused tests should simulate inactive bootversion directories, orphan overlay initrds, booted inactive deployment guard, and fs-verity unsupported-after-partial behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sysroot-cleanup.c -->
