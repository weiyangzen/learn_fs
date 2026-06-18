# subset-b-009254 research

Grouped research report for kdevops bootlinux, storage/build helper, CXL, partitioning, and devconfig Ansible role files. Each section preserves the exact source path and is wrapped for deterministic reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/templates/config-xfs-6.1.y -->
# sources/test-tools/kdevops/playbooks/roles/bootlinux/templates/config-xfs-6.1.y

Source read: complete file, 6081 lines, 161852 bytes, sha256 `ca34467e30860d28`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/bootlinux/templates/config-xfs-6.1.y_research.md`.

Purpose: static Linux 6.1 kernel `.config` template for the kdevops bootlinux role, tuned around XFS test guests. It fixes compiler/toolchain assumptions, x86_64 virtualization support, block/storage features, filesystem modules, tracing, and debug/fault-injection behavior for reproducible kernel builds.

Important APIs/types/functions: this is declarative Kconfig data rather than executable code. High-signal settings include `CONFIG_X86_64=y`, `CONFIG_MODULES=y`, `CONFIG_PREEMPT=y`, `CONFIG_CGROUPS=y`, `CONFIG_IO_URING=y`, `CONFIG_BLOCK=y`, `CONFIG_BLK_DEV_ZONED=y`, `CONFIG_BLK_DEBUG_FS=y`, `CONFIG_XFS_FS=m`, `CONFIG_XFS_QUOTA=y`, `CONFIG_XFS_POSIX_ACL=y`, `CONFIG_XFS_RT=y`, `CONFIG_XFS_DEBUG=y`, `CONFIG_EXT4_FS=m`, `CONFIG_BTRFS_FS=m`, `CONFIG_KVM=m`, `CONFIG_VIRTIO_BLK=m`, `CONFIG_NVME_*`, `CONFIG_DM_*`, `CONFIG_MD_RAID*`, and `CONFIG_CXL_*`.

Control flow: the bootlinux workflow consumes the file as a kernel configuration seed, normally copying or merging it into the Linux source tree before build. There are no branches at runtime in this file; behavior emerges when Kconfig, `make`, module packaging, bootloader setup, and initramfs handling interpret these symbols.

State and persistence behavior: the selected symbols persist into the built kernel image, generated modules, `/proc/config.gz` when `CONFIG_IKCONFIG_PROC=y`, and boot/runtime capabilities. XFS, ext4, btrfs, KVM, virtio, NVMe, SCSI, CXL, DM, and MD support are mostly modular, so module availability and initramfs contents determine what is usable at boot.

Dependencies and integration: tied to GCC/binutils style x86_64 builds (`CONFIG_CC_IS_GCC=y`, GCC 11.3 in the captured text), kdevops VM boot flows, storage tests, block debugfs/fault-injection tooling, QEMU/KVM guests, virtio devices, NVMe fabrics/target tests, and CXL/pmem workflows. NFS is disabled, so NFS workflows need another config.

Risks: XFS debug and broad tracing add overhead and can change timing-sensitive filesystem tests. XFS online scrub is disabled. btrfs lacks POSIX ACL, integrity, sanity, debug, assert, and ref-verify settings, so it is not a maximal btrfs debug kernel. NFS client/server support is absent. Modular storage drivers can break early root/data-device discovery if not included in initramfs.

Test signals: useful validation is `scripts/config` or `make olddefconfig` stability, successful boot under the target QEMU/KVM profile, `/proc/config.gz` matching the template intent, `modprobe xfs btrfs ext4 virtio_blk nvme cxl_mem`, mounting XFS with quotas/ACL/rt where expected, and running storage tests that exercise block debugfs, fail-make-request, dm-log-writes, and XFS debug paths.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/templates/config-xfs-6.1.y -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/btrfs_progs/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/btrfs_progs/defaults/main.yml

Source read: complete file, 8 lines, 215 bytes, sha256 `b47e75c917f94f33`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/btrfs_progs/defaults/main.yml_research.md`.

Purpose: defaults for the `btrfs_progs` role. They disable source builds by default and define where btrfs-progs will be cloned, which repository is used, and which branch/tag to build.

Important APIs/types/functions: Ansible variables `btrfs_progs_build`, `btrfs_progs_data`, `btrfs_progs_git`, and `btrfs_progs_version`. The path depends on the broader `data_path` variable supplied by kdevops inventory/workflow configuration.

Control flow: loaded automatically by the role before tasks run. Downstream tasks use `btrfs_progs_build|bool` to decide whether dependency install, git clone, configure, build, and install steps are active.

State and persistence behavior: no host state is changed by this file alone. It determines persistent clone/build state under `{{ data_path }}/btrfs-progs` when enabled.

Dependencies and integration: integrated with `btrfs_progs/tasks/main.yml`, distribution-specific dependency tasks, and any workflow that needs a custom btrfs-progs binary instead of the distro package.

Risks: the default `devel` version tracks a moving upstream branch, so enabled builds are not reproducible unless callers pin `btrfs_progs_version`. `GIT_SSL_NO_VERIFY` in the consuming task reduces transport assurance.

Test signals: an Ansible dry run should show no build activity with defaults; with `btrfs_progs_build=true`, the role should clone to `btrfs_progs_data` and produce an installed `btrfs` binary in the configured bindir.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/btrfs_progs/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/btrfs_progs/tasks/install-deps/debian/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/btrfs_progs/tasks/install-deps/debian/main.yml

Source read: complete file, 22 lines, 496 bytes, sha256 `330a058aed97b947`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/btrfs_progs/tasks/install-deps/debian/main.yml_research.md`.

Purpose: Debian-family dependency installation for building btrfs-progs from source.

Important APIs/types/functions: `ansible.builtin.apt` updates the package cache and installs `libext2fs-dev`, `pkg-config`, `libblkid-dev`, `libzstd-dev`, `libudev-dev`, and `liblzo2-dev`. Tasks use `become: true` with sudo and tags `btrfs-progs`, `update-cache`, and `build-deps`.

Control flow: first refresh apt metadata, then install the build dependency set. This file is imported only when the dispatcher sees `ansible_facts['os_family']|lower == 'debian'`.

State and persistence behavior: mutates apt cache and package database. Installed development headers persist on the target VM.

Dependencies and integration: supports `btrfs_progs/tasks/main.yml` before `autogen.sh`, `configure`, and `make`. It assumes Debian/Ubuntu package names and apt availability.

Risks: no retry wrapper around apt operations. Missing `git`, compiler, automake/autoconf, or make may be supplied elsewhere; if not, source builds can fail after this dependency step.

Test signals: run with the role tag on Debian/Ubuntu and confirm apt reports the listed packages present before configure.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/btrfs_progs/tasks/install-deps/debian/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/btrfs_progs/tasks/install-deps/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/btrfs_progs/tasks/install-deps/main.yml

Source read: complete file, 9 lines, 395 bytes, sha256 `8767e6f3cbe0468d`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/btrfs_progs/tasks/install-deps/main.yml_research.md`.

Purpose: OS-family dispatcher for btrfs-progs build dependencies.

Important APIs/types/functions: `ansible.builtin.import_tasks` statically imports `debian/main.yml`, `suse/main.yml`, or `redhat/main.yml` based on `ansible_facts['os_family']|lower`.

Control flow: evaluates three independent `when` clauses for Debian, SUSE, and RedHat families. Only the matching import should execute in normal facts.

State and persistence behavior: the dispatcher has no direct state mutation; imported files install packages and may set SUSE distro facts.

Dependencies and integration: called from `btrfs_progs/tasks/main.yml` when `btrfs_progs_build` is true. Relies on gathered facts and relative task paths.

Risks: unsupported OS families silently skip all dependency setup. Because `import_tasks` is static, syntax errors in any imported file can affect play parsing even when conditions later skip execution.

Test signals: `ansible-playbook --syntax-check` and distro matrix dry runs should show exactly one dependency path selected per target.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/btrfs_progs/tasks/install-deps/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/btrfs_progs/tasks/install-deps/redhat/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/btrfs_progs/tasks/install-deps/redhat/main.yml

Source read: complete file, 14 lines, 318 bytes, sha256 `c06ea188ec89d827`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/btrfs_progs/tasks/install-deps/redhat/main.yml_research.md`.

Purpose: Red Hat family package installation for btrfs-progs source builds.

Important APIs/types/functions: `ansible.builtin.dnf` installs `e2fsprogs-devel`, `libblkid-devel`, `libuuid-devel`, `libzstd-devel`, `systemd-devel`, and `lzo-devel` with sudo.

Control flow: a single package task runs when imported by the OS dispatcher on RedHat-family systems.

State and persistence behavior: updates the rpm/dnf package database by ensuring development packages are present.

Dependencies and integration: prepares for btrfs-progs `autogen.sh` and `configure`. The role assumes package naming is valid across Red Hat-like distributions.

Risks: package names such as `systemd-devel` and `lzo-devel` vary across old enterprise releases and may need CodeReady/CRB repos enabled. No retry or cache refresh is included here.

Test signals: on Fedora/RHEL/CentOS/Oracle Linux, dnf should install the list and a subsequent `./configure --disable-documentation --enable-experimental` should locate blkid, uuid, zstd, udev/systemd, lzo, and ext2fs headers.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/btrfs_progs/tasks/install-deps/redhat/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/btrfs_progs/tasks/install-deps/suse/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/btrfs_progs/tasks/install-deps/suse/main.yml

Source read: complete file, 21 lines, 631 bytes, sha256 `cafa726d37836660`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/btrfs_progs/tasks/install-deps/suse/main.yml_research.md`.

Purpose: SUSE-family package installation for btrfs-progs source builds.

Important APIs/types/functions: `ansible.builtin.set_fact` creates `is_sle`, `is_leap`, and `is_tumbleweed`; `ansible.builtin.package` installs e2fsprogs, blkid, uuid, zstd, lzo, zlib, and udev development packages.

Control flow: facts are always set, then package installation runs with sudo when the file is imported for SUSE.

State and persistence behavior: records distro classification as host facts for later tasks in the play and changes the zypper/rpm package state.

Dependencies and integration: supports btrfs-progs configure/build on SLES, SLED, Leap, and Tumbleweed. Similar fact naming appears in other kdevops SUSE tasks.

Risks: the distro facts are not used in this file to gate packages, so older SLE systems with missing repositories may fail. Duplicate/inconsistent package names across SUSE releases can require devconfig repo preparation.

Test signals: a SUSE run should install the package set and allow btrfs-progs configure to detect zlib, libudev, zstd, lzo, uuid, blkid, and ext2fs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/btrfs_progs/tasks/install-deps/suse/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/btrfs_progs/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/btrfs_progs/tasks/main.yml

Source read: complete file, 103 lines, 2708 bytes, sha256 `d5c6fc54e4cbb968`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/btrfs_progs/tasks/main.yml_research.md`.

Purpose: main orchestration for optionally building and installing upstream btrfs-progs.

Important APIs/types/functions: `include_vars` for optional `extra_vars`, `include_role: create_data_partition`, `include_tasks: install-deps/main.yml`, `set_fact` for `build_btrfs_progs_now` and `bindir`, `ansible.builtin.git`, `community.general.make`, and `ansible.builtin.command` for `autogen.sh`, `configure`, `{{ num_jobs }}`, and `{{ make }} install`.

Control flow: load optional variables, ensure the data partition role runs, install dependencies only if `btrfs_progs_build`, compute the build flag, choose `/usr/bin` on Debian and `/usr/sbin` elsewhere, clone the selected repository/version when building, attempt `make clean-all`, run autotools configure with documentation and Python disabled plus experimental enabled, build with `nproc.stdout`, and install with elevated privileges.

State and persistence behavior: creates or updates the btrfs-progs git checkout under `btrfs_progs_data`, may leave build artifacts there, and installs binaries into `/usr` with distro-specific bindir behavior. It also mutates Ansible facts used later in the play.

Dependencies and integration: depends on `create_data_partition`, distro dependency tasks, `num_jobs`, `make`, `data_path`, and btrfs-progs autotools. It integrates with storage workflows that need a newer btrfs userland than the distro package.

Risks: `make clean-all` lacks a `when` guard and ignores errors, so it can run even when no source checkout exists. `GIT_SSL_NO_VERIFY=true` weakens clone verification. Build idempotence is coarse, and installing from a moving `devel` branch can replace distro tools unpredictably.

Test signals: with `btrfs_progs_build=false`, only variable loading and data partition setup should run. With it true, confirm clone, configure, parallel make, and install all run and `btrfs --version` reflects the requested version.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/btrfs_progs/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_linux/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/build_linux/defaults/main.yml

Source read: complete file, 26 lines, 1007 bytes, sha256 `e9b3d0f5e2a2eba4`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/build_linux/defaults/main.yml_research.md`.

Purpose: defaults for the build-linux workflow role, controlling repeated kernel build benchmarking and optional dedicated build storage.

Important APIs/types/functions: variables include `build_linux_repeat_count`, `build_linux_make_jobs`, `build_linux_target`, `build_linux_clean_between`, `build_linux_collect_stats`, `build_linux_results_dir`, `build_linux_storage_enable`, `build_linux_device`, `build_linux_use_latest_tag`, `build_linux_allow_modifications`, `shallow_clone`, `clone_depth`, `linux_source_dir`, `linux_build_dir`, and `linux_git_url`.

Control flow: no executable tasks; these defaults are consumed by `tasks/main.yml` and the copied `build_linux.py` script.

State and persistence behavior: defaults place kernel source, object tree, and results under `{{ data_path }}/build`. Enabling storage causes the role to format and mount `build_linux_device`.

Dependencies and integration: `linux_git_url` defaults to `bootlinux_tree` or Torvalds' tree, tying the benchmark to bootlinux/kernel configuration. Results feed workflow reporting under `workflows/build-linux/results` and target-side `build-results`.

Risks: repeat count 100 can be long and storage-heavy. `shallow_clone=true` with depth 1 limits tag/history operations unless later fetching succeeds. An empty `build_linux_device` is dangerous if storage is enabled without inventory validation.

Test signals: inspect resolved vars before running; a smoke run with low repeat count should create source/build directories and a summary JSON.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_linux/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_linux/tasks/install-deps/debian/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/build_linux/tasks/install-deps/debian/main.yml

Source read: complete file, 24 lines, 685 bytes, sha256 `d17bd62949d096d5`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/build_linux/tasks/install-deps/debian/main.yml_research.md`.

Purpose: Debian-family dependency installation for build-linux timing and visualization support.

Important APIs/types/functions: `ansible.builtin.apt` installs `time` for timing statistics and `python3-matplotlib` plus `python3-numpy` for visualization, gated by `kdevops_workflow_enable_build_linux|default(false)|bool`.

Control flow: two independent package tasks run only when the build-linux workflow is enabled.

State and persistence behavior: mutates apt package state on targets. It does not install compiler/kernel build prerequisites, which are presumably provided elsewhere.

Dependencies and integration: imported by the build_linux dependency dispatcher. The installed Python packages support result plotting/reporting rather than the core kernel build.

Risks: if compiler/build dependencies are absent, this file alone is insufficient. No apt cache update or retry is present.

Test signals: on Debian/Ubuntu with the workflow flag true, apt should ensure `time`, matplotlib, and numpy are installed; with the flag false, the task should be skipped.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_linux/tasks/install-deps/debian/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_linux/tasks/install-deps/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/build_linux/tasks/install-deps/main.yml

Source read: complete file, 13 lines, 589 bytes, sha256 `87b5aa5f2260f49b`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/build_linux/tasks/install-deps/main.yml_research.md`.

Purpose: OS-family dispatcher for build-linux dependency tasks.

Important APIs/types/functions: `ansible.builtin.import_tasks` routes to Debian, RedHat, or SUSE task files using `ansible_facts['os_family']|lower`.

Control flow: evaluates three distro-family `when` clauses; exactly one should match a supported host.

State and persistence behavior: no direct state changes, but imported files install packages.

Dependencies and integration: first task imported by `build_linux/tasks/main.yml`; assumes fact gathering and the relative install-deps layout.

Risks: unsupported OS families receive no dependency setup. Static import behavior can expose parse errors in skipped files.

Test signals: syntax check and distro dry runs should show only the matching package manager module executing.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_linux/tasks/install-deps/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_linux/tasks/install-deps/redhat/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/build_linux/tasks/install-deps/redhat/main.yml

Source read: complete file, 24 lines, 685 bytes, sha256 `83ad7e6fa5200b97`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/build_linux/tasks/install-deps/redhat/main.yml_research.md`.

Purpose: Red Hat family installation of build-linux timing and visualization packages.

Important APIs/types/functions: `ansible.builtin.dnf` installs `time`, `python3-matplotlib`, and `python3-numpy`, each task gated by `kdevops_workflow_enable_build_linux|default(false)|bool`.

Control flow: timing dependencies and visualization dependencies are separate tasks.

State and persistence behavior: changes dnf/rpm package state when the workflow is enabled.

Dependencies and integration: mirrors the Debian/SUSE package intent for build result statistics and plotting.

Risks: package availability may depend on enabled repos. Core kernel build dependencies are out of scope here.

Test signals: on RedHat-family hosts, enabling the workflow should install these packages and allow the downstream summary visualization code to import numpy/matplotlib.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_linux/tasks/install-deps/redhat/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_linux/tasks/install-deps/suse/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/build_linux/tasks/install-deps/suse/main.yml

Source read: complete file, 24 lines, 695 bytes, sha256 `4fbc28b48f992a64`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/build_linux/tasks/install-deps/suse/main.yml_research.md`.

Purpose: SUSE-family installation of build-linux timing and visualization packages.

Important APIs/types/functions: `community.general.zypper` installs `time`, `python3-matplotlib`, and `python3-numpy`, gated by `kdevops_workflow_enable_build_linux|default(false)|bool`.

Control flow: two package tasks run when the build-linux workflow flag is true.

State and persistence behavior: mutates zypper package state and leaves the tools installed for future benchmark runs.

Dependencies and integration: imported by the build-linux OS dispatcher and supports result statistics/plotting.

Risks: old SLE repos may not provide the Python visualization packages without repo preparation. No retry or repo refresh is performed.

Test signals: SUSE dry runs should skip unless enabled; real enabled runs should leave `time` and importable numpy/matplotlib available.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_linux/tasks/install-deps/suse/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_linux/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/build_linux/tasks/main.yml

Source read: complete file, 245 lines, 8141 bytes, sha256 `333bea63daf7cd58`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/build_linux/tasks/main.yml_research.md`.

Purpose: full orchestration for repeated Linux kernel build benchmarking, including optional filesystem setup, source checkout validation, script deployment, asynchronous builds, and result summary display.

Important APIs/types/functions: `set_fact`, `stat`, `shell`, `command`, `ansible.builtin.filesystem`, `ansible.posix.mount`, `ansible.builtin.git`, `copy`, `slurp`, `from_json`, and `debug`. It calls `build_linux.py` with source/build/results/count/jobs/target/clean/stats/tag arguments.

Control flow: install deps; infer filesystem type and optional XFS block size from hostname for multifs testing; optionally format and mount a dedicated build filesystem; create source/build/result dirs; validate existing git repo; delete corrupt repo; shallow or full clone Linux; optionally fetch tags; ensure data dir ownership; copy the Python benchmark script; run repeated kernel builds asynchronously with a 10-hour timeout; display stdout; read summary JSON and print aggregate statistics.

State and persistence behavior: can destructively reformat `build_linux_device`, mounts `{{ data_path }}/build`, creates/chowns directories, clones or removes a Linux source tree, writes `{{ data_path }}/build_linux.py`, and produces summary JSON under `{{ data_path }}/build-results`.

Dependencies and integration: integrates with workflow flags, `bootlinux_tree`, `build_linux_*` vars, the external `workflows/build-linux/scripts/build_linux.py`, git, mkfs tools, `mkfs.xfs`, Ansible mount/filesystem modules, and target hostname conventions for multifs.

Risks: enabling storage with the wrong device can wipe data. The `mount_check` shell greps broad mount output. If an existing `.git` directory is corrupt, the source directory is removed. Long async builds can hide early failures until polling completes. Tag fetching is skipped when the source dir is not writable.

Test signals: smoke with `build_linux_repeat_count=1`; verify filesystem type/mount when storage is enabled; confirm clone path, build script copy, nonzero stdout, and `summary_{{ ansible_hostname }}.json` with total/success/failure/time fields.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_linux/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_qemu/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/build_qemu/defaults/main.yml

Source read: complete file, 16 lines, 496 bytes, sha256 `7a90edfef861cdba`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/build_qemu/defaults/main.yml_research.md`.

Purpose: defaults for optional QEMU source build/install support.

Important APIs/types/functions: variables include `qemu_build`, `qemu_force_install_if_present`, `qemu_bin_path`, `qemu_data`, `qemu_git`, `qemu_version`, `qemu_build_dir`, `qemu_target`, `build_linux_shallow_clone`, and `build_linux_clone_depth`.

Control flow: no tasks; values are consumed by `build_qemu/tasks/main.yml` and dependency dispatchers.

State and persistence behavior: when enabled, clone and build artifacts persist under `{{ data_path }}/qemu`, with install targeting `/usr/local/bin/qemu-system-x86_64` by default.

Dependencies and integration: supports kdevops workflows that require a custom QEMU, especially storage/CXL behavior not available in distro QEMU.

Risks: default version `v7.2.0-rc4` is old and pre-release. The `build_linux_*` variable names in this QEMU role may be confusing or unused here.

Test signals: with defaults no QEMU build should happen; enabling `qemu_build` should drive clone/configure/build/install unless a usable binary already exists and force is false.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_qemu/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/debian/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/debian/main.yml

Source read: complete file, 75 lines, 1625 bytes, sha256 `108d9cbe4126b381`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/debian/main.yml_research.md`.

Purpose: Debian-family QEMU build dependency installation.

Important APIs/types/functions: `ansible.builtin.apt` updates the cache and installs a broad set of QEMU development dependencies: Meson/Ninja/Python/Sphinx, pixman, libfdt, libslirp, liburing, libusb, GTK/SDL/VTE/virgl, storage libraries for gluster/rbd/iscsi/nfs/pmem, RDMA, Xen, SPICE, seccomp, zstd, and documentation tooling.

Control flow: update cache first, then install the package list in one apt task tagged `qemu` and `build-deps`.

State and persistence behavior: persists a large development toolchain and library set on the target.

Dependencies and integration: imported by the build_qemu dependency dispatcher on Debian/Ubuntu and consumed by QEMU `./configure --target-list=... --disable-download`.

Risks: the package set is expansive and may differ across Debian/Ubuntu releases. No retry is present. Some packages are optional for the configured `x86_64-softmmu` target but still installed.

Test signals: after install, QEMU configure should not attempt downloads and should find Meson/Ninja plus the listed optional libraries.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/debian/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/fedora/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/fedora/main.yml

Source read: complete file, 271 lines, 6055 bytes, sha256 `69abb67030010304`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/fedora/main.yml_research.md`.

Purpose: Fedora-specific QEMU dependency installation with an initial binary presence check.

Important APIs/types/functions: `ansible.builtin.command: which qemu-system-x86_64` registers `qemu_present`; `ansible.builtin.dnf` installs a very large Fedora package set spanning compiler tools, Meson/Ninja, GTK/SDL/SPICE/VTE, gluster, RDMA, liburing, Xen, Sphinx docs, tracing, valgrind, virgl, USB redirection, and storage/network libraries.

Control flow: verify whether QEMU is already in PATH, treating rc 1 as changed but not failed; then install the package list.

State and persistence behavior: changes dnf package state significantly. The verify task only records state; it does not gate the install inside this file.

Dependencies and integration: selected specifically when `ansible_facts['distribution']|lower == 'fedora'`, separate from generic RedHat handling.

Risks: enormous package footprint, duplicated entries, and version-pinned names such as `pkgconf-1.8.0` can break across Fedora releases. The verification result is not used locally to skip installation.

Test signals: Fedora runs should complete dnf dependency installation and then allow QEMU configure/build without subproject downloads.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/fedora/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/main.yml

Source read: complete file, 22 lines, 794 bytes, sha256 `479b00a197f3d129`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/main.yml_research.md`.

Purpose: OS and distribution dispatcher for QEMU build dependencies.

Important APIs/types/functions: optional `include_vars` loads `{{ ansible_facts['os_family'] | lower }}.yml`; `import_tasks` dispatches to Debian, SUSE, RedHat, or Fedora task files.

Control flow: load optional distribution-specific variables if present; run Debian for Debian family, SUSE for SUSE family, RedHat for RedHat family except Fedora, and Fedora for Fedora distribution.

State and persistence behavior: no direct state changes except loaded vars; imported files install package dependencies.

Dependencies and integration: called from `build_qemu/tasks/main.yml` only when a QEMU source build is requested and needed.

Risks: RedHat package file appears to use Debian-style package names in places, making the Fedora split important and non-Fedora RedHat behavior suspect. Unsupported distributions silently skip dependency setup.

Test signals: syntax check and dry runs should prove only one install-deps path is selected; Fedora must not also run `redhat/main.yml`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/redhat/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/redhat/main.yml

Source read: complete file, 66 lines, 1427 bytes, sha256 `00f749d8b5494129`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/redhat/main.yml_research.md`.

Purpose: generic Red Hat family QEMU build dependency installation for non-Fedora systems.

Important APIs/types/functions: `ansible.builtin.dnf` installs a package list that mirrors the Debian dependency names, including `gnutls-dev`, `libaio-dev`, `libcurl4-gnutls-dev`, `libfdt-dev`, `liburing-dev`, `python3-sphinx-rtd-theme`, `zlib1g-dev`, and others.

Control flow: one dnf task ensures the list is present when imported by the dispatcher.

State and persistence behavior: mutates rpm package state.

Dependencies and integration: intended for RHEL/CentOS/Oracle Linux QEMU source builds.

Risks: many names are Debian-style and likely invalid on RHEL-compatible systems, unlike the Fedora file's native names. CodeReady/CRB repositories may be needed even after names are corrected. No retry or repo enablement occurs here.

Test signals: run on the target non-Fedora RedHat family release; if dnf cannot resolve names, this file needs a package-name translation pass before QEMU builds can be reliable.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/redhat/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/suse/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/suse/main.yml

Source read: complete file, 421 lines, 9853 bytes, sha256 `63bacada8a90b5b6`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/suse/main.yml_research.md`.

Purpose: SUSE-family QEMU build dependency installation, currently targeting Tumbleweed with a broad package closure.

Important APIs/types/functions: `set_fact` classifies SLE/Leap/Tumbleweed; `ansible.builtin.package` installs hundreds of packages including compilers, cross toolchains, Meson/Ninja, GTK/SDL/SPICE/VTE, gluster, RDMA, liburing, Xen, Sphinx docs, virgl, USB redirection, CXL-adjacent storage libraries, and X/Wayland development packages. The package task runs only when `is_tumbleweed`.

Control flow: set distro facts, then install the package set for Tumbleweed.

State and persistence behavior: changes zypper/rpm package state heavily and leaves a full QEMU build environment on the host.

Dependencies and integration: imported by QEMU dependency dispatcher for SUSE systems. It assumes Tumbleweed package naming and repository availability.

Risks: Leap/SLE are classified but do not install anything here, so QEMU builds on those systems lack dependencies. The package set is large, version-specific (`python38-*`, `gcc12`), and likely to age quickly.

Test signals: on Tumbleweed, dependency install should complete and QEMU configure should find expected optional features. On Leap/SLE, dry runs should reveal skipped dependency installation as a known gap.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/suse/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/main.yml

Source read: complete file, 109 lines, 2729 bytes, sha256 `96af79fafd95290f`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/main.yml_research.md`.

Purpose: main orchestration for optional QEMU source clone, configure, build, and install.

Important APIs/types/functions: optional `include_vars`, `stat` for `qemu_bin_path`, `include_tasks: install-deps/main.yml`, `set_fact build_qemu_now`, `file`, `git`, `command` for Meson subproject/configure/nproc, `community.general.make`, and privileged install through `{{ make }} install`.

Control flow: load extra vars; verify local QEMU binary when building; install deps if building and force or binary absent; initialize and maybe set `build_qemu_now`; ensure `local_dev_path`; clone QEMU; delete old build dir; run `meson subprojects download` despite the task name "Disable downloads"; configure with `--disable-download`; build with `nproc.stdout`; install with sudo.

State and persistence behavior: creates `local_dev_path`, clones/updates `qemu_data`, removes `qemu_build_dir`, builds in the source tree, and installs QEMU into the system prefix. Facts control later tasks.

Dependencies and integration: depends on distro dependency tasks, `num_jobs`, `make`, `local_dev_path`, data path defaults, and the configured QEMU upstream tag. It feeds kdevops VM/workflow execution that needs the built QEMU binary.

Risks: `build_qemu_now` is set true only when `qemu_present.stat is not defined` rather than when the file is absent; after the stat task runs and the binary is missing, this condition may not build as intended. `GIT_SSL_NO_VERIFY=true` weakens clone verification. The "Disable downloads" task actually downloads subprojects before configure disables downloads.

Test signals: test both missing-binary and force-install paths. A missing `qemu_bin_path` with `qemu_build=true` should result in clone/configure/build/install; if not, the `build_qemu_now` condition is faulty.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/codereadyrepo/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/codereadyrepo/defaults/main.yml

Source read: complete file, 6 lines, 155 bytes, sha256 `c22c6b8ca48c6f3f`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/codereadyrepo/defaults/main.yml_research.md`.

Purpose: defaults for selecting/enabling CodeReady Builder or equivalent repositories.

Important APIs/types/functions: `kdevops_enable_terraform` and `kdevops_enable_guestfs` default to false and are used by the task file to choose provider-specific RHEL repository names.

Control flow: no executable behavior.

State and persistence behavior: no direct state mutation; variables influence whether repository enablement commands run.

Dependencies and integration: supports `codereadyrepo/tasks/main.yml` and roles that need packages from CRB/CodeReady, notably guestfs or RHEL cloud provider images.

Risks: defaults may leave `codeready_repo` undefined for RedHat unless guestfs or terraform/provider flags are set.

Test signals: variable resolution tests for RedHat/AWS/Azure/GCE/CentOS/OracleLinux should select the intended repo string.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/codereadyrepo/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/codereadyrepo/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/codereadyrepo/tasks/main.yml

Source read: complete file, 67 lines, 2501 bytes, sha256 `a77ad52f458a5afc`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/codereadyrepo/tasks/main.yml_research.md`.

Purpose: enable the correct CodeReady Builder, CRB, or cloud RHUI repository for non-Fedora RedHat-like systems unless a custom yum repo file is configured.

Important APIs/types/functions: `set_fact codeready_repo`, `ansible.builtin.fail`, and `ansible.builtin.command` invoking `/usr/bin/dnf config-manager --enable {{ codeready_repo }}`.

Control flow: skip Fedora and custom yum repofile hosts; choose repo name for RedHat+guestfs, OracleLinux, CentOS, RedHat+terraform AWS/Azure/GCE; fail if no heuristic matches; enable selected repo and mark changed on success.

State and persistence behavior: mutates dnf repository enablement on the target. The selected repo name persists as an Ansible fact for the play.

Dependencies and integration: relies on `devconfig_custom_yum_repofile`, distribution facts, terraform provider variables, and dnf config-manager availability. It enables packages needed by other roles.

Risks: RedHat without guestfs or recognized terraform provider fails. `devconfig_custom_yum_repofile` must be defined or defaulted elsewhere. Repo names are provider/version/architecture sensitive.

Test signals: matrix dry runs across RedHat bare, AWS, Azure, GCE, CentOS, OracleLinux, and Fedora should show the expected enable or skip/fail behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/codereadyrepo/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/common/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/common/defaults/main.yml

Source read: complete file, 7 lines, 168 bytes, sha256 `8325d12e9b10e149`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/common/defaults/main.yml_research.md`.

Purpose: defaults for the common kdevops role.

Important APIs/types/functions: `kdevops_data`, `kdevops_git`, and `kdevops_git_reset`.

Control flow: no direct tasks; the values control whether `common/tasks/main.yml` refreshes the kdevops checkout and where it lives.

State and persistence behavior: when reset is enabled, the checkout under `/data/kdevops` is created or updated from the configured repository.

Dependencies and integration: common role is included by data partition setup when UID/group inference is enabled and may be used by other roles needing shared user/group facts.

Risks: `kdevops_git_reset=false` means stale local checkout state is preserved by default. Enabling reset with `GIT_SSL_NO_VERIFY` in tasks weakens transport verification.

Test signals: default run should not modify the checkout; enabling reset should update `kdevops_data` from `kdevops_git`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/common/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/common/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/common/tasks/main.yml

Source read: complete file, 89 lines, 2432 bytes, sha256 `22ce1ed2005382cb`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/common/tasks/main.yml_research.md`.

Purpose: common role tasks for optional kdevops checkout reset and user/group inference.

Important APIs/types/functions: optional `include_vars`, `ansible.builtin.git`, `command whoami`, `set_fact`, and `ansible.builtin.getent` for passwd/group lookups.

Control flow: load extra vars; optionally clone/update kdevops with retries when `kdevops_git_reset`; when `infer_uid_and_group`, capture current username, set `target_user`, query passwd and group databases, derive primary gid if no group by username exists, then set `data_user` and `data_group` either from named group or primary gid group.

State and persistence behavior: may update `kdevops_data` checkout. Mostly sets Ansible facts used by partition/filesystem roles for ownership.

Dependencies and integration: used by `create_data_partition` and any role needing correct target ownership. Depends on POSIX `whoami` and getent databases.

Risks: `GIT_SSL_NO_VERIFY=true` weakens clone verification. The group extraction expression for `getent_on_group.values()` is complex and may be brittle across Ansible versions. UID inference is skipped entirely unless `infer_uid_and_group` is defined true.

Test signals: run on hosts where username group exists and where it does not; verify `data_user`/`data_group` facts match expected ownership before creating `/data`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/common/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/compile_dbench/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/compile_dbench/defaults/main.yml

Source read: complete file, 6 lines, 183 bytes, sha256 `3fe74b866bbd25e9`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/compile_dbench/defaults/main.yml_research.md`.

Purpose: defaults for optional dbench source compilation.

Important APIs/types/functions: `compile_dbench`, `dbench_data`, and `dbench_git`.

Control flow: no tasks; defaults are consumed by `compile_dbench/tasks/main.yml`.

State and persistence behavior: enabled runs clone into `{{ data_path }}/dbench` and may install dbench system-wide.

Dependencies and integration: supports filesystem benchmark workflows needing the kdevops dbench fork.

Risks: default false avoids source build; no version pin is provided, so enabled builds track repository default branch.

Test signals: with defaults the clone/build/install tasks should skip; with `compile_dbench=true`, the checkout should appear at `dbench_data`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/compile_dbench/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/compile_dbench/tasks/install-deps/debian/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/compile_dbench/tasks/install-deps/debian/main.yml

Source read: complete file, 51 lines, 992 bytes, sha256 `ebc62a493873c5ae`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/compile_dbench/tasks/install-deps/debian/main.yml_research.md`.

Purpose: Debian dependency setup for compiling dbench.

Important APIs/types/functions: `ansible.builtin.apt` updates cache and installs git/autotools/compiler/make/sed, uuid/quota/acl/aio/attr/gdbm/ssl/xfs/cap/libtool/pkg-config/popt/tirpc/xsltproc/smbclient/iscsi dependencies. A preceding `set_fact` named "Force dbench compilation on Debian" actually sets `compile_dbench: false`.

Control flow: update apt cache, force `compile_dbench` false, then install the dependency list.

State and persistence behavior: changes apt package state and resets the play fact so downstream clone/build tasks do not run on Debian.

Dependencies and integration: imported through `install-deps/main.yml` after including the `pkg` role for variables such as `pkg_libaio`.

Risks: the task name and value conflict: it says force compilation but disables it. Dependencies install even though compilation is disabled, which may be intentional for package-provided dbench or a bug.

Test signals: Debian run should show `compile_dbench` false after this file; downstream compile tasks should skip despite dependencies being installed.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/compile_dbench/tasks/install-deps/debian/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/compile_dbench/tasks/install-deps/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/compile_dbench/tasks/install-deps/main.yml

Source read: complete file, 11 lines, 356 bytes, sha256 `99fad5006889d476`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/compile_dbench/tasks/install-deps/main.yml_research.md`.

Purpose: dependency dispatcher for dbench compilation.

Important APIs/types/functions: `include_role: pkg` and `import_tasks: tasks/install-deps/debian/main.yml` for Debian-family hosts.

Control flow: load the package helper role, then import Debian-specific dependencies only on Debian family.

State and persistence behavior: direct state comes from the pkg role and imported dependency tasks.

Dependencies and integration: called from `compile_dbench/tasks/main.yml`; currently only Debian is supported.

Risks: path uses `tasks/install-deps/debian/main.yml` from within the role task tree, which is less conventional than `debian/main.yml` and depends on Ansible's relative resolution. Non-Debian systems skip all dependency setup.

Test signals: syntax check should confirm the relative import resolves; Debian dry run should include pkg and apt tasks.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/compile_dbench/tasks/install-deps/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/compile_dbench/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/compile_dbench/tasks/main.yml

Source read: complete file, 66 lines, 1478 bytes, sha256 `3b714c459d6099ba`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/compile_dbench/tasks/main.yml_research.md`.

Purpose: optional clone/build/install orchestration for dbench.

Important APIs/types/functions: optional `include_vars`, `import_tasks: install-deps/main.yml`, `ansible.builtin.git`, `ansible.builtin.command` for `autogen.sh`, `configure`, and `{{ num_jobs }}`, `community.general.make`, and privileged `{{ make }} install`.

Control flow: load extra vars; install dependencies; when `compile_dbench` remains true, clone/update dbench, run autotools generation/configure, determine parallel jobs, build, and install.

State and persistence behavior: creates/updates `dbench_data`, leaves build artifacts, and installs binaries/libraries into the system prefix.

Dependencies and integration: depends on pkg/dependency tasks, `num_jobs`, `make`, autotools, and the configured dbench repository.

Risks: Debian dependency file sets `compile_dbench=false`, so the build path may never run on Debian. No version pin and no clone transport hardening are present.

Test signals: explicitly set `compile_dbench=true` and inspect after dependency import; if it flips false, either the role intentionally disables Debian builds or the fact assignment needs correction.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/compile_dbench/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_data_partition/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/create_data_partition/defaults/main.yml

Source read: complete file, 4 lines, 117 bytes, sha256 `e907ecb34ffa53a1`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/create_data_partition/defaults/main.yml_research.md`.

Purpose: defaults for creating the primary kdevops data partition.

Important APIs/types/functions: `kdevops_enable_terraform` and `kdevops_use_declared_hosts`.

Control flow: no tasks; variables are used by `create_data_partition/tasks/main.yml` to decide whether AWS terraform block-device discovery is needed.

State and persistence behavior: no direct mutation.

Dependencies and integration: feeds the wrapper role that calls `create_partition` with data device/filesystem/path/user/group variables.

Risks: defaults avoid terraform-specific mapping; provider runs must set required variables elsewhere.

Test signals: with terraform disabled, the role should proceed directly to `create_partition` using `data_device` values from inventory.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_data_partition/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_data_partition/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/create_data_partition/tasks/main.yml

Source read: complete file, 55 lines, 1985 bytes, sha256 `9c497aeebb751c1b`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/create_data_partition/tasks/main.yml_research.md`.

Purpose: wrapper role that resolves the data device and invokes generic partition creation for the kdevops data filesystem.

Important APIs/types/functions: `include_role: common`, terraform `output -json block_device_map`, `from_json`, `with_dict`, `set_fact data_volume_id/data_device`, and `include_role: create_partition` with mapped `disk_setup_*` vars.

Control flow: optionally infer user/group through common; on AWS terraform, query block-device map on localhost, find `/dev/sdf`, convert the EBS volume id into the NVMe serial naming pattern, scan `ansible_devices` for a matching id link, and override `data_device`; then call `create_partition`.

State and persistence behavior: sets facts for the current role and delegates actual filesystem/mount/permission persistence to `create_partition`.

Dependencies and integration: depends on terraform output layout, AWS NVMe EBS naming, `topdir_path`, `ansible_devices`, and global variables `data_device`, `data_fstype`, `data_label`, `data_fs_opts`, `data_path`, `data_user`, and `data_group`.

Risks: AWS mapping has a FIXME and hard-codes `/dev/sdf`. If volume id matching fails, the role may fall back to an unsafe or unset `data_device`. Terraform command runs once on localhost and assumes current state exists.

Test signals: in AWS terraform inventory, debug `data_volume_id` and resolved `data_device` before formatting; in non-AWS paths, verify the original inventory device reaches `create_partition`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_data_partition/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_nfs_mount/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/create_nfs_mount/defaults/main.yml

Source read: complete file, 6 lines, 170 bytes, sha256 `8198ed5bb5f95e6a`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/create_nfs_mount/defaults/main.yml_research.md`.

Purpose: defaults for mounting an NFS export as the data path.

Important APIs/types/functions: `nfs_mount_options`, `nfs_mounted_on`, `nfs_server_hostname`, and `nfs_server_export`.

Control flow: no tasks; consumed by `create_nfs_mount/tasks/main.yml`.

State and persistence behavior: defaults target `/data` mounted from `kdevops-nfsd:/export`.

Dependencies and integration: supports workflows using shared NFS data storage instead of local disks/tmpfs.

Risks: default hostname assumes a matching inventory/DNS entry. Mount options are plain `defaults`, with no explicit version, retry, or timeout.

Test signals: variable resolution should show the intended server/export before the mount role runs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_nfs_mount/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_nfs_mount/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/create_nfs_mount/tasks/main.yml

Source read: complete file, 51 lines, 1284 bytes, sha256 `1923674688e87f2a`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/create_nfs_mount/tasks/main.yml_research.md`.

Purpose: install NFS client tooling and mount a configured NFS export.

Important APIs/types/functions: optional `include_vars`, `ansible.builtin.package` with distro package map, `command mountpoint -q`, and `ansible.posix.mount` with `state: mounted`.

Control flow: load extra vars; install `nfs-common` on Debian or `nfs-utils` on SUSE/RedHat; inspect whether the mount point is already mounted; mount `{{ nfs_server_hostname }}:{{ nfs_server_export }}` at `{{ nfs_mounted_on }}` with throttle 1 when not mounted.

State and persistence behavior: installs client packages and writes/mounts an NFS entry through Ansible's mount module.

Dependencies and integration: relies on `ansible_os_family` keys matching `Debian`, `Suse`, or `RedHat`; integrates as an alternative storage setup for `/data`.

Risks: the mount condition uses `when: mountpoint_stat != 0` rather than `mountpoint_stat.rc != 0`, which may not behave as intended because the registered result is a dict. Package map key `Suse` may not match all fact spellings.

Test signals: check idempotence: a second run should not remount unnecessarily. Verify the mount task condition evaluates on actual `mountpoint_stat.rc`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_nfs_mount/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_partition/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/create_partition/defaults/main.yml

Source read: complete file, 14 lines, 449 bytes, sha256 `65b2f8190dace395`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/create_partition/defaults/main.yml_research.md`.

Purpose: defaults for generic block device filesystem creation and mounting.

Important APIs/types/functions: `disk_setup_device`, `disk_setup_fstype`, `disk_setup_mount_opts`, `disk_setup_label`, `disk_setup_fs_opts`, `disk_setup_path`, `disk_setup_user`, `disk_setup_group`, `disk_setup_mode`, and `disk_setup_env`.

Control flow: no tasks; consumed by `create_partition/tasks/main.yml`.

State and persistence behavior: defaults describe an XFS filesystem labeled `data` mounted at `/data` with broad sticky permissions.

Dependencies and integration: used by `create_data_partition` and any role needing generic disk formatting/mounting.

Risks: placeholder `disk_setup_device` must be overridden. The default mode `u=rwx,g=rwx,o=rwxt` is permissive and appropriate only for shared data semantics.

Test signals: variable validation should ensure `disk_setup_device` is not left as `/dev/some-block-device` before destructive filesystem tasks run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_partition/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/install-deps/debian/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/install-deps/debian/main.yml

Source read: complete file, 11 lines, 245 bytes, sha256 `0f0b91aabdd546ca`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/install-deps/debian/main.yml_research.md`.

Purpose: Debian-family installation of filesystem creation tools.

Important APIs/types/functions: `ansible.builtin.apt` installs `btrfs-progs`, `e2fsprogs`, and `xfsprogs` with cache update under sudo.

Control flow: a single package task runs when imported for Debian.

State and persistence behavior: changes apt package state so filesystem modules can call mkfs tools.

Dependencies and integration: prerequisite for `community.general.filesystem` creating btrfs/ext/ext/xfs filesystems in `create_partition`.

Risks: no retry; package names are Debian-specific.

Test signals: after running, `mkfs.xfs`, `mkfs.btrfs`, and ext filesystem tools should be in PATH.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/install-deps/debian/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/install-deps/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/install-deps/main.yml

Source read: complete file, 10 lines, 511 bytes, sha256 `16590314d9da8032`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/install-deps/main.yml_research.md`.

Purpose: OS-family dispatcher for partition creation dependencies.

Important APIs/types/functions: `import_tasks` for Debian, SUSE, and RedHat dependency files selected by `ansible_facts['os_family']|lower`.

Control flow: exactly one distro-specific package file should run on supported systems.

State and persistence behavior: no direct mutation; imported files install filesystem tools and may set SUSE facts.

Dependencies and integration: called before destructive or mounting operations in `create_partition/tasks/main.yml`.

Risks: unsupported OS families proceed without installing mkfs tools. Static import paths include `tasks/install-deps/...`, depending on role-relative resolution.

Test signals: syntax check plus per-distro dry runs should verify import path resolution and package-manager selection.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/install-deps/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/install-deps/redhat/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/install-deps/redhat/main.yml

Source read: complete file, 27 lines, 558 bytes, sha256 `7b798efcfd862c3c`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/install-deps/redhat/main.yml_research.md`.

Purpose: Red Hat family installation of base filesystem tools for partition creation.

Important APIs/types/functions: `ansible.builtin.dnf` installs `xfsprogs` and `e2fsprogs` on all RedHat-family systems, and installs `btrfs-progs` with retries only on Fedora.

Control flow: run base package install with cache update; then, if `ansible_distribution == 'Fedora'`, retry btrfs-progs install up to three times.

State and persistence behavior: mutates dnf package state.

Dependencies and integration: prepares `create_partition` to format XFS/ext filesystems everywhere and btrfs on Fedora.

Risks: non-Fedora RedHat systems do not install btrfs-progs, so `disk_setup_fstype=btrfs` can fail. Cache update on every run may slow playbooks.

Test signals: Fedora run should install all three tool families; RHEL/CentOS with btrfs requested should be tested for expected failure or separate repo support.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/install-deps/redhat/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/install-deps/suse/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/install-deps/suse/main.yml

Source read: complete file, 66 lines, 2257 bytes, sha256 `df1a68af45e6ed86`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/install-deps/suse/main.yml_research.md`.

Purpose: SUSE-family filesystem tool dependency setup with legacy SLE repo gating.

Important APIs/types/functions: `set_fact` for SUSE family/version flags and `ansible.builtin.package` installing `xfsprogs`, `e2fsprogs`, and `btrfsprogs` when `repos_present`.

Control flow: classify SLE/Leap/Tumbleweed; set detailed SLE service-pack booleans; clear them on non-SLE; default `repos_present=true`; set it false for SLE10/SLE11; install packages only if repos are present.

State and persistence behavior: records distro facts and changes package state on supported SUSE releases.

Dependencies and integration: mirrors SUSE gating used in other roles and feeds `create_partition`.

Risks: old SLE systems skip package installation but later partition tasks may still run and fail. Package name is `btrfsprogs`, not `btrfs-progs`, which is correct for some SUSE releases but version-sensitive.

Test signals: verify SLE10/11 skip behavior; Leap/Tumbleweed/SLE15 should install mkfs tooling.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/install-deps/suse/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/main.yml

Source read: complete file, 159 lines, 4705 bytes, sha256 `222082ba7a4e87ec`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/main.yml_research.md`.

Purpose: generic filesystem creation, mount, and permission setup for a configured block device/path.

Important APIs/types/functions: optional `include_vars`, `import_tasks: install-deps/main.yml`, `mountpoint -q`, `/etc/fstab` awk/grep shell checks, `lsblk` label and partition inspection, `ansible.builtin.stat`, `community.general.filesystem`, `ansible.posix.mount`, and `ansible.builtin.file`.

Control flow: load vars; install mkfs deps; check whether target path is mounted, present in fstab, and whether any block label matches; stat the device if not already configured; wipe old filesystem if not in fstab/mounted/labeled; inspect partitions; set `part_mounts`; create filesystem when device has no partitions and no matching label/mount; mount by `LABEL="{{ disk_setup_label }}"`; ensure directory permissions.

State and persistence behavior: potentially destructive filesystem wipe/create on `disk_setup_device`, persistent fstab/mount state via `ansible.posix.mount`, and ownership/mode changes on `disk_setup_path`.

Dependencies and integration: used by data partition role and any workflow needing local block storage. Depends on mkfs tools, lsblk output shape, labels, and caller-provided device/path/user/group/fstype.

Risks: destructive operations rely on shell-derived mount/fstab/label checks. `part_mounts_item` is referenced but not looped or defined in this file, making create/mount conditions hard to reason about and possibly broken. Matching any label globally can skip formatting even if the label is on the wrong device.

Test signals: run in a disposable VM for cases: fresh whole disk, already mounted path, fstab entry present, existing label, device absent, and device with partitions. Confirm idempotent second run and correct fstab entry.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_tmpfs/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/create_tmpfs/defaults/main.yml

Source read: complete file, 7 lines, 181 bytes, sha256 `9e72518485a94507`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/create_tmpfs/defaults/main.yml_research.md`.

Purpose: defaults for mounting tmpfs as a data path.

Important APIs/types/functions: `tmpfs_mount_options`, `tmpfs_mounted_on`, `tmpfs_user`, `tmpfs_group`, and `tmpfs_mode`.

Control flow: no tasks; consumed by `create_tmpfs/tasks/main.yml`.

State and persistence behavior: defaults describe a tmpfs mounted at `/data` with root ownership and sticky world-writable style mode.

Dependencies and integration: supports workflows where ephemeral memory-backed data storage is desired.

Risks: default mount options do not set size, so tmpfs size follows system defaults and can pressure memory/swap.

Test signals: variable overrides should set size/security options when workloads need bounded memory use.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_tmpfs/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_tmpfs/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/create_tmpfs/tasks/main.yml

Source read: complete file, 56 lines, 1467 bytes, sha256 `a5c8890df87312b9`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/create_tmpfs/tasks/main.yml_research.md`.

Purpose: mount a tmpfs at the configured path and set its permissions.

Important APIs/types/functions: optional `include_vars`, `command mountpoint -q`, shell `/etc/fstab` check, `ansible.posix.mount`, and `ansible.builtin.file`.

Control flow: load extra vars; inspect current mountpoint; inspect fstab; mount tmpfs with throttle 1 when not mounted; then set owner/group/mode on the mounted path.

State and persistence behavior: creates a persistent mount entry through `ansible.posix.mount` and changes directory metadata. Data stored on tmpfs is non-persistent across reboot.

Dependencies and integration: alternative storage setup for workflows that do not need durable `/data`.

Risks: mount condition uses `when: mountpoint_stat != 0` rather than `mountpoint_stat.rc != 0`, likely making idempotence unreliable. The fstab check result is registered but not used.

Test signals: first run should mount tmpfs; second run should be idempotent. Validate the condition against the registered rc field.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_tmpfs/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/cxl/defaults/main.yml

Source read: complete file, 9 lines, 304 bytes, sha256 `c3387be4d42d6362`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/cxl/defaults/main.yml_research.md`.

Purpose: defaults for the CXL/ndctl workflow role.

Important APIs/types/functions: `ndctl_git`, `ndctl_data`, `ndctl_version`, `ndctl_meson_testlog`, `kdevops_run_cxl_tests`, `kdevops_enable_cxl_dcd`, and `kdevops_qmp_str`.

Control flow: no direct tasks; consumed by CXL build/setup/test tasks.

State and persistence behavior: enabled role clones ndctl under `{{ data_path }}/ndctl`, builds it, may convert CXL/DAX memory to system RAM, and may collect Meson logs.

Dependencies and integration: integrates with QEMU CXL devices, QMP dynamic capacity commands, ndctl/daxctl/cxl utilities, kernel CXL modules, and kdevops result collection.

Risks: `ndctl_version` default `pending` must exist in the repository. Dynamic capacity and memory onlining are destructive/host-stateful operations.

Test signals: variable resolution should confirm whether classic CXL memory or DCD path is selected and whether test execution is enabled.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/cxl-create-dc-region/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/cxl/tasks/cxl-create-dc-region/main.yml

Source read: complete file, 20 lines, 1041 bytes, sha256 `94c45a6e7e8721f1`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/cxl/tasks/cxl-create-dc-region/main.yml_research.md`.

Purpose: create a CXL dynamic-capacity region through sysfs before adding dynamic capacity extents.

Important APIs/types/functions: privileged `ansible.builtin.shell` writing to `/sys/bus/cxl/devices/...` files, `cxl list -uR`, and debug output.

Control flow: write `create_dc_region`, configure interleave granularity/ways, set decoder mode `dc0`, set DPA and region size, bind target, commit the region, bind it to the CXL region driver, then display `cxl list -uR`.

State and persistence behavior: mutates live kernel CXL sysfs state by creating and binding a region. This is runtime hardware/VM state, not a config file.

Dependencies and integration: included from `cxl/tasks/main.yml` when `kdevops_enable_cxl_dcd` is true. Assumes decoder names `decoder0.0` and `decoder2.0` and available cxl CLI.

Risks: hard-coded sysfs paths, sizes, region id, and decoder topology make this fragile across QEMU/kernel versions. The long shell string has no `set -e`, so partial failures may go unnoticed.

Test signals: `cxl list -uR` should show a committed DC region with the expected size/target; sysfs writes should fail loudly in negative topology tests.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/cxl-create-dc-region/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/cxl-dcd-setup/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/cxl/tasks/cxl-dcd-setup/main.yml

Source read: complete file, 65 lines, 2079 bytes, sha256 `bfed3af047c6bbb2`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/cxl/tasks/cxl-dcd-setup/main.yml_research.md`.

Purpose: add QEMU CXL dynamic capacity extents, create a DAX device for the region, reconfigure it as system RAM, and show resulting memory.

Important APIs/types/functions: delegated localhost shell building QMP JSON and sending it with `ncat`, `ls` of CXL sysfs, `daxctl create-device`, `daxctl reconfigure-device --mode=system-ram --no-online`, `daxctl online-memory`, `lsmem`, and debug outputs.

Control flow: parse QMP port from `qmp_port_str`; send `qmp_capabilities` and `cxl-add-dynamic-capacity`; show region sysfs; create DAX device for `region0`; list `/dev/dax*`; convert `dax0.1` to system RAM and online it; display memory layout.

State and persistence behavior: mutates QEMU device state, kernel CXL region state, DAX device state, and online memory state. Effects last for the VM runtime.

Dependencies and integration: included when DCD is enabled, after the DC region exists. Requires QMP listener, `ncat`, daxctl, kernel CXL DCD support, and expected device names.

Risks: QMP JSON is manually shell-quoted and sizes are hard-coded. `dax0.1` and `region0` assumptions can break if device numbering changes. Some commands use shell without robust failure checking.

Test signals: QMP command should report success, `daxctl list` or `/dev/dax*` should show the new device, `lsmem` should show newly onlined memory, and repeated runs should be tested for idempotence failures.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/cxl-dcd-setup/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/cxl-mem-setup/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/cxl/tasks/cxl-mem-setup/main.yml

Source read: complete file, 21 lines, 692 bytes, sha256 `68f3a1bd853044c0`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/cxl/tasks/cxl-mem-setup/main.yml_research.md`.

Purpose: configure ordinary CXL memory as a DAX namespace, convert it to system RAM, and online it.

Important APIs/types/functions: `cxl create-region -m -d decoder0.0 -w 1 mem0 -s 256M`, `ndctl create-namespace -m dax -r region0`, `daxctl reconfigure-device --mode=system-ram --no-online dax0.0`, and `daxctl online-memory dax0.0`.

Control flow: create CXL region, create DAX namespace, reconfigure the dax device as system RAM without auto-online, then online memory explicitly.

State and persistence behavior: mutates CXL region/namespace and memory hotplug state in the running system.

Dependencies and integration: included from CXL main when `kdevops_enable_cxl_dcd` is false. Assumes decoder `decoder0.0`, endpoint `mem0`, `region0`, and `dax0.0`.

Risks: hard-coded topology/device names and no idempotence guards mean reruns can fail after the region or namespace already exists. Commands are privileged and alter memory layout.

Test signals: `cxl list`, `ndctl list`, `daxctl list`, and `lsmem` should reflect region0/dax0.0 and online memory after the task.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/cxl-mem-setup/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/debian/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/debian/main.yml

Source read: complete file, 33 lines, 646 bytes, sha256 `ef8181cb5280dcf1`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/debian/main.yml_research.md`.

Purpose: Debian-family dependency setup for building ndctl/cxl tooling.

Important APIs/types/functions: `ansible.builtin.apt` updates cache and installs git, meson, gcc, pkg-config, cmake, kmod/udev/uuid/json-c/keyutils/iniparser/traceevent/tracefs development headers, asciidoctor, bash-completion, and jq.

Control flow: update apt cache, then install the package list.

State and persistence behavior: changes apt package state on the target.

Dependencies and integration: supports `meson setup build`, ndctl/cxl compilation, documentation, shell completion, JSON handling, and trace libraries in the CXL main role.

Risks: package names target modern Debian/Ubuntu; older releases may lack tracefs/traceevent dev packages. No retry is configured.

Test signals: after installation, `meson setup build` in ndctl should find kmod, udev, uuid, json-c, keyutils, iniparser, traceevent, and tracefs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/debian/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/generic.yml -->
# sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/generic.yml

Source read: complete file, 9 lines, 254 bytes, sha256 `12c4933fb4f0d00d`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/generic.yml_research.md`.

Purpose: install CXL workflow packages common to all supported distributions.

Important APIs/types/functions: `ansible.builtin.package` installs `numactl` under sudo.

Control flow: single package task imported after distro-specific CXL dependencies.

State and persistence behavior: changes package state by ensuring numactl is installed.

Dependencies and integration: useful for memory locality inspection/testing after CXL/DAX memory is onlined.

Risks: package name is assumed common across supported distros.

Test signals: `numactl --hardware` should work after the dependency phase.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/generic.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/main.yml

Source read: complete file, 13 lines, 606 bytes, sha256 `1ebb1168b057ad03`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/main.yml_research.md`.

Purpose: OS-family dispatcher for CXL/ndctl dependency installation, plus common package installation.

Important APIs/types/functions: `import_tasks` for Debian, SUSE, RedHat, then `import_tasks: generic.yml`.

Control flow: import the distro-specific dependency file based on `ansible_facts['os_family']|lower`, then always import common dependencies.

State and persistence behavior: no direct mutation except imported package installs and facts.

Dependencies and integration: called at the beginning of the CXL main role before ndctl clone/build and CXL setup.

Risks: unsupported OS families still run generic `numactl` install but skip ndctl build dependencies. Static import path uses `tasks/install-deps/...`, requiring role-relative resolution.

Test signals: distro dry runs should show exactly one distro file plus generic file.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/redhat/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/redhat/main.yml

Source read: complete file, 27 lines, 583 bytes, sha256 `3bf582a141b6ab73`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/redhat/main.yml_research.md`.

Purpose: Red Hat family build dependency installation for ndctl/cxl.

Important APIs/types/functions: `ansible.builtin.dnf` installs git-core, meson, cmake, gcc, pkgconf, kmod/systemd/uuid/json-c/keyutils/iniparser/traceevent/tracefs development packages, asciidoctor, bash-completion, and jq.

Control flow: one dnf task with cache update ensures the package list is present.

State and persistence behavior: changes rpm package state.

Dependencies and integration: prepares for ndctl Meson build in `cxl/tasks/main.yml`.

Risks: package availability may require CRB/CodeReady/EPEL depending on release. Both `uuid-devel` and `libuuid-devel` are listed, which can be redundant or release-dependent.

Test signals: ndctl `meson setup build` should find all required dependencies on RHEL/CentOS/Fedora-like targets.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/redhat/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/suse/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/suse/main.yml

Source read: complete file, 83 lines, 2630 bytes, sha256 `5df178e38ecbb149`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/suse/main.yml_research.md`.

Purpose: SUSE-family build dependency installation for ndctl/cxl with old SLE repo gating.

Important APIs/types/functions: `set_fact` for distro/service-pack flags and `community.general.zypper` installing git-core, meson, gcc, pkg-config, uuid/kmod/udev/json-c/asciidoctor/keyutils/iniparser/bash-completion/jq/traceevent/tracefs packages with `replacefiles: true`.

Control flow: classify SUSE variant and SLE versions; default repos present; disable repos for SLE10/SLE11; install dependency list when repos are present.

State and persistence behavior: records facts and changes zypper package state.

Dependencies and integration: prepares ndctl build for SUSE systems in the CXL workflow.

Risks: ruby/asciidoctor package name is version-specific (`ruby3.1-rubygem-asciidoctor`). Older SLE skips deps but later ndctl build tasks may still execute and fail.

Test signals: Leap/Tumbleweed/SLE15 should install dependencies and pass ndctl Meson setup; SLE10/11 should be treated as unsupported before build.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/suse/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/cxl/tasks/main.yml

Source read: complete file, 218 lines, 6279 bytes, sha256 `be88170abfbb06b7`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/cxl/tasks/main.yml_research.md`.

Purpose: full CXL workflow orchestration: build/install ndctl, configure CXL memory or dynamic capacity, optionally run CXL tests, and collect Meson test logs.

Important APIs/types/functions: optional `include_vars`, dependency include, `create_data_partition`, `git`, Meson setup/configure/compile/install commands, includes for `cxl-mem-setup`, `cxl-create-dc-region`, and `cxl-dcd-setup`, `uname -r`, `set_fact` result paths, `modprobe configfs/cxl_test`, `sysctl kernel.printk`, `meson test -C build --suite cxl`, `find`, and `fetch`.

Control flow: load vars, install deps, ensure data partition, clone ndctl, configure/build/install with destructive tests enabled, choose classic CXL memory or DCD setup, compute result paths and kernel version, remove prior local result directory, write last-kernel marker, optionally load modules and run CXL Meson tests, find test logs on targets, and fetch them to local workflow results.

State and persistence behavior: updates ndctl checkout/build tree, installs ndctl/cxl/daxctl tools, mutates CXL/DAX/system RAM state, changes kernel printk, loads/unloads modules, removes local result directories, and fetches logs.

Dependencies and integration: depends on QEMU CXL topology, CXL kernel config/modules, ndctl Meson project, data partition role, localhost result tree, and workflow tags for prep/run/copy phases.

Risks: ndctl build always runs, regardless of `kdevops_run_cxl_tests`. CXL setup tasks hard-code device names and are not idempotent. `last_kernel` is derived from `stdout_lines` with regex string cleanup, which is brittle. Test task uses `ignore_errors` and `no_log`, so failures can be easy to miss except via fetched logs.

Test signals: verify installed `cxl/ndctl/daxctl`, successful memory setup (`lsmem`), optional `cxl_test` module load/unload, presence of `testlog.txt`, and fetched results under `workflows/cxl/results/last-run/{{ last_kernel }}`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/devconfig/defaults/main.yml

Source read: complete file, 66 lines, 2188 bytes, sha256 `9b9d5672ac7c6bd1`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/devconfig/defaults/main.yml_research.md`.

Purpose: defaults for development host customization, repository setup, sysctl tuning, journal/timesync options, custom repos/packages, guestfs/source-copy behavior, and workflow flags.

Important APIs/types/functions: variables cover home/git/bash config paths, repo refresh/upgrade/kdevtools booleans, SUSE registration/KOTD/systemd watchdog settings, sysctl overcommit settings, RHEL org/activation, CLI install, journal remote, timesyncd/NTP provider choices, guestfs copy flags, Debian hop1 mirror tracking, unattended upgrades, inferred user/group, terraform/declared hosts, and custom repo/package comma-separated strings.

Control flow: no executable tasks; these defaults are consumed by multiple devconfig task files.

State and persistence behavior: defaults govern possible mutations to user dotfiles, package repositories, system update state, sysctl config, systemd services, package installs, and source copies.

Dependencies and integration: central variable surface for devconfig role, apt mirror repair, SUSE repo scripts, RedHat custom repos/packages, DataCrunch ML setup, guestfs, terraform, and workflow bootstrap.

Risks: many booleans default false, so feature tasks must explicitly enable them. Sensitive RHEL registration values default empty. Custom repo/package vars are strings requiring comma splitting and non-empty validation.

Test signals: role-level variable dump should confirm only intended devconfig features are enabled for a given inventory.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/scripts/add-suse-repo-if-not-found.sh -->
# sources/test-tools/kdevops/playbooks/roles/devconfig/scripts/add-suse-repo-if-not-found.sh

Source read: complete file, 18 lines, 371 bytes, sha256 `b84c26e677669093`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/devconfig/scripts/add-suse-repo-if-not-found.sh_research.md`.

Purpose: helper shell script to ensure a SUSE zypper repository exists and is enabled, while removing existing YaST-related repositories first.

Important APIs/types/functions: positional args `REPO_URL` and `REPO_NAME`; `zypper lr -d`, `grep yast2`, `awk`, `zypper rr`, `zypper mr -e`, `zypper ar -f -c`, and `zypper --non-interactive --gpg-auto-import-keys refresh`.

Control flow: collect repo ids whose detailed listing contains `yast2`; remove each; try enabling the requested repo; exit success if enable works; otherwise add the repo with refresh/check enabled and refresh it.

State and persistence behavior: mutates zypper repository configuration and refresh metadata.

Dependencies and integration: likely called from devconfig SUSE repo setup tasks to add kernel/tooling repos only if missing.

Risks: unquoted variables and shell word splitting can break URLs/names with spaces. Removing every repo matching `yast2` is broad. Output redirection order `2>&1 > /dev/null` leaves stderr not fully suppressed as likely intended.

Test signals: run on disposable SUSE images with existing repo, missing repo, and YaST repos present; verify only intended repos are removed and the target repo is enabled/refreshed.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/scripts/add-suse-repo-if-not-found.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/scripts/prepare_suse_repos.sh -->
# sources/test-tools/kdevops/playbooks/roles/devconfig/scripts/prepare_suse_repos.sh

Source read: complete file, 89 lines, 2210 bytes, sha256 `d71d7057bb99d0a7`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/devconfig/scripts/prepare_suse_repos.sh_research.md`.

Purpose: SUSE repository preparation and optional SLE/SLED registration script.

Important APIs/types/functions: sources `/etc/os-release`; parses `--register-system-code`; checks root via `id -u`; uses `SUSEConnect` for base registration and SLE 15 SP2/SP3/SP4 desktop/development modules; optionally disables NVIDIA repo on SLED; runs `zypper --non-interactive --gpg-auto-import-keys refresh` or plain refresh.

Control flow: parse args; require root; distinguish SLE/SLED from openSUSE by filtering `ID=` lines; if registering, call SUSEConnect with reg code, add modules for known service packs on success, disable NVIDIA repo for SLED, then refresh repos; openSUSE path simply refreshes.

State and persistence behavior: registers the system, enables SUSE modules, disables selected NVIDIA repo, and refreshes zypper repository metadata.

Dependencies and integration: used by devconfig SUSE prep where private registration code may be supplied. Depends on `/etc/os-release`, `SUSEConnect`, zypper, and network access.

Risks: argument parser uses `while [[ ${#1} -gt 0 ]]`, which tests length of the first arg rather than arg count and is unusual. Several variables are unquoted. The SLE/openSUSE detection via `grep '^ID=' | sed '/opensuse/d'` is brittle. Unknown versions skip module enablement silently.

Test signals: test `--help`, non-root failure, openSUSE refresh path, SLES registration success/failure, SLED NVIDIA repo disable, and SP2/SP3/SP4 module enablement.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/scripts/prepare_suse_repos.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/check-apt-mirrors.yml -->
# sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/check-apt-mirrors.yml

Source read: complete file, 214 lines, 7690 bytes, sha256 `60ecba12e52952fc`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/check-apt-mirrors.yml_research.md`.

Purpose: detect and repair Debian testing APT mirror configuration, preferring a local hop1 mirror when available and falling back to official DEB822 sources when the current mirror is unreachable.

Important APIs/types/functions: delegated localhost shell calls to `scripts/get-distro-has-hop-count-sources.sh`, grep/awk parsing of DEB822 and legacy sources, `set_fact`, `stat`, `wait_for` port 80 checks, `copy` backups, `template` for `debian-hop1-mirror.sources` and `debian-testing-fallback.sources`, `file` removal of legacy sources.list, `apt update_cache`, and debug messages.

Control flow: detect hop1 mirror on control host; parse host/path; inspect target DEB822 vs legacy apt sources; parse current mirror host; check current mirror connectivity; if hop1 is available and reachable, back up sources, template hop1 DEB822 sources, remove legacy list if migrating, update apt; if current mirror failed and no reachable hop1 path is active, back up sources and install official fallback DEB822 sources.

State and persistence behavior: may rewrite `/etc/apt/sources.list.d/debian.sources`, remove `/etc/apt/sources.list`, create `.backup` files, and refresh apt cache.

Dependencies and integration: tied to Debian testing/trixie comments, devconfig mirror maintenance, templates in the role, and control-host mirror discovery script.

Risks: comments say only Debian testing, but this file has no explicit distribution/version guard internally. Registered variables for skipped tasks can be undefined; some `when` expressions assume `.stdout` fields. Migrating to DEB822 removes legacy sources, which is persistent and can surprise users.

Test signals: scenarios for DEB822 current mirror reachable, legacy current mirror reachable, current mirror unreachable with reachable hop1, unreachable hop1 fallback, missing source files, and non-Debian guarded caller behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/check-apt-mirrors.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/config-custom-repos-and-packages/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/config-custom-repos-and-packages/main.yml

Source read: complete file, 6 lines, 194 bytes, sha256 `b2b019b08a5390bc`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/config-custom-repos-and-packages/main.yml_research.md`.

Purpose: dispatcher for custom repository and package installation tasks in devconfig.

Important APIs/types/functions: `ansible.builtin.import_tasks: redhat/main.yml` gated by `ansible_facts['os_family']|lower == 'redhat'`.

Control flow: only RedHat-family hosts run custom repo/package setup.

State and persistence behavior: no direct mutation; imported task copies repo files and installs packages.

Dependencies and integration: called by devconfig when custom repo/package variables are configured.

Risks: Debian/SUSE custom repo/package vars are ignored by this dispatcher. Static import can expose syntax errors even when skipped.

Test signals: RedHat dry run should include copy/dnf tasks when variables are non-empty; non-RedHat should skip.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/config-custom-repos-and-packages/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/config-custom-repos-and-packages/redhat/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/config-custom-repos-and-packages/redhat/main.yml

Source read: complete file, 27 lines, 731 bytes, sha256 `5d54794d10ec1cf7`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/config-custom-repos-and-packages/redhat/main.yml_research.md`.

Purpose: RedHat-family implementation for installing custom yum/dnf repository files and packages.

Important APIs/types/functions: `ansible.builtin.copy` copies each repo file to `/etc/yum.repos.d/{{ basename }}` with root ownership and 0644 mode; `ansible.builtin.dnf` installs each custom package with retries until rc 0. Inputs are comma-split `kdevops_devconfig_custom_repos` and `kdevops_devconfig_custom_packages`.

Control flow: if custom repos string length is greater than 1 after trim, iterate over comma-separated paths and copy them; if custom packages string length is greater than 1, iterate package names and dnf install with retry.

State and persistence behavior: writes repo files into `/etc/yum.repos.d` and mutates rpm package state.

Dependencies and integration: supports devconfig extensibility for RedHat-like images without changing core roles.

Risks: comma splitting has no whitespace cleanup per item, so values with spaces can fail. `copy src` reads from the controller, not target. Package task does not set `state: present` explicitly, relying on module default behavior.

Test signals: provide two repo files and packages with whitespace variations; verify copied basenames, dnf repo visibility, retry behavior, and idempotent second run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/config-custom-repos-and-packages/redhat/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/datacrunch_ml.yml -->
# sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/datacrunch_ml.yml

Source read: complete file, 111 lines, 3095 bytes, sha256 `4a764476cadcc953`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/datacrunch_ml.yml_research.md`.

Purpose: DataCrunch-specific machine-learning development bootstrap for Debian-family instances.

Important APIs/types/functions: `ansible.builtin.apt` dist-upgrade and package install, `get_url` for a pinned `uv-installer.sh` checksum, `command` for installer and venv creation, `ansible.builtin.pip` for PyTorch, shell `modprobe -r` NVIDIA modules, `community.general.modprobe`, `community.general.npm` installing `@anthropic-ai/claude-code`, `copy` to `/etc/motd`, and `lineinfile` auto-activating the venv.

Control flow: upgrade Debian packages; install development/ML dependencies; download/verify/run/remove uv installer; create `~/.venv`; install torch into it; unload and reload NVIDIA kernel module stack; install Claude Code globally via npm; write MOTD; append venv activation to `.bashrc`.

State and persistence behavior: heavily mutates system package state, user home, Python virtualenv, kernel module state, global npm packages, `/etc/motd`, and shell startup behavior.

Dependencies and integration: tailored to DataCrunch GPU instances, Debian package names, Python 3.12 venv, npm, NVIDIA kernel modules, uv release assets, and PyTorch package availability.

Risks: `apt upgrade: dist` is broad. uv checksum/version must stay aligned. PyTorch install has no CUDA index selection, so installed wheel may not match GPU needs. Unloading NVIDIA modules can disrupt active workloads. Auto-sourcing venv in `.bashrc` affects all interactive shells.

Test signals: on a fresh DataCrunch Debian instance, verify package upgrade success, checksum validation, `uv` installed, venv activation, `python -c 'import torch'`, `nvidia-smi` after module reload, npm global command availability, and idempotent rerun behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/datacrunch_ml.yml -->
