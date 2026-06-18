# Research: subset-b-009262

Grouped research for kdevops script files. Each section preserves the source path and is bounded by reconciliation markers for per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/lib.sh -->
# sources/test-tools/kdevops/scripts/lib.sh

## Purpose
This shell fragment centralizes common kdevops runtime variables for scripts and workflow watchdog helpers. It is meant to be sourced after `.config` has exported Kconfig-derived shell variables and after `TOPDIR` is available.

## Important APIs and state
It does not define functions. Its API is a set of exported or shell-global variables: `PLAYBOOKDIR`, `INVENTORY`, `KDEVOPSHOSTSPREFIX`, kernel CI status/log file names, KOTD log file names, manual kill notice path, and workflow `.begin` marker paths. When fstests is enabled it also derives `FSTYP` and `TEST_DEV` from `CONFIG_FSTESTS_*`.

## Control flow
Execution is immediate on source. It assigns variables and conditionally reads fstests settings if `CONFIG_KDEVOPS_WORKFLOW_ENABLE_FSTESTS=y`.

## Persistence and integration
The variables name persisted files under `TOPDIR`, including `.kernel-ci.*`, `.kotd.*`, `.running_kill_pids.sh`, and workflow begin markers. `workflows/*/kill_pids.sh` sources this file for `MANUAL_KILL_NOTICE_FILE`.

## Dependencies
Depends on `TOPDIR` and Kconfig variables already being in the environment or sourced shell.

## Risks and test signals
There is no validation for missing Kconfig variables, so unset values silently produce empty paths or settings. Test by sourcing it under a known `.config` and checking expected variables, and by running dependent kill/list scripts in list mode.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/libvirt_pool.sh -->
# sources/test-tools/kdevops/scripts/libvirt_pool.sh

## Purpose
Provides shell helpers for discovering libvirt storage pool support and mapping a base directory to a virsh pool name/path.

## Important APIs
`get_can_sudo()` probes noninteractive sudo and returns `y` or `n`. `get_pool_vars()` detects Fedora user-session behavior from `$OS_FILE`, sets `CAN_SUDO`, and chooses `REQ_SUDO`. `virsh_works()` checks sudo/session capability, `virsh` availability, and `virsh pool-list`. `virsh_get_pool_list()` fills global `POOL_LIST`. `virsh_path_in_pool_list_exists()`, `virsh_path_pool_list_name()`, and `virsh_path_pool_list_path()` search pool XML paths for `$BASE_DIR`.

## Control flow and state
The script is a library with global variables: `USES_QEMU_USER_SESSION`, `CAN_SUDO`, `REQ_SUDO`, `POOL_LIST`, `POOL_PATH`, and expected caller-provided `BASE_DIR` and `OS_FILE`. Several search helpers call `exit` after printing a match, so they are designed for script execution contexts as much as pure sourcing.

## Dependencies and integration
Uses `sudo`, `which`, `virsh`, `grep`, `sed`, and `awk`. It integrates with kdevops libvirt setup scripts that need to decide if storage pool commands should run through sudo or a user session.

## Risks and test signals
`get_can_sudo()` treats any sudo output not containing `may not` as usable sudo, including password prompts or other errors. XML is parsed with grep/sed rather than XML tooling. Test signals are `virsh_works` returning `y`, a non-empty `POOL_LIST`, and correct base directory pool lookup on Fedora and non-Fedora hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/libvirt_pool.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/mirror-docker-images.sh -->
# sources/test-tools/kdevops/scripts/mirror-docker-images.sh

## Purpose
Mirrors Docker images used by kdevops workflows into a local registry and optionally stores compressed offline archives.

## Important APIs
Functions include `check_registry()`, `mirror_image(image)`, `save_image_archive(image)`, `load_images_list(file)`, `scan_for_images()`, `create_manifest()`, `main()`, and `show_usage()`. Environment knobs are `MIRROR_DIR` and `REGISTRY_PORT`; positional argument 1 may be an image-list file.

## Control flow
The script validates that `http://localhost:$REGISTRY_PORT/v2/` responds, creates `$MIRROR_DIR/images/manifest.txt`, appends custom images, optionally scans role defaults for image references, then loops over `DEFAULT_IMAGES`. Each image is pulled, retagged as `localhost:$REGISTRY_PORT/<image_name>`, pushed, and optionally archived with `docker save`, `gzip`, and `sha256sum`.

## State and persistence
Persists a manifest under `$MIRROR_DIR/images/manifest.txt` and archives under `$MIRROR_DIR/images/archives`. Docker daemon image/tag state is modified.

## Dependencies and integration
Requires `docker`, `curl`, `gzip`, `sha256sum`, and a running registry. It supports mirror setup for vLLM, MinIO, Milvus, LMCache, etcd, and registry images.

## Risks and test signals
Tag rewriting uses `${image#*/}`, which can collapse registry namespaces and may collide for images sharing the same tail. `--scan` is only checked in `$2`, so option ordering is limited. Test by running with a small custom list against a local registry and checking manifest entries, pushed tags, and archive checksums.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/mirror-docker-images.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/nixos_ssh_key_name.py -->
# sources/test-tools/kdevops/scripts/nixos_ssh_key_name.py

## Purpose
Generates a deterministic SSH key name for NixOS VMs associated with a specific kdevops checkout.

## Important APIs
`get_ssh_key_name()` computes `kdevops-nixos-<last-two-path-components>-<8-char-sha256>`. `main()` prints either the key name or, with `--path`, `~/.ssh/<key_name>`.

## Control flow and state
The script anchors naming to the script location: it takes the directory containing this script, moves one level up to the kdevops root, hashes that absolute path, and combines it with readable path suffixes. It writes no files.

## Dependencies and integration
Uses only Python standard library modules `os`, `sys`, and `hashlib`. It integrates with NixOS provisioning code that needs stable per-checkout SSH key names independent of the caller's current working directory.

## Risks and test signals
Because the path is derived from script location rather than the runtime checkout root, copied scripts or symlinks can change naming expectations. Test with and without `--path`, and ensure generated names remain stable across invocations from different directories.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/nixos_ssh_key_name.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/os-debian-version.sh -->
# sources/test-tools/kdevops/scripts/os-debian-version.sh

## Purpose
Checks whether `/etc/debian_version` contains a requested Debian version/distribution string.

## Important APIs and control flow
`check_debian_version(pattern)` greps `DEBIAN_VERSION_FILE=/etc/debian_version` case-insensitively for the first positional argument, prints `y` on match and `n` otherwise. If the file is absent it prints `n` and exits. The function is invoked immediately at the end of the script.

## State, dependencies, and integration
The script is read-only and depends on `/etc/debian_version` and `grep`. It is suitable for kdevops distro/version checks that expect boolean stdout.

## Risks and test signals
It has no argument validation, so an empty pattern may match unexpectedly depending on grep behavior. It exits with status 0 for both `y` and `n`, so callers must read stdout. Test by probing known version substrings and non-matching strings on Debian-derived and non-Debian hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/os-debian-version.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/os-release-check.sh -->
# sources/test-tools/kdevops/scripts/os-release-check.sh

## Purpose
Reports whether the current host matches a requested Linux distribution family, using `/etc/os-release`.

## Important APIs
`check_distro(arg)` dispatches supported names. `check_distro_redhat()`, `check_distro_suse()`, and `check_distro_ubuntu()` grep `/etc/os-release` for family-specific identifiers and print `y` or `n`.

## Control flow
The script requires one distribution argument. If `/etc/os-release` is missing it prints `n` and exits 0. Unsupported distro names also produce `n`.

## State and dependencies
Read-only. Depends on `/etc/os-release`, `grep`, and shell conditionals. It is likely used from Make/Kconfig glue that expects single-character boolean output.

## Integration points
Useful for conditional package/install logic where the caller wants Red Hat, SUSE, or Ubuntu family detection without parsing the file directly.

## Risks and test signals
Matching is simple substring grep and can be sensitive to case or future `os-release` formatting. It returns success status even for `n`, so callers must read stdout. Test with fixture files or container images for each distro family.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/os-release-check.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/spdxcheck.py -->
# sources/test-tools/kdevops/scripts/spdxcheck.py

## Purpose
Validates SPDX license identifiers in source file headers against license metadata from a kernel-style `LICENSES` tree.

## Important APIs and types
`SPDXdata` stores license and exception identifiers. `read_spdxdata(repo)` loads `LICENSES/preferred` metadata from the Git tree. `id_parser` is a PLY lexer/parser for SPDX expressions with tokens `ID`, `EXC`, `AND`, `OR`, `WITH`, `LPAR`, and `RPAR`. It validates identifiers and exception/license compatibility. `parse_lines(fd, maxlines, fname)` scans file headers for `SPDX-License-Identifier:`. `scan_git_tree()` and `scan_git_subtree()` walk GitPython tree objects.

## Control flow
CLI arguments select paths, stdin, or full tree scan. The script opens the current directory as a Git repository, reads SPDX metadata, constructs the parser, then scans up to `--maxlines` lines per file. It prints parse errors with file, line, column, message, and token; verbose mode prints counters.

## State and dependencies
Runtime state is in parser counters and SPDX lists. Dependencies are GitPython (`git`) and PLY (`ply.lex`, `ply.yacc`), plus a kernel-like `LICENSES` layout.

## Integration points
Used as a style/compliance checker in kernel-derived projects. It excludes the `LICENSES` tree and `license-rules.rst`.

## Risks and test signals
Only `LICENSES/preferred` is enabled, with dual/deprecated/exception directory support commented out. A bug path in `parse_lines` can reference `col` when `pe.tok` is false. Test with valid IDs, invalid IDs, invalid `WITH` exceptions, stdin mode, subtree mode, and `--verbose` counters.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/spdxcheck.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/ssh_config_file_name.py -->
# sources/test-tools/kdevops/scripts/ssh_config_file_name.py

## Purpose
Generates a unique SSH config filename for the current working directory, preventing multiple kdevops checkouts from sharing one generated SSH config.

## Important APIs
`get_directory_hash(path, length=8)` returns the first N hex characters of a SHA256 hash of an absolute path. `generate_ssh_config_filename(base_path="~/.ssh/config_kdevops")` appends the current directory hash to the base path. `main()` handles `--help`, optional custom base path, and default output.

## Control flow and state
The script is pure computation and prints the chosen path. It does not expand `~` or create files.

## Dependencies and integration
Uses Python `hashlib`, `os`, and `sys`. It integrates with provisioning scripts that need a stable `Include ~/.ssh/config_kdevops_*` naming pattern.

## Risks and test signals
Because it hashes `os.getcwd()`, callers must run it from the intended kdevops root. Moving a checkout changes the filename. Test by running from two directories and by passing a custom base path.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/ssh_config_file_name.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/status_nixos.sh -->
# sources/test-tools/kdevops/scripts/status_nixos.sh

## Purpose
Displays libvirt status for NixOS-backed kdevops virtual machines, networks, and storage pools.

## Important APIs and control flow
The script computes `SCRIPTS_DIR=$(dirname $0)`, sources `libvirt_pool.sh`, runs `get_pool_vars`, detects the libvirt URI through `detect_libvirt_session.sh` when present, exports `LIBVIRT_DEFAULT_URI`, then prints filtered `virsh list --all`, `virsh net-list --all`, and `virsh pool-list --all` output.

## State and dependencies
It is read-only over libvirt state and depends on `virsh`, optional sudo capability, and helper variables from `libvirt_pool.sh`. It does not persist state itself.

## Integration points
This wrapper gives Make targets or users a stable `scripts/status_nixos.sh` entry point for NixOS VM, network, and pool status.

## Risks and test signals
Unquoted `$0` and helper paths can misbehave if the checkout path contains whitespace. The grep filters only `nixos` or `kdevops`, so custom names may be hidden. Test with user-session and system libvirt URIs and with missing `virsh`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/status_nixos.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/test-linux-ab-config.py -->
# sources/test-tools/kdevops/scripts/test-linux-ab-config.py

## Purpose
Verifies that the current kdevops configuration enables Linux A/B testing and produces different baseline and development kernel refs.

## Important APIs
`LinuxABTester` tracks `failed_checks`. Methods are `check_config_file()`, `check_extra_vars()`, `verify_refs()`, `check_makefile_structure()`, and `run_checks()`. `main()` enforces execution from a kdevops root by requiring `Kconfig`.

## Control flow
The runner reads `.config`, requires `CONFIG_KDEVOPS_BASELINE_AND_DEV=y` and `CONFIG_BOOTLINUX_AB_DIFFERENT_REF=y`, reads `extra_vars.yaml`, extracts `target_linux_ref` and `target_linux_dev_ref` with regexes, verifies they are non-empty and distinct, and optionally checks `workflows/linux/Makefile` target names.

## State and dependencies
Read-only over `.config`, `extra_vars.yaml`, and optionally `workflows/linux/Makefile`. Uses Python standard library. The imported `subprocess` and `Path` are unused.

## Integration points
Useful in CI or local developer checks after `make` or `make extra_vars.yaml` generation for Linux A/B workflows.

## Risks and test signals
It parses YAML as text, so quoting/comments are not interpreted structurally. Output includes Unicode symbols, which may be noisy in minimal terminals. Test success should exit 0 with distinct refs; missing config, missing vars, identical refs, and wrong working directory should exit 1.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/test-linux-ab-config.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/test-linux-ab.sh -->
# sources/test-tools/kdevops/scripts/test-linux-ab.sh

## Purpose
Runs a TAP-style local validation of all Linux A/B defconfig build methods without requiring full infrastructure bringup.

## Important APIs
`tap_result(result, test_name, details)` emits TAP lines and tracks counters. `check_condition(condition, test_name, error_msg)` evaluates shell conditions. `restore_state()` restores a `.config.backup.$$` at exit.

## Control flow
The script backs up `.config`, declares a TAP plan of `1..18`, loops over `target`, `9p`, and `builder`, runs `make mrproper`, applies `make defconfig-linux-ab-testing-$method`, generates `extra_vars.yaml`, checks A/B Kconfig symbols, and validates method-specific symbols. It then extracts baseline/dev refs and verifies they differ before printing a summary.

## State and persistence
It modifies `.config` and `extra_vars.yaml` via Make, with a trap restoring `.config` only. It leaves generated files from Make unless cleanup is handled elsewhere.

## Dependencies and integration
Requires `make`, kdevops defconfig targets, grep, awk, and shell arrays. Designed for CI containers where full bringup is not possible.

## Risks and test signals
The hard-coded TAP plan says 18, but the script emits additional ref extraction tests, so TAP consumers may see a plan mismatch. `eval` in `check_condition` is acceptable for fixed internal strings but should not receive user input. Success exits 0 with all checks passing.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/test-linux-ab.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/test_git_firewall.sh -->
# sources/test-tools/kdevops/scripts/test_git_firewall.sh

## Purpose
Checks whether the host can open the native Git protocol port to `git.kernel.org`.

## Important APIs and control flow
There are no functions. It accepts but does not use `$1` as `CUR_VAL`, checks for `nc`, and if absent prints `y`. If `nc` exists, it runs `nc -v -z -w 3 git.kernel.org 9418` and prints `y` for success or `n` for failure.

## State and dependencies
Read-only network probe. Depends on `nc` when installed and external connectivity to `git.kernel.org:9418`.

## Integration points
Likely feeds Kconfig or setup checks to decide whether Git protocol is usable behind a firewall.

## Risks and test signals
Returning `y` when `nc` is missing treats untestable as allowed, which may hide firewall issues. Firewalls can also block ICMP/DNS differently than TCP 9418. Test by running on networks with and without Git protocol egress, and by temporarily moving `nc` out of PATH.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/test_git_firewall.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/update_ssh_config_guestfs.py -->
# sources/test-tools/kdevops/scripts/update_ssh_config_guestfs.py

## Purpose
Generates SSH config entries for libvirt/guestfs kdevops guests by querying guest IP addresses through the QEMU guest agent.

## Important APIs
`get_addr(name)` repeatedly runs `virsh qemu-agent-command <name> guest-network-get-interfaces` until it finds the first non-loopback IPv4 address or exceeds `KDEVOPS_SSH_CONFIG_TIMEOUT` seconds. `main()` reads `extra_vars.yaml`, loads the nodes file, and writes stanzas from `ssh_template`.

## Control flow
The script resolves `TOPDIR`, reads `extra_vars.yaml`, opens the configured `kdevops_nodes` YAML, chooses `~/.ssh/config_kdevops_<topdir_path_sha256sum>`, then iterates `nodes["guestfs_nodes"]`. Each host stanza includes host alias, IP alias, username `kdevops`, SSH port, guestfs identity file, disabled known-host checking, and fatal log level.

## State and persistence
It overwrites the generated SSH config and chmods it `0600`. It polls live VM agent state and may wait up to 180 seconds by default.

## Dependencies and integration
Requires PyYAML, `/usr/bin/virsh`, QEMU guest agent support, `extra_vars.yaml`, and the generated guestfs nodes file.

## Risks and test signals
JSON parsing assumes successful virsh output is valid and shaped with `return`. It picks the last matching IPv4 encountered. Test with guests that boot slowly, guests without agent networking, custom SSH port, and generated config permission checks.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/update_ssh_config_guestfs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/update_ssh_config_lambdalabs.py -->
# sources/test-tools/kdevops/scripts/update_ssh_config_lambdalabs.py

## Purpose
Adds, updates, or removes SSH config stanzas for Lambda Labs cloud instances.

## Important APIs
`update_ssh_config(action, hostname, ip_address, username, config_file, ssh_key, provider_name, port=22)` writes or removes entries. `remove_from_config(hostname, config_file)` deletes a block whose `Host` line starts with the hostname. `main()` parses positional arguments.

## Control flow
For `update`, the script expands paths, removes an existing block for the hostname, appends a provider-commented stanza containing hostname and IP aliases, and prints a success message. For `remove`, it removes the block and prints success.

## State and persistence
It mutates the supplied SSH config file in place. It does not create parent directories or chmod the file.

## Dependencies and integration
Uses Python standard library only. It is intended for cloud provisioning/deprovisioning steps that know instance hostname, IP, user, and private key path.

## Risks and test signals
Removal only detects `Host <hostname> ` or `Host <hostname>\t`, so entries with only `Host <hostname>` may be missed. Appending can fail if the config directory does not exist. Test update idempotency, removal, custom provider name, and custom port.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/update_ssh_config_lambdalabs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/update_ssh_config_nixos.py -->
# sources/test-tools/kdevops/scripts/update_ssh_config_nixos.py

## Purpose
Manages SSH config entries for native QEMU NixOS VMs, with explicit update and remove actions.

## Important APIs
`update_ssh_config(action, hostname, host_ip, port, username, ssh_config_path, ssh_key_path, tag)` uses a `# kdevops-managed: <tag> - <hostname>` marker plus a regex to replace or remove managed blocks. `main()` validates arguments, fills defaults, and handles errors.

## Control flow
The script expands the config path, creates its parent directory, reads existing content if present, removes any matching managed entry, then either writes a new stanza for `update` or only writes the reduced content for `remove`.

## State and persistence
It rewrites the supplied SSH config file. Unlike the guestfs script, it does not chmod the file. Entries include `StrictHostKeyChecking no`, `/dev/null` known-hosts, and `LogLevel ERROR`.

## Dependencies and integration
Uses Python standard library. It is called by NixOS VM lifecycle code that knows host-forwarded SSH port and private key location.

## Risks and test signals
The argument length check uses `< 8` but usage lists eight post-program fields; missing tag is allowed by code. Regex removal assumes the marker format remains unchanged. Test update idempotency, remove, default host/user/port behavior, and config directory creation.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/update_ssh_config_nixos.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/version_check/ansible-playbook -->
# sources/test-tools/kdevops/scripts/version_check/ansible-playbook

## Purpose
Checks that the installed `ansible-playbook` version meets kdevops' minimum requirement.

## Important APIs and control flow
The script sets `MIN_REQ=2.13.4`, derives `OWN_VER` from `ansible-playbook --version`, normalizes both versions through `${TOPDIR}/scripts/ld-version.sh`, and compares the normalized integers. If installed version is older it prints `ansible-playbook >= 2.13.4 required` and exits 1.

## State and dependencies
Read-only. Depends on `ansible-playbook`, `head`, `awk`, `sed`, and `TOPDIR/scripts/ld-version.sh`.

## Integration points
Used as a version gate before running Ansible-based workflows.

## Risks and test signals
If `TOPDIR` is unset or `ansible-playbook` is missing, errors will come from shell command substitution rather than a tailored diagnostic. Version parsing assumes the version is the last token of the first output line after removing `]`. Test with supported, unsupported, and missing Ansible installs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/version_check/ansible-playbook -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/vfio-permissions.sh -->
# sources/test-tools/kdevops/scripts/vfio-permissions.sh

## Purpose
Prepares host VFIO/PCI sysfs permissions for specified PCI device IDs used by passthrough workflows.

## Important APIs and control flow
The script is immediate-execution shell with `set -e`. It requires at least one PCI ID, loads `vfio-pci`, grants group `libvirt` access to `/sys/bus/pci/drivers_probe`, copies `10-qemu-hw-users.rules` into `/etc/udev/rules.d/` and `10-qemu-limits.conf` into `/etc/security/limits.d`, then for each PCI ID adjusts group/mode on `driver_override` and `driver/unbind`.

## State and dependencies
Mutates host kernel module state, sysfs node permissions, udev rules, and security limits. Requires `sudo`, `modprobe`, a `libvirt` group, and valid `/sys/bus/pci/devices/<PCI-ID>` paths.

## Integration points
Supports PCI passthrough and QEMU/libvirt workflows that need non-root libvirt users to bind/unbind devices to VFIO.

## Risks and test signals
Changing sysfs permissions is host-global and may be reset by udev or reboot. The script assumes a `libvirt` group and does not validate each PCI ID before chmod/chgrp. Test with a disposable passthrough device and verify libvirt/QEMU can unbind and bind it afterward.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/vfio-permissions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/virsh-destroy.sh -->
# sources/test-tools/kdevops/scripts/virsh-destroy.sh

## Purpose
Destroys all currently listed libvirt domains whose names contain `kdevops`.

## Important APIs and control flow
The script loops over `virsh list | awk '{print $2'} | grep kdevops`, echoes each matched domain name, and runs `virsh destroy` on it.

## State and dependencies
Mutates libvirt domain runtime state by forcibly stopping every matching running VM. Depends on `virsh` and the caller's libvirt permissions/session.

## Integration points
Can be called by Make or cleanup targets to stop all active kdevops guests in the current libvirt session.

## Risks and test signals
Destroy is abrupt and can lose guest state. Matching is based only on domain name substring and ignores stopped domains because `virsh list` omits inactive guests. Test in a session containing only disposable kdevops domains.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/virsh-destroy.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/virsh-reset.sh -->
# sources/test-tools/kdevops/scripts/virsh-reset.sh

## Purpose
Resets all currently listed libvirt domains whose names contain `kdevops`.

## Important APIs and control flow
The script loops over `virsh list | awk '{print $2'} | grep kdevops` and runs `virsh reset` on each matched running domain.

## State and dependencies
Mutates all matching running VMs by issuing hard resets. Depends on `virsh` and appropriate libvirt permissions.

## Integration points
Used by watchdog or manual recovery paths that need all active kdevops guests rebooted without graceful shutdown.

## Risks and test signals
Hard resets can corrupt guest state if storage is active. Matching is broad and only sees active domains. Test in an isolated libvirt session and confirm only intended `kdevops` domains reset.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/virsh-reset.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/vllm-quick-test.sh -->
# sources/test-tools/kdevops/scripts/vllm-quick-test.sh

## Purpose
Runs a quick functional test against kdevops vLLM deployments, covering baseline and optional development nodes.

## Important APIs
`test_node(node, node_type)` resolves node IP with Ansible, starts a kubectl port-forward for Kubernetes deployments when needed, calls the OpenAI-compatible completions endpoint, validates JSON, extracts completion text, and prints timing and response details.

## Control flow
The script loads `.config` and `extra_vars.yaml`, detects A/B mode, declared-host mode, and bare-metal vLLM mode, builds a `NODES` array, then tests each node. Requests are sent over SSH to `localhost:8000/v1/completions` with model `facebook/opt-125m`, prompt `kdevops is`, and max tokens 30.

## State and persistence
It may start background `kubectl port-forward` processes on target nodes and writes `/tmp/pf.log` remotely. It does not clean them up.

## Dependencies and integration
Requires `ansible`, `ssh`, `kubectl` on target for Kubernetes mode, `curl`, `bc`, and Python JSON tooling.

## Risks and test signals
Service naming is hard-coded as `vllm-prod-${node}-router-service`, which must match Helm output. JSON payload is shell-embedded and only safe for the fixed prompt. Success requires valid JSON, no API error message, and extractable choice text for every node.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/vllm-quick-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/vllm-status-summary.py -->
# sources/test-tools/kdevops/scripts/vllm-status-summary.py

## Purpose
Parses verbose vLLM status output, typically Ansible output, into a concise deployment summary with per-node state, images, Helm values, services, and suggested test commands.

## Important APIs
`parse_status_output(lines)` builds a status dictionary with timestamp, `ansible_running`, `nodes`, `overall_state`, `docker_images`, `helm_values`, and `services`. `print_simplified_status(status)` renders the summary. `main()` reads stdin and prints the report.

## Control flow
Parsing tracks the current section from marker lines such as `--- Kubernetes Pods ---` and tracks current node from Ansible result headers. It detects Helm deploy commands, Kubernetes readiness, minikube containers, 9P mirror mounts, pod states, Docker images, Helm image/model values, and Kubernetes services. Overall state is derived as deploying, configuring, running, starting, or stopped.

## State and dependencies
No persistence. Uses `datetime`, `re`, and stdin. Output includes Unicode symbols and human-oriented command snippets.

## Integration points
Designed behind a `make vllm-status-simplified` style target that pipes verbose status into this script.

## Risks and test signals
Parsing is tightly coupled to exact section headings and text patterns. Helm value parsing stores `_pending_repo` internally and may mis-associate tags if values are nested differently. Test with captured status logs for stopped, starting, deploying, and running deployments.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/vllm-status-summary.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/blktests/blktests_watchdog.py -->
# sources/test-tools/kdevops/scripts/workflows/blktests/blktests_watchdog.py

## Purpose
Reports blktests progress per host and flags possible hung or timed-out tests.

## Important APIs
`print_blktest_host_status(host, verbose, basedir, config)` combines `kssh.get_uname()`, `blktests.get_section()`, `blktests.get_blktest_host()`, and `blktests.get_last_run_time()` to print either a compact table row or verbose details. `_main()` parses hostfile, host section, and verbosity.

## Control flow
The CLI validates the hostfile and `.config`, computes `basedir`, reads hosts through `blktests.get_hosts()`, prints a table header, and processes each host. Percent complete is current runtime divided by historical runtime when available. Stall state is `Timeout`, `Hung-Stalled`, or `OK`.

## State and dependencies
Read-only over Ansible inventory, `.config`, remote SSH state, dmesg/journal lines, and prior blktests results. Requires the local `lib` package modules.

## Integration points
Used by blktests workflow monitoring and manual watchdog views.

## Risks and test signals
If historical runtime is absent, percent remains zero and stall detection may rely on default thresholds. Remote SSH timeouts map to stall signals. Test with host fixtures running a known blktest, no running process, and a forced timeout.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/blktests/blktests_watchdog.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/blktests/kill_pids.sh -->
# sources/test-tools/kdevops/scripts/workflows/blktests/kill_pids.sh

## Purpose
Kills kdevops workflow processes associated with the blktests workflow in the current checkout.

## Important APIs
Shared implementation with the workflow `list_pids.sh` wrappers. `usage()`, `parse_args()`, and `list_pid(pid, mode)` support `--help`, `--watchdog-mode`, list-only output, and manual-kill notice behavior.

## Control flow
The script sources `TOPDIR/.config` and `scripts/lib.sh`, identifies its target workflow from `basename $(dirname $0)`, verifies `CONFIG_KDEVOPS_WORKFLOW_ENABLE_BLKTESTS=y`, scans `ps -fu $USER`, filters processes whose `/proc/<pid>/cwd` is `TOPDIR` and whose `.config` matches the workflow, skips kernel CI and baseline loop processes, then sends signals to matching `make`, `run_loop`, `ansible-playbook`, and `ssh` processes.

## State and dependencies
Writes and removes `$MANUAL_KILL_NOTICE_FILE` unless in watchdog mode. Mutates process state by signaling process groups and processes. Depends on `/proc`, `ps`, `grep`, `readlink`, and sourced config.

## Risks and test signals
Process matching is string-based and can catch broad `ssh`/`make` processes in the checkout. Test with the sibling `list_pids.sh` first, then kill in a controlled workflow run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/blktests/kill_pids.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/blktests/list_pids.sh -->
# sources/test-tools/kdevops/scripts/workflows/blktests/list_pids.sh

## Purpose
Lists, without killing, processes that the blktests workflow kill helper would skip or terminate.

## Important APIs and control flow
This file shares the same body as `kill_pids.sh` and switches behavior based on `CALL=$(basename $0)`. When invoked as `list_pids.sh`, it sets `LIST_ONLY=true`, scans same-checkout workflow processes, and prints "Would be killed" or "Would be skipped" with `/proc/<pid>/cmdline` contents.

## State and dependencies
Read-only except for sourced shell variables. Requires `/proc`, `ps`, `readlink`, grep tools, `TOPDIR/.config`, and `scripts/lib.sh`.

## Integration points
Primary safety companion before running `workflows/blktests/kill_pids.sh`.

## Risks and test signals
Because it uses the exact matching logic as the killer, list output is the best preflight signal. NUL-separated `/proc/<pid>/cmdline` may print densely. Test during an active blktests run and verify protected kernel CI/baseline loop entries are marked skipped.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/blktests/list_pids.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/cxl/gen_qemu_cxl.py -->
# sources/test-tools/kdevops/scripts/workflows/cxl/gen_qemu_cxl.py

## Purpose
Generates QEMU command-line or libvirt XML `qemu:arg` fragments for CXL topologies.

## Important APIs
Builder functions produce device/object strings: `host_bridge()`, `root_port()`, `switch()`, `mailbox()`, `downstream_port()`, `memdev()`, `lsa()`, `type3()`, and `fmw()`. `qemu_print(kind, value, last=False)` emits either command-line continuation syntax or XML.

## Control flow
After argument parsing, the script validates size suffix `M` or `G`, computes bytes, emits `-machine cxl=on`, creates or references an LSA file, loops over host bridges, root ports, switches, downstream ports, memory backend files, and type3 devices, then emits a fixed-window memory mapping.

## State and persistence
With `--create-memdev-files`, it creates sparse raw files under `--memdev-path`: one `cxl_lsa.raw` and one `cxl_mem<N>.raw` per downstream port. It uses `os.umask(0)` before file creation.

## Dependencies and integration
Uses Python standard library only. Integrates with QEMU/libvirt launch configuration for CXL test workflows.

## Risks and test signals
The script exits if the backing directory is missing and does not validate free space. Global `args` is referenced by `qemu_print`. Test by generating both formats with small topologies and verifying QEMU accepts the emitted topology.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/cxl/gen_qemu_cxl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/demos/reboot-limit/analyze_results.py -->
# sources/test-tools/kdevops/scripts/workflows/demos/reboot-limit/analyze_results.py

## Purpose
Analyzes reboot-limit workflow results and optionally generates boot-time graphs for regular and kexec reboot comparisons.

## Important APIs
`RebootLimitAnalyzer` holds `hosts_data`, `regular_data`, `kexec_data`, and `comparison_mode`. Key methods include `parse_systemd_analyze_line()`, `load_host_data()`, `load_all_data()`, `calculate_statistics()`, `plot_boot_times()`, `plot_single_mode_analysis()`, `plot_comparison_analysis()`, `print_summary()`, `print_single_mode_summary()`, and `print_comparison_summary()`.

## Control flow
`main()` accepts a results directory, output path, and `--no-plot`. The analyzer detects comparison mode when `regular/` and `kexec/` subdirectories exist; otherwise each host subdirectory is loaded directly. It parses `reboot-count.txt` and `systemctl-analyze.txt`, prints textual statistics, and generates matplotlib PNG plots unless disabled.

## State and persistence
Reads workflow results and writes a PNG graph, creating the output directory if needed. It exits 0 when no data exists, treating that as a normal pre-run state.

## Dependencies and integration
Uses Python standard library plus `matplotlib`. It is tied to reboot-limit result layout and systemd-analyze output formats with and without initrd.

## Risks and test signals
The parser only accepts seconds with `s`, not `ms` or `min`. Comparison plot combines all hosts into aggregate series, which can obscure host-level variance. Test with generated sample data, no-data directories, comparison mode, and `--no-plot` on hosts without matplotlib.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/demos/reboot-limit/analyze_results.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/demos/reboot-limit/generate_sample_data.py -->
# sources/test-tools/kdevops/scripts/workflows/demos/reboot-limit/generate_sample_data.py

## Purpose
Creates synthetic reboot-limit result data for testing the analyzer and visualization pipeline.

## Important APIs
`generate_sample_data(results_dir, num_hosts=2, num_boots=50)` creates host directories, writes `reboot-count.txt`, and writes repeated `systemctl-analyze.txt` lines with randomized kernel, initrd, userspace, and total boot times.

## Control flow
The first host is named `demo-reboot-limit`; additional hosts use a development-style name. Random variation and periodic slow boots are applied to make graphs non-flat. The script has a direct `__main__` path for sample generation.

## State and dependencies
Persists files under the requested results directory. Uses Python standard library `os`, `random`, and `pathlib`.

## Integration points
Feeds `analyze_results.py` without needing real reboot-limit workflow runs.

## Risks and test signals
Randomness means output is not deterministic unless seeded externally. Host naming for `i > 0` appears fixed to `demo-reboot-limit-dev`, so more than two hosts would collide. Test by generating into a scratch directory and running the analyzer over it.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/demos/reboot-limit/generate_sample_data.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/demos/reboot-limit/run_loop.sh -->
# sources/test-tools/kdevops/scripts/workflows/demos/reboot-limit/run_loop.sh

## Purpose
Runs the reboot-limit baseline Make target repeatedly until a configured steady-state loop goal is reached or a failure occurs.

## Important APIs
`run_loop()` is the main loop body. It uses common kernel-CI log variables from `scripts/lib.sh`, especially `.kernel-ci.ok`, `.kernel-ci.fail`, `.kernel-ci.log`, `.kernel-ci.fail.log`, `.kernel-ci.diff.log`, and `.kernel-ci.logtime.loop`.

## Control flow
It sources `.config` and `scripts/lib.sh`, resumes count from `.kernel-ci.ok` when incremental mode is enabled, runs `/usr/bin/time -p -o .kernel-ci.logtime.loop make reboot-limit-baseline`, records git status and timing, writes diff/failure files on nonzero return, appends each iteration to the full log, updates `.kernel-ci.ok`, and exits once `CONFIG_REBOOT_LIMIT_ENABLE_LOOP=y` and count exceeds `CONFIG_REBOOT_LIMIT_LOOP_STEADY_STATE_GOAL`.

## State and persistence
Persists kernel-CI style loop files in the current working directory. The invoked Make target may separately persist reboot-limit result files and reboot target systems repeatedly.

## Dependencies and integration
Depends on kdevops Make targets, `/usr/bin/time`, Git, Ansible/SSH access through the Make target, sourced Kconfig variables, and the reboot-limit workflow layout.

## Risks and test signals
This is intentionally disruptive because `make reboot-limit-baseline` reboots hosts. The script overwrites kernel-CI log files and records git diffs on failure. Test with a low steady-state goal and disposable host, and verify `.kernel-ci.ok` resume behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/demos/reboot-limit/run_loop.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/demos/reboot-limit/run_loop_kotd.sh -->
# sources/test-tools/kdevops/scripts/workflows/demos/reboot-limit/run_loop_kotd.sh

## Purpose
Placeholder KOTD wrapper for reboot-limit loop testing.

## Important APIs and control flow
The script ensures `TOPDIR`, sources `.config` and `scripts/lib.sh`, sets `TARGET_HOSTS` to `baseline` or the first argument, prints that kernel-of-the-day updates are not implemented, and invokes `${TOPDIR}/scripts/workflows/demos/reboot-limit/run_loop.sh`.

## State and dependencies
Shares the same persistence and dependencies as `run_loop.sh`; `TARGET_HOSTS` is not exported in this script, so its effect depends on downstream environment behavior.

## Integration points
Used as a compatibility entry point for workflows that still reference a KOTD reboot-limit loop.

## Risks and test signals
The main risk is assuming KOTD updates happen; the script explicitly does not implement them. Test with minimal reboot count and confirm the standard loop runs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/demos/reboot-limit/run_loop_kotd.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/fstests/copy-results.sh -->
# sources/test-tools/kdevops/scripts/workflows/fstests/copy-results.sh

## Purpose
Copies the latest fstests results tarball and kdevops config into a separate results archive repository.

## Important APIs and control flow
The script validates `kdevops-results-archive` exists next to the current checkout and contains an `fstests` subdirectory. It ensures `workflows/fstests/results/archive` is a symlink to that archive, validates `extra_vars.yaml`, `last-kernel.txt`, and the result tarball, derives filesystem type and provider type, then creates a date/count archive directory.

## State and persistence
Creates symlink `workflows/fstests/results/archive`, copies `${LAST_KERNEL}.xz` and `.config` into `archive/$USER/$FSTYP/$TYPE/YYYYMMDD-NNNN`, then runs `git add` in the archive repository.

## Dependencies and integration
Requires shell tools, Git, `extra_vars.yaml`, and fstests result layout. It supports manual archival after baseline/test runs.

## Risks and test signals
The provider type is inferred from grepping YAML and can misclassify. It stages changes in another repo but does not commit. Test with a scratch archive repo, existing count directories, and missing tarball failure paths.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/fstests/copy-results.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/fstests/find-common-failures.sh -->
# sources/test-tools/kdevops/scripts/workflows/fstests/find-common-failures.sh

## Purpose
Finds common fstests expunge entries across per-section expunge files and appends them to `all.txt`.

## Important APIs
`usage()`, `parse_args()`, and `print_all_common_expunges()` implement CLI handling and output. `--lazy-baseline` changes the definition of common from present in all files to present in at least two files.

## Control flow
The script validates an expunge directory, collects all files except `all.txt`, loops over each test token from each file, counts how many files contain it, appends qualifying entries to a temporary list, merges that into `$DIR/all.txt`, sorts, and deduplicates.

## State and persistence
Mutates `$DIR/all.txt`, creating or extending it. Uses `mktemp` for intermediate state.

## Dependencies and integration
Depends on `find`, `grep`, `awk`, `sort`, `uniq`, `mktemp`. Used by `lazy-baseline.sh` and manual expunge maintenance.

## Risks and test signals
Grep patterns are unescaped test names, so regex metacharacters could overmatch. Nested loops are quadratic in number of files and entries. Test with known expunge fixtures in strict and lazy modes.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/fstests/find-common-failures.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/fstests/fstests_watchdog.py -->
# sources/test-tools/kdevops/scripts/workflows/fstests/fstests_watchdog.py

## Purpose
Reports fstests progress per host, detects stalls, and integrates crash detection/reset handling.

## Important APIs
`print_fstest_host_status(host, verbose, use_remote, use_ssh, basedir, config)` gathers kernel version, current/last test status, stall estimate, and crash state. `_main()` parses hostfile, section, verbosity, systemd-remote, and SSH forcing options.

## Control flow
The watchdog reads `.config`, optionally validates membership in `systemd-journal-remote`, enumerates hosts, prints a table, and processes each host. It prefers systemd-remote journal data when configured, falls back to SSH for kernel version and process discovery, computes progress from historical `check.time`, adjusts for soak-duration tests, then runs `KernelCrashWatchdog.check_and_reset_host()`.

## State and persistence
Reads host inventories, local config/results, remote journals/processes, and may write crash logs and reset hosts through the crash watchdog.

## Dependencies and integration
Depends on local `lib.kssh`, `lib.fstests`, `lib.systemd_remote`, and `lib.crash`, plus SSH, journal files, and group permissions.

## Risks and test signals
It can reset hosts during a status check if crashes are found. Group lookup uses `grp.getgrnam()` but assumes success path shape. Test with `--use-ssh`, systemd-remote enabled, active fstests, no running process, and known crash fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/fstests/fstests_watchdog.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/fstests/kill_pids.sh -->
# sources/test-tools/kdevops/scripts/workflows/fstests/kill_pids.sh

## Purpose
Kills kdevops processes associated with the fstests workflow in the current checkout and filesystem configuration.

## Important APIs and control flow
This is the shared workflow process killer. For `TARGET_WORFKLOW=fstests`, it requires `CONFIG_KDEVOPS_WORKFLOW_ENABLE_FSTESTS=y`, records `FS=$CONFIG_FSTESTS_FSTYP`, and only targets processes whose current working directory is `TOPDIR` and whose `.config` has the same `CONFIG_FSTESTS_FSTYP`.

## State and persistence
Creates `$MANUAL_KILL_NOTICE_FILE` for manual kills, removes it at the end, and sends termination/alarm signals to matching process groups and PIDs.

## Dependencies and integration
Depends on `/proc`, user process list, sourced `.config`, and `scripts/lib.sh`. It is used for manual or watchdog cleanup after stuck fstests runs.

## Risks and test signals
String matching may kill broad SSH or Make processes if they belong to the same checkout and filesystem workflow. Always compare with `workflows/fstests/list_pids.sh` output first. Successful cleanup should leave no matching run_loop, ansible-playbook, or workflow SSH processes.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/fstests/kill_pids.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/fstests/lazy-baseline.sh -->
# sources/test-tools/kdevops/scripts/workflows/fstests/lazy-baseline.sh

## Purpose
Automates lazy baseline expunge maintenance for fstests by finding failures common to at least two sections and removing those common entries from section files.

## Important APIs and control flow
The script validates `extra_vars.yaml`, `last-kernel.txt`, and helper scripts, extracts `LAST_KERNEL` and `FSTYP`, constructs `EXPUNGE_DIR="$EXPUNGE_BASE/$LAST_KERNEL/$FSTYP/unassigned/"`, then runs `find-common-failures.sh -l` followed by `remove-common-failures.sh`.

## State and persistence
Mutates expunge files below `workflows/fstests/expunges/<kernel>/<fstyp>/unassigned/`, especially `all.txt`, and may remove emptied files through the helper.

## Dependencies and integration
Depends on the two helper scripts, fstests result metadata, and shell tools. It is a convenience target for curating unstable/common failures into a lazy baseline.

## Risks and test signals
It assumes the `unassigned` priority path and trusts text parsing of YAML. Test with a copied expunge directory before running against tracked data; verify `all.txt` and per-section files contain expected entries.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/fstests/lazy-baseline.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/fstests/list_pids.sh -->
# sources/test-tools/kdevops/scripts/workflows/fstests/list_pids.sh

## Purpose
Lists fstests workflow processes that would be skipped or terminated by the fstests process killer.

## Important APIs and control flow
The file shares the process scanner with `kill_pids.sh` and switches to read-only mode because its basename is `list_pids.sh`. It filters by checkout path and matching fstests filesystem type, then prints command lines under "Would be skipped" or "Would be killed".

## State and dependencies
Read-only over process state and config files. Requires `/proc`, `ps`, `readlink`, `.config`, and `scripts/lib.sh`.

## Integration points
Used as a preflight and diagnostic tool before terminating an fstests workflow.

## Risks and test signals
It exposes the exact string-matching behavior of the killer, including broad process matches. Test while fstests is active and ensure unrelated checkouts or different filesystem configurations are not listed.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/fstests/list_pids.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/fstests/remove-common-failures.sh -->
# sources/test-tools/kdevops/scripts/workflows/fstests/remove-common-failures.sh

## Purpose
Removes failures listed in an expunge directory's `all.txt` from each per-section expunge file.

## Important APIs and control flow
The script validates exactly one directory argument, requires `$DIR/all.txt`, builds an alternation of first-column entries from `all.txt`, then filters each non-`all.txt` file through `grep -E -v`, sorting and deduplicating results.

## State and persistence
Rewrites each expunge file in place via a temporary file. If running inside a Git worktree and a file becomes empty, it runs `git rm -f` on that file.

## Dependencies and integration
Requires `find`, `grep`, `awk`, `sort`, `uniq`, `du`, `mktemp`, and optionally Git. Called by `lazy-baseline.sh`.

## Risks and test signals
The alternation regex is not escaped, so special regex characters in test names or comments can overmatch. The same temp file is moved repeatedly and relies on `mktemp` path reuse semantics. Test with fixture expunge files and verify only all.txt entries are removed.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/fstests/remove-common-failures.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/generic/crash_report.py -->
# sources/test-tools/kdevops/scripts/workflows/generic/crash_report.py

## Purpose
Builds a text summary of collected crash, corruption, and warning logs under the `crashes/` directory.

## Important APIs
`clean_lines(text)` strips ANSI escapes and non-printable characters. `collect_host_logs(host_path)` prefers decoded crash variants over raw crash files, includes warnings and corruption files, and returns typed entries. `generate_commit_log()` prints a Markdown-like report grouped by host.

## Control flow
When run, the script exits 0 with a no-crashes message if `crashes/` does not exist. Otherwise it iterates host directories, collects logs, and prints fenced cleaned content for each entry.

## State and dependencies
Read-only over crash output files. Uses Python `pathlib`, `re`, and `os`.

## Integration points
Consumes files produced by `KernelCrashWatchdog`, suitable for commit messages, CI logs, or failure summaries.

## Risks and test signals
Typo in the no-crashes message says "isues". Report size can grow large because full log contents are printed. Test with decoded and raw duplicate crash files to confirm decoded preference.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/generic/crash_report.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/generic/crash_watchdog.py -->
# sources/test-tools/kdevops/scripts/workflows/generic/crash_watchdog.py

## Purpose
CLI wrapper around `KernelCrashWatchdog` for detecting kernel crashes/warnings on one host or all active hosts and optionally resetting affected guests.

## Important APIs
`get_active_hosts()` uses `ansible-inventory -i hosts --list` and returns baseline hosts. `run_crash_watchdog_on_host(args, host)` constructs `KernelCrashWatchdog` and returns crash/warning status. `run_crash_watchdog_all_hosts(args)` loops over active hosts. `write_log_section()` can embed log snippets, though it is not used by `main()`.

## Control flow
`main()` parses host, output directory, collection method (`auto`, `remote`, `console`, `ssh`), full-log mode, decode/reset toggles, fstests-log extraction, and warning saving. If invoked as `get_console.py`, it adjusts options for console retrieval. It exits 1 when any crash is detected and 0 otherwise.

## State and dependencies
May write crash/warning files, decode stack traces, and reset hosts through the library. Depends on Ansible, PyYAML, SSH, journal access, and `lib.crash`.

## Risks and test signals
`--save-warnings` is declared as an option with a default `True` string rather than a boolean action, so CLI semantics are confusing. It can reset guests as part of a status run. Test with `--no-reset`, each collection method, single-host and all-host modes.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/generic/crash_watchdog.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/generic/get_console.py -->
# sources/test-tools/kdevops/scripts/workflows/generic/get_console.py

## Purpose
Provides the get-console entry point for the generic crash watchdog behavior.

## Important APIs and control flow
The file shares the `crash_watchdog.py` implementation pattern: when the invoked program name is `get_console.py`, the watchdog path disables reset, disables warning saving, and requests full log behavior. It delegates log collection to `KernelCrashWatchdog`.

## State and dependencies
Read-only intent, but actual behavior depends on the shared watchdog code and selected method. It may still read guestfs console logs, remote journals, or SSH journal output. Depends on the same Python modules and kdevops inventory/config files as `crash_watchdog.py`.

## Integration points
Used as a convenience command or symlink target for retrieving kernel console output without treating it as a crash response action.

## Risks and test signals
The shared code sets `args.full_log_mode = True`, while the library uses `full_log`; if this file is a copy rather than symlink, confirm the intended flag is actually passed. Test by invoking as `get_console.py` with `--no-reset` behavior and verifying no reset occurs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/generic/get_console.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/generic/kill_pids.sh -->
# sources/test-tools/kdevops/scripts/workflows/generic/kill_pids.sh

## Purpose
Shared process killer for workflow directories, supporting fstests, blktests, and reboot-limit based on the script's parent directory.

## Important APIs
`usage()`, `parse_args()`, and `list_pid()` implement CLI behavior. `CALL=$(basename $0)` decides list-only versus kill mode. `TARGET_WORFKLOW="$(basename $(dirname $0))"` selects workflow-specific config matching.

## Control flow
After sourcing `TOPDIR/.config` and `scripts/lib.sh`, the script validates the selected workflow is enabled, scans the user's process table, filters to same checkout and workflow config, skips kernel CI and baseline loop commands, and sends SIGTERM/SIGALRM to matching Make, run_loop, ansible-playbook, and SSH commands.

## State and persistence
Touches `$MANUAL_KILL_NOTICE_FILE` for manual kill notification and removes it at completion. Mutates process state.

## Dependencies and integration
Depends on `/proc`, shell tools, and kdevops config. Workflow-specific copies/symlinks reuse this body.

## Risks and test signals
The variable name `TARGET_WORFKLOW` is misspelled but consistently used. String process matching is broad. Use list mode first and test in isolated runs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/generic/kill_pids.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/lib/blktests.py -->
# sources/test-tools/kdevops/scripts/workflows/lib/blktests.py

## Purpose
Library routines for blktests watchdogs: process detection, last-test discovery, historical runtime lookup, config parsing, and host enumeration.

## Important APIs
`blktests_check_pid(host)` finds a remote `check` process and verifies its cwd has `tests`. `get_blktest_host(host, basedir, kernel, section, config)` returns `(last_test, last_test_time, current_time_str, delta_seconds, stall_suspect)`. `get_last_run_time()` reads prior runtime data. `get_config()`, `get_section()`, and `get_hosts()` parse kdevops config/inventory.

## Control flow
The host status function handles uname issues, missing last-test logs, SSH timeouts, missing running `check` process, then parses a `run blktests ... at ...` line. If watchdog config is enabled it compares elapsed time with either default new-test thresholds or historical runtime multiplied by configured factors.

## State and dependencies
Read-only over remote process/journal state and local `workflows/blktests/results/last-run/`. Depends on `lib.kssh`, `datetime`, `configparser`, and shell-style `.config` parsing.

## Integration points
Consumed by `blktests_watchdog.py`.

## Risks and test signals
`enable_watchdog` is a stripped string, so non-empty values such as `n` are truthy in Python. Runtime file search walks the whole last-run tree. Test with watchdog enabled/disabled configs and representative last-run files.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/lib/blktests.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/lib/crash.py -->
# sources/test-tools/kdevops/scripts/workflows/lib/crash.py

## Purpose
Implements kernel crash, warning, and filesystem corruption detection for kdevops hosts, with log collection from guestfs console logs, systemd remote journals, or SSH journalctl and optional libvirt reset.

## Important APIs and types
`KernelCrashWatchdog` is the main class. Important methods include `normalize_kernel_snippet()`, `get_qr_ascii()`, `load_known_crashes()`, `is_known_crash()`, `try_remote_journal()`, `convert_console_log()`, `check_host_reachable()`, `collect_journal()`, `detect_crash()`, `detect_filesystem_corruption()`, `infer_fstests_state()`, `extract_kernel_snippet()`, `decode_log_output()`, `save_log()`, `reset_host_now()`, `wait_for_ssh()`, `next_issue_filename()`, and `check_and_reset_host()`.

## Control flow
Construction reads `extra_vars.yaml` for provider, journal, guestfs, and topdir settings, then loads known issue hashes from existing crash files. `check_and_reset_host()` filters stale issue files by boot time, collects logs using console, remote journal, then SSH according to method/config, normalizes logs, optionally trims already-seen console lines, infers fstests context, saves warnings if requested, suppresses expected fstests corruption, extracts a relevant snippet, writes a new issue file with a QR code, decodes stack traces when possible, resets libvirt hosts, and waits for SSH.

## State and persistence
Persists numbered `journal-XXXX.crash`, `.corruption`, `.crash_and_corruption`, `.warning`, and decoded variants under `output_dir/host`. Maintains known-crash hashes in memory and may remove stale files older than last boot.

## Dependencies and integration
Uses PyYAML, qrcode, SSH, journalctl, guestfs console logs, libvirt `virsh`, Ansible wait_for_connection, and `linux/scripts/decode_stacktrace.sh`.

## Risks and test signals
Detection is regex-based and broad; false positives can reset hosts. `warnings` list is unused, so warning-only reset suppression relies on `warning_file`. The intentional-corruption list must stay current with fstests. Test with synthetic logs for panic, warning, benign warning, expected and unexpected corruption, duplicate issue suppression, and `--no-reset`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/lib/crash.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/lib/debug_print_filesystem_sections.sh -->
# sources/test-tools/kdevops/scripts/workflows/lib/debug_print_filesystem_sections.sh

## Purpose
Debug helper that prints configured fstests filesystem sections for ext4, xfs, and btrfs.

## Important APIs and control flow
The script sets `TOPDIR=$PWD`, sources `scripts/workflows/fstests/ext4/lib.sh`, `btrfs/lib.sh`, and `xfs/lib.sh`, then echoes `EXT4_SECTIONS`, `XFS_SECTIONS`, and `BTRFS_SECTIONS`.

## State and dependencies
No persistent state. It depends on being run from the kdevops root and on the filesystem-specific helper libraries defining the section variables.

## Integration points
Located under `workflows/lib`, so it is shared support for filesystem workflow debugging and configuration inspection.

## Risks and test signals
It forcibly sets `TOPDIR` to the current directory, so running outside the repository root breaks the source paths. Test by invoking from the root and verifying non-empty section lists for enabled filesystem helpers.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/lib/debug_print_filesystem_sections.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/lib/fstests.py -->
# sources/test-tools/kdevops/scripts/workflows/lib/fstests.py

## Purpose
Library routines for fstests watchdogs, including running-process checks, current test discovery, stall estimation, soak-duration handling, config parsing, and inventory host extraction.

## Important APIs
`fstests_check_pid(host)`, `fstests_test_uses_soak_duration(testname)`, `get_fstest_host(use_remote, use_ssh, host, basedir, kernel, section, config)`, `get_checktime(host, basedir, kernel, section, last_test)`, `get_config(dotconfig)`, `get_section(host, config)`, and `get_hosts(hostfile, hostsection)`.

## Control flow
`get_fstest_host()` chooses SSH or systemd-remote journal based on config/options, parses the last `run fstests ... at ...` line, ignores completed sentinel tests, computes elapsed seconds, loads configured watchdog thresholds, adds soak duration for known soak tests, and marks stalls when elapsed time exceeds threshold outside start/end sentinels.

## State and dependencies
Read-only over remote process/journal state and local `workflows/fstests/results/<host>/<kernel>/<section>/check.time`. Depends on `lib.kssh`, `lib.systemd_remote`, `datetime`, and `configparser`.

## Integration points
Consumed by `fstests_watchdog.py`.

## Risks and test signals
Like blktests, stripped config strings are truthy even if value is `n`. The soak test list is hard-coded and can go stale. Test with SSH and remote journal modes, timezone-suffixed timestamps, missing `check.time`, and soak tests.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/lib/fstests.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/lib/kssh.py -->
# sources/test-tools/kdevops/scripts/workflows/lib/kssh.py

## Purpose
Provides SSH-based helpers for workflow watchdogs to query remote process, program, kernel, test, and time state.

## Important APIs and types
Exceptions: `KsshError`, `ExecutionError`, `TimeoutExpired`. Functions: `_check()`, `dir_exists(host, dirname)`, `first_process_name_pid(host, process_name)`, `prog_exists(host, prog)`, `get_uname(host)`, `get_test(host, suite)`, `get_last_fstest(host)`, `get_last_blktest(host)`, and `get_current_time(host)`.

## Control flow
Each helper runs an SSH command via `subprocess.Popen`, waits up to 120 seconds, and converts return codes/timeouts into booleans or sentinel strings such as `Timeout` and `Uname-issue`. `get_test()` chooses `journalctl -k -g` when available, otherwise `dmesg`, then extracts the last `run <suite> ... at ...` line.

## State and dependencies
No persistence. Requires SSH, sudo on targets for several commands, remote `ps`, `which`, `journalctl` or `dmesg`, and local subprocess support.

## Integration points
Used by fstests and blktests libraries and watchdog scripts.

## Risks and test signals
Commands are passed as argument lists containing shell metacharacters like `|`, so behavior depends on SSH joining remote command arguments as intended. `first_process_name_pid()` casts stdout to int and can fail if multiple lines leak through. Test against reachable, unreachable, and sudo-limited hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/lib/kssh.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/lib/systemd_remote.py -->
# sources/test-tools/kdevops/scripts/workflows/lib/systemd_remote.py

## Purpose
Reads systemd-journal-remote files for host kernel versions, current time, and last workflow test markers.

## Important APIs
Exceptions mirror the SSH module. `get_host_ip(host)` resolves SSH config hostname via `ssh -G`. `get_current_time(host)` returns local current time. `get_extra_journals(remote_path, host)` finds rotated/suffixed remote journal files for the host IP. `get_uname(remote_path, host, configured_kernel)` extracts the last `Linux version` line. `get_test(remote_path, host, suite)` extracts the latest `run fstests` or `run blktests` marker. `get_last_fstest()` and `get_last_blktest()` wrap `get_test()`.

## Control flow
The module maps a host to `remote-<ip>.journal`, adds extra matching files, then runs `journalctl --no-pager -k -g ... --file ...`. On missing kernel version it can return the configured kernel fallback.

## State and dependencies
Read-only over `/var/log/journal/remote` style files. Requires `ssh -G`, `journalctl`, file permissions for remote journals, and local time.

## Integration points
Used by `fstests.py` and `fstests_watchdog.py` when systemd remote journal support is configured.

## Risks and test signals
`logger.warning` is referenced without defining `logger`. Current time is local host time, not remote journal host time. Test with complete journal files, rotated extra journals, missing `Linux version`, and missing permissions.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/lib/systemd_remote.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/pynfs/check_pynfs_results.py -->
# sources/test-tools/kdevops/scripts/workflows/pynfs/check_pynfs_results.py

## Purpose
Compares new pynfs JSON results against a baseline JSON result set and reports newly failing test cases.

## Important APIs and control flow
`main()` loads `sys.argv[1]` as baseline and `sys.argv[2]` as result. It builds a dictionary of failures from `result["testcase"]` keyed by `case["code"]`, removes any failures already present in the baseline, pretty-prints remaining failures, and exits 1 if any remain; otherwise exits 0.

## State and dependencies
Read-only over two JSON files. Uses Python `json`, `sys`, and `pprint`.

## Integration points
Suitable for CI gates where only regressions relative to a known pynfs baseline should fail the run.

## Risks and test signals
There is no argument validation or schema validation; missing files, invalid JSON, missing `testcase`, or missing `code` will raise tracebacks. Test with no new failures, one new failure, existing baseline failures, and malformed input handling if used in CI.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/pynfs/check_pynfs_results.py -->
