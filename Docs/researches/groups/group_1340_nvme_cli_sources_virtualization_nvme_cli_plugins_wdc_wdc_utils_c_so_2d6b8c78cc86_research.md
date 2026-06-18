# Group Research: group_1340_nvme_cli_sources_virtualization_nvme_cli_plugins_wdc_wdc_utils_c_so_2d6b8c78cc86

Scope: `Docs/research_subset_a.md`, source tree `sources/virtualization/nvme-cli`.

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/wdc/wdc-utils.c -->
# File Research: sources/virtualization/nvme-cli/plugins/wdc/wdc-utils.c

Implements Western Digital plugin utility routines used by WDC-specific nvme-cli commands.

Key elements:
- Wraps `vsnprintf` as `wdc_UtilsSnprintf`.
- Provides string utilities for deleting a character, case-insensitive compare, and fixed-width string formatting with trailing-space trimming.
- Provides local time extraction into `UtilsTimeInfo`, including timezone handling via `tm_gmtoff` when available or `timezone` fallback.
- Creates directories with WDC-specific status code mapping.
- Appends buffers to files with explicit partial-write status handling.
- Checks controller UUID-list support by running Identify Controller, checking `NVME_CTRL_CTRATT_UUID_LIST`, and retrieving the UUID list.

Dependencies:
- Uses libnvme identify helpers, nvme-cli status/error display helpers, and WDC status constants from `wdc-utils.h`.

Notes:
- `mkdir(path, 0x999)` is unusual permission syntax and depends on normal mode masking; it is preserved upstream behavior.
- `wdc_UtilsStrCompare` compares with `toupper` but subtracts original characters, so ordering is not fully case-folded even though equality is case-insensitive.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/wdc/wdc-utils.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/wdc/wdc-utils.h -->
# File Research: sources/virtualization/nvme-cli/plugins/wdc/wdc-utils.h

Header for WDC plugin utility helpers.

Key elements:
- Defines WDC utility status codes for success, invalid parameter, memory errors, file/directory errors, and archive-related failures.
- Defines constants for firmware revision length, serial length, seconds per minute, and max path length.
- Defines `UtilsTimeInfo`, a simple local-time structure with year/month/day/hour/min/sec, DST flag, milliseconds, and timezone offset.
- Declares WDC string, file, directory, time, formatting, and UUID-list support helpers.

Dependencies:
- Pulls in standard C headers, POSIX stat/time headers, and expects libnvme types for `struct libnvme_transport_handle` and `struct nvme_id_uuid_list`.

Notes:
- This header includes many implementation headers directly; users get a broad include surface.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/wdc/wdc-utils.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ymtc/ymtc-nvme.c -->
# File Research: sources/virtualization/nvme-cli/plugins/ymtc/ymtc-nvme.c

Implements the YMTC vendor plugin command `smart-log-add`.

Key elements:
- Registers through `ymtc-nvme.h` using `CREATE_CMD`.
- Fetches a vendor-specific SMART log page with log ID `0xca` via `nvme_get_nsid_log`.
- Supports `--namespace-id` and `--raw-binary`.
- In formatted mode, identifies the controller to obtain firmware revision and prints selected normalized/raw vendor SMART attributes.
- Converts several 48-bit raw fields with `int48_to_long`.
- Handles allocation failures for temporary normalized/raw buffers and reports NVMe positive status codes.

Dependencies:
- Uses `ymtc-utils.h` for log item layout and attribute indexes.
- Uses nvme-cli parsing/opening helpers, raw dump helper `d_raw`, and libnvme transport handles.

Notes:
- Raw fields are accessed through casts like `*(uint16_t *)raw`; this assumes acceptable alignment and host endianness for this plugin’s target behavior.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ymtc/ymtc-nvme.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ymtc/ymtc-nvme.h -->
# File Research: sources/virtualization/nvme-cli/plugins/ymtc/ymtc-nvme.h

Command registration header for the YMTC vendor plugin.

Key elements:
- Sets `CMD_INC_FILE` to `plugins/ymtc/ymtc-nvme`.
- Defines plugin name `ymtc` with description `Ymtc vendor specific extensions`.
- Registers one command: `smart-log-add`, mapped to `get_additional_smart_log`.
- Includes the common command registration machinery and `define_cmd.h`.

Dependencies:
- Consumed by `ymtc-nvme.c` under `CREATE_CMD`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ymtc/ymtc-nvme.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ymtc/ymtc-utils.h -->
# File Research: sources/virtualization/nvme-cli/plugins/ymtc/ymtc-utils.h

Defines YMTC vendor SMART-log data structures and attribute indexes.

Key elements:
- Defines the vendor SMART log size as 4096 bytes.
- Defines per-item component sizes: 3-byte ID, 2-byte normalized value, 7-byte raw value.
- Lists YMTC external SMART attribute IDs such as program fail, erase fail, wear leveling, PCIe CRC errors, writes, reads, temperature, and power loss protection.
- Defines internal enum indexes used to address `itemArr`.
- Defines `nvme_ymtc_smart_log_item` and `nvme_ymtc_smart_log`, with padding to a 4096-byte log page.

Dependencies:
- Used by `ymtc-nvme.c` to interpret log ID `0xca`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ymtc/ymtc-utils.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/zns/zns.c -->
# File Research: sources/virtualization/nvme-cli/plugins/zns/zns.c

Implements the Zoned Namespace Command Set plugin.

Key command areas:
- `list`: scans libnvme topology and displays namespaces whose sysfs `queue/zoned` attribute is `host-managed`.
- `id-ctrl`: issues ZNS Identify Controller via admin passthrough and prints in selected output format.
- `id-ns`: identifies base namespace and ZNS namespace data, then prints combined ZNS namespace information.
- Zone management send wrappers: reset, close, finish, open, offline, set descriptor extension, ZRWA flush, and generic `zone-mgmt-send`.
- Zone management receive and report paths: `zone-mgmt-recv`, `report-zones`, and `changed-zone-list`.
- `zone-append`: reads data/metadata from files or stdin, validates LBA/metadata alignment, sets command control flags, issues append, and optionally prints latency.

Important behaviors:
- Defaults namespace ID from the opened device when `--namespace-id` is omitted.
- Computes zone descriptor extension bytes from ZNS identify namespace data using active LBA format.
- `report_zones` first reads total zone count, allocates huge memory for chunked zone reports, then iterates chunks using zone size to advance offsets.
- Uses nvme-cli output flag validation and JSON/list helpers for formatted output.
- Uses cleanup attributes for libnvme contexts and allocated buffers where available.

Dependencies:
- Uses libnvme admin and IO passthrough initializers for ZNS commands.
- Uses `nvme-print` ZNS display functions and nvme-cli argument parser macros.

Notes:
- `zone_append` calls `libnvme_exec_admin_passthru` after initializing a ZNS append command; append is an I/O command, so this is a point worth checking against current libnvme expectations.
- Metadata buffer allocation uses `meta_size` while reading `cfg.metadata_size`; if metadata size can exceed one metadata element, this path deserves scrutiny.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/zns/zns.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/zns/zns.h -->
# File Research: sources/virtualization/nvme-cli/plugins/zns/zns.h

Command registration header for the ZNS plugin.

Key elements:
- Sets `CMD_INC_FILE` to `plugins/zns/zns`.
- Registers plugin name `zns` with description `Zoned Namespace Command Set`.
- Registers ZNS commands including list, identify controller/namespace, report zones, zone reset/close/finish/open/offline, descriptor extension, ZRWA flush, changed zone list, management send/receive, and zone append.
- Includes `define_cmd.h` for command table generation.

Dependencies:
- Consumed by `zns.c` under `CREATE_CMD`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/zns/zns.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/pyproject.toml -->
# File Research: sources/virtualization/nvme-cli/pyproject.toml

Python packaging metadata for libnvme bindings.

Key elements:
- Uses `mesonpy` as build backend with requirements: `meson-python`, `meson`, `ninja`, and `swig`.
- Publishes project name `libnvme`, dynamic version, LGPL-2.1-or-later license text, and Python `>=3.6`.
- Declares homepage/source/bug tracker URLs pointing at linux-nvme/nvme-cli.
- Configures meson-python setup arguments to disable nvme CLI, enable libnvme and Python, enable PyPI mode, and disable tests/examples.

Role:
- Supports building Python bindings from the same source tree without building the CLI tools or test suites.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/pyproject.toml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/scripts/build.sh -->
# File Research: sources/virtualization/nvme-cli/scripts/build.sh

CI build orchestration script for nvme-cli.

Key elements:
- Supports Meson and Muon build tools.
- Options select build type, compiler, build tool, coverage, sanitizer setup, cross target, and valgrind setup.
- Provides Meson configs for default, musl, libdbus, fallback dependencies, cross compile, docs variants, static builds, minimal static builds, no-fabrics builds, tests, libnvme-only, and distro split build.
- Provides Muon default config and bootstrap helpers for Samurai and Muon if missing.
- Runs configure, compile, tests, optional coverage via `gcovr`, and config-specific install when defined.

Notable config behavior:
- Static/minimal static configs disable several dependencies and tests.
- `distro` first installs libnvme into the CI build prefix, then builds nvme-cli against that installed dependency.
- Sanitizer and valgrind are implemented as Meson test setups.
- Script deletes `.build-ci` before each run.

Dependencies:
- Requires git top-level discovery, Meson/Muon/Ninja/Samurai, compiler toolchains, and optional tools such as valgrind/gcovr.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/scripts/build.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/scripts/gen-hostnqn.sh -->
# File Research: sources/virtualization/nvme-cli/scripts/gen-hostnqn.sh

Minimal helper script that invokes:

- `nvme gen-hostnqn`

Role:
- Generates an NVMe host NQN using the installed or built `nvme` command available on `PATH`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/scripts/gen-hostnqn.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/scripts/latency -->
# File Research: sources/virtualization/nvme-cli/scripts/latency

Shell script for simple QD=1 read/write latency sampling through nvme-cli.

Key elements:
- Accepts `-d DEVICE`, `-n COUNT`, and `-w` for write mode.
- Requires a nonzero count and a device path.
- Runs `make clean` and `make install` before tests.
- In read mode, repeatedly runs `nvme read` with `--latency`.
- In write mode, creates random data, runs `nvme write` with `--latency`, and warns that write mode can overwrite drive data.
- Extracts latency values into `latency.dat` and computes average microseconds with `bc`.

Notes:
- This is a destructive-capable manual helper, not a Meson test.
- Assumes the `nvme` command installed by `make install` is used.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/scripts/latency -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/scripts/meson-vcs-tag.sh -->
# File Research: sources/virtualization/nvme-cli/scripts/meson-vcs-tag.sh

Meson helper for deriving a version tag from git.

Key elements:
- Requires source directory and fallback version arguments.
- Changes into the source directory before running git to avoid dirty-tree false positives with `--git-dir`.
- If `.git` exists, runs `git describe --abbrev=7 --dirty=+` and strips a leading `v`.
- Falls back to the provided fallback string when no `.git` metadata exists.

Role:
- Supplies build-time version strings for Meson builds, including tarball builds without git metadata.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/scripts/meson-vcs-tag.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/scripts/regress -->
# File Research: sources/virtualization/nvme-cli/scripts/regress

Manual regression shell script for basic nvme-cli commands.

Key elements:
- Accepts `-d DEVICE`, `-w` for write mode, and `-l` to include `nvme list`.
- Requires a device path.
- Runs `make clean` and `make install`.
- Executes identify, namespace list, log, feature, flush, read, and optionally write/diff commands.
- Uses colorized pass/fail output and exits on first failure.
- Write mode uses random data and warns that it can overwrite the drive.

Role:
- Legacy/manual smoke test below the Python/Meson TAP test infrastructure.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/scripts/regress -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/scripts/release.sh -->
# File Research: sources/virtualization/nvme-cli/scripts/release.sh

Release automation script.

Key elements:
- Accepts `VERSION` plus flags to skip docs, force sanity checks, or skip library dependency update.
- Validates versions like `v2.1`, `v2.1.0`, or pre-release forms such as `-rc.0`.
- Registers cleanup that deletes created tags and resets to the original HEAD unless release completes.
- Requires clean tree and `master` branch unless forced.
- Optionally regenerates docs via `scripts/update-docs.sh` and commits them.
- Updates `meson.build` version with `sed`, commits, creates a signed tag, dry-runs push, then asks before pushing.

Notes:
- Uses destructive git operations in cleanup (`git reset --hard`) by design for release rollback.
- Mentions `dry_run` in a branch although no `dry_run` variable is defined in this file.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/scripts/release.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/scripts/update-docs.sh -->
# File Research: sources/virtualization/nvme-cli/scripts/update-docs.sh

Documentation regeneration script.

Key elements:
- Creates a temporary Meson build directory and removes it on exit.
- Configures Meson with nvme, libnvme, all docs, and docs build enabled.
- Compiles the build.
- Replaces generated libnvme man pages, RST files, `conf.py`, `index.rst`, and config schema.
- Copies generated nvme-cli `.1` man pages and `.html` files into `Documentation/`.

Role:
- Used by release automation to refresh generated documentation artifacts.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/scripts/update-docs.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/tests/config.json -->
# File Research: sources/virtualization/nvme-cli/tests/config.json

Default Python test configuration.

Fields:
- `controller`: `/dev/nvme0`
- `ns1`: `/dev/nvme0n1`
- `log_dir`: `nvmetests`
- `log_level`: `DEBUG`

Role:
- Loaded by `TestNVMe` to select the controller, namespace, log directory, and logging verbosity for hardware-backed tests.

Notes:
- Defaults target real NVMe device nodes and can be destructive for namespace-management tests.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/tests/config.json -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/tests/meson.build -->
# File Research: sources/virtualization/nvme-cli/tests/meson.build

Meson definition for Python integration tests and Python lint/format targets.

Key elements:
- Lists test infrastructure files and concrete test modules.
- Runs each test module through `tap_runner.py --start-dir <tests_dir> <module>`.
- Sets `PATH` so the project build root precedes system binary paths.
- Uses TAP protocol, serial execution, and 500-second timeout.
- Adds optional `lint-python` target when `mypy` and `flake8` are found.
- Adds optional `format-python` target when `autopep8` and `isort` are found.

Role:
- Integrates hardware-backed Python tests into Meson while producing TAP output.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/tests/meson.build -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_attach_detach_ns_test.py -->
# File Research: sources/virtualization/nvme-cli/tests/nvme_attach_detach_ns_test.py

Python integration test for namespace create/attach/detach/delete.

Flow:
- Inherits `TestNVMe`.
- Skips if namespace management/attachment is unsupported.
- Computes namespace size from controller NVM capacity and active LBA format.
- Deletes all namespaces in setup.
- Creates namespace 1, attaches it, runs simple I/O, detaches it, deletes it, and resets the controller.
- Tear down recreates and attaches the primary namespace.

Risk:
- Destructive by design: deletes namespaces on the configured controller.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_attach_detach_ns_test.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_compare_test.py -->
# File Research: sources/virtualization/nvme-cli/tests/nvme_compare_test.py

Python integration test for the NVMe Compare command.

Flow:
- Inherits `TestNVMeIO`.
- Skips if Optional NVM Command Support does not advertise Compare.
- Writes a patterned block at start block 1023.
- Compares against a different pattern and expects failure.
- Compares against the written pattern and expects success.
- Handles separate metadata namespaces by creating metadata buffers and passing `--metadata-size`/`--metadata`.

Dependencies:
- Uses `TestNVMeIO` for PI/metadata-aware data size and write command construction.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_compare_test.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_copy_test.py -->
# File Research: sources/virtualization/nvme-cli/tests/nvme_copy_test.py

Python integration tests for NVMe Copy descriptor formats.

Structure:
- `TestNVMeCopy`: shared base for copy tests.
- `TestNVMeCopyFormat0`: in-namespace copy with descriptor format 0.
- `TestNVMeCopyFormat1`: in-namespace copy with descriptor format 1 after reformatting to 64-bit guard PI.
- `TestNVMeCopyFormat23`: cross-namespace copy with descriptor formats 2 and 3, including `sopts` variants.

Key behaviors:
- Reads Optional Copy Formats Supported (`ocfs`) and namespace copy limits (`mcl`, `mssrl`, `msrc`).
- Skips unsupported descriptor formats or namespaces with zero copy limits.
- Detects current PIF from `id-ns` and `nvm-id-ns`.
- Can recreate namespace 1 with a chosen LBA format when namespace management is supported.
- Enables Host Behavior Support CDFE bits for cross-namespace descriptor formats and restores the original CDFE in teardown.
- Runs `nvme copy` with destination LBA, source block list, descriptor format, optional source namespace ID, and optional source options.

Risk:
- Can reformat/delete/recreate namespaces for 64-bit guard copy tests.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_copy_test.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_create_max_ns_test.py -->
# File Research: sources/virtualization/nvme-cli/tests/nvme_create_max_ns_test.py

Python integration test for creating the maximum advertised number of namespaces.

Flow:
- Skips if namespace management/attachment is unsupported.
- Computes per-namespace capacity from total NVM capacity divided by max namespace count, then halves it for headroom.
- Deletes all namespaces.
- Iterates from namespace ID 1 through `nn`, creating, attaching, and running one-block I/O on each namespace.
- Detaches and deletes every namespace, then resets controller.
- Tear down recreates namespace 1.

Risk:
- Highly destructive and potentially long-running on controllers with many namespace slots.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_create_max_ns_test.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_ctrl_reset_test.py -->
# File Research: sources/virtualization/nvme-cli/tests/nvme_ctrl_reset_test.py

Python integration test for controller reset.

Flow:
- Runs `nvme reset <controller>`.
- After reset, runs simple namespace I/O to verify queues are usable again.

Dependencies:
- Uses shared `TestNVMe.run_ns_io`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_ctrl_reset_test.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_dsm_test.py -->
# File Research: sources/virtualization/nvme-cli/tests/nvme_dsm_test.py

Python integration test for Dataset Management.

Flow:
- Sets namespace ID 1, start block 0, and range 0.
- Runs `nvme dsm <controller> --namespace-id=1 --blocks=0 --slbs=0`.
- Expects success.

Notes:
- The docstring says verify in one helper comment, but the command is DSM.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_dsm_test.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_error_log_test.py -->
# File Research: sources/virtualization/nvme-cli/tests/nvme_error_log_test.py

Python integration test for error log retrieval.

Flow:
- Calls shared `get_error_log`.
- The shared helper runs `nvme error-log`, parses normal text output, and checks the printed entry count against the number of `Entry[...]` lines.

Role:
- Verifies command success and a basic consistency property of human-readable output.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_error_log_test.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_flush_test.py -->
# File Research: sources/virtualization/nvme-cli/tests/nvme_flush_test.py

Python integration test for Flush.

Flow:
- Runs `nvme flush <controller> --namespace-id=1`.
- Expects success.

Role:
- Simple command smoke test against the configured controller/default namespace.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_flush_test.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_format_test.py -->
# File Research: sources/virtualization/nvme-cli/tests/nvme_format_test.py

Python integration test for namespace formats.

Flow:
- Skips if namespace management/attachment is unsupported.
- Creates a small primary namespace, attaches it, reads `id-ns --output-format=json`, and captures `lbafs`.
- Detaches/deletes namespace and resets controller.
- Iterates every advertised LBA format, creates namespace 1 with that format, attaches it, runs I/O, detaches, deletes, and resets.
- Uses `dps=1` when metadata size string equals `8`, otherwise `0`.
- Tear down recreates namespace 1.

Risk:
- Destructive and format-changing by design.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_format_test.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_fw_log_test.py -->
# File Research: sources/virtualization/nvme-cli/tests/nvme_fw_log_test.py

Python integration test for firmware log retrieval.

Flow:
- Runs `nvme fw-log <controller>`.
- Expects success.

Role:
- Basic firmware log command smoke test.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_fw_log_test.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_get_features_test.py -->
# File Research: sources/virtualization/nvme-cli/tests/nvme_get_features_test.py

Python integration test for mandatory Get Features IDs.

Flow:
- Tests feature IDs `0x01`, `0x02`, `0x04`, `0x05`, `0x07`, `0x08`, `0x09`, `0x0A`, and `0x0B`.
- Determines interrupt vector count by grepping `/proc/interrupts` for controller queue names.
- For Interrupt Vector Configuration (`0x09`), loops over detected vectors and passes `--cdw11`.
- For Error Recovery (`0x05`), includes namespace ID.
- Uses `--human-readable` for all feature commands.

Dependencies:
- Requires Linux `/proc/interrupts` layout and controller queue naming.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_get_features_test.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_get_lba_status_test.py -->
# File Research: sources/virtualization/nvme-cli/tests/nvme_get_lba_status_test.py

Python integration test for Get LBA Status.

Flow:
- Skips unless Identify Controller OACS bit 9 indicates Get LBA Status support.
- Runs `nvme get-lba-status` with namespace, start LBA 0, max DW 1, action `0x11`, and range length 1.
- Expects success.

Notes:
- The command uses `self.ctrl` and passes `--namespace-id` as `self.ns1`, which is a device path string from config rather than numeric `1`; this is worth checking against command parser expectations.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_get_lba_status_test.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_id_ctrl_test.py -->
# File Research: sources/virtualization/nvme-cli/tests/nvme_id_ctrl_test.py

Python integration test for Identify Controller.

Flow:
- Runs normal `nvme id-ctrl <controller>`.
- Runs vendor-specific `nvme id-ctrl --vendor-specific <controller>`.
- Expects both to succeed.

Role:
- Exercises both standard and vendor-specific identify controller output paths.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_id_ctrl_test.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_id_ns_test.py -->
# File Research: sources/virtualization/nvme-cli/tests/nvme_id_ns_test.py

Python integration test for Identify Namespace.

Flow:
- Collects namespace list via `nvme list-ns --output-format=json`.
- Runs `nvme id-ns <controller> --namespace-id=1`.
- Iterates every namespace from `nsid_list` and runs `id-ns`.
- Expects success for all.

Dependencies:
- Uses shared JSON parsing and namespace-list helpers from `TestNVMe`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_id_ns_test.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_lba_status_log_test.py -->
# File Research: sources/virtualization/nvme-cli/tests/nvme_lba_status_log_test.py

Python integration test for LBA Status Log.

Flow:
- Skips unless OACS bit 9 indicates Get LBA Status support.
- Runs `nvme lba-status-log <controller>`.
- Expects success.

Role:
- Smoke test for the log-page counterpart to Get LBA Status.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_lba_status_log_test.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_read_write_test.py -->
# File Research: sources/virtualization/nvme-cli/tests/nvme_read_write_test.py

Python integration test for read/write round trip.

Flow:
- Inherits `TestNVMeIO`.
- Writes a patterned file to start block 1023.
- Reads the block back into another file.
- Compares the files with `filecmp.cmp`.
- Creates metadata buffers when active namespace uses separate metadata.

Dependencies:
- Uses `TestNVMeIO` to select data size and PI/metadata options.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_read_write_test.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_simple_template_test.py -->
# File Research: sources/virtualization/nvme-cli/tests/nvme_simple_template_test.py

Template/example Python test.

Key elements:
- Inherits `TestNVMe`.
- Sets up a per-test log directory.
- Defines placeholder `simple_template_test`.
- Test method calls the placeholder and therefore performs no command-specific assertions.

Role:
- Serves as a starting pattern for adding new tests.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_simple_template_test.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_smart_log_test.py -->
# File Research: sources/virtualization/nvme-cli/tests/nvme_smart_log_test.py

Python integration test for SMART log retrieval.

Flow:
- Runs controller-wide SMART log using namespace ID `0xFFFFFFFF`.
- Reads Identify Controller `lpa`.
- If SMART/health information is namespace-specific, iterates namespaces and runs SMART log for each.
- Expects all invoked commands to succeed.

Dependencies:
- Uses shared `get_smart_log`, `get_nsid_list`, and numeric conversion helper.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_smart_log_test.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_test.py -->
# File Research: sources/virtualization/nvme-cli/tests/nvme_test.py

Shared base class and utility library for nvme-cli Python integration tests.

Key elements:
- Loads `config.json` for controller, namespace, log directory, optional binary path, PCI validation flag, and log level.
- Validates the configured controller is PCI-backed by searching `/sys/devices`.
- Detects namespace management/attachment support from Identify Controller OACS bits.
- If namespace management is supported, recreates and attaches default namespace 1 in setup and teardown.
- Provides robust JSON parsing helpers with typed assertions.
- Wraps command execution through `subprocess.run(shell=True)` with logging.
- Provides helpers for reset, controller ID, namespace list, max namespace count, LBA status support, active LBA format, DPS/PIF, metadata extension, LBA format size, NVM capacity, identify field extraction, copy format support, namespace create/attach/detach/delete, SMART/error logs, and simple namespace I/O.

Important behavior:
- The base setup can delete all namespaces when namespace management is supported.
- `run_ns_io` uses `dd` reads and zero writes against the namespace block device.
- `setup_log_dir` redirects stdout/stderr to `TestNVMeLogger`.

Role:
- Central fixture for all hardware-backed Python tests.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_test.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_test_io.py -->
# File Research: sources/virtualization/nvme-cli/tests/nvme_test_io.py

Shared read/write helper subclass for Python tests.

Key elements:
- Determines active data size, metadata size, PI type, metadata transfer mode, and `prinfo`.
- Handles three major cases:
  - PI active with extended LBA: uses `prinfo=8` so controller inserts/strips PI.
  - PI active with separate metadata: uses `prinfo=0` and explicit zero metadata buffers.
  - No PI: includes metadata bytes in data size only for extended LBA mode.
- Provides data-file creation with repeated text pattern.
- Provides binary zero metadata file creation.
- Builds `nvme write` and `nvme read` commands with data, optional `--prinfo`, and optional metadata file arguments.

Role:
- Keeps data/metadata/PI command construction consistent across compare, read/write, write-zeroes, and write-uncorrectable tests.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_test_io.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_test_logger.py -->
# File Research: sources/virtualization/nvme-cli/tests/nvme_test_logger.py

Simple stdout/stderr tee logger for Python tests.

Key elements:
- Stores the original `sys.stdout` in `terminal`.
- Opens a log file for writing.
- `write` sends every message to both terminal and log file.
- `flush` is a no-op for Python 3 compatibility.

Role:
- Used by `TestNVMe.setup_log_dir` to capture per-test stdout/stderr while still printing to the terminal/TAP diagnostic stream.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_test_logger.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_verify_test.py -->
# File Research: sources/virtualization/nvme-cli/tests/nvme_verify_test.py

Python integration test for NVMe Verify.

Flow:
- Checks Optional NVM Command Support bit 7 for Verify.
- Skips if unsupported.
- Runs `nvme verify <controller> --namespace-id=1 --start-block=0 --block-count=0`.
- Expects success.

Role:
- Capability-gated smoke test for the Verify command.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_verify_test.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_writeuncor_test.py -->
# File Research: sources/virtualization/nvme-cli/tests/nvme_writeuncor_test.py

Python integration test for Write Uncorrectable.

Flow:
- Inherits `TestNVMeIO`.
- Skips unless Optional NVM Command Support bit 1 is set.
- Reads a block successfully.
- Issues `nvme write-uncor` at start block 1023.
- Expects a subsequent read to fail.
- Writes valid data and then expects read to succeed again.

Risk:
- Intentionally marks media logical block state uncorrectable during the test.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_writeuncor_test.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_writezeros_test.py -->
# File Research: sources/virtualization/nvme-cli/tests/nvme_writezeros_test.py

Python integration test for Write Zeroes.

Flow:
- Inherits `TestNVMeIO`.
- Writes patterned data to start block 1023.
- Reads it back and verifies it matches.
- Runs `nvme write-zeroes` on the same block.
- Reads again and verifies data matches a locally generated zero-filled file.
- Handles separate metadata buffer setup for writes/reads.

Role:
- End-to-end validation that write-zeroes changes the target block to zeros.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/tests/nvme_writezeros_test.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/tests/run_py_linters.py -->
# File Research: sources/virtualization/nvme-cli/tests/run_py_linters.py

Helper script for Meson Python lint and format targets.

Key elements:
- Reads `MESON_SOURCE_ROOT` and `MESON_BUILD_ROOT`.
- Targets the `tests` directory.
- `lint` mode runs `flake8` and strict `mypy` with Python 3.8, namespace packages, ignored missing imports, and a build-dir mypy cache.
- `format` mode gathers Python files and runs `autopep8 --in-place` followed by `isort` with vertical hanging indent and trailing commas.
- Does not fail fast because subprocess calls use `check=False`.

Role:
- Provides optional developer tooling targets rather than mandatory test enforcement.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/tests/run_py_linters.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/tests/tap_runner.py -->
# File Research: sources/virtualization/nvme-cli/tests/tap_runner.py

TAP version 13 runner for Python unittest modules.

Key elements:
- Imports a named test module, loads tests with `unittest.TestLoader`, and emits TAP header and plan.
- `TAPDiagnosticStream` prefixes test stdout lines with `# ` so regular output remains TAP-compliant diagnostics.
- `TAPTestResult` emits `ok`, `not ok`, `# SKIP`, and TODO-style expected/unexpected failure lines.
- Failures/errors include YAML-ish traceback diagnostics on stderr.
- CLI supports `--start-dir` to prepend tests directory to `sys.path`.

Notable behavior:
- `main` always exits `0` after running tests, regardless of `result.wasSuccessful()`. Meson TAP parsing may still detect `not ok`, but process status alone will not indicate failure.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/tests/tap_runner.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/types.h -->
# File Research: sources/virtualization/nvme-cli/types.h

Defines nvme-cli wrapper argument structure for Get Log.

Key element:
- `struct nvme_get_log_args` carries namespace ID, RAE, LSP, LID, LSI, CSI, offset type, UUID index, log page offset, destination buffer, length, and command result pointer.

Dependencies:
- Includes `<nvme/nvme-types.h>` for NVMe integer and enum types.

Role:
- Local CLI-side argument bundle for Admin Get Log operations.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/types.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/unit/meson.build -->
# File Research: sources/virtualization/nvme-cli/unit/meson.build

Meson definition for C unit tests.

Targets:
- `test-uint128` using `test-uint128.c`, `util/types.c`, and `util/suffix.c`.
- `test-suffix-si-parse` using `util/suffix.c`.
- `test-suffix-binary-parse` using `util/suffix.c`.
- `test-uint128-si` using `util/types.c` and `util/suffix.c`.
- `test-argconfig-parse` using `util/argconfig.c` and `util/suffix.c`.

Dependencies:
- `config_dep`, `ccan_dep`, and `libnvme_dep`.

Role:
- Adds focused parser/formatting tests to Meson’s test suite.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/unit/meson.build -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/unit/test-argconfig-parse.c -->
# File Research: sources/virtualization/nvme-cli/unit/test-argconfig-parse.c

C unit test for `util/argconfig.c`.

Coverage:
- Tests parsing of flags, suffixed integers, uint/int/long/double/byte/short/increment/string/fmt/file/list/str options.
- Tests option value aliases with prefix matching and ambiguity/error cases.
- Tests comma-separated `u32` array parsing, including empty input, invalid tokens, overflow, sparse commas, and max-length overflow.
- Tests global option parsing before subcommands, including verbose increments, dry-run flag, stopping at first non-option, option without subcommand, and unknown option failure.
- Captures stderr for selected global parse tests via `tmpfile`, `dup`, and `dup2`.

Role:
- Guards command-line parser behavior, especially global parser semantics needed by subcommand dispatch.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/unit/test-argconfig-parse.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/unit/test-suffix-binary-parse.c -->
# File Research: sources/virtualization/nvme-cli/unit/test-suffix-binary-parse.c

C unit test for binary suffix parsing.

Cases:
- Plain integer `1234`.
- Binary suffixes such as `1Ki` and `34Gi`.
- Invalid fractional binary suffix `34.9Ki`.
- Invalid repeated suffix `32Gii`.

Role:
- Verifies `suffix_binary_parse` returns expected values and `-EINVAL` on malformed input.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/unit/test-suffix-binary-parse.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/unit/test-suffix-si-parse.c -->
# File Research: sources/virtualization/nvme-cli/unit/test-suffix-si-parse.c

C unit test for SI suffix parsing.

Cases:
- Plain numbers and decimal SI suffixes like `M`, `k`, `T`, and `G`.
- Fractional values are truncated to integer byte/count values.
- Invalid inputs include unsupported characters, comma decimal separator, double dots, repeated suffixes, suffix followed by digits, and trailing decimal point forms.
- Sets numeric locale to `C`.

Role:
- Guards decimal suffix parsing behavior for CLI numeric arguments.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/unit/test-suffix-si-parse.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/unit/test-uint128-si.c -->
# File Research: sources/virtualization/nvme-cli/unit/test-uint128-si.c

C unit test for converting 128-bit NVMe counters to SI strings.

Key elements:
- Defines `U128` helper from four 32-bit words.
- Tests zero, small values, a mixed large value, max 128-bit value, and several sector-count-style values with `bytes_per_unit = 1000 * 512`.
- Expected units include B, TB, RB, and QB.

Role:
- Verifies `uint128_t_to_si_string` formatting and scaling.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/unit/test-uint128-si.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/unit/test-uint128.c -->
# File Research: sources/virtualization/nvme-cli/unit/test-uint128.c

C unit test for 128-bit integer string formatting.

Key elements:
- Tests raw decimal conversion for zero, small values, a mixed large value, and max `uint128`.
- Tests localized formatting under `fr_FR.utf-8`, expecting a thousands separator for `1000`.
- Skips locale-specific assertion if the system locale or thousands separator is unavailable.

Role:
- Guards `uint128_t_to_string` and `uint128_t_to_l10n_string`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/unit/test-uint128.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/util/argconfig.c -->
# File Research: sources/virtualization/nvme-cli/util/argconfig.c

Command-line parsing utility implementation for nvme-cli.

Key elements:
- Maintains appended usage string for help output.
- Prints word-wrapped descriptions and option help.
- Builds `getopt_long_only` option tables dynamically from `argconfig_commandline_options`.
- Parses typed values: string, int, byte, short, uint/positive, increment, long, binary-suffix long, double, and flag.
- Supports enum-like option value tables with case-insensitive prefix matching; ambiguous prefixes fail.
- Tracks whether each option was seen.
- Resets locale to `C` unless a `human-readable` flag option was seen.
- Provides `argconfig_parse_global`, using a leading `+` in the short option string so parsing stops at the first non-option subcommand.
- Generates comma-separated array parsers for int, short, long, and fixed-width unsigned integer types.
- Provides `argconfig_parse_seen`.

Dependencies:
- Uses `getopt`, `suffix_binary_parse`, cleanup attributes, and `libnvme_strerror`.

Notes:
- Global parser uses `getopt_long` while subcommand parser uses `getopt_long_only`.
- Comma-separated array parsing mutates the input string through `strtok`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/util/argconfig.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/util/argconfig.h -->
# File Research: sources/virtualization/nvme-cli/util/argconfig.h

Public macro and type interface for nvme-cli argument parsing.

Key elements:
- Defines `enum argconfig_types`.
- Provides `OPT_*` macros for flags, suffix numbers, uint/int/long/double/byte/short/increment/string/fmt/file/list/string options, groups, and terminator.
- Provides JSON-conditional `OPT_FLAG_JSON`.
- Provides `VAL_*` macros for option value alias tables.
- Defines `union argconfig_val`, `struct argconfig_opt_val`, and `struct argconfig_commandline_options`.
- Declares parser, help, comma-separated array parser, word-wrap, and seen-check APIs.

Role:
- Used widely by command implementations to declare CLI options compactly.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/util/argconfig.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/util/base64.c -->
# File Research: sources/virtualization/nvme-cli/util/base64.c

RFC4648-style base64 encode/decode implementation.

Key elements:
- Uses standard Base64 alphabet with `+` and `/`.
- `base64_encode` consumes bytes, emits 6-bit alphabet values, and pads with `=`.
- Encoded output is not NUL-terminated by the function.
- `base64_decode` maps characters through `strchr`, handles `=`, rejects invalid or NUL characters with `-EINVAL`, and rejects leftover nonzero bits with `-EAGAIN`.

Role:
- Small local utility for encoding/decoding binary data where nvme-cli needs textual representation.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/util/base64.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/util/base64.h -->
# File Research: sources/virtualization/nvme-cli/util/base64.h

Header for base64 helpers.

Exports:
- `base64_encode(const unsigned char *src, int len, char *dst)`
- `base64_decode(const char *src, int len, unsigned char *dst)`

Role:
- Public declaration layer for `util/base64.c`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/util/base64.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/util/cleanup.h -->
# File Research: sources/virtualization/nvme-cli/util/cleanup.h

Cleanup attribute helper macros for RAII-style cleanup in C.

Key elements:
- Defines `__cleanup(fn)` as GCC/Clang cleanup attribute.
- Provides cleanup helpers for:
  - `free`
  - `libnvme_free`
  - huge libnvme allocations
  - file descriptors greater than stderr
  - libnvme global contexts
  - libnvme controllers
  - `FILE *` via `fclose`
- Under `CONFIG_FABRICS`, adds URI and NVMf context cleanup helpers.

Role:
- Used throughout command code to reduce manual cleanup paths.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/util/cleanup.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/util/crc32.c -->
# File Research: sources/virtualization/nvme-cli/util/crc32.c

CRC-32 implementation sourced from elfutils.

Key elements:
- Includes a 256-entry precomputed CRC table.
- `crc32(uint32_t crc, unsigned char *buf, size_t len)` inverts the initial CRC, processes each byte, and returns the inverted final CRC.
- License header permits LGPLv3-or-later, GPLv2-or-later, or both in parallel.

Role:
- Provides local CRC-32 utility for nvme-cli code paths needing checksum calculation.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/util/crc32.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/util/crc32.h -->
# File Research: sources/virtualization/nvme-cli/util/crc32.h

Header for CRC-32 helper.

Exports:
- `uint32_t crc32(uint32_t crc, unsigned char *buf, size_t len)`

Role:
- Public declaration for `util/crc32.c`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/util/crc32.h -->