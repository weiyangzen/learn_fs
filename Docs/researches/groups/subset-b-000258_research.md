# subset-b-000258 research

Grouped research for the OSTree test files assigned to `subset-b-000258`. Each section preserves the source path as its title and is delimited for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/pull-test.sh -->
# sources/cloud-native/ostree/tests/pull-test.sh

Purpose: sourced TAP integration suite for pull behavior across HTTP, file URLs, mirrors, static deltas, GPG, corruption, timestamp checks, custom remotes, and bad server responses. It assumes a prepared HTTP server and `repo_mode` from the caller.

Important APIs/functions: local `repo_init()` recreates `repo` and adds `origin`; `verify_initial_contents()` checks checkout content. It drives `ostree pull`, `pull-local`, `remote add/delete`, `summary -u`, `static-delta generate`, `fsck`, `checkout`, `show`, and `rev-parse`.

Control flow: initializes a repo, verifies ordinary and per-object-fsync pulls, mirrors subsets/all refs, rejects unsafe bare-user-only content, injects corrupted objects/path traversal, tests detached metadata and timestamp rollback prevention, then exercises static delta dry-run, required-delta success/failure, inline and byteswapped deltas, custom backend errors, 404s, GPG signatures, and invalid ref HTML.

State/persistence: mutates `repo`, `mirrorrepo`, `ostree-srv/gnomerepo`, summaries, deltas, refs, commitpartial markers, remote config, and checkout trees. Dependencies include `libtest.sh`, `ostree-trivial-httpd`, xattrs, optional gpgme, tar fixtures, and shell assertions.

Integration/risk/test signals: covers the main network pull path and many security-sensitive failure modes. Fragility comes from exact progress regexes, HTTP fixture layout, feature-dependent branches, and compression-size tolerances. TAP `ok` lines and `fsck` calls are the primary success signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/pull-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/pull-test2.sh -->
# sources/cloud-native/ostree/tests/pull-test2.sh

Purpose: small sourced continuation for pull checkout semantics, focused on the state produced by a remote pull into the selected repository mode.

Important APIs/functions: defines the same `repo_init()` pattern as `pull-test.sh`, computes `COMMIT_ARGS`, `CHECKOUT_U_ARG`, and `CHECKOUT_H_ARGS` based on bare, bare-user, or bare-user-only mode, then relies on caller-provided `$OSTREE`, `${CMD_PREFIX}`, `is_bare_user_only_repo`, and assertion helpers.

Control flow: creates a fresh repo, adds `origin` without signature verification, normalizes checkout/commit flags for the repo mode, and runs compact pull/checkout checks rather than the broad corruption and delta matrix in `pull-test.sh`.

State/persistence: recreates `${test_tmpdir}/repo` and writes remote configuration. It is intentionally sourced, so environment variables and shell options propagate into the caller.

Integration/risk/test signals: validates mode-sensitive checkout behavior through command success and assertions. The main risk is duplicated flag-selection logic drifting from `basic-test.sh` and `pull-test.sh`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/pull-test2.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/repo-finder-mount.c -->
# sources/cloud-native/ostree/tests/repo-finder-mount.c

Purpose: GLib unit/integration test for `OstreeRepoFinderMount`, validating asynchronous repository discovery against mocked GIO volume/mount data.

Important APIs/types/functions: uses `OstreeRepoFinderMount`, `OstreeRepoFinder`, `OstreeCollectionRef`, `OstreeRepoFinderResult`, `GAsyncResult`, and mock helpers from `test-mock-gio.h`. `result_cb()` captures async completion. `main()` configures locale, mock mounts, refs, and event-loop waiting.

Control flow: builds a mock mount environment, calls `ostree_repo_finder_resolve_async()`, spins the main context until completion, finishes the async operation, and asserts returned results match expected mounted repository metadata and priorities.

State/persistence: no persistent repo writes; state is in memory through GObject instances and mock GIO objects. Dependencies include GLib/GIO, libglnx, private OSTree repo-finder headers, and test mock infrastructure.

Integration/risk/test signals: checks the mount finder glue between platform mount discovery and OSTree collection-ref resolution. Risks include async lifetime bugs, mock divergence from real GIO behavior, and private API changes. `g_assert_no_error()` and GLib test exit status are the signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/repo-finder-mount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/run-installed -->
# sources/cloud-native/ostree/tests/run-installed

Purpose: convenience runner for tests that must execute against installed binaries after a development `make install`.

Important APIs/functions: plain Bash with `set -xeuo pipefail`; computes `dn=$(dirname $0)` and runs Cargo in `tests/inst` via `(cd ${dn}/../tests/inst && cargo run --release)`.

Control flow: no branching. It changes to the Rust installed-test directory relative to the script and delegates all test logic to Cargo.

State/persistence: writes only whatever Cargo build/test artifacts are produced under the Rust target tree. It depends on an installed OSTree environment, Rust/Cargo, and the `tests/inst` crate.

Integration/risk/test signals: integrates the shell test tree with Rust installed tests. Risks are path assumptions and accidental testing of build-tree binaries if the environment is not clean. Success is Cargo's release run exit status.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/run-installed -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/runkola -->
# sources/cloud-native/ostree/tests/runkola

Purpose: developer helper to build the project, create a QEMU image through CoreOS-style tooling, install kola tests, and run kola integration tests.

Important APIs/functions: uses `git rev-parse --show-toplevel`, `make`, `cosa build-fast`, `make -C tests/kolainst`, `sudo make -C tests/kolainst install`, and `kola run -p qemu --qemu-image`.

Control flow: moves to the repository root, builds, selects the first `fastbuild-*-qemu.qcow2`, defaults the test pattern to `ext.ostree.*` if no arguments are provided, installs test assets, and `exec`s kola.

State/persistence: creates build outputs, QEMU images, and installed kola tests. It depends on `cosa`, `kola`, sudo, and a QEMU-capable host.

Integration/risk/test signals: bridges local source builds to VM-level validation. Risks are destructive or expensive host-side build/install steps and ambiguous image selection. Success is kola's exit status after replacing the shell process.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/runkola -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-boot-counting-tries.sh -->
# sources/cloud-native/ostree/tests/test-admin-boot-counting-tries.sh

Purpose: verifies sysroot configuration `sysroot.boot-counting-tries` is honored in generated bootloader entry names.

Important APIs/functions: sources `libtest.sh`, calls `setup_os_repository "archive" "syslinux"`, uses `ostree config set/get`, `pull-local`, `rev-parse`, and `ostree admin deploy`.

Control flow: initializes a syslinux sysroot, sets boot-counting tries to `3`, confirms the config value, pulls the runtime ref, deploys it, and asserts the only BLS entry is named `ostree-1+3.conf`.

State/persistence: mutates `sysroot/ostree/repo/config`, imports commit objects, and writes `sysroot/boot/loader/entries`. Dependencies are the admin test harness and syslinux boot setup.

Integration/risk/test signals: protects boot-counting naming consumed by bootloaders/systemd-bless-boot flows. Risk is exact file-name assumptions when boot counting format changes. TAP uses two `tap_ok` calls and `tap_end`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-boot-counting-tries.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-deploy-2.sh -->
# sources/cloud-native/ostree/tests/test-admin-deploy-2.sh

Purpose: regression suite for deployment cleanup and boot object lifecycle after repeated upgrades and deploys.

Important APIs/functions: `setup_os_repository`, `pull-local`, `ostree admin deploy`, `remote add`, `admin upgrade`, `os_repository_new_commit`, and filesystem assertions against `/boot/ostree`.

Control flow: deploys an initial runtime with kernel arguments, creates new commits, upgrades twice to rotate old deployments, verifies boot checksums and deployment directories, and checks that boot assets for no-longer-referenced deployments are collected while active ones remain.

State/persistence: writes sysroot deployments, bootloader entries, boot object directories, remote config, and test commits. It relies on exported `rev` and `bootcsum` from `libtest.sh`.

Integration/risk/test signals: validates admin deployment garbage collection across update generations. Risks include boot checksum coupling and assumptions about deployment index rotation. Eight TAP plan entries report command and layout success.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-deploy-2.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-deploy-bootid-gc.sh -->
# sources/cloud-native/ostree/tests/test-admin-deploy-bootid-gc.sh

Purpose: ensures failed deployment staging directories are scoped by boot ID and garbage-collected when a later deploy uses a different boot ID.

Important APIs/functions: uses `OSTREE_REPO_TEST_ERROR=pre-commit`, `OSTREE_BOOTID`, `ostree admin deploy`, and temporary staging path assertions under `sysroot/ostree/repo/tmp`.

Control flow: deploys a base commit, creates a new commit, forces a pre-commit failure with one synthetic boot ID, asserts a `staging-${TEST_BOOTID}-*` directory exists, then deploys with another boot ID and checks old staging is removed.

State/persistence: manipulates repo tmp staging directories and sysroot deployments. Dependencies include test-only OSTree failure injection and boot ID environment handling.

Integration/risk/test signals: targets cleanup of interrupted deploy transactions. Risks are reliance on private test error hooks and tmp naming format. The single TAP case passes when stale staging does not survive the replacement deploy.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-deploy-bootid-gc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-deploy-bootprefix.sh -->
# sources/cloud-native/ostree/tests/test-admin-deploy-bootprefix.sh

Purpose: verifies `sysroot.bootprefix=true` causes generated BLS entries to prefix kernel and initrd paths with `/boot`.

Important APIs/functions: `setup_os_repository`, `ostree config set sysroot.bootprefix true`, `pull-local`, `ostree admin deploy`, and `assert_file_has_content_literal`.

Control flow: builds a syslinux admin test repository, pulls a runtime ref, enables bootprefix in repo config, deploys with a root karg, and inspects `ostree-1.conf` for `linux /boot/ostree/testos-` and `initrd /boot/ostree/testos-`.

State/persistence: changes repo config and writes bootloader snippets. Dependencies are bootloader layout from the admin harness.

Integration/risk/test signals: protects compatibility with bootloaders or layouts requiring `/boot`-prefixed paths. Risk is exact BLS text matching if formatting changes. TAP reports one `bootprefix` case.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-deploy-bootprefix.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-deploy-clean.sh -->
# sources/cloud-native/ostree/tests/test-admin-deploy-clean.sh

Purpose: confirms undeploying the only deployment removes generated deployment refs from the sysroot repository.

Important APIs/functions: `setup_os_repository`, `pull-local`, `ostree admin deploy`, `ostree admin undeploy`, `ostree refs`, and negative content assertions.

Control flow: initializes a syslinux sysroot, pulls and deploys a runtime, undeploys index `0`, lists refs in `sysroot/ostree/repo`, and verifies no `ostree/` deployment refs remain.

State/persistence: writes then removes deployment state and bootloader artifacts; validates repository refs after cleanup. It depends on admin harness initialization and deployment-ref naming.

Integration/risk/test signals: catches leaks in generated deployment refs, which would affect pruning and status reporting. Risk is limited coverage of multiple-deployment cleanup. One TAP plan entry reports `deploy + undeploy repo prune`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-deploy-clean.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-deploy-composefs.sh -->
# sources/cloud-native/ostree/tests/test-admin-deploy-composefs.sh

Purpose: verifies admin deployment behavior when composefs support is available, including runtime disablement and artifact generation.

Important APIs/functions: `skip_without_ostree_feature composefs`, `setup_os_repository`, `ostree commit`, `pull-local`, `ostree admin deploy`, config file `usr/lib/ostree/prepare-root.conf`, and `.ostree.cfs` checks.

Control flow: writes a tree config disabling composefs at runtime, commits and deploys it, asserts a composefs blob is still generated, then mutates config/commits for additional deploy cases covering enabled behavior and metadata expectations.

State/persistence: creates commits with `version=*.composefs`, writes deployment directories and `.ostree.cfs` files. Dependencies include composefs-enabled OSTree and syslinux admin setup.

Integration/risk/test signals: validates composefs deployment artifacts independent from runtime mount policy. Risks include feature gating, exact artifact names, and external composefs capability changes. TAP output and file counts signal success.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-deploy-composefs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-deploy-emptyetc.sh -->
# sources/cloud-native/ostree/tests/test-admin-deploy-emptyetc.sh

Purpose: tests deployment when the committed tree contains an empty `/etc`, ensuring defaults from `/usr/etc` still populate the mutable deployment etc.

Important APIs/functions: `setup_os_repository`, direct mutation of `${test_tmpdir}/osdata`, `ostree commit`, `pull-local`, `ostree admin deploy`, `admin --print-current-dir`, and file content assertions.

Control flow: creates an empty `etc` directory in the source tree, commits it, pulls the runtime, deploys, resolves the current deployment path, and checks `etc/NetworkManager/nm.conf` contains the default daemon file.

State/persistence: updates the test OS repository and writes deployment `/etc`. Dependencies include the harness-created `/usr/etc/NetworkManager/nm.conf`.

Integration/risk/test signals: protects `/usr/etc` to `/etc` merge behavior when `/etc` exists but is empty. One TAP case reports `empty etc`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-deploy-emptyetc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-deploy-etcmerge-cornercases.sh -->
# sources/cloud-native/ostree/tests/test-admin-deploy-etcmerge-cornercases.sh

Purpose: exercises difficult `/etc` merge cases across deployments: modified files, directory permissions, removed paths, symlinks, and file/directory conflicts.

Important APIs/functions: `setup_os_repository`, `pull-local`, `ostree admin deploy`, `os_repository_new_commit`, shell filesystem mutation, `stat`, `readlink`, and assertion helpers.

Control flow: deploys a base commit, edits the live deployment's `/etc`, creates nested directories with custom modes, removes and replaces selected defaults, creates symlink cases, generates a new upstream commit, redeploys, and validates that local admin changes and permissions are merged or pruned as intended.

State/persistence: modifies deployed `/etc` in place and compares it with the next deployment. Dependencies are admin harness default config files and kernel boot state.

Integration/risk/test signals: covers one of OSTree admin's highest-risk persistence contracts: preserving local config without keeping obsolete defaults. Risks are broad fixture coupling and exact mode expectations. TAP ok lines segment the merge scenarios.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-deploy-etcmerge-cornercases.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-deploy-grub2.sh -->
# sources/cloud-native/ostree/tests/test-admin-deploy-grub2.sh

Purpose: runs the shared admin deployment suite with a grub2 bootloader configuration and ostree-grub-generator enabled.

Important APIs/functions: sources `libtest.sh`, calls `setup_os_repository "archive" "grub2 ostree-grub-generator"`, sets `extra_admin_tests=0`, and sources `admin-test.sh`.

Control flow: this wrapper delegates almost all behavior to `admin-test.sh`, which performs init-fs, deploy, status, rollback, undeploy, `/etc` merge, and bootloader validation checks.

State/persistence: creates a sysroot with grub2 config and all deployment artifacts exercised by the shared suite. Dependencies include grub2 fixture support and `bootloader-entries-crosscheck.py`.

Integration/risk/test signals: proves the generic admin suite works for grub2-specific bootloader integration. Risks are inherited from `admin-test.sh` plus grub2 file layout drift. TAP plan comes from the shared suite.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-deploy-grub2.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-deploy-karg.sh -->
# sources/cloud-native/ostree/tests/test-admin-deploy-karg.sh

Purpose: validates deployment-time kernel argument propagation, proc-cmdline import, and duplicate handling.

Important APIs/functions: `setup_os_repository`, `pull-local`, repeated `ostree admin deploy --karg=...`, `--karg-proc-cmdline`, and regex assertions against BLS `options` lines.

Control flow: deploys with base `root` and `quiet`, redeploys with additional kargs, checks they are carried forward into later deployments, imports current `/proc/cmdline`, and verifies filtered/expected arguments in loader entries.

State/persistence: updates `sysroot/boot/loader/entries/ostree-*.conf` and deployment metadata. Dependencies include host `/proc/cmdline`, so some assertions account for filtered bootloader-managed args.

Integration/risk/test signals: protects karg inheritance semantics used by admin deploy and upgrade. Risks are host cmdline variability and exact options ordering. Five TAP cases report karg scenarios.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-deploy-karg.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-deploy-nomerge.sh -->
# sources/cloud-native/ostree/tests/test-admin-deploy-nomerge.sh

Purpose: verifies `ostree admin deploy --no-merge` creates a fresh deployment without carrying forward mutable `/etc` changes or prior kernel args.

Important APIs/functions: `setup_os_repository`, `pull-local`, `ostree admin deploy`, `admin --print-current-dir`, and assertions on deployment files and BLS options.

Control flow: deploys with `root=LABEL=foo` and `testkarg=1`, writes a local file under `/etc`, redeploys with `--no-merge` and a different root karg, then checks the deployment changed, the local test file is gone, and old kargs are not present.

State/persistence: mutates deployment `/etc` and bootloader entries. Dependencies are syslinux admin setup.

Integration/risk/test signals: guards the explicit opt-out from deployment merging. Risk is narrow single-file coverage. One TAP case reports `no merge deployment`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-deploy-nomerge.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-deploy-none.sh -->
# sources/cloud-native/ostree/tests/test-admin-deploy-none.sh

Purpose: runs shared admin deploy tests with `sysroot.bootloader none` and then verifies BLS snippet generation despite an incidental grub2 directory.

Important APIs/functions: `setup_os_repository "archive" "sysroot.bootloader none"`, `admin-test.sh`, `pull-local`, `ostree admin deploy`, and file assertions for BLS, kernel, hmac, and initramfs.

Control flow: delegates the large deployment matrix to `admin-test.sh`, resets the sysroot, creates a fake `boot/grub2/grub.cfg`, deploys with bootloader `none`, and asserts OSTree updates BLS snippets and boot assets rather than invoking grub2 behavior.

State/persistence: writes bootloader config snippets and boot asset directories in a bootloader-none sysroot.

Integration/risk/test signals: protects a workaround for systems where grub2 files exist but OSTree bootloader management is disabled. Risks are inherited shared-suite breadth and exact output message matching.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-deploy-none.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-deploy-switch.sh -->
# sources/cloud-native/ostree/tests/test-admin-deploy-switch.sh

Purpose: validates `ostree admin switch` between refs and remotes, including expected error when switching to the same ref.

Important APIs/functions: `setup_os_repository`, `remote add`, `pull`, `admin deploy`, `admin switch`, `rev-parse`, and filesystem assertions under deployment `/usr/include`.

Control flow: deploys runtime, confirms devel header absent, attempts a same-ref switch and expects failure, switches to the devel ref and checks header presence, then adds another remote and exercises switching remote/ref origins.

State/persistence: updates remote config, origin files, deployment directories, and bootloader entries. Dependencies include runtime and devel refs created by the OS repository harness.

Integration/risk/test signals: protects branch/rebase-like admin switch behavior. Risks include assumptions about fixture refs and header content. Four TAP entries describe switch outcomes.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-deploy-switch.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-deploy-syslinux.sh -->
# sources/cloud-native/ostree/tests/test-admin-deploy-syslinux.sh

Purpose: runs shared admin deployment tests under syslinux and adds legacy boot-directory layout checks.

Important APIs/functions: `setup_os_repository "archive" "syslinux"`, `admin-test.sh`, `pull-local`, `ostree admin deploy`, and assertions for `boot/loader/entries`, `/boot/ostree`, and tree-local kernel/initramfs paths.

Control flow: executes the full `admin-test.sh` suite with three extra TAP cases, then iterates over legacy boot directories `boot` and `usr/lib/ostree-boot`, recreating the repository and verifying deployed boot assets are present in both sysroot boot storage and the deployment tree with checksummed names.

State/persistence: repeatedly recreates `sysroot`, `testos-repo`, and boot artifacts. Dependencies include syslinux fixture setup and `bootcsum`.

Integration/risk/test signals: covers syslinux-specific and historical boot path compatibility. Risks are exact path conventions and duplicate setup cost.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-deploy-syslinux.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-deploy-uboot.sh -->
# sources/cloud-native/ostree/tests/test-admin-deploy-uboot.sh

Purpose: runs shared admin deployment tests with u-boot and verifies uEnv boot script handling across upgrades.

Important APIs/functions: `setup_os_repository "archive" "uboot"`, `admin-test.sh`, `os_repository_new_commit`, `ostree commit`, and assertions around `uEnv.txt`, module directory `usr/lib/modules/3.6.0`, and kernel argument expansion.

Control flow: sets a module-style boot directory, delegates the common admin suite, creates a new commit containing `usr/lib/ostree-boot/uEnv.txt`, upgrades/deploys, and checks u-boot boot config behavior.

State/persistence: writes u-boot configuration, deployment boot assets, and additional commits. Dependencies include uboot fixture functions and kernel version variable `kver`.

Integration/risk/test signals: protects u-boot-specific bootloader integration and boot checksum recalculation. Risks are text-template fragility and inherited shared-suite coupling.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-deploy-uboot.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-deploy-var.sh -->
# sources/cloud-native/ostree/tests/test-admin-deploy-var.sh

Purpose: validates initial `/var` population from a commit when the `initial-var` feature is enabled.

Important APIs/functions: `has_ostree_feature initial-var`, `setup_os_repository`, direct `osdata/var/lib` creation, `ostree commit`, `pull-local`, `admin deploy`, and file assertions under `sysroot/ostree/deploy/testos/var`.

Control flow: checks feature availability, creates `var/lib/somefile` in the OS tree, commits and pulls it, deploys, then confirms the stateroot var contains the file. It later creates tmpfiles-style data and verifies expected var behavior across additional commits.

State/persistence: writes stateroot shared var, deployment usr trees, and commits. Dependencies include feature support and syslinux setup.

Integration/risk/test signals: protects one-time initial var seeding without confusing deployment-local usr data. Risks include feature-gated behavior and broad `ls -R` diagnostics. Assertions on var content are the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-deploy-var.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-deploy-whiteouts.sh -->
# sources/cloud-native/ostree/tests/test-admin-deploy-whiteouts.sh

Purpose: validates deployment of OCI-style whiteout device nodes and preservation of their permissions.

Important APIs/functions: `skip_without_whiteouts_devices`, `setup_os_repository`, `pull-local`, `ostree admin deploy`, `admin --print-current-dir`, `assert_is_whiteout_device`, and mode/file absence assertions.

Control flow: deploys the runtime tree containing container layer whiteouts, resolves current deployment, asserts a whiteout device exists, confirms `.ostree-wh.whiteout` marker files are not materialized, and verifies modes for multiple whiteout entries.

State/persistence: reads deployment `/usr/container/layers/...` content from the committed fixture and writes boot deployment state. Dependencies include device-node support/privileges.

Integration/risk/test signals: protects container image whiteout translation in admin deployments. Risks are privilege and filesystem capability requirements. Three TAP cases cover device, marker absence, and permissions.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-deploy-whiteouts.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-gpg.sh -->
# sources/cloud-native/ostree/tests/test-admin-gpg.sh

Purpose: validates admin deploy/status behavior for GPG-signed commits pulled over HTTP.

Important APIs/functions: custom `setup_os_repository_signed()` builds a signed OS repo using `--gpg-sign` and `--gpg-homedir`; uses `ostree remote add`, `pull-local --gpg-verify=true`, `admin deploy`, `admin status`, and `admin status --verify`.

Control flow: skips without `OSTREE_HTTPD`, creates signed runtime/devel commits and HTTP serving symlink, initializes sysroot and bootloader, adds remote, pulls with verification, deploys, and checks status output includes valid GPG signature information without missing-key errors.

State/persistence: creates signed repo objects, commitmeta signatures, HTTP daemon state, sysroot deployments, and bootloader assets. Dependencies include gpgme, test gpghome, and HTTP test server.

Integration/risk/test signals: bridges repository signing with admin status verification. Risks include GPG environment brittleness and exact status text. Two TAP cases cover deploy and signature display.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-gpg.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-instutil-set-kargs.sh -->
# sources/cloud-native/ostree/tests/test-admin-instutil-set-kargs.sh

Purpose: tests `ostree admin instutil set-kargs` replacement, merge, replace, append, and proc-cmdline import behavior.

Important APIs/functions: `setup_os_repository`, `pull-local`, `admin deploy`, `admin instutil set-kargs`, options `--merge`, `--replace`, `--append`, `--import-proc-cmdline`, and loader entry regex assertions.

Control flow: deploys once, replaces all kargs, merges an additional duplicate, replaces matching `FOO`, appends multiple values including duplicates, and imports `/proc/cmdline` while skipping `ostree=`, `initrd=`, and `BOOT_IMAGE=` arguments.

State/persistence: edits the active bootloader entry in `sysroot/boot/loader/entries`. Dependencies include host proc cmdline and admin sysroot state.

Integration/risk/test signals: protects low-level installed-system karg editing. Risks are host-specific cmdline values and options ordering. Five TAP cases align with the command modes.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-instutil-set-kargs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-kargs.sh -->
# sources/cloud-native/ostree/tests/test-admin-kargs.sh

Purpose: validates `ostree admin kargs edit-in-place --append-if-missing` for both key/value and bare keyword arguments.

Important APIs/functions: `setup_os_repository`, `pull-local`, `admin deploy`, `admin kargs edit-in-place`, and negative duplicate checks against the loader `options` line.

Control flow: deploys with root and quiet, appends `TESTARG=TESTVALUE` and `ARGWITHOUTKEY`, asserts both appear, then repeats `quiet` and `TESTARG=TESTVALUE` append-if-missing operations and verifies no duplicate trailing entries are created.

State/persistence: mutates the deployment bootloader entry in place. Dependencies are syslinux bootloader layout and command-line parser behavior.

Integration/risk/test signals: protects idempotent karg editing for scripts/tools. Risks are regex limitations for duplicate detection. Two TAP cases cover basic append and duplicate suppression.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-kargs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-locking.sh -->
# sources/cloud-native/ostree/tests/test-admin-locking.sh

Purpose: stress-tests admin deployment locking by running many concurrent retained deploys.

Important APIs/functions: `setup_os_repository`, GNU `parallel`, `getconf _NPROCESSORS_ONLN`, `ostree admin deploy --retain`, `admin status`, and line-count assertions.

Control flow: skips if GNU parallel is unavailable, pulls and deploys a base runtime, computes twice the online CPU count, launches that many parallel deploy commands, then checks `ostree admin status` contains the expected number of matching deployments.

State/persistence: concurrently writes sysroot deployments, bootloader entries, repo refs, and lock-protected admin state. Dependencies include GNU parallel and sufficient filesystem capacity.

Integration/risk/test signals: catches races in admin lock acquisition and deployment list mutation. Risks include slow/flaky behavior under high CPU counts and exact status counting. One TAP case reports `deploy locking`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-locking.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-pull-deploy-commit.sh -->
# sources/cloud-native/ostree/tests/test-admin-pull-deploy-commit.sh

Purpose: regression test for deploying a directly pulled commit checksum rather than a ref.

Important APIs/functions: `setup_os_repository`, `remote add`, `pull`, `rev-parse`, `ostree admin deploy`, and parent commit resolution through `${rev}^`.

Control flow: creates a sysroot, adds a remote, pulls the runtime ref, resolves its parent commit, explicitly pulls that parent checksum, then deploys the parent by checksum with kernel arguments.

State/persistence: imports commit objects and writes one deployment. Dependencies include a repository history with at least one parent commit.

Integration/risk/test signals: protects issue-era behavior where pulled commits without ref names must remain deployable. Risk is limited to parent commit fixture shape. One TAP case reports `deploy pulled commit`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-pull-deploy-commit.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-pull-deploy-split.sh -->
# sources/cloud-native/ostree/tests/test-admin-pull-deploy-split.sh

Purpose: tests split `ostree admin upgrade --pull-only` and `--deploy-only` workflows.

Important APIs/functions: `setup_os_repository`, `remote add`, `pull`, `pull ref@checksum`, `admin deploy`, `admin upgrade --pull-only`, `admin upgrade --deploy-only`, and BLS/deployment directory assertions.

Control flow: deploys an older parent revision under a refspec, runs pull-only twice and confirms new content is available but not deployed, creates another upstream commit, runs deploy-only and confirms it deploys the already-pulled revision rather than the latest upstream, then checks a second deploy-only is a no-op.

State/persistence: maintains remote refs, local deployment directories, and boot entries across split phases.

Integration/risk/test signals: protects transactional separation for update managers. Risks are subtle duplicate `--os` usage and fixture revision assumptions. One TAP case covers the split workflow.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-pull-deploy-split.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-stateroot.sh -->
# sources/cloud-native/ostree/tests/test-admin-stateroot.sh

Purpose: validates stateroot initialization and `set-default` bootconfig swap decisions.

Important APIs/functions: `setup_os_repository`, `admin deploy`, `admin status`, `admin stateroot-init`, `admin set-default`, grep/sed ref extraction, and output assertions for `bootconfig swap`.

Control flow: deploys on `testos`, extracts the deployed ref, creates `testos2`, deploys the same ref there, sets default to the new stateroot and expects `bootconfig swap: yes`; then deploys identical entries again and expects `bootconfig swap: no`.

State/persistence: writes multiple stateroots under `sysroot/ostree/deploy` and bootloader ordering state. Dependencies include stable `admin status` text.

Integration/risk/test signals: protects bootloader update minimization across stateroots. Risks are parsing status output and index-based default selection. Two TAP cases cover changed vs equal deployments.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-stateroot.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-upgrade-endoflife.sh -->
# sources/cloud-native/ostree/tests/test-admin-upgrade-endoflife.sh

Purpose: verifies upgrade handling of commits marked end-of-life with a rebase target.

Important APIs/functions: `setup_os_repository`, `remote add`, `pull`, `admin deploy`, `os_repository_new_commit`, `ostree commit --add-metadata-string ostree.endoflife*`, `admin upgrade --pull-only`, and `--deploy-only`.

Control flow: deploys the runtime branch, creates a new branch, commits an empty EOL marker on the original branch with `ostree.endoflife` and `ostree.endoflife-rebase`, runs split upgrade, and checks the deployment moved to the new branch with expected boot checksum, content iteration, and origin.

State/persistence: writes branch refs, EOL metadata, origin files, and deployment directories. Dependencies include metadata-aware upgrade logic.

Integration/risk/test signals: protects product EOL rebasing semantics. Risks are exact origin content and boot checksum coupling. TAP ok lines cover initial deploy, new branch creation, and redirect update.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-upgrade-endoflife.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-upgrade-not-backwards.sh -->
# sources/cloud-native/ostree/tests/test-admin-upgrade-not-backwards.sh

Purpose: ensures admin upgrade refuses chronologically older commits unless downgrades are explicitly allowed.

Important APIs/functions: `setup_os_repository`, `remote add`, `pull`, `admin deploy`, `admin upgrade`, `admin upgrade --allow-downgrade`, timestamped `ostree commit`, and object-path helpers.

Control flow: deploys a ref, performs a normal upgrade, creates a new upstream commit with an old timestamp and new content, attempts upgrade and expects a chronological error without importing the new file object, then reruns with `--allow-downgrade` and expects success.

State/persistence: mutates upstream repo history and sysroot repo objects; checks absence/presence of content object paths. Dependencies include timestamp comparison logic.

Integration/risk/test signals: protects downgrade safety during upgrades. Risks are time metadata and exact error text. TAP reports refusal and allowed downgrade.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-upgrade-not-backwards.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-upgrade-systemd-update.sh -->
# sources/cloud-native/ostree/tests/test-admin-upgrade-systemd-update.sh

Purpose: verifies `.updated` stamp files used by systemd-update-style flows are removed from new deployments and shared var during upgrade.

Important APIs/functions: `setup_os_repository "archive-z2"`, `remote add`, `pull`, `admin deploy`, `os_repository_new_commit`, `admin upgrade`, `touch -r`, and file existence assertions.

Control flow: deploys once, confirms no `.updated` stamps, creates stamps in deployment `/etc` and stateroot `/var`, creates a new commit, upgrades, and checks the new deployment and shared var lack stamps while the previous deployment's `/etc/.updated` remains.

State/persistence: writes deployment-local etc stamps and stateroot var stamps. Dependencies include archive-z2 setup and upgrade behavior.

Integration/risk/test signals: protects cleanup of update markers across deployment boundaries. Risk is mtime/source directory assumptions. Two TAP cases cover deploy and stamp removal.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-upgrade-systemd-update.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-upgrade-unconfigured.sh -->
# sources/cloud-native/ostree/tests/test-admin-upgrade-unconfigured.sh

Purpose: validates user-facing failure when a deployment origin is marked unconfigured and confirms switching can move to a configured remote.

Important APIs/functions: `setup_os_repository`, `pull-local`, `admin deploy`, manual edit of `.origin`, `remote add`, `admin upgrade`, and `admin switch`.

Control flow: deploys a runtime, appends `unconfigured-state=...` to the deployment origin, adds the remote, attempts upgrade and expects the subscription-style message, then adds another remote and switches to it successfully.

State/persistence: mutates the active deployment origin file and remote config. Dependencies include origin parsing and unconfigured-state validation.

Integration/risk/test signals: protects subscription/unconfigured remote UX and switch escape path. Risks are exact error message regexes. Two TAP cases report error and switch success.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-admin-upgrade-unconfigured.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-archivez.sh -->
# sources/cloud-native/ostree/tests/test-archivez.sh

Purpose: checks archive-z2 compatibility, including archive-z2 alias initialization and pulling from a file URI.

Important APIs/functions: `setup_test_repository "archive"`, `ostree init --mode=archive-z2`, `remote add`, `pull`, `rev-parse`, and `fsck`.

Control flow: creates a standard archive repository fixture, initializes a second repo using the archive-z2 alias, then creates another repo with a file remote pointed at the fixture, pulls the test branch, resolves the remote ref, and fscks.

State/persistence: writes `repo-archive-z2`, `repo2`, remote config, and imported objects. Dependencies include local file URI support and archive mode compatibility.

Integration/risk/test signals: protects mode alias compatibility and local pull behavior. Risks are narrow coverage of archive-z2 beyond initialization. Two TAP cases report init and file pull.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-archivez.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-auto-summary.sh -->
# sources/cloud-native/ostree/tests/test-auto-summary.sh

Purpose: tests automatic summary update configuration for commits and ref mutations.

Important APIs/functions: `setup_test_repository "bare"`, `$OSTREE commit`, `summary --update`, `config set core.commit-update-summary`, `config set core.auto-update-summary`, `reset`, `refs --delete`, and md5 comparisons.

Control flow: creates a summary, confirms ordinary commits do not update it, enables `commit-update-summary` and confirms commit changes it, verifies manual summary update deletes `summary.sig`, then tests `auto-update-summary` for adding, changing, and deleting refs.

State/persistence: mutates `repo/summary`, `repo/summary.sig`, branch refs, and repo config. Dependencies are deterministic summary file changes.

Integration/risk/test signals: protects repository metadata freshness knobs. Risks include MD5 comparison sensitivity to unrelated summary metadata and system clock changes. Four TAP plan entries are emitted.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-auto-summary.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-backcompat-fsck.sh -->
# sources/cloud-native/ostree/tests/test-backcompat-fsck.sh

Purpose: verifies fsck compatibility for archive commits containing many user xattrs, including optional cross-check with the system-installed OSTree.

Important APIs/functions: `skip_without_user_xattrs`, `setup_test_repository "archive"`, `checkout`, `setfattr`, `commit --canonical-permissions --consume`, `fsck`, and optional `/usr/bin/ostree --repo=repo fsck`.

Control flow: checks out `test2`, adds 100 `user.*` xattrs to a file, recommits with canonical permissions, fscks with the built/test OSTree, then if `/usr/bin/ostree` exists, runs it with `LD_LIBRARY_PATH` unset to validate backward compatibility.

State/persistence: writes xattr-rich content objects and consumes the checkout. Dependencies include user xattrs and optionally a system OSTree binary.

Integration/risk/test signals: protects object/xattr canonicalization compatibility. Risks are environment-dependent skips and installed binary version variability. TAP reports fsck and optional compat.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-backcompat-fsck.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-basic-bare-split-xattrs.sh -->
# sources/cloud-native/ostree/tests/test-basic-bare-split-xattrs.sh

Purpose: tests experimental `bare-split-xattrs` repository mode initialization, fsck, disabled writes, and fixture reading.

Important APIs/functions: `ostree init --mode bare-split-xattrs`, `fsck --all`, `commit --orphan`, environment `OSTREE_EXP_WRITE_BARE_SPLIT_XATTRS=true`, sudo tar extraction, `log`, `ls -X`, symlink and xattr assertions.

Control flow: verifies mode init/config, fsck on empty repo, rejects normal commit, allows experimental commit but expects fsck failure, then if privileged/sudo-capable extracts a fixture tarball and validates commit log, xattr output, and symlink content.

State/persistence: creates/removes `repo`, `files`, and fixture objects. Dependencies include sudo for ownership-preserving fixture extraction.

Integration/risk/test signals: documents and guards an experimental storage mode. Risks include privilege gating and intentionally failing experimental writes. TAP marks fixture read skipped if sudo is unavailable.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-basic-bare-split-xattrs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-basic-c.c -->
# sources/cloud-native/ostree/tests/test-basic-c.c

Purpose: GLib C unit tests for low-level libostree repository, content stream, xattr, hardlink, and validation APIs.

Important APIs/types/functions: uses `OstreeRepo`, `OstreeRepoDevInoCache`, `OstreeRepoCommitModifier`, `OstreeMutableTree`, `ostree_raw_file_to_archive_z2_stream`, `ostree_content_stream_parse`, `ostree_repo_write_content`, `ostree_repo_write_regfile_inline`, `ostree_break_hardlink`, `ostree_validate_remote_name`, `ostree_fs_get_all_xattrs`, and `ostree_validate_structureof_dirmeta`.

Control flow: sets up a test repo, registers GLib tests for repo-not-system, archive stream roundtrip, object writes and checksum failures, devino-cache xattr callbacks, hardlink breaking, remote-name validation, large metadata commits, xattr reading, and invalid dirmeta xattrs.

State/persistence: creates temporary repos/checkouts, writes content objects, metadata objects, hardlinks, symlinks, and xattrs. Dependencies include GLib/GIO, libglnx, `libostreetest`, xattr support, and shell harness invocation from C.

Integration/risk/test signals: covers core library contracts beneath CLI tests. Risks are feature-dependent skips and direct use of internal object encodings. GLib test paths and assertions signal success.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-basic-c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-basic-root.sh -->
# sources/cloud-native/ostree/tests/test-basic-root.sh

Purpose: root-only ownership behavior tests for bare repositories and checkout modes.

Important APIs/functions: `id -u`, `skip`, `setup_test_repository "bare"`, `$OSTREE checkout`, `$OSTREE commit --owner-uid`, `$OSTREE ls`, hardlink checkout `-H`, user checkout `-U`, and `stat`.

Control flow: skips unless running as uid 0, commits a tree with owner uid incremented from root, validates `ostree ls` ownership, checks hardlinked/copy checkouts preserve ownership, then confirms user-mode checkout maps ownership to the current user.

State/persistence: writes a bare repo commit and temporary checkouts. Dependencies include root privileges and filesystem ownership support.

Integration/risk/test signals: protects ownership preservation in privileged bare repo operations. Risks are container uid assumptions and lack of `-C` coverage noted in comments. One TAP case reports ownership.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-basic-root.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-basic-user-only.sh -->
# sources/cloud-native/ostree/tests/test-basic-user-only.sh

Purpose: wrapper plus extra cases for `bare-user-only` repository mode.

Important APIs/functions: `setup_test_repository bare-user-only`, sources `basic-test.sh`, parses `ostree --version` as YAML, tests `pull-local`, `commit --statoverride`, metadata key validation, permissions canonicalization, hardlink pulls from bare-user, and `checkout --force-copy/--union-identical`.

Control flow: runs the shared 91-case basic suite with seven extra tests, resets repos to test rejection of setuid content and empty metadata keys, preserves group-writable files, canonicalizes world-writable dirs and file modes, validates safe hardlinking, and confirms automatic canonical permissions.

State/persistence: repeatedly recreates `repo`, `repo-input`, `files`, and checkouts. Dependencies include YAML Python module and optional user xattrs.

Integration/risk/test signals: protects the unprivileged object model that strips unsafe metadata. Risks are broad inherited state from `basic-test.sh` and feature-dependent branches. Extra `ok` lines extend the TAP plan.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-basic-user-only.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-basic-user.sh -->
# sources/cloud-native/ostree/tests/test-basic-user.sh

Purpose: wrapper plus extra tests for `bare-user` repositories with user xattrs.

Important APIs/functions: `skip_without_user_xattrs`, `setup_test_repository bare-user`, sources `basic-test.sh`, uses object-path helpers, `checkout -U -H`, `commit --statoverride`, `--link-checkout-speedup`, `--owner-uid/gid`, and `-I` devino canonicalization.

Control flow: runs shared basic tests with six extras, resets state, verifies committed object modes, checkout modes, unwritable/unreadable file handling, unioning component checkouts with distinct ownership, and precedence between owner overrides, link-checkout speedup, and devino cache reuse.

State/persistence: creates bare-user content objects, component refs, rootfs checkouts, and mode-specific object files. Dependencies include user xattrs and uid/gid support.

Integration/risk/test signals: protects user-mode storage semantics and ownership preservation. Risks include many setup resets and filesystem permission assumptions. TAP ok lines report each mode-specific behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-basic-user.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-basic.sh -->
# sources/cloud-native/ostree/tests/test-basic.sh

Purpose: minimal wrapper that runs the shared `basic-test.sh` suite for a privileged `bare` repository.

Important APIs/functions: sources `libtest.sh`, calls `skip_without_no_selinux_or_relabel`, sets `mode="bare"`, runs `setup_test_repository "$mode"`, and sources `basic-test.sh`.

Control flow: after environment capability checks and fixture setup, all behavior is delegated to `basic-test.sh`, which covers checkout, commit, diff, pull-local, xattrs, refs, cat, union checkout, statoverride, skip lists, and pruning.

State/persistence: creates the standard `repo`, `files`, and many temporary checkouts through the shared suite. Dependencies include the libtest harness and compatible SELinux/relabeling environment.

Integration/risk/test signals: validates the broad basic CLI contract for the canonical bare mode. Risk is inherited from the large shared script; this wrapper mainly selects mode and gating.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-basic.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-bloom.c -->
# sources/cloud-native/ostree/tests/test-bloom.c

Purpose: GLib unit tests for OSTree's private bloom filter implementation.

Important APIs/types/functions: `OstreeBloom`, `ostree_bloom_new`, `ostree_bloom_new_from_bytes`, `ostree_bloom_get_size`, `ostree_bloom_get_k`, `ostree_bloom_get_hash_func`, `ostree_bloom_add_element`, `ostree_bloom_seal`, `ostree_bloom_maybe_contains`, and `ostree_str_bloom_hash`.

Control flow: registers tests for constructor initialization, building/sealing/reloading a filter, empty-filter negative membership, and membership checks while incrementally adding elements.

State/persistence: all state is in-memory `OstreeBloom` and `GBytes`; no filesystem persistence. Dependencies are GLib and private bloom headers.

Integration/risk/test signals: protects summary/repo-finder acceleration primitives that rely on stable hashes. Risks are false-positive theory versus tests that expect specific non-members to be false because the hash function is stable. GLib test paths report success.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-bloom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-bootconfig-parser-internals.c -->
# sources/cloud-native/ostree/tests/test-bootconfig-parser-internals.c

Purpose: tests internal bootconfig parser helpers by including `ostree-bootconfig-parser.c` directly.

Important APIs/functions: `parse_bootloader_tries`, `OstreeBootconfigParser`, `ostree_bootconfig_parser_set/get`, `_ostree_bootconfig_parser_get_extra_keys_variant`, `_ostree_bootconfig_parser_set_extra_keys_from_variant`, `parse_at`, and `write_at`.

Control flow: validates valid and invalid boot counting suffix parsing, verifies standard BLS keys are excluded from extra-key variants, preserves extension/custom keys, roundtrips extra keys through variants, and parses/writes a BLS file while keeping extension keys.

State/persistence: mostly in-memory parser objects; one test writes temporary BLS files and rereads them. Dependencies include GLib and private source inclusion, so it tracks internal implementation closely.

Integration/risk/test signals: protects boot counting and BLS extension metadata preservation. Risks are tight coupling to private functions and standard-key list changes. GLib test paths under `/bootconfig-parser/...` signal success.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-bootconfig-parser-internals.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-bsdiff.c -->
# sources/cloud-native/ostree/tests/test-bsdiff.c

Purpose: verifies bundled bsdiff/bspatch integration can create and apply a binary patch.

Important APIs/functions: `bsdiff`, `bspatch`, custom `bzdiff_write()` appending to `GMemoryOutputStream`, `bzpatch_read()` reading from `GMemoryInputStream`, and GLib byte stream helpers.

Control flow: defines old/new byte arrays, runs `bsdiff` into an in-memory stream, closes it, feeds the patch through `bspatch`, and asserts generated output byte-for-byte matches the target.

State/persistence: all state is in memory; no repository or filesystem writes. Dependencies include GLib and the bsdiff implementation headers.

Integration/risk/test signals: protects static delta binary diff primitives. Risks are narrow fixed fixture size and lack of error-path coverage. A single GLib `/bsdiff` test reports success.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-bsdiff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-checksum.c -->
# sources/cloud-native/ostree/tests/test-checksum.c

Purpose: tests parsing of static delta name strings into from/to checksums.

Important APIs/functions: `ostree_parse_delta_name`, GLib `g_assert_cmpstr`, `g_assert_null`, and `g_test_add_func`.

Control flow: feeds valid one-ended and two-ended delta names and several invalid forms into the parser. It checks expected `from` and `to` checksum pointers for each case, including null values when parsing should fail or represent an empty-from delta.

State/persistence: no persistent state; all allocations are local strings. Dependencies include libostree checksum/delta parser code and GLib tests.

Integration/risk/test signals: protects CLI and repo code that interprets `FROM-TO` delta identifiers. Risks are limited cases and dependence on fixed checksum constants. The `/ostree_parse_delta_name` GLib test is the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-checksum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-cli-extensions.sh -->
# sources/cloud-native/ostree/tests/test-cli-extensions.sh

Purpose: validates OSTree CLI extension command discovery and unknown-command error behavior.

Important APIs/functions: uses `${CMD_PREFIX} ostree env`, `${CMD_PREFIX} ostree nosuchcommand`, `assert_file_has_content`, and `assert_not_reached`.

Control flow: runs the `env` extension and checks it receives/prints a custom test flag, then runs a nonexistent command and expects a clean `Unknown command 'nosuchcommand'` error instead of invoking an absent extension.

State/persistence: writes `out.txt` and `err.txt` only. Dependencies include the test environment's local extension path and `libtest.sh` assertions.

Integration/risk/test signals: protects command dispatch between built-in commands and `ostree-*` extension binaries. Risks are environment path setup and exact error wording. Two TAP ok messages cover extension and unknown command.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-cli-extensions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-commit-sign-sh-ext.c -->
# sources/cloud-native/ostree/tests/test-commit-sign-sh-ext.c

Purpose: C companion test for commit signature verification APIs, invoked by the shell GPG signing test when running uninstalled.

Important APIs/functions: `ostree_repo_resolve_rev`, `ostree_repo_load_variant`, `ostree_repo_read_commit_detached_metadata`, `ostree_repo_signature_verify_commit_data`, helper `corrupt()`, and `assert_error_contains()`.

Control flow: opens the test repo, loads `origin:main` commit data and detached metadata, verifies signatures for remote `origin`, then checks expected failures for no enabled verification types, empty metadata, missing remote, and corrupted commit bytes.

State/persistence: reads an existing repo prepared by `test-commit-sign.sh`; no writes beyond process allocations. Dependencies include signed test data, GLib, and libostree signature modules.

Integration/risk/test signals: protects lower-level signature verification independent of CLI pull. Risks are relying on caller-prepared repo/remotes and exact error substrings. Exit status from the C test is the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-commit-sign-sh-ext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-commit-sign.sh -->
# sources/cloud-native/ostree/tests/test-commit-sign.sh

Purpose: end-to-end tests for GPG-signed commits, signature verification during pull/show, corrupted signatures, and signature addition/deletion after content is already present.

Important APIs/functions: `skip_without_ostree_feature gpgme`, `setup_fake_remote_repo1`, `ostree commit --gpg-sign`, `ostree pull`, `show --gpg-verify-remote`, `gpg-sign --delete`, and optional `test-commit-sign-sh-ext`.

Control flow: creates multiple signed remote commits, verifies pull fails without trusted keys, succeeds with the fixture key, optionally runs C API tests, corrupts detached signature metadata and expects verified pulls to fail, disables GPG to repull corrupted content, then tests pulling an unsigned commit that is later signed and later signature-deleted.

State/persistence: mutates remote commitmeta files, local repo signatures, HTTP serving state, and gpghome trust. Dependencies include gpgme and test keys.

Integration/risk/test signals: protects signature lifecycle and detached metadata synchronization. Risks are GPG environment fragility and exact signature count output. TAP plan covers pull/verify/corruption/update cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-commit-sign.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-commit-timestamp.sh -->
# sources/cloud-native/ostree/tests/test-commit-timestamp.sh

Purpose: verifies explicit and reproducible commit timestamp inputs.

Important APIs/functions: `ostree commit --timestamp='@1234567890'`, `ostree show`, environment `SOURCE_DATE_EPOCH`, and error assertions for invalid/overflowing values.

Control flow: initializes `testrepo`, commits with a CLI timestamp and checks displayed date, commits with `SOURCE_DATE_EPOCH`, verifies invalid and overflowing environment values fail, and confirms the valid environment timestamp appears in `show`.

State/persistence: writes commits to `testrepo` and captures show/error output files. Dependencies include stable UTC date formatting.

Integration/risk/test signals: protects reproducible build timestamp behavior and input validation. Risks are date formatting changes and platform-specific overflow wording, handled with an alternation regex. Two TAP cases cover CLI and environment timestamps.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-commit-timestamp.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-composefs.sh -->
# sources/cloud-native/ostree/tests/test-composefs.sh

Purpose: tests composefs metadata generation and composefs checkout modes.

Important APIs/functions: `skip_without_ostree_feature composefs`, `setup_test_repository bare-user`, `commit --generate-composefs-metadata`, `show --print-metadata-key ostree.composefs.digest.v0`, `checkout --composefs`, `checkout --composefs-noverity`, `composefs-info dump`, and corrupted digest validation.

Control flow: commits a checkout with and without composefs metadata, verifies deterministic digest, performs verity and noverity composefs checkouts, validates image digests and dumped file metadata, then commits a deliberately bad digest and expects checkout to fail.

State/persistence: writes commits, composefs image files, and dump/error files. Dependencies include composefs support, composefs-info, and user xattrs.

Integration/risk/test signals: protects composefs metadata determinism and checkout integrity. Risks include hard-coded digest values and external tool output format. TAP cases cover metadata, checkout, noverity, and bad digest.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-composefs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-concurrency.py -->
# sources/cloud-native/ostree/tests/test-concurrency.py

Purpose: Python stress test for concurrent commits and prunes against the same repository.

Important APIs/functions: `subprocess.Popen`, helper `mktree()`, `commit(v)`, `prune()`, `wait_check(proc)`, and `run(n_committers, n_pruners)`. It shells out to `ostree --repo=repo init`, `commit --fsync=0`, and `prune`.

Control flow: creates several small trees, starts an even number of committers against repeated trees and a configurable number of pruners, waits for processes, prints diagnostics, and fails if any child exits unsuccessfully.

State/persistence: creates `repo` and temporary tree directories named by serial. Dependencies include Python 3 and the `ostree` CLI on `PATH`.

Integration/risk/test signals: catches repository lock/transaction races under simultaneous write and prune workloads. Risks are timing sensitivity and limited corruption checks beyond child exit status. Failure prints process output and exits nonzero.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-concurrency.py -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-config.sh -->
# sources/cloud-native/ostree/tests/test-config.sh

Purpose: validates `ostree config get/set/unset` behavior, grouped remote keys, argument errors, and value validation.

Important APIs/functions: `setup_test_repository bare`, `ostree remote add --set`, `ostree config get`, `set`, `unset`, `--group`, `--` separator, and config file assertions.

Control flow: creates remotes with custom keys, reads core and remote values, verifies too-many-argument errors, updates core and remote values, unsets keys including missing/remote groups, validates missing-key errors, and checks `core.min-free-space-size` rejects invalid values while accepting `100MB`.

State/persistence: mutates `repo/config` and remote entries. Dependencies include GLib keyfile error wording and config validation code.

Integration/risk/test signals: protects CLI config editing used by scripts and admins. Risks are exact keyfile error text and quoting/group syntax. TAP ok lines cover get, set, unset, and validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-config.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-core.js -->
# sources/cloud-native/ostree/tests/test-core.js

Purpose: GJS introspection test for core libostree repository APIs from JavaScript.

Important APIs/types/functions: imports `Gio` and `OSTree`, defines `assertEquals()` and `assertThrows()`, uses `Repo.new`, `repo.create`, `prepare_transaction`, `write_directory_to_mtree`, `write_mtree`, `write_commit`, `read_commit`, `transaction_set_refspec`, and `commit_transaction`.

Control flow: creates a repo, builds a mutable tree from a Gio file/directory, writes a commit with subject/body, reads it back, sets a refspec transactionally, resolves/reads it, and checks expected exceptions for invalid operations.

State/persistence: writes a local OSTree repo, commits, and refs. Dependencies include GJS, GI bindings for OSTree, Gio, and ByteArray.

Integration/risk/test signals: protects public introspection bindings, not just C ABI. Risks include binding signature changes and JS exception text. Process exit status and explicit assertions are the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-core.js -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-corruption.sh -->
# sources/cloud-native/ostree/tests/test-corruption.sh

Purpose: tests `ostree fsck` detection and cleanup behavior for corrupted or missing objects and path traversal dirtrees.

Important APIs/functions: `setup_test_repository bare`, `$OSTREE fsck -q`, `fsck --delete`, `fsck -a --delete`, object path helpers, manual chmod/truncation/deletion/corruption, and checkout of path traversal fixture.

Control flow: creates repos, damages object permissions and metadata, deletes commits, verifies path traversal fsck and checkout errors, removes or corrupts file objects, confirms commits are marked partial, and checks `--all` reports multiple corrupted files.

State/persistence: intentionally mutates `repo/objects`, `repo/state/*.commitpartial`, and extracted `ostree-path-traverse` fixture data. Dependencies include object layout helpers and tar fixture.

Integration/risk/test signals: protects repository integrity checks and partial-commit marking. Risks are exact error string matching and direct object layout coupling. TAP ok lines cover each corruption class.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-corruption.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-create-usb.sh -->
# sources/cloud-native/ostree/tests/test-create-usb.sh

Purpose: validates `ostree create-usb` for collection refs, destination repo placement, summaries, and repo-finder integration.

Important APIs/functions: `skip_without_ostree_feature gpgme`, `ostree init`, signed commits and `summary --update --gpg-sign`, `remote add --collection-id --gpg-import`, `pull`, `create-usb`, `refs --collections`, `summary -v`, symlink assertions, and repo-finder output checks.

Control flow: builds a signed source repo with several refs, pulls them into a local repo, creates USB repositories in default, standard, and non-standard destinations, appends refs to an existing USB, and checks finder output includes trusted keyring and collection-ref checksums.

State/persistence: writes mount-like directories `dest-mount*`, `.ostree/repo`, `.ostree/repos.d` symlinks, summaries, and trusted keyrings. Dependencies include GPG fixture keys.

Integration/risk/test signals: protects offline media creation and discovery. Risks are symlink path expectations and GPG feature gating. Five TAP cases cover USB variants and finder lookup.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-create-usb.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-delta-ed25519.sh -->
# sources/cloud-native/ostree/tests/test-delta-ed25519.sh

Purpose: exhaustive static delta signing and verification tests for the ed25519 signature module.

Important APIs/functions: `skip_without_ostree_feature sign-ed25519`, `static-delta generate --sign-type=ed25519`, `--sign`, `--keys-file`, `--inline`, `static-delta verify`, `static-delta apply-offline`, `--keys-dir`, and helper functions for file permutation and delta directory lookup.

Control flow: creates two revisions, signs deltas with inline keys and key files, verifies with correct, wrong, and multiple public keys, validates failure with bad key files, tests public-key files and multiple keys, applies offline with key files/directories, and checks revocation behavior.

State/persistence: writes `repo/deltas`, key files under the temp dir, `repo2` apply targets, and signature material. Dependencies include user xattrs and ed25519 support.

Integration/risk/test signals: protects modern signature verification for delta transport. Risks include hard-coded key material and large matrix maintenance. TAP ok lines segment each key mode and apply-offline scenario.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-delta-ed25519.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-delta-sign.sh -->
# sources/cloud-native/ostree/tests/test-delta-sign.sh

Purpose: tests static delta signing through the dummy signature module and signature verification enforcement during offline apply.

Important APIs/functions: environment `OSTREE_DUMMY_SIGN_ENABLED=1`, `static-delta generate`, `--inline`, `--sign-type=dummy`, `--sign`, `static-delta verify`, `static-delta apply-offline`, and `core.sign-verify-deltas`.

Control flow: creates old/new commits from permuted binaries, confirms unsigned deltas fail verification, generates signed non-inline and inline deltas that verify, checks bad keys fail, applies offline without verification, then enforces verification to require keys and tests good/bad dummy keys.

State/persistence: writes archive repo deltas and repeated `repo2` bare-user apply targets. Dependencies include user xattrs and dummy signing feature flag.

Integration/risk/test signals: protects generic delta signature plumbing independent of real crypto. Risks are dummy module availability and exact error messages. Seven TAP cases cover verification and offline apply modes.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-delta-sign.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-delta.sh -->
# sources/cloud-native/ostree/tests/test-delta.sh

Purpose: broad static delta CLI integration test covering generation, listing, indexes, bsdiff options, endian handling, pulling, offline apply, deletion, empty deltas, summaries, rebases, and error handling.

Important APIs/functions: `static-delta generate/list/reindex/indexes/show/delete/apply-offline`, `pull-local --require-static-deltas`, `--disable-static-deltas`, `--commit-metadata-only`, `summary -u`, `core.no-deltas-in-summary`, and helper delta directory lookup.

Control flow: creates binary commits, generates empty and from-to deltas, checks idempotent generation, tests inline vs detached parts and bsdiff knobs, validates show output and endian heuristics using fixtures, pulls via deltas including commitpartial, applies offline, deletes deltas, handles empty delta parts, toggles summary index publication, tests rebase deltas, and rejects bad delta names.

State/persistence: heavily mutates `repo/deltas`, summaries, temp repos, fixture repos, and content refs. Dependencies include user xattrs and pre-endian tar fixtures.

Integration/risk/test signals: protects the static delta subsystem end to end. Risks are output regex brittleness, fixture size assumptions, and compression variability. Fourteen TAP cases provide milestone signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-delta.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-demo-buildsystem.sh -->
# sources/cloud-native/ostree/tests/test-demo-buildsystem.sh

Purpose: demonstrates and tests an OSTree-based package compose workflow using package commits, union checkouts, triggers, publish, deltas, and summaries.

Important APIs/functions: `skip_without_fuse`, `skip_without_user_xattrs`, functions `demo_triggers()`, `exampleos_build_commit_package()`, and `exampleos_recompose()`, plus `rofiles-fuse`, `fusermount -u`, `commit --link-checkout-speedup`, `pull-local`, `static-delta generate`, and `summary -u`.

Control flow: initializes a bare-user build repo and archive publish repo, builds fake `bash` and `systemd` package refs, recomposes by union checkout and trigger execution through a rofiles-fuse mount, publishes the standard ref, updates one package, recomposes, republishes, generates a delta, and updates the summary.

State/persistence: writes build-package directories, `exampleos-build`, FUSE mount `mnt`, build and publish repos, deltas, and summaries. Dependencies include FUSE and user xattrs.

Integration/risk/test signals: validates a realistic build-system pattern and link-checkout optimization. Risks are FUSE availability and date-varying trigger output. One TAP case reports the demo workflow.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-demo-buildsystem.sh -->
