# sources/distributed-fs/ceph-client/tools/perf/builtin-mem.c

## Purpose

`builtin-mem.c` implements `perf mem`, a focused frontend for memory access sampling. The `record` subcommand configures memory-load/store events and delegates to `perf record`; the `report` subcommand delegates to `perf report --mem-mode` or dumps raw memory samples in text form. It also handles memory-operation selection, CPU filtering, physical address capture/reporting, data page size capture/reporting, and memory data-type profiling.

## Important APIs, Types, and Functions

`struct perf_mem` stores command state: embedded `perf_tool`, input name, sort key, booleans for unresolved-symbol hiding, raw dumping, force, physical address, page size, all-kernel/all-user, data type mode, selected load/store operations, CPU list, and CPU bitmap. `parse_record_events()` selects and configures PMU memory events from `-e`. `__cmd_record()` builds delegated record arguments. `dump_raw_samples()`, `process_sample_event()`, and `report_raw_events()` implement raw sample reporting. `get_sort_order()` builds default report sort keys. `__cmd_report()`, `parse_mem_ops()`, and `cmd_mem()` orchestrate command behavior.

## Control Flow

`cmd_mem()` initializes defaults to `perf.data` and both load/store sampling, parses common options and the `record` or `report` subcommand, resolves stdin pipe input when no input name is set, and dispatches on a prefix match for `record` or `report`.

`record` first locates a PMU supporting perf memory events and initializes memory-event support. It parses record-specific options while keeping unknown options for `cmd_record()`. It allocates enough argv space for all memory PMUs and optional CPU filtering, starts with `record`, decides whether the combined load-store event can satisfy both requested operations, otherwise enables separate load/store records, adds `-W` when weight sampling is needed and always adds `-d` for data source sampling. It appends `--phys-data`, `--data-page-size`, generated PMU event arguments from `perf_mem_events__record_args()`, all-user/all-kernel flags, CPU list, and remaining user arguments before calling `cmd_record()`.

`report` parses report options. If `--dump-raw-samples` is set it creates a perf session, configures a tool that resolves mmap/comm/fork/attr/build-id/auxtrace metadata, optionally builds a CPU bitmap, initializes symbols, prints a raw header, and processes events through `dump_raw_samples()`. Otherwise it builds `report --mem-mode -n`, appends a generated default `--sort=...` when needed, passes remaining arguments through, and calls `cmd_report()`.

`dump_raw_samples()` resolves the sample address, applies unresolved-symbol filtering, marks the DSO as hit, prints PID/TID/IP/data address, optional physical address and data page size, local weight, data source encoding, DSO, and symbol using the configured field separator.

## State and Persistence Behavior

The only persistent artifact is perf.data written by `record`; `report` reads perf.data or stdin. Runtime state is contained in `struct perf_mem`, global `input_name`, `symbol_conf.field_sep`, global memory-event configuration such as `perf_mem_record[]` and `perf_mem_events__loads_ldlat`, and temporary delegated argv arrays. Raw reporting creates and deletes a `perf_session`; delegated report/record leave persistence to those builtins.

## Dependencies and Integration Points

This file integrates with perf PMU memory-event helpers, perf record/report builtins, perf sessions, auxtrace synthesis, symbol resolution, address-location and DSO helpers, CPU bitmap parsing, sort key help for `SORT_MODE__MEMORY`, parse-options, and memory data source fields in perf samples. It relies on PMU support for memory events and on `perf_mem_events__record_args()` to emit architecture/PMU-specific event selectors.

## Risks and Edge Cases

No PMU support or failed memory-event initialization aborts record. `parse_record_events()` calls `exit()` for list/parse failures rather than returning an error, which is consistent with some perf option callbacks but makes it hard to recover. `get_sort_order()` uses a fixed 128-byte buffer and appends optional keys; current strings fit but future sort expansions need care. Store-only reports omit weight-oriented columns because stores have no cost. Raw output mutates `symbol_conf.field_sep` to a space when none is supplied. The non-field-separator IP/address format contains a suspicious `0x016` literal for the data address field, which may be a formatting bug. Combined load-store event selection depends on PMU tags and requested operation bits.

## Test Signals

Useful tests include `perf mem record` with default load/store, load-only, store-only, `-e list`, custom event strings, CPU lists, all-user/all-kernel, physical address and page-size flags, report default sort generation for load/store/data-type modes, `--sort` overriding while preserving `type` for data-type profile, raw dumping with and without field separators, hide-unresolved behavior, CPU filtering on raw reports, stdin input detection, and no-memory-PMU failure handling.
