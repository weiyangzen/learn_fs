# Group Research: group_1333_nvme_cli_sources_virtualization_nvme_cli_nvme_print_c_sources_virtu_a464a6cacf40

Scope confirmed against `Docs/research_subset_a.md`: all files are under `sources/virtualization/nvme-cli`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/nvme-print.c -->
# File Research: sources/virtualization/nvme-cli/nvme-print.c

- Purpose: central print facade for nvme-cli. It selects stdout, JSON, or binary `print_ops` backends and exposes stable `nvme_show_*` wrappers used by command implementations.
- Backend dispatch: `nvme_print_ops()` chooses JSON when requested globally or by flags, binary for `BINARY`, otherwise stdout. `nvme_print()` suppresses output during `nvme_args.dry_run`.
- String decoding: maps many NVMe enums and fields to user-facing strings, including ANA states, admin/I/O opcodes, sanitize status, persistent event types, FDP events, registers, log page IDs, features, timestamp attributes, temperature units, power measurement fields, write-protect states, and fabrics transport error types.
- Log/identify wrappers: forwards decoded structures for identify controller/namespace, NVM/ZNS identify data, SMART, error, firmware, sanitize, ANA, reservation, FDP, endurance, predictable latency, persistent events, LBA status, supported logs, discovery, topology, and several newer NVMe log pages.
- Register helpers: checks fabrics register validity, optional fabrics registers, CMB/PMR readiness, reads 32-bit or 64-bit MMIO registers, and forwards register values for printing.
- Error reporting: `nvme_show_err`, `nvme_show_io_cmd_err`, `nvme_show_admin_cmd_err`, `nvme_show_status`, and `nvme_show_opcode_status` route negative errno-style errors and positive NVMe status codes to the active printer.
- Device path helpers: `nvme_dev_full_path()` and `nvme_generic_full_path()` resolve namespace names to `/dev/...`, SPDK paths, or generic `ngXnY` paths when present.
- Notable behavior: several conversion functions return static buffers, so callers should treat results as short-lived and not thread-safe.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/nvme-print.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/nvme-print.h -->
# File Research: sources/virtualization/nvme-cli/nvme-print.h

- Purpose: public declaration header for nvme-cli printing, formatting, status, and conversion helpers.
- Core type: defines `struct print_ops`, the large vtable used by stdout, JSON, and binary printers for logs, identify data, topology, messages, status, and key/value output.
- Shared structures: declares `nvme_effects_log_node_t`, `struct nvme_error_log_filter`, and `struct nvme_bar_cap`.
- Output API: declares all `nvme_show_*` wrapper functions implemented in `nvme-print.c`, including identify, log, topology, FDP, ZNS, discovery, and persistent-event helpers.
- Conversion API: declares `nvme_*_to_string()` helpers for commands, logs, features, registers, power, temperature, timestamps, PEL fields, sanitize states, and FDP events.
- JSON integration: conditionally declares `nvme_get_json_print_ops()` when `CONFIG_JSONC` is enabled, otherwise provides a NULL inline fallback.
- Dependency role: included by command/plugin code that should not know the concrete print backend implementation.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/nvme-print.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/nvme-rpmb.c -->
# File Research: sources/virtualization/nvme-cli/nvme-rpmb.c

- Purpose: implements nvme-cli RPMB support commands: info, program-key, read-counter, read-data, write-data, read-config, and write-config.
- Crypto path: uses Linux `AF_ALG` sockets for `hmac(sha256)` and `md5`; HMAC authenticates RPMB writes and MD5 seeds request nonces.
- Protocol structures: defines packed RPMB data frames, config blocks, request/response type enums, security protocol constants, and controller RPMB capability bitfield parsing from identify-controller `rpmbs`.
- NVMe transport: sends RPMB frames through Security Send and Security Receive admin passthrough commands with protocol `0xEA` and SPSP `0x0001`.
- Request handling: builds request frames with type, target, nonce, address, sector count, and optional data; reads responses and checks response type, result, nonce, MAC, and write-counter progression.
- Data operations: chunks authenticated reads/writes according to controller access size, validates transfer size against total RPMB size, and writes read data/config blocks to files when requested.
- Config operations: reads and writes the device configuration block, including boot partition protection and lock status display.
- CLI integration: `rpmb_cmd_option()` parses keys from inline string or file, data from inline string or file, target/address/block options, opens the device, identifies RPMB support, and dispatches the chosen RPMB action.
- Risks and notes: key sizes are limited to 1..223 bytes; file writes append with `ab+`; randomness for nonce is based on `rand()` hashed with MD5, not a cryptographic RNG.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/nvme-rpmb.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/nvme.control.in -->
# File Research: sources/virtualization/nvme-cli/nvme.control.in

- Purpose: Debian package control template for nvme-cli.
- Fields: package name `nvme`, version placeholder `@VERSION@`, amd64 architecture, dependency placeholder `@DEPENDS@`, maintainer Keith Busch, and short package description.
- Integration: Meson/package generation substitutes placeholders for the produced Debian package metadata.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/nvme.control.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/nvme.h -->
# File Research: sources/virtualization/nvme-cli/nvme.h

- Purpose: central nvme-cli header for global arguments, output flags, helper macros, and shared command/open declarations.
- Output model: defines `nvme_print_flags` values `NORMAL`, `VERBOSE`, `JSON`, `VS`, `BINARY`, and `TABULAR`.
- Global args: `struct nvme_args` carries output format, verbosity, timeout, dry-run, retry/probing toggles, and output format version.
- CLI macro: `NVME_ARGS` appends common global options to command-specific argconfig option arrays.
- Topology helpers: includes multipath detection and iopolicy table-column filtering helpers.
- Core declarations: exposes `parse_and_open`, transport cleanup, output format validation, `__id_ctrl`, `libnvme_strerror`, elapsed time helper, register helpers, and `nvme_get_nsid_log`.
- Cleanup integration: defines `__cleanup_nvme_transport_handle` for automatic transport handle release.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/nvme.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/nvme.spec.in -->
# File Research: sources/virtualization/nvme-cli/nvme.spec.in

- Purpose: RPM spec template for packaging nvme-cli.
- Install behavior: runs `meson install`, creates host NQN/host ID placeholders under `@SYSCONFDIR@/nvme`, and packages binary, man pages, completions, config files, udev rules, dracut config, and systemd units.
- Post-install behavior: initializes hostnqn and hostid on first install if empty, reloads systemd, reloads udev rules, and triggers udev.
- Template variables: uses placeholders for version, license, URL, dependencies, install directories, and system paths.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/nvme.spec.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/nvmf-autoconnect/dracut-conf/70-nvmf-autoconnect.conf.in -->
# File Research: sources/virtualization/nvme-cli/nvmf-autoconnect/dracut-conf/70-nvmf-autoconnect.conf.in

- Purpose: dracut configuration snippet.
- Behavior: adds the generated `70-nvmf-autoconnect.rules` udev rule to initramfs install items through `install_items+=`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/nvmf-autoconnect/dracut-conf/70-nvmf-autoconnect.conf.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/nvmf-autoconnect/nm-dispatcher/80-nvmf-connect-nbft.sh.in -->
# File Research: sources/virtualization/nvme-cli/nvmf-autoconnect/nm-dispatcher/80-nvmf-connect-nbft.sh.in

- Purpose: NetworkManager dispatcher script for NBFT-defined NVMe-oF connections.
- Trigger logic: on interface `up`, starts NBFT reconnect when interface name begins with `nbft` or `CONNECTION_ID` begins with `NBFT connection HFI`.
- Action: starts `nvmf-connect-nbft.service` asynchronously with substituted `@SYSTEMCTL@`; failures are ignored.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/nvmf-autoconnect/nm-dispatcher/80-nvmf-connect-nbft.sh.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/nvmf-autoconnect/systemd/nvmefc-boot-connections.service.in -->
# File Research: sources/virtualization/nvme-cli/nvmf-autoconnect/systemd/nvmefc-boot-connections.service.in

- Purpose: boot-time FC-NVMe discovery service.
- Conditions/order: runs only when `/sys/class/fc/fc_udev_device/nvme_discovery` exists, after udevd and before `local-fs-pre.target`.
- Action: oneshot shell command writes `add` to the FC discovery sysfs node.
- Hardening: enables several systemd sandboxing restrictions such as `ProtectSystem`, `ProtectHome`, `ProtectProc`, `MemoryDenyWriteExecute`, and `RestrictAddressFamilies=none`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/nvmf-autoconnect/systemd/nvmefc-boot-connections.service.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/nvmf-autoconnect/systemd/nvmf-autoconnect.service.in -->
# File Research: sources/virtualization/nvme-cli/nvmf-autoconnect/systemd/nvmf-autoconnect.service.in

- Purpose: boot-time automatic NVMe-oF connect-all service.
- Conditions/order: runs when either `config.json` or `discovery.conf` exists, wants/after `modprobe@nvme_fabrics.service`, after network-online, before remote-fs-pre.
- Action: `@SBINDIR@/nvme connect-all --context=autoconnect`.
- Hardening: restricts filesystem, home, proc, kernel modules/logs/control groups, realtime, personality, IPC, W+X memory, and address families to IPv4/IPv6.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/nvmf-autoconnect/systemd/nvmf-autoconnect.service.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/nvmf-autoconnect/systemd/nvmf-connect-nbft.service.in -->
# File Research: sources/virtualization/nvme-cli/nvmf-autoconnect/systemd/nvmf-connect-nbft.service.in

- Purpose: service started by network management after an NBFT interface is configured.
- Conditions/order: requires either ACPI NBFT table path, loads nvme-fabrics, waits for network-online, and runs before remote-fs-pre.
- Action: `@SBINDIR@/nvme connect-all --nbft`.
- Hardening: same style as other autoconnect units, with AF_INET/AF_INET6 address-family restriction.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/nvmf-autoconnect/systemd/nvmf-connect-nbft.service.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/nvmf-autoconnect/systemd/nvmf-connect.target.in -->
# File Research: sources/virtualization/nvme-cli/nvmf-autoconnect/systemd/nvmf-connect.target.in

- Purpose: grouping target for all `nvmf-connect@.service` instances.
- Content: only a Unit description, used by udev-triggered autoconnect services.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/nvmf-autoconnect/systemd/nvmf-connect.target.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/nvmf-autoconnect/systemd/nvmf-connect@.service.in -->
# File Research: sources/virtualization/nvme-cli/nvmf-autoconnect/systemd/nvmf-connect@.service.in

- Purpose: templated service for discovery-controller event-driven NVMe-oF reconnect scans.
- Ordering: no default dependencies, after systemd-udevd, before local-fs-pre, part of and requiring `nvmf-connect.target`.
- Action: decodes escaped instance arguments into `CONNECT_ARGS` and runs `nvme connect-all --context=autoconnect --quiet ...`.
- Hardening: similar to autoconnect services, limited to IPv4/IPv6 address families.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/nvmf-autoconnect/systemd/nvmf-connect@.service.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/nvmf-autoconnect/udev-rules/65-persistent-net-nbft.rules.in -->
# File Research: sources/virtualization/nvme-cli/nvmf-autoconnect/udev-rules/65-persistent-net-nbft.rules.in

- Purpose: udev rule to preserve NBFT network interface names.
- Behavior: for non-remove net events where `INTERFACE` matches `nbft*`, assigns the kernel name from the interface environment value.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/nvmf-autoconnect/udev-rules/65-persistent-net-nbft.rules.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/nvmf-autoconnect/udev-rules/70-nvmf-autoconnect.rules.in -->
# File Research: sources/virtualization/nvme-cli/nvmf-autoconnect/udev-rules/70-nvmf-autoconnect.rules.in

- Purpose: udev rules for NVMe-oF autoconnect on discovery log changes and FC discovery events.
- Trigger scope: only `ACTION=="change"` events.
- Compatibility: sets empty `NVME_HOST_IFACE` to `none` for older expectations.
- Discovery AEN handling: on NVMe discovery log change AEN `0x70f002`, restarts a specific `nvmf-connect@...service` instance with device, transport, traddr, trsvcid, host-traddr, and host-iface arguments.
- FC handling: supports old-style FC `FC_EVENT=="nvmediscovery"` events and restarts the templated service with FC-specific arguments.
- Rediscover handling: when a discovery controller reconnects with `NVME_EVENT=="rediscover"`, rereads the discovery log through the templated service.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/nvmf-autoconnect/udev-rules/70-nvmf-autoconnect.rules.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/nvmf-autoconnect/udev-rules/70-nvmf-keys.rules.in -->
# File Research: sources/virtualization/nvme-cli/nvmf-autoconnect/udev-rules/70-nvmf-keys.rules.in

- Purpose: loads NVMe/TCP TLS pre-shared keys when kernel support appears.
- Trigger: module add event for `nvme_tcp` when `@SYSCONFDIR@/nvme/tls-keys` exists.
- Action: runs `nvme tls --import --keyfile @SYSCONFDIR@/nvme/tls-keys`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/nvmf-autoconnect/udev-rules/70-nvmf-keys.rules.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/nvmf-autoconnect/udev-rules/71-nvmf-hpe.rules.in -->
# File Research: sources/virtualization/nvme-cli/nvmf-autoconnect/udev-rules/71-nvmf-hpe.rules.in

- Purpose: vendor udev policy for HPE Alletra NVMe-oF devices.
- Behavior: sets `iopolicy=round-robin` for HPE Alletra NVM subsystems and `ctrl_loss_tmo=-1` for matching TCP controllers.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/nvmf-autoconnect/udev-rules/71-nvmf-hpe.rules.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/nvmf-autoconnect/udev-rules/71-nvmf-netapp.rules.in -->
# File Research: sources/virtualization/nvme-cli/nvmf-autoconnect/udev-rules/71-nvmf-netapp.rules.in

- Purpose: vendor udev policy for NetApp NVMe-oF devices.
- Behavior: sets ONTAP subsystem `iopolicy=queue-depth`, E-Series `iopolicy=round-robin`, and TCP ONTAP controller `ctrl_loss_tmo=-1`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/nvmf-autoconnect/udev-rules/71-nvmf-netapp.rules.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/nvmf-autoconnect/udev-rules/71-nvmf-vastdata.rules.in -->
# File Research: sources/virtualization/nvme-cli/nvmf-autoconnect/udev-rules/71-nvmf-vastdata.rules.in

- Purpose: vendor udev policy for VAST Data NVMe-oF devices.
- Behavior: sets NVM subsystem `iopolicy=round-robin` and controller `ctrl_loss_tmo=-1` for model `VASTData`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/nvmf-autoconnect/udev-rules/71-nvmf-vastdata.rules.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugin.c -->
# File Research: sources/virtualization/nvme-cli/plugin.c

- Purpose: generic plugin and command dispatcher for nvme-cli.
- Built-ins: implements `version`, `help`, usage printing, and general command/plugin help.
- Dispatch behavior: parses global help/version options before subcommand parsing, supports exact command names, aliases, unique command abbreviations, extension plugin names, and legacy combined `plugin-command` invocation.
- Help behavior: tries to open command-specific man pages with `man`, then falls back to generated command help.
- Extension listing: built-in plugin help lists installed extension plugins; extension plugin help lists only that plugin’s commands.
- Error behavior: invalid subcommands return `-ENOTTY` and print an error.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugin.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugin.h -->
# File Research: sources/virtualization/nvme-cli/plugin.h

- Purpose: lightweight declarations for the nvme-cli plugin framework.
- Structures: defines `program`, `plugin`, and `command` with command arrays, parent/next/tail links, names, versions, descriptions, handlers, and aliases.
- API: declares `general_help()` and `handle_plugin()`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugin.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/amzn/amzn-nvme.c -->
# File Research: sources/virtualization/nvme-cli/plugins/amzn/amzn-nvme.c

- Purpose: Amazon vendor plugin for EC2 NVMe identify-controller data and latency/statistics log page output.
- Identify support: decodes vendor-specific controller field `bdev` and prints it or adds it to JSON.
- Stats log: reads Amazon log page `0xD0`, recognizes EBS and local-storage magic values, and decodes totals for read/write ops, bytes, time, performance-exceeded counters, queue length, and latency histograms.
- Local storage behavior: detects Amazon EC2 NVMe Instance Storage by model prefix and may use namespace-specific log retrieval.
- Detail mode: for version 1 logs, can print per-I/O-size read/write histogram counts.
- JSON support: emits total counters and histogram arrays when `CONFIG_JSONC` is available.
- Polling mode: optional interval mode repeatedly fetches the log, computes deltas from previous cumulative counters/histograms, and stops on SIGINT.
- Notable issue: `get_stats()` validates a local `cfg.output_format` initialized to `"normal"` and does not expose it in command options, so global output-format handling appears inconsistent with other commands.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/amzn/amzn-nvme.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/amzn/amzn-nvme.h -->
# File Research: sources/virtualization/nvme-cli/plugins/amzn/amzn-nvme.h

- Purpose: command-registration header for the Amazon plugin.
- Plugin: `amzn`, description `Amazon vendor specific extensions`, version `NVME_VERSION`.
- Commands: `id-ctrl` for Identify Controller with Amazon vendor decoding, and `stats` for EBS/local-storage statistics.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/amzn/amzn-nvme.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/dapustor/dapustor-nvme.c -->
# File Research: sources/virtualization/nvme-cli/plugins/dapustor/dapustor-nvme.c

- Purpose: DapuStor vendor plugin for additional SMART log retrieval and decoding.
- Data layout: defines packed SMART log item unions for raw 48-bit counters, wear-level triples, thermal throttle fields, temperature triples, power consumption triples, and extended SMART attributes.
- Log retrieval: reads vendor log `0xCA` for base additional SMART and attempts log `0xCB` for extended SMART; absence of extended log is tolerated.
- Output modes: supports normal text, JSON, and raw binary.
- Decoded metrics: includes program/erase fail counts, wear leveling, E2E/CRC errors, timed workload metrics, thermal throttle, NAND/host bytes, system-area life, NAND reads, temperature/power stats, power-loss protection, read failures, media errors, write amplification, firmware update count, DRAM ECC, XOR counts, inflight I/O, and lifetime/boot temperature ranges.
- CLI: command parses namespace, raw-binary, JSON/global output options and uses common parse/open and print helpers.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/dapustor/dapustor-nvme.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/dapustor/dapustor-nvme.h -->
# File Research: sources/virtualization/nvme-cli/plugins/dapustor/dapustor-nvme.h

- Purpose: command-registration header for the DapuStor plugin.
- Plugin: `dapustor`, description `DapuStor vendor specific extensions`, version `NVME_VERSION`.
- Command: `smart-log-add` runs `dapustor_additional_smart_log`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/dapustor/dapustor-nvme.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/dell/dell-nvme.c -->
# File Research: sources/virtualization/nvme-cli/plugins/dell/dell-nvme.c

- Purpose: Dell vendor identify-controller decoder.
- Data layout: interprets vendor bytes as three 16-bit version components plus array-name bytes.
- Output: prints or JSON-encodes `array_name` and `array_ver`; empty array names are rendered as `NULL`.
- Integration: command handler delegates normal identify-controller retrieval to shared `__id_ctrl()` with Dell-specific vendor callback.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/dell/dell-nvme.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/dell/dell-nvme.h -->
# File Research: sources/virtualization/nvme-cli/plugins/dell/dell-nvme.h

- Purpose: command-registration header for the Dell plugin.
- Plugin: `dell`, description `DELL vendor specific extensions`, version `NVME_VERSION`.
- Command: `id-ctrl` runs Dell Identify Controller vendor decoding.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/dell/dell-nvme.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/dera/dera-nvme.c -->
# File Research: sources/virtualization/nvme-cli/plugins/dera/dera-nvme.c

- Purpose: Dera vendor plugin for device status and additional SMART-like health fields.
- Log layout: defines `nvme_dera_smart_info_log` with rebuild counters, capacitor health, NAND/DDR/PCIe error counters, power fields, firmware strings, voltage counters, temperature sensor counters, and reserved padding.
- Status command: retrieves log page `0xC0`, then sends admin passthrough opcode `0xC0` with `cdw12=0x104` to obtain current device status.
- Output: prints status strings, rebuild progress where applicable, capacitor state/voltage, NAND errors, power level/current power, PCIe voltage status, temperature abnormal count, NAND retry failures, and firmware slot version.
- Registration: exposed as `smart-log-add` with alias `stat`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/dera/dera-nvme.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/dera/dera-nvme.h -->
# File Research: sources/virtualization/nvme-cli/plugins/dera/dera-nvme.h

- Purpose: command-registration header for the Dera plugin.
- Plugin: `dera`, description `Dera vendor specific extensions`, version `NVME_VERSION`.
- Command: `smart-log-add`, alias `stat`, runs `get_status`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/dera/dera-nvme.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/fdp/fdp.c -->
# File Research: sources/virtualization/nvme-cli/plugins/fdp/fdp.c

- Purpose: plugin for managing NVMe Flexible Data Placement devices.
- Log commands: `configs`, `usage`, `stats`, and `events` retrieve FDP configuration, reclaim-unit handle usage, FDP statistics, and FDP events through libnvme helper APIs.
- Variable-length handling: configuration, usage, and RUH status commands first fetch headers, compute required length, allocate buffers, then refetch full data.
- I/O command support: `status` and `update` use FDP reclaim unit handle status passthrough commands; `update` parses comma-separated placement IDs.
- Feature control: `set-events` updates `NVME_FEAT_FID_FDP_EVENTS`; `feature` shows, enables, or disables FDP configuration for an endurance group.
- Output: uses common FDP print wrappers and supports raw binary/human-readable flags where applicable.
- Validation: requires endurance-group IDs for several commands and validates placement/event list presence.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/fdp/fdp.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/fdp/fdp.h -->
# File Research: sources/virtualization/nvme-cli/plugins/fdp/fdp.h

- Purpose: command-registration header for the FDP plugin.
- Plugin: `fdp`, description `Manage Flexible Data Placement enabled devices`, version `NVME_VERSION`.
- Commands: `configs`, `usage`, `stats`, `events`, `status`, `update`, `set-events`, and `feature`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/fdp/fdp.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/feat/feat-nvme.c -->
# File Research: sources/virtualization/nvme-cli/plugins/feat/feat-nvme.c

- Purpose: named command wrappers for getting and setting selected NVMe feature IDs.
- Generic get path: `feat_get_nsid()` optionally obtains feature data length, allocates a buffer, calls `nvme_get_features`, and prints decoded feature output.
- Supported features: power management, performance characteristics, host controlled thermal management, timestamp, temperature threshold, arbitration, volatile write cache, power limit, power threshold, power measurement, error recovery, number of queues, and host behavior support.
- Set behavior: constructs correct CDW fields with NVME_SET macros and calls either generic `nvme_set_features` or specialized init helpers for temperature/arbitration/host behavior.
- Partial updates: temperature threshold, arbitration, number of queues, and host behavior read current or saved values first so unspecified fields can be preserved.
- Data payloads: timestamp and host behavior use structured payloads; performance characteristics can read vendor-specific attribute data from a file.
- CLI integration: the `FEAT_ARGS` macro adds common `--save` and `--sel` options to each feature command.
- Notable issue: `num_queues_set()` appears to OR an unspecified `ncqr` value into `FEAT_NRQS_NSQR` rather than `FEAT_NRQS_NCQR`, likely a typo in preserving existing completion queue count.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/feat/feat-nvme.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/feat/feat-nvme.h -->
# File Research: sources/virtualization/nvme-cli/plugins/feat/feat-nvme.h

- Purpose: command-registration and shared macro header for the feature plugin.
- Descriptions: defines per-command description strings and `FEAT_PLUGIN_VERSION`.
- Macro: `FEAT_ARGS` wraps `NVME_ARGS` and adds common `save` and `sel` options.
- Plugin: `feat`, description `NVMe feature extensions`, version `1.0`.
- Commands: registers wrappers for power management, performance characteristics, HCTM, timestamp, temp threshold, arbitration, volatile write cache, power limit, power threshold, power measurement, error recovery, number of queues, and host behavior support.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/feat/feat-nvme.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/feat/meson.build -->
# File Research: sources/virtualization/nvme-cli/plugins/feat/meson.build

- Purpose: Meson source-list fragment for the feature plugin.
- Behavior: appends `plugins/feat/feat-nvme.c` to `plugin_sources`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/feat/meson.build -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/huawei/huawei-nvme.c -->
# File Research: sources/virtualization/nvme-cli/plugins/huawei/huawei-nvme.c

- Purpose: Huawei vendor plugin for listing Huawei NVMe namespaces and decoding Huawei identify-controller vendor data.
- Device scan: scans `/dev` with `libnvme_filter_namespace`, opens namespace devices, identifies controller and namespace, and filters by model containing `Huawei` or PCI vendor ID `0x19E5`.
- List data: records device node, namespace ID, block-device status, namespace vendor name, array vendor name, NGUID, and usage computed from LBA size and namespace utilization.
- Output: prints aligned normal table or JSON device array with device path, index, namespace name, and array name.
- Identify support: `huawei_id_ctrl` delegates to `__id_ctrl()` and decodes the vendor-specific array name.
- Notable issue: length helper loops use `list_items->ns_name` and `list_items->array_name` instead of indexing `list_items[i]`, so computed column widths may only reflect the first item.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/huawei/huawei-nvme.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/huawei/huawei-nvme.h -->
# File Research: sources/virtualization/nvme-cli/plugins/huawei/huawei-nvme.h

- Purpose: command-registration header for the Huawei plugin.
- Plugin: `huawei`, description `Huawei vendor specific extensions`, version `NVME_VERSION`.
- Commands: `list` for all Huawei NVMe devices/namespaces on the machine, and `id-ctrl` for Huawei identify-controller vendor data.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/huawei/huawei-nvme.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ibm/ibm-nvme.c -->
# File Research: sources/virtualization/nvme-cli/plugins/ibm/ibm-nvme.c

- Purpose: IBM vendor plugin for additional SMART log, VPD log, and IBM-specific persistent event log decoding.
- Additional SMART: reads vendor log `0xF0` into packed IBM attribute entries and prints known attributes such as read errors, retired blocks, power-on hours, power cycles, ECC, erased MB, spare blocks, program/erase failures, life remaining/used, temperature, thermal throttling, flash/host lifetime I/O, backup failures, security wear, and PCIe receive errors.
- VPD log: reads vendor log `0xF1` and prints fixed-width fields for part numbers, EC/FRU/final assembly, feature code, CCIN, 11S serial, SSID, endurance, capacity, warranty, encryption, RCTT, load ID, location, timeout values, queue count, media type, manufacturer serial, and firmware.
- Persistent events: retrieves standard persistent event log context, scans event entries for vendor-specific event type `0xDE`, then decodes IBM change-definition and reported-error vendor event payloads.
- Output modes: SMART and VPD support raw binary; persistent event supports binary and verbose human decoding through common PEL header helpers.
- Memory note: persistent event allocation uses `libnvme_alloc` but does not free `pevent_log_info` before return in this file.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ibm/ibm-nvme.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ibm/ibm-nvme.h -->
# File Research: sources/virtualization/nvme-cli/plugins/ibm/ibm-nvme.h

- Purpose: command-registration header for the IBM plugin.
- Plugin: `ibm`, description `IBM vendor specific extensions`, version `NVME_VERSION`.
- Commands: `crit-log` for IBM SMART information, `vpd` for IBM VPD information, and `persist-event-log` for IBM-specific persistent event log decoding.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ibm/ibm-nvme.h -->