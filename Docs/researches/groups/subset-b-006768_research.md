# Grouped Research: subset-b-006768

This grouped report covers the requested perf utility sources under `sources/distributed-fs/ceph-client/tools/perf/util/`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf_event_attr_fprintf.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/perf_event_attr_fprintf.c

## Purpose
This file renders a `struct perf_event_attr` into human readable fields for perf diagnostics. It converts numeric `type`, `config`, `sample_type`, branch sample type, and read format values into symbolic names where possible, falling back to decimal or hex encodings for unknown values.

## Important APIs, Types, and Functions
The exported API is `perf_event_attr__fprintf(FILE *fp, struct perf_event_attr *attr, attr__fprintf_f attr__fprintf, void *priv)`. Internal helpers include `__p_bits`, `__p_sample_type`, `__p_branch_sample_type`, `__p_read_format`, and the `stringify_perf_*` family. `__p_config_id` dispatches config formatting by `attr->type`; it can use `tracepoint_id_to_name()` and `perf_pmu__name_from_config()`.

## Control Flow
`perf_event_attr__fprintf` first resolves the PMU by `attr->type`, with a second pass for hardware and cache events that encode an extended PMU type in `attr->config`. It then walks each attr field through `PRINT_ATTRn` and `PRINT_ATTRf` macros. Required fields such as `type` and `config` are always printed, while most booleans and optional values are emitted only when nonzero.

## State and Persistence
The file has no persistent state. It consults the global PMU registry through `perf_pmus__find_by_type()` and may allocate a transient tracepoint name that is freed immediately.

## Dependencies and Integration Points
It depends on Linux perf ABI constants, `evsel_fprintf` callback formatting, PMU lookup/name decoding, and trace-event lookup. It is integrated with verbose perf output paths that need deterministic attr dumps.

## Risks
Bit-name tables must track kernel ABI additions or newer fields print as empty numeric masks. `__p_bits` advances the output pointer but keeps the original size argument, so it depends on `scnprintf` behavior and bounded fixed buffers. PMU name resolution can trigger lazy PMU discovery and may produce different strings on heterogeneous systems.

## Test Signals
Useful tests compare attr dump output for hardware, software, tracepoint, cache, raw, and extended-type events. Regression signals include missing names for new sample bits, tracepoint config leaks, and invalid PMU fallback strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf_event_attr_fprintf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf_regs.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/perf_regs.c

## Purpose
This file is the architecture-neutral dispatcher for perf register metadata. It maps ELF machine IDs to architecture-specific register masks, register names, IP and SP register identifiers, and SDT argument parsing hooks.

## Important APIs, Types, and Functions
Exports include `perf_sdt_arg_parse_op`, `perf_intr_reg_mask`, `perf_user_reg_mask`, `perf_reg_name`, `perf_reg_value`, `perf_arch_reg_ip`, and `perf_arch_reg_sp`. It works with `struct regs_dump` from sample decoding and the architecture helpers declared in `perf_regs.h`.

## Control Flow
Most functions switch on `e_machine` and call the matching `__perf_reg_*_<arch>` helper. Unknown machines log debug messages and return empty masks, `"unknown"`, or zero IP/SP IDs. `perf_reg_value` checks the requested ID against `PERF_SAMPLE_REGS_CACHE_SIZE`, validates that the sampled register mask contains it, computes the dense index in the sample register array, and caches the value by register ID.

## State and Persistence
There is no global state. Per-call caching is stored in the caller-owned `regs_dump` through `cache_mask` and `cache_regs`.

## Dependencies and Integration Points
The file depends on ELF machine constants, architecture-specific perf register modules, DWARF register naming, and sampled register storage. It feeds perf script/report paths that display sampled register values or resolve probe SDT arguments.

## Risks
Unsupported `e_machine` values silently lose register masks, which can degrade decoding without failing the whole command. `perf_reg_value` assumes `regs->regs` is ordered by ascending bits in `regs->mask`; mismatch with sample parsing corrupts displayed values.

## Test Signals
Tests should cover each supported ELF machine, unknown-machine fallbacks, dense-index register extraction, cache reuse, and invalid IDs. Architecture build coverage is important because missing helper definitions surface only on some configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf_regs.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/perf_regs.h

## Purpose
This header defines the register decoding contract used by perf sample display, SDT probe parsing, and DWARF integration. It exposes generic dispatch APIs and declares architecture-specific helper entry points.

## Important APIs, Types, and Functions
Public functions include `perf_sdt_arg_parse_op`, `perf_intr_reg_mask`, `perf_user_reg_mask`, `perf_reg_name`, `perf_reg_value`, `perf_arch_reg_ip`, and `perf_arch_reg_sp`. It defines `SDT_ARG_VALID`, `SDT_ARG_SKIP`, and `DWARF_MINIMAL_REGS(e_machine)`, which builds a minimal IP/SP sample mask.

## Control Flow
The header itself has no control flow except the `DWARF_MINIMAL_REGS` inline expression. Implementations are dispatched by `perf_regs.c` to per-architecture helpers such as arm64, arm, csky, loongarch, mips, powerpc, riscv, s390, and x86.

## State and Persistence
No state is declared here. Callers pass a `struct regs_dump` whose ownership and lifetime remain outside this header.

## Dependencies and Integration Points
It depends on Linux integer types and compiler annotations. It is included by code that decodes sampled registers, names registers for output, and converts SDT operand syntax into perf-compatible probe arguments.

## Risks
Adding a new architecture requires updating both declarations here and switch dispatch in `perf_regs.c`. `DWARF_MINIMAL_REGS` assumes IP and SP IDs fit in a 64-bit mask.

## Test Signals
Build matrix coverage across supported architectures is the primary signal. Unit tests can verify that `DWARF_MINIMAL_REGS` contains exactly the architecture IP and SP bits and that declarations stay aligned with implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/pfm.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/pfm.c

## Purpose
This file integrates libpfm4 event encoding into perf. It parses `--pfm-events` style event strings into perf evsels and lists host-supported libpfm events through perf's generic print callback interface.

## Important APIs, Types, and Functions
Exports are `parse_libpfm_events_option` and `print_libpfm_events`. Internal helpers include `libpfm_initialize`, `is_libpfm_event_supported`, `print_attr_flags`, and `print_libpfm_event`. It uses libpfm APIs such as `pfm_initialize`, `pfm_get_perf_event_encoding`, `pfm_get_pmu_info`, `pfm_get_event_info`, and `pfm_get_event_attr_info`.

## Control Flow
`parse_libpfm_events_option` duplicates the user string, tokenizes it on commas and braces, rejects nested groups, encodes each libpfm event into `perf_event_attr`, creates an evsel, marks it as a libpfm event, and applies group leadership. `print_libpfm_events` initializes libpfm, iterates present non-perf-event PMUs, fetches each event, builds an encoding description, checks support by attempting to open the event, and emits event or umask rows through callbacks.

## State and Persistence
There is no durable state in this file. It mutates the caller's `evlist` during parsing and creates transient CPU/thread maps while checking support.

## Dependencies and Integration Points
This file is compiled only when libpfm support is enabled. It integrates with perf parse-options, evlist/evsel creation, PMU lookup, thread and CPU maps, and print-events output.

## Risks
Group parsing is simple and does not support nesting. Support checks open real perf events and can vary by privileges, paranoid settings, CPU availability, and PMU driver behavior. Event listing can be expensive because every candidate may be probed.

## Test Signals
Tests should cover single events, grouped events, bad group syntax, unsupported libpfm names, and print output on hosts with and without libpfm PMUs. Permission-sensitive tests should validate the exclude-kernel retry path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/pfm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/pfm.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/pfm.h

## Purpose
This header provides the conditional public interface for libpfm4 integration. It lets callers use libpfm parsing and listing when available while compiling to no-op stubs without libpfm.

## Important APIs, Types, and Functions
With `HAVE_LIBPFM`, it declares `parse_libpfm_events_option` and `print_libpfm_events`. Without it, inline stubs return success for parsing and emit nothing for listing.

## Control Flow
The header uses preprocessor selection to either declare real functions or define inline no-op replacements. There is no runtime branching here.

## State and Persistence
No state is owned by the header. The real implementation mutates evlists, while stubs intentionally do not.

## Dependencies and Integration Points
It depends on `print-events.h` and subcmd parse-options. It is included by command-line parsing and event-listing code that should not care whether libpfm was built in.

## Risks
The disabled stub for parsing returns zero, so callers must ensure the option is not exposed or is documented correctly when libpfm support is absent. Otherwise a user-provided libpfm option could appear accepted but produce no events.

## Test Signals
Build tests should cover both `HAVE_LIBPFM` and non-libpfm configurations. CLI tests should ensure unavailable libpfm options are either hidden or handled explicitly by higher layers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/pfm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/pmu.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/pmu.c

## Purpose
This file implements individual PMU discovery, metadata loading, event alias handling, event-term to `perf_event_attr` encoding, PMU matching, sysfs path helpers, capabilities parsing, and cleanup. It is the core implementation behind `struct perf_pmu`.

## Important APIs, Types, and Functions
Key public APIs include `perf_pmu__init`, `perf_pmu__lookup`, `perf_pmu__config`, `perf_pmu__config_terms`, `perf_pmu__check_alias`, `perf_pmu__for_each_event`, `perf_pmu__num_events`, `perf_pmu__for_each_format`, `perf_pmu__format_pack`, `perf_pmu__format_unpack`, `perf_pmu__caps_parse`, `perf_pmu__warn_invalid_config`, `perf_pmu__pathname_*`, and `perf_pmu__delete`. Internal `struct perf_pmu_alias` stores sysfs and JSON event alias metadata.

## Control Flow
PMU creation reads type, format file names, CPU masks, uncore identifiers, alias names, max precision, event tables, and architecture defaults. Format files are often registered first and parsed lazily through flex/bison when needed. Alias lookup first checks the case-insensitive hashmap, optionally probes sysfs for a matching event file, then loads sysfs aliases or JSON events. Configuration parses terms, resolves aliases into weak terms, validates format names and maximum values, and packs sparse bitfields into `config` through `config4`.

## State and Persistence
State lives in the caller-owned `struct perf_pmu`: format lists, alias hashmap, sysfs/json alias counters, caps list, CPU maps, identifier strings, config masks, and lazy-loaded flags. Persistent external state is read from sysfs under `/bus/event_source/devices/<pmu>/` and built-in pmu-events tables.

## Dependencies and Integration Points
The file integrates with `pmus.c` for global registry scans, parse-events term structures, hwmon and DRM PMU specializations, tool and tracepoint PMUs, PMU JSON event tables, sysfs helpers, locale-safe scale parsing, and architecture hooks through weak `perf_pmu__arch_init`.

## Risks
Lazy loading makes ordering subtle: callers must tolerate aliases, formats, and caps becoming available on demand. Incorrect format masks can silently truncate config values when no parse error object is supplied. Sysfs and JSON aliases can overlap, with sysfs metadata being enriched or overridden by JSON. Regex matching for uncore identifiers and wildcard suffix stripping are compatibility-sensitive.

## Test Signals
Tests should use synthetic sysfs directories for format parsing, alias parsing, unit/scale/per-pkg/snapshot files, caps, invalid terms, value overflow, JSON/sysfs overlap, uncore name matching, and fake PMUs. Integration tests should verify that parsed event strings produce expected `perf_event_attr` fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/pmu.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/pmu.h

## Purpose
This header defines the PMU data model and public PMU operations used across perf event parsing, listing, selection, validation, and output.

## Important APIs, Types, and Functions
Core types are `struct perf_pmu`, `struct perf_pmu_caps`, `struct perf_pmu_info`, `struct pmu_event_info`, and `struct perf_pmu_format`. It defines PMU kind/type ranges for kernel perf-event PMUs, DRM, HWMON, tool, and fake PMUs. The header declares PMU configuration, alias checking, format packing, event iteration, matching, sysfs path helpers, caps parsing, deletion, and `perf_pmu__kind`.

## Control Flow
The header is declarative, with one inline classifier `perf_pmu__kind` that maps a PMU type value to an enum range. Runtime behavior is implemented mainly in `pmu.c` and consumed by `pmus.c`, parse-events, and print-events.

## State and Persistence
`struct perf_pmu` stores persistent in-process state for each discovered PMU: names, type, core/uncore flags, auxtrace flag, format list, alias hashmap, event-table pointer, alias counters, caps, CPU map, config masks, missing-feature flags, and memory-event descriptors.

## Dependencies and Integration Points
It depends on Linux bitmaps/lists/perf ABI, parse-events, generated pmu-events tables, map symbols, and memory-event definitions. It is the shared contract between PMU discovery, event parser, PMU printer, tool PMUs, hwmon, DRM, and architecture-specific code.

## Risks
The structure is broad and mutable, so initialization discipline matters. Fields such as `sysfs_aliases_loaded`, `cpu_aliases_added`, and `config_masks_computed` gate lazy work and can cause stale behavior if not reset in tests. Type range changes must stay aligned with `perf_pmu__kind`.

## Test Signals
Header-level signals are build coverage and ABI consistency. Unit tests can validate type classification, fake PMU behavior, initialized list heads, and that call sites do not dereference optional fields before initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/pmu.l -->
# sources/distributed-fs/ceph-client/tools/perf/util/pmu.l

## Purpose
This flex lexer tokenizes PMU sysfs format descriptions, such as `config:0-7` or `config1:1,6-7`, for the parser in `pmu.y`.

## Important APIs, Types, and Functions
It is generated with the `perf_pmu_` prefix, reentrant scanner support, and bison bridge support. The local `value` helper converts decimal text to a numeric `PP_VALUE` token and reports `PP_ERROR` on conversion failure. It also returns tokens for `config`, `-`, `:`, and `,`.

## Control Flow
The scanner matches decimal numbers first, then the literal `config`, punctuation, dots, and newlines. Dots and newlines are ignored. `perf_pmu_wrap` returns 1 to indicate end of input.

## State and Persistence
Scanner state is owned by flex and passed through `yyscan_t`. Parsed numeric values are stored in the bison semantic value for the current scanner.

## Dependencies and Integration Points
It includes `pmu.h` and `pmu-bison.h`, and is called by `__perf_pmu_format__load` in `pmu.c`. The parser ultimately fills a `struct perf_pmu_format`.

## Risks
Only decimal numeric input is accepted by this lexer. It silently ignores dots, which matches expected sysfs grammar but could hide malformed input. Overflow and conversion errors are collapsed into `PP_ERROR`.

## Test Signals
Parser tests should feed valid ranges, single bits, multiple comma-separated terms, malformed numbers, unsupported tokens, and config indexes. Generated scanner build coverage is also required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/pmu.l -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/pmu.y -->
# sources/distributed-fs/ceph-client/tools/perf/util/pmu.y

## Purpose
This bison grammar parses PMU format files into sparse bitmaps describing which bits of `perf_event_attr.config`, `config1`, `config2`, `config3`, or `config4` a named format term controls.

## Important APIs, Types, and Functions
The grammar accepts `PP_CONFIG ':' bits` and `PP_CONFIG PP_VALUE ':' bits`. `perf_pmu__set_format` builds a bitmap for single bits or ranges. Reductions call `perf_pmu_format__set_value(format, config_index, bits)`.

## Control Flow
The parser recognizes one or more format terms. `bits` is a comma-joined union of `bit_term` values, and `bit_term` is either a single number or a closed numeric range. Empty `to` values in `perf_pmu__set_format` mean a single bit.

## State and Persistence
The parser mutates the `struct perf_pmu_format` supplied through `%parse-param {void *format}`. It has no global state and uses a pure parser with reentrant lexer state.

## Dependencies and Integration Points
It depends on Linux bitmap helpers and `PERF_PMU_FORMAT_BITS` from `pmu.h`. `pmu.c` invokes it when a PMU format file is loaded.

## Risks
There is no explicit range validation in the grammar body before setting bits, so invalid large values depend on bitmap helper behavior and parser input constraints. Error reporting is intentionally silent through `perf_pmu_error`, making diagnostics depend on higher layers.

## Test Signals
Tests should validate config target selection, bit unions, ranges, single-bit terms, multiple format terms, and parse failures. Fuzzing malformed sysfs format text can catch grammar acceptance issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/pmu.y -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/pmus.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/pmus.c

## Purpose
This file manages the global collection of discovered PMUs. It lazily scans sysfs and tool-provided PMU sources, separates core PMUs from other PMUs, sorts and deduplicates names, finds PMUs by name/type/attr, and prints PMU event catalogs.

## Important APIs, Types, and Functions
Exports include `perf_pmus__find`, `perf_pmus__find_by_type`, `perf_pmus__find_by_attr`, scan functions, `perf_pmus__print_pmu_events`, `perf_pmus__print_raw_pmu_events`, `perf_pmus__have_event`, `perf_pmus__num_core_pmus`, `perf_pmus__supports_extended_type`, test PMU adders, `perf_pmus__fake_pmu`, and `perf_pmus__destroy`.

## Control Flow
`perf_pmus__find` first checks loaded lists, then selectively scans core, other, tool, hwmon, or DRM PMUs based on the requested name. `pmu_read_sysfs` opens the event source devices directory, creates PMUs through `perf_pmu__lookup`, adds placeholder core PMUs if needed, adds tool/hwmon/DRM PMUs, sorts lists, and marks type groups as read. Printing first counts all events, copies event metadata into a sortable array, sorts by topic/core/PMU/name, suppresses duplicates, and calls print callbacks.

## State and Persistence
The file owns static `core_pmus`, `other_pmus`, `read_pmu_types`, and cached extended-type support state. All state is in-process and reset by `perf_pmus__destroy`.

## Dependencies and Integration Points
It depends on sysfs PMU lookup in `pmu.c`, tool PMUs, hwmon, DRM, print callbacks, event support probing, list sorting, pthread once, and parse helpers for PMU name suffixes.

## Risks
Lazy scanning and static caches can leak cross-test assumptions if not destroyed. PMU suffix deduplication is architecture-sensitive, especially for decimal versus hexadecimal suffixes. Extended hardware type support is cached once and depends on opening real events successfully.

## Test Signals
Synthetic sysfs tests should verify scan order, core placeholder creation, suffix sorting, duplicate suppression, wildcard scans, attr fallback to first core PMU, and destroy/reset behavior. Runtime tests should cover hybrid core PMUs and unsupported extended types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/pmus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/pmus.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/pmus.h

## Purpose
This header declares the global PMU registry API used to discover, iterate, query, and print PMUs.

## Important APIs, Types, and Functions
It exposes PMU name comparison helpers, registry destruction, find-by-name/type/attr, iteration over all/core/event-matching/wildcard PMUs, event printing, raw PMU event printing, event existence checks, core PMU counts, extended-type support, test PMU insertion, fake PMU access, and first-core-PMU lookup.

## Control Flow
The header has no implementation control flow. Its functions are implemented in `pmus.c`, with individual PMU details delegated to `pmu.c` and specialized PMU providers.

## State and Persistence
No state is declared here, but the API operates on the static global PMU lists owned by `pmus.c`.

## Dependencies and Integration Points
It depends on `struct perf_pmu`, `struct perf_event_attr`, and `struct print_callbacks`. Consumers include event parsing, attr formatting, event listing, tests, and evsel PMU resolution.

## Risks
The API hides lazy global scans, so callers may trigger sysfs reads or event probes unexpectedly. Test helper functions mutate global PMU lists and require cleanup discipline.

## Test Signals
Build coverage should ensure all registry consumers include this header cleanly. Unit tests should validate name comparison and that `perf_pmus__destroy` resets state after using test PMUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/pmus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/powerpc-vpadtl.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/powerpc-vpadtl.c

## Purpose
This file decodes PowerPC VPA Dispatch Trace Log auxtrace data and turns it into synthesized perf samples that can be interleaved with normal ordered events.

## Important APIs, Types, and Functions
The exported entry point is `powerpc_vpadtl_process_auxtrace_info`. Internal state types are `struct powerpc_vpadtl` and `struct powerpc_vpadtl_queue`. Key helpers include `powerpc_vpadtl_decode`, `powerpc_vpadtl_decode_all`, `powerpc_vpadtl_timestamp`, `powerpc_vpadtl_sample`, `powerpc_vpadtl_process_queues`, queue setup/update functions, auxtrace callbacks, and `powerpc_vpadtl_synth_events`.

## Control Flow
Auxtrace info allocates decoder state, initializes queues, installs auxtrace callbacks, records PMU type, optionally prints dump info, synthesizes a `vpa-dtl` event attr, and processes indexed auxtrace queues. Queue setup reads the first buffer to capture boot timebase and frequency, computes queue timestamps, and inserts queues into an auxtrace heap. During ordered event processing, queues with timestamps earlier than the next perf sample are decoded and delivered as synthesized samples.

## State and Persistence
State is attached to `session->auxtrace`, with per-queue buffer pointers, timestamps, boot timebase, frequency, packet offsets, CPU numbers, and heap membership. No persistent files are written.

## Dependencies and Integration Points
It depends on perf session, auxtrace queues/heaps, perf data file access, evlist/evsel IDs, sample delivery, colorized dump output, and PowerPC DTL entry layout from included platform headers.

## Risks
Timestamp conversion uses floating-point division and assumes valid boot timebase/frequency records. Buffer sizes are rounded down to entry boundaries. Ordered-events mode is required. Raw sample sizing uses `sizeof(record)` where `record` is a pointer, which is a notable correctness risk if downstream expects the full entry size.

## Test Signals
Tests should feed synthetic auxtrace buffers containing boot records and DTL entries, verify timestamp ordering, heap interleaving, synthesized event IDs/names, dump mode output, malformed buffer handling, and cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/powerpc-vpadtl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/powerpc-vpadtl.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/powerpc-vpadtl.h

## Purpose
This header exposes the PowerPC VPA DTL auxtrace integration point and defines the private auxtrace info layout indexes used by perf data records.

## Important APIs, Types, and Functions
It defines `POWERPC_VPADTL_TYPE`, `VPADTL_AUXTRACE_PRIV_MAX`, `VPADTL_AUXTRACE_PRIV_SIZE`, and declares `powerpc_vpadtl_process_auxtrace_info(union perf_event *event, struct perf_session *session)`.

## Control Flow
There is no runtime control flow in the header. The declared function is invoked when a PowerPC VPA DTL `PERF_RECORD_AUXTRACE_INFO` record is encountered.

## State and Persistence
The header declares no state. The private-size macro describes how much auxtrace private data is expected in the perf event record.

## Dependencies and Integration Points
It forward-declares `union perf_event`, `struct perf_session`, and `struct perf_pmu`, and is consumed by auxtrace dispatch code and the implementation file.

## Risks
The enum order is part of the perf data auxtrace private ABI for this decoder. Any change must remain compatible with recorded data producers.

## Test Signals
Build tests should ensure the header is usable with forward declarations only. Auxtrace tests should validate that records smaller than `VPADTL_AUXTRACE_PRIV_SIZE` are rejected by the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/powerpc-vpadtl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/print-events.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/print-events.c

## Purpose
This file coordinates printing of all event categories used by `perf list`: PMU events, raw descriptors, breakpoints, SDT events, metric groups, and libpfm events.

## Important APIs, Types, and Functions
Exports are `print_events`, `print_sdt_events`, `metricgroup__print`, and `is_event_supported`. Internal `struct mep` stores metric printing rows in an rbtree. The `event_type_descriptors` table labels perf event types.

## Control Flow
`print_events` invokes PMU event printing, emits generic raw and breakpoint templates, prints SDT events from build-id probe caches, prints metrics, and delegates libpfm event listing. `is_event_supported` opens a temporary evsel for the requested type/config and retries with `exclude_kernel` and then `exclude_guest` if needed. Metric printing gathers metrics into an ordered rbtree before invoking callbacks.

## State and Persistence
The file does not keep global state. It reads build-id caches, probe caches, PMU tables, and metric tables, and creates temporary evsels/thread maps/rbtrees.

## Dependencies and Integration Points
It depends on PMU registry printing, probe-file/cache code, build-id cache, metricgroup APIs, libpfm stubs/implementation, tracepoint and event parsing helpers, and `struct print_callbacks`.

## Risks
Support probing depends on privileges and kernel policy. `print_sdt_events` returns early without deleting `sdtlist` if build-id listing fails, which is a small cleanup risk. Duplicate SDT names require build-id/path disambiguation, so cache corruption can affect output names.

## Test Signals
Tests should verify callback order, raw/breakpoint templates, metric grouping by semicolon-separated groups, SDT duplicate disambiguation, and support probing retry behavior. Both libpfm-enabled and disabled builds should be covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/print-events.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/print-events.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/print-events.h

## Purpose
This header defines the callback interface for printing event and metric catalogs independent of the final output format.

## Important APIs, Types, and Functions
`struct print_callbacks` contains lifecycle callbacks, `print_event`, `print_metric`, and `skip_duplicate_pmus`. It declares `print_events`, `print_sdt_events`, `metricgroup__print`, and `is_event_supported`.

## Control Flow
The header is declarative. Implementations call callbacks in a producer-defined order, allowing text, JSON, or other output formats to share event discovery logic.

## State and Persistence
No state is stored here. The caller supplies a `print_state` pointer passed back to every callback.

## Dependencies and Integration Points
It depends on Linux perf event and type definitions and is consumed by PMU printing, libpfm printing, and command output code.

## Risks
The callback contract assumes `skip_duplicate_pmus` is non-null where used. Field order and nullable string behavior must remain consistent across producers and output backends.

## Test Signals
Mock callback tests can validate all producers pass expected nullability, PMU metadata, descriptions, encodings, and duplicate-skipping decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/print-events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/print_binary.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/print_binary.c

## Purpose
This file provides a generic callback-driven binary dump formatter and a helper to identify null-terminated printable strings.

## Important APIs, Types, and Functions
Exports are `binary__fprintf` and `is_printable_array`. The printer callback receives `enum binary_printer_ops` events such as data begin, line begin, address, numeric data, padding, separator, character data, line end, and data end.

## Control Flow
`binary__fprintf` rounds `bytes_per_line` up to a power of two, iterates bytes, emits line start/address events at line boundaries, emits numeric byte data, pads incomplete final lines, emits a separator, emits printable-character phase callbacks, and ends the line/data. `is_printable_array` requires a non-null, non-empty, NUL-terminated buffer whose characters before the terminator are printable or whitespace.

## State and Persistence
There is no persistent state. All formatting state is local to one call and accumulated through callback return values.

## Dependencies and Integration Points
It depends on Linux `roundup_pow_of_two` and ctype helpers. It is used by perf output code that wants customizable binary presentation without hard-coding exact text formatting.

## Risks
`roundup_pow_of_two(0)` would be unsafe if callers pass zero bytes per line. Several callback invocations pass `-1` through an unsigned parameter, relying on callback interpretation. The separator callback return is not added to `printed`.

## Test Signals
Tests should cover full lines, partial final lines, different line widths, null callback, zero-length data, printable string detection, and callback return accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/print_binary.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/print_binary.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/print_binary.h

## Purpose
This header declares the binary printing operation protocol and public helpers for dumping byte arrays.

## Important APIs, Types, and Functions
It defines `enum binary_printer_ops`, `binary__fprintf_t`, `binary__fprintf`, inline `print_binary`, and `is_printable_array`.

## Control Flow
The inline `print_binary` simply calls `binary__fprintf` with `stdout`. Full control flow is implemented in `print_binary.c`.

## State and Persistence
No state is declared. Callers provide optional callback-private `extra` data.

## Dependencies and Integration Points
It depends on standard `stddef.h` and `stdio.h`. The enum is a stable callback protocol between generic binary traversal and concrete output renderers.

## Risks
Callbacks must handle all enum operations and unsigned values used as sentinels. API callers must provide a nonzero `bytes_per_line`.

## Test Signals
Compile tests should verify callback signatures. Behavior tests should validate that custom printers receive operations in the documented line/data order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/print_binary.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/print_insn.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/print_insn.c

## Purpose
This file prints sampled instruction bytes either as raw hex or as assembly using the capstone-backed disassembler.

## Important APIs, Types, and Functions
Exports are `sample__fprintf_insn_raw`, `fprintf_insn_asm`, and `sample__fprintf_insn_asm`. Internal `is64bitip` decides disassembler bitness from the mapped DSO or normalized machine architecture.

## Control Flow
Raw printing iterates `sample->insn` and emits two-digit hex bytes separated by spaces. Assembly printing delegates to `capstone__fprintf_insn_asm`. Sample assembly printing computes 64-bit mode, calls the disassembler with sample CPU mode, instruction buffer, length, and IP, and falls back to raw hex when disassembly returns an error.

## State and Persistence
No state is stored. All behavior depends on the passed sample, thread, machine, address location, and capstone backend.

## Dependencies and Integration Points
It depends on perf sample structures, machine/thread/map/dso metadata, capstone wrapper, and dump-insn output conventions. It is used by script/report paths that display sampled instruction bytes.

## Risks
Bitness fallback is heuristic when no DSO is mapped. Capstone availability and architecture support determine assembly quality. Invalid sample instruction lengths or buffers can affect output.

## Test Signals
Tests should cover raw output spacing, assembly fallback on disassembler error, DSO-derived 32/64-bit selection, and normalized machine-name fallback for x86_64, arm64, and s390.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/print_insn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/print_insn.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/print_insn.h

## Purpose
This header declares instruction printing helpers for perf samples and direct byte buffers.

## Important APIs, Types, and Functions
It declares `sample__fprintf_insn_asm`, `sample__fprintf_insn_raw`, and `fprintf_insn_asm`, and defines `PRINT_INSN_IMM_HEX`. Forward declarations cover `perf_sample`, `thread`, `machine`, and `perf_insn`.

## Control Flow
There is no header control flow. Implementations choose raw versus assembly output and capstone fallback behavior.

## State and Persistence
No state is declared. All formatting uses caller-supplied sample and machine context.

## Dependencies and Integration Points
The header depends on standard size and file types and is included by perf reporting/script code that needs instruction display.

## Risks
The prototypes mention `struct addr_location` without a forward declaration in this header, relying on includer context. That can be fragile if included standalone.

## Test Signals
Build tests with minimal includers can catch missing forward declarations. Functional tests should use the implementation through this API for raw and disassembled output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/print_insn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/probe-event.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/probe-event.c

## Purpose
This file converts user-facing `perf probe` definitions into kernel `kprobe_events` and `uprobe_events` trace definitions, lists existing probes, shows source lines and variables, handles SDT/probe caches, and applies or displays generated probe events.

## Important APIs, Types, and Functions
Major exports include `init_probe_symbol_maps`, `exit_probe_symbol_maps`, `get_target_map`, `parse_line_range_desc`, `parse_perf_probe_command`, `parse_probe_trace_command`, `synthesize_perf_probe_arg`, `synthesize_perf_probe_command`, `synthesize_probe_trace_command`, `convert_perf_probe_events`, `show_probe_trace_events`, `show_bootconfig_events`, `apply_perf_probe_events`, `cleanup_perf_probe_events`, `show_available_funcs`, `show_line_range`, `show_available_vars`, and `copy_to_probe_trace_arg`. It manages `struct perf_probe_event`, `struct probe_trace_event`, line ranges, trace args, and blacklist nodes.

## Control Flow
Parsing starts with probe point syntax, optional event/group names, SDT targets, line/offset/return modifiers, and probe arguments. Conversion sets default groups, tries absolute-address conversion, checks probe caches, tries DWARF debuginfo, then falls back to symbol maps. Post-processing rewrites DWARF addresses into kernel/module/user trace definitions, filters out blacklisted or out-of-text kprobes, and assigns event names while avoiding conflicts. Applying opens tracefs probe files, writes events, and optionally updates caches. Listing reads raw probe files, parses trace commands, converts back to user-facing probe events, and prints them.

## State and Persistence
Global state includes `probe_event_dry_run`, `probe_conf`, `host_machine`, `host_env`, a cached debuginfo object/path, and the kprobe blacklist list. Persistent external state is read from or written to tracefs/debugfs probe files, build-id caches, probe caches, debuginfo files, and namespace-aware target paths.

## Dependencies and Integration Points
It depends on symbol maps, DSOs, namespaces, build-id cache, probe cache/file APIs, libdw and optional debuginfod, tracefs feature probes, parse-events helpers, source path lookup, maps, sessions, and architecture weak hooks for probe post-processing.

## Risks
This file has many privilege and environment-sensitive paths: `/proc/kallsyms`, debugfs blacklist, tracefs feature support, debuginfo availability, namespaces, kernel relocation, and module load state. Memory ownership is complex across parse, conversion, and cleanup paths. Fallback behavior can produce less precise probes when DWARF is unavailable. Event naming must respect `MAX_EVENT_NAME_LEN` and conflict rules.

## Test Signals
Tests should cover command parsing, invalid syntax, SDT cache lookup, DWARF-required probes, no-DWARF symbol fallback, kprobe blacklist filtering, uprobe absolute addresses, event name conflict suffixing, trace command synthesis/parsing round trips, cache writes, bootconfig output, namespace target handling, and cleanup after partial failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/probe-event.c -->
