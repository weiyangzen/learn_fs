# subset-b-009266 research

This grouped report covers kdevops workflow configuration, orchestration scripts, result analysis helpers, and static Linux tree reference data. Each section is source-tree-aligned and intended to be split into the corresponding `Docs/researches/<source>_research.md` artifact.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/btrfs/Kconfig -->
## sources/test-tools/kdevops/workflows/fstests/btrfs/Kconfig

Purpose: Defines the btrfs fstests coverage matrix. It lets distributions choose manual coverage, opt out of RAID56, and select combinations of compression, holes/no-holes, free-space-tree, no-holes plus free-space-tree, simple profile, and ZNS simple-profile sections.

Important APIs/types/functions: This is Kconfig data, so its public surface is config symbols such as `FSTESTS_BTRFS_MANUAL_COVERAGE`, `FSTESTS_BTRFS_ENABLES_COMPRESSION_*`, `FSTESTS_BTRFS_ENABLES_*`, and `FSTESTS_BTRFS_SECTION_*`. Distro capability symbols such as `HAVE_DISTRO_BTRFS_PREFERS_MANUAL` and `HAVE_DISTRO_BTRFS_DISABLES_RAID56` influence defaults.

Control flow: The file branches first on manual coverage. In manual mode, user-visible symbols expose all feature families and section selectors. In non-manual mode, hidden symbols set a default upstream-oriented matrix: compression enabled with zstd, free-space-tree and no-holes/free-space-tree enabled, holes/no-holes legacy sections mostly off, and simple/ZNS sections on.

State and persistence: Kconfig selections persist in `.config` and later become `CONFIG_FSTESTS_BTRFS_*` variables consumed by the fstests Makefile and Ansible extra-vars. No runtime state is written by this file.

Dependencies and integration points: Integrated through the parent `workflows/fstests/Kconfig` when `FSTESTS_BTRFS` is selected. Section names must match fstests config sections and the btrfs Makefile argument names.

Risks and test signals: Risk centers on drift between Kconfig defaults, generated host sections, and btrfs feature support in kernels/progs. Test signals include generated `.config` defaults, `extra_vars.yaml` values produced by Makefiles, and successful provisioning of btrfs sections that match selected symbols.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/btrfs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/btrfs/Makefile -->
## sources/test-tools/kdevops/workflows/fstests/btrfs/Makefile

Purpose: Translates btrfs fstests Kconfig selections into `FSTESTS_ARGS` variables passed into the kdevops Ansible workflow.

Important APIs/types/functions: The API is Make variables appended to `FSTESTS_ARGS`, such as `fstests_btrfs_enables_raid56=True`, `fstests_btrfs_enables_compression_zstd=True`, and `fstests_btrfs_section_nohofspace_zstd=True`.

Control flow: Nested `ifeq (y,$(CONFIG_*))` blocks mirror the Kconfig feature hierarchy. Feature-level enablement gates section-level args so only coherent btrfs coverage combinations are exported.

State and persistence: It does not persist state directly. It derives args from the checked-in or generated `.config` and contributes to `WORKFLOW_ARGS` through the parent fstests Makefile.

Dependencies and integration points: Included by `workflows/fstests/Makefile` when `CONFIG_FSTESTS_BTRFS=y`. Downstream Ansible roles must understand every emitted `fstests_btrfs_*` variable.

Risks and test signals: Typos in variable names silently break provisioning because Make succeeds while Ansible sees missing vars. Compare `make print-vars`/generated `extra_vars.yaml` with expected btrfs section inventory and run a dry provisioning target to verify.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/btrfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/cifs/Kconfig -->
## sources/test-tools/kdevops/workflows/fstests/cifs/Kconfig

Purpose: Configures SMB/CIFS fstests execution, including whether to use a kdevops-provisioned SMB server and which SMB3 security variants to test.

Important APIs/types/functions: Public symbols include `FSTESTS_USE_KDEVOPS_SMBD`, `FSTESTS_SMB_SERVER_HOST`, `HAVE_DISTRO_CIFS_PREFERS_MANUAL`, `FSTESTS_CIFS_MANUAL_COVERAGE`, and section selectors `FSTESTS_CIFS_SECTION_SMB3`, `_SMB3_SEAL`, and `_SMB3_SIGN`.

Control flow: The file first selects server mode. Manual coverage exposes user-facing section choices. Non-manual mode hides selectors and defaults to SMB3 only, leaving encryption and signing variants off.

State and persistence: Selections are stored in `.config`; server host values and section booleans are later emitted as Make/Ansible arguments.

Dependencies and integration points: Selecting the kdevops server pulls in `KDEVOPS_SETUP_SMBD`. The parent fstests workflow sources this file only for CIFS runs, and the Makefile maps selected sections to `fstests_cifs_*` args.

Risks and test signals: External server mode has weak validation and depends on a pre-created hierarchy. Test signals are generated inventory for `smbd`, rendered `fstests_smb_server_host`, and successful mount/run of smb3, seal, or signing sections.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/cifs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/cifs/Makefile -->
## sources/test-tools/kdevops/workflows/fstests/cifs/Makefile

Purpose: Emits CIFS-specific fstests workflow arguments from Kconfig.

Important APIs/types/functions: Adds `fstests_cifs_enable`, `fstests_cifs_use_kdevops_smbd`, `fstests_smb_server_host`, and `fstests_cifs_section_*` values to `FSTESTS_ARGS`.

Control flow: It starts with CIFS enabled, chooses the server host from either `CONFIG_FSTESTS_SMB_SERVER_HOST` or the kdevops host prefix plus `-smbd`, then appends section args for SMB3, encrypted SMB3, and signed SMB3.

State and persistence: No file state is written. The persistent source is `.config`; the output path is Make variables that feed Ansible extra vars.

Dependencies and integration points: Included by the parent fstests Makefile when CIFS is selected. It depends on `CONFIG_KDEVOPS_HOSTS_PREFIX` for kdevops-managed server naming.

Risks and test signals: A mismatch between server host naming and inventory breaks all CIFS sections. Verify by inspecting `extra_vars.yaml` and running a CIFS dry run or mount smoke test.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/cifs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/ext4/Kconfig -->
## sources/test-tools/kdevops/workflows/fstests/ext4/Kconfig

Purpose: Defines ext4 fstests section coverage, including default ext4 profiles, small block sizes, bigalloc cluster sizes, and advanced feature testing.

Important APIs/types/functions: Main symbols are `HAVE_DISTRO_EXT4_PREFERS_MANUAL`, `FSTESTS_EXT4_MANUAL_COVERAGE`, and `FSTESTS_EXT4_SECTION_*` selectors for defaults, 1K/2K/4K blocks, bigalloc cluster sizes, and advanced features.

Control flow: Manual mode exposes all section choices. Non-manual mode enables only the default and advanced feature sections by default, avoiding the larger manual block-size/bigalloc matrix.

State and persistence: Kconfig selections persist to `.config` and are used by the fstests host-generation logic. The file writes no runtime state.

Dependencies and integration points: Sourced by the parent fstests Kconfig when `FSTESTS_EXT4` is active. Section names must align with fstests config templates and oscheck section parsing.

Risks and test signals: Several help strings mention "1k block size" for multiple sections, which could confuse users even though symbol names differ. Test by verifying generated ext4 sections and mkfs options in host configs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/ext4/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/nfs/Kconfig -->
## sources/test-tools/kdevops/workflows/fstests/nfs/Kconfig

Purpose: Configures NFS fstests, including use of a kdevops knfsd server, manual coverage across NFS protocol/transport features, and Kerberos auth flavor selection.

Important APIs/types/functions: Symbols include `FSTESTS_USE_KDEVOPS_NFSD`, `FSTESTS_NFS_SERVER_HOST`, `FSTESTS_NFS_MANUAL_COVERAGE`, section selectors for pNFS, RDMA, TLS, nfsd, v4.2/v4.1/v4.0/v3, and `FSTESTS_NFS_AUTH_FLAVOR`.

Control flow: Server mode is selected first. Manual coverage exposes detailed sections; automatic mode enables a default section and leaves v3 off. A separate auth choice is shown only when Kerberos setup is enabled.

State and persistence: Kconfig choices persist in `.config`; auth flavor and selected sections are later rendered into `FSTESTS_ARGS`.

Dependencies and integration points: `FSTESTS_USE_KDEVOPS_NFSD` selects `KDEVOPS_SETUP_NFSD`; TLS depends on `KDEVOPS_SETUP_KTLS`; auth choice depends on `KDEVOPS_SETUP_KRB5`. The Makefile passes these into Ansible roles.

Risks and test signals: Network feature sections depend on external infrastructure such as RDMA, kTLS, Kerberos, and knfsd exports. Test signals include inventory with an `nfsd` host, rendered `fstests_nfs_auth_flavor`, and successful NFS mounts for each selected section.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/nfs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/nfs/Makefile -->
## sources/test-tools/kdevops/workflows/fstests/nfs/Makefile

Purpose: Builds NFS-specific fstests Ansible variables from Kconfig.

Important APIs/types/functions: Emits `fstests_nfs_enable`, `fstests_nfs_use_kdevops_nfsd`, `fstests_nfs_server_host`, per-section `fstests_nfs_section_*`, and optional `fstests_nfs_auth_flavor`.

Control flow: The host is either an explicit configured server or the kdevops prefix plus `-nfsd`. Each selected protocol/feature section appends a boolean arg.

State and persistence: No direct state; it maps `.config` symbols to Make variables used by the parent workflow.

Dependencies and integration points: Included by the fstests Makefile for NFS. Integrates with NFS server provisioning, Kerberos/TLS roles, and fstests config generation.

Risks and test signals: Missing export information in external-server mode can pass Make but fail at mount time. Verify with generated extra-vars and a target-side mount smoke test.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/nfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/osfiles/debian/helpers.sh -->
## sources/test-tools/kdevops/workflows/fstests/osfiles/debian/helpers.sh

Purpose: Provides Debian-specific hooks for oscheck: OS identification, known expunge lists, skip groups, ypbind restart, and distro-kernel detection.

Important APIs/types/functions: Implements `debian_read_osfile`, `debian_special_expunges`, `debian_skip_groups`, `debian_restart_ypbind`, and `debian_distro_kernel_check`, which are discovered dynamically by `oscheck-lib.sh`.

Control flow: Release-specific cases add xfsprogs or ext4 expunge files. XFS always skips the `encrypt` group. Kernel detection checks `/boot/config-$(uname -r)` for Debian trusted keys.

State and persistence: It mutates shell variables such as `VERSION_ID`, `SKIP_GROUPS`, and `_SKIP_GROUPS`, and appends expunge flags through oscheck library helpers. It writes no files itself.

Dependencies and integration points: Requires `lsb_release`, `/etc/os-release` or equivalent release data, `/boot/config-*`, and oscheck functions such as `oscheck_add_expunge_if_exists`.

Risks and test signals: Debian testing release handling is string-based and can drift. Test by sourcing through `oscheck-get-failures.sh --test-section ...` and confirming expected expunge files and distro-kernel classification.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/osfiles/debian/helpers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/osfiles/fedora/helpers.sh -->
## sources/test-tools/kdevops/workflows/fstests/osfiles/fedora/helpers.sh

Purpose: Supplies Fedora-specific oscheck behavior for release parsing, expunges, XFS skip groups, ypbind restart, and distro-kernel detection.

Important APIs/types/functions: Implements `fedora_read_osfile`, `fedora_special_expunges`, `fedora_skip_groups`, `fedora_restart_ypbind`, and `fedora_distro_kernel_check`.

Control flow: Reads `VERSION_ID` and `PRETTY_NAME` from os-release. Fedora 28 gets broad XFS skip groups and older xfsprogs/y2038 expunges; Fedora 34 gets xfsprogs-maintainer and ext4 xfstests-bld expunges.

State and persistence: Mutates shell state for `VERSION_ID`, `_SKIP_GROUPS`, and expunge flags; no direct persistence.

Dependencies and integration points: Loaded by `oscheck_include_os_files` when `OSCHECK_ID=fedora`. Uses `file /boot/vmlinuz-$(uname -r)` to detect Fedora kernels.

Risks and test signals: Kernel detection depends on the `file` output containing `fedoraproject.org`. Validate on Fedora images by running `oscheck.sh --is-distro` and checking generated skip args.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/osfiles/fedora/helpers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/osfiles/ol/helpers.sh -->
## sources/test-tools/kdevops/workflows/fstests/osfiles/ol/helpers.sh

Purpose: Provides Oracle Linux oscheck hooks for release display, XFS skip groups, and distro-kernel detection.

Important APIs/types/functions: Implements `ol_read_osfile`, `ol_skip_groups`, and `ol_distro_kernel_check`.

Control flow: Reads release metadata from `/etc/os-release`, always skips XFS `encrypt`, and identifies distro kernels by asking rpm which package owns `/boot/config-$(uname -r)`.

State and persistence: Only shell variables are mutated (`VERSION_ID`, `PRETTY_NAME`, `SKIP_GROUPS`, `_SKIP_GROUPS`). No files are written.

Dependencies and integration points: Loaded dynamically by oscheck when `ID=ol`. Requires rpm database availability for kernel classification.

Risks and test signals: Minimal release-specific expunge coverage can under-triage known failures. Test with `oscheck-get-failures.sh` on OL images and compare with expected distro expunge policy.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/osfiles/ol/helpers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/osfiles/opensuse-leap/helpers.sh -->
## sources/test-tools/kdevops/workflows/fstests/osfiles/opensuse-leap/helpers.sh

Purpose: Implements openSUSE Leap-specific oscheck hooks for release metadata, known expunges, skip groups, ypbind restart, and distro-kernel detection.

Important APIs/types/functions: Exposes dynamically named functions `opensuse-leap_read_osfile`, `opensuse-leap_special_expunges`, `opensuse-leap_skip_groups`, `opensuse-leap_restart_ypbind`, and `opensuse-leap_distro_kernel_check`.

Control flow: `VERSION_ID` cases 15.0 through 15.4 add xfs/ext4 expunges. Older 15.0 skips several XFS risk groups; all XFS runs skip `encrypt`. Kernel detection greps `/boot/config-*` for `CONFIG_SUSE_KERNEL=y`.

State and persistence: Mutates oscheck shell variables and expunge flags. No persistent files are produced.

Dependencies and integration points: Loaded by `oscheck-lib.sh` based on os-release ID. Requires shell support for hyphenated function names as defined in bash; callers use `${OSCHECK_ID}_...` dispatch.

Risks and test signals: Hyphenated function names are bash-specific and would not work under plain POSIX sh. Test by sourcing under bash via `oscheck.sh`, verifying selected expunge files for each Leap release.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/osfiles/opensuse-leap/helpers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/osfiles/opensuse-tumbleweed/helpers.sh -->
## sources/test-tools/kdevops/workflows/fstests/osfiles/opensuse-tumbleweed/helpers.sh

Purpose: Provides openSUSE Tumbleweed oscheck hooks for rolling release expunges, skip groups, ypbind restart, and distro-kernel detection.

Important APIs/types/functions: Implements `opensuse-tumbleweed_read_osfile`, `_special_expunges`, `_skip_groups`, `_restart_ypbind`, and `_distro_kernel_check` variants.

Control flow: Groups release IDs by year patterns. 2019 releases get broader XFS expunges and skip groups; 2020/2021 add xfsprogs-maintainer and ext4 xfstests-bld expunges. Distro kernel detection uses `CONFIG_SUSE_KERNEL=y`.

State and persistence: Updates shell variables and expunge flag lists; no persistent writes.

Dependencies and integration points: Integrated through dynamic oscheck dispatch. Uses os-release, `/boot/config-*`, and the common `oscheck_systemctl_restart_ypbind` helper.

Risks and test signals: Date-pattern release matching can become stale for newer Tumbleweed snapshots. Test by running with a current Tumbleweed `VERSION_ID` and checking whether intended expunges still apply.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/osfiles/opensuse-tumbleweed/helpers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/osfiles/sles/helpers.sh -->
## sources/test-tools/kdevops/workflows/fstests/osfiles/sles/helpers.sh

Purpose: Adds SLES-specific oscheck policy for known fstests failures, skip groups, ypbind restart, and distro-kernel verification.

Important APIs/types/functions: Implements `sles_read_osfile`, `sles_special_expunges`, `sles_skip_groups`, `sles_restart_ypbind`, and `sles_distro_kernel_check`.

Control flow: Release cases for 15.2 through 15.4 add XFS and ext4 expunges. SLES 15.2 also skips older-risk XFS groups, and all XFS runs skip `encrypt`.

State and persistence: Mutates `_SKIP_GROUPS`, `SKIP_GROUPS`, `VERSION_ID`, and expunge flags. It does not write files.

Dependencies and integration points: Loaded by oscheck via `OSCHECK_ID=sles`; uses `/boot/config-$(uname -r)` and `CONFIG_SUSE_KERNEL=y`.

Risks and test signals: `sles_restart_ypbind` only handles 15.0 while expunge cases target later releases; ypbind recovery may fail silently on current images. Test with `oscheck.sh --check-deps` and NIS-active systems.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/osfiles/sles/helpers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/osfiles/ubuntu/helpers.sh -->
## sources/test-tools/kdevops/workflows/fstests/osfiles/ubuntu/helpers.sh

Purpose: Provides Ubuntu oscheck hooks, including optional installation of missing fstests dependencies for Ubuntu 18.04, known expunges, skip groups, ypbind restart, and distro-kernel detection.

Important APIs/types/functions: Functions include `install_basic_reqs`, `ubuntu_install_*`, `ubuntu_read_osfile`, `ubuntu_special_expunges`, `ubuntu_skip_groups`, `ubuntu_restart_ypbind`, and `ubuntu_distro_kernel_check`.

Control flow: Install helpers funnel most required tools through `install_basic_reqs`; fio, dbench, setcap, and setfattr have focused package installs. Release 18.04 receives older XFS expunges and broad XFS skip groups.

State and persistence: May persist package changes through `apt-get install` when oscheck requests missing requirement remediation. Also mutates expunge and skip variables.

Dependencies and integration points: Loaded dynamically by oscheck. Depends on `apt-get`, `lsb_release`, `dpkg -S`, and common oscheck helper functions.

Risks and test signals: Package installation is narrowly coded for 18.04, so newer Ubuntu releases may only emit a suggestion. Test with `FSTESTS_SETUP_SYSTEM=y oscheck.sh --check-deps` and verify dependency remediation behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/osfiles/ubuntu/helpers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/scripts/gendisks.sh -->
## sources/test-tools/kdevops/workflows/fstests/scripts/gendisks.sh

Purpose: Creates sparse-file-backed loop devices for fstests scratch/test devices and optionally formats the configured test device.

Important APIs/types/functions: Functions are `known_hosts`, `parse_config_section`, `setup_loop`, `delete_loops`, `gendisk_usage`, and `parse_args`. Inputs are environment/config variables such as `HOST_OPTIONS`, `FSTESTS_SPARSE_FILE_PATH`, `FSTESTS_SPARSE_FILE_SIZE`, `FSTESTS_SPARSE_FILENAME_PREFIX`, `TEST_DEV`, `FSTYP`, and `MKFS_OPTIONS`.

Control flow: The script infers the host section from hostname, parses default and inferred config sections, processes `-d` and `-m`, ensures the sparse directory exists, exits unless sparse generation is enabled, then creates loop devices `/dev/loop5` through `/dev/loop16` backed by truncated files. With `-m`, it runs `mkfs.$FSTYP` against `TEST_DEV`, including optional log/rt device mkfs args.

State and persistence: Persists sparse backing files, loop device attachments, and optionally filesystem signatures on `TEST_DEV`. `-d` detaches all loop devices from `losetup -a` and removes matching sparse files.

Dependencies and integration points: Relies on fstests host config syntax, `losetup`, `truncate`, `mknod`, optional `lsblk`, and mkfs tools. Supports sections generated by kdevops fstests config.

Risks and test signals: `delete_loops` detaches every loop device on the system, not only those created here. Test in isolated guests, verify `losetup -a`, and check that generated loop sector size matches backing storage expectations.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/scripts/gendisks.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/scripts/ld-version.sh -->
## sources/test-tools/kdevops/workflows/fstests/scripts/ld-version.sh

Purpose: Converts a linker/tool version string from stdin into a comparable integer version code.

Important APIs/types/functions: This AWK script strips prefixes/suffixes, splits the first remaining token on `.`, and prints `major*100000000 + minor*1000000 + patch*10000`.

Control flow: It processes the first input record only, normalizes strings that include `version ` or parenthesized prefixes, emits one numeric value, and exits.

State and persistence: Stateless; no files are read or written beyond stdin/stdout.

Dependencies and integration points: Used by `oscheck.sh` to compare filesystem tool versions such as xfsprogs, btrfs-progs, e2fsprogs, and reiserfs tools.

Risks and test signals: Missing patch components become zero/empty AWK arithmetic, which is usually acceptable but should be tested for two-component versions. Test with version samples like `4.15.1`, `mke2fs 1.47.0`, and vendor-suffixed strings.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/scripts/ld-version.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/scripts/naggy-check.sh -->
## sources/test-tools/kdevops/workflows/fstests/scripts/naggy-check.sh

Purpose: Repeatedly runs fstests `./check` for one or more tests until a count is reached or, optionally, a failure occurs.

Important APIs/types/functions: Functions include `known_hosts_local`, `get_config_sections`, `parse_config_section_local`, `sig_exit`, and `parse_args`. CLI options include `--section`, `--count`, and `--fail-triggers-exit`.

Control flow: The script resolves host options, infers a section from the hostname, parses default and selected config sections, then loops over `./check -s $SECTION $TESTS`. It reports PASS/FAIL per iteration and per test by inspecting `.out.bad` and `.dmesg` result files.

State and persistence: It writes normal fstests result artifacts through `./check`; it does not manage cleanup. It reads config from `/var/lib/xfstests/configs` or local options.

Dependencies and integration points: Requires an fstests tree, `./check`, result layout under `results/$(hostname)/$(uname -r)/$SECTION`, and host config syntax compatible with xfstests/kdevops.

Risks and test signals: The loop can run indefinitely by default. Test with `--count 1` and a known passing/failing test, and verify per-test failure detection against generated result files.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/scripts/naggy-check.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/scripts/oscheck-get-failures.sh -->
## sources/test-tools/kdevops/workflows/fstests/scripts/oscheck-get-failures.sh

Purpose: Prints the unique list of known failure test IDs for the current OS, filesystem, and section by reusing oscheck expunge resolution.

Important APIs/types/functions: Uses `oscheck-lib.sh` functions: `oscheck_lib_init_vars`, `oscheck_lib_set_run_section`, `oscheck_lib_get_host_options_vars`, `oscheck_lib_read_osfiles_verify_kernel`, `oscheck_lib_validate_section`, `oscheck_lib_set_expunges`, and `oscheck_lib_mktemp`.

Control flow: Parses `--test-section`, initializes oscheck with non-failure expunges skipped and quiet distro checks, resolves section and expunge files, concatenates the first field from every expunge file, sorts, uniques, and prints non-empty IDs.

State and persistence: Creates a temporary file through `oscheck_lib_mktemp` and removes it. It otherwise reads configs and expunge files only.

Dependencies and integration points: Requires `FSTYP`, host config, os-release data, expunge file tree, and oscheck library. Intended for automation that needs the known-failure list rather than running tests.

Risks and test signals: It intentionally skips non-failure expunges, so output differs from the full `oscheck.sh` exclude set. Test by comparing with `oscheck.sh -n --expunge-list` and confirming only known failures appear.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/scripts/oscheck-get-failures.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/scripts/oscheck-lib.sh -->
## sources/test-tools/kdevops/workflows/fstests/scripts/oscheck-lib.sh

Purpose: Shared library for fstests OS-aware test preparation, section parsing, distro detection, expunge-file discovery, and validation.

Important APIs/types/functions: Major functions include `oscheck_lib_init_vars`, `known_hosts`, `oscheck_lib_set_run_section`, `oscheck_lib_parse_config_section`, `oscheck_include_os_files`, `oscheck_add_expunge_if_exists`, `oscheck_handle_section_expunges`, `oscheck_read_osfile_and_includes`, `oscheck_distro_kernel_check`, `oscheck_lib_validate_section`, and `oscheck_lib_set_expunges`.

Control flow: Initialization validates `FSTYP`, sets default paths, release variables, kernel version, and expunge controls. Runtime helpers infer the test section, parse host config sections with `sed`/`eval`, load OS-specific helpers based on os-release ID, run distro-kernel checks, assemble expunge candidates by category/priority/section, add quick-test and large-disk excludes, and validate that intended section expunges were queued.

State and persistence: Maintains state through exported shell variables such as `OSCHECK_ID`, `VERSION_ID`, `RUN_SECTION`, `EXPUNGE_FLAGS`, `EXPUNGE_FILES`, `OSCHECK_EXCLUDE_DIR`, and `KERNEL_VERSION`. It writes only temporary files when callers request `oscheck_lib_mktemp`.

Dependencies and integration points: Sourced by `oscheck.sh` and `oscheck-get-failures.sh`. Depends on host config files, `/etc/os-release`, distro helper files under `osfiles`, expunge file layout, `lsb_release`, and `/boot` kernel metadata for distro-specific checks.

Risks and test signals: Section parsing uses `eval` on config content, so config files must be trusted. A likely bug in `oscheck_lib_set_run_section` assigns `RUN_SECTION="${FSTYP}_${s}"` even though `s` is not defined; this affects short section names without filesystem prefixes. Test with full and short section names, `--expunge-list`, distro-kernel checks, and missing-expunge verification.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/scripts/oscheck-lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/scripts/oscheck.sh -->
## sources/test-tools/kdevops/workflows/fstests/scripts/oscheck.sh

Purpose: OS wrapper around fstests `check.sh` that validates dependencies, devices, distro policy, expunges, and then runs `./check` with the correct section and exclusions.

Important APIs/types/functions: Key functions are `parse_args`, `oscheck_get_progs_version`, `check_services`, `check_reqs`, `check_mount`, `oscheck_run_section`, `_check_dev_setup`, `oscheck_test_dev_setup`, `check_kernel_config`, `check_test_dev_setup`, and `check_dev_pool`.

Control flow: The script requires root, parses wrapper and passthrough args, resolves the run section and host config, unmounts an already-mounted test dir, loads OS helper policy, applies skip groups, checks users/groups/directories/tools/services, validates the fstests tree and kernel config, validates devices/pools, optionally exits after dependency checks, gathers tool versions, formats/mount-checks devices, computes expunges, and finally runs `LC_ALL=C bash ./check ...`.

State and persistence: It may create users/groups/directories when `FSTESTS_SETUP_SYSTEM=y`, format block devices, mount/unmount test devices, write `/tmp/run-cmd.txt`, and optionally emit journal output through `systemd-cat`. It inherits and exports substantial shell state from oscheck-lib.

Dependencies and integration points: Requires fstests tree, root privileges, mkfs tools, user/group management tools, systemd/ypbind when relevant, host config files, expunge files, and the oscheck library. Kdevops uses it inside fstests workflows to normalize per-distro execution.

Risks and test signals: It can alter system users/groups and filesystems, so dry-run and dependency-only modes are important. Test signals include `--check-deps`, `-n --show-cmd`, `--expunge-list`, root/non-root behavior, and a smoke run against a disposable test device.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/scripts/oscheck.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/tmpfs/Kconfig -->
## sources/test-tools/kdevops/workflows/fstests/tmpfs/Kconfig

Purpose: Defines tmpfs fstests coverage sections for default mounts, noswap mode, and huge-page mount policies.

Important APIs/types/functions: Symbols include `FSTESTS_TMPFS_MANUAL_COVERAGE`, `FSTESTS_TMPFS_SECTION_DEFAULT`, `FSTESTS_TMPFS_ENABLE_NOSWAP`, `FSTESTS_TMPFS_SECTION_NOSWAP_HUGE_*`, `FSTESTS_TMPFS_ENABLE_HUGE`, and `FSTESTS_TMPFS_SECTION_HUGE_*`.

Control flow: Manual mode exposes default, noswap, and huge-page section selections. Non-manual mode defaults only the default section and leaves other hidden selectors unset.

State and persistence: Selections persist in `.config` and are converted to Make/Ansible args by the tmpfs Makefile.

Dependencies and integration points: Sourced by parent fstests Kconfig for tmpfs. Downstream inventory/host config generation must map selected symbols to tmpfs mount options such as huge modes and swap behavior.

Risks and test signals: Huge-page behavior depends on kernel and system THP settings, not only mount options. Verify generated tmpfs section configs and target runtime mount options.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/tmpfs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/tmpfs/Makefile -->
## sources/test-tools/kdevops/workflows/fstests/tmpfs/Makefile

Purpose: Emits tmpfs fstests Ansible arguments from tmpfs Kconfig selections.

Important APIs/types/functions: Adds `fstests_tmpfs_enable`, `fstests_tmpfs_section_default`, `fstests_tmpfs_enable_noswap`, `fstests_tmpfs_section_noswap_huge_*`, `fstests_tmpfs_enable_huge`, and `fstests_tmpfs_section_huge_*` to `FSTESTS_ARGS`.

Control flow: Flat conditional checks append args for default, noswap, noswap huge policies, and huge policies. Comments note this Makefile could shrink if Kconfig gains direct extra-vars YAML output.

State and persistence: No state beyond derived Make variables.

Dependencies and integration points: Included by parent fstests Makefile. The Ansible side must interpret these booleans into tmpfs config sections/mount options.

Risks and test signals: Because all args are optional booleans, missing a true arg changes coverage silently. Inspect generated extra vars and host config sections for each selected tmpfs mode.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/tmpfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/xfs/Kconfig -->
## sources/test-tools/kdevops/workflows/fstests/xfs/Kconfig

Purpose: Defines a large XFS fstests coverage model, including xfsprogs/xfsdump build options, quota mount options, CRC/no-CRC, reflink/rmapbt, external log, realtime device, large block size, stripe, nrext64, and bigblock configurations.

Important APIs/types/functions: Distro capability symbols include `HAVE_DISTRO_XFS_SUPPORTS_*` and `HAVE_DISTRO_XFS_IGNORES_NOCRC`. User/config symbols include `FSTESTS_XFS_BUILD_CUSTOM_XFSPROGS`, `FSTESTS_XFS_XFSPROGS_*`, `FSTESTS_XFS_BUILD_XFSDUMP`, `FSTESTS_XFS_QUOTA_ENABLED`, `FSTESTS_XFS_SECTION_*`, and `FSTESTS_XFS_ENABLE_LBS*`.

Control flow: After tool-build and quota options, manual coverage exposes detailed section switches. Nested gates constrain logdev, rtdev, no-CRC, LBS-real, LBS-on-4K-sector, and reflink sections. Non-manual mode supplies a smaller hidden default matrix with CRC, no-CRC, 512-byte no-CRC, reflink, 1K reflink, normapbt, logdev enabled, and bigblock if supported.

State and persistence: Kconfig persists selections into `.config`; Make/Ansible later use them to create hosts and fstests config sections. No direct file writes.

Dependencies and integration points: Sourced by the parent fstests Kconfig when XFS is selected. It depends on architecture/storage capability symbols such as `HAVE_ARCH_64K_PAGES` and `EXTRA_STORAGE_SUPPORTS_*`; tool build options integrate with xfsprogs/xfsdump repositories and mirrors.

Risks and test signals: The matrix is large and easy to desynchronize from actual generated config templates or storage availability. Test by enumerating generated XFS sections, validating mkfs options, and running `oscheck.sh --check-deps` plus dry-run `./check` commands per selected section.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/xfs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/gitr/Kconfig -->
## sources/test-tools/kdevops/workflows/gitr/Kconfig

Purpose: Configures the Git regression test workflow and the filesystem under test.

Important APIs/types/functions: Symbols include filesystem choice `GITR_XFS/BTRFS/EXT4/NFS/TMPFS`, `GITR_MNT`, repository selectors `HAVE_MIRROR_GIT`, `GITR_REPO_CUSTOM`, `GITR_REPO_URL`, `GITR_REPO`, `GITR_REPO_COMMIT`, test selectors `GITR_ALL_TESTS`, `GITR_TEST_LIST`, and thread mode symbols.

Control flow: The file selects one filesystem, sources its sub-Kconfig, sets mount path and repository source/ref, and in dedicated workflow mode exposes all-vs-specific tests plus single/fast/stress/custom thread modes.

State and persistence: Kconfig state persists in `.config` and becomes gitr extra vars through Makefile translation.

Dependencies and integration points: Integrates with filesystem-specific subdirectories, libvirt mirror detection, default Git URL constants, and host group generation for dedicated workflows.

Risks and test signals: Default `GITR_REPO_COMMIT` is pinned, so test age must be intentional. Validate selected filesystem args, repository URL/ref, and generated test group lists before running `make gitr-baseline`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/gitr/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/gitr/Makefile -->
## sources/test-tools/kdevops/workflows/gitr/Makefile

Purpose: Converts gitr Kconfig into Ansible vars and defines Make targets to setup, run, reset, and display Git regression test results.

Important APIs/types/functions: Emits `GITR_ARGS` into `WORKFLOW_ARGS_DIRECT`, maintains `GITR_ENABLED_TEST_GROUPS`, and defines targets `gitr`, `gitr-baseline`, `gitr-dev-baseline`, `gitr-dev-reset`, `gitr-show-results`, and `gitr-help-menu`.

Control flow: Includes one filesystem-specific Makefile, adds repo/ref and thread/test arguments, chooses play tags based on all-vs-specific tests, computes result path from `last-kernel.txt`, and invokes `ansible-playbook` against baseline/dev host groups.

State and persistence: Reads `workflows/gitr/results/last-kernel.txt` and result summaries. Writes are performed by the Ansible playbook, not Make directly.

Dependencies and integration points: Depends on `KDEVOPS_PLAYBOOKS_DIR`, `extra_vars.yaml`, inventory groups, filesystem sub-Makefiles, and result layout.

Risks and test signals: `WORKFLOW_ARGS_DIRECT` vs separated args affect how values with spaces are passed. Test by inspecting generated Ansible command lines and running `gitr-show-results` after a known test run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/gitr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/gitr/btrfs/Kconfig -->
## sources/test-tools/kdevops/workflows/gitr/btrfs/Kconfig

Purpose: Supplies btrfs device, label, and mount-option settings for running Git regression tests on btrfs.

Important APIs/types/functions: Symbols are `GITR_BTRFS_DEVICE`, `GITR_BTRFS_LABEL`, and `GITR_BTRFS_MOUNT_OPTS`.

Control flow: Device defaults vary by backend and storage driver: libvirt NVMe/virtio/IDE, AWS m5ad, GCE, and Azure get different device paths. Label and mount options have simple defaults.

State and persistence: Values persist in `.config` and become gitr Ansible vars.

Dependencies and integration points: Used when `GITR_BTRFS` is selected. Integrates with kdevops storage provisioning and the btrfs gitr Makefile.

Risks and test signals: Device path defaults can drift with provider images. Verify the configured device exists before mkfs/mount and inspect `gitr_device` in extra vars.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/gitr/btrfs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/gitr/btrfs/Makefile -->
## sources/test-tools/kdevops/workflows/gitr/btrfs/Makefile

Purpose: Emits gitr btrfs filesystem variables.

Important APIs/types/functions: Adds `gitr_fstype=btrfs`, `gitr_uses_no_devices='False'`, `gitr_device`, `gitr_label`, `gitr_mount_opts`, and appends `btrfs` to `GITR_ENABLED_TEST_GROUPS`.

Control flow: Straight-line Make variable appends from Kconfig.

State and persistence: No direct state; it derives from `.config`.

Dependencies and integration points: Included by gitr Makefile when btrfs is selected. Consumed by the gitr Ansible playbook for formatting and mounting.

Risks and test signals: Ensure quoting preserves mount options. Validate `extra_vars.yaml` and target mount output.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/gitr/btrfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/gitr/ext4/Kconfig -->
## sources/test-tools/kdevops/workflows/gitr/ext4/Kconfig

Purpose: Defines ext4 block device, filesystem label, and mount options for gitr.

Important APIs/types/functions: Symbols are `GITR_EXT4_DEVICE`, `GITR_EXT4_LABEL`, and `GITR_EXT4_MOUNT_OPTS`.

Control flow: Device defaults are selected by infrastructure backend and storage type. Label defaults to `gitr`; mount options default to `defaults`.

State and persistence: Stored in `.config`, then translated to Ansible args.

Dependencies and integration points: Active only when `GITR_EXT4` is selected. Relies on extra storage provisioning matching the default path.

Risks and test signals: Cloud/local device naming is the main risk. Test by validating the target device and rendered `gitr_fstype=ext4` args.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/gitr/ext4/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/gitr/ext4/Makefile -->
## sources/test-tools/kdevops/workflows/gitr/ext4/Makefile

Purpose: Emits gitr ext4 filesystem variables.

Important APIs/types/functions: Adds `gitr_fstype=ext4`, `gitr_uses_no_devices='False'`, `gitr_device`, `gitr_label`, `gitr_mount_opts`, and enabled group `ext4`.

Control flow: Straight-line mapping from `CONFIG_GITR_EXT4_*` symbols to `GITR_ARGS`.

State and persistence: No direct writes; used to produce Ansible invocation variables.

Dependencies and integration points: Included from the main gitr Makefile when ext4 is selected.

Risks and test signals: Wrong device selection can destroy data on a target. Test only on provisioned disposable disks and verify generated variables before running.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/gitr/ext4/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/gitr/nfs/Kconfig -->
## sources/test-tools/kdevops/workflows/gitr/nfs/Kconfig

Purpose: Configures gitr execution over NFS, including server source, export path, mount options, and dedicated NFS feature sections.

Important APIs/types/functions: Symbols include `GITR_USE_KDEVOPS_NFSD`, `GITR_NFS_SERVER_HOSTNAME`, `GITR_NFS_SERVER_EXPORT`, `GITR_NFS_MOUNT_OPTS`, and section flags for pNFS, RDMA, NFSv4.2/v4.1/v4.0/v3.

Control flow: Server settings are selected first; section selectors are exposed only in dedicated gitr workflow mode.

State and persistence: Kconfig values become `GITR_ARGS` and `GITR_ENABLED_TEST_GROUPS`.

Dependencies and integration points: `GITR_USE_KDEVOPS_NFSD` selects `KDEVOPS_SETUP_NFSD`. The Makefile maps this into NFS server/export vars for the gitr playbook.

Risks and test signals: External NFS server exports are not deeply validated by Kconfig. Test by checking generated mount command and running a simple Git test on the mounted path.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/gitr/nfs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/gitr/nfs/Makefile -->
## sources/test-tools/kdevops/workflows/gitr/nfs/Makefile

Purpose: Emits gitr NFS variables and selected NFS test group labels.

Important APIs/types/functions: Adds `gitr_fstype=nfs`, `gitr_uses_no_devices='True'`, `gitr_nfs_server_host`, `gitr_nfs_server_export`, `gitr_nfs_use_kdevops_nfsd`, `gitr_mount_opts`, and group labels such as `nfs-v42`.

Control flow: Chooses kdevops server host/export or external configured host/export, then appends selected NFS section labels.

State and persistence: No direct state. It feeds Ansible variables and separated test group lists.

Dependencies and integration points: Included by main gitr Makefile for NFS. Integrates with knfsd provisioning and NFS mount roles.

Risks and test signals: NFS mount options are free-form and quoted; bad values fail at runtime. Verify with target mount output and a minimal `git init`/test on the mount.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/gitr/nfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/gitr/tmpfs/Kconfig -->
## sources/test-tools/kdevops/workflows/gitr/tmpfs/Kconfig

Purpose: Defines tmpfs mount options for gitr.

Important APIs/types/functions: Single public symbol `GITR_TMPFS_MOUNT_OPTS`, defaulting to `size=75%`.

Control flow: No branching; the configured string controls tmpfs mount behavior.

State and persistence: Stored in `.config` and emitted to gitr Ansible vars.

Dependencies and integration points: Used when `GITR_TMPFS` is selected and mapped by the tmpfs gitr Makefile.

Risks and test signals: Large Git test runs may exceed the tmpfs size. Test by checking target memory/swap and available space after mount.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/gitr/tmpfs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/gitr/tmpfs/Makefile -->
## sources/test-tools/kdevops/workflows/gitr/tmpfs/Makefile

Purpose: Emits gitr variables for tmpfs-backed testing.

Important APIs/types/functions: Adds `gitr_fstype=tmpfs`, `gitr_uses_no_devices='True'`, `gitr_mount_opts`, and enabled group `tmpfs`.

Control flow: Straight-line mapping from `CONFIG_GITR_TMPFS_MOUNT_OPTS`.

State and persistence: No direct persistence; feeds Ansible vars.

Dependencies and integration points: Included by the main gitr Makefile when tmpfs is selected.

Risks and test signals: Mount option string must be valid for target kernels. Verify by running only setup/mount tags before full Git regression.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/gitr/tmpfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/gitr/xfs/Kconfig -->
## sources/test-tools/kdevops/workflows/gitr/xfs/Kconfig

Purpose: Defines XFS device, label, and mount options for gitr.

Important APIs/types/functions: Symbols are `GITR_XFS_DEVICE`, `GITR_XFS_LABEL`, and `GITR_XFS_MOUNT_OPTS`.

Control flow: Device defaults branch on libvirt storage driver and cloud backend. Label and mount options are simple strings.

State and persistence: Values persist in `.config` and are translated into gitr vars.

Dependencies and integration points: Active when `GITR_XFS` is selected. Depends on provisioned extra storage matching the selected path.

Risks and test signals: Wrong device path can be destructive. Validate inventory storage and generated `gitr_device` before running setup.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/gitr/xfs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/gitr/xfs/Makefile -->
## sources/test-tools/kdevops/workflows/gitr/xfs/Makefile

Purpose: Emits gitr XFS filesystem variables.

Important APIs/types/functions: Adds `gitr_fstype=xfs`, `gitr_uses_no_devices='False'`, `gitr_device`, `gitr_label`, `gitr_mount_opts`, and enabled group `xfs`.

Control flow: Straight-line Make argument emission.

State and persistence: No direct persistence.

Dependencies and integration points: Included by main gitr Makefile when XFS is selected and consumed by the gitr playbook.

Risks and test signals: Mount-option quoting and device correctness are the key checks. Inspect generated vars and target `findmnt`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/gitr/xfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/kdevops/scripts/jounal-dump.sh -->
## sources/test-tools/kdevops/workflows/kdevops/scripts/jounal-dump.sh

Purpose: Converts remote systemd journal files into artifact-friendly per-guest text dumps.

Important APIs/types/functions: Script inputs are one argument `DIR` pointing to remote journals and a hardcoded `hosts` inventory file. It uses `journalctl --file`.

Control flow: Creates a local `journal` directory, validates one argument, extracts guest names from the `[all]` group in `hosts`, then for each guest reads `$DIR/remote-$guest.journal` and writes `journal/$guest.journal` if present.

State and persistence: Persists text journal dumps under `journal/`. Reads remote journal binary files but does not alter them.

Dependencies and integration points: Depends on Ansible inventory format, systemd `journalctl`, and kdevops journal naming. The filename is misspelled `jounal`, matching related scripts.

Risks and test signals: Inventory parsing only reads immediate lines after `[all]` and may miss complex inventories. Test with a sample `hosts` file and one remote journal file.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/kdevops/scripts/jounal-dump.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/kdevops/scripts/jounal-ln.sh -->
## sources/test-tools/kdevops/workflows/kdevops/scripts/jounal-ln.sh

Purpose: Creates host-name symlinks for remote journal files that are named by IP address.

Important APIs/types/functions: Positional args are `DIR`, `HOST`, and `IP`. Uses `find`, `sed`, `rm`, and `ln -s`.

Control flow: Removes broken symlinks under `DIR`, finds files whose path contains the IP, computes a target path by replacing the IP with the host name, removes any existing target, and creates a symlink.

State and persistence: Deletes broken symlinks and creates/replaces host-name symlinks.

Dependencies and integration points: Intended to support the journal dump/list tooling and kdevops remote journal layout.

Risks and test signals: Unquoted variables and regex interpolation can misbehave for unusual paths/IPs. Test in a temporary directory with representative journal filenames before using on real artifacts.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/kdevops/scripts/jounal-ln.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/kdevops/scripts/jounal-ls.sh -->
## sources/test-tools/kdevops/workflows/kdevops/scripts/jounal-ls.sh

Purpose: Lists remote journal symlinks and their backing file sizes/IP addresses.

Important APIs/types/functions: Takes one `DIR` argument, reads `kdevops_host_prefix` from `extra_vars.yaml`, and uses `find`, `readlink`, `du`, and formatted `printf`.

Control flow: Validates one argument, computes a host prefix, finds symlinked journal files matching the prefix, skips names containing `@`, resolves each link, gets size, derives IP from the real filename, and prints a table.

State and persistence: Read-only aside from command output.

Dependencies and integration points: Depends on `extra_vars.yaml`, symlinks created by `jounal-ln.sh`, and remote journal naming.

Risks and test signals: The early `FILES=$(find ... $IP ...)` references unset `IP` and is unused; path stripping assumes exact `$DIRremote-` concatenation. Test with real symlink paths and confirm IP extraction.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/kdevops/scripts/jounal-ls.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/linux/Kconfig -->
## sources/test-tools/kdevops/workflows/linux/Kconfig

Purpose: Configures the bootlinux workflow for cloning, building, installing, and rebooting into selected Linux kernel trees.

Important APIs/types/functions: Major symbols include build-location choices `BOOTLINUX_TARGETS`, `BOOTLINUX_9P`, `BOOTLINUX_BUILDER`; compiler choice; reproducible/clean/ccache options; tree families `BOOTLINUX_LINUS/STABLE/DEV/CUSTOM`; derived `BOOTLINUX_TREE_NAME`, `BOOTLINUX_TREE`, `BOOTLINUX_TREE_REF`; message-id testing via `BOOTLINUX_TEST_MESSAGE_ID`; shallow clone; and A/B baseline/dev ref controls.

Control flow: The file is gated by `BOOTLINUX`. It selects build topology, optional 9p settings, compiler/cache behavior, tree family and sourced tree-specific Kconfigs, custom tree overrides, derived tree/ref values, optional b4 patch application, shallow clone depth, and A/B baseline/dev kernel selection.

State and persistence: Kconfig writes persistent `.config` and YAML-output variables. Runtime state is created by the Makefile/Ansible playbook, not by Kconfig.

Dependencies and integration points: Sources many generated/static Kconfig fragments (`Kconfig.linus`, stable, next, vfs, xfs, modules, etc.). Integrates with CLI variables `LINUX_TREE`, `LINUX_TREE_REF`, `B4_MESSAGE_ID`, libvirt 9p, ccache, and kdevops baseline/dev host groups.

Risks and test signals: Tree/ref derivation is complex and CLI override interaction can be subtle. Test via menuconfig/defconfig, inspect `extra_vars.yaml`, run clone-only targets, and verify baseline/dev refs when A/B testing is enabled.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/linux/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/linux/Makefile -->
## sources/test-tools/kdevops/workflows/linux/Makefile

Purpose: Converts bootlinux Kconfig into Ansible arguments and defines Make targets for kernel clone, build, install, deploy, uninstall, reboot, uname, and optional CXL module workflows.

Important APIs/types/functions: Uses `BOOTLINUX_ARGS`, `BOOTLINUX_LIMIT`, `LINUX_CLONE_DEFAULT_TYPE`, `LINUX_DYNAMIC_RUNTIME_VARS`, `HELP_TARGETS`, and targets `linux`, `linux-baseline`, `linux-dev`, `linux-mount`, `linux-deploy`, `linux-build`, `linux-install`, `linux-uninstall`, `linux-clone-*`, `linux-grub-setup`, `linux-reboot`, `uname`, and `linux-cxl`.

Control flow: Derives tree URL/name/ref/config, appends kernel build vars, shallow clone depth, make override, b4 message-id vars, 9p vars, and CXL test flag. If knfsd setup is enabled, `BOOTLINUX_LIMIT` includes `nfsd`. `linux` either fans into baseline/dev targets for A/B different refs or runs one playbook over the selected host limit.

State and persistence: Reads Kconfig-generated variables and may read `KVER` for uninstall. Runtime writes occur through Ansible: clones, builds, installs, GRUB changes, reboots, and saved kernel artifacts.

Dependencies and integration points: Depends on `KDEVOPS_PLAYBOOKS_DIR`, `bootlinux.yml`, inventory nodes, `extra_vars.yaml`, and configuration symbols from linux Kconfig.

Risks and test signals: Playbook tags must match role tag names; wrong host limits can skip NFS server kernel updates. Test with `make linux-clone`, `make linux-build`, `make uname`, and A/B baseline/dev invocations.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/linux/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/linux/refs/static/btrfs-devel.yaml -->
## sources/test-tools/kdevops/workflows/linux/refs/static/btrfs-devel.yaml

Purpose: Static ref manifest for the btrfs-devel kernel tree.

Important APIs/types/functions: Provides one `configs` entry mapping label `btrfs-devel` to config symbol `BOOTLINUX_TREE_BTRFS_DEVEL_REF_BTRFSDEVEL`, ref `btrfs-devel`, and help text.

Control flow: Data-only YAML consumed by Kconfig generation or ref selection tooling.

State and persistence: No runtime state; checked-in static metadata.

Dependencies and integration points: Must align with `workflows/linux/Kconfig.btrfs` generated symbols and bootlinux tree selection.

Risks and test signals: Ref names can stale if upstream branches rename. Test by regenerating Kconfig fragments and attempting a clone/checkout.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/linux/refs/static/btrfs-devel.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/linux/refs/static/cel-linux.yaml -->
## sources/test-tools/kdevops/workflows/linux/refs/static/cel-linux.yaml

Purpose: Static ref manifest for the cel-linux NFS server development tree.

Important APIs/types/functions: Defines `next`, `fixes`, `testing`, and `custom` entries mapped to `BOOTLINUX_TREE_CEL_LINUX_REF_*` symbols and refs such as `nfsd-next`.

Control flow: Data-only selection list; custom entry delegates ref to `BOOTLINUX_TREE_CEL_LINUX_CUSTOM_REF_NAME`.

State and persistence: Static metadata only.

Dependencies and integration points: Consumed by Linux Kconfig fragment generation and bootlinux tree/ref selection.

Risks and test signals: Branch names are external contracts with the maintainer tree. Validate by generating Kconfig and checking out each static ref.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/linux/refs/static/cel-linux.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/linux/refs/static/jlayton-linux.yaml -->
## sources/test-tools/kdevops/workflows/linux/refs/static/jlayton-linux.yaml

Purpose: Static ref manifest for Jeff Layton's Linux tree.

Important APIs/types/functions: Entries map `kdevops`, `iversion`, and `custom` to `BOOTLINUX_TREE_JLAYTON_LINUX_REF_*` symbols and refs.

Control flow: Data-only; custom ref uses `BOOTLINUX_TREE_JLAYTON_LINUX_CUSTOM_REF_NAME`.

State and persistence: Static YAML metadata.

Dependencies and integration points: Integrated into generated Linux tree Kconfig and bootlinux ref selection.

Risks and test signals: Ref availability can drift. Test by generated Kconfig symbol presence and clone checkout of `kdevops` and `iversion-next`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/linux/refs/static/jlayton-linux.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/linux/refs/static/kdevops-linus.yaml -->
## sources/test-tools/kdevops/workflows/linux/refs/static/kdevops-linus.yaml

Purpose: Static ref manifest for kdevops branches based on Linus's tree.

Important APIs/types/functions: Provides `minorder` mapped to `BOOTLINUX_TREE_KDEVOPS_LINUS_REF_LBS_MINORDER` and ref `large-block-minorder`.

Control flow: Data-only.

State and persistence: Static YAML metadata.

Dependencies and integration points: Feeds Linux Kconfig ref generation for kdevops-maintained trees.

Risks and test signals: Single-entry manifests are easy to overlook during branch cleanup. Validate checkout of `large-block-minorder`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/linux/refs/static/kdevops-linus.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/linux/refs/static/linus.yaml -->
## sources/test-tools/kdevops/workflows/linux/refs/static/linus.yaml

Purpose: Static ref manifest for Linus tree selections.

Important APIs/types/functions: Lists `master` and several release-candidate tags mapped to `BOOTLINUX_TREE_LINUS_REF_*` symbols.

Control flow: Data-only list used by generation tooling.

State and persistence: Static metadata only.

Dependencies and integration points: Integrated with `Kconfig.linus` and `LATEST_BOOTLINUX_TREE_REF` selection.

Risks and test signals: RC tags are historical and may not represent current desired test coverage. Test by regenerating Kconfig and checking `git ls-remote` for every ref.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/linux/refs/static/linus.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/linux/refs/static/mcgrof-linus.yaml -->
## sources/test-tools/kdevops/workflows/linux/refs/static/mcgrof-linus.yaml

Purpose: Static ref manifest for mcgrof large-block branches based on Linus's tree.

Important APIs/types/functions: Defines `lbs` and `lbs-nodeb` entries with symbols `BOOTLINUX_TREE_MCGROF_LINUS_REF_LBS*` and refs `large-block-linus` and `large-block-linus-nobdev`.

Control flow: Data-only.

State and persistence: Static YAML metadata.

Dependencies and integration points: Used by Linux Kconfig generation and bootlinux tree checkout.

Risks and test signals: Help text mentions sector-size compatibility; checkout and kernel config support should be verified for both branches.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/linux/refs/static/mcgrof-linus.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/linux/refs/static/mcgrof-next.yaml -->
## sources/test-tools/kdevops/workflows/linux/refs/static/mcgrof-next.yaml

Purpose: Static ref manifest for mcgrof large-block branches based on linux-next.

Important APIs/types/functions: Entries `lbs` and `lbs-nobdev` map to `BOOTLINUX_TREE_MCGROF_NEXT_REF_*` and refs `large-block-next`/`large-block-nobdev`.

Control flow: Data-only.

State and persistence: Static YAML metadata.

Dependencies and integration points: Feeds bootlinux Kconfig ref choices for development kernels.

Risks and test signals: next-based branches move or rebase often. Test checkout and build config availability before long workflow runs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/linux/refs/static/mcgrof-next.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/linux/refs/static/modules.yaml -->
## sources/test-tools/kdevops/workflows/linux/refs/static/modules.yaml

Purpose: Static ref manifest for modules tree testing.

Important APIs/types/functions: One entry `modules-next` maps to `BOOTLINUX_TREE_MODULES_REF_NEXT` and ref `modules-next`.

Control flow: Data-only.

State and persistence: Static metadata.

Dependencies and integration points: Used by generated modules Kconfig and bootlinux tree selection.

Risks and test signals: Ref availability is the only functional risk. Validate with `git ls-remote`/clone checkout.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/linux/refs/static/modules.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/linux/refs/static/next.yaml -->
## sources/test-tools/kdevops/workflows/linux/refs/static/next.yaml

Purpose: Static ref manifest for linux-next and fs-next/current branches.

Important APIs/types/functions: Entries include `master`, dated `next-20250328`, `fs-current`, and `fs-next`, mapped to `BOOTLINUX_TREE_NEXT_REF_*` symbols.

Control flow: Data-only selection set.

State and persistence: Static YAML metadata.

Dependencies and integration points: Integrated into `Kconfig.next` and bootlinux default/ref logic.

Risks and test signals: Dated next refs can age out of relevance, while `master` moves continuously. Test clone checkout and kernel config presence.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/linux/refs/static/next.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/linux/refs/static/stable.yaml -->
## sources/test-tools/kdevops/workflows/linux/refs/static/stable.yaml

Purpose: Static ref manifest for stable Linux releases and stable branches.

Important APIs/types/functions: Lists historical tags and longterm branch refs mapped to `BOOTLINUX_TREE_STABLE_REF_*`, including `linux-6.1.y` and `linux-6.6.y`.

Control flow: Data-only list.

State and persistence: Static YAML metadata.

Dependencies and integration points: Feeds stable Kconfig generation and bootlinux ref selection.

Risks and test signals: Stable branch coverage may lag current maintained series. Test generation, checkout, and whether inferred configs exist for selected stable refs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/linux/refs/static/stable.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/linux/refs/static/stable_rc.yaml -->
## sources/test-tools/kdevops/workflows/linux/refs/static/stable_rc.yaml

Purpose: Static ref manifest for stable release-candidate queue branches.

Important APIs/types/functions: Entries map queue branches `queue/5.4` through `queue/6.15` to `BOOTLINUX_TREE_STABLE_RC_REF_QUEUE_*` symbols.

Control flow: Data-only.

State and persistence: Static YAML metadata.

Dependencies and integration points: Used by stable-rc Kconfig generation and bootlinux tree/ref selection.

Risks and test signals: Queue branches are moving targets and may force rebuild variability. Test by recording exact commit IDs during workflow runs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/linux/refs/static/stable_rc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/linux/refs/static/vfs.yaml -->
## sources/test-tools/kdevops/workflows/linux/refs/static/vfs.yaml

Purpose: Static ref manifest for VFS block-size work.

Important APIs/types/functions: Defines `lbs` mapped to `BOOTLINUX_TREE_VFS_REF_LBS` and ref `vfs.blocksize`.

Control flow: Data-only.

State and persistence: Static metadata.

Dependencies and integration points: Consumed by Linux Kconfig generation for VFS tree choices.

Risks and test signals: Branch name is external and may be rebased. Validate checkout and build support for selected test configs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/linux/refs/static/vfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/linux/refs/static/xfs.yaml -->
## sources/test-tools/kdevops/workflows/linux/refs/static/xfs.yaml

Purpose: Static ref manifest for the XFS development tree.

Important APIs/types/functions: One entry `for-next` maps to `BOOTLINUX_TREE_XFS_REF_NEXT` and ref `for-next`.

Control flow: Data-only.

State and persistence: Static YAML metadata.

Dependencies and integration points: Used by XFS Linux Kconfig generation and bootlinux tree selection.

Risks and test signals: Moving `for-next` can change behavior across runs. Test by recording checked-out commit IDs and verifying config availability.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/linux/refs/static/xfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/ltp/Kconfig -->
## sources/test-tools/kdevops/workflows/ltp/Kconfig

Purpose: Configures Linux Test Project workflow groups and repository source/ref.

Important APIs/types/functions: Test group symbols include `LTP_TESTS_CVE`, `FCNTL`, `FS`, `FS_BIND`, `FS_PERMS_SIMPLE`, `FS_READONLY`, `NFS`, `NOTIFY`, `RPC`, `SMACK`, and `TIRPC`. Repo symbols include `HAVE_MIRROR_LTP`, `LTP_REPO_CUSTOM`, `LTP_REPO_URL`, `LTP_REPO`, and `LTP_REPO_COMMIT`.

Control flow: Dedicated workflow mode exposes test group selections. Repo source defaults to a mirror when present or default upstream otherwise, with custom URL override support.

State and persistence: Kconfig selections persist to `.config`; Makefile turns them into `LTP_ARGS` and group lists.

Dependencies and integration points: Uses libvirt mirror detection and default LTP URL constants. Integrated with `ltp.yml` Ansible playbook.

Risks and test signals: Default commit is pinned to `20240129`; users expecting latest LTP need to update it. Test by inspecting generated `ltp_repo`/`ltp_repo_commit` and selected group vars.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/ltp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/ltp/Makefile -->
## sources/test-tools/kdevops/workflows/ltp/Makefile

Purpose: Emits LTP workflow variables and defines targets to setup, run, reset, and display LTP results.

Important APIs/types/functions: Uses `LTP_ARGS`, `LTP_ENABLED_TEST_GROUPS`, `WORKFLOW_ARGS`, `WORKFLOW_ARGS_SEPARATED`, and targets `ltp`, `ltp-baseline`, `ltp-dev-baseline`, `ltp-dev-reset`, `ltp-show-results`, and `ltp-help-menu`.

Control flow: Maps every group symbol to explicit true/false vars and appends enabled group labels. Results path is based on `workflows/ltp/results/last-kernel.txt`; targets invoke `ltp.yml` with setup or run/copy tags.

State and persistence: Reads result metadata and logs. Runtime state is created by Ansible on guests and copied into workflow result directories.

Dependencies and integration points: Depends on `KDEVOPS_PLAYBOOKS_DIR`, `extra_vars.yaml`, baseline/dev host groups, and result directory conventions.

Risks and test signals: False vars are emitted for disabled groups, which is useful but must match Ansible expectations. Test with a minimal group selection and inspect playbook variable decisions and copied logs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/ltp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/minio/Kconfig -->
## sources/test-tools/kdevops/workflows/minio/Kconfig

Purpose: Top-level MinIO workflow Kconfig for enabling MinIO Warp benchmarking.

Important APIs/types/functions: Main symbol is `KDEVOPS_WORKFLOW_ENABLE_MINIO_WARP`. When enabled, it sources `Kconfig.docker`, `Kconfig.storage`, and `Kconfig.warp`.

Control flow: The whole menu is gated by `KDEVOPS_WORKFLOW_ENABLE_MINIO`; Warp support defaults on and then pulls in docker/storage/warp subconfiguration.

State and persistence: Kconfig persists selections and YAML-output symbols from sourced files; this file itself writes no runtime state.

Dependencies and integration points: Integrates with MinIO Ansible roles, Docker/container settings, storage provisioning, and warp benchmark options.

Risks and test signals: Top-level enablement can hide sub-options if the parent workflow is disabled. Test by menuconfig/defconfig and checking generated extra-vars for MinIO subconfigs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/minio/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/minio/Makefile -->
## sources/test-tools/kdevops/workflows/minio/Makefile

Purpose: Defines MinIO setup, teardown, benchmark, result-generation, monitoring, and help targets.

Important APIs/types/functions: Targets include `minio`, `minio-install`, `minio-uninstall`, `minio-destroy`, `minio-warp`, `minio-results`, `monitor-results`, and `minio-help`. Uses `MINIO_PLAYBOOK=playbooks/minio.yml`.

Control flow: Setup delegates to install. Install/uninstall/destroy/run invoke `ansible-playbook` with specific tags. Results target checks `workflows/minio/results`, runs `generate_warp_report.py`, prints output locations, and lists recent PNGs.

State and persistence: Ansible creates/destroys MinIO containers/data. Result generation writes HTML/PNG artifacts under `workflows/minio/results`.

Dependencies and integration points: Depends on inventory, `KDEVOPS_EXTRA_VARS`, MinIO playbook tags, Python/matplotlib report generator, and warp result JSON naming.

Risks and test signals: The results target includes Unicode console icons and assumes generated PNG globbing; functional risk is mainly missing Python deps or result files. Test by running `make minio-results` on a directory with sample warp JSON.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/minio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/minio/scripts/analyze_warp_results.py -->
## sources/test-tools/kdevops/workflows/minio/scripts/analyze_warp_results.py

Purpose: Loads MinIO Warp JSON results, extracts performance metrics, and generates charts plus text/HTML reports.

Important APIs/types/functions: Functions include `load_warp_results`, `extract_metrics`, `generate_throughput_chart`, `generate_latency_chart`, `generate_performance_summary_chart`, `generate_text_report`, `generate_html_report`, and `main`.

Control flow: `main` resolves `workflows/minio/results`, loads `warp_benchmark_*.json`, extracts metrics from `total`, `by_op_type`, and `summary` structures, then writes throughput, latency, summary PNGs, a text report, and an HTML dashboard.

State and persistence: Reads result JSON files and writes `warp_throughput_performance.png`, `warp_latency_analysis.png`, `warp_performance_summary.png`, `warp_analysis_report.txt`, and `warp_benchmark_report.html`.

Dependencies and integration points: Requires Python, matplotlib, numpy, and optionally dateutil for robust timestamp parsing. It is a standalone analyzer adjacent to the MinIO workflow results directory.

Risks and test signals: Some report fields use metric keys that `extract_metrics` does not populate (`latency_min_ms`, `ops_total`, `error_rate`), so tables can show zeros despite available data. Test with representative Warp JSON schemas and verify generated charts are meaningful.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/minio/scripts/analyze_warp_results.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/minio/scripts/generate_warp_report.py -->
## sources/test-tools/kdevops/workflows/minio/scripts/generate_warp_report.py

Purpose: Generates per-result MinIO Warp throughput/operation graphs and an HTML report.

Important APIs/types/functions: Functions are `parse_warp_json`, `generate_throughput_graph`, `generate_operation_stats_graph`, `generate_html_report`, and `main`.

Control flow: `main` accepts an optional results directory, finds `warp_benchmark_*.json`, builds an HTML report over all results, then separately generates graphs for the most recent result. Parsing skips any non-JSON prefix before the first `{`.

State and persistence: Reads warp JSON files and writes `warp_benchmark_report.html` plus `*_throughput.png` and `*_operations.png` chart files in the results directory.

Dependencies and integration points: Called by `make minio-results`. Requires matplotlib and a Warp JSON schema with `total.throughput.segmented.segments` for throughput graphs.

Risks and test signals: The timestamp parser replaces only `-07:00`, which is brittle for other offsets, and the CSS contains an extra brace. Test with JSON from multiple time zones and confirm HTML/charts render.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/minio/scripts/generate_warp_report.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/minio/scripts/run_benchmark_suite.sh -->
## sources/test-tools/kdevops/workflows/minio/scripts/run_benchmark_suite.sh

Purpose: Runs a comprehensive MinIO Warp benchmark suite across mixed, get, put, delete, list, small-object, large-object, and high-concurrency workloads.

Important APIs/types/functions: Functions include `parse_duration_to_seconds` and `run_benchmark`. CLI positional inputs are host, access key, secret key, and total duration.

Control flow: Converts total duration to seconds, derives a per-test duration with a minimum of 30 seconds, creates `/tmp/warp-results`, then calls `warp` eight times with workload-specific concurrency/object size and JSON output redirected to timestamped files.

State and persistence: Writes result JSON/stdout files under `/tmp/warp-results`; leaves benchmark buckets because `--noclear` is used.

Dependencies and integration points: Requires the `warp` CLI, network access to MinIO, valid credentials, and MinIO bucket permissions. Intended to feed the MinIO report scripts.

Risks and test signals: Output filenames use only test type and one shared timestamp, so repeated `mixed` tests overwrite each other within a run. Test by running a short suite and counting result files; expected eight workloads may produce fewer files due to collisions.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/minio/scripts/run_benchmark_suite.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/mmtests/Kconfig -->
## sources/test-tools/kdevops/workflows/mmtests/Kconfig

Purpose: Configures mmtests repository and memory-management benchmark options.

Important APIs/types/functions: Symbols include `HAVE_MIRROR_MMTESTS`, `MMTESTS_GIT_URL`, `MMTESTS_TEST_TYPE`, `MMTESTS_ENABLE_THPCOMPACT`, `MMTESTS_ENABLE_THPCHALLENGE`, iteration/monitoring options, pretest drop-cache/compaction flags, and `MMTESTS_PRETEST_THP_SETTING`.

Control flow: The file is gated by `KDEVOPS_WORKFLOW_ENABLE_MMTESTS`, chooses repo URL from mirror/default, selects one mmtests type, sets iteration and monitor options, and sources type-specific and filesystem sub-Kconfigs.

State and persistence: Many symbols have `output yaml`, so selections become extra-vars. Runtime state is produced by Ansible/mmtests.

Dependencies and integration points: Integrates with libvirt mirror, default mmtests GitHub URL, monitoring playbooks, ftrace/proc/mpstat dependencies, and sourced mmtests subconfig files.

Risks and test signals: Monitor options assume target-side tool availability and permissions. Test by inspecting extra vars and running setup plus a small iteration count.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/mmtests/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/mmtests/Makefile -->
## sources/test-tools/kdevops/workflows/mmtests/Makefile

Purpose: Defines mmtests setup, run, results, compare, monitor, clean, and help targets.

Important APIs/types/functions: Targets are `mmtests`, `mmtests-baseline`, `mmtests-dev`, `mmtests-tests`, `mmtests-results`, `mmtests-compare`, `monitor-results`, `mmtests-clean`, and `mmtests-help`; shared variable is `MMTESTS_ARGS`.

Control flow: Each target invokes an Ansible playbook with relevant tags and host limits. Baseline/dev targets limit to `mmtests:&baseline` or `mmtests:&dev`; compare uses `mmtests-compare.yml`.

State and persistence: Runtime state is in guest mmtests installations and copied result directories. Make itself does not write state.

Dependencies and integration points: Depends on `playbooks/mmtests.yml`, `playbooks/mmtests-compare.yml`, `playbooks/monitor-results.yml`, `extra_vars.yaml`, and inventory groups.

Risks and test signals: The `mmtests` target has a command line where `$(MMTESTS_ARGS)` appears after a non-continued line, which may be interpreted as a separate shell command. Test `make -n mmtests` to verify emitted commands.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/mmtests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/nfstest/Kconfig -->
## sources/test-tools/kdevops/workflows/nfstest/Kconfig

Purpose: Configures the nfstest workflow: NFS server source, mount point, nfstest repository/ref, and selected nfstest groups.

Important APIs/types/functions: Symbols include `NFSTEST_USE_KDEVOPS_NFSD`, `NFSTEST_NFS_SERVER_HOST`, `NFSTEST_MNT`, `HAVE_MIRROR_NFSTEST`, `NFSTEST_REPO_CUSTOM`, `NFSTEST_REPO_URL`, `NFSTEST_REPO`, `NFSTEST_REPO_COMMIT`, and group selectors `NFSTEST_TEST_GROUP_*`.

Control flow: Server and repo settings are always available when workflow is enabled; group selectors are exposed in dedicated workflow mode. Default group is interop.

State and persistence: Kconfig persists values in `.config`; Makefile emits nfstest args and group list.

Dependencies and integration points: Selecting kdevops server pulls in `KDEVOPS_SETUP_NFSD`. Repo defaults use default nfstest URL or libvirt mirror.

Risks and test signals: The closing comment says `KDEVOPS_WORKFLOW_ENABLE_GITR`, likely a copy/paste error but not functional. Test by checking generated config, rendered repo/ref, and selected groups.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/nfstest/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/nfstest/Makefile -->
## sources/test-tools/kdevops/workflows/nfstest/Makefile

Purpose: Emits nfstest Ansible variables and defines setup/run/reset/results targets.

Important APIs/types/functions: Uses `NFSTEST_ARGS`, `NFSTEST_ENABLED_TEST_GROUPS`, `WORKFLOW_ARGS`, `WORKFLOW_ARGS_SEPARATED`, and targets `nfstest`, `nfstest-baseline`, `nfstest-dev-baseline`, `nfstest-dev-reset`, `nfstest-show-results`, and `nfstest-help-menu`.

Control flow: Chooses kdevops or external NFS server args, appends mount path, repo/ref, selected group labels, computes result find path from `last-kernel.txt`, and invokes `nfstest.yml` with setup or run/copy tags.

State and persistence: Reads result metadata/logs; Ansible handles nfstest installation and result copying.

Dependencies and integration points: Depends on `KDEVOPS_PLAYBOOKS_DIR`, `extra_vars.yaml`, baseline/dev host groups, and result directory layout.

Risks and test signals: External server branch references `CONFIG_NFSTEST_NFS_SERVER_HOSTNAME` and `CONFIG_NFSTEST_NFS_SERVER_EXPORT`, but the Kconfig defines `NFSTEST_NFS_SERVER_HOST` and no export symbol in the listed file. Test external-server mode specifically, as generated vars may be empty.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/nfstest/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/nfstest/scripts/generate_nfstest_html.py -->
## sources/test-tools/kdevops/workflows/nfstest/scripts/generate_nfstest_html.py

Purpose: Generates an HTML visualization for parsed nfstest results, with summary cards, progress bars, per-suite tables, optional charts, and configuration display.

Important APIs/types/functions: Functions include `format_time`, `generate_suite_chart`, `generate_overall_chart`, `embed_image`, `generate_html`, and `main`. `HTML_TEMPLATE` contains the page structure and styling.

Control flow: `main` takes a results directory or defaults to `workflows/nfstest/results/last-run`, requires `parsed_results.json`, creates a sibling `html` directory, loads parsed JSON, and calls `generate_html`. The generator computes overall stats, optionally produces matplotlib charts, embeds PNGs as base64, builds expandable suite sections, and writes `index.html`.

State and persistence: Reads `parsed_results.json`; writes chart PNGs and `index.html` under the generated html directory.

Dependencies and integration points: Depends on a separate parser (`parse_nfstest_results.py`) producing the expected JSON schema. Matplotlib is optional; without it the HTML still renders without charts.

Risks and test signals: The template contains decorative Unicode and some CSS brace irregularities, but the bigger functional risk is schema drift in `parsed_results.json`. Test with parser output containing passed/failed suites, no-result suites, and no matplotlib installed.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/nfstest/scripts/generate_nfstest_html.py -->
