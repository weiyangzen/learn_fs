# Research: subset-b-000241

Grouped research for the requested OSTree Rust bindings, boot integration, and libostree support files. Each section preserves the source path in its title and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/sys/src/lib.rs -->
# sources/cloud-native/ostree/rust-bindings/sys/src/lib.rs

Purpose: This is the generated `ostree_sys` Rust FFI surface produced by `gir` for libostree. It exposes C ABI constants, enum aliases, bitflags, records, opaque GObject classes/interfaces, callbacks, and `extern "C"` declarations so higher-level Rust bindings can call libostree without re-declaring raw symbols by hand.

Important APIs, types, and functions: The file imports `gio_sys`, `glib_sys`, `gobject_sys`, `libc`, and C primitive types, then re-exports `manual::*` for hand-maintained ABI gaps such as `stat`. It defines aliases like `OstreeCollectionRefv` and `OstreeRepoFinderResultv`; enum integer types for deployment unlocked state, GPG errors and signature attributes, object types, repo modes, checkout modes, remote changes, static delta options, and lock types; constants for GVariant signatures, metadata keys, object limits, checksum lengths, signing backend names, and `/run/ostree-booted`; bitflag aliases for checksum, diff, commit modifier, commit state, list refs/objects, prune, pull, verify, SELinux restorecon, sysroot write/deploy, and upgrader operations. Records include public layout structs such as `OstreeCollectionRef`, `OstreeCommitSizesEntry`, `OstreeDiffDirsOptions`, `OstreeDiffItem`, checkout options, transaction stats, sign interface vtable, sysroot deploy/write opts, plus opaque zero-sized handles for GObjects such as `OstreeRepo`, `OstreeSysroot`, `OstreeDeployment`, `OstreeMutableTree`, `OstreeSePolicy`, `OstreeAsyncProgress`, and finder/sign interfaces.

Control flow: There is no internal Rust algorithmic flow beyond type declarations and generated `Debug` implementations. Runtime control transfers from Rust callers directly into libostree through the `extern "C"` block. The declarations are organized by libostree type families: boxed/refcounted values, kernel args, remotes, commit modifiers, traverse iterators, repo finders, async progress, bootconfig parsing, deployments, GPG verification, mutable trees, repositories, repo files, SELinux policy, sysroots, upgraders, blob readers, sign interfaces, and standalone utility functions.

State and persistence behavior: The file itself stores no runtime state. It models state owned by libostree: repository objects, refs, static deltas, remotes, config files, sysroot deployments, bootconfig files, GPG/signing material, SELinux labels, mutable trees, transaction statistics, and asynchronous progress key/value maps. Functions such as `ostree_repo_prepare_transaction`, `ostree_repo_write_commit`, `ostree_repo_transaction_set_ref`, `ostree_repo_commit_transaction`, `ostree_sysroot_write_deployments`, and staged deployment helpers are persistence entry points, but all mutation is performed in C.

Dependencies and integration points: The binding is tightly coupled to the installed libostree ABI and GLib/GIO/GObject conventions. `#[cfg(feature = "...")]` gates symbols by libostree release features, preventing older builds from exposing unavailable APIs. It integrates with higher-level safe Rust crates in `rust-bindings`, with ABI tests that compare Rust layout/constants to C, and with libostree consumers that need raw file descriptor, GVariant, GError, GHashTable, GPtrArray, and GAsyncResult access.

Risks: The central risk is ABI drift. Struct layout, integer values, ownership transfer, nullable pointers, varargs contracts, and feature gates must match the C headers exactly or safe wrappers can become unsound. Several structs are intentionally truncated because the C type contains incomplete fields, so callers must not assume full layout. Varargs functions and raw pointer callbacks are especially unsafe. Generated code also depends on correct GIR metadata; manual corrections are limited to `manual.rs`.

Test signals: `sys/tests/abi.rs`, `constant.c`, `layout.c`, and `manual.h` directly validate this file by compiling C probes against `ostree-1` and comparing constants plus `size_of`/`align_of` for exported Rust types. Higher-level tests under `rust-bindings/tests` exercise repo creation, commits, traversal, checkout, static delta generation, and signing through safe wrappers backed by these symbols.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/sys/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/sys/src/manual.rs -->
# sources/cloud-native/ostree/rust-bindings/sys/src/manual.rs

Purpose: This hand-maintained Rust module supplements generated FFI with declarations that `gir` does not emit correctly or at all. In this snapshot it re-exports `libc::stat`.

Important APIs, types, and functions: The only public item is `pub use libc::stat;`, making the Unix `struct stat` type available to generated callback and function signatures in `lib.rs`, especially checkout filters and checksum-at APIs.

Control flow: There is no executable control flow. The generated `lib.rs` declares `mod manual; pub use manual::*;`, so the `stat` name is pulled into the `ostree_sys` public namespace before it is used in FFI signatures.

State and persistence behavior: None. This file carries type identity only.

Dependencies and integration points: It depends on `libc` and the target being Unix-compatible for `stat`. It is paired conceptually with `sys/tests/manual.h`, which provides manual C-side compatibility definitions used by ABI tests.

Risks: A wrong `stat` type would corrupt ABI for callbacks or functions that pass `struct stat` across FFI. Platform assumptions matter because `stat` layout is libc and target dependent.

Test signals: `sys/tests/abi.rs` compiles only on Unix and uses generated FFI that references `stat`; successful ABI test compilation is the main signal that this manual export is sufficient.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/sys/src/manual.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/sys/tests/abi.rs -->
# sources/cloud-native/ostree/rust-bindings/sys/tests/abi.rs

Purpose: This generated Unix-only Rust test validates the `ostree_sys` raw ABI against the installed C libostree headers by comparing exported constant values and type layouts with small compiled C programs.

Important APIs, types, and functions: `Compiler` builds commands from `CC`, `CFLAGS`, `CPPFLAGS`, and `pkg-config --cflags ostree-1`, always adding `-Wno-deprecated-declarations`, `-std=c11`, and a MinGW printf define. `cross_validate_constants_with_c` compares `RUST_CONSTANTS` to output from `tests/constant.c`. `cross_validate_layout_with_c` compares `RUST_LAYOUTS` to output from `tests/layout.c`. `get_c_output` compiles the C fixture into a temporary executable and captures stdout. `Results` accumulates pass/fail counts and panics if any mismatch occurs.

Control flow: Each test runs the corresponding C fixture, parses semicolon-separated lines, zips C rows with the Rust manifest arrays in order, checks names first, then values or layouts, and records detailed stderr diagnostics before the final summary assertion. The compiler setup fails early if environment variables cannot be shell-split or pkg-config cannot locate `ostree-1`.

State and persistence behavior: State is limited to temporary directories from `tempfile::Builder`, process environment variables, and child compiler/executable processes. No repository state is modified. The test does depend on the system-installed libostree development files visible to pkg-config.

Dependencies and integration points: Depends on `ostree_sys::*`, Rust `std::process::Command`, `shell_words`, `tempfile`, C compiler tooling, pkg-config, `tests/constant.c`, `tests/layout.c`, and `tests/manual.h`. It is the bridge between generated Rust declarations and the authoritative C headers.

Risks: The test assumes identical ordering between `RUST_CONSTANTS`/`RUST_LAYOUTS` and C fixture output; a missing row can cascade into many name mismatches. It only checks selected constants and selected layouts, not every function signature or ownership rule. Local compiler/pkg-config differences can make failures environmental rather than source regressions.

Test signals: This file is itself the ABI test signal. Passing output means selected constants, struct sizes, and alignments match the installed libostree headers for the active feature set and target.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/sys/tests/abi.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/sys/tests/constant.c -->
# sources/cloud-native/ostree/rust-bindings/sys/tests/constant.c

Purpose: This generated C fixture prints libostree constant names and values so `abi.rs` can compare them against Rust constants in `ostree_sys`.

Important APIs, types, and functions: It includes `manual.h` and `<stdio.h>`. The `PRINT_CONSTANT` macro emits `<name>;<value>\n` using C11 `_Generic` to select a printf format for strings, characters, signed and unsigned integer widths, and floating types. `main` prints OSTree checksum flags, GVariant format strings, commit metadata keys, deployment states, diff flags, GPG errors and signature attributes, object types, repo checkout/commit/list/prune/pull/remote/verify flags, SELinux flags, SHA256 lengths, signing names, static delta options, sysroot flags, and tree/summary format strings.

Control flow: `main` is a straight-line list of `PRINT_CONSTANT(...)` invocations followed by `return 0`. No branching occurs beyond format selection in `_Generic`.

State and persistence behavior: The fixture has no persistent state. Its only side effect is stdout.

Dependencies and integration points: It depends on libostree C headers through `manual.h`, on C11 for `_Generic`, and on the exact output ordering expected by `RUST_CONSTANTS` in `abi.rs`.

Risks: `_Generic` coverage must match the types of printed constants; unsupported types would fail to compile. Order drift between this file and `RUST_CONSTANTS` causes false mismatches. Backfilled constants in `manual.h` can hide older-header gaps intentionally, so tests verify compatibility behavior rather than only upstream header declarations.

Test signals: When compiled and run by `abi.rs`, each stdout row becomes an assertion target for the Rust binding constant with the same textual name.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/sys/tests/constant.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/sys/tests/layout.c -->
# sources/cloud-native/ostree/rust-bindings/sys/tests/layout.c

Purpose: This generated C fixture prints C `sizeof` and `alignof` values for selected libostree types so Rust ABI layout declarations can be checked.

Important APIs, types, and functions: It includes `manual.h`, `<stdalign.h>`, and `<stdio.h>`. `main` prints semicolon-separated rows for classes/interfaces, enum and flag typedefs, boxed structs, option structs, stats structs, vtables, and pointer-vector aliases such as `OstreeCollectionRefv` and `OstreeRepoFinderResultv`.

Control flow: Straight-line `printf` calls produce `<type>;<size>;<alignment>` rows in the order expected by `RUST_LAYOUTS`.

State and persistence behavior: None beyond stdout. No OSTree repository or object state is created.

Dependencies and integration points: Requires a C compiler with `alignof` support, the libostree headers, GLib/GObject type definitions pulled through `ostree.h`, and the ordering contract with `abi.rs`.

Risks: It checks type size and alignment but not field offsets. If Rust fields are reordered in a way that preserves total size and alignment, this test would not detect it unless another assertion is added. Conditional header compatibility in `manual.h` affects what can compile against older libostree.

Test signals: Passing `cross_validate_layout_with_c` confirms the Rust FFI declarations for selected records and typedefs have C-compatible size and alignment on the test platform.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/sys/tests/layout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/sys/tests/manual.h -->
# sources/cloud-native/ostree/rust-bindings/sys/tests/manual.h

Purpose: This hand-maintained C header supports generated ABI fixtures by including libostree headers and defining compatibility constants for older libostree versions.

Important APIs, types, and functions: It includes `<ostree.h>`. If `OSTREE_CHECK_VERSION(2019, 2)` is false, it defines `OSTREE_REPO_LIST_REFS_EXT_EXCLUDE_MIRRORS`, `OSTREE_REPO_REMOTE_CHANGE_REPLACE`, and `OSTREE_REPO_RESOLVE_REV_EXT_LOCAL_ONLY` to their expected numeric values.

Control flow: Preprocessor-only control flow checks the libostree version and conditionally defines missing constants before C fixtures are compiled.

State and persistence behavior: None.

Dependencies and integration points: Used by `constant.c` and `layout.c`. It is C-side counterpart to `sys/src/manual.rs`: both patch generated or version-dependent ABI knowledge.

Risks: Backfilled values must match the newer libostree ABI exactly. Incorrect fallback values would make ABI tests pass for the wrong Rust constant and could mislead compatibility claims.

Test signals: Successful compilation of the C fixtures against libostree versions older than 2019.2 indicates these fallbacks cover the expected missing constants.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/sys/tests/manual.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/tests/core/mod.rs -->
# sources/cloud-native/ostree/rust-bindings/tests/core/mod.rs

Purpose: This Rust integration test verifies higher-level variant decoding for OSTree commit objects.

Important APIs, types, and functions: `variant_types` uses `TestRepo::new`, `test_commit`, `Repo::load_variant`, `ostree::ObjectType::Commit`, and `ostree::CommitVariantType`. It extracts the commit tuple and asserts that the subject field equals `Test Commit`.

Control flow: Create a temporary repository, write a test commit through shared utilities, load the commit object as a `GVariant`, decode it into the typed commit representation, and assert a known field.

State and persistence behavior: Creates a temporary archive-mode OSTree repo and writes one commit. State lives under `tempfile::TempDir` and is removed after the test.

Dependencies and integration points: Depends on `tests/util/mod.rs`, the safe `ostree` crate, GLib variant conversion, and the test data archive used by `create_mtree`.

Risks: It covers only one field of one commit variant. It assumes the utility commit subject remains `Test Commit`, so utility changes can break the test without a core variant regression.

Test signals: Passing confirms that commit `GVariant` loading and typed extraction work for at least the generated fixture commit.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/tests/core/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/tests/functions/mod.rs -->
# sources/cloud-native/ostree/rust-bindings/tests/functions/mod.rs

Purpose: This integration test module exercises safe wrapper functions for listing repository objects and checksumming loaded file content.

Important APIs, types, and functions: `list_repo_objects` calls `Repo::list_objects` with `ffi::OSTREE_REPO_LIST_OBJECTS_ALL`, iterates `ObjectName` keys, counts `DirTree`, `DirMeta`, `File`, and `Commit`, and validates the commit checksum. `should_checksum_file_from_input` traverses a commit, loads each file object via `Repo::load_file`, and calls `ostree::checksum_file_from_input`.

Control flow: Both tests create a temporary `TestRepo`, write a known commit, then inspect repository objects. The checksum test filters traversal output to file objects before recomputing each checksum from loaded stream, metadata, and xattrs.

State and persistence behavior: Temporary repository state includes one commit and its file/tree metadata objects. No state persists beyond test cleanup.

Dependencies and integration points: Uses `TestRepo`, `ObjectType`, `gio::Cancellable::NONE`, the `ffi` constant from raw bindings, and safe wrappers that depend on FFI declarations in `sys/src/lib.rs`.

Risks: Expected object counts are fixture-specific and can change if `tests/data/test.tar` changes. The checksum test skips non-file objects, so metadata checksum wrapper regressions would be covered elsewhere.

Test signals: Passing confirms object listing maps raw OSTree object types correctly and that file content checksum recomputation matches stored object checksums.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/tests/functions/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/tests/repo/checkout_at.rs -->
# sources/cloud-native/ostree/rust-bindings/tests/repo/checkout_at.rs

Purpose: This test module verifies the safe Rust `Repo::checkout_at` wrapper, including `None` options, default options, explicit checkout options, and optional checkout filtering.

Important APIs, types, and functions: Tests use `TestRepo`, `cap_std::fs::Dir`, `AsRawFd`, `RepoCheckoutAtOptions`, `RepoCheckoutMode::User`, `RepoCheckoutOverwriteMode::AddFiles`, `RepoDevInoCache::new`, `RepoCheckoutFilter::new`, and filter results `Allow`/`Skip`. `assert_test_file` verifies checked-out content.

Control flow: Each test creates a temporary repo and commit, opens a capability directory for a temp checkout root, calls `checkout_at` with a destination fd and path, then verifies filesystem output. The filter test conditionally skips `/testdir/testfile` and asserts the directory exists but the file does not.

State and persistence behavior: Writes a temporary checkout tree on disk. The third test also creates a devino-to-checksum cache for checkout acceleration/canonicalization behavior. The filter closure is transient callback state passed through FFI.

Dependencies and integration points: Depends on libostree checkout-at API, capability-oriented directory handles from `cap-std`, Unix raw file descriptors, and feature gates for APIs introduced around `v2016_8` and `v2018_2`.

Risks: File descriptor lifetime and callback ownership are important unsafe boundaries. The filter path comparison assumes libostree reports paths with a leading slash. The tests validate success cases but not overwrite conflict handling or SELinux policy options.

Test signals: Passing confirms `checkout_at` accepts null/default/non-default option structs, can use a devino cache, and can invoke Rust filter callbacks safely enough to affect checkout output.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/tests/repo/checkout_at.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/tests/repo/generate_static.rs -->
# sources/cloud-native/ostree/rust-bindings/tests/repo/generate_static.rs

Purpose: This test verifies static delta generation through the safe Rust repo wrapper.

Important APIs, types, and functions: `should_generate_static_delta_at` builds a `HashMap<String, glib::Variant>` with a `filename` option, encodes a NUL-terminated path as a variant, creates two commits, and calls `Repo::static_delta_generate` with `StaticDeltaGenerateOpt::Major`, `Some(&from)`, `&to`, no metadata, option variant, and no cancellable.

Control flow: Create a temp output path, convert it to the variant format expected by libostree, create a temporary repo, commit two revisions, invoke static delta generation, then assert that the target delta file exists.

State and persistence behavior: Writes two temporary commits and a static delta file under a temporary directory. No persistent repo mutation survives outside test cleanup.

Dependencies and integration points: Depends on GLib variant conversion traits, the safe `ostree` repo API, `TestRepo`, and libostree's static delta backend.

Risks: The path conversion requires valid UTF-8 and successful `CString` creation. The test only checks file existence, not delta contents, signature validation, or apply behavior.

Test signals: Passing indicates the Rust wrapper can marshal static delta options and invoke libostree to write a delta artifact.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/tests/repo/generate_static.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/tests/repo/mod.rs -->
# sources/cloud-native/ostree/rust-bindings/tests/repo/mod.rs

Purpose: This is the main integration test module for safe `ostree::Repo` behavior: creating commits, resolving refs, listing commits, capability-based repo creation, traversing and reading objects, checkout, object copying, and repo file descriptor access.

Important APIs, types, and functions: It imports `ostree::prelude::*`, `ObjectName`, `ObjectType`, and conditionally `cap_std`. Tests cover `require_rev`, `create_mtree`, `commit`, `Repo::new_for_path`, `open`, `list_refs`, `list_commit_objects_starting_with`, `Repo::create_at_dir`, `Repo::open_at_dir`, `traverse_commit`, `read_dirmeta`, `query_file`, `read_commit`, `checkout_tree`, `load_object_stream`, `write_content`, `load_variant`, `write_metadata`, and `dfd_as_file`.

Control flow: The tests build temporary repositories from the shared tar fixture, perform operations through safe wrappers, and assert exact checksums/counts/content. Helper functions `copy_file` and `copy_metadata` copy traversed objects from one repo to another and assert output checksums match source object names.

State and persistence behavior: Temporary archive-mode repos are created and mutated with commits, refs, object files, metadata variants, and checkouts. Transactions in `util::commit` ensure ref updates are committed atomically. Capability tests use directory fds to avoid ambient path access for newer feature sets.

Dependencies and integration points: Integrates the safe Rust crate with raw FFI, GLib/GIO, cap-std feature-gated APIs, Unix metadata APIs, and fixed fixture checksums from `tests/data/test.tar`.

Risks: Exact object checksums and mode expectations are fixture- and environment-sensitive; comments note uid/gid are from the test runner, while mode is asserted. The module verifies representative flows but does not cover remote pull, pruning, locking, or error recovery.

Test signals: Passing provides broad confidence that core repo wrappers marshal strings, variants, streams, fds, transactions, object names, and checkout parameters correctly.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/tests/repo/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/tests/sign/mod.rs -->
# sources/cloud-native/ostree/rust-bindings/tests/sign/mod.rs

Purpose: This integration module verifies the safe signing API wrappers, including dummy signer failure behavior and optional ed25519 signing/verification.

Important APIs, types, and functions: `sign_api_should_work` uses `Sign::by_name`, `SignExt::data`, `data_verify`, and GLib `Bytes`/variant conversion. `inner_sign_ed25519` accepts any `T: SignExt`, generates keys by sourcing `tests/libtest.sh`, calls `set_sk`, `add_pk`, `data`, and `data_verify`, and checks error cases for modified payloads and ill-formed signatures. `sign_ed25519` runs only when the ed25519 backend is available.

Control flow: The dummy test confirms lookup and expected failures. The ed25519 path creates a temp dir, runs bash to generate keys, reads secret/public material, configures the signer, signs a payload, verifies it, then tests invalid payload and malformed signature rejection.

State and persistence behavior: Temporary key files are written in a temp directory. Signer objects hold key material in memory through libostree. No repo commits are signed in this file.

Dependencies and integration points: Depends on feature gate `v2020_2` or `dox`, libostree sign backends, GLib prelude traits, bash, `tests/libtest.sh`, and environment variable `G_TEST_SRCDIR`.

Risks: The test shells out and sources shared shell test code, so it can fail if run from an unexpected directory or without required shell tooling. It skips ed25519 if the backend is unavailable, reducing coverage on minimal builds. It validates data signing, not commit/summary signing.

Test signals: Passing confirms signer discovery, key loading, data signing, successful verification, and failure reporting for bad signatures through Rust traits.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/tests/sign/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/tests/tests.rs -->
# sources/cloud-native/ostree/rust-bindings/tests/tests.rs

Purpose: This is the top-level Rust integration test module that wires submodules into the test binary.

Important APIs, types, and functions: It declares `mod core`, `mod functions`, `mod repo`, `mod util`, and conditionally `mod sign` for feature `v2020_2` or `dox`.

Control flow: Rust test discovery compiles this module, then discovers `#[test]` functions in each child module. The only branch is compile-time feature gating for signing tests.

State and persistence behavior: This file has no runtime state. It controls which test modules can create temporary repos or key material.

Dependencies and integration points: Integrates the test suite modules under `rust-bindings/tests` and applies feature-sensitive coverage selection.

Risks: If a module is omitted here, its tests silently stop running. Feature gating can also hide regressions unless CI runs appropriate feature matrices.

Test signals: Successful compilation confirms the integration test tree is wired; actual behavioral signal comes from the submodules.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/tests/tests.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/tests/util/mod.rs -->
# sources/cloud-native/ostree/rust-bindings/tests/util/mod.rs

Purpose: This shared test utility module creates temporary OSTree repositories, writes fixture commits, and verifies checkout content for the Rust binding integration tests.

Important APIs, types, and functions: `TestRepo` stores a `tempfile::TempDir` and `ostree::Repo`. `TestRepo::new` and `new_with_mode` create archive-mode repos by default. `test_commit` writes a fixture commit. Feature-gated `CapTestRepo` uses `cap_tempfile` and `Repo::create_at_dir`. `create_mtree` creates a `MutableTree`, asserts initially empty copied files/subdirs, and imports `rust-bindings/tests/data/test.tar` through `write_archive_to_mtree`. `commit` uses `auto_transaction`, `write_mtree`, `write_commit`, `transaction_set_ref`, and transaction commit. `assert_test_file` reads `test-checkout/testdir/testfile` and expects `test\n`.

Control flow: Repo helpers create temp storage, initialize libostree repos, import a tar fixture into a mutable tree, write it to the repo, create a commit with subject `Test Commit`, set a ref, and commit the transaction. Tests call these helpers to avoid duplicating setup.

State and persistence behavior: All state is temporary but realistic: repo config, object storage, refs, transaction state, mutable trees, and checkout directories. Transaction helper is the key persistence boundary for commits and refs.

Dependencies and integration points: Depends on GLib prelude traits, GIO file APIs, `tempfile`, optional `cap_tempfile`, the `ostree` safe crate, and the fixture archive path resolved via `CARGO_MANIFEST_DIR`.

Risks: Many tests depend on exact fixture contents and commit subject. Any change to `test.tar` can update object checksums, object counts, and checkout assertions. The helper panics on setup failures, which is appropriate for tests but not reusable production logic.

Test signals: Because most integration tests use this module, successful test setup across modules is a broad signal that repo initialization, archive import, transaction commit, and fixture checkout remain healthy.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/tests/util/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/boot/dracut/module-setup.sh -->
# sources/cloud-native/ostree/src/boot/dracut/module-setup.sh

Purpose: This dracut module installs OSTree's initramfs prepare-root integration so an OSTree deployment can become the real root during early boot.

Important APIs, types, and functions: Dracut hook functions include `installkernel`, `check`, `depends`, and `install`. `installkernel` requests `erofs` and `overlay` kernel modules. `check` returns `255` only when systemd and `/usr/lib/ostree/ostree-prepare-root` are executable, which tells dracut the module is usable. `install` copies `ostree-prepare-root`, optional `prepare-root.conf` from `/usr/lib/ostree` or `/etc/ostree`, optional `initramfs-root-binding.key`, and `ostree-prepare-root.service`, then links the service into `initrd-root-fs.target.wants`.

Control flow: Dracut calls these shell functions during initramfs generation. The script conditionally includes configs and always wires the systemd unit when installation proceeds.

State and persistence behavior: It writes files and symlinks into the generated initramfs image, not the live root at boot time. Including root-binding keys and prepare-root config affects how early boot later resolves and validates the OSTree root.

Dependencies and integration points: Depends on dracut helper functions (`instmods`, `dracut_install`, `inst_simple`, `ln_r`), systemd unit directories, the OSTree prepare-root binary, and optional config/key files. It pairs with `ostree-prepare-root.service`.

Risks: Missing modules or service links can make OSTree systems fail before root switch. Including host-specific keys/configs in initramfs needs packaging care. `check` excludes non-systemd initramfs environments.

Test signals: There are no direct tests in this subset. Practical validation comes from dracut image generation and boot tests where `ostree-prepare-root.service` runs in initramfs.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/boot/dracut/module-setup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/boot/dracut/ostree.conf -->
# sources/cloud-native/ostree/src/boot/dracut/ostree.conf

Purpose: This dracut configuration requests the OSTree and systemd modules and enables reproducible image generation.

Important APIs, types, and functions: It appends `ostree systemd` to `add_dracutmodules` and sets `reproducible=yes`.

Control flow: Dracut sources this config while building an initramfs. There is no custom shell function.

State and persistence behavior: It influences generated initramfs contents and reproducibility. It does not run during boot.

Dependencies and integration points: Integrates with dracut's config parser and the `module-setup.sh` OSTree module.

Risks: If this config is not installed or sourced, required OSTree/systemd initramfs pieces may be absent. Reproducibility depends on dracut support and broader image inputs.

Test signals: Indirect signal is successful dracut image construction containing the OSTree module and systemd boot path.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/boot/dracut/ostree.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/boot/grub2/grub2-15_ostree -->
# sources/cloud-native/ostree/src/boot/grub2/grub2-15_ostree

Purpose: This GRUB2 mkconfig helper delegates generation of OSTree boot menu entries to `ostree admin instutil grub2-generate` when a non-BLS GRUB configuration needs OSTree entries.

Important APIs, types, and functions: It checks for the `ostree` command, `/ostree/repo`, `/etc/default/grub`, and BLS support via `/boot/grub2/.grub2-blscfg-supported` plus `GRUB_ENABLE_BLSCFG`. It requires `GRUB_DEVICE`, sources `/usr/share/grub/grub-mkconfig_lib`, computes `DEVICE`, exports `GRUB2_BOOT_DEVICE_ID` from `grub_get_device_id`, exports `GRUB2_PREPARE_ROOT_CACHE` from `prepare_grub_to_access_device`, then execs `ostree admin instutil grub2-generate`.

Control flow: The script exits 0 for systems where it is irrelevant, exits 1 if invoked outside `grub2-mkconfig`, and otherwise runs with `set -e` before replacing itself with the OSTree generator.

State and persistence behavior: It writes no files itself. It passes computed GRUB device access state through environment variables to the generator that emits menu entries.

Dependencies and integration points: Depends on GRUB mkconfig environment, `/etc/default/grub`, GRUB helper library, OSTree system repo, and `ostree admin instutil`. It intentionally avoids generating entries when BLS can handle them.

Risks: Environment assumptions are fragile: missing `GRUB_DEVICE`, unavailable helper functions, or unexpected boot device detection can break menu generation. BLS detection must stay aligned with distro GRUB packaging.

Test signals: No direct tests in this subset. Integration is validated by grub2-mkconfig runs and bootloader entry generation tests elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/boot/grub2/grub2-15_ostree -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/boot/grub2/ostree-grub-generator -->
# sources/cloud-native/ostree/src/boot/grub2/ostree-grub-generator

Purpose: This shell script is OSTree's built-in GRUB configuration generator for systems that do not use `grub2-mkconfig`. It converts Boot Loader Specification entry files into GRUB `menuentry` blocks.

Important APIs, types, and functions: It defines `read_config`, `populate_menu`, `populate_warning`, `populate_header`, and `generate_grub2_cfg`. Inputs are the output config path argument, the neighboring `entries` directory, optional `OSTREE_BOOT_PARTITION`, `/boot/ostree`, and `/ostree/repo`. It parses BLS records `title`, `initrd`, `linux`, `devicetree`, and `options`.

Control flow: `generate_grub2_cfg` writes a warning, a static serial/default/timeout header, then menu entries. `populate_menu` chooses a boot prefix: `/boot` when `/boot/ostree` and `/ostree/repo` are on the same device and `OSTREE_BOOT_PARTITION` is unset, otherwise the environment-provided boot partition prefix. It iterates entry configs with `ls -v -r`, reads each config, and appends GRUB stanza text.

State and persistence behavior: Appends to the new grub config path supplied by the caller, which is intended to be an atomically safe temporary target during bootloader updates. It reads BLS entry files but does not mutate them.

Dependencies and integration points: Invoked by `ostree-bootloader-grub2.c`, relies on POSIX/busybox-compatible shell behavior, `stat`, `ls -v -r`, BLS entry format, and GRUB syntax.

Risks: Unquoted variable use and simple line parsing can be sensitive to spaces or shell metacharacters in paths/titles/options. The script appends rather than truncates, so the caller must provide a fresh output file. Embedded systems with minimal tools must provide compatible `stat` and `ls`.

Test signals: No direct tests here. Generated grub.cfg inspection and boot tests are the main validation signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/boot/grub2/ostree-grub-generator -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/boot/mkinitcpio/ostree -->
# sources/cloud-native/ostree/src/boot/mkinitcpio/ostree

Purpose: This mkinitcpio install hook adds OSTree early-boot binaries and systemd unit wiring to Arch-style initramfs images.

Important APIs, types, and functions: The `build` function calls mkinitcpio helpers `add_binary`, `add_file`, and `add_symlink` for `/usr/lib/ostree/ostree-prepare-root`, `/usr/lib/ostree/ostree-remount`, `ostree-prepare-root.service`, and the `initrd-root-fs.target.wants` symlink.

Control flow: mkinitcpio invokes `build` during image construction. There is no runtime branching.

State and persistence behavior: It writes selected files and symlink metadata into the generated initramfs. It does not mutate the live filesystem directly.

Dependencies and integration points: Depends on mkinitcpio's hook API, systemd in initramfs, and OSTree binaries installed under `/usr/lib/ostree`. It is selected by `ostree-mkinitcpio.conf`.

Risks: Missing binaries or incorrect symlink target can prevent prepare-root from running. The hook assumes systemd-based initramfs behavior.

Test signals: Validation is by mkinitcpio image generation and boot behavior; no direct test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/boot/mkinitcpio/ostree -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/boot/mkinitcpio/ostree-mkinitcpio.conf -->
# sources/cloud-native/ostree/src/boot/mkinitcpio/ostree-mkinitcpio.conf

Purpose: This mkinitcpio configuration defines the hook order needed for OSTree systems.

Important APIs, types, and functions: It sets `HOOKS="base systemd ostree autodetect modconf block filesystems keyboard fsck"`.

Control flow: mkinitcpio reads the hook list in order when building an initramfs. The `ostree` hook is placed after `systemd` and before hardware/filesystem autodetection and mounting hooks.

State and persistence behavior: It controls generated initramfs composition only.

Dependencies and integration points: Integrates with the `src/boot/mkinitcpio/ostree` hook and standard mkinitcpio hooks.

Risks: Hook ordering is boot-critical; moving `ostree` can prevent prepare-root services from being present or correctly ordered. The single-line config is easy for packagers to override incorrectly.

Test signals: Indirect validation through mkinitcpio build output and OSTree boot tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/boot/mkinitcpio/ostree-mkinitcpio.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/boot/ostree-boot-complete.service -->
# sources/cloud-native/ostree/src/boot/ostree-boot-complete.service

Purpose: This systemd oneshot marks an OSTree boot as complete and handles cleanup/failure propagation before staged deployment finalization.

Important APIs, types, and functions: Unit conditions require `ostree` on the kernel command line and either `/boot/ostree/finalize-failure.stamp` or `/run/ostree/nextroot-booted`. It has `DefaultDependencies=no`, runs `After=sysinit.target`, requires mounts for `/boot`, and runs `Before=ostree-finalize-staged.service`. Service uses `MountFlags=slave`, `RemainAfterExit=yes`, and `ExecStart=/usr/bin/ostree admin boot-complete`.

Control flow: systemd starts it early when conditions match. The OSTree CLI performs the actual boot-complete logic and any soft-reboot cleanup.

State and persistence behavior: The service may write to `/boot` through the OSTree command, including removing or recording boot/finalization state. It remains active after completion to preserve ordering.

Dependencies and integration points: Integrates with staged deployment finalization, boot-complete CLI implementation, `/boot` mount availability, and soft reboot state under `/run/ostree`.

Risks: If it fails or is skipped incorrectly, finalization failure markers may not propagate and later staged finalization can run with stale state. `/boot` mount accessibility and namespace behavior are important.

Test signals: No direct test here; systemd boot integration and OSTree admin command tests provide validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/boot/ostree-boot-complete.service -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/boot/ostree-finalize-staged-hold.service -->
# sources/cloud-native/ostree/src/boot/ostree-finalize-staged-hold.service

Purpose: This systemd service keeps `/boot` open for the duration of staged deployment finalization to avoid automount timeouts and namespace issues.

Important APIs, types, and functions: It requires `/run/ostree-booted`, has no default dependencies, requires mounts for `/sysroot` and `/boot`, runs after `local-fs.target`, before `basic.target` and `final.target`, and executes `+/usr/bin/ostree admin finalize-staged --hold` with `Type=exec`.

Control flow: `ostree-finalize-staged.service` wants and orders after this hold service, ensuring the hold process is active before finalization later occurs.

State and persistence behavior: The command's purpose is to keep resources open, primarily `/boot`; it is not the final mutation step itself. The `+` prefix runs with elevated/root namespace behavior.

Dependencies and integration points: Tightly paired with `ostree-finalize-staged.service`, systemd mount handling, autofs behavior, and OSTree staged deployment state.

Risks: If the hold service exits too early or cannot access `/boot`, staged finalization may fail on systems with automounted `/boot`. Root namespace execution is deliberate and security-sensitive.

Test signals: Validation is boot/shutdown integration; no direct unit tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/boot/ostree-finalize-staged-hold.service -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/boot/ostree-finalize-staged.service -->
# sources/cloud-native/ostree/src/boot/ostree-finalize-staged.service

Purpose: This systemd service finalizes a staged OSTree deployment during shutdown by running its command in `ExecStop`.

Important APIs, types, and functions: Unit conditions require `/run/ostree-booted`. It has no default dependencies, requires mounts for `/sysroot`, `/boot`, and `/etc`, runs after `local-fs.target`, `systemd-journal-flush.service`, and the hold service, before `basic.target` and `final.target`, and conflicts with `final.target`. It wants `ostree-finalize-staged-hold.service`. Service uses `Type=oneshot`, `RemainAfterExit=yes`, `ExecStop=/usr/bin/ostree admin finalize-staged`, `TimeoutStopSec=5m`, `ProtectHome=yes`, and `ReadOnlyPaths=/etc`.

Control flow: The service starts and remains active during boot; finalization occurs when systemd stops it during shutdown. Ordering is designed so logs are flushed and `/boot` remains available before the staged deployment is committed.

State and persistence behavior: `finalize-staged` mutates deployment and bootloader state under `/sysroot` and `/boot`, and may remove `/var/.updated`. It explicitly avoids changing the current deployment's `/etc` by making `/etc` read-only.

Dependencies and integration points: Integrates with the staged deployment machinery, bootloader updates, journal flushing, hold service, systemd shutdown transaction, and mounted sysroot/boot filesystems.

Risks: This is high-risk boot state mutation. Timeout, mount, or bootloader failures can leave upgrades unfinalized. Running at shutdown makes observability harder, hence journal ordering. Sandboxing must allow required `/sysroot` and `/boot` writes while limiting unrelated state access.

Test signals: No direct test in this subset. End-to-end staged upgrade tests and bootloader state inspections are needed.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/boot/ostree-finalize-staged.service -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/boot/ostree-prepare-root.service -->
# sources/cloud-native/ostree/src/boot/ostree-prepare-root.service

Purpose: This initramfs systemd unit invokes `ostree-prepare-root` to prepare the OSTree deployment root under `/sysroot`.

Important APIs, types, and functions: Conditions require `ostree` on the kernel command line and `/etc/initrd-release`, identifying initramfs context. It requires and runs after `sysroot.mount`, before `initrd-root-fs.target`, and sends failures to `emergency.target` with isolate job mode. `ExecStart=/usr/lib/ostree/ostree-prepare-root /sysroot`.

Control flow: During initramfs boot, systemd mounts sysroot, runs this oneshot, then proceeds to `initrd-root-fs.target` if successful. Failure isolates emergency mode.

State and persistence behavior: The binary performs root preparation and mount rearrangement under `/sysroot`; the unit itself remains after exit to preserve ordering. It writes logs to journal and console.

Dependencies and integration points: Installed by dracut/mkinitcpio hooks. Depends on initramfs systemd, kernel command line, sysroot mount, and OSTree prepare-root binary.

Risks: Failure blocks boot. Conditions must prevent accidental execution outside initramfs. Console error output is important because root setup failures happen before the normal system is available.

Test signals: Validated by initramfs boot tests and image-generation checks; no direct test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/boot/ostree-prepare-root.service -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/boot/ostree-remount.service -->
# sources/cloud-native/ostree/src/boot/ostree-remount.service

Purpose: This systemd oneshot remounts OSTree OS bind mounts early in the real boot so writable state such as `/etc` and `/var` is ready before core services need it.

Important APIs, types, and functions: It runs only with `ostree` on the kernel command line, has no default dependencies, conflicts with `umount.target`, runs after `-.mount`, `var.mount`, and `systemd-remount-fs.service`, and before `local-fs.target`, `umount.target`, random seed, Plymouth read-write, journal flush, tmpfiles setup, and rfkill units. `ExecStart=/usr/lib/ostree/ostree-remount`; installed as `WantedBy=local-fs.target`.

Control flow: systemd orders it after core mounts but before services that require write access. Failure triggers emergency target.

State and persistence behavior: The OSTree binary performs mount namespace/bind mount changes for deployment state. The service remains active after exit.

Dependencies and integration points: Integrates with systemd local filesystem ordering, OSTree deployment mounts, `/var`, `/etc`, and early services that read/write persistent machine state.

Risks: Incorrect ordering can cause services to see read-only or wrong `/etc`/`/var`. Failure early in boot can isolate emergency mode. It must avoid racing unmount during shutdown.

Test signals: Boot integration tests and systemd ordering analysis are primary validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/boot/ostree-remount.service -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/boot/ostree-state-overlay@.service -->
# sources/cloud-native/ostree/src/boot/ostree-state-overlay@.service

Purpose: This templated systemd unit creates an OSTree state overlay on a selected top-level path such as `/%I`.

Important APIs, types, and functions: It runs only on OSTree boots, has no default dependencies, runs after `var.mount` and `boot.mount`, before `local-fs.target`, and executes `/usr/bin/ostree admin state-overlay %i /%I`. It remains active and is wanted by `local-fs.target`.

Control flow: For each enabled instance, systemd substitutes the instance name into `%i` and `%I`, waits for `/var` and `/boot`, then invokes the OSTree CLI before local filesystems are considered ready.

State and persistence behavior: The CLI stores upperdir state under `/var` and overlays the requested path. This affects runtime writable state for otherwise immutable deployments.

Dependencies and integration points: Integrates with OSTree admin CLI, systemd template units, `/var` storage, boot/sysroot metadata, and local-fs ordering.

Risks: Instance naming controls the target path, so misconfiguration can overlay the wrong directory. Overlay setup before local-fs is timing-sensitive and depends on `/var` availability.

Test signals: No direct tests here; validation requires enabled unit instances and boot-time overlay behavior checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/boot/ostree-state-overlay@.service -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/boot/ostree-tmpfiles.conf -->
# sources/cloud-native/ostree/src/boot/ostree-tmpfiles.conf

Purpose: This tmpfiles configuration creates OSTree runtime directories and removes stale temporary unlock overlay directories.

Important APIs, types, and functions: It declares `d /run/ostree 0755 root root -` and `R! /var/tmp/ostree-unlock-ovl.*`.

Control flow: systemd-tmpfiles processes the rules during tmpfiles setup. Directory creation and removal are declarative.

State and persistence behavior: Ensures `/run/ostree` exists for runtime state and force-removes matching `/var/tmp/ostree-unlock-ovl.*` paths at tmpfiles cleanup time. `/run` state is volatile; `/var/tmp` cleanup affects persistent temporary state.

Dependencies and integration points: Used by systemd-tmpfiles and comments reference historical unlock overlay behavior. It complements boot services that use `/run/ostree`.

Risks: The removal glob must stay specific; overly broad cleanup could delete unrelated data. Removing stale overlay temp dirs is useful, but active use must not overlap tmpfiles cleanup timing.

Test signals: Validation comes from tmpfiles runs and checking runtime directory presence/cleanup behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/boot/ostree-tmpfiles.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/bupsplit.c -->
# sources/cloud-native/ostree/src/libostree/bupsplit.c

Purpose: This C file implements bup-style content-defined chunk boundary detection using a rolling checksum. OSTree can use it to split content into stable chunks for delta/static-delta style operations.

Important APIs, types, and functions: Internal `Rollsum` holds `s1`, `s2`, a `BUP_WINDOWSIZE` byte window, and a window offset. `rollsum_add`, `rollsum_init`, `rollsum_roll`, and `rollsum_digest` implement the rolling checksum. Public `bupsplit_sum` computes a digest over a buffer slice. Public `bupsplit_find_ofs` scans a buffer for a chunk boundary and optionally reports boundary strength in `bits`.

Control flow: `bupsplit_find_ofs` initializes the rolling checksum, rolls each input byte, checks whether low bits of `s2` match the boundary mask `(BUP_BLOBSIZE - 1)`, computes additional matching bits when requested, and returns the boundary offset as `count + 1`; if no boundary is found it returns 0. `bupsplit_sum` rolls from `ofs` to `len` and returns the digest.

State and persistence behavior: All state is stack-local and deterministic for the input bytes. No persistent state or allocation is used.

Dependencies and integration points: Depends on `bupsplit.h` constants, `stdint.h`, `memory.h`, and C integer arithmetic. The code is imported from bup/librsync-style algorithms and carries a separate license block.

Risks: `bupsplit_find_ofs` takes `int len`, so very large buffers must be chunked by callers. Rolling checksum arithmetic intentionally wraps unsigned values; changing types can alter results. Boundary behavior is part of delta efficiency and compatibility expectations.

Test signals: No direct test in this subset. Algorithmic tests should verify stable boundaries for known byte sequences and edge cases with no boundary.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/bupsplit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/bupsplit.h -->
# sources/cloud-native/ostree/src/libostree/bupsplit.h

Purpose: This header declares the bupsplit rolling-checksum API and its chunk/window sizing constants.

Important APIs, types, and functions: It defines `BUP_BLOBBITS` as 13, `BUP_BLOBSIZE` as `1 << BUP_BLOBBITS`, `BUP_WINDOWBITS` as 7, and `BUP_WINDOWSIZE` as `1 << (BUP_WINDOWBITS - 1)`. It declares `uint32_t bupsplit_sum(uint8_t *buf, size_t ofs, size_t len)` and `int bupsplit_find_ofs(const unsigned char *buf, int len, int *bits)` inside an `extern "C"` block for C++ callers.

Control flow: No executable flow beyond preprocessor include guards and C++ linkage guards.

State and persistence behavior: None. Constants define deterministic algorithm parameters used by `bupsplit.c`.

Dependencies and integration points: Includes `<stdint.h>` and `<sys/types.h>`. Included by `bupsplit.c` and any libostree code that needs chunk boundary detection.

Risks: Changing constants changes chunk boundaries and can affect delta size, compatibility, and performance. The API exposes mutable `uint8_t *` for `bupsplit_sum` even though implementation only reads, which may limit const-correctness.

Test signals: Consumers should test against known chunk offsets and sums; no direct signal in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/bupsplit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-1.pc.in -->
# sources/cloud-native/ostree/src/libostree/ostree-1.pc.in

Purpose: This pkg-config template describes how external C/Rust build systems discover libostree compiler and linker flags.

Important APIs, types, and functions: It defines substituted variables `prefix`, `exec_prefix`, `libdir`, `includedir`, `features`, and `cliextdir`. Metadata includes `Name: OSTree`, description, version, public requirement `gio-unix-2.0`, private requirements/libs substitutions, `Libs: -L${libdir} -lostree-1`, and `Cflags: -I${includedir}/ostree-1`.

Control flow: Meson/configure-time substitution produces the final `.pc` file; pkg-config later reads the static fields.

State and persistence behavior: Installed development metadata persists on the system and directly affects downstream compilation. It does not execute code.

Dependencies and integration points: Used by `pkg-config --cflags ostree-1` in `sys/tests/abi.rs`, by downstream C projects, and by Rust build scripts or tests needing libostree headers.

Risks: Missing public/private dependencies or wrong include/lib paths break downstream builds. Incorrect `features` can mislead feature detection. Public vs private dependency placement affects static linking.

Test signals: ABI tests in this subset use pkg-config cflags, so their successful compilation indirectly validates the installed `.pc` metadata.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-1.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-async-progress.c -->
# sources/cloud-native/ostree/src/libostree/ostree-async-progress.c

Purpose: This C file implements `OstreeAsyncProgress`, a thread-safe GObject used by asynchronous libostree operations to publish progress key/value state and emit coalesced change notifications in the caller's thread-default `GMainContext`.

Important APIs, types, and functions: The object stores `GMutex lock`, `GMainContext *maincontext`, `GSource *idle_source`, `GHashTable *values`, and `gboolean dead`. Public APIs include `ostree_async_progress_new`, `new_and_connect`, `get_variant`, `get_uint`, `get_uint64`, varargs `get`, `set_status`, `get_status`, varargs `set`, `set_variant`, `set_uint`, `set_uint64`, `copy_state`, and `finish`. Class setup registers the `changed` signal. `ensure_callback_locked` creates and attaches an idle source; `idle_invoke_async_progress` clears the source and emits `changed`.

Control flow: Setters lock the object, ignore updates after `dead`, compare new `GVariant` values to existing values, replace only changed entries, and schedule one idle callback for one or more changes. The idle callback runs in the captured main context and emits `changed`. Getters lock and either ref/copy variants or atomically unpack multiple varargs values. `finish` marks the object dead, destroys pending idle source, and emits one final `changed` if a callback was pending.

State and persistence behavior: State is in-memory only and scoped to the progress object. Keys are interned to `GQuark` pointers in the hash table and values are owned `GVariant` refs. No disk persistence occurs, but progress state influences UI/CLI feedback and async operation observers.

Dependencies and integration points: Depends on GLib/GObject, `config.h`, `ostree-async-progress.h`, and `libglnx` hash iteration macros. It is exposed through the public C API and raw Rust FFI declarations in `sys/src/lib.rs`. Repo pull and other asynchronous operations accept `OstreeAsyncProgress *`.

Risks: Varargs APIs require exact key/format/value sequences and NULL termination; misuse can assert or corrupt reads. `ostree_async_progress_get` asserts keys exist and formats match, so callers must know state shape. Thread safety depends on holding the mutex around hash table access and careful idle source lifetime management. Calling `copy_state` does not notify destination watchers by design, which can surprise consumers.

Test signals: No direct test in this subset, but Rust FFI ABI layout checks include `OstreeAsyncProgressClass`, and higher-level pull/progress tests elsewhere should validate signal behavior and status values.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-async-progress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-async-progress.h -->
# sources/cloud-native/ostree/src/libostree/ostree-async-progress.h

Purpose: This public header declares the `OstreeAsyncProgress` GObject type, its class signal slot, and the progress key/value API implemented in `ostree-async-progress.c`.

Important APIs, types, and functions: It defines GObject type-check/cast macros, forward declares `OstreeAsyncProgress` and `OstreeAsyncProgressClass`, and defines the class struct with `GObjectClass parent_class` and `void (*changed)(OstreeAsyncProgress *, gpointer)`. Public declarations include constructors, status getters/setters, varargs `get`/`set`, typed uint/uint64 accessors, variant accessors, `finish`, and `copy_state`.

Control flow: Header-only flow is limited to macro expansion and C linkage via `G_BEGIN_DECLS`/`G_END_DECLS`. Runtime behavior is in the C implementation.

State and persistence behavior: The header exposes an opaque instance type, preventing callers from depending on internal fields. It defines an in-memory progress object API and no persistence contract.

Dependencies and integration points: Includes `ostree-types.h` for GLib type dependencies and `_OSTREE_PUBLIC`. Consumed by libostree users, GIR generation, and Rust FFI generation in `sys/src/lib.rs`.

Risks: ABI stability of the class struct matters because the raw Rust binding mirrors `OstreeAsyncProgressClass`. Adding virtual slots changes layout and must be reflected in generated bindings/tests. Varargs declarations must remain annotated as NULL-terminated for compiler diagnostics and introspection expectations.

Test signals: `sys/tests/layout.c` and `abi.rs` compare `OstreeAsyncProgressClass` size/alignment with Rust. Behavioral signal depends on async progress tests outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-async-progress.h -->
