# subset-b-006763 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/header.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/header.c

## Purpose
`header.c` implements perf.data header and feature-section serialization, deserialization, printing, and pipe-mode feature-event processing for perf. It is the compatibility layer between recorded perf files/streams and `perf_session`, `evlist`, `evsel`, `perf_env`, build-id, tracing, AUX trace, BPF, PMU, topology, cache, clock, compression, and scheduler-domain metadata.

## Important APIs, types, and functions
The public entry points are `perf_session__read_header`, `perf_session__write_header`, `perf_header__write_pipe`, `perf_session__inject_header`, `perf_session__data_offset`, `perf_header__process_sections`, `perf_header__fprintf_info`, `perf_event__process_feature`, `perf_event__process_attr`, `perf_event__process_event_update`, `perf_event__process_build_id`, `perf_file_header__read`, `is_perf_magic`, feature bit helpers, `do_write`, `write_padded`, `build_caches_for_cpu`, and weak architecture hooks `get_cpuid`, `get_cpuid_str`, and `strcmp_cpuid_str`. The central dispatch table is `feat_ops[HEADER_LAST_FEATURE]`, built with `FEAT_OPR`/`FEAT_OPN` entries mapping each `HEADER_*` feature to optional write, print, and process callbacks.

## Control flow
Write-side flow starts in `perf_session__write_header` or `perf_session__inject_header`, both entering `perf_session__do_write_header`. It lays out ID arrays, `perf_file_attr` records, data offsets, feature offsets, feature sections via `perf_header__adds_write`, then rewrites the fixed `perf_file_header` at offset zero. `do_write_feat` writes or copies a feature section and clears the feature bit if the write fails. Pipe mode writes a smaller `perf_pipe_file_header` and later processes feature records through `perf_event__process_feature`.

Read-side flow starts in `perf_session__read_header`. It first tries pipe format, then reads regular file headers with endian and ABI detection, constructs an `evlist`, reads every event attribute and ID, then calls `perf_header__process_sections` to visit feature sections in feature-bit order. Each feature process callback fills `header.env`, session auxtrace state, evlist event names/groups, tracing data, or build-id DSOs.

## State and persistence
Persistent on-disk state includes the fixed perf header, attribute table, ID arrays, data section, and variable feature sections. In-memory state is stored in `perf_header` (`needs_swap`, offsets, feature bitmap, `last_feat`, `perf_env`) and in owning `perf_session` structures. Many process callbacks allocate strings, topology arrays, PMU capability arrays, BPF metadata nodes, cache nodes, memory-node bitmaps, or CPU domain maps that become part of `perf_env`. Compatibility state includes legacy magic handling, legacy ABI size probing, feature-bit byte swapping, old build-id ABI quirks, old CPU topology layouts, and pipe-stream `last_feat` discovery.

## Dependencies and integration points
The file depends on perf core utilities (`evlist`, `evsel`, `session`, `data`, `tool`, `pmu`, `pmus`, `env`, `build-id`, `auxtrace`, `trace-event`, `bpf-event`, `clockid`, `cputopo`, `cacheline`) plus Linux/sysfs/procfs interfaces. It integrates with `/proc/cpuinfo`, `/proc/meminfo`, `/proc/schedstat`, `/sys/devices/system/*`, libtraceevent, libbpf, AUX trace indexing, build-id DSOs/machines, perf inject feature copying, and perf report header printing.

## Risks
This file parses untrusted perf.data input. Bounds checks exist for command line count, NUMA nodes, PMU mappings, group descriptions, cache entries, BPF payload sizes, PMU caps, scheduler domains, and feature section sizes, but regressions here can still become memory pressure, bad offsets, wrong byte swapping, leaks on partial parse, or corrupted `perf_env` state. Feature write failures silently clear feature bits, which preserves file creation but can hide metadata loss. Cross-endian BPF info/BTF is intentionally ignored. Several process paths return early after allocating nested structures without full cleanup on every failure path, so fuzz/error tests matter. Header layout and feature ordering are compatibility-sensitive and must remain stable.

## Test signals
Good test coverage includes perf record/report round trips, pipe-mode report, cross-endian perf.data files, legacy `PERFFILE`/ABI samples, perf inject with copied features, BPF/libbpf enabled and disabled builds, libtraceevent enabled and disabled builds, malformed feature-section fuzzing, huge-count rejection tests for every capped section, sysfs/procfs-missing tests, topology-heavy machines, hybrid/PMU capability cases, AUX trace sessions, and `perf report --header`/`--header-only` output checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/header.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/header.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/header.h

## Purpose
`header.h` declares perf.data header constants, on-disk structures, in-memory header state, feature I/O helpers, and public APIs for reading, writing, injecting, processing, and printing perf headers and feature events.

## Important APIs, types, and functions
The `HEADER_*` enum assigns stable feature IDs from tracing data and build IDs through topology, BPF, compression, PMU capabilities, CPU domain info, ELF machine flags, and cacheline size. `struct perf_file_section`, `struct perf_file_header`, and `struct perf_pipe_file_header` describe serialized file/pipe headers. `struct perf_header` holds version, byte-swap requirement, offsets, feature bitmap, feature limit, and `perf_env`. `struct feat_fd` abstracts feature read/write against either a file descriptor or memory buffer. `struct perf_header_feature_ops`, `feat_writer`, and `feat_copier` define feature operation contracts.

## Control flow
Callers create or use a `perf_session`, then call `perf_session__read_header` for input or `perf_session__write_header`/`perf_session__inject_header` for output. Feature readers can use `perf_header__process_sections`; pipe readers feed feature events to `perf_event__process_feature`. Event attr/update/build-id processing APIs let stream readers reconstruct evlists and environment while consuming records.

## State and persistence
The declarations preserve the source of truth for the perf.data ABI. `HEADER_FEAT_BITS` is fixed at 256, and `DECLARE_BITMAP(adds_features, HEADER_FEAT_BITS)` appears in both serialized and in-memory structures. Header version, swap state, data size/offset, and feature offset are persisted or derived during reads.

## Dependencies and integration points
The header depends on Linux perf ABI types, bitmaps, `perf_env`, cpumap, stdio, and forward declarations for perf session/tool/event types. Architecture-specific implementations override CPUID hooks declared here.

## Risks
Changing enum ordering, struct layout, bitmap width, or function contracts breaks perf.data compatibility. `struct feat_fd` permits either `buf` or `fd`; misuse can route feature I/O to the wrong backend. The file exposes weak architecture hooks whose default behavior intentionally omits CPUID, so callers must tolerate missing CPU identifiers.

## Test signals
Compilation across architectures, ABI-size assertions or fixture reads, cross-endian header fixture tests, pipe-mode feature processing, and perf inject/record/report round trips are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/header.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/help-unknown-cmd.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/help-unknown-cmd.c

## Purpose
`help-unknown-cmd.c` implements perf's unknown-command suggestion and optional autocorrect behavior. It loads known built-in/external command names, computes Levenshtein distances against the user input, prints suggestions, and can return a single assumed command.

## Important APIs, types, and functions
The public function is `help_unknown_cmd(const char *cmd, struct cmdnames *main_cmds)`. Internal helpers are `perf_unknown_cmd_config` for `help.autocorrect`, `levenshtein_compare` for sorting by edit distance then name, and `add_cmd_list` for merging discovered external command names into the main command list.

## Control flow
`help_unknown_cmd` reads perf config, calls `load_command_list("perf-", ...)`, merges command arrays, sorts and deduplicates with subcmd helpers, then reuses `cmdname->len` to store edit distance. The best-distance prefix becomes the suggestion set. If `help.autocorrect` is set and exactly one best match exists, it warns, optionally sleeps via `poll`, and returns the assumed command name. Otherwise it prints an error and any close suggestions with distance below 6.

## State and persistence
State is transient except the static `autocorrect` config variable. Ownership is subtle: on autocorrect, `main_cmds->names[0]` is set to `NULL` before cleanup so the returned string remains valid for the caller; `other_cmds` is cleaned and merged storage is left in `main_cmds`.

## Dependencies and integration points
The file uses perf config parsing, command discovery/cleanup from subcmd help, `alloc_nr`, `zfree`, Levenshtein scoring, and the builtin command registry.

## Risks
`cmdname->len` is repurposed from name length to edit distance, so later code must not assume it still contains a string length after this function. Allocation failure falls back to the generic error path. Autocorrect sleeps in tenths of a second and can unexpectedly execute a command if config enables it.

## Test signals
Tests should cover no suggestions, single autocorrect match, multiple equal-distance suggestions, external command merging, duplicate removal, allocation failure simulation, and `help.autocorrect` values of zero, positive, and negative.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/help-unknown-cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/help-unknown-cmd.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/help-unknown-cmd.h

## Purpose
`help-unknown-cmd.h` is an empty zero-line header in this tree. It currently declares no include guard, types, macros, or functions.

## Important APIs, types, and functions
There are no APIs in this file. The implementation entry point for unknown-command handling is present in `help-unknown-cmd.c`, not declared here.

## Control flow
No control flow exists in this header.

## State and persistence
No state is declared or persisted.

## Dependencies and integration points
No direct dependencies exist because the file is empty. If included by another source file, it contributes no declarations and only serves as a placeholder.

## Risks
The main risk is assuming this header provides a prototype. Callers need an external declaration from another header or local declaration, otherwise compiler warnings/errors depend on include paths and C standard settings.

## Test signals
Build coverage is sufficient: if future code relies on declarations here, missing prototypes should surface during compilation with warnings-as-errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/help-unknown-cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hisi-ptt-decoder/hisi-ptt-pkt-decoder.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/hisi-ptt-decoder/hisi-ptt-pkt-decoder.c

## Purpose
This file pretty-prints HiSilicon PCIe Trace and Tuning packet bytes for dump/debug output. It understands the PTT 4DW and 8DW packet layouts and emits colored annotated dword rows.

## Important APIs, types, and functions
The public API is `hisi_ptt_pkt_desc(const unsigned char *buf, int pos, enum hisi_ptt_pkt_type type)`, which returns the decoded packet size. Internal packet layout enums name 8DW and 4DW fields. `union hisi_ptt_4dw` overlays DW0 bitfields for 4DW packets. Helpers include `hisi_ptt_print_pkt`, `hisi_ptt_8dw_kpt_desc`, `hisi_ptt_4dw_print_dw0`, and `hisi_ptt_4dw_kpt_desc`.

## Control flow
The dispatcher selects 8DW or 4DW decoding. 8DW decoding skips the check/reserved DW0 and reserved DW6 fields, printing prefix, headers, and time. 4DW decoding prints DW0 as decoded bitfields, then prints header DW1-DW3. Every printed row reads four bytes from `buf + pos` and advances by `HISI_PTT_FIELD_LENTH`.

## State and persistence
No persistent state is kept. Output goes directly to stdout using perf color helpers.

## Dependencies and integration points
It is called by `hisi-ptt.c` when `dump_trace` is enabled for AUX trace data. It depends on `color.h` and constants from `hisi-ptt-pkt-decoder.h`.

## Risks
The decoder assumes the caller rounded buffer length to complete packets and that `pos` is valid. It casts unaligned byte pointers to `uint32_t *` and uses C bitfields, which can be sensitive to alignment and compiler/endianness expectations. The function name typo `kpt` is internal but can hinder searches.

## Test signals
Use known 4DW/8DW packet byte fixtures, boundary tests for one packet, mixed invalid/truncated buffer tests in the caller, and stdout golden output for DW0 field formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hisi-ptt-decoder/hisi-ptt-pkt-decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hisi-ptt-decoder/hisi-ptt-pkt-decoder.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/hisi-ptt-decoder/hisi-ptt-pkt-decoder.h

## Purpose
This header defines the small packet-decoder ABI for HiSilicon PTT trace dumps: packet type identifiers, packet sizes, field width constants, and the decode/print function prototype.

## Important APIs, types, and functions
Constants include `HISI_PTT_8DW_CHECK_MASK`, `HISI_PTT_IS_8DW_PKT`, `HISI_PTT_MAX_SPACE_LEN`, and `HISI_PTT_FIELD_LENTH`. `enum hisi_ptt_pkt_type` distinguishes 4DW and 8DW packets. `hisi_ptt_pkt_size[]` maps packet types to 16 and 32 bytes. The declared function is `hisi_ptt_pkt_desc`.

## Control flow
Consumers inspect packet headers, choose an enum value, use `hisi_ptt_pkt_size[type]` for alignment/iteration, and call `hisi_ptt_pkt_desc` for formatted output.

## State and persistence
The header defines a non-const `static int hisi_ptt_pkt_size[]` in every translation unit that includes it. This is per-TU state, although it is intended as immutable lookup data.

## Dependencies and integration points
It relies on Linux `GENMASK` being available from includers before macro use; the `.c` files include `<linux/bitops.h>` before this header. It integrates with `hisi-ptt.c` and the decoder implementation.

## Risks
The array should ideally be `static const` to prevent accidental writes. The `HISI_PTT_FIELD_LENTH` typo is part of the local API. The header itself does not include `<linux/bitops.h>`, so standalone inclusion can fail.

## Test signals
Build the decoder and `hisi-ptt.c` together, assert packet sizes match 4DW/8DW expectations, and compile a standalone include test if the header is made more public.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hisi-ptt-decoder/hisi-ptt-pkt-decoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hisi-ptt.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/hisi-ptt.c

## Purpose
`hisi-ptt.c` plugs HiSilicon PCIe Trace and Tuning AUX trace data into perf session processing. It registers an `auxtrace` handler from `PERF_RECORD_AUXTRACE_INFO`, reads AUXTRACE payloads, and dumps decoded PTT packets when trace dumping is enabled.

## Important APIs, types, and functions
The public function is `hisi_ptt_process_auxtrace_info`. Internal `struct hisi_ptt` embeds `struct auxtrace` and records auxtrace type, session, host machine, and PMU type. Key callbacks are `hisi_ptt_process_auxtrace_event`, `hisi_ptt_process_event`, `hisi_ptt_flush`, `hisi_ptt_free_events`, `hisi_ptt_free`, and `hisi_ptt_evsel_is_auxtrace`.

## Control flow
`hisi_ptt_process_auxtrace_info` validates private data size, allocates a handler, extracts the PMU type from `auxtrace_info->priv[0]`, fills callback slots, installs it into `session->auxtrace`, and optionally prints info. Later, `hisi_ptt_process_auxtrace_event` mallocs a buffer sized by `event->auxtrace.size`, reads that many bytes from the perf data fd, and calls `hisi_ptt_dump_event` under `dump_trace`. Dumping determines packet type from the first dword, rounds the whole buffer down to that packet size, and iterates packet descriptions.

## State and persistence
State is session-scoped and freed by the auxtrace `free` callback. The implementation does not persist decoded events; it only consumes/dumps raw AUXTRACE data. `hisi_ptt_process_event`, flush, and free-events callbacks are placeholders returning success/no-op.

## Dependencies and integration points
It integrates with perf AUX trace, perf session data fds, `evsel` PMU typing, host machine state, `dump_trace`, color output, and the PTT packet decoder.

## Risks
`event->auxtrace.size` is stored in an `int`, so very large payload sizes risk truncation before allocation/read. The code computes `data_offset` for non-pipe input but does not use it after reading. Packet type is inferred once from the first packet, so mixed packet streams would be decoded incorrectly. Normal analysis support is minimal: non-dump processing currently drops data after reading.

## Test signals
Tests should cover AUXTRACE_INFO private-size validation, PMU type matching, pipe and file-backed AUXTRACE reads, `dump_trace` packet output for 4DW/8DW fixtures, zero/truncated payloads, large-size rejection behavior if added, and cleanup through session auxtrace free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hisi-ptt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hisi-ptt.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/hisi-ptt.h

## Purpose
`hisi-ptt.h` declares the public hooks and constants for HiSilicon PTT perf support.

## Important APIs, types, and functions
It defines `HISI_PTT_PMU_NAME` as `"hisi_ptt"` and `HISI_PTT_AUXTRACE_PRIV_SIZE` as one `u64`. It declares `hisi_ptt_recording_init` for record-side setup and `hisi_ptt_process_auxtrace_info` for report/session-side auxtrace setup.

## Control flow
Record code can initialize an auxtrace recorder for the `hisi_ptt` PMU. Read/report code calls `hisi_ptt_process_auxtrace_info` when an AUXTRACE_INFO event of this type is encountered.

## State and persistence
The private AUXTRACE payload contract is one `u64`, currently used by `hisi-ptt.c` as the PMU type.

## Dependencies and integration points
The declarations depend on perf PMU, auxtrace record, perf event, and perf session types supplied by including translation units. The header links record and report sides of HiSilicon PTT support.

## Risks
Only a minimal private data size is specified; future extensions must preserve compatibility. The header does not forward-declare all referenced structs itself, so include ordering matters unless callers already include perf core headers.

## Test signals
Build record/report configurations with HiSilicon PTT enabled, validate AUXTRACE private size, and test both PMU-name discovery and auxtrace-info processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hisi-ptt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hist.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/hist.c

## Purpose
`hist.c` implements perf's histogram aggregation engine: adding samples, merging equivalent entries, maintaining callchains, memory/branch/block metadata, applying filters, sorting/collapsing output trees, hierarchy navigation, diff pairing, event statistics, titles, and hists lifecycle.

## Important APIs, types, and functions
Public entry points include column width helpers, `hists__add_entry*`, `hist_entry_iter__add`, `hist_entry__delete`, `hists__collapse_resort`, output resort functions, hierarchy navigation functions, filter functions, stats incrementors, `hists__match/link/unlink`, `hist__account_cycles`, `evlist__fprintf_nr_events`, totals, title formatting, config parsing, `__hists__init`, `hists__init`, and `perf_hpp_list__init`. Four exported iterator operation tables implement normal, branch, memory, and cumulative sample handling.

## Control flow
Sample ingestion builds a temporary `hist_entry` in `__hists__add_entry`, resolves callchains through `hist_entry_iter__add`, and inserts or updates entries in `hists->entries_in` via `hists__findnew_entry`. Iterators specialize preparation and finish behavior for memory addresses, branch stacks, normal samples, or cumulative callchains. Collapse resort rotates input trees, merges by collapse keys into `entries_collapsed`, and optionally builds hierarchical trees. Output resort then sorts entries into `hists->entries`, sorts callchains, recomputes stats and column widths, and honors callbacks/progress.

## State and persistence
Histogram state is in-memory only. `struct hists` owns red-black trees, entry counts, filter pointers, stats, column widths, memory stat arrays, and hierarchy format lists. `struct hist_entry` owns references or copies of thread/map symbols, callchains, branch info, mem info, block/kvm info, srcline/srcfile, raw data, trace output, memory stats, diff pairs, hierarchy child trees, and optional custom allocation ops. Entries can move between input, collapsed, and output trees; hierarchy mode creates parent/child entries with `parent_he` and nested roots.

## Dependencies and integration points
The file depends on perf symbol/thread/map/session/callchain/sort/hpp infrastructure, memory and branch decoders, cgroup/namespace data, KVM/block info, annotation, source-line lookup, UI progress, and global `symbol_conf`. It is used by report/top/diff-style paths through `evsel__hists` and the evsel object extension registered by `hists__init`.

## Risks
Ownership is complex: insertion may clone or steal fields, hierarchy insertion intentionally nulls fields in source or new entries depending on active sort formats, and deletion must recursively release child trees and all optional metadata. Filter and hierarchy code mutates periods, filtered masks, folded UI state, and tree ordering; mistakes can produce wrong percentages or dangling rb-tree nodes. Cumulative callchain duplicate detection depends on comparator consistency. `random_max` assumes a nonzero reservoir size. `hists__filter_entry_by_parallelism` tests a bit indexed by `he->parallelism`; invalid values could read outside the intended bitmap if upstream data is not constrained.

## Test signals
Useful tests include normal/mem/branch/cumulative sample aggregation, callchain append/merge/sort, collapse with multiple sort keys, hierarchy reports with filters at different levels, diff pairing/link/unlink including dummy entries, column-width recalculation, decay/delete paths, memory-stat totals, source-line and trace-output ownership, lost/dropped sample stats, `hist.percentage` config parsing, and sanitizer runs for lifecycle-heavy report/top workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hist.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/hist.h

## Purpose
`hist.h` declares the data model and public APIs for perf histogram collection, output formatting, filtering, hierarchy traversal, TUI integration, and event statistics.

## Important APIs, types, and functions
Core types are `enum hist_filter`, `enum hist_column`, `struct hists`, `struct hist_iter_ops`, `struct hist_entry_iter`, `struct res_sample`, `struct he_stat`, `struct hist_entry_diff`, `struct hist_entry_ops`, `struct hist_entry`, `struct hists_evsel`, `struct perf_hpp`, `struct perf_hpp_fmt`, `struct perf_hpp_list`, `struct perf_hpp_list_node`, `struct hist_browser_timer`, and `struct block_hist`. It declares add/delete/resort/filter/match/link/stat/title APIs plus HPP registration, formatting, and dynamic-entry helpers.

## Control flow
Callers initialize histogram support with `hists__init` and per-hists state with `__hists__init`, add samples through `hist_entry_iter__add` or `hists__add_entry*`, collapse and output-sort entries, then render through HPP/TUI/stdio helpers. Filters update the same hists trees and stats. Hierarchy traversal helpers provide next/previous navigation over nested output trees.

## State and persistence
All state is runtime memory. `hists` stores input/collapsed/output trees, stats, filters, widths, memory-stat configuration, and hierarchy HPP formats. `hist_entry` is a large owning node with reference-counted thread/map symbol state, optional callchain storage as a flexible array, branch/memory/block/KVM metadata, UI fold state, diff data, raw/trace payloads, parent/child hierarchy roots, and custom allocator hooks.

## Dependencies and integration points
The header ties together callchain, color, events stats, evsel, map symbols, memory events, mutexes, samples, spark stats, stat helpers, UI progress, TUI/slang declarations, sort/HPP formatting, annotation, branch accounting, and parse-options config.

## Risks
Because many structs are exposed, ABI-like coupling inside perf is high. `struct hist_entry` requires `callchain` to remain last for flexible allocation. Inline helpers assume initialized list heads and non-null `hists`/`hpp_list`. TUI stubs return success when slang is disabled, so callers must understand that UI functionality may be compiled out.

## Test signals
Compile coverage with and without slang, unit-style tests for inline pair and percent helpers, report/top/diff integration tests, hierarchy navigation tests, HPP format registration tests, and memory sanitizer coverage around `hist_entry` flexible allocation are strong signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hwmon_pmu.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/hwmon_pmu.c

## Purpose
`hwmon_pmu.c` exposes Linux hwmon sysfs sensors as synthetic perf PMUs/events. It discovers `/sys/class/hwmon/hwmon*`, parses sensor files such as `temp1_input`, lists events with labels/descriptions, configures perf attrs from event terms, opens sensor input files, and reads counts.

## Important APIs, types, and functions
Public functions are `perf_pmu__is_hwmon`, `evsel__is_hwmon`, `parse_hwmon_filename`, `hwmon_pmu__new`, `hwmon_pmu__exit`, `hwmon_pmu__for_each_event`, `hwmon_pmu__num_events`, `hwmon_pmu__have_event`, `hwmon_pmu__config_terms`, `hwmon_pmu__check_alias`, `perf_pmus__read_hwmon_pmus`, `evsel__hwmon_pmu_open`, and `evsel__hwmon_pmu_read`. Internal `struct hwmon_pmu` embeds `perf_pmu`; `struct hwmon_pmu_event_value` tracks present item/alarm bitmaps, label, and generated name.

## Control flow
Discovery scans sysfs class hwmon symlinks, opens each device name, creates PMUs named `hwmon_<fixed-name>`, and assigns synthetic PMU types in the hwmon reserved range. Event loading opens the hwmon directory, parses regular filenames into type/number/item/alarm, groups files by type+number in a hashmap, reads labels, derives friendly names, and removes events lacking an `_input` file. Listing walks the hashmap and emits `pmu_event_info` with aliases, scale units, descriptions, extra item values, and config encodings. Config parsing resolves either direct `<type><num>` names or label-derived `<type>_<label>` names. Open creates fd entries for every requested cpu/thread slot; read `pread`s the input file and updates perf counts.

## State and persistence
State is per `struct hwmon_pmu`: sysfs directory path, perf PMU metadata, and a lazily populated hashmap of available sensor events. `pmu.sysfs_aliases_loaded` prevents repeated directory scans. Runtime event fds are stored in the evsel fd xyarray. Counts accumulate in `evsel->counts`; if `prev_raw_counts` exists, reads add the current raw sysfs value to previous values and increment enabled/running counts.

## Dependencies and integration points
The module depends on perf PMU/event parsing, hashmap, counts, evsel fd arrays, thread maps, sysfs helpers, low-level `io_dir`, and hwmon naming conventions documented by the kernel. It integrates with perf PMU discovery, `perf list`, parse-events alias checking, event opening, and stat/read paths.

## Risks
`parse_hwmon_filename` assumes sorted type/item string tables for `bsearch`; table changes must preserve lexical order. `evsel__hwmon_pmu_read` reads into `char buf[32]` then writes `buf[len] = '\0'`; if `pread` returns exactly 32, this is out of bounds. `hwmon_pmu__describe_items` appends with `snprintf(out_buf + len, out_buf_len - len, ...)` without guarding `len >= out_buf_len`, so long descriptions can underflow the remaining size. In `hwmon_pmu__new`, failure after `zalloc` calls `perf_pmu__delete(&hwm->pmu)` and may rely on initialization state. Event fds are duplicated per cpu/thread even though sensors are not CPU-specific. Sysfs labels and names are normalized but collisions are possible.

## Test signals
Tests should use fake sysfs hwmon trees for filename parsing, PMU discovery, label-derived names, events without input removal, alarm/item descriptions, direct and label alias config, scale/unit selection, fd open cleanup on partial failure, read count accumulation, and boundary cases for 32-byte sensor values and long descriptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hwmon_pmu.c -->
