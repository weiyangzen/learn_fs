# Group Research: group_1334_nvme_cli_sources_virtualization_nvme_cli_plugins_innogrit_innogrit__ea7185ccfd1b

Scope: `Docs/research_subset_a.md` includes `sources/virtualization/nvme-cli`. This grouped report covers vendor/plugin sources under `nvme-cli/plugins` for Innogrit, Inspur, Intel, Live Migration, MangoBoost, Memblaze, and plugin Meson wiring.

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/innogrit/innogrit-nvme.c -->
# File Research: sources/virtualization/nvme-cli/plugins/innogrit/innogrit-nvme.c

This file implements the Innogrit nvme-cli plugin commands registered in `innogrit-nvme.h`: `get-eventlog` and `get-cdump`.

Main behavior:
- Provides `nvme_vucmd()` as a generic Innogrit vendor admin passthrough helper. It sets the vendor signature `IGVSC_SIG` in `cdw2`, sets namespace to all namespaces, uses `data_len / 4` in `cdw10`, and sends the command through `libnvme_exec_admin_passthru()`.
- Provides `getlogpage()` as a wrapper around `nvme_init_get_log()` and `libnvme_get_log()`, adding the log-specific `LSP` field into `cdw10`.
- Detects vendor command style with `getvsctype()`, trying log page `0xe1` first and falling back to vendor opcode `0xfe`; a `drvinfo_t.signature == 0x5A` indicates type 1 handling.
- `getvsc_eventlog()` retrieves event logs via vendor-specific commands. It handles two command layouts depending on `getvsctype()`, validates `EVLOG_SIG`, tolerates up to 16 invalid chunks, writes 4 KiB chunks to a file, and stops when the tail marker `0xffffffff00000000` is observed.
- `getlogpage_eventlog()` retrieves event logs via log page `0xcb` with LSP selectors. It probes support with selector `0x01`, retrieves total-size metadata with selector `0x02`, then pulls data with selector `0x00`.
- `innogrit_geteventlog()` opens the device, creates a timestamped `eventlog_MMDD-HHMMSS.eraw` file in the current working directory, tries the log-page path first, falls back to VSC retrieval on `IG_UNSUPPORT`, and chmods the output to `0666`.
- `innogrit_vsc_getcdump()` retrieves controller dump data. It first attempts Innogrit VSC dump metadata and supports multiple cdump packs with firmware-version-labeled filenames. If VSC metadata is unavailable, it falls back to standard log page `0x07`. It writes `cdumpstart` and `cdumpend` markers around raw dump payloads.

Important data dependencies:
- Uses constants and structures from `typedef.h`: `IGVSC_SIG`, `SRB_SIGNATURE`, `EVLOG_SIG`, `drvinfo_t`, `evlg_flush_hdr`, and `cdumpinfo`.
- Depends on nvme-cli helpers: `parse_and_open()`, cleanup attributes, `nvme_get_nsid_log()`, and libnvme passthrough helpers.

Notable quirks:
- `getlogpage()` accepts a `result` pointer but does not pass it to `libnvme_get_log()` or fill it. `getlogpage_eventlog()` expects `result` to contain total pages after selector `0x02`, so that path appears ineffective unless libnvme mutates state outside the visible argument.
- In `innogrit_vsc_getcdump()`, after advancing to the next VSC pack, it recomputes `fname` but reopens `filename` without updating it from `fname`; this can append later packs to the previous path.
- File creation uses `sprintf()` into fixed buffers and `fopen(..., "a+")`, so repeated timestamps or long current directories may behave poorly.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/innogrit/innogrit-nvme.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/innogrit/innogrit-nvme.h -->
# File Research: sources/virtualization/nvme-cli/plugins/innogrit/innogrit-nvme.h

This header declares the Innogrit plugin command table for nvme-cli’s command-generation system.

Registered plugin:
- Name: `innogrit`
- Description: `innogrit vendor specific extensions`
- Version: `NVME_VERSION`

Registered commands:
- `get-eventlog`: calls `innogrit_geteventlog`
- `get-cdump`: calls `innogrit_vsc_getcdump`

The file follows the usual nvme-cli plugin pattern:
- Sets `CMD_INC_FILE` to `plugins/innogrit/innogrit-nvme`.
- Uses a multiple-read include guard compatible with command-table generation.
- Includes `cmd.h` before `PLUGIN(...)`.
- Includes `define_cmd.h` at the end.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/innogrit/innogrit-nvme.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/innogrit/typedef.h -->
# File Research: sources/virtualization/nvme-cli/plugins/innogrit/typedef.h

This header contains Innogrit-specific constants and binary layouts used by `innogrit-nvme.c`.

Constants:
- Return codes: `IG_SUCCESS`, `IG_UNSUPPORT`, `IG_ERROR`.
- Vendor opcodes: `NVME_VSC_GET_EVENT_LOG`, `NVME_VSC_GET`, `NVME_VSC_TYPE1_GET`.
- Function selector: `VSC_FN_GET_CDUMP`.
- Signatures: `IGVSC_SIG`, `EVLOG_SIG`, `SRB_SIGNATURE`.
- Utility constants: terminal clear-line escape `XCLEAN_LINE`, `SIZE_MB`.

Structures:
- `evlg_flush_hdr`: event-log chunk header with signature, firmware version/type, project, trace count, CRC, and reserved words.
- `eventlog`: simple event entry with millisecond timestamp and seven parameters.
- `drvinfo_t`: 512-byte-ish drive-info structure used for VSC-type detection; includes signature, SoC/NAND/DDR/firmware/build metadata, clocks, NAND geometry, SPI/ROM info, and reserved padding.
- `cdump_pack`: cdump pack length and 8-byte firmware version.
- `cdumpinfo`: cdump metadata signature, pack count, and up to 32 `cdump_pack` records.

Role in the subsystem:
- This is not a generic typedef header; it is the protocol contract for Innogrit vendor admin commands and log payload parsing.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/innogrit/typedef.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/inspur/inspur-nvme.c -->
# File Research: sources/virtualization/nvme-cli/plugins/inspur/inspur-nvme.c

This file implements the single Inspur plugin command `nvme-vendor-log`.

Main behavior:
- `nvme_get_vendor_log()` opens the target device, allocates a 4 KiB stack buffer, retrieves vendor log page `VENDOR_SMART_LOG_PAGE` (`0xc0`) with `nvme_get_log_simple()`, and prints parsed output.
- `show_r1_vendor_log()` formats a packed `r1_cli_vendor_log_t` structure from `inspur-utils.h`. It prints:
  - Device health state.
  - Commit ID and MCU telemetry.
  - Power, voltage, current, temperature, capacitor transition timing, capacitor health.
  - Warning/current and warning-history bitfields with named bit output.
  - NAND bytes written per partition.
  - Per-partition I/O/protection/DMA/LBA error counters.
  - PCIe reset/link/error counters.
  - NAND controller counters for read/program/erase, rebuild, retry, and bad-block categories.
  - Temperature throttling counters.
  - Wear-leveling counters.
  - End-to-end check counters.
- `show_r1_media_err_log()` prints up to 10 read-error LBAs for each of four media groups.

Data handling:
- Uses explicit little-endian conversion through `le32_to_cpu()` and `le64_to_cpu()` for most numeric fields.
- Interprets temperature-like fields as Kelvin and prints Celsius by subtracting 273.
- Uses `PRIu64` for 64-bit counters.

Notable quirks:
- `show_r1_vendor_log()` prints some final counters with index `i` after loops, leaving `i == 4`; the prefix is cosmetic but misleading.
- The command always fetches `sizeof(r1_cli_vendor_log_t)` into a 4 KiB local buffer; this assumes the packed layout remains within 4 KiB.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/inspur/inspur-nvme.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/inspur/inspur-nvme.h -->
# File Research: sources/virtualization/nvme-cli/plugins/inspur/inspur-nvme.h

This header registers the Inspur nvme-cli plugin.

Registered plugin:
- Name: `inspur`
- Description: `Inspur vendor specific extensions`
- Version: `NVME_VERSION`

Registered command:
- `nvme-vendor-log`: calls `nvme_get_vendor_log` and retrieves/displays the Inspur vendor log.

It uses the standard nvme-cli plugin macro pattern with `CMD_INC_FILE`, `PLUGIN`, `COMMAND_LIST`, `ENTRY`, and final `define_cmd.h` inclusion.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/inspur/inspur-nvme.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/inspur/inspur-utils.h -->
# File Research: sources/virtualization/nvme-cli/plugins/inspur/inspur-utils.h

This header defines the packed Inspur vendor log payload consumed by `inspur-nvme.c`.

Constants:
- Byte-size helpers from 128 bytes through 64 KiB.
- `VENDOR_SMART_LOG_PAGE = 0xc0`.

Packed structures:
- `r1_cap_transtime_t`: two 16-bit capacitor transition time fields inside a 32-bit word.
- `vendor_warning_str`: a 64-bit-style warning bit layout represented as bitfields across rebuild, self-test, internal, capacitance, I/O, firmware, spare, lifetime, temperature, and MCU-disable indicators.
- `r1_vendor_log_nandctl_count_t`: NAND controller read/program/erase counters, rebuild/retry counters, and bad-block counters.
- `r1_wearlvl_vendor_log_count_t`: wear-leveling and GC counters.
- `vendor_media_err_t`: ten LBA error entries.
- `r1_vendor_log_io_err_t`: protection, DMA, read/write fail, and LBA error counters.
- `r1_cli_vendor_log_t`: the full packed vendor-log payload, combining power/temperature/capacitor status, warning unions, PCIe counters, NAND/wear-leveling sections, E2E counters, and media-error arrays.

Role:
- This file is the binary ABI definition for Inspur log page `0xc0`. It is tightly coupled to fixed device firmware layout and is not independently executable.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/inspur/inspur-utils.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/intel/intel-nvme.c -->
# File Research: sources/virtualization/nvme-cli/plugins/intel/intel-nvme.c

This file implements Intel nvme-cli plugin commands for identify-controller vendor fields, SMART/temperature/marketing logs, latency statistics, internal firmware logs, and latency feature controls.

Command families:
- `id_ctrl()`: delegates to nvme-cli’s `__id_ctrl()` with Intel vendor-specific field decoding.
- `get_additional_smart_log()`: reads Intel additional SMART log page `0xca`.
- `get_market_log()`: reads marketing-name log page `0xdd`.
- `get_temp_stats_log()`: reads temperature statistics log page `0xc5`.
- `get_lat_stats_log()`: reads read/write latency statistics log pages `0xc1`/`0xc2`.
- `get_internal_log()`: exports Intel internal firmware logs via vendor opcode `0xd2`.
- `enable_lat_stats_tracking()`: gets/sets feature `0xe2`.
- `set_lat_stats_thresholds()`: sets Optane latency bucket thresholds via feature `0xf7`.

Important structures:
- `nvme_additional_smart_log_item` and `nvme_additional_smart_log`: Intel additional SMART attributes with normalized and 48-bit raw values.
- `nvme_vu_id_ctrl_field`: Intel identify-controller vendor-specific area fields such as subsystem status, health, bootloader, world-wide identifier, and MIC versions.
- `intel_temp_stats`: temperature statistics fields.
- `intel_lat_stats` and `optane_lat_stats`: NAND and Optane latency-stat layouts.
- Internal log structures: `intel_vu_log`, `intel_vu_nlog`, `intel_assert_dump`, `intel_event_dump`, `intel_event_header`, and command selector `intel_cd_log`.

Output support:
- Additional SMART supports normal, raw binary, and JSON output.
- Latency statistics support normal, raw binary, and JSON output.
- Identify-controller vendor fields support normal output and JSON through the root object passed by `__id_ctrl()`.

Latency-statistics logic:
- Reads the longest latency log first because Optane clears stats when the latency log is pulled.
- Interprets media version from the first four bytes.
- Supports NAND major revisions 3 and 4 with linear or logarithmic bucket ranges.
- Supports Optane major version 1000 minor 0 by querying bucket thresholds from feature `0xf7`.
- Uses helper formatting for microseconds/milliseconds/seconds and infinity bucket bounds.

Internal firmware log logic:
- Builds default output filenames from log type and controller serial number: `Nlog_<sn>.bin`, `EventLog_<sn>.bin`, or `AssertLog_<sn>.bin`.
- Reads a header with opcode `0xd2`, then handles old firmware formats separately.
- Supports log type 0 nlog, 1 event log, and 2 assert log.
- Can select all cores/nlogs or specific region/nlog.
- Writes binary log content to the output file and optionally prints verbose nlog metadata.

Notable quirks:
- `OPTANE_V1000_BUCKET_LEN` is defined twice with the same value.
- JSON support for Intel latency revision 4 handles minor versions 0-5, while text output accepts 0-6.
- Several internal log sizes and offsets are handled in dwords, while `data_len` is bytes; the code is careful in places but the mixture makes this command sensitive to off-by-four errors.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/intel/intel-nvme.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/intel/intel-nvme.h -->
# File Research: sources/virtualization/nvme-cli/plugins/intel/intel-nvme.h

This header registers the Intel nvme-cli plugin.

Registered plugin:
- Name: `intel`
- Description: `Intel vendor specific extensions`
- Version: `NVME_VERSION`

Registered commands:
- `id-ctrl`
- `internal-log`
- `lat-stats`
- `set-bucket-thresholds`
- `lat-stats-tracking`
- `market-name`
- `smart-log-add`
- `temp-stats`

Each command maps to a static implementation in `intel-nvme.c`. The header follows the standard nvme-cli generated-command include pattern.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/intel/intel-nvme.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/lm/lm-nvme.c -->
# File Research: sources/virtualization/nvme-cli/plugins/lm/lm-nvme.c

This file implements the NVMe Live Migration plugin command set.

Registered command implementations:
- `lm_create_cdq()`: creates a Controller Data Queue.
- `lm_delete_cdq()`: deletes a Controller Data Queue.
- `lm_track_send()`: sends Track Send management commands.
- `lm_migration_send()`: sends migration management data.
- `lm_migration_recv()`: receives migration/controller state data.
- `lm_set_cdq()`: sets Controller Data Queue feature `0x21`.
- `lm_get_cdq()`: gets Controller Data Queue feature `0x21`.

Core behavior:
- Uses libnvme initialization helpers such as `nvme_init_lm_cdq_create()`, `nvme_init_lm_cdq_delete()`, `nvme_init_lm_track_send()`, `nvme_init_lm_migration_send()`, and `nvme_init_lm_migration_recv()`.
- Uses `libnvme_exec_admin_passthru()` for live-migration admin commands.
- Uses `nvme_get_features()` and `nvme_set_features()` for CDQ feature operations.
- Uses hugepage allocation for data buffers that are passed to the controller.

Important validation:
- `lm_create_cdq()` requires explicit `--consent` because the code notes CDQs cannot be safely mapped to user space and may cause device writes to invalid memory.
- `lm_track_send()` currently supports only `NVME_LM_SEL_LOG_USER_DATA_CHANGES`, and provides `--start`/`--stop` convenience flags.
- `lm_migration_send()` checks that suspend/resume options do not include controller-state-only fields, and that `SET_CONTROLLER_STATE` has an input file and does not include suspend-only options.
- `lm_migration_recv()` refuses to parse non-zero-offset output unless binary output is requested.

Output handling:
- `lm_migration_recv()` can write raw controller-state data to an output file, or delegate decoded display to `lm_show_controller_state_data()`.
- `lm_get_cdq()` delegates display to `lm_show_controller_data_queue()`.

Notable quirks:
- `lm_create_cdq()` checks `if (!consent)` instead of `if (!cfg.consent)`, so it tests the non-null description string rather than the parsed flag. This appears to bypass the intended consent gate.
- In `lm_migration_recv()`, `fopen()` result is compared with `< 0`; for `FILE *`, the correct failure check is `fd == NULL`.
- The file relies on live-migration definitions from libnvme/nvme headers, so it is a thin CLI/admin-command wrapper rather than a protocol implementation from scratch.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/lm/lm-nvme.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/lm/lm-nvme.h -->
# File Research: sources/virtualization/nvme-cli/plugins/lm/lm-nvme.h

This header registers the `lm` nvme-cli plugin for NVMe Live Migration extensions.

Registered plugin:
- Name: `lm`
- Description: `Live Migration NVMe extensions`
- Version: `NVME_VERSION`

Registered commands:
- `create-cdq`
- `delete-cdq`
- `track-send`
- `migration-send`
- `migration-recv`
- `set-cdq`
- `get-cdq`

The command table maps each CLI verb to the corresponding static implementation in `lm-nvme.c`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/lm/lm-nvme.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/lm/lm-print-binary.c -->
# File Research: sources/virtualization/nvme-cli/plugins/lm/lm-print-binary.c

This file implements the binary output backend for LM plugin display operations.

Behavior:
- `binary_controller_state_data()` dumps the supplied controller-state buffer with `d_raw()`.
- `binary_controller_data_queue()` dumps the raw `nvme_lm_ctrl_data_queue_fid_data` structure.
- Exposes `lm_get_binary_print_ops()`, which stores the active print flags and returns the static `lm_print_ops` table.

Role:
- This is one of the strategy backends selected by `lm-print.c` when output flags include `BINARY`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/lm/lm-print-binary.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/lm/lm-print-json.c -->
# File Research: sources/virtualization/nvme-cli/plugins/lm/lm-print-json.c

This file implements JSON output for LM plugin data structures.

Behavior:
- `json_controller_state_data()` rejects non-zero offsets because it cannot interpret partial controller-state data. For full data, it emits:
  - Top-level controller state version, attributes, NVMe controller state size, and vendor-specific size.
  - Nested NVMe controller state header with version and queue counts.
  - Arrays for I/O submission queues and I/O completion queues, including PRP, queue size, IDs, attributes, and head/tail pointers.
- `json_controller_data_queue()` emits CDQ head pointer and tail pointer trigger.
- `lm_get_json_print_ops()` returns the JSON print-ops table.

Dependencies:
- Uses json-c wrappers from nvme-cli `common.h`.
- Uses little-endian conversions, including 128-bit helper conversion for state sizes.

Role:
- This backend is selected by `lm-print.c` when JSON output is requested and `CONFIG_JSONC` support is present.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/lm/lm-print-json.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/lm/lm-print-stdout.c -->
# File Research: sources/virtualization/nvme-cli/plugins/lm/lm-print-stdout.c

This file implements human-readable stdout output for LM plugin data structures.

Behavior:
- `stdout_controller_state_data()` decodes a full `nvme_lm_controller_state_data` buffer.
- It prints the outer controller-state header, including version, attributes, NVMe controller state size, and vendor-specific size.
- It prints the nested NVMe controller state header and then iterates submission and completion queue records.
- With verbose flags, it decodes selected bitfields for suspended state, submission queue priority/contiguity, completion queue interrupt/phase/contiguity fields.
- It detects and warns about truncated headers or truncated queue arrays based on the supplied buffer length.
- `stdout_show_controller_data_queue()` prints CDQ head pointer and tail pointer trigger.
- `lm_get_stdout_print_ops()` stores flags and returns the stdout ops table.

Notable quirk:
- The completion-queue pointer is calculated as `&data->data.cqs[niosq + i]`; given typical flexible layout naming, this may intentionally account for submission queue storage preceding completions, but it is worth checking against the exact struct definition in libnvme headers.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/lm/lm-print-stdout.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/lm/lm-print.c -->
# File Research: sources/virtualization/nvme-cli/plugins/lm/lm-print.c

This file is the LM print dispatcher.

Behavior:
- Defines an `lm_print()` macro that resolves an `lm_print_ops` table and invokes the requested operation if present.
- `lm_print_ops()` selects:
  - JSON backend when flags include `JSON` or global output format is JSON.
  - Binary backend when flags include `BINARY`.
  - Stdout backend otherwise.
- `lm_show_controller_state_data()` dispatches controller-state rendering.
- `lm_show_controller_data_queue()` dispatches CDQ feature rendering.

Role:
- Centralizes output-format selection so command implementations in `lm-nvme.c` do not need to know backend-specific formatting details.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/lm/lm-print.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/lm/lm-print.h -->
# File Research: sources/virtualization/nvme-cli/plugins/lm/lm-print.h

This header defines the LM print backend interface.

Key type:
- `struct lm_print_ops` with function pointers for:
  - `controller_state_data`
  - `controller_data_queue`
  - stored `nvme_print_flags_t flags`

Declared backends:
- `lm_get_stdout_print_ops()`
- `lm_get_binary_print_ops()`
- `lm_get_json_print_ops()` when `CONFIG_JSONC` is enabled

Fallback behavior:
- If JSON support is not compiled in, `lm_get_json_print_ops()` is an inline stub returning `NULL`.

Public display API:
- `lm_show_controller_state_data()`
- `lm_show_controller_data_queue()`

Role:
- Provides the shared contract between `lm-nvme.c`, the dispatcher, and individual print backends.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/lm/lm-print.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/lm/meson.build -->
# File Research: sources/virtualization/nvme-cli/plugins/lm/meson.build

This Meson snippet adds LM plugin source files to `plugin_sources`.

Always included:
- `plugins/lm/lm-nvme.c`
- `plugins/lm/lm-print.c`
- `plugins/lm/lm-print-stdout.c`
- `plugins/lm/lm-print-binary.c`

Conditionally included:
- `plugins/lm/lm-print-json.c` only when `json_c_dep.found()`.

Role:
- Keeps LM’s multi-file implementation integrated into the nvme-cli plugin build when the top-level plugin selection includes `lm`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/lm/meson.build -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/mangoboost/mangoboost-nvme.c -->
# File Research: sources/virtualization/nvme-cli/plugins/mangoboost/mangoboost-nvme.c

This file implements MangoBoost’s vendor-specific identify-controller extension.

Behavior:
- Defines `nvme_vu_id_ctrl_field`, with three 16-bit fields for a JSON-RPC 2.0 version tuple and reserved padding.
- `mangoboost_id_ctrl()` casts the identify-controller vendor-specific bytes, formats the version as `0x%04x%04x%04x`, and either:
  - adds `json_rpc_2_0_ver` to a JSON root, or
  - prints it to stdout.
- `id_ctrl()` delegates to nvme-cli’s shared `__id_ctrl()` with MangoBoost’s vendor-specific decoder callback.

Role:
- This is a minimal plugin implementation focused entirely on decoding a vendor-specific identify-controller field.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/mangoboost/mangoboost-nvme.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/mangoboost/mangoboost-nvme.h -->
# File Research: sources/virtualization/nvme-cli/plugins/mangoboost/mangoboost-nvme.h

This header registers the MangoBoost nvme-cli plugin.

Registered plugin:
- Name: `mangoboost`
- Description: `MangoBoost vendor specific extensions`
- Version: `NVME_VERSION`

Registered command:
- `id-ctrl`: calls the MangoBoost identify-controller wrapper in `mangoboost-nvme.c`.

The file uses the standard nvme-cli command generation macros and include pattern.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/mangoboost/mangoboost-nvme.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/memblaze/memblaze-nvme.c -->
# File Research: sources/virtualization/nvme-cli/plugins/memblaze/memblaze-nvme.c

This file implements the Memblaze nvme-cli plugin. It contains legacy Memblaze commands and newer `-x` commands for updated SMART, latency, high-latency, and performance logs.

Major command groups:
- Legacy SMART:
  - `mb_get_additional_smart_log()` reads log page `0xca` and chooses old Memblaze or newer Intel-like formatting based on controller model name.
- Power management:
  - `mb_get_powermanager_status()` gets feature `0x02`.
  - `mb_set_powermanager_status()` sets feature `0x02`.
- Legacy high latency:
  - `mb_set_high_latency_log()` sets feature `0xe1`.
  - `mb_high_latency_log_print()` reads log page `0xc3` repeatedly and writes `log_c3.csv`.
- Firmware:
  - `mb_selective_download()` downloads firmware chunks and commits with select values for `OOB`, `EEP`, or `ALL`.
- Legacy latency statistics:
  - `mb_set_lat_stats()` gets/sets latency tracking feature `0xe2`.
  - `mb_lat_stats_log_print()` reads log pages `0xc1`/`0xc2` and writes `log_c1.csv` or `log_c2.csv`.
- Error clearing:
  - `memblaze_clear_error_log()` sets feature `0xf7` with value `0x534d0001`.
- Newer `-x` logs/features:
  - `mb_get_smart_log_add()` reads `LID_SMART_LOG_ADD` (`0xca`) and prints versioned layouts.
  - `mb_set_latency_feature()` sets `FID_LATENCY_FEATURE` (`0xd0`) with monitor bits, command mask, and thresholds.
  - `mb_get_latency_feature()` reads and decodes feature `0xd0`.
  - `mb_get_latency_stats()` reads `LID_LATENCY_STATISTICS` (`0xd0`).
  - `mb_get_high_latency_log()` reads `LID_HIGH_LATENCY_LOG` (`0xd1`).
  - `mb_get_performance_stats()` reads `LID_PERFORMANCE_STATISTICS` (`0xd2`).

Key internal structures:
- Legacy/new SMART helpers rely on `nvme_memblaze_smart_log` and `nvme_p4_smart_log` from `memblaze-utils.h`.
- New SMART layout `smart_log_add` supports versions 0, 2, and 3 with different item structures and attribute maps.
- `latency_stats` supports version 2.0 with read/write/trim bucket arrays.
- `high_latency_log` supports version 1 with 1024 detailed latency entries.
- `performance_stats` supports versions 1 and 2 with up to 24 hourly timestamp groups and 3600 entries per timestamp.

Important implementation details:
- `getlogpage_format_type()` treats newer models as Intel-format and older `P...` models before `P5920` as Memblaze-format.
- Legacy high-latency parsing stops on `deadbeef`, zero latency/revision, or command error.
- Firmware download validates 4-byte image alignment, allocates a full firmware buffer, transfers in 4 KiB chunks, then commits with a vendor-specific select code.
- Newer performance stats handle odd duration by requesting one extra timestamp to avoid non-dword-alignment issues, while dumping only the requested logical size.
- Temperature fields are often printed in both Celsius and Kelvin through `K2C()`.

Notable quirks:
- Several legacy print paths allocate tiny buffers for normalized/raw values where stack arrays would be simpler.
- Some raw casts such as `*(__u16 *)raw` assume unaligned access is safe.
- `mb_get_performance_stats()` calls `exit(1)` on invalid duration, which is abrupt for a plugin command path.
- The file mixes older CSV-producing commands with newer stdout/raw commands, so behavior differs significantly between legacy and `-x` interfaces.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/memblaze/memblaze-nvme.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/memblaze/memblaze-nvme.h -->
# File Research: sources/virtualization/nvme-cli/plugins/memblaze/memblaze-nvme.h

This header registers the Memblaze nvme-cli plugin.

Registered plugin:
- Name: `memblaze`
- Description: `Memblaze vendor specific extensions`
- Version: `NVME_VERSION`

Registered commands:
- `smart-log-add`
- `get-pm-status`
- `set-pm-status`
- `select-download`
- `lat-stats`
- `lat-stats-print`
- `lat-log`
- `lat-log-print`
- `clear-error-log`
- `smart-log-add-x`
- `lat-set-feature-x`
- `lat-get-feature-x`
- `lat-stats-print-x`
- `lat-log-print-x`
- `perf-stats-print-x`

Role:
- Exposes both legacy Memblaze command names and newer expanded `-x` monitor/log commands implemented in `memblaze-nvme.c`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/memblaze/memblaze-nvme.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/memblaze/memblaze-utils.h -->
# File Research: sources/virtualization/nvme-cli/plugins/memblaze/memblaze-utils.h

This header defines Memblaze SMART log constants, layouts, and debug/printing macros.

Constants:
- SMART log sizes: old 512 bytes and new 4096 bytes.
- Field sizes for new SMART items: ID, normalized value, raw value.
- External SMART attribute IDs for Intel-like/Raisin layouts.
- Internal enum indexes mapping SMART items into arrays.
- Old Memblaze item enum indexes.

Structures:
- `nvme_memblaze_smart_log_item`: packed old-format SMART item with 3-byte ID, normalized value, and raw unions for temperature, power, thermal throttle, wear-leveling, power-loss protection, and related forms.
- `nvme_memblaze_smart_log`: old-format SMART log array plus padding to 512 bytes.
- `nvme_p4_smart_log_item`: newer Intel-like item with 3-byte ID, 2-byte normalized value, and 7-byte raw value.
- `nvme_p4_smart_log`: newer 4096-byte SMART log layout.

Macros:
- Debug macros prefixed `D...` for printing file/line/function and values.
- `fPRINT_PARAM1`/`fPRINT_PARAM2` write to a file and/or stdout depending on `fdi` and `print`.

Role:
- Provides the binary layout and attribute IDs used by both legacy and newer Memblaze SMART parsing in `memblaze-nvme.c`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/memblaze/memblaze-utils.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/meson.build -->
# File Research: sources/virtualization/nvme-cli/plugins/meson.build

This top-level plugin Meson file maps selected nvme-cli plugin names to source files and conditionally enters multi-file plugin subdirectories.

Main behavior:
- Defines `all_plugins`, mapping plugin names to C source files for simple plugins.
- Includes the group’s simple plugins:
  - `innogrit`: `plugins/innogrit/innogrit-nvme.c`
  - `inspur`: `plugins/inspur/inspur-nvme.c`
  - `intel`: `plugins/intel/intel-nvme.c`
  - `mangoboost`: `plugins/mangoboost/mangoboost-nvme.c`
  - `memblaze`: `plugins/memblaze/memblaze-nvme.c`
- On non-Windows hosts, reads selected plugin names from Meson option `plugins`; on Windows, selects none.
- Builds `plugin_sources` by stripping selected plugin names and appending matching entries from `all_plugins`.
- Conditionally adds subdirectories:
  - `feat`
  - `lm`
  - `ocp`
  - `sed` when OPAL support is enabled
  - `solidigm` when json-c is available
- Also conditionally includes `nbft` when fabrics support and `nbft` selection are present.

Role:
- This is the central build selection layer for nvme-cli plugins. LM is not in `all_plugins` because it has its own `plugins/lm/meson.build`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/meson.build -->