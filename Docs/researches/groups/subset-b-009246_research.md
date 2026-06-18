# subset-b-009246 Research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_multifs_run/tasks/generate_comparison.yml -->
# sources/test-tools/kdevops/playbooks/roles/ai_multifs_run/tasks/generate_comparison.yml

This task writes and executes `generate_comparison.py`, a generated Python report tool for AI benchmark results across filesystem configurations. The embedded script loads every subdirectory below `ai_multifs_results_dir` except `comparison`, reads optional `filesystem_config.txt` metadata, parses all `results_*.json`, computes per-filesystem averages for insert rate, index creation time, query QPS, and query latency, then persists an HTML report and JSON summary under `ai_multifs_results_dir/comparison`.

Important APIs are Ansible `copy`, `command`, and `debug`, plus Python `json`, `glob`, `os`, and `datetime`. Control flow is linear: generate executable script, run it with Python 3, then print artifact paths. State is entirely file-based: benchmark JSON and config text are read, while `multi_filesystem_comparison.html` and `multi_filesystem_summary.json` are overwritten. Integration depends on the JSON schema emitted by `milvus_benchmark.py` and the directory layout created by `run_single_filesystem.yml`. Risks include unescaped config text inserted into HTML, treating zero or missing metrics as valid best/worst candidates, and no Ansible `changed_when`/failure shaping around report generation. Test signals should include synthetic result trees with empty, partial, and malformed JSON files.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_multifs_run/tasks/generate_comparison.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_multifs_run/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/ai_multifs_run/tasks/main.yml

This task file is the entry point for executing enabled multi-filesystem AI benchmark configurations. It imports optional `../extra_vars.yaml`, filters `ai_multifs_configurations` down to entries whose `enabled` value equals true, loops over that list with `fs_config` and `fs_index`, includes `run_single_filesystem.yml` for each filesystem, and includes `generate_comparison.yml` only when more than one filesystem was tested.

The primary Ansible APIs are `include_vars`, `set_fact`, and `include_tasks`. Control flow is data-driven by the defaults from `ai_multifs_setup/defaults/main.yml` and any extra vars. State is held in the transient `enabled_fs_configs` fact; persistent benchmark state is delegated to included task files. Integration points are the setup role, per-filesystem runner, comparison generator, and the Milvus benchmark script. A key risk is that `selectattr('enabled', 'equalto', true)` may not match string values produced by templated defaults unless they are resolved to booleans by the inventory. Test signals should cover zero, one, and multiple enabled configurations.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_multifs_run/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_multifs_run/tasks/run_single_filesystem.yml -->
# sources/test-tools/kdevops/playbooks/roles/ai_multifs_run/tasks/run_single_filesystem.yml

This file runs one destructive filesystem benchmark iteration for the current `fs_config`. It unmounts the shared mount point, formats `ai_multifs_device` using `fs_config.mkfs_cmd`, mounts it with `fs_config.filesystem` and `fs_config.mount_opts`, creates per-filesystem result and benchmark data directories, renders a Milvus config from `milvus_config.json.j2`, runs `milvus_benchmark.py` asynchronously with a two-hour timeout, records filesystem metadata, captures `df` plus filesystem-specific diagnostics, and unmounts the filesystem.

Important APIs are Ansible `mount`, `shell`, `file`, `template`, `copy`, and async polling. Persistent state includes a newly formatted block device, data under `ai_multifs_mount_point`, JSON results, `filesystem_config.txt`, and `filesystem_stats.txt`. Integration depends on the setup role validating packages and device existence, the benchmark script being available under `playbook_dir`, and Milvus being reachable according to the rendered config. The main risk is data loss because `mkfs` runs directly on `ai_multifs_device`; quoting is also weak around shell-expanded paths and commands. Test signals should use disposable loop devices or mocked Ansible runs and verify unmount behavior after failures.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_multifs_run/tasks/run_single_filesystem.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_multifs_setup/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/ai_multifs_setup/defaults/main.yml

This defaults file defines the multi-filesystem AI benchmark matrix. It sets the shared results directory, block device, mount point, and a list of filesystem configurations for XFS with 4K/16K/32K/64K block sizes, ext4 with normal and bigalloc layouts, and btrfs default options. Each configuration includes a display `name`, filesystem type, `mkfs_cmd`, mount options, and a templated `enabled` expression.

The data model is consumed by setup and run roles through `ai_multifs_configurations`, `ai_multifs_device`, `ai_multifs_mount_point`, and `ai_multifs_results_dir`. State is declarative only; persistence happens when tasks create directories, format devices, and write results. Integration requires external boolean variables such as `ai_multifs_test_xfs`, `ai_multifs_xfs_4k_4ks`, and similar toggles. Risks include templated booleans becoming strings, XFS block-size combinations that may require compatible kernel/page-size support, and ext4 bigalloc parameters that may fail on unsuitable devices. Test signals should validate the matrix rendering and enabled filtering under representative extra vars.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_multifs_setup/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_multifs_setup/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/ai_multifs_setup/tasks/main.yml

This task file prepares the host for multi-filesystem AI benchmarks. It imports optional extra vars, creates `ai_multifs_results_dir` and `ai_multifs_mount_point`, unmounts any stale mount at the test path, installs filesystem utilities for XFS, ext4, and btrfs, derives `enabled_fs_configs`, validates that `ai_multifs_device` exists, and writes a `test_configuration.txt` summary of the enabled configurations.

Important APIs are `include_vars`, `file`, `mount`, `package`, `set_fact`, `stat`, `debug`, and `copy`. Control flow is straightforward host preparation followed by validation. Persistent state includes directories and the summary file; it intentionally does not format the target device. Integration points are the defaults file, later `ai_multifs_run` tasks, and package managers on target distributions. Risks include package name differences across distros, ignored unmount errors masking a busy mount, and device validation checking existence but not whether the block device is safe to overwrite. Test signals should include missing-device failure, no enabled configs, and package install on supported OS families.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_multifs_setup/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_results/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/ai_results/tasks/main.yml

This role is a minimal collection stub for AI benchmark results. It ensures `ai_benchmark_results_dir` exists, recursively finds all `*.json` files below it, registers the result set as `result_files`, and logs the count. The file comments indicate future aggregation, analysis, and reporting are expected but not yet implemented.

Important APIs are `ansible.builtin.file`, `find`, and `debug`. Control flow is linear and read-only after directory creation. State is a central results directory plus the transient `result_files` fact. Integration depends on `ai_run_benchmarks` and multi-filesystem roles writing JSON into the same results hierarchy. Risks are low but include false confidence: no schema validation, no aggregation, no artifact copy, and no failure when expected results are absent. Test signals should assert directory creation, recursive discovery, and behavior with zero result files.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_results/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_run_benchmarks/files/milvus_benchmark.py -->
# sources/test-tools/kdevops/playbooks/roles/ai_run_benchmarks/files/milvus_benchmark.py

This Python script benchmarks a Milvus vector database. `MilvusBenchmark` connects to Milvus, recreates a collection, generates random NumPy float vectors, measures batched insert throughput and flush time, creates an HNSW or IVF_FLAT index, loads the collection with retry and timeout logic, runs searches over selected top-k and batch-size combinations, records filesystem/kernel/hostname metadata, and writes a JSON result file.

Important APIs include `pymilvus.connections`, `Collection`, `CollectionSchema`, `FieldSchema`, `DataType`, `utility.load_state`, NumPy random generation, `subprocess.run`, and `argparse`. Control flow in `run_benchmark()` is fail-fast: filesystem detection, connect, create collection, insert, index, query, save. State is persisted in Milvus collections and the JSON output; existing collections named by `database_name` are dropped. Dependencies are a working Milvus server, pymilvus, numpy, and OS tools such as `df` and `uname`. Risks include random vectors without a seed, memory pressure for large datasets, fixed insert batch size, collection deletion, and query QPS computed from batch size over average elapsed batch time. Test signals should mock pymilvus, validate result schema, and run a small integration benchmark against ephemeral Milvus.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_run_benchmarks/files/milvus_benchmark.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_run_benchmarks/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/ai_run_benchmarks/tasks/main.yml

This role runs Milvus benchmark iterations with lock and virtualenv management. It imports optional extra vars, optionally removes a stale lock, checks for existing `milvus_benchmark.py` processes, ensures the results/workdir directories, enforces a `.benchmark.lock`, copies the benchmark script, installs Python venv packages, removes accidental global pymilvus/numpy installs, verifies the pre-existing venv can import pymilvus, renders `benchmark_config.json`, waits for Milvus, runs a sequence of JSON-producing benchmark iterations, and always removes the lock.

Important APIs are `include_vars`, `shell`, `fail`, `stat`, `file`, `copy`, `package`, `command`, `template`, `wait_for`, and Ansible `block/always`. Persistent state includes the venv, workdir, lock file, config, and `results_<hostname>_<iteration>.json`. Integration depends on `ai_setup` having Milvus online and `make ai` having provisioned the venv. Risks include a five-minute stale-lock threshold that may be too short, process detection via shell pipeline, global pip uninstall side effects, and lock cleanup depending on `lock_created.changed`. Test signals should cover concurrent launch rejection, forced unlock, missing venv failure, and multiple iteration outputs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_run_benchmarks/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_setup/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/ai_setup/tasks/main.yml

This task file provisions Docker-backed Milvus dependencies. When `ai_milvus_docker` is true, it creates Docker storage directories, creates a Docker network, starts an etcd container with fixed compaction/quota settings, delegates MinIO setup to the shared `minio_setup` role, waits for etcd, starts the Milvus standalone container with etcd and MinIO environment variables, and waits for the Milvus port.

Important APIs are `community.docker.docker_network`, `community.docker.docker_container`, `include_role`, `wait_for`, and file creation. Persistent state includes Docker containers, network, mounted storage paths for Milvus, etcd, and MinIO. Integration points are Docker, the MinIO role, benchmark tasks, and variables defining image strings, ports, credentials, resources, and paths. A notable risk is the Milvus container task using `ansible.builtin.command: milvus run standalone` inside the docker_container module argument block, which appears to be an invalid namespaced parameter rather than the module's `command` option. Test signals should include Ansible syntax validation and a Docker smoke test that reaches port 19530.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_setup/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_uninstall/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/ai_uninstall/tasks/main.yml

This role removes the Docker-based AI benchmark runtime. It imports optional extra vars, removes the Milvus, MinIO, and etcd containers, removes the Docker network, optionally uninstalls Python graphing packages when `ai_benchmark_enable_graphing` is true, and prints a completion message that data directories are preserved.

Important APIs are `community.docker.docker_container`, `community.docker.docker_network`, `ansible.builtin.pip`, and `debug`. Control flow is linear and guarded by `ai_milvus_docker` for Docker resources. Persistent data under `ai_docker_data_path` and `ai_benchmark_results_dir` is intentionally retained. Integration depends on the same container/network names used by `ai_setup`. Risks include `failed_when: false` hiding partial cleanup failures, pip uninstall operating outside the benchmark venv, and no removal of volumes or directories. Test signals should validate idempotency, missing-container behavior, and preservation of benchmark artifacts.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_uninstall/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ansible_cfg/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/ansible_cfg/defaults/main.yml

This defaults file defines values used to render the repository's `ansible.cfg`. It controls deprecation warnings, the dense callback plugin behavior, stderr and skipped-host display settings, per-host start display, task path reporting, Python interpreter discovery (`auto_silent`), and fork count.

The file is declarative and has no runtime control flow. Its important integration surface is the `ansible_cfg` task template `ansible.cfg.j2`, which consumes these variables to configure local Ansible execution behavior for kdevops workflows. Persistent state is created only when the task role writes the generated config. Risks are mostly operational: callback settings can hide or show large amounts of output, fork count affects concurrency and load, and `auto_silent` may obscure interpreter discovery problems. Test signals should render the template with defaults and verify expected keys in the generated `ansible.cfg`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ansible_cfg/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ansible_cfg/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/ansible_cfg/tasks/main.yml

This task file generates the kdevops `ansible.cfg`. It imports the first matching optional extra vars file from YAML or JSON names, renders `ansible.cfg.j2` to `ansible_cfg_file` with executable permissions, and touches `topdir_path/ansible.cfg` so Make sees an updated target.

Important APIs are `include_vars` with `with_first_found`, `template`, and `file state=touch`. State persistence is the generated config and timestamp update. Integration points include the defaults file, any extra vars, the template, and Makefile dependency behavior. Risks include mode `0755` being broader than necessary for a config file, `failed_when: false` masking malformed extra vars, and touching `topdir_path/ansible.cfg` regardless of whether `ansible_cfg_file` points elsewhere. Test signals should include rendering with no extra vars, with each supported extra vars extension, and verifying make-style timestamp updates.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ansible_cfg/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/base_image/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/base_image/defaults/main.yml

This defaults file provides base image role toggles and helper variables. It defaults to user-session libvirt (`libvirt_uri_system: false`), disables copying sources into guests, disables custom raw images, leaves `kdevops_uid` blank, and sets the default GRUB update command to `/usr/sbin/update-grub2`.

The file is declarative; behavior is implemented by `base-image.yml` and `custom-image.yml`. Integration points are libguestfs, virt-builder, virt-customize, libvirt ownership expectations, and templates that use `kdevops_uid` and `update_grub_cmd`. Persistent state is created later as raw images and virt-builder repository metadata. Risks are configuration mismatch: system libvirt needs different ownership, distro-specific GRUB commands are adjusted later only for selected image versions, and empty `kdevops_uid` changes generated guest user behavior. Test signals should render the virt-builder template under both system and user libvirt modes.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/base_image/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/base_image/tasks/base-image.yml -->
# sources/test-tools/kdevops/playbooks/roles/base_image/tasks/base-image.yml

This task file creates a raw base OS image through `virt-builder`. It gathers facts, detects the control host `kdevops` UID, chooses a Red Hat GRUB command when needed, renders a temporary virt-builder command file, runs `virt-builder` with architecture, output path, size, raw format, and command file, optionally adjusts SELinux to permissive for Fedora images on Debian/Ubuntu hosts, fixes image ownership/permissions depending on system versus user libvirt, and deletes the temporary command file.

Important APIs are `gather_facts`, `command`, `set_fact`, `tempfile`, `template`, and `file`. Persistent state is `base_image_pathname`; temporary state is the command file. Integration depends on libguestfs tools, `virt-builder.j2`, distro variables, `libvirt_image_size`, and `libvirt_qemu_group`. Risks include image creation being expensive and privileged, `creates` preventing regeneration after template changes, SELinux customization only on changed builds, and divergent permission behavior between libvirt modes. Test signals should include dry template rendering and image build smoke tests for user and system libvirt.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/base_image/tasks/base-image.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/base_image/tasks/custom-image.yml -->
# sources/test-tools/kdevops/playbooks/roles/base_image/tasks/custom-image.yml

This file turns a supplied custom raw image into a kdevops-compatible virt-builder source and base image. It builds paths for custom image storage, downloads the raw image and optional SHA512 sums, verifies checksums, resizes and expands the root partition, customizes the image using `virt-customize` or firstboot commands for cross-architecture cases, writes a sentinel, creates virt-builder source and index files, runs `virt-builder-repository`, copies the custom image to `base_image_pathname`, and applies libvirt ownership.

Important APIs include `set_fact`, `file`, `stat`, `get_url`, `command`, `tempfile`, `template`, and `debug`. Persistent state spans `custom_image`, `.ok` sentinel, `/etc/virt-builder/repos.d/...conf`, the custom index, and the final base image. Integration depends on guestfs variables, architecture flags, libvirt mode, qemu-img, virt-resize, virt-customize, and templates. Risks include a sentinel hiding stale customization, hard-coded `/dev/sda1` expansion, privileged writes under `/etc`, cross-architecture firstboot being less complete than normal customization, and copy only when the custom image exists or was downloaded. Test signals should cover checksum failure, rebuild after sentinel removal, and cross-architecture conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/base_image/tasks/custom-image.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/base_image/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/base_image/tasks/main.yml

This entry point decides whether to create a base image. It stats `base_image_pathname`, includes `custom-image.yml` when `guestfs_has_custom_raw_image` is true, and includes `base-image.yml` only when the target image does not already exist and no custom raw image is configured.

Important APIs are `stat` and `include_tasks`. State is the existence check result and the base image file created by the included path. Integration depends on defaults and higher-level guestfs configuration selecting custom versus virt-builder generation. Risks include skipping regeneration whenever a stale image exists, unconditional custom-image execution regardless of whether `base_image_pathname` already exists, and no checksum or metadata validation on existing base images. Test signals should verify all three branches: existing normal image, missing normal image, and custom image configuration.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/base_image/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/blktests/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/blktests/defaults/main.yml

This defaults file configures the blktests workflow. It disables test execution by default, defines rerun/failure and skip toggles, sets optional oscheck and test-limit arguments, declares source repositories and local paths for blktests, NBD, and optional dbench compilation, and defaults `blktests_test_devs` to `/dev/null` as a safety placeholder.

The variables are consumed by dependency installation, source checkout/build, test execution, and result collection. Persistent state is later created under `data_path`, `/usr/local/blktests/`, and workflow result directories. Integration points include upstream blktests, NBD, dbench, kdevops workflow scripts, and block devices supplied by inventory. Risks include the typo-like `blktets_data` variable name, `/dev/null` requiring explicit override before tests, and source checkouts pinned to moving branches/tags such as blktests `master`. Test signals should render role vars and assert safety failures when devices are unset.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/blktests/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/blktests/handlers/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/blktests/handlers/main.yml

This handler restarts the watchdog daemon using the service name stored in `watchdog_service_name`. It is a single Ansible service action named `Restart watchdog daemon`.

The important API is `ansible.builtin.service` with `state: restarted`. Control flow is event-driven: the handler runs only when notified by other tasks or roles. Persistent state is limited to the system service lifecycle. Integration depends on watchdog configuration elsewhere in the kdevops playbooks and on `watchdog_service_name` being defined for the target distribution. Risks are simple but operationally important: an undefined or wrong service name will fail handler execution, and restarting watchdog during long block tests may affect failure detection timing. Test signals should include handler notification in a host with a known watchdog service and an undefined-variable lint check.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/blktests/handlers/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/blktests/scripts/add-suse-repo-if-not-found.sh -->
# sources/test-tools/kdevops/playbooks/roles/blktests/scripts/add-suse-repo-if-not-found.sh

This shell helper manages SUSE zypper repositories for blktests dependencies. It accepts a repository URL and repository name, removes existing repos whose detailed listing contains `yast2`, tries to enable the named repository with `zypper mr -e`, and if that fails adds the repository with refresh/autorefresh/check flags, then refreshes it with automatic GPG key import.

Important commands are `zypper lr -d`, `zypper rr`, `zypper mr -e`, `zypper ar -f -c`, and `zypper refresh`. State persistence is global zypper repository configuration. Integration occurs from SUSE dependency tasks when benchmark repos are needed for dbench. Risks include broad removal of repos matching `yast2`, positional arguments with no validation, stdout/stderr redirection style that may hide useful diagnostics, and no `set -e` despite multiple privileged package-manager operations. Test signals should run in a disposable SUSE container or VM and verify idempotency for existing and missing repo names.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/blktests/scripts/add-suse-repo-if-not-found.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/blktests/tasks/install-deps/debian/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/blktests/tasks/install-deps/debian/main.yml

This Debian-specific dependency file updates apt metadata, installs `nvme-cli`, and installs the packages needed to build and run blktests, blktrace, NBD, dbench, filesystem tools, multipath tools, fio, compilers, headers, and development libraries.

Important APIs are `ansible.builtin.apt` with `become`. Control flow is linear package installation. Persistent state is the system package database and installed tools. Integration points are the main blktests role, Debian/Ubuntu package names, and variables such as `pkg_libaio`. Risks include duplicate package entries, missing variable `pkg_libaio`, package-name drift between Debian releases, and broad dependency installation on test hosts. Test signals should run apt check mode or molecule-style provisioning on supported Debian releases and verify tools such as `nvme`, `fio`, and compiler commands exist.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/blktests/tasks/install-deps/debian/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/blktests/tasks/install-deps/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/blktests/tasks/install-deps/main.yml

This dispatcher includes the shared `pkg` role and imports the distribution-specific dependency file for Debian, SUSE, or Red Hat based on `ansible_facts['os_family']|lower`.

Important APIs are `include_role` and `import_tasks`. Control flow is purely conditional on gathered OS family facts. State persistence is delegated to the distro files, which install packages and sometimes build NBD. Integration points are role `pkg` and the three distro-specific task files. Risks include no fallback or failure message for unsupported OS families, exact lower-case comparisons that must match Ansible fact values, and static imports making syntax errors in all distro files visible even when not executed. Test signals should include ansible-lint/syntax checks and fact-matrix tests for supported families.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/blktests/tasks/install-deps/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/blktests/tasks/install-deps/redhat/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/blktests/tasks/install-deps/redhat/main.yml

This Red Hat dependency file installs blktests build and runtime packages with DNF. The package list covers compilers, filesystem tools, quota, lvm, fio, dbench, multipath, PCI utilities, development headers, and block/storage utilities.

Important APIs are `ansible.builtin.dnf` with `become`, retry settings inherited by the module task, and a local `packages` variable. Control flow is a single package installation task. Persistent state is the RPM database and installed toolchain. Integration points are Fedora/RHEL/CentOS package availability, EPEL or base repositories configured elsewhere, and the main blktests build tasks. Risks include package differences across RHEL major versions, requiring `dbench` from repositories that may not provide it, and no explicit retries unlike the bootlinux Red Hat dependency role. Test signals should run package resolution on supported Red Hat family releases and confirm `make`, `fio`, `dbench`, and `multipathd` availability.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/blktests/tasks/install-deps/redhat/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/blktests/tasks/install-deps/suse/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/blktests/tasks/install-deps/suse/main.yml

This SUSE dependency file derives release facts, decides whether repositories and `nvme-cli` are available, installs blktests dependencies, conditionally adds benchmark repositories for older SLE releases, installs dbench, and conditionally clones/builds/installs NBD from source.

Important APIs are `set_fact`, `package`, `script`, `git`, `file`, `command`, and `community.general.make`. Persistent state includes installed packages, zypper repos, cloned NBD source, generated placeholder manpage inputs, and installed NBD binaries. Integration depends on the helper repo script, variables `nbd_git`, `nbd_version`, `nbd_data`, `num_jobs`, and `make`. Risks are high: several conditions reference `sle15sp4` instead of `is_sle15sp4`, Leap packages are guarded by `is_tumbleweed`, and NBD `autogen`, `configure`, build, and install tasks lack the same `compile_nbd`/`repos_present` guards as the clone. Test signals should include `ansible-playbook --syntax-check`, SUSE version fact simulation, and an actual SLE/openSUSE dependency run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/blktests/tasks/install-deps/suse/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/blktests/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/blktests/tasks/main.yml

This role provisions and optionally runs blktests. It imports extra vars, creates a data partition, installs dependencies, clones kdevops, copies `.config`, optionally compiles dbench, rebuilds blktrace and blktests from source, links `oscheck.sh`, disables multipathd, reboots, records kernel information, validates test devices, starts optional monitoring, computes test limits from env or known failures, runs `oscheck.sh`, collects results back to localhost, augments expunge lists, generates result directories, reports new expunges, and compresses kernel-specific results.

Important APIs include role inclusion, `git`, `copy`, `community.general.make`, privileged `command`, `systemd`, `reboot`, `find`, `fetch`, `archive`, and delegated localhost commands. State spans source trees under `data_path`, installed `/usr/local/blktests`, workflow `results` and `expunges`, `.begin` sentinel, and compressed archives. Integration points are kdevops workflow scripts, monitoring tasks, block devices, kernel under test, and expunge tooling. Risks include destructive source-tree removal, `ignore_errors/no_log` on the actual test run, shell commands writing local files, strict `/dev/null` guard, and result-copy assumptions. Test signals should verify dry-run setup, device validation failures, limited test runs, and result archive creation.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/blktests/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/bootlinux/defaults/main.yml

This defaults file defines the bootlinux workflow's kernel build, install, and configuration settings. It covers data partition defaults, target Linux git/ref/tree/path, make commands, ccache and reproducible-build environment construction, uninstall toggles, 9P/target/builder modes, packaged-kernel mode, A/B baseline/dev kernel parameters, config-fragment toggles, architecture/page-size choices, and many kdevops fragment switches.

The important data structures are `bootlinux_make_params` and `bootlinux_build_environment`, which combine compiler, ccache, and reproducible-build variables for later make/shell tasks. State is declarative until tasks clone/build/install kernels and mount filesystems. Integration points include create_data_partition, build task files, config templates/fragments, GRUB update tasks, packaged artifacts, and workflow variables. Risks include many booleans that must be mutually coherent, possible undefined variables for ccache settings unless provided elsewhere, and target refs defaulting to an old stable kernel. Test signals should include variable rendering for GCC/Clang, ccache, reproducible builds, 9P, packaged, and A/B modes.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/ccache.yml -->
# sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/ccache.yml

This task file configures kdevops-managed ccache for bootlinux builds. When ccache and managed mode are enabled, it creates `topdir_path/.ccache` and `bootlinux_ccache_dir`, renders `ccache.conf.j2`, and prints a summary of enabled mode, config path, cache directory, and maximum size.

Important APIs are `file`, `template`, and `debug`. Persistent state includes the ccache directory tree and generated config. Integration points are defaults that inject `CCACHE_CONFIGPATH` and `CC` into build environments, plus the distro dependency files that install `ccache`. Risks include directory mode `0755` exposing cache metadata, undefined `bootlinux_ccache_dir` or `bootlinux_ccache_max_size`, and only configuring managed mode while system-wide mode depends on external setup. Test signals should render the config and run a tiny make invocation with the expected `CCACHE_CONFIGPATH`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/ccache.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/config-fragments.yml -->
# sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/config-fragments.yml

This file builds a kernel configuration by merging selected upstream and kdevops fragments. It initializes `fragment_list`, appends upstream paths such as `kernel/configs/kvm_guest.config`, appends role template fragments such as `storage.config`, page-size fragments, and subsystem-specific fragments based on boolean variables, prints the selected list or a warning, then runs `scripts/kconfig/merge_config.sh -n .config` inside `target_linux_dir_path`, optionally prefixed with `LLVM=1` for Clang.

Important APIs are `set_fact`, loops over condition/path records, `debug`, and `shell`. Persistent state is the kernel `.config` in the source tree. Integration depends on `config.yml` selecting or preparing a base `.config`, the kernel source containing `merge_config.sh`, and role template fragments existing. Risks include shell path quoting, no explicit validation that fragments exist before merge, and conflicting fragments where the last applied setting wins. Test signals should include fragment-list unit rendering and a kernel-tree smoke run with representative fragment combinations.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/config-fragments.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/config.yml -->
# sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/config.yml

This task file selects the kernel config template name used for bootlinux builds. It initializes a search list with `config-kdevops` and `config-{{ target_linux_config }}`, discovers `config-next-*` templates on localhost, version-sorts them, appends the newest linux-next config, optionally runs `make mrproper` for clean non-9P builds, and uses `with_first_found` to set `linux_config` to the basename of the first available config.

Important APIs are `set_fact`, delegated `find`, `community.general.version_sort`, `community.general.make`, and `with_first_found`. Persistent state is limited to optional source-tree cleanup; selected config state is the `linux_config` fact. Integration points are role templates, kernel source directory, build tasks, and `bootlinux_clean_before_build`. Risks include `mrproper` deleting existing build state, linux-next sorting depending on filename shape, and this file selecting but not itself copying the config into `.config`. Test signals should cover missing target-specific config fallback and clean-before-build behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/config.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install-deps/debian/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install-deps/debian/main.yml

This Debian dependency file updates apt metadata and installs packages needed to build and install Linux kernels. The list includes compilers, make, git, bison/flex, bc, libssl/libelf/ncurses development headers, filesystem utilities, mdadm, iSCSI, Python pip, zstd, b4, ccache, rsync, dwarves, and lz4.

Important APIs are `ansible.builtin.apt` with privileged execution. Persistent state is installed packages. Integration points are bootlinux build tasks, Rust dependency role, optional b4 patch application, ccache setup, and kernel packaging/install commands. Risks include package availability differences across Debian/Ubuntu versions, `portmap` being obsolete on some distributions, and no retry logic for apt operations. Test signals should include package resolution on supported releases and verifying `make`, `gcc`, `b4`, `ccache`, and `pahole` are available.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install-deps/debian/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install-deps/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install-deps/main.yml

This dispatcher imports full kernel build dependency tasks for Debian, SUSE, or Red Hat based on `ansible_os_family`. It is used when bootlinux builds happen on target nodes rather than 9P host builds and when packaged workflow mode is disabled.

Important APIs are conditional `import_tasks`. Control flow is static and OS-family driven. Persistent state is delegated to the distro files, which install package sets. Integration points are `bootlinux/tasks/main.yml`, distro fact gathering, and the target build mode. Risks include unsupported OS families silently doing nothing, exact family spelling requirements (`Suse`, `RedHat`), and syntax errors in any imported file affecting playbook parsing. Test signals should include syntax checks and fact-driven include tests for all three supported families.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install-deps/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install-deps/redhat/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install-deps/redhat/main.yml

This Red Hat dependency file enables EPEL for non-Fedora systems, installs the kernel build package set with DNF and retries, conditionally installs `btrfs-progs` on Fedora, installs Clang/LLVM/Lld when `bootlinux_compiler_clang` is true, installs rpmbuild support when `bootlinux_builder` is true, and removes `dracut-config-generic` to avoid initramfs behavior that interferes with the workflow.

Important APIs include `include_role`, `dnf`, retry/until loops, and conditional tasks. Persistent state is RPM package installation/removal. Integration points are EPEL, bootlinux build modes, ccache, packaged kernel artifacts, and GRUB/initramfs behavior. Risks include package-name drift, destructive removal of `dracut-config-generic`, Fedora-only btrfs install despite other Red Hat releases possibly needing it, and EPEL role availability. Test signals should cover Fedora and RHEL-family hosts, Clang mode, builder mode, and idempotent repeated runs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install-deps/redhat/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install-deps/suse/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install-deps/suse/main.yml

This SUSE dependency file installs Linux kernel build dependencies using `community.general.zypper`. The package list includes compilers, git, make, kconfig/build tools, OpenSSL and ELF development libraries, filesystem utilities, mdadm, rpc/portmap, hwinfo, iSCSI, and ccache.

Important APIs are privileged `community.general.zypper` with `disable_recommends: false`. Persistent state is the zypper package database. Integration points are bootlinux build tasks, ccache setup, and SUSE package repositories. Risks include package naming differences between openSUSE and SLE, missing retry logic, and no optional Clang path unlike Red Hat. Test signals should include package resolution on intended SUSE releases and verifying the kernel build can reach configuration and compile phases.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install-deps/suse/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install-minimal-deps/debian/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install-minimal-deps/debian/main.yml

This Debian minimal dependency file supports 9P bootlinux mode, where the kernel build happens on the host and the guest only needs enough tooling for installation. It runs `apt-get update --allow-releaseinfo-change` best-effort, refreshes apt metadata through the apt module, and installs `make`, `gcc`, `kmod`, and `ccache`.

Important APIs are privileged `command` and `apt`. Persistent state is the installed minimal package set. Integration points are 9P build/install tasks and ccache environment variables. Risks include ignoring update-releaseinfo errors, still installing `gcc` even if only module installation is needed, and no retry around apt. Test signals should include a 9P-mode guest provisioning run and verification that `modules_install install` prerequisites exist.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install-minimal-deps/debian/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install-minimal-deps/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install-minimal-deps/main.yml

This dispatcher imports minimal dependency tasks for Debian, SUSE, or Red Hat based on `ansible_os_family`. It is selected by `bootlinux/tasks/main.yml` when `bootlinux_9p` is true and packaged workflow mode is disabled.

Important APIs are conditional `import_tasks`. State changes occur only in the imported distro files. Integration points are 9P mode, target guest package managers, and the later kernel install steps. Risks include silent no-op on unsupported OS families, exact OS-family spelling, and the possibility that minimal dependencies are insufficient for distro-specific install hooks. Test signals should include fact-matrix include validation and a 9P install smoke test on each supported family.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install-minimal-deps/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install-minimal-deps/redhat/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install-minimal-deps/redhat/main.yml

This Red Hat minimal dependency file installs `make`, `gcc`, `kmod`, and `ccache` with DNF for 9P mode. It has two nearly identical tasks split by distribution major version less than 8 versus greater than or equal to 8; both currently use `ansible.builtin.dnf`.

Important APIs are privileged `dnf` and `ansible_facts['distribution_major_version']`. Persistent state is installed minimal packages. Integration points are bootlinux 9P mode and kernel installation hooks on Red Hat family guests. Risks include redundant version split, use of DNF even for older releases where yum compatibility may vary, and no retry logic. Test signals should include RHEL/CentOS 7 and 8+ package installation and a follow-on `make modules_install install` check.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install-minimal-deps/redhat/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install-minimal-deps/suse/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install-minimal-deps/suse/main.yml

This SUSE minimal dependency file installs the small tool set needed by 9P kernel installation mode: `make`, `gcc`, `kmod-compat`, and `ccache`.

The important API is privileged `community.general.zypper`. Persistent state is the installed package set. Integration points are bootlinux 9P mode and SUSE kernel module/install tooling. Risks include `kmod-compat` availability varying by SUSE release, no retry logic, and assuming ccache is useful even when the guest is only installing artifacts. Test signals should include package resolution on supported SLE/openSUSE releases and a kernel install smoke test after the 9P mount is present.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install-minimal-deps/suse/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install/packages.yml -->
# sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install/packages.yml

This task file installs prebuilt kernel packages from `bootlinux_artifacts_dir` onto target nodes. For non-Debian systems it finds RPMs on localhost, copies them to `/tmp`, filters out devel/header packages when building `kernel_packages`, and installs selected RPMs with `rpm -i --force`. For Debian systems it finds DEBs, copies them to `/tmp`, filters out headers, and installs selected packages with `dpkg -i`.

Important APIs are delegated `find`, `copy`, `set_fact`, privileged `command`, and loops. Persistent state is uploaded package files in `/tmp` and installed kernel packages. Integration points are packaged workflow builders that populate artifacts and optionally `kernel.release`. Risks include `kernel_packages` accumulating across hosts/runs, installing only core packages while omitting headers/devel by substring, forced RPM install bypassing dependency management, and no failure when no artifacts are found. Test signals should include empty artifact directory failure expectations, RPM and DEB install dry runs, and kernel package selection validation.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install/packages.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/main.yml

This is the main bootlinux orchestration role. It imports extra vars, selects kernel config, installs Rust and distro dependencies, configures ccache, optionally installs b4, derives A/B testing and 9P active kernel refs, can stop early for debug, creates the data partition, mounts 9P sources, dispatches target/9P/builder build tasks, supports uninstalling old kernels, updates GRUB console/default settings, installs packaged or source-built kernels, updates GRUB default selection, reboots, and reports the running kernel.

Important APIs include `include_tasks`, `include_role`, `import_tasks`, `set_fact`, `debug`, `mount`, `command`, `find`, `file`, `lineinfile`, `shell`, and `reboot`. Persistent state spans data partitions, kernel source trees, installed modules and boot files, GRUB config, package installs, and rebooted host state. Integration points are build subroles, create_data_partition, update-grub tasks, package artifacts, ccache, and A/B inventory groups. Risks include complex variable interactions, destructive uninstall patterns under `/boot` and `/lib/modules`, debug paths using `meta: end_play`, and shell-based kernel install. Test signals should include syntax checks, 9P and non-9P smoke runs, packaged install, A/B targeting, and post-reboot uname validation.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/update-grub/debian.yml -->
# sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/update-grub/debian.yml

This Debian GRUB update file runs `update-grub` with privilege escalation, registers `grub_update`, and marks the task changed when the command exits successfully.

The important API is `ansible.builtin.command`; state persistence is the regenerated GRUB configuration under the distro's normal boot paths. Integration points are bootlinux main and install tasks that modify `/etc/default/grub`, install kernels, or set GRUB defaults. Risks include assuming `update-grub` exists, marking changed on every successful run, and no explicit stderr handling or retries. Test signals should include Debian/Ubuntu runs after kernel installation and validation that `/boot/grub/grub.cfg` contains the target kernel entry.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/update-grub/debian.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/update-grub/install.yml -->
# sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/update-grub/install.yml

This file configures GRUB to boot the newly installed kernel by default. It sets `GRUB_DEFAULT=saved`, disables submenus with `GRUB_DISABLE_SUBMENU=y`, refreshes GRUB, derives the kernel release from either the source tree's `include/config/kernel.release` or packaged `bootlinux_artifacts_dir/kernel.release`, builds an awk/grep pipeline to find the flat menu entry number on Debian, runs `grub-set-default`, and prints the selected entry.

Important APIs are `lineinfile`, imported update-grub tasks, `stat`, `slurp`, `lookup('file')`, `set_fact`, privileged `shell`, privileged `command`, and `debug`. Persistent state includes `/etc/default/grub`, regenerated GRUB config, and saved default entry. Integration depends on Debian GRUB menu format, package/source build outputs, and prior kernel install. Risks include grep matching multiple releases, only implementing entry selection for Debian, shell quoting around `kernelrelease`, and silently leaving `kernelrelease: unknown`. Test signals should parse representative GRUB configs, validate saved default, and reboot-check `uname -r`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/update-grub/install.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/update-grub/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/update-grub/main.yml

This dispatcher imports the distro-specific GRUB update task for Debian, SUSE, or Red Hat based on `ansible_facts['os_family']|lower`.

Important APIs are conditional `import_tasks`. Persistent state changes happen in the imported files, which regenerate bootloader configuration. Integration points are bootlinux main uninstall/install flows and `update-grub/install.yml`. Risks include unsupported OS families doing nothing, static import syntax exposure, and relying on lower-case family strings. Test signals should include fact-matrix include checks and verifying each supported distro produces a changed GRUB update after kernel installation.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/update-grub/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/update-grub/redhat.yml -->
# sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/update-grub/redhat.yml

This Red Hat GRUB update file disables GRUB menu auto-hide, detects UEFI by checking `/sys/firmware/efi/efivars`, sets `grub_config_file` to `/etc/grub2.cfg` for BIOS or `/etc/grub2-efi.cfg` for UEFI, then runs `grub2-mkconfig -o` against that path.

Important APIs are privileged `command`, `stat`, `set_fact`, and changed-state registration. Persistent state includes GRUB environment and regenerated GRUB config files. Integration points are Red Hat bootlinux kernel install/uninstall flows and saved-default handling in other tasks. Risks include `grub2-editenv - unset menu_auto_hide` missing `changed_when`, assumptions about `/etc/grub2*.cfg` symlink locations, and marking every successful mkconfig as changed. Test signals should include BIOS and UEFI Red Hat family hosts and validation that the target kernel appears in the generated menu.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/update-grub/redhat.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/update-grub/suse.yml -->
# sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/update-grub/suse.yml

This SUSE GRUB update file runs `update-bootloader --refresh` with privilege escalation, registers `grub_update`, and marks the task changed when the command succeeds.

The important API is privileged `ansible.builtin.command`. Persistent state is the refreshed SUSE bootloader configuration. Integration points are bootlinux kernel install/uninstall flows and any prior edits to GRUB defaults. Risks include assuming `update-bootloader` exists on all SUSE variants, changed-on-success behavior, and no validation that the intended kernel entry was produced or selected. Test signals should include SLE/openSUSE kernel install runs followed by bootloader menu inspection and reboot verification.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/update-grub/suse.yml -->
