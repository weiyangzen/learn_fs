# Group Research: group_1336_nvme_cli_sources_virtualization_nvme_cli_plugins_ocp_ocp_nvme_c_sou_005bfa9b2ac6

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-nvme.c -->
# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-nvme.c

## Role

`ocp-nvme.c` is the main implementation file for the `nvme-cli` OCP cloud SSD plugin. It registers and implements user-facing commands for OCP log pages, vendor-specific feature get/set operations, telemetry retrieval/parsing, persistent event log decoding, and several delegated OCP helper commands.

The source tree `sources/virtualization/nvme-cli` is included by `Docs/research_subset_a.md`, so this file is in subset A scope.

## Command Surface

Through `CREATE_CMD` plus `ocp-nvme.h`, this file provides handlers for log retrieval, mutating feature commands, feature readers, telemetry workflows under `internal-log`, persistent events, hardware component logs, and wrappers for SMART, firmware history, and clear-feature helpers.

## Core Data Flow

Most command handlers define CLI options with `NVME_ARGS`, call `parse_and_open()`, validate output format when needed, call libnvme get-log/get-feature/set-feature/admin passthrough APIs, then dispatch decoded output through `ocp-print.c` wrappers.

For fixed OCP log pages, helpers allocate a buffer, call `ocp_get_log_simple()` or a tailored `nvme_init_get_log()` path, verify the OCP log page GUID, cast to a packed wire-layout struct from `ocp-nvme.h`, and pass it to the selected printer.

## Telemetry Behavior

The telemetry subsystem can fetch host/controller telemetry headers and data areas, save telemetry and C9 string logs to binary files, parse existing binaries, handle data area 4 ETDAS setup/cleanup, compute dynamic C9 table offsets, and route decoded output through the OCP print layer.

Global buffers such as `header_data`, `log_data`, `ptelemetry_buffer`, `pstring_buffer`, and `pC9_string_buffer` make this path stateful inside the process.

## Notable Risks And Edge Cases

- Several paths trust device-reported table sizes and offsets for allocation and copying.
- Some telemetry buffers are not freed on all early error paths.
- `extract_dump_get_log()` risks writing to an invalid descriptor for very small one-chunk dumps.
- Output/status printing is inconsistent across normal, JSON, and binary paths.
- Mutating commands rely mainly on parsing, UUID lookup, and NSID selection as safety gates.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-nvme.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-nvme.h -->
# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-nvme.h

## Role

`ocp-nvme.h` is both the OCP plugin command-registration header and the shared wire-format definition header for several OCP log pages and feature identifiers.

## Plugin Registration

The `PLUGIN()` block registers the `ocp` plugin as `OCP cloud SSD extensions` version `3.0.0`, with commands for SMART extended log, latency monitor, telemetry, firmware history, EOL/PLP mode, PCIe error clearing, unsupported requirements, error recovery, device capabilities, DSSD power state, PLP interval, telemetry profile/string log, async events, TCG configuration, error injection, IEEE1667 silo, hardware components, persistent events, and idle wake-up time.

## Wire Layouts

The header defines packed layouts for C3 latency monitor, C5 unsupported requirements, C1 error recovery, C4 device capabilities, C7 TCG configuration, and OCP TCG activity persistent event data. It also defines OCP log IDs and feature IDs.

## Notable Risks And Edge Cases

- Packed structs are wire contracts and must track OCP spec offsets exactly.
- Generic macros such as `READ`, `WRITE`, and `TRIM` can be easy to misuse.
- Future spec drift requires coordinated updates in this header and all print backends.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-nvme.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-print-binary.c -->
# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-print-binary.c

## Role

`ocp-print-binary.c` implements the binary output backend for selected OCP print operations by emitting raw log-page bytes through `d_raw()`.

## Implemented Operations

It supports raw output for hardware component logs, persistent event logs, C5 unsupported requirements, C1 error recovery, C4 device capabilities, C9 telemetry string logs, and C7 TCG configuration logs.

It does not implement binary callbacks for firmware activation history, SMART extended log, telemetry parse output, or C3 latency monitor log.

## Notable Risks And Edge Cases

- Hardware component size is derived from a device-reported 128-bit field converted through `long double`.
- Unsupported binary operations fail late through generic dispatch.
- The static backend stores flags globally for the process.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-print-binary.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-print-json.c -->
# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-print-json.c

## Role

`ocp-print-json.c` implements the JSON backend for OCP logs and OCP-specific persistent event decoding.

## Supported Logs

It supports JSON output for hardware component logs, firmware activation history, SMART extended log, telemetry parse output, C3, C5, C1, C4, C9, C7, and persistent event logs including OCP TCG activity events.

## Formatting Strategy

The file builds json-c objects with nvme-cli JSON helpers, converts little-endian numeric fields, formats GUIDs, and prints/frees root objects per operation. SMART extended output has two schema variants: v1 with historical human labels and v2 with snake_case keys.

## Notable Risks And Edge Cases

- Some GUID buffers are too small for 16-byte hex GUID strings.
- C9 uses variable-length stack arrays sized from device-reported fields.
- Some JSON keys are repeated in loops, notably C4 DSSD descriptors.
- Some wide fields are emitted with int-oriented helpers.
- JSON schemas are inconsistent across logs and SMART versions.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-print-json.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-print-stdout.c -->
# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-print-stdout.c

## Role

`ocp-print-stdout.c` implements the normal human-readable output backend for OCP print operations.

## Supported Logs

It prints hardware component logs, firmware activation history, SMART extended log, telemetry parse output when JSONC support is present, C3, C5, C1, C4, C9, C7, and persistent event logs.

## Formatting Strategy

The file prints directly with `printf()`, using endian conversion helpers and nvme-cli utility printers. C3 output converts encoded timers and thresholds into minutes/milliseconds. C9 output prints the fixed header, FIFO labels, optional string tables, and ASCII table.

## Notable Risks And Edge Cases

- C9 table arrays are variable-length stack arrays sized from device data.
- FIFO 15 prints `fifo16[j]` as the ASCII character, likely a copy/paste bug.
- Some fields are printed with narrower conversions than their struct type.
- Normal telemetry output is compiled only under `CONFIG_JSONC`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-print-stdout.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-print.c -->
# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-print.c

## Role

`ocp-print.c` is the OCP output dispatch layer. It chooses JSON, binary, or stdout backends based on output flags and exposes one wrapper per OCP log type.

## Dispatch Model

JSON is selected when flags include `JSON` or the global nvme-cli output format is JSON. Binary is selected when flags include `BINARY`. Otherwise stdout is used. Missing backend callbacks emit `unhandled output format`.

## Public Wrappers

The file wraps hardware component, firmware activation history, persistent event, SMART extended, telemetry, C3, C5, C1, C4, C9, and C7 print operations.

## Notable Risks And Edge Cases

- JSON takes precedence over binary if global output format says JSON.
- Missing callbacks are reported generically at runtime.
- Static backend objects mutate their `flags` field per call.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-print.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-print.h -->
# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-print.h

## Role

`ocp-print.h` defines the OCP print abstraction: `struct ocp_print_ops`, backend factory functions, and public dispatch wrappers.

## Print Operations

The callback table covers hardware component, firmware activation history, persistent event, SMART extended, telemetry, C3, C5, C1, C4, C9, and C7 output. It also stores `nvme_print_flags_t`.

## Backend Factories

Stdout and binary factories are always declared. JSON is conditional on `CONFIG_JSONC`; without it, `ocp_get_json_print_ops()` returns `NULL`.

## Notable Risks And Edge Cases

- Adding a new log requires updating the table, backends, and dispatch wrappers.
- Without JSONC, JSON requests degrade to generic unhandled-format behavior.
- Callback arguments are raw pointers to device-derived structures.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-print.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-smart-extended-log.c -->
# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-smart-extended-log.c

## Role

`ocp-smart-extended-log.c` implements the `smart-add-log` command for the OCP plugin. It retrieves the C0 SMART / Health Information Extended log page, validates its GUID, and dispatches output.

## Control Flow

`ocp_smart_add_log()` opens the target device and calls `get_c0_log_page()`. That helper validates output format, allocates a 512-byte buffer, gets the OCP UUID index, initializes an NVMe get-log command for `OCP_LID_SMART`, encodes UUID index into `cdw14`, submits it, validates the SMART cloud attribute GUID, and calls `ocp_smart_extended_log()`.

## Notable Risks And Edge Cases

- `ocp_get_uuid_index()` return value is not checked before using `uidx`.
- Status text is printed for non-JSON formats before GUID validation.
- GUID mismatch diagnostics are not zero-padded.
- The fixed 512-byte allocation assumes the C0 layout remains one log page.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-smart-extended-log.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-smart-extended-log.h -->
# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-smart-extended-log.h

## Role

`ocp-smart-extended-log.h` declares the OCP SMART / Health Information Extended C0 log page layout and the `ocp_smart_add_log()` command entry point.

## Data Layout

`struct ocp_smart_extended_log` maps the 512-byte C0 payload, including physical media units, NAND block health, ECC/recovery/error counters, thermal and PCIe metrics, shutdown/free-block/capacitor data, security and namespace utilization, PLP/endurance, OCP and NVMe version fields, media die health, command timeout/system-area counters, power and firmware build fields, reserved space, log page version, and GUID.

## Notable Risks And Edge Cases

- The struct is not explicitly marked `__packed`, unlike several OCP structs in `ocp-nvme.h`.
- Misspelled field names are now part of the C API consumed by printers.
- Print code reads some byte arrays as integer pointers.
- Future C0 revisions require updates here and in both print backends.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/ocp/ocp-smart-extended-log.h -->