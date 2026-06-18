# Group Research: group_1337_nvme_cli_sources_virtualization_nvme_cli_plugins_ocp_ocp_telemetry__19e4803e7fb8

Scope: `Docs/research_subset_a.md`, source tree `sources/virtualization/nvme-cli`.

This group covers OCP telemetry decoding support and the Sandisk nvme-cli vendor plugin layer. The OCP files implement binary telemetry/string-log interpretation into text and JSON. The Sandisk files register user-facing plugin commands, determine device capabilities, and route many operations through shared WDC command implementations while adding Sandisk-specific telemetry capture, UDUI capture, SN861 resize, and C2 firmware activation history handling.

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-telemetry-decode.c -->
# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-telemetry-decode.c

## Role

`ocp-telemetry-decode.c` is the implementation side of OCP telemetry log decoding. It consumes global telemetry and string-log buffers declared in the companion header, interprets OCP/NVMe telemetry headers, statistics descriptors, event FIFO descriptors, and optional vendor-unique strings, then emits either plain text or JSON depending on build configuration and caller options.

The file is data-format driven. It contains parser tables for fixed structures, static fallback names for statistic identifiers, helper printers, string-table lookup logic, event-class parsers, statistics parsers, event FIFO iteration, and top-level normal/JSON output functions.

## Main Data Tables

The top of the file defines display-oriented `struct request_data` arrays for generic parsing:

- `host_log_page_header` and `controller_log_page_header` describe the generic 512-byte telemetry log header layouts.
- `reason_identifier` describes the embedded OCP reason identifier.
- `ocp_header_in_da1` describes the OCP data-area-1 header, including profile, string-log size, firmware revision, statistics ranges, and up to 16 FIFO locations.
- `smart` and `smart_extended` describe the standard SMART/health and OCP extended SMART blocks embedded after the DA1 OCP header.

`statistic_identifiers_map` provides fallback text for OCP statistic IDs `0x00` through `0x6f` when a telemetry string log does not provide an ASCII string entry. The same file also has early legacy-style printers (`print_vu_event_data`, `print_stats_desc`, `print_telemetry_fifo_event`) that use the ID-to-string helpers from the header and print decoded event details directly.

## String Log Lookup

The string lookup path is centered on `parse_ocp_telemetry_string_log()`. It dispatches to:

- `get_statistic_id_ascii_string()` for statistic identifier strings.
- `get_event_id_ascii_string()` for event ID strings.
- `get_vu_event_id_ascii_string()` for vendor-unique event ID strings.
- FIFO ASCII names stored directly in `nvme_ocp_telemetry_string_header::fifo_ascii_string`.

All table offsets and sizes are treated as DWORD counts and multiplied by `SIZE_OF_DWORD`. If a statistic string is missing and the ID is in the fixed OCP range, the parser falls back to `statistic_identifiers_map`.

## Offset Calculation

`get_telemetry_das_offset_and_size()` validates input pointers, selects the proper telemetry header size based on `NVME_LOG_LID_TELEMETRY_HOST` versus `NVME_LOG_LID_TELEMETRY_CTRL`, and calculates start offsets and byte sizes for DA1 through DA4. It uses the telemetry common header's last-block fields and the OCP 512-byte block size. These offsets are reused by statistics and FIFO parsing.

## Event Parsing

When `CONFIG_JSONC` is enabled, the file provides detailed event parsers:

- `parse_time_stamp_event()` handles timestamp class events with 8 bytes of class-specific data and optional VU payload.
- `parse_pcie_event()` handles 4 bytes of PCIe class-specific data and optional VU payload.
- `parse_nvme_event()` handles 8 bytes of NVMe class-specific data and optional VU payload.
- `parse_media_wear_event()` handles 12 bytes of media-wear class-specific data and optional VU payload.
- `parse_common_event()` handles classes whose event body is treated as VU event identifier plus VU data.

Each parser supports three output modes through the same code path: JSON object population, file-backed text output, or stdout text output. They add common fields such as class-specific data, VU event ID, VU event string, and VU data. Size checks are minimal and assume the containing FIFO range is trustworthy.

## FIFO Parsing

`parse_event_fifo()` is the core FIFO walker. For a single FIFO it:

1. Resolves the FIFO name from the string log.
2. Creates a JSON array or prints a text section header.
3. Iterates event descriptors until the FIFO size is exhausted or a reserved class terminator is found.
4. Emits generic descriptor fields: debug class, event ID, event string, and data size.
5. Dispatches class-specific parsing for timestamp, PCIe, NVMe, reset, boot, firmware assert, temperature, media, media wear, and statistic snapshot classes.
6. Advances by descriptor size plus event data size.

`parse_event_fifos()` builds a 16-entry `nvme_ocp_event_fifo_data` array from DA1 header metadata, filters FIFOs by the requested data area, calculates FIFO byte offsets from DWORD starts/sizes, and invokes `parse_event_fifo()` for each matching FIFO. It supports DA1 and DA2 only in the actual pointer selection.

## Statistics Parsing

`parse_statistics()` selects the statistics region for DA1 or DA2 using the `da1_statistic_start`, `da1_statistic_size`, `da2_statistic_start`, and `da2_statistic_size` fields in the OCP DA1 header. It walks `nvme_ocp_telemetry_statistic_descriptor` entries until the configured region ends or a reserved statistic ID terminator is seen.

`parse_statistic()` emits descriptor metadata and the statistic payload. Three bad-block statistics get special field names and split percentage/raw values:

- `MAX_DIE_BAD_BLOCK_ID`
- `MAX_NAND_CHANNEL_BAD_BLOCK_ID`
- `MIN_NAND_CHANNEL_BAD_BLOCK_ID`

All other statistic data is emitted as a formatted variable-size hex string.

## Top-Level Output

`print_ocp_telemetry_normal()` emits text to stdout or `<output_file>.txt`. It prints the log header, reason identifier, DA1 OCP header, SMART, extended SMART, DA1 statistics, DA1 FIFOs, and optionally DA2 statistics/FIFOs when `options->data_area == 2`.

`print_ocp_telemetry_json()` builds a JSON object with the same major sections and writes it to `<output_file>.json` or prints it. It always uses `host_log_page_header` for the top header in the JSON path, even though the normal path checks `options->telemetry_type` for host versus controller.

## Dependencies and Integration

This file depends on nvme-cli/libnvme types and helpers from `common.h`, `nvme.h`, `plugin.h`, `util/types.h`, `nvme-print.h`, and `ocp-telemetry-decode.h`. It relies heavily on helpers such as `generic_structure_parser()`, `print_formatted_var_size_str()`, JSON helper functions, `nvme_show_error()`, and endianness conversion macros. Its public entry points are declared in `ocp-telemetry-decode.h`.

## Notable Risks

The parser frequently casts unaligned byte pointers directly to packed or scalar types and does only limited bounds validation inside telemetry regions. Many values are consumed without little-endian conversion before arithmetic or JSON formatting. String lookup copies `ascii_id_length + 1` bytes into caller-provided buffers without checking destination capacity. `parse_event_fifo()` allocates 41 bytes for `description` but clears only `sizeof(40)` bytes, and some error paths return without freeing that allocation. These are acceptable for a diagnostic decoder in trusted tooling contexts but should be reviewed carefully before using this parser on untrusted telemetry blobs.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-telemetry-decode.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-telemetry-decode.h -->
# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-telemetry-decode.h

## Role

`ocp-telemetry-decode.h` is the schema and interface header for the OCP telemetry decoder. It defines telemetry statistic IDs, event class IDs, event-specific ID-to-string lookup tables, binary layout structs for telemetry/string logs, string constants used in output, parser option structures, and public function prototypes implemented by `ocp-telemetry-decode.c`.

## Global Buffers

The header declares:

- `extern __u8 *ptelemetry_buffer`
- `extern __u8 *pstring_buffer`

The decoder implementation treats these as the active telemetry log buffer and C9 string-log buffer. Most parser functions take offsets/options but still rely on these globals for the underlying binary content.

## ID Enumerations and String Tables

The first half of the file is a large set of OCP/NVMe telemetry identifiers and their display strings:

- `enum TELEMETRY_STATISTIC_ID` and `telemetry_stat_id_str[]`.
- `enum TELEMETRY_EVENT_CLASS_TYPE` and `telemetry_event_class_str[]`.
- Timestamp, PCIe, NVMe, reset, boot sequence, firmware assert, temperature, media debug, media wear, and virtual FIFO event ID enums.
- PCIe state, speed, and width enums.

The static inline helpers at the end of this table section use `ARGSTR()` and `arg_str()` to safely return `"unrecognized"` if an index is out of range or has no string. The implementation file uses these helpers in direct printer paths.

## Constants and Output Labels

The header defines key telemetry sizing constants:

- `TELEMETRY_HEADER_SIZE`, `TELEMETRY_BYTE_PER_BLOCK`, and `OCP_TELEMETRY_DATA_BLOCK_SIZE` are 512-byte based.
- `SIZE_OF_DWORD` is 4 and is used throughout string-log, stats, and FIFO calculations.
- `MAX_NUM_FIFOS` is 16.
- `DEFAULT_TELEMETRY_LOG`, `DEFAULT_STRING_BIN`, and `DEFAULT_OUTPUT_FORMAT_JSON` provide CLI defaults.

It also defines output string constants such as `STR_LOG_PAGE_HEADER`, `STR_REASON_IDENTIFIER`, `STR_DA_1_STATS`, `STR_EVENT_IDENTIFIER`, `STR_VU_DATA`, and separator lines used consistently by text and JSON paths.

## Binary Layout Structures

The header carries two groups of layout definitions. Older/general structures include `telemetry_initiated_log`, `telemetry_stats_desc`, `telemetry_event_desc`, `event_fifo`, and `telemetry_data_area_1`. The newer OCP-specific packed definitions include:

- `nvme_ocp_telemetry_reason_id`
- `nvme_ocp_telemetry_common_header`
- `nvme_ocp_telemetry_host_initiated_header`
- `nvme_ocp_telemetry_controller_initiated_header`
- `nvme_ocp_telemetry_smart`
- `nvme_ocp_telemetry_smart_extended`
- `nvme_ocp_header_in_da1`
- `nvme_ocp_telemetry_statistic_descriptor`
- `nvme_ocp_telemetry_event_descriptor`
- class-specific payload structs for timestamp, PCIe, NVMe, media wear, and common VU data
- string-log table entries and `nvme_ocp_telemetry_string_header`

These structures encode OCP telemetry offsets directly in C type layout and comments include byte positions for maintainability.

## String Log Structures

The header defines both `telemetry_str_log_format` and the OCP-specific `nvme_ocp_telemetry_string_header`, plus table entry structs for statistics, event, and VU event string lookup. The string log format is organized around DWORD offsets/sizes for statistics identifier string table, event string table, VU event string table, ASCII table, and 16 FIFO ASCII labels.

## Parser Options and Prototypes

`struct ocp_telemetry_parse_options` carries input/output choices:

- telemetry log filename
- string log filename
- output file prefix
- output format
- requested data area
- telemetry type

The prototypes expose the full parser surface: top-level telemetry parsing, string lookup, DA offset calculation, statistics parsing, FIFO parsing, event-class parsing, and normal/JSON printing.

## Dependencies and Integration

The header includes nvme-cli headers `nvme.h`, `nvme-print.h`, `util/utils.h`, `common.h`, and `ocp-nvme.h`. It assumes `struct json_object` is visible from included nvme-cli JSON support and that packed layout support is available through the project headers.

## Notable Risks

This header embeds many static const string arrays in a header, meaning each translation unit that includes it gets its own copy. That is acceptable for plugin-local code but increases object size. Some enum comments and names contain typos or legacy names, but the numeric values are the important ABI. Several packed structures contain bitfields; those are convenient for local parsing but can be compiler-layout sensitive compared with explicit mask/shifts.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-telemetry-decode.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-types.h -->
# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-types.h

## Role

`ocp-types.h` is a tiny helper header for OCP-specific bitfield access. It wraps the nvme-cli `NVME_GET` and `NVME_SET` macros with OCP-prefixed field names:

- `OCP_GET(value, name)` expands to `NVME_GET(value, OCP_##name)`.
- `OCP_SET(value, name)` expands to `NVME_SET(value, OCP_##name)`.

## Defined Field

The file defines `enum nvme_ocp_enable_ieee1667_silo` with:

- `NVME_OCP_ENABLE_IEEE1667_SILO_SHIFT = 31`
- `NVME_OCP_ENABLE_IEEE1667_SILO_MASK = 1`

This describes a one-bit OCP IEEE1667 silo enable flag at bit 31.

## Dependencies and Integration

The file does not include other headers directly. It assumes callers include the nvme-cli headers that define `NVME_GET` and `NVME_SET` before using these macros. It is likely included by OCP command code that wants compact feature-field accessors.

## Notable Risks

There is no include dependency enforcement in this header. If included before the base NVMe bitfield macros are available, compilation will fail at macro use sites rather than at include time.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-types.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-utils.c -->
# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-utils.c

## Role

`ocp-utils.c` provides small shared helpers for OCP plugin commands. It centralizes OCP UUID handling, simple OCP get-log command construction, and detection of a specific TCG activity persistent-event encoding.

## UUID Handling

The file defines the OCP UUID as `ocp_uuid`, a 16-byte constant:

`c1 94 d5 5b e0 94 47 94 a2 1d 29 99 8f 56 be 6f`

`ocp_find_uuid_index()` uses `libnvme_find_uuid()` to locate this UUID in an identify UUID list. It returns zero and stores the positive index when found, initializes `*index` to zero, and returns `-errno` if the UUID cannot be found.

`ocp_get_uuid_index()` retrieves the UUID list via `nvme_identify_uuid_list()` and delegates to `ocp_find_uuid_index()`.

## Simple Log Retrieval

`ocp_get_log_simple()` creates a `libnvme_passthru_cmd` for an OCP DSSD log ID. It:

1. Attempts to retrieve the OCP UUID index.
2. Calls `nvme_init_get_log()` using `NVME_NSID_ALL`, the requested log ID, `NVME_CSI_NVM`, the caller buffer, and the requested length.
3. Encodes the UUID index into `cdw14`.
4. Calls `libnvme_get_log()`.

The helper ignores the return value of `ocp_get_uuid_index()`, so a UUID lookup failure leaves `uidx` at whatever value the callee set, usually zero.

## Persistent Event Predicate

`ocp_is_tcg_activity_event()` inspects a persistent event entry and associated vendor-specific descriptor. It returns true only when the event is vendor-specific and exact header/length/type constants match the TCG activity event shape:

- event type is `NVME_PEL_VENDOR_SPECIFIC_EVENT`
- event header length is `0x15`
- vendor-specific information length is `0x04`
- event length is `0x30`
- vendor-specific event code is `0x01`
- vendor-specific event data length is `0x26`
- vendor-specific data type is binary

## Dependencies and Integration

The file includes `nvme-cmds.h`, `ocp-nvme.h`, `ocp-utils.h`, `types.h`, and utility type headers. It works at the libnvme transport-handle layer and is meant to be shared by OCP command implementations.

## Notable Risks

`ocp_get_log_simple()` does not propagate UUID lookup failure before issuing the log command. That may be intentional for devices where UUID index zero is acceptable, but it means callers cannot distinguish “UUID missing” from “log read attempted at index zero”.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-utils.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-utils.h -->
# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-utils.h

## Role

`ocp-utils.h` declares the shared OCP utility interface implemented by `ocp-utils.c`. It exposes the OCP UUID constant, UUID lookup helpers, simple OCP log retrieval, and the TCG activity persistent-event predicate.

## Public API

The header declares:

- `extern const unsigned char ocp_uuid[NVME_UUID_LEN]`
- `ocp_get_uuid_index(struct libnvme_transport_handle *hdl, __u8 *index)`
- `ocp_find_uuid_index(struct nvme_id_uuid_list *uuid_list, __u8 *index)`
- `ocp_get_log_simple(struct libnvme_transport_handle *hdl, enum ocp_dssd_log_id lid, __u32 len, void *log)`
- `ocp_is_tcg_activity_event(struct nvme_persistent_event_entry *pevent_entry_head, __u16 el, __u16 vsil)`

The comments describe return behavior for UUID lookup: zero on success, positive NVMe command result from UUID-list retrieval, or negative POSIX-style errors otherwise.

## Dependencies and Integration

The file includes `nvme.h` for libnvme and NVMe structure/type visibility. It references `enum ocp_dssd_log_id`, which is provided by OCP plugin headers included by users of this header in the broader plugin code.

## Notable Risks

The prototype for `ocp_get_log_simple()` is a long single line and depends on the OCP DSSD log-id enum being visible at the point of use. There are no inline guards for misuse beyond normal C type checking.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-utils.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/sandisk/sandisk-nvme.c -->
# File Research: sources/virtualization/nvme-cli/plugins/sandisk/sandisk-nvme.c

## Role

`sandisk-nvme.c` is the implementation file for the Sandisk nvme-cli plugin. It registers command handlers through `sandisk-nvme.h`, implements Sandisk-specific telemetry/internal log paths, SN861 resize, firmware activation history on C2 logs, clear firmware history via vendor feature, capability reporting, and delegates many commands to the WDC plugin compatibility layer.

The plugin version in the header is `3.1.3`, and this source pulls in `plugins/wdc/wdc-nvme-cmds.h` because most command handlers are wrappers around `run_wdc_*` functions.

## Telemetry and Internal Firmware Log Capture

The largest command path is `sndk_vs_internal_fw_log()`. It parses options for output file, transfer size, data area, telemetry type, verbose mode, and deprecated file-size/offset parameters. It opens the NVMe handle, scans topology, checks that the device is Sandisk/WDC-supported, builds a default output filename from the controller serial and timestamp when none is provided, validates data-area values, parses the requested telemetry type (`NONE`, `HOST`, `CONTROLLER`, or `BOTH`), obtains device capabilities, and selects the capture method.

`sndk_do_cap_telemetry_log()` captures NVMe telemetry logs through libnvme. It validates telemetry support via controller `lpa`, optionally enables ETDAS for data area 4, handles host-initiated versus controller-initiated selection, rejects `BOTH`, opens the output file, retrieves the full telemetry log through libnvme, writes the full buffer, fsyncs it, clears ETDAS if it changed host behavior, and frees the log.

`sndk_do_cap_both_telemetry_log()` captures host and controller telemetry separately into temporary files, then packages them into a tar file by constructing and executing a `tar -cf` command. It removes the temporary files afterward.

`sndk_do_cap_udui()` captures Device Unit Info through vendor opcode `0xFA`, first reading an NVMe telemetry-like header to determine total size from `dalb4`, then reading chunks by offset via `sndk_dump_udui_data()` and writing them to the output file.

If Sandisk-specific capabilities are not present, `sndk_vs_internal_fw_log()` falls back to `run_wdc_vs_internal_fw_log()`.

## Resize Command

The file defines an SN861-specific resize admin command:

- opcode `0xD1`
- 4096-byte buffer
- `cdw10 = 0x40`
- `cdw12 = 0x103`
- `cdw13 = 0x1`
- new size copied into the command buffer

`sndk_drive_resize()` checks capabilities and uses this path when `SNDK_DRIVE_CAP_RESIZE_SN861` is set. Otherwise, it delegates to `run_wdc_drive_resize()`.

## Firmware Activation History

The file has a C2 log GUID constant `ocp_C2_guid` and C2 firmware activation history support:

- `sndk_get_fw_act_history_C2()` reads log page `0xC2`, validates the log page GUID, limits entries to `SNDK_MAX_NUM_ACT_HIST_ENTRIES`, and dispatches printing.
- `sndk_print_fw_act_history_log_normal()` prints a tabular text view of entry number, timestamp, power-cycle count, previous/new firmware, slot, action bits, and result.
- `sndk_print_fw_act_history_log_json()` prints one JSON object per entry.
- `sndk_print_fw_act_history_log()` selects normal or JSON output.

Both normal and JSON paths detect the oldest entry when the circular table is full by comparing adjacent firmware activation history entry numbers.

`sndk_clear_fw_activate_history()` uses `sndk_do_clear_fw_activate_history_fid()` when the drive supports `SNDK_DRIVE_CAP_VU_FID_CLEAR_FW_ACT_HISTORY`; that helper sets feature ID `0xC1` with bit 31 set. Otherwise, the command delegates to WDC.

## Delegated Command Wrappers

Many handlers are thin wrappers to WDC plugin commands:

- NAND stats
- additional SMART log
- clear PCIe correctable errors
- drive status
- clear assert dump
- telemetry controller option
- reason identifier
- log page directory
- namespace resize
- drive info
- cloud SSD plugin version
- PCIe stats
- latency monitor log
- error recovery log
- device capabilities log
- unsupported requests log
- cloud boot SSD version
- cloud log
- hardware revision log
- device WAF
- set latency monitor feature
- temperature stats
- customer unique SMART log

This file therefore acts as a compatibility facade: Sandisk-specific capability detection decides whether to run local logic or reuse the WDC implementation.

## Capabilities Command

`sndk_capabilities()` scans topology, validates the device, retrieves the capability bitmask via `sndk_get_drive_capabilities()`, and prints a supported/not-supported line for each user-facing command and several underlying log pages. It reports `capabilities` itself as always supported after reaching that point.

## Dependencies and Integration

The file depends on libnvme, nvme-cli command parsing (`NVME_ARGS`, `parse_and_open`), cleanup attributes, `sandisk-utils.h`, and WDC command shims. It is compiled with `CREATE_CMD` before including `sandisk-nvme.h`, which causes the plugin command table to bind to the static functions defined here.

## Notable Risks

`sndk_do_cap_both_telemetry_log()` uses `system()` with a shell command assembled from file paths, quoting with double quotes but not escaping embedded double quotes or shell metacharacters inside paths. The telemetry capture path uses blocking writes and full-buffer allocation. Several local variables such as `device_id` and `read_vendor_id` are retrieved but not used in `sndk_vs_internal_fw_log()`. The JSON firmware-history printer reuses a single JSON root object across entries, which relies on overwriting identical keys before each print rather than creating a fresh object per entry.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/sandisk/sandisk-nvme.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/sandisk/sandisk-nvme.h -->
# File Research: sources/virtualization/nvme-cli/plugins/sandisk/sandisk-nvme.h

## Role

`sandisk-nvme.h` is the command registration header for the Sandisk nvme-cli plugin. It follows the nvme-cli plugin macro pattern: set `CMD_INC_FILE`, guard multi-read inclusion, define plugin metadata, list commands, and include `define_cmd.h`.

## Plugin Metadata

The header defines:

- plugin name: `sndk`
- description: `Sandisk vendor specific extensions`
- version: `3.1.3`

The plugin body is created with `PLUGIN(NAME(...), COMMAND_LIST(...))`.

## Registered Commands

The command list exposes the following CLI entries:

- `vs-internal-log`
- `vs-nand-stats`
- `vs-smart-add-log`
- `clear-pcie-correctable-errors`
- `get-drive-status`
- `clear-assert-dump`
- `drive-resize`
- `vs-fw-activate-history`
- `clear-fw-activate-history`
- `vs-telemetry-controller-option`
- `vs-error-reason-identifier`
- `log-page-directory`
- `namespace-resize`
- `vs-drive-info`
- `vs-temperature-stats`
- `capabilities`
- `cloud-SSD-plugin-version`
- `vs-pcie-stats`
- `get-latency-monitor-log`
- `get-error-recovery-log`
- `get-dev-capabilities-log`
- `get-unsupported-reqs-log`
- `cloud-boot-SSD-version`
- `vs-cloud-log`
- `vs-hw-rev-log`
- `vs-device-waf`
- `set-latency-monitor-feature`
- `cu-smart-log`

Each entry maps to a `sndk_*` handler implemented as a static function in `sandisk-nvme.c` when `CREATE_CMD` is defined.

## Dependencies and Integration

The header includes `cmd.h` inside the plugin guard and `define_cmd.h` at the end, matching nvme-cli plugin-generation conventions. `CMD_INC_FILE` is set to `plugins/sandisk/sandisk-nvme`, allowing the command macro infrastructure to re-include the file in different modes.

## Notable Risks

This header intentionally references handler names before normal C declarations; that is part of the nvme-cli macro generation pattern. The user-visible description for `namespace-resize` says `NamespaceDrive Resize`, which appears to be a typo.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/sandisk/sandisk-nvme.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/sandisk/sandisk-utils.c -->
# File Research: sources/virtualization/nvme-cli/plugins/sandisk/sandisk-utils.c

## Role

`sandisk-utils.c` implements the shared utility layer behind the Sandisk plugin. It handles device/vendor identification, device support checks, commit-action formatting, C2 device manageability log retrieval and parsing, capability-bitmask construction, serial-based filename generation, local time capture, snprintf wrapping, and controller-initiated telemetry option validation.

## UUIDs and Device Identity

The file defines three UUID constants:

- `WDC_UUID`
- `WDC_UUID_SN640_3`
- `SNDK_UUID`

These are used to retrieve vendor C2 device manageability log pages with the correct UUID index. `sndk_get_pci_ids()` locates the controller or namespace in libnvme topology, reads vendor/device IDs from sysfs, and parses them with `strtol()`. If sysfs probing fails in higher-level checks, `sndk_get_vendor_id()` falls back to `nvme_identify_ctrl()` and reads the controller vendor ID.

`sndk_check_device()` accepts Sandisk and WDC vendor IDs and rejects other vendors with an error message.

## C2 Device Manageability Parsing

The C2 log parsing helpers operate on a log whose top-level header is `sndk_c2_log_page_header`, followed by repeated `sndk_c2_log_subpage_header` entries:

- `sndk_parse_dev_mng_log_entry()` walks entries until it finds the requested entry ID, validating entry sizes, remaining length, and entry ID range.
- `sndk_nvme_parse_dev_status_log_entry()` extracts a `__u32` entry value.
- `sndk_nvme_parse_dev_status_log_str()` extracts variable-length string data from a CBS-style entry body.
- `sndk_validate_dev_mng_log()` validates the overall log entry sequence.
- `sndk_get_dev_mgmt_log_page_data()` reads log page `0xC2` using the selected UUID index, reallocates if the real length exceeds the initial 4 KiB buffer, validates the log, and returns a right-sized copy to the caller.
- `sndk_get_dev_mgment_data()` chooses Sandisk UUID first, then WDC UUID, then the SN640/SN655 UUID, defaulting to UUID index 0 if UUID lists are unsupported.

The parser intentionally treats malformed lengths, zero entry size, out-of-range entry IDs, and unaligned ends as invalid.

## Capability Detection

`sndk_get_drive_capabilities()` first obtains PCI IDs, falling back to identify vendor ID for NVMe-oF style devices where device ID may be unavailable. With a known vendor/device pair, it maps supported device IDs to capability flags. SN861, SN862, SNESSD, SN7150, SNCSSD, SNTMP, and WDC device families receive different combinations of internal log, C0/C3/CA/OCP log pages, UDUI, firmware history, clear feature, drive status, resize, cloud version, log-page directory, and latency monitor capabilities.

If the device ID is unavailable but a vendor ID is present, it delegates to `sndk_get_enc_drive_capabilities()`. If no Sandisk capability mapping matches, it falls back to `run_wdc_get_drive_capabilities()`.

`sndk_get_enc_drive_capabilities()` is the capability path for identified vendor but unknown/enclosure-style devices. For WDC vendor IDs it starts with a base capability set, selects a C2 UUID index, verifies C2 support via WDC helpers, reads C2 manageability data, extracts customer ID, marketing name, and form factor, checks individual supported log pages, and adds OCP/SN861-specific capabilities based on customer IDs or marketing name/form factor.

## Miscellaneous Utilities

`sndk_get_commit_action_bin()` maps commit action values 0 through 7 to binary-looking strings `000b` through `111b`, otherwise `INVALID`.

`sndk_get_serial_name()` identifies the controller, trims trailing spaces from the serial number, and formats a filename using an existing prefix plus serial plus suffix.

`sndk_UtilsGetTime()` fills `SNDK_UtilsTimeInfo` from local time and timezone offset.

`sndk_UtilsSnprintf()` is a thin `vsnprintf()` wrapper.

`sndk_check_ctrl_telemetry_option_disabled()` reads vendor feature ID `0xD2`; a nonzero result means controller-initiated telemetry is disabled and the helper returns `-EINVAL`.

## Dependencies and Integration

The file includes libnvme, nvme-cli command helpers, `sandisk-utils.h`, and WDC command helpers. It is the main dependency of `sandisk-nvme.c` for device validation and capability routing.

## Notable Risks

`sndk_get_dev_mgmt_log_page_data()` allocates data for callers but the ownership contract is implicit; callers must free it. `sndk_get_enc_drive_capabilities()` obtains `dev_mng_log` but does not free it before returning, which appears to leak that buffer. Several functions rely on sysfs paths and libnvme topology state being available. `sndk_nvme_parse_dev_status_log_str()` copies a length from device data into the caller buffer without taking the caller buffer capacity.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/sandisk/sandisk-utils.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/sandisk/sandisk-utils.h -->
# File Research: sources/virtualization/nvme-cli/plugins/sandisk/sandisk-utils.h

## Role

`sandisk-utils.h` is the constant, structure, and function declaration header for the Sandisk plugin utility layer. It encodes supported vendor/device IDs, capability bit definitions, vendor log page IDs, feature IDs, customer IDs, telemetry type values, C2 log structures, firmware activation history structures, and utility function prototypes.

## Device and Vendor IDs

The header defines Sandisk and WDC vendor IDs and a large set of device IDs across enterprise and client product families, including SN630, SN640, SN650, SN655, SN861, SN862, SNESSD generations, SN7150, SNCSSD, SN520/SN530/SN350/SN570/SN850X/SN5000/SN7000S, SN7100, SN8000S, SN720/SN730/SN740, ZN350, SN810, SN820CL, and SN5100S variants. `sandisk-utils.c` uses these IDs to map devices to capability flags.

## Capability Flags

The file defines a 64-bit capability flag namespace shared with the WDC plugin. Flags cover:

- internal log and UDUI/DUI capture modes
- C0/C1/C3/CA/D0 and OCP C1/C4/C5 log pages
- drive status, clear assert, clear PCIe, resize, namespace resize
- NAND stats, SMART log support, temperature stats, PCIe stats
- firmware activation history and clear firmware history
- controller telemetry option, reason ID, log page directory, drive info
- cloud SSD/plugin/boot version, cloud log, hardware revision log
- device WAF and latency monitor feature support

Mask macros group related capability variants such as SMART log support, clear PCIe support, internal log support, firmware history support, clear firmware history support, and resize support.

## Log Pages, Features, and Customer Values

Vendor log page IDs include:

- `0xC0` SMART/cloud attributes and EOL status
- `0xC1` error recovery
- `0xC2` firmware activation history or device manageability
- `0xC3` latency monitor
- `0xC4` device capabilities
- `0xC5` unsupported requests
- `0xCA` device info
- `0xCB` firmware activation history
- `0xD0` VU SMART

Feature IDs include `0xC1` for clear firmware activation history and `0xD2` for disabling controller telemetry option. Customer IDs and C2 entry IDs are defined for capability derivation.

## Structures

The header defines:

- `SNDK_UtilsTimeInfo` for local timestamp components.
- `sndk_c2_log_page_header` and `sndk_c2_log_subpage_header` for device manageability log parsing.
- `sndk_c2_cbs_data` for variable-length string entries.
- `sndk_fw_act_history_log_entry_c2` for a single C2 firmware activation history entry.
- `sndk_fw_act_history_log_format_c2` for the full C2 firmware activation history log, including 20 entries and a trailing GUID.

The firmware history structs are packed to match device binary log layout.

## Public API

The prototypes expose PCI/vendor ID lookup, device validation, commit action formatting, C2 log entry parsing, C2 log retrieval/validation, capability detection, serial-name formatting, time/snprint utilities, and telemetry option validation. These functions are consumed primarily by `sandisk-nvme.c`.

## Notable Risks

This header mixes many domains: device IDs, command capability flags, binary log schemas, and utility prototypes. That is pragmatic for a plugin but creates broad rebuild coupling. It includes many standard library and system headers directly, so any translation unit including it inherits a large include surface.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/sandisk/sandisk-utils.h -->