# sources/distributed-fs/ceph-client/tools/power/x86/intel-speed-select/isst-display.c

## Purpose
`isst-display.c` centralizes text and JSON rendering for `intel-speed-select`. It formats package/die/powerdomain/CPU hierarchy, performance-profile details, base-frequency and turbo-frequency properties, core-power CLOS data, command results, errors, and TRL values. It is intentionally presentation-only but it influences command correctness because JSON state must be opened and closed in the right order.

## Important APIs, Types, And Functions
Public rendering functions include `isst_ctdp_display_information_start()`, `isst_ctdp_display_information_end()`, `isst_ctdp_display_information()`, `isst_ctdp_display_core_info()`, `isst_pbf_display_information()`, `isst_fact_display_information()`, `isst_clos_display_information()`, `isst_clos_display_clos_information()`, `isst_clos_display_assoc_information()`, `isst_display_result()`, `isst_display_error_info_message()`, and `isst_trl_display_information()`. Internal helpers `printcpulist()` and `printcpumask()` convert cpumasks; `format_and_print_txt()` and `format_and_print()` implement text/JSON indentation and object closure; `print_package_info()` emits the scope header.

## Control Flow
Callers normally bracket a command with `isst_ctdp_display_information_start()` and `_end()`. Within the bracket, each display function calls `print_package_info()` to enter the scope, emits nested fields through `format_and_print()`, and closes back to the package level. `isst_ctdp_display_information()` walks processed TDP levels, prints CPU counts, masks, ratios, base frequencies, uncore and memory frequencies, feature support/enabled state, thermal/power properties, TRL buckets, and nested PBF/FACT details. PBF and FACT standalone commands use the same internal helpers at a different base indentation.

## State And Persistence Behavior
The file has no external persistence, but it keeps formatting state in static variables `last_level`, `start`, and error index counters. Output goes to the `FILE *` supplied by callers or returned by `get_output_file()` for errors. The JSON mode is manually assembled by tracking indentation levels and recent levels, not by a JSON library.

## Dependencies And Integration Points
It depends on `out_format_is_json()`, `api_version()`, platform predicates, frequency multiplier and TRL level-name helpers, CPU topology size, `get_cpu_count()`, and standard `cpu_set_t` macros. The data being printed comes from structures declared in `isst.h` and populated by `isst-core.c` backends.

## Risks And Edge Cases
Manual JSON generation is fragile: missing start/end calls, unexpected level jumps, or error messages outside active output can produce invalid JSON. `printcpumask()` allocates a temporary integer mask and silently returns on allocation failure. Several buffers are fixed-size and can truncate long CPU lists on very large systems. Frequency formatting depends on backend multipliers, so incorrect ops selection yields wrong units. Some output field names vary by platform/API, which tests need to account for.

## Test Signals
Snapshot tests should exercise text and JSON output for platform scope, single CPU scope, API v1 and API v2+ package labels, PBF, FACT with bucket filtering and AVX filtering, CLOS info/config/association, result success/failure, errors both inside and outside display brackets, empty cpumasks, and large CPU masks. JSON output should be parsed by a JSON parser in tests, not only compared as text.
