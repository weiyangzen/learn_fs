# Group Research: group_1149_mdadm_sources_block_storage_mdadm_github_dependabot_yml_sources_blo_77cbba75d5d5

Scope checked against `Docs/research_subset_a.md`: this group belongs to the included `sources/block-storage/mdadm` source tree. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/.github/dependabot.yml -->
# File Research: sources/block-storage/mdadm/.github/dependabot.yml

## Purpose
This is a minimal Dependabot configuration for the mdadm GitHub repository. It enables Dependabot version checks for GitHub Actions workflows.

## Behavior
- Uses Dependabot config `version: 2`.
- Defines one update entry for `package-ecosystem: "github-actions"`.
- Scans the repository root directory `/`.
- Schedules checks daily.

## Integration Notes
The file affects only GitHub-hosted dependency automation for workflow action versions. It has no direct runtime or build impact on mdadm itself.

## Risks and Maintenance Notes
Because this tracks GitHub Actions actions from the repository root, changes in `.github/workflows/*` action versions can be proposed automatically. There are no grouping, ignore, or target-branch policies in this file, so all default Dependabot behavior applies.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/.github/dependabot.yml -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/.github/tools/.checkpatch.conf -->
# File Research: sources/block-storage/mdadm/.github/tools/.checkpatch.conf

## Purpose
This file configures the `checkpatch` review job used by the mdadm GitHub Actions workflow.

## Behavior
- Disables git tree assumptions with `--no-tree`.
- Shows issue types with `--show-types`.
- Excludes `.github`, `clustermd_tests`, `documentation`, `misc`, `systemd`, and `tests` from checkpatch review.
- Ignores `FILE_PATH_CHANGES`, `EMAIL_SUBJECT`, and `NEW_TYPEDEFS`.

## Integration Notes
The review workflow moves this file into the repository root before invoking `webispy/checkpatch-action@v9`. The exclusions focus style review on main source areas while avoiding generated, test, documentation, and infrastructure paths.

## Risks and Maintenance Notes
Ignoring `NEW_TYPEDEFS` is a project style choice that permits typedef additions without CI failure. Excluding `.github` means workflow and tool scripts are not linted by this checkpatch pass.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/.github/tools/.checkpatch.conf -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/.github/tools/install_ubuntu_packages.sh -->
# File Research: sources/block-storage/mdadm/.github/tools/install_ubuntu_packages.sh

## Purpose
This helper script prepares Ubuntu GitHub Actions runners for the mdadm review build matrix.

## Behavior
- Reads `VERSION_CODENAME` from `/etc/os-release`.
- Adds the matching Ubuntu `main universe` archive repository for `amd64`.
- Installs the GCC version passed as the first argument, using package name `gcc-$1`.
- Installs common build/review dependencies: `make`, `gcc`, `libudev-dev`, and `devscripts`.
- Uses `--no-upgrade`, `--no-install-recommends`, and `--no-install-suggests` to limit package churn.

## Integration Notes
`review.yml` calls this script for each compiler version in the matrix. `devscripts` supplies tools such as `hardening-check`, which the workflow runs after compilation.

## Risks and Maintenance Notes
The script assumes an Ubuntu-like environment with `add-apt-repository`, `sudo`, and `apt-get`. It interpolates the first argument into a package name without validation; in this controlled workflow context the input is the fixed compiler matrix.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/.github/tools/install_ubuntu_packages.sh -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/.github/tools/run_mdadm_tests.sh -->
# File Research: sources/block-storage/mdadm/.github/tools/run_mdadm_tests.sh

## Purpose
This helper script builds, installs, and runs the mdadm test suite inside the self-hosted/Vagrant test environment.

## Behavior
- Runs `sudo make clean`, then builds with `sudo make -j$(nproc)`.
- Exits immediately with an error message if build or install fails.
- Installs with `sudo make install`.
- Stops active md arrays with `sudo mdadm -Ss`.
- Runs `sudo ./test setup`.
- Executes the test harness with skipped known-problem and expensive modes: `--skip-broken`, `--no-error`, `--disable-integrity`, `--disable-multipath`, `--disable-linear`, `--keep-going`, and `--skip-bigcase`.
- Captures the test return code, runs `sudo ./test cleanup`, and exits with the original test status.

## Integration Notes
`.github/workflows/tests.yml` invokes this script through `vagrant ssh` from a self-hosted runner. The script intentionally cleans up after the test run even when tests fail.

## Risks and Maintenance Notes
The script uses privileged build, install, array stop, setup, test, and cleanup commands. It is appropriate for disposable CI VMs, not a developer workstation with important active md arrays.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/.github/tools/run_mdadm_tests.sh -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/.github/workflows/mdadm-test.yml -->
# File Research: sources/block-storage/mdadm/.github/workflows/mdadm-test.yml

## Purpose
This GitHub Actions workflow builds mdadm and runs the test harness on GitHub-hosted Ubuntu runners.

## Behavior
- Named `mdadm test`.
- Runs on pushes to branch `test_on_push`, pull requests to branch `test_on_pr`, and manual `workflow_dispatch`.
- Path filters include top-level C and header files, `tests/*`, `test`, and this workflow file.
- Checks out the repository with full history.
- Installs `make`, `gcc`, and `libudev-dev`.
- Builds with `make -j$(nproc) BINDIR=/usr/sbin`.
- Installs mdadm binaries with `sudo make BINDIR=/usr/sbin install-bin`.
- Prints `mdadm --version`.
- Rewrites the test harness `targetdir` from `/var/tmp` to `/mnt/tmp`, creates that directory, and runs tests under `sudo`.
- Uploads `/mnt/tmp/*.log` as `mdadm-failed-test-logs`.
- Runs tests with `continue-on-error: true`, then explicitly fails the job if the test step outcome was not success.

## Integration Notes
This workflow is separate from the main `tests.yml` self-hosted path. It gives a GitHub-hosted smoke/integration test route with reduced test modes: integrity, multipath, and linear are disabled.

## Risks and Maintenance Notes
The branch filters are nonstandard (`test_on_push`, `test_on_pr`), so the workflow does not run for ordinary branches unless repository policy uses those branch names. Artifact upload runs unconditionally after the test step, so missing logs may depend on action behavior.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/.github/workflows/mdadm-test.yml -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/.github/workflows/review.yml -->
# File Research: sources/block-storage/mdadm/.github/workflows/review.yml

## Purpose
This workflow performs pull-request review checks: compiler matrix builds, hardening checks, and checkpatch review.

## Behavior
- Runs on every pull request.
- Sets `cflags: -Werror` in the workflow environment.
- The `make` job runs on `ubuntu-24.04` across GCC versions 9 through 14.
- For each compiler version it installs packages through `.github/tools/install_ubuntu_packages.sh`.
- Verifies the selected compiler with `gcc-N --version`.
- Builds repeatedly with different `CXFLAGS`: `-DEBUG`, `-DEBIAN`, `-USE_PTHREADS`, and `-DNO_LIBUDEV`, cleaning between variants.
- Performs a normal build, then runs `hardening-check mdadm` and `hardening-check mdmon`.
- The `checkpatch` job checks out the pull request head SHA with full history, moves `.github/tools/.checkpatch.conf` to the repository root, and runs `webispy/checkpatch-action@v9`.

## Integration Notes
The build matrix exercises feature/preprocessor combinations that affect mdadm portability and packaging. `devscripts` from the install helper supplies `hardening-check`.

## Risks and Maintenance Notes
The `CXFLAGS=-DEBUG`, `CXFLAGS=-DEBIAN`, and `CXFLAGS=-USE_PTHREADS` values are notable because typical C preprocessor defines use `-D...`; this may be intentional project makefile syntax or a latent workflow issue. The workflow depends on old GCC packages being installable for the current Ubuntu codename.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/.github/workflows/review.yml -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/.github/workflows/tests.yml -->
# File Research: sources/block-storage/mdadm/.github/workflows/tests.yml

## Purpose
This workflow defines the heavier upstream mdadm test run on self-hosted infrastructure.

## Behavior
- Runs on pull requests touching top-level C/header files, tests, `test`, and GitHub workflow/tooling files.
- The main `upstream_tests` job is currently disabled with `if: ${{ github.repository == 'disabled' }}` and a comment that Intel hosted runners are down.
- When enabled, it runs on a self-hosted runner with a 150-minute timeout.
- Uses Vagrant to restore a clean VM snapshot, start the VM, set UTC time, restart time synchronization, and print the kernel version.
- Exports `RUNNER_NAME` into the GitHub environment.
- Runs `.github/tools/run_mdadm_tests.sh` inside the VM at `/home/vagrant/host/mdadm`.
- On failure, moves `/var/tmp/*.log` from the VM into host logs and uploads artifacts from runner-specific paths for `inspur5` or `inspur5-2`.
- Cleans copied logs after upload and explicitly fails the job if testing failed.
- A dependent `cleanup` job halts the VM with `vagrant halt`.

## Integration Notes
This workflow is tied to specific self-hosted runner filesystem layouts and Vagrant snapshots. It is the CI path that exercises the project’s privileged test harness in a VM rather than directly on the GitHub runner.

## Risks and Maintenance Notes
The main job is disabled by an always-false repository check, which also means the dependent cleanup job will not normally run. Runner names and artifact paths are hard-coded, so adding or renaming self-hosted runners requires workflow edits.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/.github/workflows/tests.yml -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/Assemble.c -->
# File Research: sources/block-storage/mdadm/Assemble.c

## Purpose
`Assemble.c` implements mdadm array assembly: discovering member devices, matching metadata identity, merging with partially assembled arrays, updating superblocks when requested, adding disks to the kernel md device, and starting arrays or container subarrays.

## Major Entry Points
- `Assemble()` is the top-level implementation for assembling a native md array or dispatching container member assembly.
- `assemble_container_content()` assembles and activates a member array described by external/container metadata.
- `select_devices()` scans candidate devices, loads metadata, applies identity matching, handles containers, and marks candidate devices for use.
- `load_devices()` rereads selected devices, optionally updates metadata, records disk roles/events, and builds the best-device table.
- `force_array()` implements `--force` event-count promotion for degraded arrays when enough safe devices are not otherwise available.
- `start_array()` sets kernel array metadata, adds selected disks, and starts or leaves the array assembled depending on policy.

## Core Control Flow
Assembly begins by requiring either explicit devices or enough identity information such as UUID, name, super-minor, member/container, or configured device filters. If metadata type was specified, it resolves a matching supertype. Without an explicit device list it uses configured devices from mdadm configuration.

`select_devices()` walks candidates and rejects devices that fail block-device checks, cannot be opened, do not contain recognizable metadata, conflict with explicit `devices=` or `container=`, are disabled by auto-assembly metadata policy, have mismatched UUID/name/level/raid-disk count, or are already assembled. Containers are handled specially: the code loads container metadata, scans contained member arrays, rejects busy or blocked members, and returns the matching member content rather than ordinary disk content.

After selection, `Assemble()` locks the mdadm map file and checks whether the array UUID already has a partially assembled md device. If so, it merges pre-existing sysfs devices into the device list and opens that md device. Otherwise it chooses a trusted name based on homehost, configuration, metadata, and command-line context, then creates a new md device.

For native arrays, `load_devices()` rereads metadata under exclusive open where needed, applies requested `--update` operations, stores updated superblocks, identifies the most recent active member by event count, and maps roles to best slots. It also detects suspicious duplicate 0.90 superblocks that may indicate overlapping partitions.

The main assembly logic counts up-to-date active devices, spares, journal devices, and rebuilding devices. Event counters must be current or within the kernel-compatible margin; devices reporting the most recent device as failed are ignored unless forced. With `--force`, `force_array()` can rewrite selected stale superblocks to the most recent event count, with reshape-progress safeguards.

Before start, the code reloads the chosen superblock, initializes sysfs, normalizes desired device states, optionally marks a forced dirty array clean, handles lockless bitmap setup, restores reshape backup data through grow helpers, updates the map, then calls `start_array()`.

## Container/Subarray Behavior
`assemble_container_content()` initializes sysfs for the member, removes old devices no longer in metadata, adds new and expansion devices, updates the map, validates or rewrites PPL when supported, checks `enough()` availability, blocks unsafe dirty degraded RAID4/5/6 unless policy allows it, configures internal bitmaps, handles reshape backup/continuation, starts mdmon for external metadata, sets array state through sysfs, and emits assembly status.

## Dependencies and Integration Points
This file depends heavily on mdadm shared APIs from `mdadm.h`: supertype operations, map locking/updating, sysfs helpers, mdstat parsing, policy/domain checks, md ioctls, mdmon control, grow/reshape helpers, and disk add/remove helpers. It bridges userspace metadata handlers with kernel md activation via `SET_ARRAY_INFO`, `ADD_NEW_DISK`, `RUN_ARRAY`, sysfs `array_state`, and related attributes.

## Safety and Risk Notes
Assembly is intentionally conservative around metadata mismatches, active arrays, busy members, event-count divergence, reshape progress disagreement, missing/stale journals, invalid PPL, and dirty degraded RAID4/5/6. `--force` can rewrite superblocks and mark arrays clean, and the code prints explicit warnings where that may risk corruption. The map lock is central to avoiding races with incremental assembly and udev/mdadm monitor behavior.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/Assemble.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/Build.c -->
# File Research: sources/block-storage/mdadm/Build.c

## Purpose
`Build.c` implements mdadm’s build mode for creating non-persistent linear or RAID0-style arrays without writing member superblocks.

## Major Entry Point
- `Build(struct mddev_ident *ident, struct mddev_dev *devlist, struct shape *s, struct context *c)`

## Behavior
The function requires an explicit RAID level, validates that all listed real devices are block devices, counts `missing` placeholders, and verifies that the number of listed devices equals `s->raiddisks`. If no layout is provided, it uses `default_layout()`.

It creates an md device, updates the mdadm map with a zero UUID and `STR_COMMON_NONE` metadata, and fills `mdu_array_info_t` directly. The array is marked `not_persistent = 1`, active/working/failed counts are derived from missing devices, and RAID0/linear chunk defaults are applied when needed. RAID0 with unset layout is forced to `RAID0_ORIG_LAYOUT`.

For each non-missing member, it opens the block device exclusively, records device size, updates `s->size` to the smallest usable size when size is unspecified or too large, sets active/sync disk state plus optional write-mostly, and adds the disk through `ADD_NEW_DISK`. Finally it starts the array with `RUN_ARRAY`, waits for the md device, and reports success.

## Dependencies and Integration Points
This code uses shared mdadm helpers for block-device validation, md device creation, map updates, size probing, md ioctl wrappers, and waiting for device readiness. It does not use metadata supertype handlers because build mode is intentionally non-persistent.

## Safety and Risk Notes
Failure paths stop the array with `STOP_ARRAY` and close the md fd. Because no superblocks are written, mdadm cannot later auto-discover the array from member metadata; callers must understand this mode is for explicit, non-persistent construction.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/Build.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/Create.c -->
# File Research: sources/block-storage/mdadm/Create.c

## Purpose
`Create.c` implements mdadm array creation: validating requested geometry, checking member devices, initializing metadata, adding member disks, optionally zeroing data ranges, and starting or preparing the new array.

## Major Entry Points
- `Create()` is the top-level create-mode implementation.
- `default_layout()` resolves default RAID layouts, preferring metadata-handler defaults when available.
- `add_disks()` performs the two-pass process of adding devices to metadata and then to the kernel array.
- `add_disk_to_super()` assigns disk roles/state and invokes the metadata handler’s `add_to_super()`.
- `update_metadata()` writes initialized metadata, configures internal bitmaps, flushes metadata updates, and updates map entries when external metadata changes UUIDs.
- `write_zeroes_fork()` and `wait_for_zero_forks()` implement optional asynchronous zeroing of data areas.

## Core Control Flow
`Create()` validates required parameters first: RAID level, device counts, RAID6 limits, spare support, bitmap support, and metadata/container constraints. If a single listed device is an md container, it can load container metadata and create a member array inside it.

Defaults are resolved for layout, chunk size, size, and metadata type. Geometry validation is delegated to the selected metadata handler through `validate_geometry()`, including consistency policy and data offset considerations. The code rounds sizes to chunk boundaries where necessary and uses the smallest suitable component size when no explicit size is given.

For each real component device, creation verifies block-device status, determines or parses data offset, validates geometry against the device, accumulates min/max usable sizes, adds drive policy information, and warns about existing ext2, reiserfs, RAID metadata, and partitions. It also warns for boot-related metadata placement and platform compatibility issues.

Before writing anything, warnings require interactive confirmation unless `--run` is used. The code also inserts intentional missing slots for certain RAID4/5/6 creation cases to prefer reconstruction behavior or satisfy kernel start requirements.

The md device is created under a map lock, checked for naming conflicts, initialized with array geometry, and passed to the metadata handler’s `init_super()`. The map is updated before disk addition so udev and other mdadm processes can identify the array.

`add_disks()` blocks SIGINT/SIGCHLD, then runs two passes. Pass one prepares per-disk metadata, removes partitions from opened devices, calls `add_to_super()`, and starts optional zeroing children. After zeroing completes, `update_metadata()` writes initial superblocks and bitmap state. Pass two adds each disk to the kernel md device with `ADD_NEW_DISK`.

After all disks are added, containers are prepared without starting data IO. Non-container arrays are started when `--run` is set or enough devices were supplied. External metadata arrays use sysfs `array_state` and mdmon coordination; native arrays use `RUN_ARRAY` unless readonly sysfs start is requested.

## Dependencies and Integration Points
The file integrates mdadm configuration defaults, metadata supertype operations, md device creation, map locking, udev blocking/unblocking, sysfs attributes, mdmon, policy checks, filesystem/partition probes, and kernel md ioctls.

## Safety and Risk Notes
Creation is careful about existing signatures, partition tables, oversized device differences, unsuitable geometry, unsupported bitmaps/PPL, clustered bitmap node counts, and metadata platform compatibility. Optional zeroing is interrupt-aware: the parent waits for zeroing children even after SIGINT so disks are not left busy in the background. Abort paths remove map entries, close fds, unblock udev, and release policy data.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/Create.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/Detail.c -->
# File Research: sources/block-storage/mdadm/Detail.c

## Purpose
`Detail.c` implements mdadm detail/reporting commands for active md arrays, inactive arrays, containers, subarrays, platform metadata support, and export/brief output modes.

## Major Entry Points
- `Detail(char *dev, struct context *c)` prints or exports array details for one md device.
- `Detail_Platform(struct superswitch *ss, int scan, int verbose, int export, char *controller_path)` reports metadata platform support.
- `detail_fname_from_uuid()` formats UUIDs for detail output with special super1 byte-order handling.

## Core Control Flow
`Detail()` opens the md device, reads sysfs metadata and device state when available, falls back to `GET_ARRAY_INFO`, and resolves external metadata/container status. If the device is a subarray, it identifies the parent container and member name, then loads container content.

To obtain richer metadata, it scans active member devices from sysfs or ioctl disk info, opens component devices, loads superblocks through the selected supertype, and extracts mdinfo. It avoids using free-floating spares with zero UUID as the authoritative source.

In `--export` mode, it emits shell-style key/value records such as `MD_LEVEL`, `MD_DEVICES`, `MD_CONTAINER`, `MD_MEMBER`, `MD_METADATA`, `MD_UUID`, `MD_DEVNAME`, reshape status, metadata-specific exported detail, and per-device role/path records unless device output is suppressed.

In brief mode, it prints an `ARRAY` or `INACTIVE-ARRAY` line suitable for configuration-like output, including level, device count, container/member or metadata, bitmap path, spares, metadata-specific brief detail, and optionally sorted device paths.

In full mode, it prints human-readable fields: metadata version, creation/update time, raid level, array and component sizes, device counts, persistence, bitmap information, state/degraded/resync status from `/proc/mdstat`, layout, chunk size, consistency policy, reshape details, metadata-specific detail, member arrays for containers, and a component table.

## Device State Handling
The component table reserves two slots per raid disk so replacements can be displayed next to primary devices, with extra devices after active slots. It reports faulty, active, sync, removed, writemostly, failfast, journal, spare, and rebuilding state. RAID10 near/far layouts may print set letters for synced members.

## Dependencies and Integration Points
This file uses sysfs readers, md ioctls, mdstat parsing, metadata supertype detail callbacks, map lookup helpers, preferred device-name mapping, container/subarray helpers, consistency-policy mappings, bitmap dirtiness checks, and platform-detail callbacks.

## Safety and Risk Notes
`Detail()` is read-oriented, but its return value changes in test mode: it indicates failed or insufficient arrays through `rv`. Export output depends on map file availability for UUID/devname records. The code contains a likely typo in `if (fstat(fd, &stb) != 0 && !S_ISBLK(stb.st_mode))`, where `stb` is consulted after failed `fstat`; the intended condition was probably failure or non-block device.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/Detail.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/Dump.c -->
# File Research: sources/block-storage/mdadm/Dump.c

## Purpose
`Dump.c` implements metadata dump and restore support for mdadm. It copies RAID metadata between real devices and same-sized dump files, using metadata-handler callbacks.

## Major Entry Points
- `Dump_metadata(char *dev, char *dir, struct context *c, struct supertype *st)`
- `Restore_metadata(char *dev, char *dir, struct context *c, struct supertype *st, int only)`

## Dump Behavior
`Dump_metadata()` requires an existing output directory, opens the source device read-only, obtains its size, guesses metadata type if not supplied, loads the superblock with hardware compatibility ignored, and requires the supertype to provide `copy_metadata`.

It creates a new file in the target directory named after the source device basename, truncates it to the same size as the source device, and asks the metadata handler to copy metadata into it. If the source is a block device, it scans `/dev/disk/by-id` for names pointing to the same `st_rdev` and creates hardlinks in the dump directory for those identifiers.

## Restore Behavior
`Restore_metadata()` opens the target device read-write, checks its size, then chooses a source file. If the restore path is a directory, it prefers a file whose name also maps through `/dev/disk/by-id` to the target block device; it rejects ambiguous matches with different inodes. If no by-id match exists, it falls back to the target device basename. If the restore path is a file, that is allowed only when `only` indicates a single target device.

The restore file must be exactly the same size as the target device. The function guesses and loads metadata from the file, requires `copy_metadata`, then copies metadata from file to device.

## Dependencies and Integration Points
Both paths use mdadm device open helpers, metadata supertype probing/loading, the `copy_metadata` callback, size probing, and `/dev/disk/by-id` stable-name matching.

## Safety and Risk Notes
The same-size check protects against restoring dumps to mismatched devices. A bug-like condition appears in `Restore_metadata()`: `if (!fl)` treats file descriptor `0` as failure but misses `-1`; the usual check should be `fl < 0`. In normal CLI execution fd 0 is often already open, but this is still a fragile error check.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/Dump.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/Examine.c -->
# File Research: sources/block-storage/mdadm/Examine.c

## Purpose
`Examine.c` implements mdadm metadata examination for component devices and bad-block logs. It reads RAID superblocks or containers and prints detailed, brief, or export-formatted metadata without assembling arrays.

## Major Entry Points
- `Examine(struct mddev_dev *devlist, struct context *c, struct supertype *forcest)`
- `ExamineBadblocks(char *devname, int brief, struct supertype *forcest)`

## Examine Behavior
For each listed device, `Examine()` opens it read-only, chooses a metadata handler from a forced supertype, container detection, or superblock guessing, then attempts to load either an ordinary superblock or container metadata. Hardware compatibility checks are temporarily ignored during load.

If `--brief` is active, devices are grouped by array using metadata type and `compare_super()`. The code tracks devices in a linked-list helper, counts spares for non-container arrays, and later emits one brief mdadm.conf-style line per discovered array, optionally including devices and subarrays in verbose mode.

If `--export` is active, it calls metadata-specific `export_examine_super()` when available. Otherwise it prints the device name followed by metadata-specific detailed examination output. Each loaded superblock is freed after use unless retained for brief grouping.

## Bad-Block Examination
`ExamineBadblocks()` opens one device, guesses or uses forced metadata, verifies that the metadata format supports `examine_badblocks`, loads the superblock, and dispatches to the metadata handler. It reports missing metadata or unsupported bad-block examination as errors.

## Dependencies and Integration Points
This file is primarily a dispatcher into supertype callbacks: `load_super`, `load_container`, `getinfo_super`, `compare_super`, `brief_examine_super`, `brief_examine_subarrays`, `export_examine_super`, `examine_super`, and `examine_badblocks`.

## Safety and Risk Notes
The operations are read-only except for the optional SPARC adjustment path, which calls `update_super(..., UOPT_SPARC22, ...)` on loaded metadata state before printing. Error reporting is suppressed in scan/brief cases to support broad probing.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/Examine.c -->