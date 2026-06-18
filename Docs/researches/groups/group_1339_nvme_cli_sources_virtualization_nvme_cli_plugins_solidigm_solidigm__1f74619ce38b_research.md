# Group Research: group_1339_nvme_cli_sources_virtualization_nvme_cli_plugins_solidigm_solidigm__1f74619ce38b

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/virtualization/nvme-cli`. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-latency-tracking.c -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-latency-tracking.c

Implements Solidigm `latency-tracking-log`, covering feature enable/disable/status and read/write latency log retrieval.

Key elements:
- Defines `struct latency_statistics` with revision fields, up to 1216 bucket counters, and optional average latency.
- Supports latency formats:
  - v3: fixed linear bucket ranges.
  - v4.0: 152 logarithmic-ish buckets with 3 base range bits.
  - v4.1+ default: 1216 buckets with 6 base range bits.
  - v4.8+: includes `average_latency`.
- Uses feature ID `0xe2` to get/set tracking enable state.
- Uses log IDs `0xc1` and `0xc2` for read/write latency statistics.
- Encodes log type into CDW10 LSP and Solidigm UUID index into CDW14.
- Output modes:
  - Normal table output with bucket start/end labels.
  - JSON root `latstats` with `type`, optional `average_latency`, and `values` array.
  - Binary raw dump for retrieved log data.
- CLI validation prevents simultaneous enable/disable and simultaneous read/write capture, validates log type `0..0xf`, and rejects `--type` without read/write retrieval.

Dependencies:
- `solidigm-util.c` for `sldgm_get_uuid_index`.
- nvme-cli/libnvme helpers: `parse_and_open`, `validate_output_format`, `nvme_get_features`, `nvme_set_features`, `libnvme_get_log`.

Notable behavior:
- If no enable/disable/read/write option is passed, the command reports current feature state.
- Binary status mode writes `putchar(enabled)`, which truncates the 64-bit feature value to one byte.
- Unsupported major revisions print a warning but still run post-parse JSON handling if JSON was initialized.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-latency-tracking.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-latency-tracking.h -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-latency-tracking.h

Small command header declaring:

- `solidigm_get_latency_tracking_log(int argc, char **argv, struct command *acmd, struct plugin *plugin)`

This exposes the latency-tracking command implementation for registration in `solidigm-nvme.c`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-latency-tracking.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-log-page-dir.c -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-log-page-dir.c

Implements Solidigm `log-page-directory`, which reports supported NVMe/OCP/Solidigm log pages by UUID index.

Key elements:
- Fetches `NVME_LOG_LID_SUPPORTED_LOG_PAGES` via `libnvme_get_log`.
- Builds `struct lid_dir` arrays mapping LID support flags to descriptions.
- Maintains separate directory mappings:
  - Standard NVMe LIDs below `0xc0`, using `nvme_log_to_string`.
  - Solidigm vendor LIDs such as `0xc1` read latency, `0xc2` write latency, `0xdd` marketing log, `0xf9` workload tracker.
  - OCP vendor LIDs such as OCP SMART, error recovery, firmware activation history, latency monitor, and telemetry string log.
- UUID logic:
  - UUID index 0 is always used for the initial standard supported-pages query.
  - If UUID list lookup is not supported, vendor-supported LIDs are assumed to be Solidigm at UUID index 0.
  - If UUIDs are supported, finds Solidigm and OCP UUID indexes and fetches per-index supported-pages data.
- Supports normal tabular output and JSON array output.

Dependencies:
- OCP helpers: `ocp_find_uuid_index`.
- Solidigm helper: `sldgm_find_uuid_index`.
- nvme-cli print/JSON helpers.

Notable behavior:
- Only UUID indexes up to `SOLIDIGM_MAX_UUID` (`2`) are displayed.
- Unsupported but known vendor LIDs retain descriptions only if the device reports them supported.
- Binary output is not handled; only normal and JSON are emitted.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-log-page-dir.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-log-page-dir.h -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-log-page-dir.h

Declares the Solidigm log-page-directory command:

- Forward declares `struct command` and `struct plugin`.
- Exports `solidigm_get_log_page_directory_log(...)`.

Used by `solidigm-nvme.c` for plugin command dispatch.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-log-page-dir.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-market-log.c -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-market-log.c

Implements Solidigm `market-log`, retrieving a marketing name log page.

Key elements:
- Uses vendor log ID `0xdd`.
- Allocates a fixed 512-byte `char log[MARKET_LOG_MAX_SIZE]`.
- Looks up Solidigm UUID index and encodes it into CDW14.
- Retrieves the log with `libnvme_get_log`.
- CLI option:
  - `--raw-binary` / `-b` dumps the 512-byte buffer with `d_raw`.
  - Default prints `Solidigm Marketing Name Log:` followed by the string.

Dependencies:
- `solidigm-util.c` for UUID-index lookup.
- nvme-cli/libnvme log setup and output helpers.

Notable behavior:
- Normal output assumes returned data is a printable C string; if the device does not NUL-terminate within 512 bytes, output can read past intended string boundaries through `printf("%s")`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-market-log.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-market-log.h -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-market-log.h

Declares:

- `sldgm_get_market_log(int argc, char **argv, struct command *acmd, struct plugin *plugin)`

This is the command entry used by Solidigm plugin registration.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-market-log.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-nvme.c -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-nvme.c

Provides Solidigm plugin command wrapper functions and includes the command table.

Key elements:
- Defines `CREATE_CMD` before including `solidigm-nvme.h`.
- Includes Solidigm command headers and selected OCP command headers.
- Most functions are thin wrappers around implementation functions:
  - `id_ctrl` delegates to `__id_ctrl(..., sldgm_id_ctrl)`.
  - SMART, internal log, garbage collection, latency tracking, telemetry, directory, market, temp stats, drive info, OCP version, workload tracker each call their Solidigm implementation.
  - Several commands redirect to OCP plugin implementations: SMART cloud, clear firmware history, clear PCIe correctable errors, firmware activation history.

Role:
- Central dispatch glue for Solidigm vendor-specific extension commands.
- Keeps plugin registration in the header macro system while implementation functions stay in separate modules.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-nvme.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-nvme.h -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-nvme.h

Defines the Solidigm nvme-cli plugin command table.

Key elements:
- Sets `CMD_INC_FILE plugins/solidigm/solidigm-nvme`.
- Defines `SOLIDIGM_PLUGIN_VERSION "1.22"`.
- Registers plugin name `solidigm` and description `Solidigm vendor specific extensions`.
- Command entries include:
  - `id-ctrl`
  - `smart-log-add`
  - `vs-smart-add-log`
  - `vs-internal-log`
  - `garbage-collect-log`
  - `market-log`
  - `latency-tracking-log`
  - `parse-telemetry-log`
  - OCP clear/history redirections
  - `log-page-directory`
  - `temp-stats`
  - `vs-drive-info`
  - `cloud-SSDplugin-version`
  - `workload-tracker`

Notable detail:
- The entry string `"clear-pcie-correctable-errors "` contains a trailing space, which may affect exact command name matching or help output.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-nvme.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-ocp-version.c -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-ocp-version.c

Implements `cloud-SSDplugin-version`.

Behavior:
- Parses an argument set with no options.
- On successful parse, prints fixed string `1.0`.
- Returns parser status.

Role:
- Reports the Solidigm plugin’s OCP extension version, separate from `SOLIDIGM_PLUGIN_VERSION`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-ocp-version.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-ocp-version.h -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-ocp-version.h

Declares:

- `sldgm_ocp_version(int argc, char **argv, struct command *acmd, struct plugin *plugin)`

Used by Solidigm plugin dispatch for `cloud-SSDplugin-version`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-ocp-version.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-smart.c -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-smart.c

Implements Solidigm additional SMART log retrieval for vendor log ID `0xca`.

Key elements:
- Defines packed 12-byte SMART item format with ID, normalized value, raw 6-byte field, and special overlays:
  - Wear-level min/max/avg.
  - Thermal throttle percentage/count.
  - Reference clock/PLL counters.
- `id_to_name` maps many vendor IDs to readable JSON/table names, with special handling for ID `0xc7` depending on whether IDs `0xe7` or `0xe8` exist.
- Normal output prints a table of ID, key name, normalized, and raw/special data.
- JSON output creates root key `Solidigm SMART log` and object `Device stats`.
- Binary output dumps the 512-byte SMART payload.
- Retrieves log via `libnvme_get_log` with Solidigm UUID index in CDW14.

Dependencies:
- `solidigm-util.c` for UUID-index lookup.
- nvme-cli JSON and raw dump helpers.

Notable behavior:
- CLI accepts `--namespace-id`, but the actual log retrieval uses `NVME_NSID_ALL`; the configured namespace is used only in displayed output.
- JSON helper uses `json_object_add_value_int` for `int48_to_long` values, which can truncate if the helper stores only signed int width.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-smart.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-smart.h -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-smart.h

Declares:

- `solidigm_get_additional_smart_log(int argc, char **argv, struct command *acmd, struct plugin *plugin)`

This exposes Solidigm vendor SMART log support to plugin registration.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-smart.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry.c -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry.c

Implements Solidigm telemetry log parsing command.

Key elements:
- Accepts either a device path or `--source-file` binary telemetry dump.
- CLI options:
  - `--host-generate` / `-g`, default `1`.
  - `--controller-init` / `-c`.
  - `--data-area` / `-d`, valid `1..4`.
  - `--config-file` / `-j` JSON parser config.
  - `--source-file` / `-s` binary log dump.
  - `--jq-filter` / `-q` key name in config containing a jq filter.
- Default data area:
  - Without explicit `--data-area`, uses DA3 if config file is supplied, otherwise DA1.
- Device mode:
  - Opens NVMe device.
  - Computes MDTS-style transfer exponent from `libnvme_get_telemetry_max`.
  - Fetches telemetry via `sldgm_dynamic_telemetry`.
- File mode:
  - Reads entire source file into a buffer and skips device open.
- Parses telemetry into `struct telemetry_log` and delegates to `solidigm_telemetry_log_data_areas_parse`.
- Emits JSON normally, or pipes JSON into external `jq -r '<filter>'` if requested and configured.

Notable behavior:
- Rejects device path when `--source-file` is used.
- `read_file2buffer` uses `ftell`/`malloc`/`fread` without checking short read beyond assigning actual length.
- jq command is built with `snprintf("jq -r '%s'", jq_filter_str)` and executed through `popen`; this treats config-provided filters as shell input.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry.h -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry.h

Declares:

- `solidigm_get_telemetry_log(int argc, char **argv, struct command *acmd, struct plugin *plugin)`

Used by the Solidigm plugin command wrapper for `parse-telemetry-log`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/cod.c -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/cod.c

Parses Solidigm telemetry COD/OEM data map objects.

Key elements:
- Defines `oemDataMapDesc[]` mapping OEM data field UIDs to descriptions such as media reads/writes, serial number, temperatures, latencies, wear, defects, PMIC values, etc.
- Expects COD signature `0x504D4443`.
- Packed COD structures:
  - `cod_header`
  - `cod_item`
  - `cod_map`
- `solidigm_telemetry_log_cod_parse`:
  - Looks up `telemetryHeader.reasonIdentifier.oemDataMapOffset` from existing parsed JSON.
  - Validates header and map bounds.
  - Checks big-endian signature.
  - Creates root object `cod`.
  - Iterates COD entries and decodes integer, float, string, 2-byte ASCII, and 4-byte ASCII fields.

Dependencies:
- Requires header parsing to have already populated reason identifier data.
- Uses `sldm_uint8_array_to_string` from telemetry header helpers.

Notable issue:
- The entry bounds check uses `item.DataFieldOffset + item.DataFieldOffset > tl->log_size`; this appears intended to include `DataFieldSizeInBytes`, so malformed offsets may not be guarded as precisely as intended.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/cod.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/cod.h -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/cod.h

Declares:

- Includes `telemetry-log.h`.
- Exports `solidigm_telemetry_log_cod_parse(struct telemetry_log *tl)`.

Used by `data-area.c` after telemetry header parsing.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/cod.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/config.c -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/config.c

Provides JSON configuration lookup helpers for telemetry parsing.

Key elements:
- Versioned structure lookup:
  - First tries exact major/minor.
  - Then wildcard minor `*`.
  - Then alternate wildcard minor `49374`.
  - Then wildcard major `*`.
  - Then alternate major `47837`.
- Public lookups:
  - `sldm_config_get_struct_by_key_version`
  - `solidigm_config_get_struct_by_token_version`
- NLOG helpers:
  - `solidigm_config_get_nlog_obj_name` resolves object token through `TELEMETRY_OBJECT_UIDS` and requires `UID_NLOG_` prefix.
  - `solidigm_config_get_nlog_formats` returns `NLOG_FORMATS`.
- Enum lookup:
  - Recursively searches structure definitions for a member with requested name and `enum == 1`.
  - Returns matching enum label by numeric value or `UNKNOWN_ENUM_VALUE`.

Role:
- Central adapter between firmware telemetry config JSON and generic binary parser.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/config.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/config.h -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/config.h

Header for telemetry JSON configuration helpers.

Key elements:
- Includes `stdbool.h` and `util/json.h`.
- Defines:
  - `STR_HEX32_SIZE`
  - `UNKNOWN_ENUM_VALUE`
- Declares versioned structure lookup, NLOG metadata lookup, NLOG format lookup, and enum label lookup functions.

Notable detail:
- Prototype names use mixed `sldm_` and `solidigm_` prefixes.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/config.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/data-area.c -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/data-area.c

Core Solidigm telemetry data-area and config-driven structure parser.

Key elements:
- `telemetry_log_get_value` extracts bitfields from telemetry log data into JSON integer values, supporting signed and unsigned fields up to 64 bits.
- `sldm_telemetry_structure_parse` recursively parses config-defined structures:
  - Requires `name`, `offsetBit`, `sizeBit`, and `arraySize`.
  - Supports arrays and multidimensional arrays.
  - Supports dynamic array size via `arraySizeIndicator`.
  - Handles nested `memberList` structures.
  - Detects signed types by `int`/`INT` prefix.
- Data-area offset calculation maps NVMe telemetry DA1-DA4 based on `dalb1..dalb4`.
- TOC parsing:
  - Reads data-area header and TOC entries.
  - Emits `tableOfContents` metadata and `telemetryObjects`.
  - Looks up object structure definitions by token/version.
  - Falls back to NLOG handling when object token maps to an NLOG object.
  - Adjusts for object headers with `hasTelemObjHdr`.
  - Detects object names containing side-trace variants and invokes side-trace parsing.
- `solidigm_telemetry_log_da1_check_ocp` detects OCP telemetry UUID in data area 1.
- `solidigm_telemetry_log_data_areas_parse` orchestrates:
  - OCP detection.
  - SKH/T signature detection.
  - Optional config metadata copy.
  - Header parse.
  - COD parse.
  - Standard TOC/object parsing when config exists.
  - SKH/T-specific parsing path when `skhT_offset` is present.

Dependencies:
- COD, header, NLOG, side-trace, SKH/T, config helpers.

Notable behavior:
- Without a config file, parsing is limited to telemetry header and COD.
- OCP logs skip standard parsing until DA3.
- Warnings are embedded as stderr messages, while invalid individual values may be represented as JSON string errors during structure parsing.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/data-area.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/data-area.h -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/data-area.h

Declares telemetry data-area parsing functions.

Key elements:
- Defines `NUM_BITS_IN_BYTE 8`.
- Declares:
  - `solidigm_telemetry_log_data_areas_parse`
  - `solidigm_telemetry_log_da1_check_ocp`
  - `sldm_telemetry_structure_parse`

Role:
- Shared parser interface used by telemetry command and specialized telemetry parsers.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/data-area.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/debug-info.c -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/debug-info.c

Parses SKH/T-style debug-info telemetry segments.

Key elements:
- Debug segment IDs:
  - UART log: `3`
  - Tracker info: `6`
  - Tracker buffer: `7`
  - Tracker context: `8`
- Requires config structures:
  - `DebugInfoBlkHeader_t`
  - `DebugInfoHeader_t`
  - `DebugInfoSegHeader_t`
- `sldm_debug_info_parse`:
  - Validates input pointers and bounds.
  - Parses top-level debug block header.
  - Iterates up to 255 core debug headers.
  - Validates each core by signature `0x54321234`.
  - Adds parsed core headers to `Cores`.
  - Parses up to 16 segment headers per core into `Segments`.
  - Dispatches segment payload:
    - UART log segments to `sldm_parse_cd_uart_log`.
    - Tracker segments to `sldm_tracker_parse`.

Dependencies:
- Config-driven structure parser.
- SKH/T version constants.
- Tracker and UART log parsers.

Notable behavior:
- Uses parsed JSON fields to determine sizes and IDs rather than static C structs.
- Stops parsing cores when signature does not match.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/debug-info.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/debug-info.h -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/debug-info.h

Declares:

- `sldm_debug_info_parse(struct telemetry_log *tl, uint32_t offset, uint32_t size, struct json_object *output)`

Includes telemetry and JSON types. Used by SKH/T and segment parsing paths.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/debug-info.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/header.c -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/header.c

Parses telemetry log header and reason-identifier fields.

Key elements:
- `sldm_uint8_array_to_string` converts fixed byte arrays to JSON strings:
  - Stops at NUL unless nonzero data follows.
  - Returns whether data was printable ASCII and cleanly terminated.
- Defines packed Solidigm reason identifier layouts:
  - v1.0
  - v1.1
  - v1.2+
- Defines OCP 2.5 reason identifier layout.
- Uses static assertions to match `nvme_telemetry_log.rsnident` size.
- `solidigm_telemetry_log_reason_id_parse`:
  - For OCP telemetry, parses OCP fields.
  - For Solidigm, parses version, reason code, drive status, and version-specific fields.
- `solidigm_telemetry_log_header_parse`:
  - Validates minimum log size.
  - Adds `telemetryHeader` JSON.
  - Emits log identifier, IEEE OUI bytes, DA last blocks, generation counters.
  - Adds parsed `reasonIdentifier`.

Dependencies:
- `telemetry-log.h` for shared state and warning macro.

Role:
- First-stage parser feeding COD and data-area parsing with header context.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/header.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/header.h -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/header.h

Declares telemetry header helpers:

- `sldm_uint8_array_to_string`
- `solidigm_telemetry_log_header_parse`

Includes `telemetry-log.h`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/header.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/meson.build -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/meson.build

Build-system fragment adding Solidigm telemetry parser sources to `plugin_sources`.

Included files:
- `cod.c`
- `header.c`
- `config.c`
- `data-area.c`
- `nlog.c`
- `tracker.c`
- `skht.c`
- `debug-info.c`
- `uart-log.c`
- `side-trace.c`

Role:
- Ensures specialized telemetry parsers are compiled as part of the nvme-cli plugin build.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/meson.build -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/nlog.c -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/nlog.c

Parses Solidigm NLOG circular event buffers.

Key elements:
- NLOG entry assumptions:
  - Header: 1 dword.
  - Timestamp: 2 dwords.
  - Up to 8 argument dwords.
  - Argument count in low nibble of header.
- Looks up event format strings by hex header key in `NLOG_FORMATS`.
- `nlog_get_events` walks the ring backward from a start offset, validates headers, extracts timestamp/header/argument arrays, and attaches matching format JSON.
- Tries multiple possible circular-buffer offsets and chooses the one with the fewest header mismatches.
- Emits warning if the best offset still has more than one mismatch.
- Output adds an `events` array.

Dependencies:
- Config helper for hex key size.
- Metadata object used for warning context.

Role:
- Converts raw telemetry NLOG objects into structured JSON event arrays.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/nlog.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/nlog.h -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/nlog.h

Declares:

- `solidigm_nlog_parse(const char *buffer, uint64_t bufer_size, struct json_object *formats, struct json_object *metadata, struct json_object *output)`

Note: parameter spelling is `bufer_size` in the header.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/nlog.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/side-trace.c -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/side-trace.c

Parses Solidigm side-trace telemetry objects.

Key elements:
- Side-trace block constants:
  - 256-byte block size.
  - 32-byte payload offset.
  - Empty token `0xffff`.
- Uses config structures:
  - `trimmedSideTraceBufferEntryHeader`
  - `sideTraceBufferEntry`
- Parses a temporary header object to extract major/minor revision, token ID, and payload size.
- Uses enum lookup from config to convert token ID to `tokenName`.
- Distinguishes:
  - Trimmed entries when major revision >= 128.
  - Full entries otherwise.
- For trimmed entries, optionally appends raw payload bytes as `payload.rawDataArray`.
- `sldm_parse_side_trace`:
  - Validates overall object bounds.
  - Adds side-trace metadata.
  - Parses entries in 256-byte increments.
  - Replaces output field `fwSideTrace` when entries exist.

Notable behavior:
- Stops parsing when token lookup returns `UNKNOWN_ENUM_VALUE`.
- Per-entry bounds check compares `offset_bytes + SIDETRACE_BLOCK_SIZE` to total log size, while the actual pointer also includes `file_offset`; the outer object bound check reduces risk but partial trailing blocks are not deeply parsed.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/side-trace.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/side-trace.h -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/side-trace.h

Declares:

- `sldm_parse_side_trace(const struct telemetry_log *tl, uint64_t file_offset, uint32_t size_bytes, struct json_object *output, struct json_object *metadata)`

Used by `data-area.c` when parsed telemetry object metadata names indicate a side-trace object.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/side-trace.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/skht.c -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/skht.c

Implements SKH/T telemetry detection and parsing.

Key elements:
- Detects `skhT` signature `0x54686b73`.
- Non-OCP logs: checks start of DA2.
- OCP logs: checks DA3 after segment headers.
- `sldm_telemetry_skhT_parse`:
  - Requires config structures `HynixHeader` and `BuildInfo`.
  - Parses both directly into root JSON using SKH/T version constants.
- `sldm_telemetry_sktT_segment_parse`:
  - Parses `SegmentHeader` at DA3.
  - Converts descriptor byte-array descriptions/type names to strings.
  - Dispatches segments by description prefix:
    - `TRACKER_DATA` -> `sldm_tracker_parse`
    - `UART_LOG_INFO` -> raw string from log
    - `DEBUG_INFO` -> `sldm_debug_info_parse`

Dependencies:
- Config-driven parser.
- Tracker, UART, and debug-info parsers.

Notable behavior:
- Uses SKH/T wildcard version constants `47837` and `49374`, matching config fallback behavior.
- Segment offsets are based on `NVME_LOG_TELEM_BLOCK_SIZE + offset`, not the DA3 absolute offset variable, which is intentional only if segment offsets are relative to the post-header telemetry block convention.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/skht.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/skht.h -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/skht.h

Declares SKH/T telemetry helpers.

Key elements:
- Defines:
  - `SKT_VER_MAJOR 47837`
  - `SKT_VER_MINOR 49374`
- Declares:
  - `sldm_telemetry_check_for_skhT`
  - `sldm_telemetry_sktT_segment_parse`
  - `sldm_telemetry_skhT_parse`
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/skht.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/telemetry-log.h -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/telemetry-log.h

Shared telemetry parser definitions.

Key elements:
- Defines C `static_assert` compatibility.
- Defines `SOLIDIGM_LOG_WARNING` as `fprintf(stderr, ...)`.
- Defines `MEMBER_SIZE`.
- Defines `struct telemetry_log`:
  - Raw `nvme_telemetry_log *log`
  - `log_size`
  - JSON root object
  - JSON configuration object
  - OCP flag
  - SKH/T offset

Role:
- Common state container passed through all Solidigm telemetry subparsers.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/telemetry-log.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/tracker.c -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/tracker.c

Parses SKH/T tracker data chunks from telemetry.

Key elements:
- Tracker chunk size is 4096 bytes.
- Expects AB list signature `0xab15ab15`.
- Required config structures:
  - `ablist_context_t`
  - `ablist_entry_t`
  - `tracker_entry_t`
- Tracker metadata lookup:
  - Reads `Tracker.TrackerEntry.<hash>` from config.
  - Uses `idName`, `file`, `line`, and `descArgN` fields when available.
- `parse_tracker_chunk_json`:
  - Parses chunk context.
  - Validates signature.
  - Walks linked entries via `next_entry_index`.
  - Parses entry header and tracker entry data dynamically.
  - Emits fields including name/file/line/time/arm_id/hash/level/group/arg_count.
  - Converts level numbers to `DEBUG`, `INFO`, `ERROR`, `CRITICAL`, or `UNKNOWN`.
  - Adds arguments object, using configured argument descriptions when present.
- `sldm_tracker_parse`:
  - Adds offset/size/chunks.
  - Parses all full 4096-byte chunks.
  - Adds `entries` array.

Notable behavior:
- Partial chunk remainders are ignored because chunk count is `size / 4096`.
- Unknown tracker hashes are skipped.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/tracker.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/tracker.h -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/tracker.h

Declares:

- `sldm_tracker_parse(struct telemetry_log *tl, uint32_t offset, uint32_t size, struct json_object *tracker_obj)`

Used by SKH/T segment and debug-info parsing.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/tracker.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/uart-log.c -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/uart-log.c

Parses controller-debug UART log telemetry entries.

Key elements:
- Requires config structures:
  - `UartLogBufHeader`
  - `UartLogBufBody`
- Each UART entry is treated as 192 bytes.
- `parse_uart_entry`:
  - Gets header/body definitions from config.
  - Parses header at entry bit offset.
  - Parses body immediately after header size from config.
  - Adds parsed entry to UART array.
- `sldm_parse_cd_uart_log`:
  - Validates offset/size.
  - Truncates size if it exceeds log size.
  - Computes number of entries by `size / 192`.
  - Adds `uart_log` array to output.

Notable behavior:
- Entries that fail to parse are skipped without aborting the whole UART log.
- Requires configuration; without it, parsing reports warnings and produces no detailed entries.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/uart-log.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/uart-log.h -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/uart-log.h

Declares:

- `sldm_parse_cd_uart_log(struct telemetry_log *tl, uint32_t offset, uint32_t size, struct json_object *output)`

Used by debug-info and SKH/T segment parsers.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/uart-log.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-temp-stats.c -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-temp-stats.c

Implements Solidigm `temp-stats` log retrieval.

Key elements:
- Primary log ID: `0xd5`.
- Legacy fallback log ID: `0xc5`.
- `struct temp_stats` contains current, last/lifetime overtemp flags, highest/lowest temperature, max/min operating temp, and estimated offset.
- Retrieves primary log with Solidigm UUID index in CDW14.
- On positive NVMe error, retries legacy log ID.
- Checks legacy buffer tail GUID to avoid treating OCP Unsupported Requirements log as Solidigm temp stats.
- CLI option:
  - `--raw-binary` / `-b` dumps raw `struct temp_stats`.
  - Default prints named values.

Dependencies:
- `sldgm_get_uuid_index`.
- nvme-cli print/raw helpers.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-temp-stats.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-temp-stats.h -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-temp-stats.h

Declares:

- `sldgm_get_temp_stats_log(int argc, char **argv, struct command *acmd, struct plugin *plugin)`

Used by Solidigm command registration.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-temp-stats.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-util.c -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-util.c

Shared Solidigm utility functions.

Key elements:
- Defines Solidigm UUID byte sequence:
  - `96 19 58 6e c1 1b 43 ad aa aa 65 41 87 f6 bb b2`
- `sldgm_find_uuid_index`:
  - Uses `libnvme_find_uuid`.
  - Sets index to found value when positive, otherwise `0` and returns `-errno`.
- `sldgm_get_uuid_index`:
  - Calls `nvme_identify_uuid_list`.
  - Delegates to `sldgm_find_uuid_index`.
- `sldgm_dynamic_telemetry`:
  - Calls `libnvme_get_telemetry_log`.
  - Starts with transfer size `(1 << mtds) * NVME_LOG_PAGE_PDU_SIZE`.
  - On `-EPERM`, halves transfer size and retries down to one PDU.
  - Clears `create` after the first attempt.

Role:
- Central UUID and telemetry fetch compatibility helper used across Solidigm command modules.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-util.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-util.h -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-util.h

Declares Solidigm helpers:

- `sldgm_find_uuid_index`
- `sldgm_get_uuid_index`
- `sldgm_dynamic_telemetry`

Includes `nvme.h` for libnvme and NVMe telemetry types.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-util.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-workload-tracker.c -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-workload-tracker.c

Implements Solidigm real-time workload tracker sampling.

Key elements:
- Uses log ID `0xf9` and feature ID `0xf1`.
- Supports sample intervals from `default` through `1h`.
- Supports tracker types:
  - Base
  - CmdQ
  - Pattern
  - RandSeq
  - Throttle
  - Power
  - Defrag
- Defines per-type field layouts with byte sizes, names, and descriptions.
- `union WorkloadLogEnable` maps set-feature dword bitfields for enable, trigger configuration, sample time, content group, stop count, and event dump.
- `struct workloadLog` defines the full log page, including up to 126 32-byte entries.
- Runtime behavior:
  - Optional enable/disable.
  - Optional trigger field/threshold configuration using feature `0xf5`.
  - Polls log page and prints only entries newer than previous poll.
  - Can reconstruct wall-clock timestamps by temporarily enabling tracker to calibrate SSD timestamp.
  - Sleeps according to sample period times flush frequency until runtime expires or trigger fires.
- CLI options include UUID index, enable/disable, sample time, type, run time, flush frequency, wall-clock output, trigger field/threshold, delta trigger, and latency trigger.

Notable behavior:
- Default `run_time_s` is zero, so without explicit runtime the main loop is skipped and one final retrieval is attempted.
- Field extraction reads unaligned 16/32-bit values directly from byte arrays and does not endian-convert entry fields.
- Helper string builders use `strcat` into fixed local buffers sized for current option sets.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-workload-tracker.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-workload-tracker.h -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-workload-tracker.h

Declares:

- `sldgm_get_workload_tracker(int argc, char **argv, struct command *acmd, struct plugin *plugin)`

Used by Solidigm plugin registration for `workload-tracker`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-workload-tracker.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ssstc/ssstc-nvme.c -->
# File Research: sources/virtualization/nvme-cli/plugins/ssstc/ssstc-nvme.c

Implements SSSTC vendor SMART log command.

Key elements:
- Defines packed SMART item format with key, normalized value, raw six-byte payload, and wear-level overlay.
- Defines `struct nvme_additional_smart_log` with SSSTC-specific counters for program/erase failures, wear leveling, E2E, CRC, NAND/host writes, reallocations, uncorrectables, ECC, GC, DRAM/SRAM UECC, RAID recovery, inflight commands, die failures, read disturb, retention, etc.
- Normal output prints a detailed textual table.
- JSON output builds `SSSTC Smart log` and `Device stats`.
- Binary output dumps the raw structure.
- Command handler:
  - Parses namespace, raw-binary, and JSON flags.
  - Retrieves log `0xca` with `nvme_get_log_simple`.
  - Dispatches output formatting.

Notable behavior:
- Namespace option affects displayed namespace but not the log retrieval call.
- The file registers command implementation through included `ssstc-nvme.h`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ssstc/ssstc-nvme.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ssstc/ssstc-nvme.h -->
# File Research: sources/virtualization/nvme-cli/plugins/ssstc/ssstc-nvme.h

Defines SSSTC plugin registration.

Key elements:
- Plugin name `ssstc`.
- Description `SSSTC vendor specific extensions`.
- Version uses `NVME_VERSION`.
- Registers one command:
  - `smart-log-add` -> `ssstc_get_add_smart_log`

Uses nvme-cli command macro include pattern.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ssstc/ssstc-nvme.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/toshiba/toshiba-nvme.c -->
# File Research: sources/virtualization/nvme-cli/plugins/toshiba/toshiba-nvme.c

Implements Toshiba NVMe vendor commands.

Key elements:
- Vendor SCT admin passthrough opcodes:
  - Status/command transfer opcode `0xe0`
  - Data transfer opcode `0xe1`
- Device support:
  - Reads SCT status.
  - Validates status version.
  - Checks internal device code against supported masks.
- Internal log transfer:
  - Sends command transfer with action code `0xfffb`.
  - Supports current and saved log function codes.
  - Reads log header to determine area last pages.
  - Transfers data in 32-sector pages, up to 128 pages per command.
  - Writes binary output file or dumps hex pages to stdout.
  - Shows progress bar.
- Vendor log command:
  - Supports log pages `0xc0` and `0xca`.
  - Can output to file or display.
  - `0xc0` is decoded as a vendor log-page directory.
- Clear PCIe correctable errors:
  - Uses set-feature feature ID `0xca`, namespace all, value `1`.
- Command handlers:
  - `vendor_log`
  - `internal_log`
  - `clear_correctable_errors`

Notable behavior:
- Some declared static const command dword variables without initializers rely on zero initialization.
- Uses pointer arithmetic on `void *` buffers, which is a GNU C extension.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/toshiba/toshiba-nvme.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/toshiba/toshiba-nvme.h -->
# File Research: sources/virtualization/nvme-cli/plugins/toshiba/toshiba-nvme.h

Defines Toshiba plugin registration.

Commands:
- `vs-smart-add-log` -> `vendor_log`
- `vs-internal-log` -> `internal_log`
- `clear-pcie-correctable-errors` -> `clear_correctable_errors`

Plugin name is `toshiba`, description `Toshiba NVME plugin`, version `NVME_VERSION`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/toshiba/toshiba-nvme.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/transcend/transcend-nvme.c -->
# File Research: sources/virtualization/nvme-cli/plugins/transcend/transcend-nvme.c

Implements Transcend vendor commands.

Commands:
- `getHealthValue`
  - Reads standard SMART log.
  - Computes health as `100 - percent_used`.
  - Prints `0%` if percent used is outside expected range.
- `getBadblock`
  - Executes admin passthrough opcode `0xc2`.
  - Uses CDW10 `0x400`, CDW12 `0x5a`.
  - Reads one byte and prints bad block count.

Dependencies:
- Standard nvme-cli parse/open and libnvme passthrough helpers.

Notable behavior:
- `percent_used` is stored in an int after reading from an unsigned SMART field; the `< 0` check is redundant.
- Device-open failure prints `Device not found` and returns `-1`, rather than propagating the parse/open error code.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/transcend/transcend-nvme.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/transcend/transcend-nvme.h -->
# File Research: sources/virtualization/nvme-cli/plugins/transcend/transcend-nvme.h

Defines Transcend plugin registration.

Commands:
- `healthvalue` -> `getHealthValue`
- `badblock` -> `getBadblock`

Plugin name is `transcend`, description `Transcend vendor specific extensions`, version `NVME_VERSION`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/transcend/transcend-nvme.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/virtium/virtium-nvme.c -->
# File Research: sources/virtualization/nvme-cli/plugins/virtium/virtium-nvme.c

Implements Virtium vendor commands for vtView-compatible SMART logging and detailed identify display.

Key elements:
- vtView log structures:
  - Session header includes path, test name, timestamp, raw identify controller, and firmware slot log.
  - SMART entry includes path, timestamp, namespace identify, controller identify, and SMART log.
- File logging:
  - Auto-generates `./vtView-Smart-log-YYYY-MM-DD.txt` when no output file is supplied.
  - Header is serialized as a semicolon-delimited text record with JSON-like session/device data and raw identify/firmware logs hex-encoded.
  - SMART entries are serialized as semicolon-delimited records with capacity, warning, temperature, spare, percentage used, 128-bit counters, thermal data, and sensors.
  - `save-smart-to-vtview-log` loops for configured hours and sleeps for configured frequency.
- Identify display:
  - `show-identify` reads controller identify and prints a large JSON-like/detail report.
  - Includes field descriptions for many NVMe controller capabilities.
  - Dumps power state descriptors and vendor-specific identify region.
- Helpers:
  - Hex conversion with optional byte reversal.
  - Fixed-space string trimming.
  - Locale forced to `C` during numeric formatting.

Notable behavior:
- Output is hand-built with many `printf`, `strcpy`, and `strcat` operations rather than using the JSON library; it is JSON-like in places but not uniformly strict JSON.
- `vt_update_vtview_log_header` length checks use `strlen(path) > sizeof(header.path)`, allowing exactly-256-byte strings before `strcpy`, which would overflow by one byte due to NUL terminator.
- The SMART log buffer size is fixed at 4096 bytes for formatted text.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/virtium/virtium-nvme.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/virtium/virtium-nvme.h -->
# File Research: sources/virtualization/nvme-cli/plugins/virtium/virtium-nvme.h

Defines Virtium plugin registration.

Commands:
- `save-smart-to-vtview-log` -> `vt_save_smart_to_vtview_log`
- `show-identify` -> `vt_show_identify`

Plugin name is `virtium`, description `Virtium vendor specific extensions`, version `NVME_VERSION`.

Notable detail:
- Help text mentions Virtium vtView and contains a non-ASCII apostrophe in `Virtium’s`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/virtium/virtium-nvme.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/wdc/wdc-nvme-cmds.h -->
# File Research: sources/virtualization/nvme-cli/plugins/wdc/wdc-nvme-cmds.h

Declares wrapper/proxy functions for WDC command implementations.

Command prototypes include:
- Cloud SSD plugin/version commands.
- Internal firmware log, NAND stats, SMART additional log.
- Clear PCIe correctable errors.
- Drive status, clear assert dump, drive resize, namespace resize.
- Firmware activation history get/clear.
- Telemetry controller option and reason identifier.
- Log page directory and drive info.
- PCIe stats, latency monitor, OCP logs, cloud log, hardware revision, device WAF, temperature stats, customer unique SMART log.

Helper prototypes:
- `run_wdc_nvme_check_supported_log_page`
- `run_wdc_get_fw_cust_id`
- `run_wdc_get_drive_capabilities`

Role:
- Header-only interface surface for WDC plugin command wrappers, not implementation.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/wdc/wdc-nvme-cmds.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/wdc/wdc-nvme.h -->
# File Research: sources/virtualization/nvme-cli/plugins/wdc/wdc-nvme.h

Defines WDC plugin registration.

Key elements:
- Plugin version `2.15.0`.
- Plugin name `wdc`, description `Western Digital vendor specific extensions`.
- Registers a broad command set for diagnostics, logs, purge, identify, internal logs, SMART, clear operations, telemetry, log-page directory, resize, capabilities, OCP/vendor logs, latency monitor, temperature stats, WAF, and customer unique SMART log.

Role:
- Command-table macro header; implementations are elsewhere.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/wdc/wdc-nvme.h -->