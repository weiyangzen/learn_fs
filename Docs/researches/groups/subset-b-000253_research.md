# Research: subset-b-000253

Grouped research report for the assigned OSTree libostree, libotcore, and libotutil sources. Each section preserves the original source path and is wrapped for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sysroot.c -->
# sources/cloud-native/ostree/src/libostree/ostree-sysroot.c

## Purpose
Implements the `OstreeSysroot` GObject, the central libostree object for inspecting and mutating a physical sysroot containing `/ostree/repo`, `/ostree/deploy`, bootloader entries, boot versions, staged deployments, deployment metadata, and deployment lock/unlock state. It bridges persistent deployment layout on disk with runtime state in `/run/ostree*`, bootloader configuration, repository access, locking, mount namespace handling, and convenience write paths.

## Important APIs, Types, And Functions
The file defines the `OstreeSysroot` type, its `path` construct property, and the `journal-msg` signal. Public constructors and lifecycle functions include `ostree_sysroot_new`, `ostree_sysroot_new_default`, `ostree_sysroot_initialize`, `ostree_sysroot_initialize_with_mount_namespace`, `ostree_sysroot_load`, `ostree_sysroot_load_if_changed`, `ostree_sysroot_unload`, `ostree_sysroot_ensure_initialized`, `ostree_sysroot_get_fd`, `ostree_sysroot_get_path`, `ostree_sysroot_is_booted`, and repo accessors `ostree_sysroot_get_repo`/`ostree_sysroot_repo`.

Deployment inspection APIs include `ostree_sysroot_get_bootversion`, `ostree_sysroot_get_subbootversion`, `ostree_sysroot_get_deployments`, `ostree_sysroot_get_booted_deployment`, `ostree_sysroot_require_booted_deployment`, `ostree_sysroot_get_staged_deployment`, `ostree_sysroot_get_deployment_dirpath`, `ostree_sysroot_get_deployment_directory`, `ostree_sysroot_get_deployment_origin_path`, `ostree_sysroot_query_deployments_for`, and `ostree_sysroot_get_merge_deployment`. Mutation APIs include `ostree_sysroot_lock`, `ostree_sysroot_try_lock`, async lock wrappers, `ostree_sysroot_init_osname`, `ostree_sysroot_simple_write_deployment`, `ostree_sysroot_deployment_unlock`, and `ostree_sysroot_deployment_set_pinned`.

Important internal helpers include `ensure_sysroot_fd`, `_ostree_sysroot_ensure_boot_fd`, `_ostree_sysroot_ensure_writable`, `_ostree_sysroot_parse_deploy_path_name`, `_ostree_sysroot_parse_bootlink`, `_ostree_sysroot_read_current_subbootversion`, `_ostree_sysroot_read_boot_loader_configs`, `read_current_bootversion`, `parse_deployment`, `sysroot_load_from_bootloader_configs`, `_ostree_sysroot_reload_staged`, `_ostree_sysroot_reload_soft_reboot`, `_ostree_sysroot_new_deployment_object`, `_ostree_sysroot_query_bootloader`, and `_ostree_sysroot_bump_mtime`.

## Control Flow
Construction records the sysroot `GFile`, falling back to the default sysroot path when none is supplied. Initialization opens the sysroot fd, reads `/run/ostree-booted` metadata if present, records the visible root device/inode, and determines whether this `OstreeSysroot` corresponds to the currently booted root. `ostree_sysroot_initialize_with_mount_namespace` additionally creates or marks a private mount namespace for privileged booted-root mutation.

Loading goes through `ostree_sysroot_load_if_changed`: initialize, ensure the repo is open, stat `ostree/deploy`, short-circuit when its mtime matches the cached timestamp, clear cached deployment state, then call `sysroot_load_from_bootloader_configs`. That loader reads the current `boot/loader` symlink, current `/ostree/boot.N` subboot symlink, soft-reboot metadata, all matching `loader.N/entries/ostree-*.conf` BLS files, and parses each `ostree=` kernel argument into deployments. Parsed deployments are sorted by BLS version, staged deployment state is optionally inserted first, indices are assigned, and booted or soft-reboot target deployments are recognized using recorded backing device/inode data.

Write-related flow first enforces fd availability and, when a private mount namespace is active, remounts `/sysroot` and `/boot` writable before reopening fds. Locking creates an exclusive lock file under the sysroot. `ostree_sysroot_simple_write_deployment` builds a replacement deployment list according to default/retain/pending/rollback/pinned rules, then delegates actual bootloader/deployment writing to lower-level write functions elsewhere. Unlocking duplicates a hotfix rollback when needed, marks a deployment mutable, prepares overlayfs upper/work directories, forks a child to mount `/usr` overlayfs safely without changing process cwd in the library, writes either persistent origin metadata or transient `/run` flags, and bumps deploy mtime.

## State And Persistence Behavior
Persistent state lives in the sysroot tree: `/ostree/repo`, `/ostree/deploy/<osname>/deploy/<checksum>.<serial>`, deployment origin files, `/ostree/boot.N` symlinks, `boot/loader` symlink, BLS entry files, bootloader selection, and pin/unlocked metadata. Runtime state is read from `/run/ostree-booted`, `/run/ostree/nextroot-booted`, staged deployment data, and deployment unlock flag files. The object caches sysroot and boot fds, repo object, boot/subboot versions, deployment arrays, booted/staged/soft-reboot deployments, root device/inode, load timestamps, mount-namespace state, and debug/global option flags from environment variables.

`ostree_sysroot_load_if_changed` relies on `ostree/deploy` mtime as its change detector, and `_ostree_sysroot_bump_mtime` intentionally updates that mtime after meaningful deployment-state changes. Hotfix unlock persists through origin metadata, while development/transient unlocks persist only through `/run` flag files. The code tolerates some incomplete sysroots for compatibility, such as missing `/boot`, but errors on invalid symlink targets, invalid deployment names, missing booted deployment entries, or `/boot` on vfat.

## Dependencies And Integration Points
This file integrates GLib/GObject/GIO, libglnx fd-relative filesystem helpers, Linux mount/statfs/statvfs/unshare/fork/wait APIs, bootloader backends for grub2/syslinux/uboot/aboot/zipl, `OstreeRepo`, `OstreeDeployment`, `OstreeBootconfigParser`, `OstreeKernelArgs`, SELinux policy labeling, systemd journal event emission, and otcore runtime metadata constants. It is a major integration point for command-line admin tools, deployment writing code in neighboring files, boot-complete and soft-reboot flows, and ostree-prepare-root metadata.

## Risks
The code is sensitive to bootloader symlink correctness, deployment directory naming, `/run` metadata versioning, device/inode comparisons across composefs/overlayfs, and mtime-based cache invalidation. Mount namespace handling and remounts require privilege and can fail in constrained containers. Unlocking uses fork plus mount and must avoid GLib in the child. `OstreeTlsCertInteraction`-style memory leaks are not relevant here, but sysroot object lifetime still depends on clearing cached GObjects and releasing locks. The repo/device same-filesystem check is important because later hardlink and sync assumptions depend on it.

## Test Signals
Useful tests include loading sysroots with and without `/boot`, invalid `boot/loader` and `/ostree/boot.N` symlinks, sorted BLS entries, staged deployment serialization round trips, soft-reboot metadata cleanup, booted deployment detection with backing device/inode metadata, mount namespace remount behavior, lock contention, deployment retain flag matrices, hotfix/development/transient unlock behavior, pin origin updates, and mtime cache behavior for `ostree_sysroot_load_if_changed`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sysroot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sysroot.h -->
# sources/cloud-native/ostree/src/libostree/ostree-sysroot.h

## Purpose
Public libostree API declaration for `OstreeSysroot`, the object used to inspect, lock, initialize, load, write, stage, deploy, unlock, pin, cleanup, and soft-reboot OSTree sysroots.

## Important APIs, Types, And Functions
The header exposes `OSTREE_PATH_BOOTED`, `OSTREE_TYPE_SYSROOT`, type-check macros, and `ostree_sysroot_get_type`. It declares constructors, initialization/loading APIs, fd/path accessors, deployment getters, repo accessors, locking APIs, cleanup APIs, origin writing, kernel argument mutation, deployment writing, overlay initrd staging, deploy/stage tree APIs, finalization, mutable/pinned/unlocked state APIs, deployment query helpers, post-copy update, simple write flags, and soft-reboot/kexec functions.

Important public option types are `OstreeSysrootWriteDeploymentsOpts`, `OstreeSysrootDeployTreeOpts`, and `OstreeSysrootSimpleWriteDeploymentFlags`. The option structs reserve unused bool/int/pointer fields for ABI-compatible growth.

## Control Flow
Consumers generally create a sysroot, initialize or load it, acquire the lock for mutation, use repo/deployment APIs to compute changes, then call deploy/stage/write helpers and cleanup. Read-only callers load and query deployments. Staging and deployment APIs accept origins, merge deployments, kernel argv overrides, overlay initrds, and locking options.

## State And Persistence Behavior
The header does not implement state, but it defines which persistent sysroot concepts are externally mutable: deployment lists, origins, bootloader state, staged deployment data, pinning, unlock mode, cleanup/prune state, and soft reboot metadata. Public APIs imply caller responsibility for ordering and locking around persistent mutations.

## Dependencies And Integration Points
It includes `ostree-deployment.h` and `ostree-repo.h`, exposing `GFile`, `GPtrArray`, `GKeyFile`, `GCancellable`, and `GError` integration. It is consumed by admin tools and other libostree modules that need stable ABI access to sysroot functionality.

## Risks
The API surface is broad and ABI-stable, so option struct layout and enum values must be preserved. Many functions require prior load/initialize or a loaded deployment list; callers can misuse them if lifecycle requirements are ignored. Locking is advisory but essential for multi-process mutation safety.

## Test Signals
Header-level tests are indirect: ABI/API checks, introspection generation, compile coverage for public declarations, option struct compatibility, and behavioral tests against the implementations declared here.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sysroot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-tls-cert-interaction-private.h -->
# sources/cloud-native/ostree/src/libostree/ostree-tls-cert-interaction-private.h

## Purpose
Private declaration for an OSTree-specific `GTlsInteraction` subclass that supplies a client certificate and key to a TLS connection on demand.

## Important APIs, Types, And Functions
The header defines `OSTREE_TYPE_TLS_CERT_INTERACTION`, cast/check macros, opaque `OstreeTlsCertInteraction` and class typedefs, an autoptr cleanup function, `_ostree_tls_cert_interaction_get_type`, and `_ostree_tls_cert_interaction_new(cert_path, key_path)`.

## Control Flow
Callers create the interaction with certificate and key paths, attach it to TLS-enabled GIO/Soup networking machinery, and the implementation responds when a certificate is requested by the TLS connection.

## State And Persistence Behavior
The header only describes an object that stores certificate/key paths and, in the implementation, lazily caches a `GTlsCertificate`. It does not write persistent state.

## Dependencies And Integration Points
It depends on `otutil.h` and GIO TLS types. The file is private, intended for internal libostree networking code that needs mTLS support without exposing this helper as public API.

## Risks
Because the type is private, ABI risks are low, but macro correctness matters. Credential path lifetime and certificate loading errors are implementation-sensitive.

## Test Signals
Compile tests should ensure the private type is available where needed. Behavioral tests should verify client certificate selection succeeds with valid cert/key files and fails cleanly with invalid paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-tls-cert-interaction-private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-tls-cert-interaction.c -->
# sources/cloud-native/ostree/src/libostree/ostree-tls-cert-interaction.c

## Purpose
Implements the private `OstreeTlsCertInteraction` `GTlsInteraction` subclass used to lazily load a client certificate/key pair and install it on a `GTlsConnection` when the peer requests a certificate.

## Important APIs, Types, And Functions
The instance stores `cert_path`, `key_path`, and cached `GTlsCertificate *cert`. `request_certificate` is the key virtual method: it calls `g_tls_certificate_new_from_files` the first time, stores the result, and sets it on the connection. `_ostree_tls_cert_interaction_new` allocates the object and duplicates the path strings.

## Control Flow
Creation records the two paths. During TLS negotiation, GIO invokes `request_certificate`; the method loads and caches the certificate if needed, returns `G_TLS_INTERACTION_FAILED` on load failure, otherwise sets the certificate and returns `G_TLS_INTERACTION_HANDLED`.

## State And Persistence Behavior
State is in-memory only. The loaded `GTlsCertificate` is cached across repeated requests for the lifetime of the interaction. The code reads cert/key files but does not write or persist anything.

## Dependencies And Integration Points
Depends on GIO TLS APIs and the private header. It plugs into libostree HTTP/TLS clients that need client certificate authentication.

## Risks
The implementation as shown does not define a finalize method to free `cert_path`, `key_path`, or unref `cert`, so repeated construction can leak memory. It does not reload changed certificate files after the first successful request. Errors from invalid key/cert pairs propagate through the TLS interaction result.

## Test Signals
Tests should exercise valid cert/key loading, invalid file handling, repeated certificate requests using the cached certificate, and object destruction under leak checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-tls-cert-interaction.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-types.h -->
# sources/cloud-native/ostree/src/libostree/ostree-types.h

## Purpose
Central forward-declaration header for libostree public and semi-public object types, avoiding include cycles across the large API surface.

## Important APIs, Types, And Functions
It defines `_OSTREE_PUBLIC` as `extern` when not already provided and forward declares `OstreeRepo`, `OstreeRepoDevInoCache`, `OstreeSePolicy`, `OstreeSysroot`, `OstreeSysrootUpgrader`, `OstreeMutableTree`, `OstreeRepoFile`, `_OstreeContentWriter`, `OstreeRemote`, and `_OstreeKernelArgs`.

## Control Flow
There is no runtime control flow. The file is included by headers needing pointer types without full definitions.

## State And Persistence Behavior
No state is stored. Its role is compile-time type sharing.

## Dependencies And Integration Points
Depends only on GIO and GLib declarations. It is a foundational integration header for libostree public headers, introspection, and consumers compiling against opaque object pointers.

## Risks
Changing typedef names or `_OSTREE_PUBLIC` handling can break ABI headers and generated bindings. Forward declarations must match real struct tags exactly.

## Test Signals
Compile coverage across public headers, introspection generation, and downstream build tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-varint.c -->
# sources/cloud-native/ostree/src/libostree/ostree-varint.c

## Purpose
Provides internal unsigned 64-bit varint encoding and decoding helpers derived from protocol-buffer varint logic for compact binary metadata formats.

## Important APIs, Types, And Functions
`_ostree_read_varuint64(buf, buflen, out_value, bytes_read)` decodes up to ten bytes into a `guint64`. `_ostree_write_varuint64(buf, n)` appends the varint representation of `n` to a `GString`. `max_varint_bytes` is fixed at 10, the maximum for 64-bit varints.

## Control Flow
Decoding loops byte by byte, stops when the high continuation bit is clear, returns false if the buffer ends or exceeds 10 bytes, and writes the decoded value and byte count on success. Encoding splits the input into 32-bit chunks, chooses an output size through a hardcoded decision tree, fills a 10-byte temporary array through fallthrough labels, clears the continuation bit on the last byte, and appends the chosen bytes.

## State And Persistence Behavior
The functions are stateless. Encoded bytes may be persisted by callers in repository or delta metadata, so compatibility of the varint representation matters.

## Dependencies And Integration Points
Depends on GLib `GString` and integer types. It is internal to libostree metadata encoding/decoding paths.

## Risks
Malformed varints return `FALSE` without distinguishing truncated from overlong encodings. The writer intentionally uses fallthrough labels, so compiler warnings or refactors must preserve ordering. The functions encode unsigned values only; signed callers need separate zigzag or other handling.

## Test Signals
Round-trip tests for boundary values, small numbers, 2/3/4/5/8/9/10-byte encodings, truncated buffers, all-continuation malformed buffers, and maximum `G_MAXUINT64` are the strongest signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-varint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-varint.h -->
# sources/cloud-native/ostree/src/libostree/ostree-varint.h

## Purpose
Internal header declaring libostree varint read/write helpers.

## Important APIs, Types, And Functions
Declares `_ostree_read_varuint64` and `_ostree_write_varuint64` under `G_BEGIN_DECLS`/`G_END_DECLS`.

## Control Flow
No runtime flow exists in the header. It provides prototypes for code needing compact unsigned integer serialization.

## State And Persistence Behavior
No state is stored. The declarations expose functions whose output may participate in persistent binary formats.

## Dependencies And Integration Points
Depends on GIO/GLib types, particularly `guint8`, `guint64`, `gsize`, `gboolean`, and `GString`.

## Risks
Changing signatures would affect all internal users. The API does not expose a maximum-length constant, so callers must rely on implementation behavior or allocate conservatively.

## Test Signals
Compile coverage plus implementation round-trip tests cover this header.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-varint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-version.h.in -->
# sources/cloud-native/ostree/src/libostree/ostree-version.h.in

## Purpose
Meson/configure template for generated libostree compile-time version macros and configured feature strings.

## Important APIs, Types, And Functions
Defines `OSTREE_YEAR_VERSION`, `OSTREE_RELEASE_VERSION`, `OSTREE_VERSION`, `OSTREE_VERSION_S`, `OSTREE_ENCODE_VERSION(year, release)`, `OSTREE_VERSION_HEX`, `OSTREE_CHECK_VERSION(year, release)`, and `OSTREE_BUILT_FEATURES`.

## Control Flow
No runtime control flow. Build substitution fills `@YEAR_VERSION@`, `@RELEASE_VERSION@`, `@VERSION@`, and `@OSTREE_FEATURES@`. Consumers use the macros in preprocessor or compile-time comparisons.

## State And Persistence Behavior
No runtime state. It records build-time version and feature information into installed headers, affecting downstream conditional compilation and diagnostics.

## Dependencies And Integration Points
Integrated with the build system and public libostree headers. `OSTREE_BUILT_FEATURES` is hidden from GI scanner to avoid introspection issues with a free-form feature string.

## Risks
Incorrect substitution breaks public version reporting and downstream `OSTREE_CHECK_VERSION` guards. Year/release encoding assumes values fit in the bit packing used by `OSTREE_ENCODE_VERSION`.

## Test Signals
Build-system tests, installed-header compile tests, and checks that `ostree --version`/library headers agree on features and version are useful signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-version.h.in -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree.h -->
# sources/cloud-native/ostree/src/libostree/ostree.h

## Purpose
Primary public umbrella header for libostree consumers.

## Important APIs, Types, And Functions
It includes public headers for async progress, bootconfig parsing, content writing, core objects, deployments, diffs, GPG verify results, kernel args, mutable trees, refs, remotes, repo files, repo finders, repo OS APIs, repo APIs, signing, sysroot upgrader, sysroot APIs, version macros, and autocleanup support.

## Control Flow
No runtime control flow. Inclusion order matters: `ostree-autocleanups.h` is included after type definitions.

## State And Persistence Behavior
No state is stored. It exposes the full public API surface for repository and sysroot persistence operations implemented elsewhere.

## Dependencies And Integration Points
Downstream applications include this header to access libostree. It coordinates installed header layout and depends on all referenced public headers being available and self-consistent.

## Risks
Adding/removing includes changes what downstream code can compile with a single include. Include ordering can affect autocleanup declarations and opaque type visibility.

## Test Signals
Installed-header compile tests, GI scanner runs, and downstream sample builds are the relevant signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotcore/otcore-ed25519-verify.c -->
# sources/cloud-native/ostree/src/libotcore/otcore-ed25519-verify.c

## Purpose
Implements ed25519 signature-verification support for otcore, using libsodium when available or OpenSSL otherwise.

## Important APIs, Types, And Functions
`otcore_ed25519_init` initializes libsodium once when compiled with libsodium and is otherwise a no-op success. `otcore_validate_ed25519_signature(data, public_key, signature, out_valid, error)` validates one detached signature over a `GBytes` payload.

## Control Flow
Initialization uses `g_once_init_enter/leave` to cache success or failure of `sodium_init`. Verification asserts non-null inputs, validates public key and signature lengths when a crypto backend exists, then calls `crypto_sign_verify_detached` or OpenSSL `EVP_DigestVerifyInit`/`EVP_DigestVerify`. Invalid signatures return success with `*out_valid` left false; malformed inputs or unavailable support return errors.

## State And Persistence Behavior
Only process-global libsodium init state is cached. The function reads in-memory commit or metadata bytes and does not persist anything.

## Dependencies And Integration Points
Depends on compile-time `HAVE_LIBSODIUM` and `HAVE_OPENSSL`, otcore signature constants, GLib `GBytes`, GError helpers, and OpenSSL EVP APIs. It is used by composefs/commit signature validation paths.

## Risks
Callers must initialize or set `*out_valid` expectations carefully; the function only sets it true on success and relies on caller-initialized false. Builds without libsodium or OpenSSL cannot validate signatures. Error text has a typo in a comment only; behavior is unaffected.

## Test Signals
Known-good and known-bad signatures, wrong key/signature lengths, no-backend builds, libsodium initialization failure simulation, and OpenSSL backend coverage are important.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotcore/otcore-ed25519-verify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotcore/otcore-prepare-root.c -->
# sources/cloud-native/ostree/src/libotcore/otcore-prepare-root.c

## Purpose
Implements shared early-boot root preparation helpers: parse kernel command lines, load prepare-root config, determine OSTree boot targets, mount `/boot`, mount `/etc`, and optionally mount composefs-backed root filesystems with verity/signature validation and runtime metadata emission.

## Important APIs, Types, And Functions
Public functions are `otcore_find_proc_cmdline_key`, `otcore_get_ostree_target`, `otcore_load_config`, `otcore_free_rootfs_config`, `otcore_load_rootfs_config`, `otcore_mount_boot`, `otcore_mount_etc`, and `otcore_mount_rootfs`. Internal composefs-enabled helpers include `load_variant`, `get_base_digest_for_bootc_commit`, `load_commit_for_deploy`, `validate_signature`, and `composefs_error_message`.

## Control Flow
Cmdline parsing scans space-separated arguments for exact `key=` matches or Android boot keys. `otcore_get_ostree_target` prefers Android A/B slot information, falls back to non-A/B Android default, then to the normal `ostree=` argument. `otcore_load_config` overlays config from `usr/lib/<filename>` and `etc/<filename>`. `otcore_load_rootfs_config` reads root transient flags, composefs mode (`true`, `false`, `maybe`, `verity`, `signed`), key path, optional public keys, and cmdline overrides.

`otcore_mount_boot` bind-mounts physical `/boot` into a deployment only when `/boot/loader` shows boot is on the physical root and the deployment has a `boot` directory. `otcore_mount_etc` either creates a transient overlay for `/etc` backed by `/run/ostree/transient-etc.*` or bind-remounts deployment `etc` writable. `otcore_mount_rootfs` records the backing deployment device/inode and root transient flags, then if composefs is compiled and enabled it prepares libcomposefs options, optional transient upper/work dirs, validates ed25519 commit signatures and composefs digest when requested, mounts `.ostree.cfs`, records composefs metadata, or tolerates a missing image only in `maybe` mode.

## State And Persistence Behavior
The code reads `/proc/cmdline`-style input, config from deployment `usr/lib` and `etc`, public key files, and OSTree commit/commitmeta objects. It writes no durable config, but creates runtime mount state, `/run/ostree` temporary overlay directories, private composefs lower mount directories, and metadata entries such as backing root device/inode, composefs usage, verity, signature key, transient root, transient-ro root, and transient `/etc` path.

## Dependencies And Integration Points
Integrates with GLib key files and variants, libglnx, Linux mount API, OSTree commit object formats, otcore ed25519 verification, libcomposefs when compiled, bootc commit metadata conventions, Android boot command-line conventions, and ostree-prepare-root/boot-complete runtime metadata consumers.

## Risks
This code runs in sensitive early-boot contexts. Incorrect cmdline parsing can choose the wrong deployment. Transient root and transient-ro are mutually exclusive except that transient-ro implies transient. Composefs signature validation requires commitmeta and public keys; bootc-imported commits may require base commit fallback. Mount failures can leave partial runtime directories. `load_variant` reads object files directly and assumes correct object path/digest conventions without linking libostree.

## Test Signals
Tests should cover cmdline parsing for normal OSTree, Android A/B, non-A/B Android, invalid slot suffixes, config precedence, composefs mode parsing and cmdline overrides, missing/empty public key files, good/bad ed25519 signatures, bootc base commit fallback, missing composefs image in maybe/yes modes, transient root directory creation, `/etc` overlay metadata, and `/boot` bind-mount conditions.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotcore/otcore-prepare-root.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotcore/otcore-spki-verify.c -->
# sources/cloud-native/ostree/src/libotcore/otcore-spki-verify.c

## Purpose
Implements SPKI signature verification using OpenSSL for otcore signing support.

## Important APIs, Types, And Functions
`otcore_spki_init` is an idempotent no-op success. `otcore_validate_spki_signature(data, public_key, signature, out_valid, error)` validates a signature using a DER SubjectPublicKeyInfo public key parsed by OpenSSL `d2i_PUBKEY`.

## Control Flow
The verifier asserts input pointers, checks public key and signature sizes against `OSTREE_SIGN_MAX_METADATA_SIZE`, creates an `EVP_MD_CTX`, parses the public key, and runs `EVP_DigestVerifyInit` plus `EVP_DigestVerify`. A valid signature sets `*out_valid = true`; invalid signatures return success with false. Builds without OpenSSL return a hard error.

## State And Persistence Behavior
No persistent state. All inputs are in-memory `GBytes`.

## Dependencies And Integration Points
Depends on OpenSSL EVP/X509 APIs, otcore signature size constants, GLib, and libglnx errors. It supports signature types declared in `otcore.h` and used by higher-level repository verification paths.

## Risks
As with ed25519, callers must initialize `out_valid` to false. Large but under-limit malformed DER inputs rely on OpenSSL parse behavior. No alternative backend exists when OpenSSL is unavailable.

## Test Signals
Good/bad SPKI signatures, malformed DER public keys, oversize public key/signature inputs, no-OpenSSL build behavior, and invalid-signature-without-error behavior are key signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotcore/otcore-spki-verify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotcore/otcore.h -->
# sources/cloud-native/ostree/src/libotcore/otcore.h

## Purpose
Private/shared otcore header for signature constants, crypto verification APIs, prepare-root helpers, root configuration, mount helpers, and runtime path/metadata constants.

## Important APIs, Types, And Functions
Defines ed25519 and SPKI signature metadata keys and variant types, ed25519 public key/signature sizes, max metadata size, `otcore_ed25519_init`, `otcore_validate_ed25519_signature`, `otcore_spki_init`, `otcore_validate_spki_signature`, command-line/config helpers, `RootConfig`, `otcore_load_rootfs_config`, `otcore_mount_rootfs`, `otcore_mount_boot`, and `otcore_mount_etc`.

The header also defines runtime and layout constants: `/run/ostree`, `/run/ostree/.private`, `PREPARE_ROOT_CONFIG_PATH`, deployment backing and overlay directory names, composefs names and lower mount path, prepare-root config keys, `/run/nextroot`, `/run/ostree-booted`, `/run/ostree/nextroot-booted`, and metadata keys for composefs, verity, signatures, transient roots, sysroot-ro, backing root device/inode, and transient `/etc`.

## Control Flow
No implementation flow is present, but it documents the call sequence used by prepare-root: parse cmdline/config into `RootConfig`, mount rootfs, mount boot, mount `/etc`, and publish runtime metadata for later sysroot/load code.

## State And Persistence Behavior
`RootConfig` owns composefs and transient-root settings plus signature key paths and loaded public keys. Constants describe transient `/run` state and deployment backing directories that must remain stable across prepare-root, sysroot, unlock, boot-complete, and soft-reboot code.

## Dependencies And Integration Points
Conditionally includes libsodium and OpenSSL headers, uses GLib/GIO, libglnx/otutil, and is included by libotcore sources and libostree sysroot code that consumes runtime metadata constants.

## Risks
Changing metadata key strings or paths breaks cross-component handoff. `RootConfig` ownership must match `otcore_free_rootfs_config`. Compile-time crypto feature macros select available signature backends.

## Test Signals
Compile coverage across feature combinations, metadata key compatibility tests, prepare-root/sysroot integration tests, and memory ownership tests for `RootConfig` are useful.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotcore/otcore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-checksum-instream.c -->
# sources/cloud-native/ostree/src/libotutil/ot-checksum-instream.c

## Purpose
Implements `OtChecksumInstream`, a `GFilterInputStream` that updates a SHA256 checksum as bytes are read from an underlying stream.

## Important APIs, Types, And Functions
The private struct contains an `OtChecksum`. `ot_checksum_instream_new` creates a SHA256 checksum stream. `ot_checksum_instream_new_with_start` optionally seeds the checksum with initial bytes. `ot_checksum_instream_read` proxies reads and updates the checksum for positive byte counts. `ot_checksum_instream_get_string` returns the final hex digest.

## Control Flow
Construction validates the base stream, initializes the checksum, and optionally updates with a prefix. Reads delegate to the base stream and update the checksum with the returned buffer. Finalization clears the checksum. Calling `get_string` finalizes the checksum through `ot_checksum_get_hexdigest`.

## State And Persistence Behavior
State is in-memory checksum context plus the base stream reference managed by `GFilterInputStream`. It does not persist data, but callers use its digest to identify or verify persisted objects.

## Dependencies And Integration Points
Depends on GObject, GIO stream classes, `ot-checksum-utils`, and SHA256 constants. It integrates into code paths that need streaming reads and checksums without buffering whole files.

## Risks
Only SHA256 is currently accepted via assertion. Fetching the digest closes the underlying checksum context, so further reads/checksum updates after `get_string` are invalid. Error propagation is exactly the base stream read error.

## Test Signals
Read-through tests comparing digest against known SHA256, seeded-prefix tests, short reads, read errors, finalization leak checks, and misuse tests around digest-before-finish are useful.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-checksum-instream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-checksum-instream.h -->
# sources/cloud-native/ostree/src/libotutil/ot-checksum-instream.h

## Purpose
Declares the `OtChecksumInstream` GObject type and constructors/accessors for checksum-filtered input streams.

## Important APIs, Types, And Functions
Defines type macros, instance/class structs, private pointer, `ot_checksum_instream_get_type`, `ot_checksum_instream_new`, `ot_checksum_instream_new_with_start`, and `ot_checksum_instream_get_string`.

## Control Flow
No runtime flow in the header. Consumers construct a stream, read through it, then request the checksum string.

## State And Persistence Behavior
Declares an instance containing private checksum state and inherited filter-stream state. No persistent state is declared.

## Dependencies And Integration Points
Depends on GIO. The macro definitions appear to reference `OT_TYPE_CHECKSUM_INPUT_STREAM` while the type macro is `OT_TYPE_CHECKSUM_INSTREAM`; that mismatch is a header risk unless hidden by lack of macro use or compatibility definitions elsewhere.

## Risks
The type macro mismatch can break code using the cast/check macros. The API does not document that only SHA256 is supported or that retrieving the digest finalizes checksum state.

## Test Signals
Compile tests using each macro, GObject type registration tests, and implementation digest tests cover this header.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-checksum-instream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-checksum-utils.c -->
# sources/cloud-native/ostree/src/libotutil/ot-checksum-utils.c

## Purpose
Provides SHA256 checksum primitives and stream/file helper functions, abstracting over OpenSSL, GnuTLS, or GLib checksum implementations.

## Important APIs, Types, And Functions
`ot_bin2hex` converts bytes to lowercase hex. `OtRealChecksum` backs public `OtChecksum`. Core functions are `ot_checksum_init`, `ot_checksum_update`, `ot_checksum_get_digest`, `ot_checksum_get_hexdigest`, `ot_checksum_clear`, `ot_csum_from_gchecksum`, `ot_gio_write_update_checksum`, `ot_gio_splice_update_checksum`, `ot_gio_splice_get_checksum`, `ot_checksum_file_at`, and `ot_checksum_bytes`.

## Control Flow
Initialization selects the compiled crypto backend and asserts SHA256 digest length. Update feeds bytes to the backend. Getting a digest finalizes the backend and marks the checksum closed. Splice helpers either manually read/write in 4 KiB chunks while updating a checksum or delegate to `g_output_stream_splice` when no checksum is requested. File checksum opens an fd-relative read stream, splices into a checksum, and returns a hex string.

## State And Persistence Behavior
Checksum state is stack- or object-owned and transient. Digests produced here are used as persistent object identifiers and verification values by callers.

## Dependencies And Integration Points
Depends on OpenSSL EVP, GnuTLS hash APIs, or GLib `GChecksum`, plus GIO streams and libglnx file helpers. It is a core utility for repository object hashing and content validation.

## Risks
`ot_checksum_get_digest`/`get_hexdigest` close the checksum; updating afterward is invalid. `ot_gio_splice_update_checksum` uses `g_input_stream_read_all`, so it loops until a full buffer or EOF and must handle short EOF correctly. `ot_checksum_file_at` ignores the `checksum_type` argument in practice because only SHA256 is implemented.

## Test Signals
Known SHA256 vectors, backend parity tests, write/splice checksum agreement, NULL output stream checksum-only mode, fd-relative file checksums, empty input handling, and update-after-finalize assertions are useful.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-checksum-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-checksum-utils.h -->
# sources/cloud-native/ostree/src/libotutil/ot-checksum-utils.h

## Purpose
Declares checksum utility APIs and the ABI-sized `OtChecksum` storage wrapper.

## Important APIs, Types, And Functions
Defines `_OSTREE_SHA256_DIGEST_LEN`, `_OSTREE_SHA256_STRING_LEN`, `OtChecksum`, cleanup support, `ot_bin2hex`, `ot_csum_from_gchecksum`, checksum init/update/digest/hex/clear APIs, `ot_checksum_update_bytes`, GIO write/splice checksum helpers, `ot_checksum_file_at`, and `ot_checksum_bytes`.

## Control Flow
No runtime flow. The inline `ot_checksum_update_bytes` extracts data from `GBytes` and delegates to `ot_checksum_update`.

## State And Persistence Behavior
`OtChecksum` is an opaque fixed-size struct large enough for the backend-specific implementation. Size assertions in the implementation enforce storage compatibility.

## Dependencies And Integration Points
Depends on `libglnx.h`, GLib/GIO stream types, and OSTree SHA256 constants when available. It is widely shared by libostree and otcore code.

## Risks
The fixed storage size must remain large enough for `OtRealChecksum`; backend changes can silently require size updates. The header exposes only SHA256-sized constants despite taking `GChecksumType` in one API.

## Test Signals
Compile checks across crypto feature combinations, static assertion coverage, and known-vector tests through all declared APIs are relevant.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-checksum-utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-fs-utils.c -->
# sources/cloud-native/ostree/src/libotutil/ot-fs-utils.c

## Purpose
Provides fd-relative filesystem helpers for converting paths, opening streams, tolerating missing files, mmap/read-all behavior, temporary file mapping, line parsing, and directory size calculation.

## Important APIs, Types, And Functions
Functions include `ot_fdrel_to_gfile`, `ot_readlinkat_gfile_info`, `ot_openat_read_stream`, `ot_ensure_unlinked_at`, `ot_openat_ignore_enoent`, `ot_dfd_iter_init_allow_noent`, `ot_fd_readall_or_mmap`, `ot_map_anonymous_tmpfile_from_content`, `ot_parse_file_by_line`, and `ot_get_dir_size`. `MapData` plus `map_data_destroy` owns mmap cleanup for `GBytes`.

## Control Flow
Most helpers wrap one syscall/libglnx operation and convert errors to `GError`. `ot_fd_readall_or_mmap` stats the file, returns empty bytes if the offset is beyond EOF, mmaps files larger than 16 KiB from the requested offset, or seeks and reads small files into memory. `ot_get_dir_size` recursively iterates directories, sums regular file sizes, and optionally rounds each file to a block-size multiple.

## State And Persistence Behavior
No persistent state is written except temporary anonymous files in `ot_map_anonymous_tmpfile_from_content`. Helpers operate fd-relative to reduce path races and support sysroot/repo code.

## Dependencies And Integration Points
Depends on libglnx, GIO Unix streams, mmap, xattrs include availability, and Unix fd APIs. It is used by sysroot, repo, static delta, and metadata code.

## Risks
`ot_openat_ignore_enoent` leaves `errno` meaningful to callers only indirectly and returns fd `-1` for missing files. `ot_fd_readall_or_mmap` uses `mmap` with an offset that must be page-aligned on many systems; callers passing arbitrary offsets may see `EINVAL`. Recursive size calculation does not follow symlinks but can still be expensive on large trees.

## Test Signals
Tests should cover missing file handling, symlink read info, follow/no-follow stream opens, mmap and small-read paths, offset beyond EOF, anonymous tmpfile mapping, line callback errors, directory recursion, and block rounding.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-fs-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-fs-utils.h -->
# sources/cloud-native/ostree/src/libotutil/ot-fs-utils.h

## Purpose
Declares fd-relative filesystem utility APIs and a cleanup helper for temporary unlink-at paths.

## Important APIs, Types, And Functions
Defines `OtCleanupUnlinkat`, `ot_cleanup_unlinkat_clear`, `ot_cleanup_unlinkat`, and cleanup macro support. Declares fd/path conversion, readlink-to-`GFileInfo`, open-read-stream, unlink-ignore-missing, open-ignore-missing, directory iterator allow-noent, anonymous tmpfile mapping, fd read/mmap, line parsing, and directory size APIs.

## Control Flow
The inline cleanup function calls `unlinkat` when a path is registered, then clears ownership. Other functions are declared only.

## State And Persistence Behavior
`OtCleanupUnlinkat` stores a directory fd and path to remove during cleanup. The declared APIs manipulate filesystem state but the header itself stores no global state.

## Dependencies And Integration Points
Depends on libglnx and `ot-unix-utils.h`, exposing Unix fd semantics to higher-level OSTree code.

## Risks
Cleanup ignores unlink errors, which is appropriate for best-effort temporary cleanup but can hide unexpected persistence. Callers must keep the directory fd valid for the cleanup lifetime.

## Test Signals
Compile tests for cleanup macros and behavioral tests in the implementation cover the header.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-fs-utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-gio-utils.c -->
# sources/cloud-native/ostree/src/libotutil/ot-gio-utils.c

## Purpose
Provides small GIO convenience helpers for path resolution, fsyncing file replacement, unlink-ignore-missing, portable enumerator iteration, cached `GFile` paths, and human-readable duration formatting.

## Important APIs, Types, And Functions
Functions include `ot_gfile_resolve_path_printf`, `ot_gfile_replace_contents_fsync`, `ot_gfile_ensure_unlinked`, compatibility `ot_file_enumerator_iterate` for older GLib, `ot_file_get_path_cached`, and `ot_format_human_duration`.

## Control Flow
Path resolution formats a relative path and resolves it against a `GFile`. Replace uses `glnx_file_replace_contents_at` with datasync. Ensure-unlinked calls `unlink` and ignores `ENOENT`. The old-GLib enumerator implementation fetches the next file and caches info/child via object qdata. Path caching uses a static quark and a global lock to memoize `g_file_get_path`. Duration formatting chooses ns, ms, or seconds based on thresholds.

## State And Persistence Behavior
Persistent writes happen through fsyncing replacement and unlink helpers. Path caching stores qdata on `GFile` objects, and the cache is protected by a static lock.

## Dependencies And Integration Points
Depends on GIO, Unix input/output stream includes, libglnx, and GLib version checks. It supports legacy code paths and common file operations across libostree.

## Risks
`ot_file_get_path_cached` returns `NULL` for non-native `GFile`s, so callers must not assume all `GFile`s have paths. Cached paths reflect the object path, not filesystem renames. Duration formatting names a variable `ms` but divides nanoseconds by 1000, which is actually microseconds; tests may expose misleading labels.

## Test Signals
Tests should cover datasync replacement, unlink missing/existing files, cached path behavior and non-native files, enumerator compatibility where applicable, and duration thresholds.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-gio-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-gio-utils.h -->
# sources/cloud-native/ostree/src/libotutil/ot-gio-utils.h

## Purpose
Declares GIO helper APIs and common fast query-info attribute strings.

## Important APIs, Types, And Functions
Defines `OSTREE_GIO_FAST_QUERYINFO`, declares path formatting, fsync replace, unlink-ignore-missing, enumerator iteration compatibility wrapper, `ot_file_get_path_cached`, alias `gs_file_get_path_cached`, and `ot_format_human_duration`.

## Control Flow
The GLib 2.44+ inline wrapper delegates to GLib's `g_file_enumerator_iterate` while suppressing deprecation warnings, then redefines `g_file_enumerator_iterate` to the local wrapper name.

## State And Persistence Behavior
No global state in the header. Declared functions may cache paths or write files.

## Dependencies And Integration Points
Depends on GIO and GLib version macros. The fast query string is used anywhere OSTree needs cheap metadata without opening files.

## Risks
The macro redefinition of `g_file_enumerator_iterate` can surprise code that expects the raw GLib symbol. The fast query string must remain synchronized with metadata needs.

## Test Signals
Compile coverage across GLib versions and metadata-query tests using `OSTREE_GIO_FAST_QUERYINFO` are useful.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-gio-utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-gpg-utils.c -->
# sources/cloud-native/ostree/src/libotutil/ot-gpg-utils.c

## Purpose
Provides GPGME integration helpers: error translation, temporary homedir/keyring setup, GIO stream adapters for GPGME data, context creation, legacy gpg-agent cleanup, and OpenPGP Web Key Directory URL generation.

## Important APIs, Types, And Functions
Public functions are `ot_gpgme_throw`, `ot_gpgme_ctx_tmp_home_dir`, `ot_gpgme_data_input`, `ot_gpgme_data_output`, `ot_gpgme_new_ctx`, `ot_gpgme_kill_agent`, and `ot_gpg_wkd_urls`. Internal callbacks map GPGME reads/writes/seeks/releases to `GInputStream`/`GOutputStream` and convert `GError` codes back to `errno`. `encode_wkd_local` computes SHA1 of the local email part and zbase32-encodes it.

## Control Flow
`ot_gpgme_throw` maps selected GPGME errors to `G_IO_ERROR` values and prefixes messages. Temporary homedir creation uses `mkdtemp`, configures the GPGME engine homedir, optionally creates `pubring.gpg`, and cleans up on failure. Data wrapper creation installs callback tables and refs the underlying stream until release. Context creation wraps `gpgme_new` and optional homedir selection. Agent cleanup skips GnuPG >= 2.1.17 and otherwise spawns `gpg-connect-agent --homedir ... killagent /bye`. WKD URL generation validates exactly one `@`, lowercases for hashing/domain path, escapes the original local part, and returns advanced/direct URLs.

## State And Persistence Behavior
Creates temporary GPG homedir directories and optional keyring files under the system temp dir. It may spawn and kill gpg-agent processes tied to a homedir. Stream wrappers hold references until GPGME releases them. WKD generation is stateless.

## Dependencies And Integration Points
Depends on GPGME, GIO streams, libglnx, zbase32, GLib checksums, URI escaping, and process spawning. Used by OSTree GPG signature verification and key retrieval flows.

## Risks
Temporary homedirs must be removed by callers after success; this file only cleans up on setup failure. `g_output_stream_flush` is attempted after writes and any flush error causes a write failure. Version parsing for GnuPG assumes at least three dotted components when available. WKD validation is simple and does not fully validate email syntax beyond one `@`.

## Test Signals
Tests should cover GPGME error mapping, temporary homedir cleanup on failure, stream read/write/seek callbacks, non-seekable streams, context homedir selection, agent cleanup command behavior with mocked versions, and WKD URL vectors.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-gpg-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-gpg-utils.h -->
# sources/cloud-native/ostree/src/libotutil/ot-gpg-utils.h

## Purpose
Declares GPGME helper APIs and cleanup macros for GPGME objects.

## Important APIs, Types, And Functions
Defines auto cleanup functions for `gpgme_data_t`, `gpgme_ctx_t`, and `gpgme_key_t`. Declares error translation, temporary homedir setup, GIO stream data adapters, context creation, agent cleanup, and WKD URL generation.

## Control Flow
No implementation flow beyond cleanup macro definitions. Consumers can use `g_auto` with GPGME types to ensure release functions run.

## State And Persistence Behavior
No state in the header. Declared APIs can create temporary homedirs and manage GPGME resources.

## Dependencies And Integration Points
Depends on libglnx, GIO, and GPGME. It is included by GPG verification and key-management code.

## Risks
Cleanup macros require correct null sentinel handling. GPGME type ownership must match whether functions return borrowed or owned handles.

## Test Signals
Compile tests with `g_auto` declarations and implementation tests for declared functions are relevant.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-gpg-utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-keyfile-utils.c -->
# sources/cloud-native/ostree/src/libotutil/ot-keyfile-utils.c

## Purpose
Provides helper functions for reading `GKeyFile` values with defaults, parsing booleans/tristates, reading string lists with flexible separators, and copying groups between key files.

## Important APIs, Types, And Functions
Key functions are `ot_keyfile_get_boolean_with_default`, `_ostree_parse_boolean`, `_ostree_parse_tristate`, `ot_keyfile_get_tristate_with_default`, `ot_keyfile_get_value_with_default`, `ot_keyfile_get_value_with_default_group_optional`, `ot_keyfile_get_string_list_with_separator_choice`, `ot_keyfile_get_string_list_with_default`, and `ot_keyfile_copy_group`. Internal `is_notfound` identifies missing key/group errors.

## Control Flow
Defaulted getters call the corresponding `GKeyFile` getter, substitute defaults on missing key/group, and propagate parse or other errors. Boolean parsing accepts `yes/no`, `true/false`, and `1/0`. Tristate parsing accepts `maybe` or boolean values. Separator-choice list parsing detects which separator from a provided set appears in a raw value, errors if multiple separator types appear, treats no separator as a one-element list, and otherwise delegates to `g_key_file_get_string_list` with the selected separator.

## State And Persistence Behavior
No persistent state is written. The string-list getter mutates the `GKeyFile` list separator setting, which can affect later reads using the same keyfile.

## Dependencies And Integration Points
Depends on GLib `GKeyFile`, libglnx errors, and `OtTristate` from the header. Used by prepare-root config parsing, repo config parsing, and CLI/config utilities.

## Risks
`ot_keyfile_get_value_with_default` treats both missing group and missing key as default, while the group-optional wrapper is partly redundant because the inner function already handles group-not-found. `g_key_file_set_list_separator` has keyfile-wide effect. Separator-choice detection only checks presence, not escaping or list syntax semantics.

## Test Signals
Tests should cover missing key/group defaults, invalid boolean/tristate values, `maybe`, separator choice with no/one/multiple separator types, default string lists, group copy behavior, and keyfile separator side effects.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-keyfile-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-keyfile-utils.h -->
# sources/cloud-native/ostree/src/libotutil/ot-keyfile-utils.h

## Purpose
Declares keyfile parsing helpers and the `OtTristate` enum.

## Important APIs, Types, And Functions
Defines `OtTristate` values `OT_TRISTATE_NO`, `OT_TRISTATE_MAYBE`, and `OT_TRISTATE_YES`. Declares boolean/tristate parsers, defaulted keyfile getters, flexible string-list getters, and `ot_keyfile_copy_group`.

## Control Flow
No implementation flow. The declarations describe helper behavior used by config-loading code.

## State And Persistence Behavior
No state in the header. Declared functions allocate returned strings/lists and may mutate `GKeyFile` parser settings.

## Dependencies And Integration Points
Depends on GIO/GLib. Integrated by otcore prepare-root and broader libostree config consumers.

## Risks
Enum value ordering can matter if persisted or compared numerically. Ownership of returned strings/lists must be followed by callers.

## Test Signals
Compile coverage plus implementation parse/default tests are sufficient.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-keyfile-utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-opt-utils.c -->
# sources/cloud-native/ostree/src/libotutil/ot-opt-utils.c

## Purpose
Provides a CLI option helper for reporting usage errors with full help text.

## Important APIs, Types, And Functions
`ot_util_usage_error(context, message, error)` prints `g_option_context_get_help` output to stderr and sets a `G_IO_ERROR_FAILED` error with the provided message.

## Control Flow
The function obtains help text, prints it, frees it, and sets the error literal. It does not return a boolean; callers decide their error flow after invoking it.

## State And Persistence Behavior
No persistent state. It writes help text to stderr and populates a `GError`.

## Dependencies And Integration Points
Depends on GLib option parsing and GIO error domains. Used by command-line tools that want consistent usage output on invalid options.

## Risks
Always prints to stderr, which can be undesirable in library-like contexts or tests expecting quiet error construction. If `error` is NULL, `g_set_error_literal` is not called but help still prints.

## Test Signals
CLI tests should verify help text is printed and the expected error message/domain/code is set for invalid arguments.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-opt-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-opt-utils.h -->
# sources/cloud-native/ostree/src/libotutil/ot-opt-utils.h

## Purpose
Declares the command-line usage error helper.

## Important APIs, Types, And Functions
Declares `ot_util_usage_error(GOptionContext *context, const char *message, GError **error)`.

## Control Flow
No runtime flow in the header.

## State And Persistence Behavior
No state. The declared function writes to stderr and sets an error.

## Dependencies And Integration Points
Depends on GIO/GLib option types. Included by CLI code using `GOptionContext`.

## Risks
The API is void, so callers cannot chain it in boolean-returning expressions without custom handling.

## Test Signals
Compile and CLI behavior tests cover the header.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-opt-utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-tool-util.c -->
# sources/cloud-native/ostree/src/libotutil/ot-tool-util.c

## Purpose
Implements small command/tool utility functions for parsing booleans, parsing `KEY=VALUE`, and finding entries in `GPtrArray` with a custom equality function.

## Important APIs, Types, And Functions
`ot_parse_boolean` accepts case-insensitive `1/true/yes` and `0/false/no/none`. `ot_parse_keyvalue` splits the first `=` into allocated key and value. `ot_ptr_array_find_with_equal_func` is a compatibility copy of GLib pointer-array find behavior.

## Control Flow
Boolean parsing compares the input against accepted literals and errors otherwise. Key/value parsing finds the first `=`, errors if missing, and duplicates both sides. Pointer-array search defaults to pointer equality if no equality function is provided, scans linearly, optionally writes the first matching index, and returns whether found.

## State And Persistence Behavior
No persistent state. Functions allocate returned strings for parsed key/value and only read arrays.

## Dependencies And Integration Points
Depends on GLib, GIO errors through `otutil.h`, and is used by command-line tools or compatibility code needing behavior from newer GLib.

## Risks
`ot_parse_keyvalue` permits empty keys or values because it only requires an equals sign. Boolean parser differs from `_ostree_parse_boolean` by being case-insensitive and accepting `none` as false.

## Test Signals
Tests should cover all accepted boolean spellings/cases, invalid booleans, key/value strings with missing, leading, trailing, and multiple equals signs, and pointer-array search with NULL/custom equality.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-tool-util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-tool-util.h -->
# sources/cloud-native/ostree/src/libotutil/ot-tool-util.h

## Purpose
Declares small tool utility APIs for argument parsing and pointer-array search.

## Important APIs, Types, And Functions
Declares `ot_parse_boolean`, `ot_parse_keyvalue`, and `ot_ptr_array_find_with_equal_func`.

## Control Flow
No implementation flow. Consumers use these helpers in CLI parsing and compatibility logic.

## State And Persistence Behavior
No state. Declared parsers allocate output strings where applicable.

## Dependencies And Integration Points
Depends on GIO/GLib. Shared by OSTree command-line tools.

## Risks
Callers must free allocated key/value outputs and handle parser differences from keyfile boolean parsing.

## Test Signals
Compile coverage and implementation parser tests are relevant.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-tool-util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-unix-utils.c -->
# sources/cloud-native/ostree/src/libotutil/ot-unix-utils.c

## Purpose
Implements Unix-specific validation and privilege helpers for filenames, relative paths, and effective process capability checks.

## Important APIs, Types, And Functions
`ot_util_filename_validate` rejects NULL, `.`, `..`, names containing `/`, and invalid UTF-8. `ot_util_path_split_validate` splits a path on `/`, rejects overly long paths and `..`, removes `.` and empty components, and returns validated components. `ot_util_process_privileged` checks euid 0 and whether `CAP_SYS_ADMIN` is present in the capability bounding set via `prctl`.

## Control Flow
Filename validation performs sequential checks and returns a `GError` on the first invalid condition. Path splitting uses an internal pointer-array splitter, then canonicalizes from the end to safely remove entries while iterating. Privilege detection first checks euid, then uses `PR_CAPBSET_READ` for `CAP_SYS_ADMIN`.

## State And Persistence Behavior
No persistent state. Path splitting allocates a `GPtrArray` of components for callers.

## Dependencies And Integration Points
Depends on Unix headers, Linux capabilities, `prctl`, GLib UTF-8 validation, and libglnx error helpers. Used by sysroot mount namespace handling and path-safety code.

## Risks
`ot_split_string_ptrarray` takes a delimiter argument but currently always searches for `/`, so it is not a general splitter. `ot_util_process_privileged` treats root without `CAP_SYS_ADMIN` as unprivileged, which is appropriate for mount operations but stricter than euid checks. `strlen(path) > PATH_MAX` allows exactly `PATH_MAX`.

## Test Signals
Tests should cover invalid filenames, UTF-8 errors, path canonicalization with repeated slashes and dot entries, rejection of `..`, long paths, and privilege checks under rootless/container capability configurations.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-unix-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-unix-utils.h -->
# sources/cloud-native/ostree/src/libotutil/ot-unix-utils.h

## Purpose
Declares Unix utility helpers and centralizes common Unix system includes for libotutil users.

## Important APIs, Types, And Functions
Declares `ot_util_filename_validate`, `ot_util_path_split_validate`, and `ot_util_process_privileged`. Includes standard Unix headers for directory entries, errno, fcntl, stdio, string, stat, types, and unistd.

## Control Flow
No implementation flow. The header exposes validation and privilege APIs to filesystem and sysroot code.

## State And Persistence Behavior
No state. Declared functions allocate path component arrays or inspect process state.

## Dependencies And Integration Points
Depends on GIO/GLib and Unix platform headers. It is included by `ot-fs-utils.h` and other Unix-specific libostree code.

## Risks
The broad include block can leak many system declarations into consumers. The comment acknowledges the header is a catch-all, so future cleanup must consider include dependencies.

## Test Signals
Compile coverage on supported Unix/Linux platforms and implementation validation tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-unix-utils.h -->
