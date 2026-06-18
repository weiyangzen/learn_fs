# subset-b-000239 Research

Grouped research report for the requested OSTree manpage, manual-test, documentation-build, Rust binding configuration, and generated Rust binding files. Each section preserves the source path and is bounded by the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/man/ostree-static-delta.xml -->
# sources/cloud-native/ostree/man/ostree-static-delta.xml

Purpose: This DocBook refentry defines the `ostree static-delta` manual page, documenting how users list, inspect, delete, generate, apply offline, and verify static delta files. Its most important contract is CLI semantics for `generate --to=REV`, optional `--from=REV`, `--empty`, `--max-usize`, and signature-related options.

Important APIs and commands: The documented subcommands are `list`, `show`, `delete`, `generate`, `apply-offline PATH [KEY-ID...]`, and `verify STATIC-DELTA [KEY-ID...]`. Signature API surface is user-facing rather than code-level: `--sign-type=ENGINE`, `--sign=KEY-ID`, positional `KEY-ID`, `--keys-file`, and `--keys-dir`. Engines documented here are `ed25519` and `dummy`; ed25519 keys are base64 encoded secret/public keys, while dummy keys are ASCII strings.

Control flow and state: The page describes a lifecycle: generate a delta from a source revision or from scratch to a target revision, publish/update repository metadata separately, then clients can apply or verify the delta. Persistent state is repository static delta content plus any signatures or key material. `--keys-dir` ties verification to a filesystem key hierarchy with well-known and revoked keys.

Dependencies and integration points: Integrates with repository revision resolution, static delta storage, summary metadata, offline delta application, signature verification engines, and file/dir based key discovery. It cross-links implicitly to `ostree summary` because generated deltas usually require summary refresh for distribution.

Risks: Documentation drift is high because signature engines and defaults evolve. The page describes key encodings but not operational key protection, revocation semantics, or concrete file format expectations for `--keys-dir`. The example is minimal and does not demonstrate generation or verification, so users may miss that summary metadata may need regeneration.

Test signals: Manual or integration tests should assert that documented options map to real CLI options, that ed25519 `--keys-file` accepts one base64 public key per line, that default sign type is still ed25519, and that generated deltas can be pulled with `--require-static-deltas`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/man/ostree-static-delta.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/man/ostree-summary.xml -->
# sources/cloud-native/ostree/man/ostree-summary.xml

Purpose: This DocBook refentry documents `ostree summary`, the command for regenerating or viewing the optional repository `summary` metadata file. It explains that summaries describe available branches and enable atomic metadata updates across multiple commits.

Important APIs and commands: The synopsis exposes two modes: update mode with `--update/-u`, optional `--add-metadata/-m KEY=VALUE`, GPG signing options `--gpg-sign` and `--gpg-homedir`, and generic signing options `--sign` plus `--sign-type`; and read mode with mutually required `--view/-v` or `--raw`. Additional metadata values must use GVariant text format and namespaced keys.

Control flow and state: Update mode writes repository metadata. If a collection ID is configured, it also updates the `ostree-metadata` branch for that collection ID with a commit containing the metadata, signed when the summary is signed. View and raw modes only read persisted summary bytes.

Dependencies and integration points: Depends on repository refs, summary file serialization, GVariant metadata parsing, GPG signing, newer signature engines such as ed25519/dummy, and collection ID metadata branch handling. The command is central to remote clients, static delta publication, and peer-to-peer metadata discovery.

Risks: Metadata parsing is user-sensitive because malformed GVariant text or unnamespaced keys can create hard-to-debug repository metadata. Signing behavior spans legacy GPG and newer sign API engines, so docs can drift from implementation defaults. Collection-ID side effects mean `--update` changes more than the single `summary` file in configured repos.

Test signals: CLI tests should cover `summary -u`, repeated `--add-metadata`, `--view`, `--raw`, signed summaries, and collection-ID repositories where the metadata branch is updated. Golden-output tests can validate the human-readable summary format shown in the example.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/man/ostree-summary.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/man/ostree.repo-config.xml -->
# sources/cloud-native/ostree/man/ostree.repo-config.xml

Purpose: This DocBook refentry documents the OSTree repository `config` keyfile. It is the main user-editable repository configuration contract, covering global `[core]`, per-remote `[remote "name"]`, `[sysroot]`, and experimental `[ex-integrity]` sections.

Important configuration keys: Core keys include `mode`, `repo_version`, `auto-update-summary`, deprecated `commit-update-summary`, `fsync`, `per-object-fsync`, `min-free-space-percent`, `min-free-space-size`, `add-remotes-config-dir`, `payload-link-threshold`, `collection-id`, `locking`, `lock-timeout-secs`, `default-repo-finders`, and `no-deltas-in-summary`. Remote keys include `url`, `contenturl`, `branches`, `proxy`, `gpg-verify`, `gpg-verify-summary`, TLS settings, `http2`, `unconfigured-state`, and `custom-backend`. Sysroot keys include `readonly`, `bootloader`, `boot-counting-tries`, `bls-append-except-default`, and `bootprefix`.

Control flow and state: This file is declarative state consumed by libostree and CLI commands when opening repositories, resolving remotes, pulling objects, checking signatures, updating summaries, locking repositories, and writing bootloader/sysroot state. Remotes may also persist outside the repo in `/etc/ostree/remotes.d/*.conf`.

Dependencies and integration points: Integrates with GLib keyfile parsing, repository open/init code, HTTP/TLS stack, GPG verification, summary generation, static delta indexes, collection-ID peer discovery, Flatpak/libostree multi-process locking, BLS bootloader handling, and OS vendor subscription hooks via `unconfigured-state` or `custom-backend`.

Risks: Several keys affect durability and security. Disabling `fsync` weakens crash safety; `tls-permissive=false` should remain the safe default; `gpg-verify=false` removes commit signature enforcement; `min-free-space-*` semantics exclude metadata objects; and `lock-timeout-secs=300` is called out as flake-prone. Documentation must stay aligned with defaults because these options control production update safety.

Test signals: Config parser tests should exercise precedence between `min-free-space-size` and percent, deprecated alias behavior, remote directory inclusion rules, mirrorlist URL parsing, TLS option propagation, locking timeout behavior, and summary delta-index behavior for `no-deltas-in-summary`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/man/ostree.repo-config.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/man/ostree.repo.xml -->
# sources/cloud-native/ostree/man/ostree.repo.xml

Purpose: This DocBook refentry introduces OSTree repository structure and layout. It frames an OSTree repository as a git-like content-addressed object store for filesystem trees, with OS-specific metadata such as uid, gid, permissions, and extended attributes.

Important concepts: The key public concepts are repository modes `bare`, `bare-user`, and `archive-z2`, the default system repository location, and the fact that the only user-editable component is the `config` file. It directs detailed configuration semantics to `ostree.repo-config(5)`.

Control flow and state: This is a documentation-only file, but it defines persistent repository state expectations: object storage, checkouts, archive transport, and default repository discovery. The documented default lookup path is used by CLI commands and many API calls when no command-line repository or `OSTREE_REPO` environment variable is specified.

Dependencies and integration points: Integrates with `ostree(1)`, repository initialization, checkout logic, archive serving over HTTP, and repository config parsing. It is the conceptual entry point for users before the detailed config manpage.

Risks: Default repository paths have changed historically across `/ostree/repo` and `/sysroot/ostree/repo` contexts, so this page must remain synchronized with actual CLI lookup behavior. The mode list is brief and may omit newer modes if implementation expands.

Test signals: Documentation tests should verify referenced manpage names and modes against the implementation and generated manpage set. CLI smoke tests can assert default repository discovery with `--repo`, `OSTREE_REPO`, current-directory repos, and the system repo.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/man/ostree.repo.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/man/ostree.xml -->
# sources/cloud-native/ostree/man/ostree.xml

Purpose: This is the top-level `ostree(1)` manpage. It explains OSTree as a system for managing multiple bootable, versioned, read-only filesystem trees installed under `/ostree`, and it indexes administrative and regular subcommands.

Important commands and concepts: Global options are `--repo`, `--verbose`, and `--version`. It lists administrative commands such as cleanup, deploy, init-fs, os-init, status, switch, undeploy, and upgrade, plus repository/tree commands such as cat, checkout, checksum, commit, config, create-usb, diff, find-remotes, fsck, init, log, ls, prune, pull, refs, remote, reset, rev-parse, show, static-delta, and summary. The terminology section defines branch, checksum, commit, ref, rev/refspec, and SHA256.

Control flow and state: The manpage documents the OSTree operating model: the running tree is not modified in place; upgrades prepare a new tree, perform a three-way config merge, and activate after reboot. Repository discovery falls back from explicit `--repo` to current directory, `OSTREE_REPO`, and then the system repository.

Dependencies and integration points: Integrates the CLI namespace, sysroot deployment model, repository model, bootable OS deployment workflow, GPG trust roots, per-remote keyrings, and subcommand manpages. It also describes trust integration through `/usr/share/ostree/trusted.gpg.d`, remote `gpgkeypath`, and per-remote trusted keyrings.

Risks: Because this file is an index, stale command lists or repository paths can mislead users broadly. Security-sensitive GPG guidance must remain accurate, especially the warning that private keys should not be stored in trusted public key directories. There is a typo in the SHA256 glossary text ("bites") that is documentation quality risk, not runtime risk.

Test signals: Manpage generation should verify every cited `ostree-*` and `ostree-admin-*` page exists. CLI integration tests should cover repository discovery order, `--version` feature output, GPG key import paths, and read-only deployment assumptions.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/man/ostree.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/man/rofiles-fuse.xml -->
# sources/cloud-native/ostree/man/rofiles-fuse.xml

Purpose: This DocBook refentry documents `rofiles-fuse`, a FUSE helper that exposes a view where directories can be changed but existing files are immutable. It protects hardlink-based OSTree checkouts from accidental in-place file mutation.

Important commands and behavior: The command syntax is `rofiles-fuse SRCDIR MNTPOINT`. The documented workflow mounts a checkout, lets arbitrary tools create, delete, or replace entries through the mount, unmounts with `fusermount -u`, and commits with `ostree commit --link-checkout-speedup`.

Control flow and state: Runtime state is a FUSE mount projecting changes back to the source directory while preventing mutation of existing file content. Persistent state is the changed checkout directory and the subsequent OSTree commit. It is especially intended for package script execution where writes must not corrupt repository hardlinks.

Dependencies and integration points: Depends on FUSE, `fusermount`, OSTree checkout hardlink behavior, and commit acceleration through `--link-checkout-speedup` or equivalent API. It bridges arbitrary filesystem mutating tools with OSTree's immutable object-store assumptions.

Risks: Mount lifecycle is critical; failing to unmount before committing or cleanup can leave confusing state. The helper protects file immutability but still permits directory-level operations, so tests must ensure replacements break hardlinks rather than mutate them. User documentation should make clear this is not a general sandbox.

Test signals: Manual tests should check that writes to new files, directory creation, deletion, and replacement are reflected in `SRCDIR`; direct mutation of original file content must fail or become a safe replacement; and commits with `--link-checkout-speedup` remain valid under `ostree fsck`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/man/rofiles-fuse.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/manual-tests/static-delta-generate-crosscheck.sh -->
# sources/cloud-native/ostree/manual-tests/static-delta-generate-crosscheck.sh

Purpose: This manual Bash test cross-checks static delta generation variants against a test repository. It verifies that a client can pull from an initial revision to a target revision using required static deltas and pass `ostree fsck`.

Important functions and commands: Inputs are repository path and branch. It resolves `from` as the branch parent and `to` as the branch head. `cleanup_tmpdir` removes the temporary workspace unless `PRESERVE_TMP` is set. `fatal` and `assert_streq` provide simple assertions. `validate_delta_options` initializes a bare-user test repo, disables fsync for speed, adds a local file remote with GPG verification disabled, generates a delta with supplied options, updates the summary, pulls the old revision, pulls the branch with `--require-static-deltas`, checks revision equality, runs `fsck`, and removes the test repo.

Control flow and state: The script uses `set -euo pipefail`, creates a `/var/tmp/ostree-delta-check.*` directory, marks it with `.tmp`, and optionally registers an EXIT trap. It invokes `validate_delta_options` three times: default, `--inline`, and `--disable-bsdiff`.

Dependencies and integration points: Depends on the `ostree` CLI, revision syntax with `^`, static delta generation, summary updates, local file remotes, pull behavior with required deltas, and repository fsck. It directly validates the manpage behavior for static delta generation.

Risks: Arguments are mostly unquoted, so paths or branch names with spaces would break. `assert_streq` uses unquoted `test`, which can misbehave on empty or special values. It disables fsync, which is acceptable for a temporary manual test but not representative of durability. Running against large repos may consume significant `/var/tmp` space.

Test signals: Success is no command failure under `set -e` and matching rev-parse outputs before and after delta pull. It should be run against content with meaningful parent/child revisions and should be extended if new delta generation options are added.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/manual-tests/static-delta-generate-crosscheck.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/manual-tests/upgrade-loop.js -->
# sources/cloud-native/ostree/manual-tests/upgrade-loop.js

Purpose: This GJS manual test repeatedly alternates deployment targets to stress OSTree sysroot upgrade/downgrade behavior. It is designed for an external supervisor to kill and restart the script and verify sysroot consistency.

Important APIs and functions: It imports `imports.gi.OSTree`, creates `OSTree.Sysroot.new_default()`, loads deployments, gets the active deployment checksum and origin, parses the origin refspec with `OSTree.parse_refspec`, pulls the remote ref, resolves the newest revision, and then loops through `sysroot.cleanup`, commit parent lookup, `repo.pull`, `sysroot.origin_new_from_refspec`, `sysroot.deploy_tree`, `sysroot.write_deployments`, `sysroot.load`, and another cleanup.

Control flow and state: Initial state is the current booted/default deployment. If the starting revision is current, the target is the parent commit, otherwise the target is the newly resolved revision. Each loop writes a two-entry deployment list `[newDeployment, firstDeployment]`, then reloads sysroot state and repeats from the new default.

Dependencies and integration points: Depends on GJS GI bindings, libostree sysroot APIs, repository pull/resolve/load_variant behavior, commit parent metadata, deployment origin keyfiles, and bootloader/sysroot deployment persistence. It exercises the same deployment model documented in `ostree(1)`.

Risks: The loop is intentionally infinite and mutates system deployment state, so it must only run in controlled test machines or VMs. It assumes at least one deployment, a valid origin refspec, a pullable remote, and a parent commit when downgrading. It does not install signal handlers or transactional external assertions itself.

Test signals: The visible markers `DEPLOY BEGIN revision=...` and `DEPLOY END revision=...` let a harness observe progress. A robust test harness should reboot or restart mid-loop, then check deployment list integrity and `ostree admin status`/`fsck`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/manual-tests/upgrade-loop.js -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/mkdocs.yml -->
# sources/cloud-native/ostree/mkdocs.yml

Purpose: This MkDocs configuration defines the OSTree documentation site name and navigation tree. It maps top-level pages and manual chapters into a stable documentation structure.

Important keys: `site_name` is `OSTree`. The `pages` list includes Home, Contributing, Contributing Tutorial, and a Manual group with introduction, repository, deployments, atomic upgrades, adapting existing systems, formats, build systems/repos, repository management, and related projects.

Control flow and state: There is no runtime control flow. The file is declarative input to MkDocs; persistent output is the generated static documentation site. Navigation order in this file controls user-facing site layout.

Dependencies and integration points: Depends on MkDocs' legacy `pages` configuration shape and the referenced Markdown files. It complements the DocBook manpages by presenting guide-style documentation.

Risks: Modern MkDocs prefers `nav`; if the configured MkDocs version changes, this file may need migration. Any missing referenced Markdown file breaks or degrades docs builds. Navigation can drift from manpage coverage if new manuals are added but not listed here.

Test signals: Documentation CI should run `mkdocs build` and fail on missing files or config deprecations. Link-checking should verify the listed manual pages still exist and are reachable.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/mkdocs.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/.ci/generate-test-jobs.sh -->
# sources/cloud-native/ostree/rust-bindings/.ci/generate-test-jobs.sh

Purpose: This shell generator emits GitLab CI YAML jobs for every Cargo feature in the Rust bindings except `dox`. It keeps feature test coverage in sync with `Cargo.toml` metadata.

Important functions and commands: `get_features` runs `cargo read-manifest` and pipes JSON to `jq`, extracting feature keys, excluding `dox`, and printing a space-delimited list. The script emits an `include: /.ci/gitlab-ci-base.yml` header, then writes one `test_feature_${feature}` job per feature that extends `.fedora-ostree-devel` and runs `cargo test --verbose --workspace --features ${feature}`.

Control flow and state: The script is deterministic given the Cargo manifest. It produces CI YAML on stdout and writes no files itself. `set -eu` makes missing commands or unset variables fail early.

Dependencies and integration points: Depends on Cargo, `jq`, GitLab CI includes, and base job definitions in `.ci/gitlab-ci-base.yml`. It integrates feature-gated generated bindings with CI so each version feature can be compiled and tested.

Risks: Feature names are interpolated into job names and shell commands without quoting or sanitization; Cargo feature names are usually safe but unusual names could produce invalid YAML. The generated jobs test each feature individually, not all feature combinations. Missing `jq` or `cargo` fails generation.

Test signals: CI should validate the generated YAML and run at least one generated feature job. A local check can compare generated output after feature changes to ensure newly added version gates get test jobs.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/.ci/generate-test-jobs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/.ci/gitlab-ci-base.yml -->
# sources/cloud-native/ostree/rust-bindings/.ci/gitlab-ci-base.yml

Purpose: This GitLab CI base file defines reusable Rust binding test environments with sccache. It provides one Fedora Rawhide/libostree-devel lane and one generic Rust image lane with Debian `libostree-dev`.

Important jobs and variables: `.sccache` sets `SCCACHE_URL`, `CARGO_TARGET_DIR`, `CARGO_HOME`, `SCCACHE_DIR`, `RUSTC_WRAPPER`, and cache paths. `.fedora-ostree-devel` uses `registry.fedoraproject.org/fedora:rawhide`, installs `cargo rust ostree-devel`, installs sccache, and creates a pkg-config symlink workaround. `.rust-ostree-devel` uses `rust`, installs `libostree-dev`, and installs sccache.

Control flow and state: CI job state is confined to GitLab workspaces and caches for cargo artifacts and sccache. The before-script prepares system dependencies before generated jobs run `cargo test`.

Dependencies and integration points: Integrates GitLab CI, Fedora/Debian package managers, libostree development packages, Rust toolchain, pkg-config, curl, tar, and sccache. The generated test jobs extend `.fedora-ostree-devel`.

Risks: Rawhide is intentionally moving and can break bindings when libostree or packaging changes. Downloading sccache from GitHub during CI adds network dependency and supply-chain surface. The pkg-config symlink workaround is fragile and may become wrong as Fedora changes.

Test signals: Successful generated feature jobs are the main signal. CI logs should show package install success, sccache available as `RUSTC_WRAPPER`, and `pkg-config` locating ostree development metadata.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/.ci/gitlab-ci-base.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/Makefile -->
# sources/cloud-native/ostree/rust-bindings/Makefile

Purpose: This Makefile orchestrates generation of Rust bindings from GIR metadata, fetching GIR inputs, and merging LGPL documentation into vendored docs.

Important targets and variables: Variables pin `GIR_REPO`, `GIR_VERSION`, `GIR_FILES_VERSION`, `OSTREE_REPO`, `OSTREE_VERSION`, and `RUSTDOC_STRIPPER_VERSION`. `all` runs `gir`. `target/tools/bin/gir` installs gtk-rs `gir` at a pinned revision. `gir` runs generation with `conf/ostree-sys.toml` and `conf/ostree.toml`. `gir-report` runs `gir -m not_bound`. `merge-lgpl-docs` installs `rustdoc-stripper`, runs gir doc mode, and writes `target/vendor.md`. `update-gir-files` refreshes GLib/Gio/GObject/GModule GIR files and symlinks local `OSTree-1.0.gir`.

Control flow and state: Persistent/generated state includes `target/tools`, downloaded `gir-files/*.gir`, symlinked `gir-files/OSTree-1.0.gir`, generated Rust binding code, and `target/vendor.md`.

Dependencies and integration points: Depends on Cargo install, curl, gtk-rs/gir, rustdoc-stripper, upstream GIR files, and a local OSTree GIR file. It is the bridge between libostree introspection metadata and the generated `src/auto` modules.

Risks: Pinned generator versions improve reproducibility but can lag new GIR features. Network fetches can fail or change availability. Regeneration can cause broad diffs in generated files, so commits should separate generator updates from manual wrapper changes.

Test signals: `make gir` should be clean or produce expected diffs; `make gir-report` should identify intended not-bound APIs; CI feature tests should compile the regenerated bindings.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/conf/ostree-sys.toml -->
# sources/cloud-native/ostree/rust-bindings/conf/ostree-sys.toml

Purpose: This GIR configuration generates the low-level `ostree-sys` Rust FFI crate for OSTree 1.0.

Important settings: `work_mode = "sys"`, `library = "OSTree"`, `version = "1.0"`, `target_path = "../sys"`, and `single_version_file = true`. External libraries are GLib, GObject, and Gio. `girs_directories` points to `../gir-files`.

Control flow and state: This file is consumed by `gir` from the Makefile and controls which raw C symbols/types become Rust FFI. It writes generated sys bindings under `../sys` and does not execute runtime logic.

Dependencies and integration points: Integrates the OSTree GIR file with gtk-rs sys generation and links through GLib/GObject/Gio FFI crates. The normal binding config depends on the generated sys layer.

Risks: The ignore list removes private, version-dependent, and build-dependent symbols such as private stream classes, signing subclasses, and version constants. If a symbol moves from private to public or vice versa, the sys surface can become incomplete or expose unsupported API. Ignoring build-dependent constants avoids unstable bindings but means callers need other ways to query features.

Test signals: Regenerating sys bindings and compiling downstream `ostree` Rust bindings is the main test. ABI/link tests should catch missing symbols, while GIR report review should catch newly exposed private APIs.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/conf/ostree-sys.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/conf/ostree.toml -->
# sources/cloud-native/ostree/rust-bindings/conf/ostree.toml

Purpose: This GIR configuration generates the safe/high-level Rust `ostree` crate bindings for OSTree 1.0. It defines generated, manual, and ignored APIs and applies per-object fixes for nullability, concurrency, string typing, and broken GIR shapes.

Important settings: `work_mode = "normal"`, `target_path = ".."`, `doc_target_path = "../target/vendor.md"`, `deprecate_by_min_version = true`, `trust_return_value_nullability = true`, and `generate_display_trait = true`. The `generate` list includes core objects, enums, flags, repo/sysroot helpers, signing, static delta options, and finder types. The `manual` list includes GLib/Gio types plus hand-written OSTree wrappers such as `KernelArgs`, checkout options, transaction stats, and sysroot deploy options.

Control flow and state: The Makefile feeds this config into `gir`, producing generated modules under `src/auto`. Per-object rules ignore functions that are unsafe, deprecated, private, impossible to represent cleanly, or better handled manually. Feature gates are derived from GIR versions.

Dependencies and integration points: Integrates with gtk-rs/gir, GIR metadata, manual wrapper modules, `ostree-sys`, GLib/Gio crates, docs generation, and CI feature testing. It is the authority for which libostree APIs Rust callers see.

Risks: `trust_return_value_nullability` makes GIR accuracy critical. Ignored APIs can hide functionality, while incorrectly generated APIs can expose unsound lifetimes, invalid arrays, or raw pointer misuse. The config explicitly disables several async finder APIs and checksum APIs due to lifetime/custom checksum concerns, which should be revisited when GIR or manual wrappers improve.

Test signals: `gir-report` for not-bound APIs, compile tests across feature gates, manual wrapper tests for ignored APIs, and diff review after GIR updates. Any change here should be validated against generated `src/auto/mod.rs` exports.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/conf/ostree.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/async_progress.rs -->
# sources/cloud-native/ostree/rust-bindings/src/auto/async_progress.rs

Purpose: Generated Rust wrapper for `OstreeAsyncProgress`, exposing progress state used by asynchronous libostree operations.

Important APIs: `AsyncProgress::new`, `copy_state` behind `v2019_6`, `finish`, getters for `status`, `uint`, `uint64`, and `variant`, setters for status/integers/variant values, and `connect_changed` for the `changed` signal. Varargs C APIs `get` and `set`, and `new_and_connect`, are left commented as unimplemented.

Control flow and state: The object stores mutable progress key/value state in the underlying GObject. Rust methods translate strings, variants, and numeric values across FFI. `connect_changed` boxes a Rust closure and registers a C trampoline through `connect_raw`.

Dependencies and integration points: Depends on `glib`, `gio` conventions, `ffi::ostree_async_progress_*`, feature gates, and signal handling. It is used by pull, checkout, and other async APIs to observe or propagate progress.

Risks: Signal connection uses unsafe trampoline plumbing and boxed closure ownership; leaks or invalid callbacks would be serious. Key names are stringly typed and not validated here. Varargs APIs are unavailable, so callers only get typed helper coverage.

Test signals: Compile under base and version features, connect a changed handler, set/get typed values, call `finish`, and validate `copy_state` under `v2019_6`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/async_progress.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/blob_reader.rs -->
# sources/cloud-native/ostree/rust-bindings/src/auto/blob_reader.rs

Purpose: Generated wrapper for the `OstreeBlobReader` interface, exposing blob-reading capability to Rust implementors and users.

Important APIs: `BlobReader` is a `glib::wrapper!` interface with `BlobReader::NONE` and extension trait `BlobReaderExt`. Under feature `v2016_5`, `read_blob` returns `Result<Option<glib::Bytes>, glib::Error>` from `ostree_blob_reader_read_blob`.

Control flow and state: The wrapper performs a synchronous FFI call with optional `gio::Cancellable`, converts GLib errors into `Result`, and converts nullable bytes into `Option`.

Dependencies and integration points: Depends on GLib object/interface mechanics, Gio cancellables, and libostree blob reader implementations. It can be used wherever libostree exposes objects implementing this interface.

Risks: A nullable successful result is represented as `Ok(None)`, so callers must not assume bytes are always returned. Interface implementor behavior is outside this wrapper. Feature gating means code must enable `v2016_5` for the actual read method.

Test signals: Feature-gated compile tests and an integration object implementing/providing `BlobReader` should verify bytes and cancellation/error paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/blob_reader.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/bootconfig_parser.rs -->
# sources/cloud-native/ostree/rust-bindings/src/auto/bootconfig_parser.rs

Purpose: Generated wrapper for `OstreeBootconfigParser`, the object used to parse, mutate, and write bootloader entry style configuration.

Important APIs: `new`, `clone`, `get`, `set`, `parse`, `parse_at`, `write`, `write_at`, `tries_done`, `overlay_initrds`/`set_overlay_initrds` behind `v2020_7`, and `tries_left` behind `v2025_2`.

Control flow and state: Parser instances hold key/value bootconfig state in the underlying GObject. `parse`/`parse_at` load config from a `gio::File` or directory fd/path pair. `write`/`write_at` persist current state. Methods follow the GLib error convention and assert error/null consistency in debug builds.

Dependencies and integration points: Depends on Gio files/cancellables, GLib string/vector conversions, and deployment bootconfig APIs. It integrates with `Deployment::bootconfig` and sysroot bootloader entry management.

Risks: File-descriptor based `parse_at`/`write_at` depend on caller-provided directory fd correctness. Version-gated boot counting fields must match installed libostree. The wrapper does not validate arbitrary keys or values.

Test signals: Parse/write round trips, `parse_at`/`write_at` with temporary dirs, overlay initrd round trips under `v2020_7`, and boot-counting field tests under relevant features.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/bootconfig_parser.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/collection_ref.rs -->
# sources/cloud-native/ostree/rust-bindings/src/auto/collection_ref.rs

Purpose: Generated boxed wrapper for `OstreeCollectionRef`, representing a collection ID plus ref name for peer-to-peer and collection-aware repository operations.

Important APIs: `CollectionRef::new(collection_id, ref_name)`, private wrapper methods for equality and hash, plus Rust `PartialEq`, `Eq`, and `Hash` implementations that delegate to libostree.

Control flow and state: Construction allocates a boxed C struct; cloning/freeing use GLib boxed copy/free with the OSTree type. Equality and hash are computed by libostree, preserving C semantics.

Dependencies and integration points: Feature-gated by `v2018_6` in `mod.rs`. Integrates with collection-ID refs, repo finders, summary metadata, and any Rust APIs that use collection-aware references.

Risks: Hash implementation hashes the C-provided `u32` hash value into Rust's hasher, so it mirrors libostree equality but compresses identity through a 32-bit value. `collection_id` is optional, so callers must understand local refs versus collection refs.

Test signals: Equality/hash property tests for same/different collection IDs and ref names, compile under `v2018_6`, and integration with collection-aware repo lookups.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/collection_ref.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/commit_sizes_entry.rs -->
# sources/cloud-native/ostree/rust-bindings/src/auto/commit_sizes_entry.rs

Purpose: Generated boxed wrapper for `OstreeCommitSizesEntry`, representing object size metadata for a commit.

Important APIs: `CommitSizesEntry::new(checksum, objtype, unpacked, archived)` returns `Option<CommitSizesEntry>` and stores checksum, `ObjectType`, unpacked size, and archived size in the underlying C struct.

Control flow and state: The wrapper uses libostree copy/free functions for boxed ownership. Construction may return null, represented as `None`, if libostree rejects inputs.

Dependencies and integration points: Feature-gated by `v2020_1`. Used by `functions::commit_get_object_sizes`, which returns vectors of these entries from commit metadata.

Risks: There are no field accessors in this generated file, so usefulness depends on derived traits and other generated/manual APIs. Caller-provided checksum/object type must be valid. Size units and semantics are inherited from libostree.

Test signals: Construct entries with valid checksums/object types, compile `commit_get_object_sizes` under `v2020_1`, and verify vector conversion does not leak or double free.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/commit_sizes_entry.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/constants.rs -->
# sources/cloud-native/ostree/rust-bindings/src/auto/constants.rs

Purpose: Generated Rust constants exposing libostree string constants as `&glib::GStr`.

Important APIs: Constants include GVariant format strings for commits, dirmeta, filemeta, GPG keys, summary, summary signatures, and trees; commit metadata keys such as version, end-of-life, ref/collection binding, architecture, source title; deployment and repo metadata keys; signing engine names; and `PATH_BOOTED`.

Control flow and state: There is no runtime control flow beyond unsafe construction of static `GStr` references from nul-terminated FFI constants. Feature gates expose constants only for libostree versions that define them.

Dependencies and integration points: Depends on `ostree-sys` constants and GLib `GStr`. Used across Rust bindings when constructing metadata dictionaries, interpreting commit metadata, or selecting signature engines.

Risks: `from_utf8_with_nul_unchecked` assumes the FFI constants are valid UTF-8 and nul-terminated. That is appropriate for libostree constants but unsafe if GIR/sys metadata is wrong. Feature gates must match symbol availability to avoid link errors.

Test signals: Compile and link under minimum and feature-enabled libostree versions; metadata integration tests should use constants rather than duplicated string literals.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/constants.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/content_writer.rs -->
# sources/cloud-native/ostree/rust-bindings/src/auto/content_writer.rs

Purpose: Generated wrapper for `OstreeContentWriter`, a `gio::OutputStream` subclass used to write OSTree content and finish with a checksum.

Important APIs: The wrapper extends `gio::OutputStream` and exposes `finish(cancellable) -> Result<glib::GString, glib::Error>`, which calls `ostree_content_writer_finish`.

Control flow and state: Callers write bytes through the output stream interface, then call `finish` to finalize content and receive the checksum. Persistent effects are managed by the underlying writer, typically repository object storage.

Dependencies and integration points: Depends on Gio output streams, cancellables, GLib error translation, and libostree content writer internals. It likely integrates with repo write APIs that return a content writer.

Risks: Finalization order matters; dropping without `finish` may leave incomplete content depending on underlying implementation. The wrapper does not expose constructor APIs here, so lifecycle is controlled by other repo APIs.

Test signals: Integration tests should write content, call `finish`, validate checksum format, and verify cancellation/error handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/content_writer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/deployment.rs -->
# sources/cloud-native/ostree/rust-bindings/src/auto/deployment.rs

Purpose: Generated wrapper for `OstreeDeployment`, representing a bootable deployed tree in a sysroot.

Important APIs: `new`, `clone`, `equal`, getters for bootconfig, boot checksum/serial, commit checksum, deploy serial, index, origin, origin relpath, OS name, unlocked state, pinned/staged/finalization-lock/soft-reboot status by feature, setters for bootconfig, bootserial, index, and origin, plus static helpers `origin_remove_transient_state` and `unlocked_state_to_string`.

Control flow and state: Deployment objects hold sysroot deployment metadata. Some setters mutate object state in memory; sysroot APIs persist deployment lists and bootloader entries. Origin is a `glib::KeyFile`, connecting deployments back to remote/ref configuration.

Dependencies and integration points: Depends on `BootconfigParser`, `DeploymentUnlockedState`, GLib keyfiles, feature-gated libostree deployment APIs, and sysroot write/deploy flows. It is central to upgrade/downgrade behavior such as the manual `upgrade-loop.js`.

Risks: Deployment identity includes index, checksum, serials, and origin; changing setters without writing sysroot state has no persistent effect. Feature-gated status methods depend on runtime libostree support. Origin keyfiles can contain transient state that should be stripped where appropriate.

Test signals: Equality/hash behavior via libostree, clone/getter/setter round trips, origin keyfile persistence through sysroot writes, and feature-gated deployment state tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/deployment.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/diff_item.rs -->
# sources/cloud-native/ostree/rust-bindings/src/auto/diff_item.rs

Purpose: Generated shared wrapper for `OstreeDiffItem`, representing one modified item in directory/tree diffs.

Important APIs: The file only defines the shared boxed/reference-counted wrapper with `ostree_diff_item_ref`, `ostree_diff_item_unref`, and type lookup. It derives debug, equality, ordering, and hash traits.

Control flow and state: Instances are produced by diff functions and reference-counted through libostree. There are no accessors in this file, so detailed diff interpretation may require other APIs or formatted output.

Dependencies and integration points: Used by `functions::diff_dirs` and `diff_print` alongside added and removed `gio::File` arrays. Depends on libostree shared ref/unref semantics.

Risks: Derived ordering/hash on shared wrapper identity may not represent semantic file diff ordering. Lack of field accessors limits Rust-side inspection and may push callers toward print-based handling.

Test signals: Diff integration tests should produce modified items, pass them to `diff_print`, and ensure reference ownership is stable.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/diff_item.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/enums.rs -->
# sources/cloud-native/ostree/rust-bindings/src/auto/enums.rs

Purpose: Generated Rust enum mappings for libostree enum types, with conversion implementations between Rust variants and C integer values.

Important APIs: Enums include `DeploymentUnlockedState`, `GpgSignatureAttr`, `ObjectType`, `RepoCheckoutFilterResult`, `RepoCheckoutMode`, `RepoCheckoutOverwriteMode`, `RepoCommitFilterResult`, `RepoCommitIterResult`, `RepoMode`, `RepoRemoteChange`, and `StaticDeltaGenerateOpt`. Each is `#[non_exhaustive]`, copyable, comparable, hashable, and has hidden `__Unknown(i32)` preservation.

Control flow and state: Conversion is pure value mapping. `IntoGlib` maps Rust variants to FFI constants; `FromGlib` maps FFI constants back, retaining unknown values for forward compatibility.

Dependencies and integration points: These enums are used across repo checkout/commit/pull APIs, object parsing, deployment state, remote mutation, static delta generation, and GPG verification metadata.

Risks: Enum constant drift is a compatibility risk. The `__Unknown` variant prevents panics on newer libostree values but callers must handle non-exhaustive matches correctly. Feature gates such as `RepoCheckoutFilterResult` under `v2018_2` must align with symbol availability.

Test signals: Compile across feature gates, round-trip known values through `IntoGlib`/`FromGlib`, and include wildcard match coverage in downstream tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/enums.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/flags.rs -->
# sources/cloud-native/ostree/rust-bindings/src/auto/flags.rs

Purpose: Generated bitflag mappings for libostree flag types.

Important APIs: Flags include `ChecksumFlags`, `DiffFlags`, `GpgSignatureFormatFlags`, `RepoCommitModifierFlags`, `RepoCommitState`, `RepoCommitTraverseFlags`, `RepoListObjectsFlags`, `RepoListRefsExtFlags`, `RepoPruneFlags`, `RepoPullFlags`, `RepoResolveRevExtFlags`, `RepoVerifyFlags`, `SePolicyRestoreconFlags`, `SysrootSimpleWriteDeploymentFlags`, `SysrootUpgraderFlags`, and `SysrootUpgraderPullFlags`. `SysrootUpgraderFlags` additionally implements GLib value/param-spec traits.

Control flow and state: Each bitflags type converts to/from its raw C bitmask. `from_bits_truncate` drops unknown bits on inbound conversion, unlike enums that preserve unknown values.

Dependencies and integration points: Used throughout repo traversal, pruning, pulling, checkout, commit modification, verification, SELinux relabeling, sysroot deployment writes, and upgrader behavior. Depends on `glib::bitflags`, GLib value traits, and FFI constants.

Risks: Unknown future bits are truncated, so newer libostree flags can be silently lost when round-tripped through older bindings. Security-sensitive flags such as `UNTRUSTED`, `TRUSTED_HTTP`, `NO_GPG`, and `NO_SIGNAPI` require careful downstream use. Feature gates must match installed library support.

Test signals: Bitmask round-trip tests for known combinations, GLib `Value` tests for `SysrootUpgraderFlags`, and compile tests for feature-gated flags.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/flags.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/functions.rs -->
# sources/cloud-native/ostree/rust-bindings/src/auto/functions.rs

Purpose: Generated free-function bindings for libostree utility APIs that are not methods on a generated object.

Important APIs: Functions cover hardlink breaking, version checks, checksum variant conversion, commit metadata queries, bootable metadata generation, content file/stream parsing, directory metadata creation, directory diffing/printing, xattr reads, GPG error quark, metadata variant type lookup, object name serialization/deserialization, refspec parsing, archive/content stream conversion, and validation of checksums, collection IDs, remote names, revs, commits, dirmeta, dirtree, file modes, and object types.

Control flow and state: Most functions are synchronous FFI calls using GLib error pointers converted to `Result`. Some return owned strings, variants, streams, file info, xattrs, vectors, or tuple out-parameters. `break_hardlink` and xattr/content parse functions touch filesystem state; validation and serialization functions are pure.

Dependencies and integration points: Depends on Gio files/streams/file info/cancellables, GLib variants and errors, generated `DiffFlags`, `DiffItem`, `ObjectType`, and feature-gated `CommitSizesEntry`. These utilities underpin repository object parsing, validation, and filesystem conversion.

Risks: Array parameters for `diff_dirs` are subtle because C APIs may expect mutable output arrays while the generated signature accepts slices; this should be verified. Trust booleans in content parsing are security-sensitive. Out-parameter handling uses `MaybeUninit` and assumes C fills values on success.

Test signals: Unit/integration tests should cover validation failures, checksum/object round trips, refspec parse cases, content parse trusted/untrusted behavior, xattr reads, diff generation, and feature-gated commit size extraction.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/functions.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/gpg_verify_result.rs -->
# sources/cloud-native/ostree/rust-bindings/src/auto/gpg_verify_result.rs

Purpose: Generated wrapper for `OstreeGpgVerifyResult`, exposing results from GPG signature verification.

Important APIs: `count_all`, `count_valid`, `all(signature_index)`, `lookup(key_id)`, and feature-gated `require_valid_signature` under `v2016_6`. Lower-level `get` with attribute arrays is left unimplemented due to unsupported C array conversion.

Control flow and state: The object stores verification results produced elsewhere. Methods read counts, retrieve a signature result as a `glib::Variant`, look up a signature index by key ID, or enforce at least one valid signature via a GLib error-returning call.

Dependencies and integration points: Depends on GPG verification paths in repo/commit/summary operations, GLib variants, and generated `GpgSignatureAttr` constants for interpreting variant data.

Risks: `all` returns an untyped variant, so callers must know the expected schema. Missing generated `get` means fine-grained typed access is unavailable. `lookup` uses `MaybeUninit` only if the C call succeeds, which is correct but relies on C API contract.

Test signals: Verification tests should cover no signatures, invalid signatures, valid signatures, `lookup` by key ID, and `require_valid_signature` error behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/gpg_verify_result.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/mod.rs -->
# sources/cloud-native/ostree/rust-bindings/src/auto/mod.rs

Purpose: Generated module aggregator for the Rust `ostree` crate's auto-generated bindings. It declares generated modules and re-exports their public types, enums, flags, constants, and selected extension traits.

Important APIs: Re-exports core object wrappers such as `AsyncProgress`, `BootconfigParser`, `Deployment`, `Repo`, `Sysroot`, `SysrootUpgrader`, finder/sign/sepolicy types, boxed/shared structs, enums, flags, and constants. It keeps `functions` as `pub(crate)` and exposes extension traits under `pub(crate) mod traits`.

Control flow and state: There is no runtime control flow. Compile-time feature gates determine which modules and symbols are included, such as `CollectionRef`, `CommitSizesEntry`, `Remote`, `RepoFinderResult`, `ChecksumFlags`, `RepoCommitState`, and `RepoVerifyFlags`.

Dependencies and integration points: This file is the central integration point between generated files and the rest of the crate. Manual modules import from these re-exports, and public crate users see this curated surface.

Risks: Export drift here can make generated APIs inaccessible or expose APIs under the wrong feature. Because `functions` is crate-private, manual wrapper code must intentionally re-export any free functions meant for public use. Regeneration can reorder or alter exports broadly.

Test signals: `cargo doc` and compile tests across features should verify exports. Public API diff tooling is useful when regenerating bindings.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/mutable_tree.rs -->
# sources/cloud-native/ostree/rust-bindings/src/auto/mutable_tree.rs

Purpose: Generated wrapper for `OstreeMutableTree`, a mutable in-memory representation of OSTree directory tree content.

Important APIs: `new`, feature-gated constructors `from_checksum` and `from_commit`, `check_error`, `ensure_dir`, `ensure_parent_dirs`, `fill_empty_from_dirtree`, checksum getters/setters, `lookup`, `remove`, `replace_file`, and `walk`. Hash-table accessors for files/subdirs are unimplemented.

Control flow and state: Methods mutate or inspect the underlying tree object. Directory creation and file replacement update in-memory tree state; loading from checksums/commits ties the tree to repository objects. Persistence requires later repo commit/write APIs outside this file.

Dependencies and integration points: Depends on `Repo` under relevant feature gates, GLib error handling, and checksum strings. It is used by commit construction and tree editing workflows.

Risks: Unimplemented files/subdirs accessors limit direct enumeration. Callers must validate checksum strings and understand that setters can create invalid state until `check_error` or downstream commit APIs reject it. Feature-gated repo constructors require matching libostree support.

Test signals: Tree edit tests should cover ensure/walk/lookup/replace/remove, invalid checksum handling, loading from commits, and committing the resulting tree through repo APIs.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/mutable_tree.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/remote.rs -->
# sources/cloud-native/ostree/rust-bindings/src/auto/remote.rs

Purpose: Generated shared wrapper for `OstreeRemote`, representing a configured remote repository.

Important APIs: `name()` returns the remote name, `url()` returns an optional URL, and `Display` prints the name. Ownership uses `ostree_remote_ref`/`ostree_remote_unref`.

Control flow and state: The wrapper is read-only in this file. Remote configuration is persisted elsewhere in repository config or remotes.d files; this type provides a referenced view of that configuration.

Dependencies and integration points: Feature-gated by `v2018_6`. Integrates with repo remote listing/configuration APIs and the repo-config manpage concepts for remote URL/content URL and verification settings.

Risks: `url()` can return `None`, so callers must handle remotes without a direct URL or with custom backends. Displaying only the name is convenient but can hide URL/config distinctions in logs.

Test signals: Remote listing tests should verify name/display behavior, URL presence/absence, and reference ownership across cloned/shared handles.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/rust-bindings/src/auto/remote.rs -->
