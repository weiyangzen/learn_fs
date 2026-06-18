# Group Research: group_1331_nvme_cli_sources_virtualization_nvme_cli_nvme_print_json_c_sources__3140e45b8f62

Scope checked against `Docs/research_subset_a.md`: `sources/virtualization/nvme-cli` is included in subset A. The referenced internal group report path was not present in this checkout, so this report is based on the subset manifest and complete reads of both listed files.

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/nvme-print-json.c -->
# File Research: sources/virtualization/nvme-cli/nvme-print-json.c

## Purpose

`nvme-print-json.c` is the JSON output backend for `nvme-cli`. It implements a large `struct print_ops` table and maps nvme-cli/libnvme print callbacks into JSON object construction using `util/json.h`. The file is not command execution logic; it is presentation logic for NVMe identify data, log pages, feature decoders, topology views, status/error reporting, and raw buffer dumps.

## Main Entry Points

- `nvme_get_json_print_ops(nvme_print_flags_t flags)` returns the JSON `print_ops` implementation after storing the active output flags.
- `json_print(struct json_object *r)` serializes a JSON object, prints a newline, and frees the object.
- `json_show_init()` / `json_show_finish()` support grouped JSON output through the file-global `json_r` object and nested `json_init` counter.
- `json_output_status()`, `json_output_opcode_status()`, `json_output_error_status()`, `json_output_message()`, `json_output_perror()`, and `json_output_key_value()` provide JSON-formatted command status and message output.

## Structure And Responsibilities

The file starts with JSON helper aliases and wrappers:

- `obj_add_*` aliases wrap the project JSON helpers.
- `d_json()` and `obj_d()` convert binary buffers into arrays of printable ASCII rows.
- `obj_add_result()` and `obj_add_key()` format variadic text into JSON fields.
- `obj_create()` changes behavior depending on whether grouped output is active: standalone calls create and print a single object, while grouped calls add a new array/object under `json_r`.

The central mode switch is `verbose_mode()`, which tests `json_print_ops.flags & VERBOSE`. Many callbacks emit raw numeric fields in normal mode and decoded, human-readable sub-objects in verbose mode.

## NVMe Identify Formatting

The file formats multiple identify structures:

- `json_nvme_id_ctrl()` emits controller identify data, including serial/model/firmware strings, power state descriptors, capabilities, namespace counts, command set attributes, fabrics fields, and optional vendor-specific data callback output.
- `json_nvme_id_ns()` emits namespace capacity/usage, feature bits, protection and metadata fields, LBA formats, NGUID/EUI64, and vendor-specific bytes.
- `json_nvme_id_ns_lbaf()` formats namespace LBA formats, using verbose descriptions when requested.
- `json_id_iocs()` and `json_id_iocs_iocsc()` format I/O command set combinations.
- `json_nvme_cmd_set_independent_id_ns()`, `json_nvme_id_ctrl_nvm()`, `json_nvme_nvm_id_ns()`, `json_nvme_zns_id_ctrl()`, and `json_nvme_zns_id_ns()` cover command-set-specific identify data for independent, NVM, and ZNS structures.
- `json_nvme_id_ns_descs()` parses namespace identifier descriptor records and emits EUI64, NGUID, UUID, and CSI descriptors.
- `json_nvme_id_uuid_list()`, `json_id_domain_list()`, `json_nvme_id_nvmset()`, `json_nvme_endurance_group_list()`, `json_nvme_list_ns()`, and `json_nvme_list_ctrl()` format list-style identify responses.

## Log Page Formatting

The file contains JSON formatters for a wide range of NVMe log pages:

- Health and reliability: `json_smart_log()`, `json_endurance_log()`, `json_error_log()`, `json_self_test_log()`, `json_sanitize_log()`.
- Namespace and ANA state: `json_changed_ns_list_log()`, `json_ana_log()`, `json_lba_status()`, `json_lba_status_log()`, `json_resv_notif_log()`, `json_nvme_resv_report()`.
- Capability/effects: `json_effects_log()`, `json_effects_log_list()`, `json_fid_support_effects_log()`, `json_mi_cmd_support_effects_log()`, `json_support_log()`.
- FDP and placement: `json_nvme_fdp_configs()`, `json_nvme_fdp_usage()`, `json_nvme_fdp_stats()`, `json_nvme_fdp_events()`, `json_nvme_fdp_ruh_status()`.
- Persistent events: `nvme_json_pevent_log_head()`, `json_pevent_entry()`, and per-event helpers for SMART, firmware commit, timestamp, power-on reset, namespace changes, format, sanitize, set-feature, telemetry, thermal excursion, and vendor-specific event data.
- Physical/media logs: `json_phy_rx_eom_log()`, `json_phy_rx_eom_descs()`, `json_media_unit_stat_log()`, `json_supported_cap_config_log()`, `json_rotational_media_info_log()`, `json_power_meas_log()`.
- Fabrics/discovery logs under `CONFIG_FABRICS`: discovery, host discovery, and AVE discovery formatting.

## Register And Property Formatting

The register code has two layers:

- Field decoders such as `json_registers_cap()`, `json_registers_cc()`, `json_registers_csts()`, `json_registers_cmbloc()`, `json_registers_cmbsz()`, `json_registers_pmrcap()`, and related PMR/CMB/boot partition helpers.
- MMIO readers such as `json_ctrl_registers_cap()` through `json_ctrl_registers_pmrmscu()` that read BAR offsets and either emit raw numbers or verbose decoded objects.

`json_ctrl_registers()` emits the full controller register set. `json_ctrl_register()` handles a single register value. `json_single_property()` handles NVMe property output, using `json_single_property_human()` in verbose mode.

## Feature Formatting

Feature output is organized around `json_feature_show()` and `json_feature_show_fields()`.

`json_feature_show()` prints the feature ID, name, selected value, and either supported/select information or decoded fields. `json_feature_show_fields()` dispatches by feature ID to specific decoders for arbitration, power management, LBA ranges, temperature thresholds, error recovery, volatile write cache, queue counts, interrupt coalescing/configuration, async events, APST, host memory buffer, timestamp, KATO, HCTM, NOPSC, read recovery level, predictable latency, host behavior, sanitize, endurance event config, IOCS profile, spinup, power loss signaling, performance characteristics, metadata, host ID, reservations, write protection, FDP, boot partition write protection, power limit, power threshold, and power measurement.

The feature decoders mostly transform packed bitfields into named JSON keys while preserving some raw values.

## Topology And List Output

The file also implements JSON output for libnvme topology/list commands:

- `json_print_nvme_subsystem_list()` emits hosts, subsystems, controllers/paths, ANA state, and optional verbose subsystem metadata.
- `json_detail_list()` and `json_detail_list_v2()` emit detailed host/subsystem/controller/namespace trees.
- `json_simple_list()` emits a flat `Devices` array of namespace device paths and size data.
- `json_simple_topology()` emits host/subsystem/namespace topology with controller/path data.
- Multipath helpers add path ANA state, I/O policy-dependent fields, controller state, transport, and address details.
- `obj_add_ctrl_address_details()` centralizes optional transport address details such as `traddr`, `host_traddr`, `host_iface`, and `trsvcid`.

## Print Ops Registration

The `json_print_ops` table binds almost all JSON formatters to the generic nvme-cli print interface. This includes libnvme data printers, topology/list printers, and message/status printers. Any command using this `print_ops` backend gets JSON behavior through that table rather than calling these functions directly.

## Notable Implementation Details

- Endianness is consistently converted with `le*_to_cpu()` before JSON emission.
- 128-bit NVMe counters use `le128_to_cpu()` and `obj_add_uint128()`.
- Some binary data is emitted as printable ASCII rows rather than hex bytes.
- Several functions allocate temporary formatted strings with `asprintf()`/`vasprintf()` and rely on `__cleanup_free`.
- The persistent event parser bounds-checks event offsets against the supplied size before decoding entries.
- Fabrics-specific formatters compile to empty stubs when `CONFIG_FABRICS` is disabled.
- `json_pull_model_ddc_req_log()` contains a direct `printf("tpdrpl: %u\n", tpdrpl);` before adding JSON fields, which appears inconsistent with pure JSON output and is worth checking if strict JSON output matters.

## Dependencies

This file depends on:

- `libnvme.h` for NVMe structures, topology handles, status helpers, register helpers, and fabrics helpers.
- `nvme-print.h` for `struct print_ops` and print flags.
- `util/json.h` for JSON object construction and serialization.
- `nvme.h`, `common.h`, and `logging.h` for shared helpers, command globals, constants, and error strings.
- Conditional `CONFIG_FABRICS` and `CONFIG_MI` blocks for fabrics and NVMe-MI output paths.

## Risks And Maintenance Notes

- The file is very broad and mirrors NVMe specification growth. Adding new log pages or features requires updating both a formatter and the `json_print_ops` table.
- JSON key naming is not fully uniform; some keys are raw field names, some are human-readable spec descriptions, and some include spaces or punctuation. Downstream consumers may depend on these exact names.
- Verbose and non-verbose output schemas often differ structurally, so consumers should not assume stable shape across flags.
- Several parsers walk variable-length device-provided buffers. Existing checks are present in some paths, but new additions should be careful about length validation before pointer arithmetic.
- `json_r`/`json_init` is global state. It is suitable for the current CLI print model, but not reentrant.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/nvme-print-json.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/nvme-print-stdout-top.c -->
# File Research: sources/virtualization/nvme-cli/nvme-print-stdout-top.c

## Purpose

`nvme-print-stdout-top.c` implements the interactive stdout `nvme top` dashboard. It scans libnvme topology, gathers per-namespace and per-path I/O statistics, formats metrics into tables, and drives an interactive terminal dashboard with refresh, scrolling, subsystem selection, subsystem detail screens, uevent rescans, and resize handling.

## Main Entry Point

- `stdout_top(int refresh_interval)` initializes topology and dashboard state, builds the subsystem selection array, resets counters, runs the main event loop, and exits the dashboard on quit or error.

## Metric Calculation

The top of the file provides small helpers for deriving dashboard metrics from libnvme counters:

- Utilization: `nvme_calc_util_percent()`, `nvme_path_calc_util_percent()`, `nvme_ns_calc_util_percent()`.
- IOPS: `nvme_calc_iops()`, path and namespace read/write wrappers.
- Latency: `nvme_calc_latency()`, path and namespace read/write wrappers.
- Bandwidth: `nvme_calc_bandwidth()`, path and namespace read/write wrappers.
- Formatting: `nvme_format_iops()`, `nvme_format_bw()`, `nvme_format_lat()`.

The calculation code uses libnvme stat intervals in milliseconds, suppresses IOPS/bandwidth if the interval is under one second, assumes 512-byte sectors for bandwidth, and computes latency as ticks divided by I/O count.

## Aggregation Paths

Two aggregation styles are used:

- `nvme_ns_calc_aggr_stat()` and `nvme_path_calc_aggr_stat()` add read/write IOPS and bandwidth while tracking maximum read latency, write latency, and utilization.
- `nvme_ns_calc_stat()` and `nvme_path_calc_stat()` compute a single namespace/path row, including inflight I/O.

These helpers are used by subsystem summary tables, namespace tables, path performance tables, and controller summaries.

## Table Rendering

The file uses `util/table.h` to build stdout tables:

- `stdout_top_print_path_health()` prints per-path ANA state, retry count, failover count, and command error count.
- `stdout_top_print_ctrl_summary()` prints per-controller transport, address, state, resets, optional reconnects, errors, IOPS, latency, bandwidth, and utilization.
- `stdout_top_print_ns_stat()` prints namespace stats for non-multipath subsystems.
- `stdout_top_print_nshead_stat()` prints namespace-head stats for multipath subsystems.
- `stdout_top_print_path_perf()` prints per-path performance and includes I/O-policy-specific `Nodes` or `Qdepth` columns.
- `stdout_top_draw_subsys_screen()` prints the top-level subsystem summary table and footer.

Column filtering is used in two places:

- `stdout_top_print_ctrl_summary_tbl_filter()` hides `Paths` when not multipath and hides `Reconnects` for non-fabrics controllers.
- `subsystem_iopolicy_filter()` is referenced from elsewhere to hide/show path performance columns based on subsystem I/O policy.

## Topology And Stat Refresh

The topology is libnvme-backed:

- `stdout_top_rescan_topology()` creates a global libnvme context and scans current topology.
- `stdout_top_search_subsystem()` finds a subsystem by name after rescan.
- `stdout_top_build_subsys_arr()` builds an array of subsystem handles for selection.
- `stdout_top_find_subsys_by_name()` restores selection after topology changes.
- `stdout_top_update_stat()` updates namespace/path stats, using path stats only for multipath subsystems.
- `stdout_top_reset_stat()` resets namespace/path stat baselines before the dashboard loop starts.

This design lets the dashboard recompute deltas between refresh frames and recover from NVMe topology uevents.

## Interactive Dashboard Flow

`stdout_top()` runs a two-level UI:

1. Top-level subsystem summary screen:
   - Shows all subsystems.
   - Up/down changes selected row.
   - Enter opens the selected subsystem.
   - Timeout refreshes.
   - NVMe uevent rescans topology and attempts to keep selection by subsystem name.
   - SIGWINCH redraws.
   - `q` exits.

2. Subsystem topology/detail screen:
   - Implemented by `stdout_top_draw_subsys_topology_screen()`.
   - Rescans topology and finds the chosen subsystem by name.
   - Prints header, subsystem topology/config, stat tables, and footer.
   - ESC returns to subsystem selection.
   - Up/down scrolls the frame buffer.
   - Timeout refreshes.
   - NVMe uevent rescans and returns to selection if the subsystem disappeared.
   - `q` or dashboard error exits.

`stdout_top_print_subsys_topology()` decides whether to render multipath-specific namespace-head/path tables or non-multipath namespace stats, then always prints controller summary.

## Output Layout

The dashboard writes to a `FILE *stream` returned by `dashboard_init()`. It manually informs the dashboard about header/footer row counts so scrolling and reverse-video highlighting work correctly. The top-level screen highlights the selected subsystem row. Detail screens use a fixed header showing refresh interval and a footer showing ESC/quit instructions.

## Dependencies

This file depends on:

- `libnvme.h` for topology handles, stat counters, update/reset APIs, and subsystem/controller/path/namespace attributes.
- `nvme.h`, `nvme-print.h`, `common.h`, and `logging.h` for shared nvme-cli helpers, error output, cleanup attributes, and topology helpers such as `nvme_is_multipath()`.
- `util/dashboard.h` for terminal frame rendering, events, scrolling, resize handling, and uevent delivery.
- `util/table.h` for table construction, filtered columns, row formatting, and stream printing.

## Notable Implementation Details

- PCIe/fabrics detection is string-based: controllers whose transport is not `"pcie"` are treated as fabrics.
- The controller summary uses the first controller in a subsystem to decide whether the `Reconnects` column is shown.
- NUMA node `"-1"` is displayed as `NUMA_NO_NODE`.
- The subsystem detail screen rescans topology before display and on uevents, avoiding stale libnvme handles.
- The top-level loop stores the selected subsystem name before rescan so it can restore focus after topology changes.
- Most table allocation failures produce `nvme_show_error()` and unwind through `table_free()`.

## Risks And Maintenance Notes

- Metric units depend on kernel/libnvme counter semantics. Bandwidth assumes 512-byte sectors.
- IOPS and bandwidth intentionally report zero for intervals below one second; short refresh intervals may look inactive.
- Several event-loop branches use `goto draw` / `goto wait_for_event` to preserve scroll behavior. Changes should be tested interactively.
- The first-controller heuristic for fabrics/reconnect column visibility may be inaccurate for mixed-transport subsystems.
- Topology handles are invalidated on rescan; the code generally handles this by searching by subsystem name, and future changes should preserve that pattern.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/nvme-print-stdout-top.c -->