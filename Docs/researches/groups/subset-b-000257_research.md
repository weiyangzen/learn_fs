# subset-b-000257 Research

Grouped research for OSTree test infrastructure and installed/kola integration tests. Each source section is source-tree aligned and wrapped for reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/basic-test.sh -->
## sources/cloud-native/ostree/tests/basic-test.sh

Purpose: sourced TAP-style integration body for the core `ostree` CLI, covering checkout, commit, pull-local, fsck, metadata, refs, remotes, cache behavior, whiteouts, and repository modes. It expects `libtest.sh` to have created `repo`, `test_tmpdir`, assertion helpers, `OSTREE`, `CMD_PREFIX`, and feature-skip helpers.

Important APIs/functions: local `validate_checkout_basic()` and `assert_trees_identical()` wrap repeated expectations; the script heavily exercises `ostree checkout`, `commit`, `diff`, `pull-local`, `prune`, `cat`, `ls`, `show`, `log`, `reset`, `remote`, and `fsck`. It branches on `is_bare_user_only_repo`, repo config mode, xattr support, SELinux relabel support, whiteout device support, and strace fault injection.

Control flow/state: the script mutates a single test repository through many refs (`test2`, `test3-*`, `branch-with-commitmsg`, etc.), repeatedly checking out trees, committing changes, resetting refs, pruning unreferenced content, and constructing auxiliary repos. Persistent state is local to the test tempdir except exported feature variables and temporary `repo/tmp/staging-*` assertions.

Dependencies/integration: requires a functioning uninstalled or installed `ostree`, GNU shell tools, `stat`, `sha256sum`, xattr tools, optional `strace`, optional SELinux, and helpers from `libtest.sh`. It is a broad regression net for repository object layout, metadata byte order via `get-byte-order`, and boot/cache semantics.

Risks/test signals: high brittleness around filesystem features, root/user mode, and exact English error strings. Strong test signals are TAP `ok` lines, explicit negative-command assertions, hardlink checks, object checksum validation, and fsck after risky operations.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/basic-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/bootc-integration/Cargo.toml -->
## sources/cloud-native/ostree/tests/bootc-integration/Cargo.toml

Purpose: defines a standalone Rust workspace/package for bootc OSTree integration tests built inside a container or VM, with one binary named `ostree-bootc-integration-tests`.

Important APIs/types/functions: declares `src/main.rs` as the binary and uses `anyhow`, `libtest-mimic`, `linkme`, `paste`, `quick-junit`, `tempfile`, and `xshell`. `linkme` and `paste` support distributed test registration; `quick-junit` supports optional XML output.

Control flow/state: no runtime logic, but the manifest intentionally separates this test workspace from the repository root workspace. It disables publishing and pins edition 2021.

Dependencies/integration: integrates Rust test harness logic with VM/container execution driven externally by bootc/tmt tooling. Dependencies imply a custom test runner instead of Rust's built-in `#[test]` harness.

Risks/test signals: dependency version drift can affect test registration or JUnit serialization. A successful build is a prerequisite signal before any privileged integration checks can run.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/bootc-integration/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/bootc-integration/src/lib.rs -->
## sources/cloud-native/ostree/tests/bootc-integration/src/lib.rs

Purpose: provides the registration infrastructure for bootc integration tests. Test functions return `anyhow::Result<()>` and are registered into a `linkme` distributed slice.

Important APIs/types/functions: `TestFn` aliases the fallible test function signature; `IntegrationTest` stores `name` and function pointer; `INTEGRATION_TESTS` is the distributed slice; `integration_test!` creates a static entry named from the function using `paste`.

Control flow/state: this file has no mutable runtime state. Registration happens at link time through `linkme`, and `main.rs` later enumerates the distributed slice.

Dependencies/integration: depends on `anyhow`, `linkme`, and `paste`, and exports the macro for submodules such as `tests/privileged.rs`. Unsafe code is allowed only because `linkme` requires it.

Risks/test signals: distributed-slice registration can silently miss tests if modules are not referenced by `main.rs`. The main signal is that registered tests appear in the custom harness listing.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/bootc-integration/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/bootc-integration/src/main.rs -->
## sources/cloud-native/ostree/tests/bootc-integration/src/main.rs

Purpose: implements the executable custom harness for bootc integration tests using `libtest_mimic`, with optional JUnit XML output.

Important APIs/types/functions: `TestOutcome` records name, duration, and stringified result. `main()` converts each `IntegrationTest` to a `Trial`, records outcomes in `Arc<Mutex<Vec<_>>>`, runs `libtest_mimic`, writes JUnit if `JUNIT_OUTPUT` is set, and exits 101 on failure. `write_junit()` builds a `quick_junit::Report`.

Control flow/state: outcomes are shared across trial closures and accumulated while tests run. JUnit output is post-run best-effort; failure to write XML only warns.

Dependencies/integration: integrates `INTEGRATION_TESTS` from the library, the `tests` module tree, CLI args accepted by `libtest_mimic`, and CI systems consuming JUnit.

Risks/test signals: mutex poisoning is unhandled via `unwrap()`. Parallel execution ordering can affect outcome order. Exit code and XML failures/successes are the main signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/bootc-integration/src/main.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/bootc-integration/src/tests/mod.rs -->
## sources/cloud-native/ostree/tests/bootc-integration/src/tests/mod.rs

Purpose: declares the test module namespace for bootc integration tests.

Important APIs/types/functions: exports `pub mod privileged;`, making privileged test registration statics reachable by the binary.

Control flow/state: no runtime control flow or persistence. Its only state effect is compile-time module inclusion.

Dependencies/integration: connects `main.rs`'s `mod tests;` with `tests/privileged.rs`.

Risks/test signals: if future test files are not added here, their distributed-slice statics will not be linked into the binary.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/bootc-integration/src/tests/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/bootc-integration/src/tests/privileged.rs -->
## sources/cloud-native/ostree/tests/bootc-integration/src/tests/privileged.rs

Purpose: defines root/booted-system integration checks for OSTree under bootc-style VM/container execution.

Important APIs/functions: `booted_test!` and `privileged_test!` create fallible functions and register them. Tests verify `/run/ostree-booted`, `/sysroot`, `/ostree/repo`, composefs overlay and `/run/ostree/.private`, `ostree --version`, `/sysroot` read-only options, `/run/ostree` permissions, immutable-bit behavior, `ostree admin os-init`, FIFO commit rejection, repo mtime updates, `repo/extensions`, and SELinux label of `/etc`.

Control flow/state: tests use `xshell` commands, temporary directories for repo-only tests, and direct host filesystem assertions for booted tests. Some checks are conditional, e.g. immutable-bit skipped on composefs and SELinux skipped if labels are absent.

Dependencies/integration: requires root, `ostree`, `systemd/findmnt/lsattr/ls -Z`, composefs when relevant, and booted OSTree layout. External VM deployment is assumed.

Risks/test signals: assertions depend on exact mount types and labels. Strong signals are `ensure!` failures with descriptive messages and command failures propagated through `anyhow`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/bootc-integration/src/tests/privileged.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/bootloader-entries-crosscheck.py -->
## sources/cloud-native/ostree/tests/bootloader-entries-crosscheck.py

Purpose: validates generated bootloader configuration against BootLoaderSpec loader entries, currently implementing SYSLINUX validation and explicitly skipping GRUB2 here.

Important APIs/functions: `main(argv)` dispatches by bootloader argument; `parse_loader_configs()` reads `/boot/loader/entries/*.conf`; `validate_syslinux()` parses `syslinux.cfg`; `get_ostree_option()` extracts the `ostree=` kernel option; `assert_key_same_file()` compares kernel/initrd stat results through `/boot` and root-relative paths.

Control flow/state: reads sysroot files only, builds sorted in-memory dictionaries by version, compares entry counts and per-entry linux/initrd/ostree options, and exits nonzero via `fatal()`.

Dependencies/integration: used by bootloader tests after `ostree admin` writes boot entries. Requires Python 3 and a synthetic or mounted sysroot with loader and syslinux config.

Risks/test signals: parser is simple and assumes single-space key/value records and integer `version`. Good signals are mismatch-specific fatal messages and success text `SYSLINUX configuration validated`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/bootloader-entries-crosscheck.py -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/coccinelle.sh -->
## sources/cloud-native/ostree/tests/coccinelle.sh

Purpose: runs semantic-patch blacklist tests over the OSTree source tree using Coccinelle `spatch`.

Important APIs/functions: sources `libtest.sh`, checks `spatch --version`, skips if `OSTREE_UNINSTALLED_SRCDIR` is unset, counts `tests/coccinelle/*.cocci`, and runs each with `spatch --very-quiet --dir`.

Control flow/state: emits a TAP plan based on the number of `.cocci` files, writes each semantic patch result to `cocci.out`, and fails if output is non-empty.

Dependencies/integration: requires uninstalled source checkout and Coccinelle. It integrates with Automake/TAP shell tests through `skip` and `fatal`.

Risks/test signals: shell word splitting over filenames is simple but acceptable for this tree. Main signal is empty `cocci.out` per semantic patch and TAP `ok` lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/coccinelle.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/corrupt-repo-ref.js -->
## sources/cloud-native/ostree/tests/corrupt-repo-ref.js

Purpose: GJS helper that corrupts random objects referenced by an OSTree ref to test fsck/pull corruption detection.

Important APIs/functions: uses GI `OSTree.Repo`, `Gio.File`, and `GLib`. `listObjectChecksumsRecurse()` resolves repo files recursively, recording dirtree, dirmeta, and filez objects. The main path reads a commit, chooses a random referenced object, opens the loose object read-write, changes 10 random bytes, and writes `corrupted-status.txt`.

Control flow/state: mutates repository object contents in place and persists a status log in the current directory. It randomly chooses both object and byte offsets.

Dependencies/integration: requires GJS with OSTree GI bindings and a loose-object repo. It is intended for tests that expect subsequent verification to fail.

Risks/test signals: randomness may hit small objects or offsets near bounds; `random_int_range(0, size)` must avoid invalid EOF reads. Signal is printed corruption detail plus downstream corruption errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/corrupt-repo-ref.js -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/get-byte-order.c -->
## sources/cloud-native/ostree/tests/get-byte-order.c

Purpose: tiny build helper used by shell tests to report host byte order for GLib variant metadata expectations.

Important APIs/functions: includes GLib or platform byte-order macros and prints the numeric byte-order value expected by tests.

Control flow/state: no state; single-process command returns one value to stdout.

Dependencies/integration: built under the test builddir and invoked by `basic-test.sh` when checking endian-sensitive `uint64` metadata display with and without byte-swapping.

Risks/test signals: must match the constants the shell test branches on (`4321` big-endian, `1234` little-endian). Failure makes metadata tests misdiagnose byte-order behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/get-byte-order.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/gpg-verify-data/gpg.conf -->
## sources/cloud-native/ostree/tests/gpg-verify-data/gpg.conf

Purpose: minimal GPG configuration fixture for signature verification tests.

Important APIs/functions: not executable; the file supplies GPG runtime settings used with a test homedir.

Control flow/state: no control flow. It influences `gpg` behavior when copied or referenced by shell tests.

Dependencies/integration: integrates with `libtest.sh` GPG fixture setup, exported test key IDs/fingerprints, and OSTree GPG verification tests.

Risks/test signals: small config changes can alter trust, keyring, or agent behavior. Test signal is successful deterministic signature verification in higher-level tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/gpg-verify-data/gpg.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/grub2-entries-crosscheck.py -->
## sources/cloud-native/ostree/tests/grub2-entries-crosscheck.py

Purpose: validates that generated GRUB2 menu entries match BootLoaderSpec loader entries for linux path, initrd path, and `ostree=` option.

Important APIs/functions: parses loader configs from `/boot/loader/entries` or argv paths, sorts by descending integer `version`, scans only the `15_ostree` block in `grub.cfg`, and compares with `assert_matches_key()`.

Control flow/state: read-only parser; constructs two entry lists and fails if counts or key values differ. Uses `get_ostree_option()` to compare only the OSTree deployment root option inside full kernel args.

Dependencies/integration: used after bootloader generation tests, including the shell `ostree-grub-generator`. Requires Python 3 and predictable GRUB2 stanza formatting.

Risks/test signals: parser assumes generated GRUB syntax starts `linux`/`initrd` at line start and ignores quoted menuentry details. Success text is `GRUB2 configuration validated`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/grub2-entries-crosscheck.py -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/inst/Cargo.toml -->
## sources/cloud-native/ostree/tests/inst/Cargo.toml

Purpose: defines the older installed-test Rust binary `ostree-test`, including non-destructive and destructive OSTree system tests.

Important APIs/types/functions: binary target is `src/insttestmain.rs`; dependencies cover CLI parsing (`structopt`, `clap`), test harness (`libtest-mimic`), OSTree/rpm-ostree bindings, async HTTP serving (`tokio`, `hyper`, `hyper-staticfile`), command shell helpers, random mutation, process/tempdir helpers, and serialization.

Control flow/state: manifest creates an isolated workspace and pulls some git dependencies (`rpmostree-client`, `with-procspawn-tempdir`), which means build reproducibility depends on pinned tags or repository availability.

Dependencies/integration: integrates with kola wrapper installation, destructive test listing, and installed VM tests.

Risks/test signals: old dependency versions may conflict with modern toolchains. Cargo build and `cargo run -- list-destructive` are primary signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/inst/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/inst/src/composefs.rs -->
## sources/cloud-native/ostree/tests/inst/src/composefs.rs

Purpose: destructive multi-boot test for composefs enablement, signed composefs verification, and composefs disablement through kernel args.

Important APIs/functions: `generate_raw_ed25519_keypair()` extracts raw public/private signing material via OpenSSL; `read_booted_metadata()` parses `/run/ostree-booted` as a GLib variant dict; `verify_composefs_sanity()`, `prepare_composefs_signed()`, `verify_composefs_signed()`, and `verify_disable_composefs()` implement the phases; `itest_composefs()` dispatches by reboot mark.

Control flow/state: on first boot, enables `ex-integrity.composefs`, stages a kargs change, and reboots. Later phases sign the pending commit, track config/key files through `rpm-ostree initramfs-etc`, verify journal messages, then append a disable karg and verify non-overlay root.

Dependencies/integration: requires root, rpm-ostree, OpenSSL, OSTree signing, composefs support, non-XFS root for fsverity, systemd journal, and autopkgtest reboot helpers.

Risks/test signals: destructive and stateful; failures can leave staged deployments or modified `/etc/ostree`. Signals include metadata keys, overlay mount type, private-dir mode, signature verification, and journal grep.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/inst/src/composefs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/inst/src/destructive.rs -->
## sources/cloud-native/ostree/tests/inst/src/destructive.rs

Purpose: destructive transactionality stress test that repeatedly interrupts rpm-ostree upgrades to verify staged deployment safety across kills, stops, clean reboots, and forced reboots.

Important APIs/types/functions: enums `PoliteInterruptStrategy`, `ForceInterruptStrategy`, `InterruptStrategy`, and `UpdateResult`; serialized `RebootMark`; `generate_srv_repo()`, `generate_update()`, `upgrade_and_finalize()`, `run_upgrade_or_timeout()`, `parse_and_validate_reboot_mark()`, `validate_live_interrupted_upgrade()`, `impl_transaction_test()`, `suppress_ostree_global_sync()`, and `itest_transactionality()`.

Control flow/state: stores server repo at `/var/tmp/ostree-test-srv` and cycle timing JSON at `/var/tmp/ostree-test-transaction-data.json`. Reboot state is serialized through `AUTOPKGTEST_REBOOT_MARK`. The main loop randomizes interrupt strategy, resets refs/cleanup before each attempt, validates the resulting commit state, and exits after `ITERATIONS` successful accounting cycles.

Dependencies/integration: requires booted OSTree, rpm-ostree, systemd units, `/sysroot`, local HTTP server from `test.rs`, tree mutation from `treegen.rs`, and autopkgtest reboot tools.

Risks/test signals: highly timing-dependent and destructive; random delays and VM load can skew interruption windows. Strong signals are commit-state classification, absence of global sync journal messages, final `ostree fsck`, and structured reboot mark counters.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/inst/src/destructive.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/inst/src/insttestmain.rs -->
## sources/cloud-native/ostree/tests/inst/src/insttestmain.rs

Purpose: entry point for `ostree-test`, dispatching non-destructive libtest-mimic tests and guarded destructive tests.

Important APIs/types/functions: `Opt` supports `list-destructive`, `run-destructive`, and `non-destructive`; `TESTS` lists sysroot and repo tests; `DESTRUCTIVE_TESTS` lists transactionality and composefs. `DESTRUCTIVE_TEST_STAMP` gates destructive execution.

Control flow/state: always switches to a tempdir under `/var/tmp`, initializes `procspawn`, parses CLI args, runs selected tests, and for destructive tests requires both `/etc/ostree-destructive-test-ok` and `/run/ostree-booted`.

Dependencies/integration: used by kola install wrappers and direct installed tests. Depends on modules `composefs`, `destructive`, `repobin`, `sysroot`, `test`, and `treegen`.

Risks/test signals: destructive-test matching is string-based from function paths. Missing stamp correctly fails closed. Signals are libtest-mimic output or `ok destructive test: <name>`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/inst/src/insttestmain.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/inst/src/repobin.rs -->
## sources/cloud-native/ostree/tests/inst/src/repobin.rs

Purpose: non-destructive repo/CLI tests using temporary repositories.

Important APIs/functions: `itest_basic()` checks `ostree --help`; `itest_nofifo()` verifies committing FIFOs fails; `itest_mtime()` verifies repo mtime changes after a second commit; `itest_extensions()` checks `repo/extensions`; `itest_pull_basicauth()` serves a repo over HTTP with Basic auth and validates unauth/badauth 403 versus good auth success.

Control flow/state: most tests run inside `with_procspawn_tempdir`; the auth test creates a server repo, client repo, remotes with credential variants, and uses `treegen::mkroot()` for content.

Dependencies/integration: relies on `sh_inline`, `with_procspawn_tempdir`, helper assertions from `test.rs`, local HTTP server, and OSTree CLI.

Risks/test signals: exact stderr strings and HTTP 403 are asserted. Auth URI embedding tests client credential handling and may expose URL parsing regressions.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/inst/src/repobin.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/inst/src/sysroot.rs -->
## sources/cloud-native/ostree/tests/inst/src/sysroot.rs

Purpose: non-destructive checks against the booted sysroot when running on an OSTree host.

Important APIs/functions: `skip_non_ostree_host()` gates tests; `itest_sysroot_ro()` loads the default `ostree::Sysroot`, verifies booted deployment, and reads its commit; `itest_immutable_bit()` checks `lsattr -d /` unless composefs overlay is active; `itest_tmpfiles()` checks `/run/ostree` mode; `itest_osinit_unshare()` runs `ostree admin os-init` and rechecks permissions.

Control flow/state: read-only for most checks, except `os-init` creates a test stateroot. Non-OSTree hosts return success without assertions.

Dependencies/integration: uses `ostree-ext` bindings, `xshell`, system utilities, and helper output assertions.

Risks/test signals: skip-by-return can hide coverage on non-OSTree hosts. Signals are API load success, commit read success, permission values, and command output.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/inst/src/sysroot.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/inst/src/test.rs -->
## sources/cloud-native/ostree/tests/inst/src/test.rs

Purpose: shared Rust helper library for installed tests, including command assertions, temporary HTTP serving, environment parsing, and autopkgtest reboot integration.

Important APIs/functions: `cmd_fails_with()`, `cmd_has_output()`, `write_file()`, `TestHttpServerOpts`, `TEST_HTTP_BASIC_AUTH`, `validate_authz()`, `http_server()`, `with_webserver_in()`, `getenv_utf8()`, `get_reboot_mark()`, `reboot()`, and `prepare_reboot()`.

Control flow/state: HTTP server binds localhost port 0 and serves static files with optional Basic auth and random per-request delay. Reboot helpers exec or call `/tmp/autopkgtest-reboot*` with a mark.

Dependencies/integration: depends on Hyper/Tokio, `hyper-staticfile`, `base64`, `rand`, and test command wrappers. Used by `repobin.rs` and `destructive.rs`.

Risks/test signals: random delay uses blocking sleep inside request handling; reboot uses `exec()` and never returns on success. Unit tests cover command matching and Basic auth decoding.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/inst/src/test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/inst/src/treegen.rs -->
## sources/cloud-native/ostree/tests/inst/src/treegen.rs

Purpose: generates synthetic root trees and mutates executable content for update/transaction tests.

Important APIs/functions: `mkroot()` and `mkvroot()` create deterministic versioned trees; `is_elf()` checks the ELF magic; `mutate_one_executable_to()` atomically writes a modified copy preserving permissions; `mutate_executables_to()` samples executable ELF candidates; `update_os_tree()` commits changed root content to an OSTree ref.

Control flow/state: `mkroot()` persists a version counter in `etc/.mkrootversion`. `update_os_tree()` creates a tempdir under repo `tmp`, scans `/usr/bin`, `/usr/lib`, `/usr/lib64`, mutates at least one eligible ELF, and commits with ownership, SELinux-from-base, link speedup, no bindings, and no xattrs.

Dependencies/integration: uses `cap-std-ext`, `rand`, `xshell`, and shared `write_file()`. Called by auth and destructive transaction tests.

Risks/test signals: candidate filter appears to require setuid/setgid bits due to the mode condition, which may limit mutations unexpectedly. Main signal is `mutated > 0` and successful `ostree commit`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/inst/src/treegen.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/Makefile -->
## sources/cloud-native/ostree/tests/kolainst/Makefile

Purpose: installs kola external test assets and Rust installed-test binary into the coreos-assembler kola layout.

Important targets: `all` syntax-checks top-level shell scripts and generates `destructive-list.txt` by running `cargo run --release -- list-destructive`; `install` copies shell libraries/directories, installs `ostree-test`, installs destructive ignition stamp config, and calls `install-wrappers.sh`; `localinstall` installs into `../kola`.

Control flow/state: uses `find`, `ls`, `rsync`, and `install`. It writes generated wrapper tests into the target tree.

Dependencies/integration: depends on the Rust `inst` binary and coreos-assembler's `/usr/lib/coreos-assembler/tests/kola/ostree/` layout.

Risks/test signals: `LIBSCRIPTS := $(shell ls *.sh)` is simple and shell-sensitive. Successful install should produce nondestructive-rs data and per-destructive wrapper scripts.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/data-shared/libinsttest.sh -->
## sources/cloud-native/ostree/tests/kolainst/data-shared/libinsttest.sh

Purpose: common installed-test shell harness for privileged kola tests.

Important APIs/functions: sources `${KOLA_EXT_DATA}/libtest-core.sh`; defines `_tmpdir_cleanup()`, `prepare_tmpdir()`, `run_tmp_webserver()`, `require_writable_sysroot()`, `nth_boot()`, `rpmostree_query_json()`, `assert_jq()`, and `assert_status_jq()`. It computes `host_commit` and `host_osname` from `rpm-ostree status --json`.

Control flow/state: validates `rpm-ostree` exists and the test is root; creates tempdirs under `/var/tmp` by default; can start a podman-backed Python HTTP server as a systemd unit; may remount `/sysroot` read-write.

Dependencies/integration: requires kola `KOLA_EXT_DATA`, rpm-ostree, jq, systemd, podman for webserver tests, and libtest-core assertions.

Risks/test signals: root and host mutation are assumed. The webserver uses a fixed container name and port 8000, so cleanup/collision failures are possible.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/data-shared/libinsttest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/data-shared/libtest-core.sh -->
## sources/cloud-native/ostree/tests/kolainst/data-shared/libtest-core.sh

Purpose: shared assertion and TAP helper library copied into installed/kola tests.

Important APIs/functions: `fatal`, `assert_not_reached`, `tap_ok`, `tap_end`, `assert_streq`, `assert_str_match`, file/dir presence assertions, content assertions, mode and whiteout assertions, `assert_files_equal`, `skip`, and `report_err` trap.

Control flow/state: sets UTF-8 locale, unsets `LANGUAGE`, exports `G_DEBUG=fatal-warnings`, and traps ERR to report the failed command.

Dependencies/integration: used by `libinsttest.sh` and nondestructive copy. Depends on POSIX/GNU tools such as `grep`, `stat`, `cmp`, and `sed`.

Risks/test signals: content checks depend on exact messages and regex dialect. Signals are immediate fatal exits with diagnostic file dumps and TAP counters where used.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/data-shared/libtest-core.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/auto-prune.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/auto-prune.sh

Purpose: destructive boot filesystem ENOSPC regression test for OSTree early bootcsum auto-pruning.

Important APIs/functions: local helpers track steps, journal cursors, journal grep/non-grep, bootcsum directory counts, and bootfs space consumption/restoration. It creates modified kernel commits `modkernel1/2/3`.

Control flow/state: may replace `/boot` with a loopback ext4 image large enough for the scenario, fills `/boot` with a big file, stages/rebases deployments, runs `ostree admin finalize-staged` with and without `OSTREE_SYSROOT_OPTS=no-early-prune`, and validates bootloader hash changes. Later phases test ext4 reserved space estimation and many-small-DTB block accounting.

Dependencies/integration: requires root, writable sysroot/repo, rpm-ostree, ext4 semantics, journalctl, loop mounts, and host kernel/initramfs paths.

Risks/test signals: highly destructive to `/boot` and assumes FCOS ext4. Strong signals are ENOSPC failures without auto-prune, journal messages about two-step bootloader updates, and expected bootcsum directory counts.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/auto-prune.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/basic-misc.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/basic-misc.sh

Purpose: small destructive installed test for OSTree CLI extension discovery.

Important APIs/functions: creates `/usr/libexec/libostree/ext/ostree-env` as a symlink to `/usr/bin/env`, invokes `ostree env`, and checks environment propagation.

Control flow/state: mutates `/usr/libexec/libostree/ext/`, writes `out.txt`, removes the extension symlink, and emits one TAP test.

Dependencies/integration: requires root, writable `/usr`, `ostree`, and `libinsttest.sh`.

Risks/test signals: the script contains an apparent typo checking `out.text` while writing `out.txt`, making the test likely fail unless a stale file exists. Intended signal is `TESTENV=foo` in extension output.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/basic-misc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/boot-automount.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/boot-automount.sh

Purpose: verifies staged deployment finalization keeps `/boot` mounted when `/boot` is managed by a short-idle systemd automount.

Important APIs/functions: uses `AUTOPKGTEST_REBOOT_MARK` phases, `systemctl`, `ostree admin deploy --stage`, `rpmostree_query_json`, and journal monotonic timestamps.

Control flow/state: phase 1 installs/enables `boot.automount`, unmounts `/boot`, starts the automount, stages a deployment with a dummy karg, checks finalize and hold services are active and `/boot` remains mounted after timeout, then reboots. Phase 2 verifies staged deployment finalized, karg is on `/proc/cmdline`, services succeeded, and hold service stopped before boot unmounting.

Dependencies/integration: requires root, systemd automounts, rpm-ostree/OSTree, journalctl, jq, and autopkgtest reboot.

Risks/test signals: timing-sensitive around automount idle timeout and journal ordering. Signals are service states, absence of staged marker, cmdline karg, and ordered timestamps.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/boot-automount.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/deployment-lint -->
## sources/cloud-native/ostree/tests/kolainst/destructive/deployment-lint

Purpose: validates deployment linting around commits containing `/var` content.

Important APIs/functions: uses `ostree commit --selinux-policy-from-base --tree=ref --tree=dir`, `ostree admin deploy`, `ostree admin stateroot-init`, and assertion helpers.

Control flow/state: creates a commit `testlint` adding `rootfs/var/testcontent`, deploys it into the current stateroot and verifies `/var/testcontent` is not materialized there, then initializes `newstatedir` and verifies the same content exists under the new stateroot deployment var.

Dependencies/integration: requires writable sysroot, host commit info, and installed OSTree.

Risks/test signals: expected warning text is asserted absent, so behavior changes in lint reporting may matter. Signals are filesystem existence checks in current `/var` versus new stateroot var.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/deployment-lint -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/finalization.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/finalization.sh

Purpose: tests staged deployment finalization locking, unlocking, and boot-time finalization behavior.

Important APIs/functions: uses `ostree admin deploy --lock-finalization`, `ostree admin lock-finalization --unlock`, `ostree admin status`, journal checks, and `rpm-ostree status --json`.

Control flow/state: first boot disables GPG verification and zincati, creates `staged-deploy`, deploys with finalization locked, and reboots. Second boot verifies it did not boot the new commit and logs say `Not finalizing`, then redeploys locked, unlocks, and reboots. Third boot verifies the new commit booted and previous finalize logs include `Bootloader updated`.

Dependencies/integration: requires writable sysroot, systemd, rpm-ostree, journalctl, jq, and autopkgtest reboot.

Risks/test signals: destructive staged state can persist on failure. Strong signals are finalization locked status text, booted checksum comparisons, and finalize journal messages.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/finalization.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/itest-bare-root.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/itest-bare-root.sh

Purpose: raw OSTree root test for committing and checking out security xattrs from the host repo.

Important APIs/functions: uses `ostree checkout -H`, `setfattr`, `ostree commit --link-checkout-speedup`, `ostree fsck`, `ostree ls -X`, and `getfattr`.

Control flow/state: in `/ostree/repo/tmp`, checks out the host commit, replaces a symlink copy to avoid corruption, adds custom `security.*` xattrs to a symlink and directory, commits to `testref`, verifies xattrs are present only in the new ref, then checks out and verifies materialized xattrs.

Dependencies/integration: requires root, writable sysroot, xattr support, and a likely `/usr/bin/gtar` symlink.

Risks/test signals: host content assumption for `/usr/bin/gtar` may fail on some images. Signals are `ostree ls -X`, `getfattr`, and `ostree fsck`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/itest-bare-root.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/itest-deploy-selinux.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/itest-deploy-selinux.sh

Purpose: verifies `/etc` merge and boot artifact labeling during deployments on SELinux systems.

Important APIs/functions: deploys host commit with current kargs, compares `ls -Z` labels for selected `/etc` files/directories, creates a `test-label` commit with modified initramfs and `--selinux-policy`, deploys it, and validates `/boot/ostree` kernel/initramfs labels.

Control flow/state: creates and undeploys temporary deployments, uses `/ostree/repo/tmp` checkout, deletes/replaces boot assets, and removes `test-label` ref at the end.

Dependencies/integration: requires SELinux labels, writable sysroot, `ls -Z`, rpm-ostree/ostree, and boot layout.

Risks/test signals: skipped files are tolerated, but exact context expectations (`boot_t`) are Fedora/SELinux-policy dependent. Signals are matching labels and successful undeploy cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/itest-deploy-selinux.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/itest-label-selinux.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/itest-label-selinux.sh

Purpose: broad SELinux labeling test for commit and checkout paths.

Important APIs/functions: exercises `ostree commit --selinux-policy`, `--selinux-labeling-epoch`, checkout `--selinux-policy`, `--subpath`, `--selinux-prefix`, `--skip-list`, `--selinux-policy-from-base`, and `--tree=tar`.

Control flow/state: checks out host commit, creates test binaries with altered labels and reflink behavior, commits and inspects `ostree ls -X`, verifies checkout relabeling for root and subpath layouts, tests prefix correction for nested trees, and verifies labels from base policy for new `/usr/bin`, `/usr/lib`, `/usr/etc` files.

Dependencies/integration: requires SELinux, xattrs, `chcon`, `filefrag`, tar, writable sysroot, and host policy.

Risks/test signals: strongly coupled to SELinux policy names (`bin_t`, `lib_t`, `etc_t`, `system_conf_t`) and reflink support. Signals are label comparisons and expected failure for `-H` with policy checkout.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/itest-label-selinux.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/kargs-edit-in-place.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/kargs-edit-in-place.sh

Purpose: verifies `ostree admin kargs edit-in-place --append-if-missing` changes bootloader entries and survives reboot.

Important APIs/functions: uses `rpm-ostree kargs --append`, `ostree admin kargs edit-in-place`, loader entry content assertions, and autopkgtest reboot.

Control flow/state: first phase stages/appends a dummy karg through rpm-ostree, edits the loader entry in place with `testarg`, asserts the loader entry contains it, and reboots. Second phase checks both kargs in `/proc/cmdline`.

Dependencies/integration: requires sudo/root, bootloader entries under `/boot/loader/entries`, rpm-ostree, and reboot harness.

Risks/test signals: destructive to kernel args and boot entries. Signals are loader-entry text before reboot and `/proc/cmdline` after reboot.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/kargs-edit-in-place.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/mount-propagation.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/mount-propagation.sh

Purpose: verifies mounts under `/var` and `/sysroot` propagate correctly into separate mount namespaces and do not leak into deployment var paths.

Important APIs/functions: `get_mount()` uses `nsenter` and `findmnt --json`; `assert_has_mount()`, `assert_not_has_mount()`, and `test_mounts()` inspect root and child namespaces. The script creates tmpfs mounts manually and via `/etc/fstab`.

Control flow/state: first phase creates `/var/foo` and `/sysroot/bar`, starts an `unshare -m` process, mounts tmpfs, tests propagation, writes fstab entries and a `test-mounts.service` ordered after `ostree-remount`, then reboots. Second phase verifies service timing from journal and repeats mount assertions in its namespace.

Dependencies/integration: requires root, mount namespaces, systemd ordering, jq, findmnt, journalctl, and writable sysroot.

Risks/test signals: timing and namespace-sensitive. Strong signals are namespace inequality, mount presence/absence, and monotonic journal ordering around remount and mount units.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/mount-propagation.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/overlay-initrds.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/overlay-initrds.sh

Purpose: multi-boot test for `ostree admin deploy --overlay-initrd`, including staging, cleanup, comparison, and multiple overlay initrds.

Important APIs/functions: `create_initrd_with_dracut_karg()` builds reproducible cpio initrds containing `/etc/cmdline.d`; `check_for_dracut_karg()` greps `dracut-cmdline` journal output; deploy phases use `--overlay-initrd` and `--stage`.

Control flow/state: phase 1 deploys overlay initrd `ostree.test1`; phase 2 verifies it and stages `ostree.test2`; phase 3 verifies replacement, checks overlay files by sha256 under `/boot/ostree/initramfs-overlays`, tests GC of old overlays and no bootconfig swap for identical overlay, then stages two overlays; phase 4 verifies both kargs and files.

Dependencies/integration: requires dracut journal behavior, cpio, sha256sum, OSTree boot overlays, writable boot, and reboot harness.

Risks/test signals: journal grep is dracut-specific; boot overlay GC depends on BLS references. Signals are kargs in boot journal, overlay image existence, and `bootconfig swap: no`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/overlay-initrds.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/root-transient-ro.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/root-transient-ro.sh

Purpose: verifies `prepare-root.conf` `[root] transient-ro = true` keeps `/` read-only while allowing writable remounts only in isolated namespaces.

Important APIs/functions: modifies `/etc/ostree/prepare-root.conf`, runs `rpm-ostree initramfs-etc --track`, checks `test -w /`, uses `unshare -m` remount with `LIBMOUNT_FORCE_MOUNT2=always`, and reboots.

Control flow/state: first phase masks zincati, copies and edits prepare-root config, tracks it into initramfs, and reboots. Second phase checks `/` is not writable in the main namespace, creates `/new-dir-in-root` through a mount namespace remount, and verifies main namespace remains read-only.

Dependencies/integration: requires rpm-ostree initramfs-etc, OSTree prepare-root, mount namespaces, and autopkgtest reboot.

Risks/test signals: modifies root/initramfs configuration and may affect later boots. Signals are write tests before/after isolated remount and presence of the new directory.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/root-transient-ro.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/soft-reboot.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/soft-reboot.sh

Purpose: destructive multi-phase test for systemd soft reboot behavior with and without OSTree `prepare-soft-reboot`.

Important APIs/functions: `assert_soft_reboot_count()`, `assert_status_jq()`, `ostree admin prepare-soft-reboot`, `--reset`, `--reboot`, `systemctl soft-reboot`, `systemctl reboot`, staged deploys, and rpm-ostree kernel-state changes.

Control flow/state: verifies `/sysroot` read-only on each boot, remounts writable for test commits, first tests bare `systemctl soft-reboot` without `/run/nextroot`, then stages `soft-reboot-test`, prepares soft reboot and checks status text/JSON plus `/run/nextroot`. Later phases verify booted commit/content, soft reboot into rollback, reset idempotence, staged-versus-soft-reboot interactions, default soft reboot via mounted nextroot, and rejection when initramfs or kargs change kernel state.

Dependencies/integration: requires systemd soft reboot support, autopkgtest soft-reboot helpers, rpm-ostree, jq, writable sysroot, and booted OSTree host.

Risks/test signals: very stateful and sensitive to host systemd behavior. Signals include `SoftRebootsCount`, mountpoints `/var` and `/boot`, deployment JSON flags, content files, `/run/ostree/nextroot-booted`, and expected `different kernel state` errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/soft-reboot.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/staged-delay.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/staged-delay.sh

Purpose: verifies delayed `ostree-finalize-staged.service` shutdown still sees `/boot/loader/entries`.

Important APIs/functions: writes a systemd drop-in adding an `ExecStop` shell command, runs `rpm-ostree kargs`, and checks previous boot logs.

Control flow/state: first phase creates `/etc/systemd/system/ostree-finalize-staged.service.d/delay.conf`, reloads systemd, stages a karg change, and reboots. Second phase reads previous boot journal for the success message and service success/deactivation, then checks the karg in `/proc/cmdline`.

Dependencies/integration: requires systemd, rpm-ostree, journalctl, jq, and reboot harness.

Risks/test signals: depends on systemd version-specific success wording. Signals are custom log line, service success pattern, and cmdline karg.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/staged-delay.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/staged-deploy.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/staged-deploy.sh

Purpose: comprehensive staged deployment behavior test, including finalization, cleanup, locking, upgrade staging, staged/non-staged interactions, ignored `/etc` special files, and boot-complete failure reporting.

Important APIs/functions: uses `ostree admin deploy --stage`, `--lock-finalization`, `lock-finalization`, `undeploy`, `upgrade --stage`, `pin`, `rpm-ostree cleanup`, journal grep/counts, and JSON status checks.

Control flow/state: first phase disables GPG verification, creates socket/FIFO to ignore during `/etc` merge, creates a synthetic commit, stages it, verifies service/ref/state, rejects pinning, and reboots. Second phase verifies finalization logs and syncfs counts, tests cleanup/restaging/locking/upgrade/unstage/overwriting/retaining behavior, then intentionally makes `/boot` immutable and stages kargs to force previous-boot finalization failure. Third phase verifies `ostree-boot-complete` captured that failure.

Dependencies/integration: requires writable sysroot, systemd, SELinux toggle, rpm-ostree, jq, journalctl, chattr, and reboot harness.

Risks/test signals: large destructive surface; can leave immutable `/boot` or staged deployments on interruption. Signals are status text/JSON, `/run/ostree/staged-deployment*`, journal messages, syncfs counts, and captured boot-complete status.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/staged-deploy.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/state-overlay.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/state-overlay.sh

Purpose: tests `ostree-state-overlay@.service` persistence and shadowing behavior for top-level mutable state overlays.

Important APIs/functions: creates a `foobar` commit with top-level content, enables `ostree-state-overlay@foobar.service`, uses reboot phases to mutate overlay contents, and upgrades back to a base commit.

Control flow/state: phase 1 commits `/foobar` content and rebases. Phase 2 verifies `/foobar` is overlay, creates persistent state files, shadows base files with changed types/symlinks/deletions/opaque dirs, and reboots. Phase 3 verifies state and shadowing persisted across reboot, commits an upgrade removing the top-level content, upgrades and reboots. Phase 4 verifies state files persist while base shadowings are gone/restored.

Dependencies/integration: requires rpm-ostree, systemd template service, overlayfs, reboot harness, and host commit.

Risks/test signals: manipulates root-level paths and overlay state. Signals are mount source `overlay`, file contents/types, deleted/restored base paths, symlink targets, and opaque dir behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/state-overlay.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/unlock-transient.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/unlock-transient.sh

Purpose: verifies `ostree admin unlock --transient` creates transient writable `/usr` overlay state that does not persist across reboot.

Important APIs/functions: computes deployment backing dir from rpm-ostree JSON, runs `ostree admin unlock --transient`, uses `unshare -m` to remount `/usr` writable, and checks backing upperdir.

Control flow/state: first phase confirms `/usr/share/writable-usr-test` absent, unlocks transiently, verifies outer namespace still cannot write, writes through an isolated namespace, verifies file exists via overlay and in the backing `usr-transient/upper`, then reboots. Second phase verifies the file did not persist, unlocks again, and rechecks absence.

Dependencies/integration: requires root, mount namespaces, rpm-ostree JSON, writable sysroot, and reboot harness.

Risks/test signals: path construction depends on deployment serial/checksum layout. Signals are write failures in outer namespace, file existence in backing upperdir, and absence after reboot.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/unlock-transient.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/var-mount.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/var-mount.sh

Purpose: regression test for explicit `/var` bind mount from deployment var path through `/etc/fstab`.

Important APIs/functions: uses `ostree admin status` to infer stateroot, appends an fstab bind mount, and verifies `var.mount`.

Control flow/state: first phase writes `/var/somenewfile`, appends `/sysroot/ostree/deploy/<stateroot>/var /var none bind 0 0` to `/etc/fstab`, and reboots. Second phase checks `systemctl status var.mount` and that the file remains in `/var`.

Dependencies/integration: requires reboot harness, systemd fstab generator, and OSTree deployment layout.

Risks/test signals: mutates `/etc/fstab` and assumes status parsing of the booted line. Signals are active `var.mount` and preserved file.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/var-mount.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/install-wrappers.sh -->
## sources/cloud-native/ostree/tests/kolainst/install-wrappers.sh

Purpose: generates one kola wrapper script per Rust destructive test listed by `ostree-test list-destructive`.

Important APIs/functions: reads a list file, symlinks `../nondestructive-rs` as `${testdir}/data`, and writes executable shell wrappers that exec `${KOLA_EXT_DATA}/ostree-test run-destructive <name>`.

Control flow/state: modifies the target install tree by creating a symlink and wrapper files. Uses `set -xeuo pipefail` for fail-fast install behavior.

Dependencies/integration: called by the kola `Makefile` during install. Depends on `KOLA_EXT_DATA` being set at runtime by kola and on destructive-list contents matching Rust test names.

Risks/test signals: unquoted wrapper names from list input can be problematic if names contain spaces, though current function paths do not. Signal is generated executable wrappers per listed test.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/install-wrappers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-alt-sysroot.sh -->
## sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-alt-sysroot.sh

Purpose: verifies `ostree admin status --sysroot` rejects a sysroot whose `/boot` is vfat.

Important APIs/functions: re-execs itself in a private mount namespace if needed, creates a 512M vfat loop image, runs `ostree admin init-fs -E 1 sysroot`, mounts image at `sysroot/boot`, and expects status failure.

Control flow/state: all state is in a tempdir under `/var/tmp`; cleanup trap removes tempdir, and the script manually unmounts `sysroot/boot` before fatal paths.

Dependencies/integration: requires root, loop mounting, `mkfs.vfat`, OSTree admin commands, and `libinsttest.sh`.

Risks/test signals: missing vfat tooling or loop capability will fail setup. Main signal is error text `/boot cannot currently be a vfat filesystem`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-alt-sysroot.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-bare-unit.sh -->
## sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-bare-unit.sh

Purpose: intended to run installed basic unit tests and verify permission-denied object reads, but currently aborts immediately with `fatal "FIXME - need to also sync over the installed tests"`.

Important APIs/functions: unreachable code would set `G_TEST_SRCDIR`, prepare `/var/tmp`, run installed `test-basic.sh` and `test-basic-c`, create a bare repo with unreadable content, verify root can read it, and verify `setpriv` non-root cannot.

Control flow/state: because `fatal` is before all substantive work, the active behavior is immediate failure. The rest is a planned/non-live test body.

Dependencies/integration: would require installed tests, `setpriv`, bare repo support, and libinsttest assertions.

Risks/test signals: as written this is a deliberate failing placeholder unless excluded by the kola harness. If enabled, signal is the FIXME fatal rather than the intended permission test.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-bare-unit.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-bare-user-root.sh -->
## sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-bare-user-root.sh

Purpose: tests bare-user repository composition with link-checkout-speedup, ownership preservation, and SELinux relabeling.

Important APIs/functions: initializes a bare-user repo, commits component trees with different owner gid values and no xattrs, union-checkouts components with `-U -H`, commits the combined rootfs with `--selinux-policy / --link-checkout-speedup`, and inspects `ostree ls`/`ls -X`.

Control flow/state: all content is synthetic in a tempdir. It creates dbus/systemd component trees, combines them into `rootfs`, and validates output metadata.

Dependencies/integration: requires host SELinux policy, root, bare-user mode, and assertion helpers.

Risks/test signals: expected gid `81` is Fedora/dbus-specific. Signals are uid/gid/mode in `ostree ls`, SELinux xattr presence, and absence of `user.ostreemeta`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-bare-user-root.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-payload-link.sh -->
## sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-payload-link.sh

Purpose: tests payload-link/reflink behavior for duplicate large objects, unprivileged child repos, and cross-device parent repos.

Important APIs/functions: creates an archive repo with duplicate random objects, serves it with `run_tmp_webserver`, creates XFS reflink loopback filesystems, sets `core.payload-link-threshold 0`, pulls with static deltas disabled, inspects `*.payload-link`, and validates payload checksum targets.

Control flow/state: sets ACLs for user `bin`, mounts two loop devices, performs a pull on the first reflink filesystem, commits from an unprivileged bare-user child repo with parent configured, then repeats across a second filesystem to ensure payload links are not created across devices.

Dependencies/integration: requires podman HTTP helper, loop devices, XFS reflink support, ACL tools, `runuser`, and root.

Risks/test signals: resource-heavy and tagged needs-internet because of webserver image. Signals are payload-link count 1 on same device, count 0 in unprivileged/parent and cross-device cases, and checksum equality.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-payload-link.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-pull-space.sh -->
## sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-pull-space.sh

Purpose: tests `min-free-space-percent` and `min-free-space-size` enforcement for object pulls and static-delta application.

Important APIs/functions: creates a 20MiB ext4 loopback filesystem, initializes bare-user repos with `fsync=false`, sets repo config free-space thresholds, runs `pull-local`, `pull-local --commit-metadata-only`, `static-delta generate --empty`, and `static-delta apply-offline`.

Control flow/state: first expects pull failure from default percent threshold, then size threshold failure and success, then verifies metadata-only writes can bypass low content free-space. It creates two repos and a 2MB file delta, fails applying with 14MB minimum, then lowers to 1MB and succeeds.

Dependencies/integration: requires loop devices, ext4 mkfs, host `/ostree/repo`, and static-delta support.

Risks/test signals: exact free-space values are tied to filesystem overhead. Signals are expected error strings `min-free-space-percent`/`min-free-space-size` and success after threshold reduction.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-pull-space.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-pull.sh -->
## sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-pull.sh

Purpose: intended HTTP/direct pull regression test, but currently exits immediately with status 0 due to a FIXME.

Important APIs/functions: inactive body would archive the host repo, serve it over HTTP, pull into a bare-user repo, corrupt content to verify fsck marks commits partial, retry pull, test pull-local across a bind mount, and verify metadata xattrs are not copied.

Control flow/state: active control flow is only `exit 0`; no state is created. Inactive code would use tempdirs, webserver, bind mounts, and repo mutations.

Dependencies/integration: if re-enabled, requires webserver support, mount permissions, xattr tools, and host repo access.

Risks/test signals: currently provides no coverage by design. The test signal is skip-like success, so regressions in the inactive scenarios are not caught.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-pull.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-remotes.sh -->
## sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-remotes.sh

Purpose: verifies installed systems have at least one OSTree remote configured, guarding `/etc/ostree/remotes.d` handling.

Important APIs/functions: runs `ostree remote list > remotes.txt` and fails if the output is empty.

Control flow/state: creates a tempdir and cleanup trap; otherwise read-only against system remote configuration.

Dependencies/integration: requires `libinsttest.sh`, rpm-ostree-derived host context, and `ostree` CLI.

Risks/test signals: image variants without remotes will fail even if OSTree itself is functional. Signal is non-empty `remotes.txt`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-remotes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/nondestructive/libtest-core.sh -->
## sources/cloud-native/ostree/tests/kolainst/nondestructive/libtest-core.sh

Purpose: nondestructive copy of the shell assertion/TAP core library.

Important APIs/functions: same core helpers as `data-shared/libtest-core.sh`: `fatal`, `assert_*`, content/mode/whiteout checks, `skip`, TAP counters, and ERR reporting.

Control flow/state: sets UTF-8 locale and `G_DEBUG=fatal-warnings`, unsets `LANGUAGE`, and traps ERR for diagnostics.

Dependencies/integration: sourced by nondestructive kola shell tests. Depends on standard shell utilities.

Risks/test signals: duplicated library can drift from `data-shared/libtest-core.sh`; assertion behavior should remain consistent across destructive and nondestructive suites.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/nondestructive/libtest-core.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/libostreetest.c -->
## sources/cloud-native/ostree/tests/libostreetest.c

Purpose: C helper library that bridges GLib/GIO tests to the shell test harness and creates test repos/sysroots.

Important APIs/functions: `ot_test_tmpdir_template()`, `ot_test_run_libtest()`, `ot_test_setup_repo()`, `ot_check_relabeling()`, `ot_check_user_xattrs()`, and `ot_test_setup_sysroot()`. It uses GLib spawning, libglnx tmpfiles/xattrs, and OSTree repo/sysroot APIs.

Control flow/state: `ot_test_run_libtest()` spawns bash, sources `tests/libtest.sh`, and runs an arbitrary command. Repo/sysroot setup delegates to shell functions, then opens resulting `repo` or `sysroot`. Relabel/user-xattr checks create linkable tmpfiles and probe xattr get/set behavior. Sysroot setup sets `OSTREE_SYSROOT_DEBUG` to mutable deployments and maybe `no-xattrs`.

Dependencies/integration: used by C tests needing canonical shell fixtures. Depends on `G_TEST_SRCDIR`, GLib, libglnx, OSTree headers/libs, and shell tests.

Risks/test signals: shell command construction is string-based. Signals are GError propagation, opened `OstreeRepo`, xattr booleans, and sysroot object creation.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/libostreetest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/libostreetest.h -->
## sources/cloud-native/ostree/tests/libostreetest.h

Purpose: public C header for the libostreetest helper functions.

Important APIs/functions: declares shell bridge, tmpdir template, repo setup, relabel/xattr probes, and sysroot setup. Uses `G_BEGIN_DECLS/G_END_DECLS` for C++ compatibility and includes `gio/gio.h` plus `ostree.h`.

Control flow/state: no implementation or state; it defines the API contract consumed by C tests.

Dependencies/integration: must stay in sync with `libostreetest.c` and linked test binaries.

Risks/test signals: signature drift breaks compilation. The header exposes nullable/error-bearing GLib patterns via `GError **` and object return pointers.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/libostreetest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/libtest-core.sh -->
## sources/cloud-native/ostree/tests/libtest-core.sh

Purpose: canonical core shell assertion library for OSTree tests.

Important APIs/functions: provides `fatal`, TAP helpers, equality/regex assertions, file/dir/content/mode/whiteout/symlink assertions, `skip`, and an ERR trap that reports the failing command.

Control flow/state: normalizes locale to UTF-8, unsets `LANGUAGE`, exports `G_DEBUG=fatal-warnings`, and increments a TAP counter through `tap_ok()`.

Dependencies/integration: sourced by `libtest.sh` and related shell tests. Its diagnostics are intentionally file-content rich for CI logs.

Risks/test signals: assertion behavior is foundational; any change can affect many tests. Exact regex handling and command trap behavior are central test signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/libtest-core.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/libtest.sh -->
## sources/cloud-native/ostree/tests/libtest.sh

Purpose: main shell harness for OSTree source tests, extending `libtest-core.sh` with repo setup, feature detection, GPG fixtures, webserver setup, boot/sysroot fixtures, and object-path helpers.

Important APIs/functions: initializes `test_srcdir`, `top_builddir`, `test_builddir`, `test_tmpdir`, exit hooks, GPG homes, feature flags, and `OSTREE_SYSROOT_DEBUG`. Key functions include `have_selinux_relabel()`, `can_create_whiteout_devices()`, `setup_test_repository()`, `ostree_repo_init()`, `run_webserver()`, `setup_fake_remote_repo1/2()`, `setup_os_repository()`, `os_repository_new_commit()`, `have_user_xattrs()`, skip helpers, signing key generators, bare-user predicates, and object path/checksum helpers.

Control flow/state: when sourced, validates/marks the tempdir, copies `gpghome`, probes xattr/whiteout support, sets `OSTREE_SKIP_CACHE=1`, may set `OSTREE_NO_XATTRS`/`OSTREE_NO_WHITEOUTS`, and exports test key variables. Setup functions create repos, sysroots, fake remotes, HTTP dirs, bootloader stubs, and multiple commits.

Dependencies/integration: used by most shell tests, C helpers, JS helpers, and installed tests. Requires OSTree CLI, xattr tools, optional HTTP daemon, GPG/OpenSSL, system utilities, and generated test fixture archives.

Risks/test signals: broad global side effects; sourcing outside an empty tempdir intentionally fails. Strong signals include skip decisions, constructed refs/content, fsck, exported `OSTREE`, and object path helpers used by corruption/hardlink checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/libtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/makecheck.py -->
## sources/cloud-native/ostree/tests/makecheck.py

Purpose: convenience wrapper around `make check` that extracts failed test output from `test-suite.log`.

Important APIs/functions: `run_make_check()` runs `make check -j 6` plus CLI args; `is_header()` detects Automake section headers; `print_truncated()` prints first line and last 20 lines; `get_failed_test_output()` parses failure/error sections; `analyze` mode parses a supplied log.

Control flow/state: on normal run, exits 0 if make succeeds; on failure, parses `test-suite.log`, optionally moves it to `$ARTIFACTS/test-suite.log`, and exits 1.

Dependencies/integration: requires GNU make, Automake-style `test-suite.log`, Python 3, and optional artifacts directory.

Risks/test signals: parser assumes previous line before `========` is `KEY: value`; malformed logs can break splitting. Signal is concise failed test tail output in CI.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/makecheck.py -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/ostree-grub-generator -->
## sources/cloud-native/ostree/tests/ostree-grub-generator

Purpose: shell GRUB2 config generator used as OSTree's built-in/custom generator template for systems not using `grub2-mkconfig`.

Important APIs/functions: `read_config()` parses BootLoaderSpec fields into globals; `populate_menu()` determines `boot_prefix`, iterates loader entry `.conf` files in version-reverse order, and appends `menuentry`, `linux`, `initrd`, and optional `devicetree` lines; `populate_warning()`, `populate_header()`, and `generate_grub2_cfg()` write the final file.

Control flow/state: takes the target grub config path as argument 2, derives entries path beside it, and appends generated content. It relies on global shell variables for parsed fields and accumulated `menu`.

Dependencies/integration: called from `ostree-bootloader-grub2.c` or tests via `OSTREE_GRUB2_EXEC`. Uses portable `/bin/sh`, `basename`, `dirname`, `stat`, `ls -v -r`, `cut`, and `printf`.

Risks/test signals: unquoted expansions and `printf "$menu"` can mishandle special characters; missing `OSTREE_BOOT_PARTITION` with separate boot layouts is sensitive. Signals are cross-checker validation against loader entries.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/ostree-grub-generator -->
