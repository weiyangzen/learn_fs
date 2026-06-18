# Group Research: group_1335_nvme_cli_sources_virtualization_nvme_cli_plugins_micron_micron_nvme_85e43a8edbae

Scope: `Docs/research_subset_a.md`, source tree `sources/virtualization/nvme-cli`.

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/micron/micron-nvme.c -->
# File Research: sources/virtualization/nvme-cli/plugins/micron/micron-nvme.c

## Role

Large Micron nvme-cli plugin implementation. It implements Micron vendor commands, OCP-like Micron log decoders, debug log package collection, feature controls, firmware update/history helpers, SMART/health extensions, and Identify Controller vendor-field display.

The file is compiled as an nvme-cli plugin translation unit by defining `CREATE_CMD` and including `micron-nvme.h`, which registers the command table.

## Command Surface Implemented

Registered via `micron-nvme.h` and implemented here:

- `select-download`: selective firmware download and commit for older 9200-style flows.
- `vs-temperature-stats`: SMART temperature and sensors.
- `vs-pcie-stats`: PCIe error status/counters through Micron admin command or `setpci`.
- `clear-pcie-correctable-errors`: clears PCIe correctable errors via Micron feature/admin command or `setpci`.
- `vs-internal-log`: builds Micron debug package from controller, namespace, SMART, error, telemetry, feature, and vendor logs.
- `vs-telemetry-controller-option`: toggles controller telemetry generation feature.
- `vs-nand-stats`: Micron/OCP NAND health statistics.
- `vs-smart-ext-log`: extended SMART pages.
- `vs-drive-info`: hardware/FTL/boot-spec/ownership fields.
- `plugin-version` and `cloud-SSD-plugin-version`.
- `log-page-directory`: probes supported log pages.
- `vs-fw-activate-history`: parses Micron firmware activation history.
- `latency-tracking`, `latency-stats`, `latency-logs`: latency monitor feature/log controls.
- `vs-smart-add-log`: OCP-style additional SMART log.
- `clear-fw-activate-history`: clear firmware activation history.
- `vs-smbus-option`: SMBus feature toggle/status.
- `cloud-boot-SSD-version`, `vs-device-waf`, `vs-cloud-log`.
- `vs-work-load-log`, `vs-vendor-telemetry-log`.
- `smart-log`: Micron SMART/health output.
- `id-ctrl`: Identify Controller with Micron vendor fields.

## Drive Model Detection

The file defines `enum eDriveModel` with `M5410`, `M51AX`, `M51BX`, `M51BY`, `M51CY`, `M51CX`, `M5407`, `M5411`, `M6001`, `M6003`, `M6004`, and `UNKNOWN_MODEL`.

`GetDriveModel()` reads sysfs vendor/device IDs from:

- `/sys/class/nvme/nvme%d/device/vendor`
- `/sys/class/misc/nvme%d/device/vendor`
- `/sys/class/nvme/nvme%d/device/device`
- `/sys/class/misc/nvme%d/device/device`

It requires Micron vendor ID `0x1344`, then maps PCI device IDs to the internal model enum. Many command handlers gate behavior by this enum.

## Core Helpers

- `WriteData()` appends binary log data to a file under a directory.
- `ReadSysFile()` reads hex sysfs IDs.
- `ZipAndRemoveDir()` packages a generated debug directory using `tar -zcf` for `.tgz`/`.tar.gz`, otherwise `zip -r`, then deletes the temporary directory.
- `SetupDebugDataDirectories()` validates output path context, normalizes serial number text into a directory name, creates main/`OS`/`Controller` directories, and handles collisions by suffixing `-N`.
- `GetLogPageSize()` reads common log headers for log IDs `0xC1`, `0xC2`, `0xC4`.
- `NVMEGetLogPage()` manually builds Get Log Page admin passthroughs, handling chunking, offsets, and special cases for telemetry/log IDs `0x07`, `0x08`, `0xE6`, `0xE7`, `0xE9`.
- `NVMEResetLog()` repeatedly reads a log until `0xdeadbeef` or max size.
- `GetCommonLogPage()` allocates and fetches a log with `nvme_get_log_simple()`.
- `micron_parse_options()` wraps `parse_and_open()` and optional model detection.

## Firmware Download and Commit

`micron_selective_download()` parses `--fw` and `--select`, accepts select strings `OOB`, `EEP`, and `ALL`, reads the firmware image, validates DWORD alignment, downloads in 4096-byte chunks using `nvme_init_fw_download()`, then commits through `micron_fw_commit()`. Commit status `0x10B` or `0x20B` is treated as a successful update requiring power cycle.

## Feature Controls

Micron vendor feature IDs include:

- `0xC3`: clear PCI correctable errors.
- `0xC1`: clear firmware activation history.
- `0xCF`: telemetry control option.
- `0xD5`: SMBus option.
- `0x16`: OCP enhanced telemetry.

`micron_smbus_option()` supports `enable`, `disable`, and `status` for selected models, using `nvme_set_features_simple()` and `nvme_get_features()`.

`micron_telemetry_cntrl_option()` validates telemetry support through `ctrl.lpa & 0x8`, then enables, disables, or reads feature `0xCF`.

`micron_clr_fw_activation_history()` uses feature `0xC1` with bit 31 set for M51CX/M51BY/M51CY/M6003/M6004.

## Temperature and PCIe Statistics

`micron_temp_stats()` reads `nvme_smart_log`, emits normal or JSON output. The composite temperature is decoded from Kelvin to Celsius.

Implementation note: sensor loop condition uses `tempSensors[i]` before assigning from `smart_log.temp_sensor[i]`, so sensor reporting appears unreachable with zero-initialized `tempSensors`.

`micron_pcie_stats()` supports:

- M5407 vendor admin command `0xD6` for counter retrieval.
- Fallback sysfs path lookup and `setpci` reads of AER correctable/uncorrectable registers.
- JSON or normal formatting through `pcie_correctable_errors[]` and `pcie_uncorrectable_errors[]`.

`micron_clear_pcie_correctable_errors()` clears through feature `0xC3` for M51CX/M51BY/M51CY, admin opcode `0xD6` for M5407, or fallback `setpci` write to AER correctable error status.

## SMART, NAND, and Vendor Log Decoding

The file defines several `struct request_data` tables describing binary log layouts:

- `ocp_c0_log_page`: OCP SMART Cloud Health Log for M51CX.
- `hyperscale_c0_log_page`: Hyperscale NVMe Boot SSD extended health.
- `datacenter_c0_log_page`: datacenter NVMe SSD SMART layout for M51BY/M51CY.
- `e1_log_page`: extended SMART.
- `fb_log_page`: vendor-specific health log.
- `D0_log_page`: Nitro `0x6001` extended health.
- `C5_log_page`: Micron workload log.
- `C6_log_page`: vendor telemetry log.

Output uses `generic_structure_parser()` for many layouts and custom helpers for D0 and hyperscale NAND stats.

`micron_nand_stats()` identifies the model, reads controller data, handles Hyperscale GG customer ID on M51CX through `0xC0`, otherwise reads `0xD0` and optionally `0xFB`.

`micron_smart_ext_log()` selects `0xE1` for M51CX/M51BY/M51CY/M6003/M6004 and `0xD0` for M6001.

`micron_work_load_log()` and `micron_vendor_telemetry_log()` read `0xC5` and `0xC6` for M6001/M6003/M6004.

`micron_ocp_smart_health_logs()` prints `0xFB` for M5410/M5407 or `0xC0` for M51CX/M51BY/M51CY/M6003/M6004.

## Debug Package Collection

`micron_internal_logs()` is the largest workflow:

1. Parses package path and optional telemetry-only mode.
2. Opens device, identifies model and controller.
3. For telemetry-only mode, reads host/controller telemetry data area and writes directly to the requested package file.
4. For package mode, creates serial-number-based temp directories.
5. Writes timestamp, controller identify data, OS config snapshots, drive info, namespace identify data, SMART, error, generic logs, telemetry, feature settings, and vendor logs.
6. Selects vendor log lists based on model families.
7. Fetches logs with model-specific handling for common-log wrapped pages, telemetry pages, resettable logs, and chunked logs.
8. Archives the directory and removes temporary data.

It calls shell commands for OS information (`uname`, `lsmod`, `/proc/*`, `dmesg`) and packaging (`zip`, `tar`, `rm`), so runtime behavior depends on host tools and permissions.

## Telemetry Logic

`micron_telemetry_log()` reads telemetry header, calculates data area sizes, reallocates to the selected area size, then reads the requested host/controller telemetry data.

`GetOcpEnhancedTelemetryLog()` enables ETDAS through feature `0x16`, reads telemetry header and data areas 1-4, and appends host/controller telemetry log data to package files.

## Firmware Activation History

The file has Micron-specific packed structures:

- `fw_activation_history_entry`
- `micron_fw_activation_history_table`

`micron_fw_activation_history()` reads log `0xC2`, validates page ID and version, checks entry count, then prints normal table output or JSON. `display_fw_activate_entry()` formats power-on time, power cycle count, previous/new firmware, slot, commit action, and result.

## Latency Monitor

Feature/log IDs:

- Feature `0xD0`: latency monitor.
- Log `0xD1`: latency monitor entries.
- Log `0xD0`: bucketed command latency stats.

`micron_latency_stats_track()` enables/disables/statuses latency tracking by command mask (`read`, `write`, `trim`, `all`) and validates threshold in 10ms units.

`micron_latency_stats_logs()` prints 16 command-level latency log entries as CSV-like output.

`micron_latency_stats_info()` prints latency bucket histograms for all/read/write/trim.

## Health and Identify Extensions

`micron_health_info()` reads standard SMART/Health log and prints Micron-oriented normal or JSON output. It exposes standard counters plus Micron-specific `op_lifetime_energy_consumed` and `interval_power_measurement`.

`micron_id_ctrl()` calls `nvme_show_id_ctrl()` with `micron_id_ctrl_vs()` to display Micron vendor fields derived from controller structure fields:

- `pms`: bit 21 of `ctratt`.
- `ipmsr`.
- `msmt`.

## External Dependencies

This file depends heavily on nvme-cli/libnvme APIs:

- `parse_and_open()`, `argconfig`, `NVME_ARGS`.
- `libnvme_exec_admin_passthru()`, `libnvme_get_log()`.
- `nvme_get_log_simple()`, `nvme_get_log_smart()`, `nvme_identify_ctrl()`, `nvme_identify_ns()`.
- `nvme_get_features()`, `nvme_set_features()`, `nvme_set_features_simple()`.
- `generic_structure_parser()`, JSON helpers, output-format validation.
- cleanup attributes from `util/cleanup.h`.

It also depends on Linux `/sys`, `/proc`, `/dev/nvme*`, and external commands `setpci`, `zip`, `tar`, `gzip`, `rm`, and common shell utilities.

## Important Implementation Notes

- Many paths use `sprintf()` into fixed buffers; inputs are largely device paths or package paths.
- Several commands rely on `argv[optind]` being a device path after parsing.
- The debug package path logic validates parent directory only when a slash is present.
- The file mixes standard nvme-cli APIs with raw admin passthroughs.
- Some device-model checks return success even when unsupported options are printed, preserving nvme-cli plugin convention in parts of the file.
- The code assumes Linux sysfs layout and will not be portable outside that environment.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/micron/micron-nvme.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/micron/micron-nvme.h -->
# File Research: sources/virtualization/nvme-cli/plugins/micron/micron-nvme.h

## Role

Command registration header for the Micron nvme-cli plugin. It follows the nvme-cli plugin pattern:

- Undefines and sets `CMD_INC_FILE` to `plugins/micron/micron-nvme`.
- Guards with `MICRON_NVME` and `CMD_HEADER_MULTI_READ`.
- Includes `cmd.h`.
- Defines `PLUGIN(NAME("micron", ...), COMMAND_LIST(...))`.
- Includes `define_cmd.h` at the end.

## Registered Plugin

Plugin name: `micron`.

Description: `Micron vendor specific extensions`.

Version source: `NVME_VERSION`.

## Registered Commands

The header registers all Micron command handlers implemented in `micron-nvme.c`, including firmware download, temperature, PCIe stats, debug log collection, telemetry feature control, NAND/SMART logs, firmware activation history, latency monitoring, SMBus, Hyperscale boot/version/WAF/cloud logs, workload/vendor telemetry logs, SMART/Health, and Identify Controller.

## Dependency Relationship

This header is included by `micron-nvme.c` with `CREATE_CMD` defined, causing the nvme-cli command generation macros to bind command names to C functions. It contains no logic beyond macro-based plugin declaration.

## Notes

- Handler names must remain synchronized with function definitions in `micron-nvme.c`.
- The command names form the user-facing CLI surface for `nvme micron ...`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/micron/micron-nvme.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/nbft/nbft-plugin.c -->
# File Research: sources/virtualization/nvme-cli/plugins/nbft/nbft-plugin.c

## Role

Implements the `nvme nbft show` command for displaying ACPI NBFT tables. NBFT data is read through libnvme fabrics/NBFT helpers, then formatted as normal text tables or JSON.

## Public Entry Point

`show_nbft()` is the only command handler. It supports options:

- `--subsystem` / `-s`: show NBFT subsystems.
- `--hfi` / `-H`: show Host Fabric Interfaces.
- `--discovery` / `-d`: show discovery controllers.
- `--nbft-path`: override the default ACPI table path.

Default NBFT table path is `/sys/firmware/acpi/tables`.

If none of subsystem/HFI/discovery are requested, all three are shown.

## Data Sources

`show_nbft()` creates a libnvme global context and calls:

- `libnvmf_nbft_read_files(ctx, nbft_path, &head)`
- `libnvmf_nbft_free(ctx, head)`

The parsed records are linked as `struct nbft_file_entry` values, each carrying a `struct libnbft_info`.

## Formatting Helpers

Normal output:

- `normal_show_nbfts()`
- `normal_show_nbft()`
- `print_nbft_subsys_info()`
- `print_nbft_hfi_info()`
- `print_nbft_discovery_info()`
- `print_hfis()`

JSON output when `CONFIG_JSONC` is enabled:

- `json_show_nbfts()`
- `nbft_to_json()`
- `hfi_to_json()`
- `ssns_to_json()`
- `discovery_to_json()`

If JSON-C is not compiled in, `json_show_nbfts` is a macro returning `-EINVAL`.

## Structure Conversion

The file translates libnbft structures into user-facing fields:

- Host: NQN, host ID, configured flags, primary admin host flag.
- HFI TCP info: PCI SBDF, MAC, VLAN, IP origin/address, subnet, gateway, route metric, DNS, DHCP server, hostname, default route, DHCP override.
- Subsystem namespace: transport, traddr, trsvcid, subsys port ID, NSID, NID type/value, NQN, controller ID, ASQ size, root path, digest requirements, discovered/unavailable flags.
- Discovery controller: security index, HFI index, URI, NQN.

## Small Utilities

- `pci_sbdf_to_string()` formats segment/bus/device/function from encoded SBDF.
- `mac_addr_to_string()` formats six-byte MAC addresses.
- `primary_admin_host_flag_to_str()` maps libnbft host primary flag enum values.
- Static `dash[100]` is used for table separators.

## Output Behavior

Normal output dynamically sizes some table columns based on field lengths, especially IP/gateway/DNS/NQN/URI/address/HFI list widths. Subsystem HFI lists are truncated with dots if they exceed `HFIS_LEN`.

JSON output builds arrays of NBFT records, with nested host/subsystem/HFI/discovery objects or arrays depending on requested sections.

## Dependencies

Includes and relies on:

- `libnvme.h`
- `nvme-print.h`
- `nvme.h`
- `fabrics.h`
- `logging.h`
- JSON helper APIs under `CONFIG_JSONC`
- nvme-cli `argconfig`, output format, and logging globals.

## Notes

- The file is a read-only display tool; it does not issue NVMe admin commands to devices.
- It is Linux/ACPI-path oriented through the default sysfs firmware table path.
- JSON construction has fail paths that free the top-level object; some intermediate JSON arrays/objects depend on json-c ownership transfer behavior.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/nbft/nbft-plugin.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/nbft/nbft-plugin.h -->
# File Research: sources/virtualization/nvme-cli/plugins/nbft/nbft-plugin.h

## Role

Command registration header for the NBFT nvme-cli plugin.

## Registered Plugin

Plugin name: `nbft`.

Description: `ACPI NBFT table extensions`.

Version source: `NVME_VERSION`.

## Registered Command

- `show`: `Show contents of ACPI NBFT tables`, mapped to `show_nbft`.

## Dependency Relationship

Included by `nbft-plugin.c` with `CREATE_CMD` defined. Uses nvme-cli command macros from `cmd.h` and finalizes generation through `define_cmd.h`.

## Notes

The header contains no data parsing logic. It only declares the plugin command surface.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/nbft/nbft-plugin.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/netapp/netapp-nvme.c -->
# File Research: sources/virtualization/nvme-cli/plugins/netapp/netapp-nvme.c

## Role

Implements the NetApp nvme-cli plugin commands:

- `smdevices`: list NetApp E-Series volumes.
- `ontapdevices`: list NetApp ONTAP NVMe namespaces.

The implementation scans `/dev` for NVMe namespace block devices, opens each with libnvme, identifies NetApp devices by controller model string, collects namespace/controller metadata, and prints normal, column, or JSON output.

## Device Types

Two internal structures model collected data:

- `struct smdevice_info`: E-Series namespace data with NSID, controller identify data, namespace identify data, and device path.
- `struct ontapdevice_info`: ONTAP namespace data with NSID, controller identify data, namespace identify data, namespace UUID, ONTAP C2 log data, and device path.

## Constants and ONTAP Log Format

Important constants:

- `ONTAP_C2_LOG_ID`: `0xC2`.
- `ONTAP_C2_LOG_SIZE`: `4096`.
- Label/path lengths: `ONTAP_LABEL_LEN`, `ONTAP_NS_PATHLEN`.

ONTAP C2 log LSPs:

- `0x0`: supported.
- `0x1`: namespace info.
- `0x2`: platform.

ONTAP namespace info TLVs:

- `0x11`: vserver name.
- `0x12`: volume name.
- `0x13`: namespace name.
- `0x14`: namespace path.

`nvme_get_ontap_c2_log()` builds a Get Log Page admin passthrough for log `0xC2`, namespace info LSP, and target NSID.

## Device Discovery

`netapp_nvme_filter()` is used by `scandir("/dev", ...)`. It accepts names matching `nvme%d n%d` namespace devices and rejects hidden files and partition names matching `nvme%dn%dp%d`.

Both command handlers optionally accept a target device name after options and validate it with `/dev/<name>` plus an `nvmeXnY` pattern.

## E-Series Flow

`netapp_smdevices()`:

1. Creates libnvme global context.
2. Parses options.
3. Validates output format.
4. Scans `/dev`.
5. Opens each NVMe namespace device.
6. Calls `netapp_smdevices_get_info()`.
7. Prints matching devices.

`netapp_smdevices_get_info()`:

- Identifies controller.
- Requires model name prefix `NetApp E-Series`.
- Gets NSID via `libnvme_get_nsid()`.
- Identifies namespace.
- Stores device path.

E-Series output derives:

- Array name from controller vendor-specific bytes at `ctrl.vs[20]`, converted from UCS-2-ish layout by `netapp_convert_string()`.
- Volume name from namespace vendor-specific bytes.
- Volume ID from namespace NGUID.
- Controller side from `ctrl.vs[0] & 0x1`.
- Namespace size, block size, and firmware version from identify data.

## ONTAP Flow

`netapp_ontapdevices()` mirrors `smdevices` but calls `netapp_ontapdevices_get_info()`.

`netapp_ontapdevices_get_info()`:

- Identifies controller.
- Requires model name prefix `NetApp ONTAP Controller`.
- Gets NSID and namespace identify data.
- Allocates namespace descriptor list and reads it with `nvme_identify_ns_descs_list()`.
- Copies UUID from the namespace descriptor payload.
- Reads ONTAP C2 namespace info log.

ONTAP output derives:

- Vserver and namespace path from C2 TLVs via `netapp_get_ontap_labels()`.
- Subsystem name from the suffix of `ctrl.subnqn`.
- UUID from namespace descriptor data.
- Size, used bytes, block size, and firmware version from identify data.

## Output Modes

`netapp_output_format()` supports:

- `normal`
- `column`
- `json` when `CONFIG_JSONC` is available

E-Series output helpers:

- `netapp_smdevices_print_regular()`
- `netapp_smdevices_print_verbose()`
- `netapp_smdevices_print_json()`
- `netapp_smdevice_json()`

ONTAP output helpers:

- `netapp_ontapdevices_print_regular()`
- `netapp_ontapdevices_print_verbose()`
- `netapp_ontapdevices_print_json()`
- `netapp_ontapdevice_json()`

Verbose mode adds used size, block format, and firmware version.

## Utility Functions

- `netapp_convert_string()` squashes UCS-2-like label strings into ASCII by taking every second byte.
- `netapp_nguid_to_str()` formats a 16-byte NGUID as 32 lowercase hex chars.
- `netapp_get_ns_size()` computes human-readable namespace size using SI suffixes.
- `netapp_get_ns_attrs()` computes size, used bytes, block size, and firmware version.
- `ontap_get_subsysname()` strips trailing spaces from target NQN and extracts the final dot-separated component.
- `ontap_labels_to_str()` copies printable ONTAP label bytes.
- `netapp_get_ontap_labels()` walks expected TLV order and composes namespace path from volume/name if explicit path TLV is absent.

## Dependencies

Uses:

- libnvme open/close, identify controller, identify namespace, namespace descriptors, NSID lookup, admin passthrough.
- nvme-cli JSON helpers, global output format, verbose flag.
- `util/suffix.h` for SI/binary suffix formatting.
- Linux `/dev` namespace naming assumptions.

## Notes

- Device classification is based on model string prefixes, not vendor ID.
- The ONTAP namespace UUID extraction assumes descriptor layout by copying after one `struct nvme_ns_id_desc`.
- Several helper functions use fixed-size buffers and `sprintf()`/`snprintf()` with known internal data sizes.
- Access state is printed as `unknown` for both E-Series modes.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/netapp/netapp-nvme.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/netapp/netapp-nvme.h -->
# File Research: sources/virtualization/nvme-cli/plugins/netapp/netapp-nvme.h

## Role

Command registration header for the NetApp nvme-cli plugin.

## Registered Plugin

Plugin name: `netapp`.

Description: `NetApp vendor specific extensions`.

Version source: `NVME_VERSION`.

## Registered Commands

- `smdevices`: mapped to `netapp_smdevices`, displays NetApp E-Series volume information.
- `ontapdevices`: mapped to `netapp_ontapdevices`, displays NetApp ONTAP namespace/device information.

## Dependency Relationship

Included by `netapp-nvme.c` with `CREATE_CMD` defined. Uses `cmd.h` and `define_cmd.h` for nvme-cli macro expansion.

## Notes

The file is declarative and contains no runtime logic.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/netapp/netapp-nvme.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/nvidia/nvidia-nvme.c -->
# File Research: sources/virtualization/nvme-cli/plugins/nvidia/nvidia-nvme.c

## Role

Implements NVIDIA vendor-specific Identify Controller display extension for nvme-cli.

The plugin adds an `id-ctrl` command that delegates most Identify Controller behavior to the shared nvme-cli `__id_ctrl()` helper, while providing a vendor-specific callback for the Identify Controller vendor-specific bytes.

## Main Data Structure

`struct nvme_vu_id_ctrl_field` overlays the vendor-specific Identify Controller area:

- `json_rpc_2_0_mjr`
- `json_rpc_2_0_mnr`
- `json_rpc_2_0_ter`
- `reserved0[1018]`

These fields are little-endian 16-bit values.

## Output Logic

`nvidia_id_ctrl()` casts the vendor-specific pointer to `struct nvme_vu_id_ctrl_field`, formats the JSON-RPC 2.0 version as a concatenated hex string:

`0x%04x%04x%04x`

It prints either:

- normal output: `json_rpc_2_0_ver : <value>`
- JSON output: adds key `json_rpc_2_0_ver`

`json_nvidia_id_ctrl()` adds that key to the JSON object.

## Public Command Handler

`id_ctrl()` calls:

`__id_ctrl(argc, argv, acmd, plugin, nvidia_id_ctrl)`

This means standard nvme-cli Identify Controller parsing, device opening, and output handling remain centralized outside this file.

## Dependencies

Includes:

- libnvme
- `common.h`
- `nvme.h`
- `plugin.h`
- `nvidia-nvme.h`

## Notes

- The file is intentionally small and callback-based.
- It does not do independent device/model validation.
- All command registration is in `nvidia-nvme.h`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/nvidia/nvidia-nvme.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/nvidia/nvidia-nvme.h -->
# File Research: sources/virtualization/nvme-cli/plugins/nvidia/nvidia-nvme.h

## Role

Command registration header for the NVIDIA nvme-cli plugin.

## Registered Plugin

Plugin name: `nvidia`.

Description: `NVIDIA vendor specific extensions`.

Version source: `NVME_VERSION`.

## Registered Command

- `id-ctrl`: mapped to `id_ctrl`, described as `Send NVMe Identify Controller`.

## Dependency Relationship

Included by `nvidia-nvme.c` with `CREATE_CMD` defined. Uses nvme-cli plugin macros from `cmd.h` and finalizes via `define_cmd.h`.

## Notes

This header contains only command registration and no parsing or device logic.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/nvidia/nvidia-nvme.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/meson.build -->
# File Research: sources/virtualization/nvme-cli/plugins/ocp/meson.build

## Role

Meson build snippet that adds OCP plugin source files to the `plugin_sources` list.

## Always-Built Sources

The file appends these OCP sources:

- `ocp-utils.c`
- `ocp-nvme.c`
- `ocp-clear-features.c`
- `ocp-smart-extended-log.c`
- `ocp-fw-activation-history.c`
- `ocp-telemetry-decode.c`
- `ocp-hardware-component-log.c`
- `ocp-print.c`
- `ocp-print-stdout.c`
- `ocp-print-binary.c`

## Conditional Source

If `json_c_dep.found()` is true, it also adds:

- `ocp-print-json.c`

## Dependency Relationship

The files researched in this group are included here:

- `ocp-clear-features.c`
- `ocp-fw-activation-history.c`
- `ocp-hardware-component-log.c`

Their JSON output support depends indirectly on the conditional inclusion of `ocp-print-json.c`.

## Notes

This file contains no runtime code. It controls compilation membership for the OCP plugin implementation.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/meson.build -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-clear-features.c -->
# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-clear-features.c

## Role

Implements OCP feature clearing and OCP PCIe correctable error counter retrieval helpers used by the main OCP plugin command wrappers.

## Core Helper

`ocp_clear_feature()` centralizes OCP feature clear behavior:

1. Parses device and `--no-uuid`.
2. Opens NVMe device.
3. Unless `--no-uuid` is set, finds the OCP UUID index using `ocp_get_uuid_index()`.
4. Sets bit 31 in the feature value (`clear = 1 << 31`).
5. Sends `nvme_set_features()` with the target feature ID and UUID index.
6. Prints success/failure/status.

The `--no-uuid` option exists because OCP 1.0 does not require UUID index support, while OCP 2.0 does.

## Public Functions

- `ocp_clear_fw_update_history()`: clears OCP firmware update history using `OCP_FID_CFUH`.
- `ocp_clear_pcie_correctable_errors()`: clears OCP PCIe correctable error counters using `OCP_FID_CPCIE`.
- `get_ocp_error_counters()`: issues Get Feature for `OCP_FID_CPCIE`.

## Get Error Counters

`get_ocp_error_counters()` options:

- `--sel` / `-s`: current/default/saved/supported selector.
- `--namespace-id` / `-n`: namespace ID.
- `--no-uuid` / `-u`: skip UUID index detection.

It calls `nvme_get_features()` with the optional UUID index and prints:

- `get-feature:0xC3 <selector> value: <hex>`

If selector is `NVME_GET_FEATURES_SEL_SUPPORTED`, it calls `nvme_show_select_result()`.

## Dependencies

Includes:

- `nvme-cmds.h`
- `nvme-print.h`
- `util/types.h`
- `ocp-nvme.h`
- `ocp-utils.h`

Uses nvme-cli parsing/opening helpers, libnvme feature APIs, and OCP constants from `ocp-nvme.h`.

## Notes

- The file exposes implementation functions declared in `ocp-clear-features.h`.
- Command names are wrapped and registered from `ocp-nvme.c`, not directly in this file.
- Failure to find a UUID index returns immediately for UUID-aware mode.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-clear-features.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-clear-features.h -->
# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-clear-features.h

## Role

Header declaring OCP clear-feature and error-counter functions for use by the main OCP plugin implementation.

## Declarations

- `ocp_clear_fw_update_history()`
- `ocp_clear_pcie_correctable_errors()`
- `get_ocp_error_counters()`

Each uses the nvme-cli command handler signature with `argc`, `argv`, `struct command *`, and `struct plugin *`.

## Dependency Relationship

Implemented by `ocp-clear-features.c`. Called by wrappers in `ocp-nvme.c`.

## Notes

The header has no include guard or `#pragma once`, but it only contains function declarations and copyright/license text.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-clear-features.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-fw-activation-history.c -->
# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-fw-activation-history.c

## Role

Implements retrieval and validation of the OCP firmware activation history log.

## Public Entry Point

`ocp_fw_activation_history_log()` is the command handler implementation. It is wrapped by the main OCP plugin and declared in `ocp-fw-activation-history.h`.

## Flow

1. Parses and opens the NVMe device.
2. Initializes a zeroed `struct fw_activation_history`.
3. Best-effort retrieves OCP UUID index with `ocp_get_uuid_index()`.
4. Builds a Get Log Page command for `OCP_LID_FAHL_OBSOLETE`.
5. Encodes UUID index into `cdw14`.
6. Calls `libnvme_get_log()`.
7. Validates returned log page GUID against `ocp_fw_activation_history_guid`.
8. Validates output format through `validate_output_format()`.
9. Prints through `ocp_fw_act_history()`.

## GUID Validation

The expected firmware activation history GUID is stored as a 16-byte array:

`6D 79 9A 76 B4 DA F6 A3 E2 4D B2 8A AC F3 1C D1`

If the log fetch succeeds but GUID differs, the function returns `-EINVAL`.

## Dependencies

Includes:

- `common.h`
- `nvme-print.h`
- `ocp-fw-activation-history.h`
- `ocp-nvme.h`
- `ocp-print.h`
- `ocp-utils.h`

Uses libnvme command initialization and nvme-cli print dispatch.

## Notes

- UUID index detection is best effort; correctness is enforced by GUID comparison.
- The function fetches a fixed-size `struct fw_activation_history`.
- Printing is delegated to the OCP print abstraction, allowing stdout/JSON/binary behavior elsewhere.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-fw-activation-history.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-fw-activation-history.h -->
# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-fw-activation-history.h

## Role

Defines the packed OCP firmware activation history log structures and declares the retrieval command handler.

## Structures

`struct fw_activation_history_entry` contains:

- version number
- entry length
- activation count
- NVMe timestamp
- power cycle count
- previous firmware revision
- new firmware revision
- slot number
- commit action
- result
- reserved fields

`struct fw_activation_history` contains:

- log ID
- valid entry count
- 20 activation history entries
- reserved padding
- log page version
- 16-byte GUID represented as two `__le64` values

Both structures are packed to match on-device log layout.

## Public Declaration

- `ocp_fw_activation_history_log()`

## Dependencies

Includes:

- `libnvme.h`
- `common.h`

Forward declares `struct command` and `struct plugin`.

## Notes

This header is consumed by retrieval code and OCP print implementations. It is part of the binary contract for parsing OCP firmware activation history data.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-fw-activation-history.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-hardware-component-log.c -->
# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-hardware-component-log.c

## Role

Implements retrieval and display dispatch for the OCP Hardware Component Log page.

## Public Entry Point

`ocp_hwcomp_log()` is the command handler. It supports:

- `--comp-id` / `-i`: component identifier, with symbolic values.
- `--list` / `-l`: list component descriptions.

Symbolic component IDs include `asic`, `nand`, `dram`, `pmic`, `pcb`, `cap`, `reg`, `case`, `sn`, `country`, `hw-rev`, `born-on-date`, and `vendor`.

## Component ID Mapping

`hwcomp_id_to_string()` maps enum values to readable descriptions:

- ASIC, NAND, DRAM, PMIC, PCB, capacitor, regulator, case.
- Device serial number, country of origin, global hardware revision, born-on date.
- Vendor unique range `0x8000 ... 0xffff`.
- Reserved fallback.

## Log Retrieval Flow

`ocp_hwcomp_log()`:

1. Parses command options and opens device.
2. Calls `get_hwcomp_log()`.

`get_hwcomp_log()`:

1. Validates output format.
2. Calls `get_hwcomp_log_data()`.
3. Calls `ocp_show_hwcomp_log(&log, id, list, fmt)`.
4. Frees allocated descriptor data.

`get_hwcomp_log_data()`:

1. Retrieves OCP UUID index via `ocp_get_uuid_index()`.
2. Fetches the fixed header portion up to `offsetof(struct hwcomp_log, desc)`.
3. Converts the 128-bit log size.
4. For log version 1, treats size as DWORD count and multiplies by 4 bytes.
5. Validates size is larger than the header.
6. Allocates descriptor payload.
7. Fetches remaining payload using Get Log Page with log page offset.
8. Stores payload pointer in `log->desc`.

## Logging Helpers

The file defines `print_info_array()` and `print_info_error()` macros that emit diagnostic information only when `log_level >= LIBNVME_LOG_INFO`.

There is a disabled `HWCOMP_DUMMY` block containing a large dummy log byte array for local testing if enabled at compile time.

## Dependencies

Includes:

- `common.h`
- `util/types.h`
- `logging.h`
- `nvme-print.h`
- `ocp-hardware-component-log.h`
- `ocp-print.h`
- `ocp-utils.h`

Uses libnvme Get Log Page helpers, nvme-cli output-format validation, OCP UUID lookup, and OCP print dispatch.

## Notes

- The log header has an inline pointer field `desc`; only bytes before that pointer are fetched for the header.
- `desc` is heap allocated and must be freed by the caller.
- If the second log fetch fails, `log->desc` is freed but not reset before returning; caller exits on error, so it is not reused.
- The command is display-oriented and delegates detailed parsing/printing to `ocp_show_hwcomp_log()`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-hardware-component-log.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-hardware-component-log.h -->
# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-hardware-component-log.h

## Role

Defines the OCP Hardware Component Log data structures, component ID enum, and public functions.

## Constants

- `HWCOMP_RSVD2_LEN`: 14
- `HWCOMP_SIZE_LEN`: 16
- `HWCOMP_RSVD48_LEN`: 16

## Structures

`struct hwcomp_desc` is packed and represents a hardware component descriptor prefix:

- `date_lot_size`
- `add_info_size`
- `id`
- `mfg`
- `rev`
- `mfg_code`

`struct hwcomp_log` is packed and represents the fetched log header plus descriptor pointer:

- version
- reserved bytes
- GUID
- 16-byte size field
- reserved bytes
- `struct hwcomp_desc *desc`

`struct hwcomp_desc_entry` is an unpacked parsed descriptor view:

- pointer to descriptor
- decoded date/lot size and pointer
- decoded additional-info size and pointer
- total descriptor size

## Component Enum

`enum hwcomp_id` defines standard and vendor component identifiers:

- Reserved: `0`
- ASIC through born-on date: `1` through `12`
- Vendor range start: `0x8000`
- Max: `0xffff`

## Public Declarations

- `ocp_hwcomp_log()`
- `hwcomp_id_to_string()`

## Dependencies

Includes:

- `cmd.h`
- `common.h`
- `ocp-nvme.h`

## Notes

The structures describe on-device binary layout and are consumed by both retrieval and print modules. The `desc` pointer in `struct hwcomp_log` is not an on-wire field; retrieval code deliberately fetches only up to its offset for the header.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-hardware-component-log.h -->