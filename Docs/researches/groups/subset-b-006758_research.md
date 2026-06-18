# subset-b-006758 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/callchain.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/callchain.c

Purpose: implements perf call graph option parsing, sample callchain resolution, insertion/merge into a compressed callchain tree, sorting for report/top output, branch-count annotation, and lifecycle helpers for callchain roots and cursors.

Important APIs/functions: `parse_callchain_record_opt`, `parse_callchain_report_opt`, `parse_callchain_top_opt`, `record_opts__parse_callchain`, `perf_callchain_config`, `callchain_register_param`, `callchain_append`, `callchain_merge`, `callchain_cursor_append`, `sample__resolve_callchain`, `hist_entry__append_callchain`, `callchain_list__sym_name`, `callchain_node__scnprintf_value`, `callchain_branch_counts`, `free_callchain`, `decay_callchain`, `get_tls_callchain_cursor`, `callchain_param_setup`, `sample__for_each_callchain_node`, and `sample__merge_deferred_callchain`.

Control flow: option parsing sets the global `callchain_param` and symbol flags, then registers a sorter based on graph, flat, folded, or fractal mode. Samples are resolved by thread/machine code into a TLS `callchain_cursor`, committed for reading, and appended into `callchain_root.node`. Insertion walks an input rb-tree of children, compares by srcline, function, or address, splits partially matched nodes, and updates hit/count totals. Report flow sorts the input hierarchy into output rb-trees using absolute or relative thresholds. Merge flow replays source nodes into a cursor and appends them to a destination root. Deferred callchains splice an original kernel-side prefix with a later user callchain record.

State and persistence: global state includes `callchain_param`, `callchain_param_default`, `dwarf_callchain_users`, and the pthread key for per-thread cursors. Persistent runtime state is in `callchain_root` trees and allocated `callchain_list` entries that hold `map_symbol` references, srcline strings, branch type stats, and hit counters. The file does not write persistent storage, but its structures are embedded in hist entries and later emitted by perf report/top.

Dependencies and integration: depends on perf symbols, maps, DSOs, machines, threads, hist entries, branch metadata, record options, `symbol_conf`, `perf_hpp_list`, libpthread TLS, Linux rbtrees/lists, and architecture constants such as `EM_AARCH64`. It integrates with record option parsing, config parsing, sample resolution, histogram aggregation, report formatting, and branch-stack display.

Risks: parsing uses prefix matching, so abbreviated tokens are accepted and ambiguous future tokens can be hazardous. The tree code has complex split/merge ownership rules for `map_symbol` and branch stats. Sorting thresholds depend on cumulative hit math and may hide nodes if counts are stale. TLS cursor allocation failure only logs at debug level in some paths. Deferred callchain merge replaces the sample callchain pointer with new storage, so callers must honor `merged_callchain` and `deferred_callchain` ownership.

Test signals: exercise `perf record --call-graph fp,dwarf,lbr`, `perf report/top --call-graph graph,flat,fractal,folded`, callchain config keys, branch callstack display, srcline/function/address sorting, aarch64 FP fallback, and deferred user callchain streams. Memory tools should cover `free_callchain`, `callchain_merge`, partial-node splitting, and error paths from allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/callchain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/callchain.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/callchain.h

Purpose: declares the callchain data model, user-facing help text, option enums, global parameters, cursor types, and public APIs used by perf record/report/top and histogram code.

Important APIs/types: defines `enum perf_call_graph_mode`, `enum chain_mode`, `enum chain_order`, `enum chain_key`, `enum chain_value`, `struct callchain_node`, `struct callchain_root`, `struct callchain_param`, `struct callchain_list`, `struct callchain_cursor_node`, `struct stitch_list`, and `struct callchain_cursor`. Declares `callchain_register_param`, `callchain_append`, `callchain_merge`, `callchain_cursor_reset`, `callchain_cursor_append`, `callchain_cursor_commit`, `callchain_cursor_current`, `callchain_cursor_advance`, `sample__resolve_callchain`, `hist_entry__append_callchain`, `fill_callchain_info`, branch count printers, TLS cursor access, deferred merge, and iteration helpers.

Control flow: callers initialize a `callchain_root` with `callchain_init`, append frames to a cursor, commit the cursor to switch from write to read mode, then call append/merge APIs. Inline cursor helpers expose sequential reading and cumulative hit/count helpers. Public parsing and setup functions connect record/report options to the shared `callchain_param`.

State and persistence: exposes global `callchain_param`, `callchain_param_default`, and `dwarf_callchain_users`. Callchain roots own rb-tree/list nodes, while cursors cache allocated nodes across samples to reduce allocation churn.

Dependencies and integration: includes Linux list/rbtree, `map_symbol.h`, and `branch.h`, and forward-declares perf sample, evsel, hists, thread, map, record options, and address location types. It is a central contract between util callchain implementation, symbol resolution, histograms, UI/reporting, and branch display.

Risks: many structs are directly visible and mutable, so invariants such as initialized lists, cursor `last` pointers, refcounted `map_symbol` copies, and rb-tree ordering must be preserved by all users. The anonymous TUI fields inside `callchain_list` couple display state into aggregation nodes.

Test signals: compile coverage for all users is important because this header exposes many inline helpers. Runtime tests should append, commit, advance, reset, merge, free, and print callchains across all chain modes and keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/callchain.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cap.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/cap.c

Purpose: checks whether the current process has a Linux capability, with a root-user fallback when the capability syscall cannot be used.

Important APIs/functions: exports `perf_cap__capable(int cap, bool *used_root)`. It builds a `_LINUX_CAPABILITY_VERSION_3` header, calls `SYS_capget`, extracts the correct effective capability word, and returns a boolean.

Control flow: initializes `used_root` false, retries `capget` in the compatibility case where the kernel rewrites the version, falls back to `geteuid() == 0` on unsupported syscall errors, and rejects capabilities above 31 when only the older 32-bit capability format is available.

State and persistence: no persistent state. Output is the return value plus `*used_root`, which tells callers whether a coarse root fallback was used.

Dependencies and integration: uses `linux/capability.h`, `syscall(SYS_capget)`, `errno`, `geteuid`, and perf debug logging. It supports permission decisions for perf features such as `CAP_PERFMON`, `CAP_SYSLOG`, or `CAP_BPF`.

Risks: `used_root` must be non-NULL. The compatibility retry condition is subtle and relies on kernel-populated header fields. The bit extraction uses `1 << (cap & 0x1f)`, so keeping the selected word correct for newer capability sets is important.

Test signals: test under normal user, root, and file-capability environments; simulate old capability versions and `capget` failure if possible. Permission-sensitive perf commands should verify diagnostics distinguish real capabilities from root fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cap.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/cap.h

Purpose: provides a small public capability-checking interface and compatibility definitions for capability constants missing on older headers.

Important APIs/types: defines fallback values for `CAP_SYSLOG`, `CAP_PERFMON`, and `CAP_BPF`; declares `perf_cap__capable(int cap, bool *used_root)`.

Control flow: no implementation flow beyond the contract that callers pass a capability id and receive capability status plus whether root fallback was used.

State and persistence: no state.

Dependencies and integration: includes `stdbool.h` and `linux/capability.h`. Used by perf permission checks that need to compile on distributions with older kernel headers.

Risks: hardcoded fallback capability numbers must match Linux UAPI. Callers must initialize and pass valid `used_root` storage.

Test signals: build on old and new kernel headers, and run permission tests for perfmon, syslog, and BPF related code paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/capstone.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/capstone.c

Purpose: integrates the Capstone disassembler into perf annotation and instruction printing, including optional runtime `dlopen` support and symbol-aware x86 operand formatting.

Important APIs/functions: exports `capstone__fprintf_insn_asm`, `symbol__disassemble_capstone`, and `symbol__disassemble_capstone_powerpc`. Internal wrappers `perf_cs_open`, `perf_cs_option`, `perf_cs_disasm`, `perf_cs_free`, and `perf_cs_close` abstract static linking vs `LIBCAPSTONE_DLOPEN`. `capstone_init`, `print_insn_x86`, `print_capstone_detail`, and `find_file_offset` handle architecture setup and output enrichment.

Control flow: Capstone handles are opened per disassembly operation using the machine architecture and 32/64-bit mode. Single-instruction printing disassembles one instruction, resolves x86 immediates to symbols when possible, writes the mnemonic/operand text, stores instruction length, and closes the handle. Full-symbol disassembly reads bytes from the DSO, emits a function header line, disassembles all bytes, creates `disasm_line` entries, adds RIP-relative symbol comments for x86, and falls back to objdump by discarding partial output if Capstone fails mid-symbol. The PowerPC path maps file offsets and currently records raw 32-bit instruction words for type-related annotation sorting rather than full textual disassembly.

State and persistence: static cached `dlopen` and `dlsym` function pointers are used when runtime loading is enabled. Annotation state is persisted in `symbol__annotation(sym)->src->source` as newly allocated disassembly lines. File-local buffers are freed before return.

Dependencies and integration: depends on Capstone headers/library, `dlfcn` when enabled, perf annotation, DSO byte readers, maps, namespaces, symbol lookup, thread/machine architecture helpers, and file map parsing. Integrated as an objdump alternative for perf annotate and as a print backend for decoded instructions.

Risks: per-call Capstone initialization is noted as a TODO and can be expensive. Runtime loading failures return generic handle errors. The full-symbol path must discard all lines on partial decode to avoid mixed incomplete annotation. x86 detail output assumes Capstone detail mode and handles only RIP-relative memory operands. PowerPC support is intentionally incomplete. Care is needed around namespace file opening and ELF file offset calculation.

Test signals: build with static Capstone, `LIBCAPSTONE_DLOPEN`, and without Capstone. Exercise annotate on x86, arm64, arm, s390, and PowerPC inputs; test missing `libcapstone.so`, explicit objdump path fallback, unknown instruction bytes, kernel maps split into sections, and namespace-backed DSOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/capstone.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/capstone.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/capstone.h

Purpose: declares Capstone-backed annotation/disassembly entry points and provides no-op stubs when Capstone support is not compiled in.

Important APIs/types: declares `capstone__fprintf_insn_asm`, `symbol__disassemble_capstone`, and `symbol__disassemble_capstone_powerpc` under `HAVE_LIBCAPSTONE_SUPPORT`; otherwise inline stubs return `-1`.

Control flow: callers can invoke these functions unconditionally and treat `-1` as unsupported or fallback-required.

State and persistence: no state in the header.

Dependencies and integration: includes standard integer/stdio headers, Linux compiler/types helpers, and forward declarations for `annotate_args`, `machine`, `symbol`, and `thread`. It gates optional Capstone integration for annotate and instruction printing.

Risks: fallback behavior relies on callers interpreting `-1` consistently. The prototype includes architecture, cpumode, print options, and output stream details, so call sites must pass coherent machine/thread context for symbol resolution.

Test signals: compile both with and without `HAVE_LIBCAPSTONE_SUPPORT`; verify annotate falls back to objdump or other disassemblers when stubs are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/capstone.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cgroup.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/cgroup.c

Purpose: manages perf cgroup objects, command-line cgroup parsing, cgroup pattern expansion into event lists, cgroup id discovery, and environment cgroup lookup trees.

Important APIs/functions: exports `cgroup__new`, `cgroup__get`, `cgroup__put`, `evlist__findnew_cgroup`, `parse_cgroups`, `evlist__expand_cgroup`, `evlist__set_default_cgroup`, `cgroup__findnew`, `cgroup__find`, `__cgroup__find`, `perf_env__purge_cgroups`, `read_all_cgroups`, `read_cgroup_id`, and `cgroup_is_v2`. Internal helpers include `open_cgroup`, `add_cgroup`, `list_cgroups`, `match_cgroups`, and rb-tree insertion.

Control flow: explicit parsing assigns comma-separated cgroups to existing evsels and replicates a single cgroup across all events. Expansion mode first splices original events out, gathers cgroup names either literally or by regex walking the cgroup mount with `nftw`, clones each original evsel for every matched cgroup, repairs leader/metric/wildcard relationships via temporary `priv` pointers, copies metric events, and splices cloned events back. Environment lookup stores cgroups by id in an rb-tree protected by the perf environment rwsem.

State and persistence: global `nr_cgroups` counts explicit or expanded cgroups and `cgrp_event_expanded` records expansion. A temporary global `cgroup_list` holds matched names during expansion/discovery. `struct cgroup` persists name, fd, id, refcount, and rb-node while attached to evsels or perf environment trees.

Dependencies and integration: depends on cgroupfs mount discovery, `name_to_handle_at` when available, `statfs` for v2 detection, `nftw`/regex for expansion, evlist/evsel clone APIs, metricgroup copying, Linux rbtrees/refcounts, and perf env locking. It is used by perf stat/record event selection and cgroup metadata resolution in perf data.

Risks: cgroups can disappear between list/match/open, causing skipped entries. Regex expansion over cgroupfs can be expensive. `nr_cgroups` is global and increments even for empty entries. Leader and metric pointer repair relies on `pos->priv` being cleared correctly. `read_all_cgroups` can insert an invalid `-1ULL` id if file-handle lookup fails unless callers tolerate it.

Test signals: cover comma parsing, empty entries, single-cgroup replication, regex expansion, no-match diagnostics, cgroup v1/v2 mounts, missing perf_event controller, disappearing cgroups, metric group cloning, leader preservation, and perf env purge under lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cgroup.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/cgroup.h

Purpose: declares the cgroup object model and APIs used by perf event lists, option parsing, and perf environment metadata.

Important APIs/types: defines `struct cgroup` with rb-node, id, name, fd, and refcount. Declares global `nr_cgroups` and `cgrp_event_expanded`; APIs for reference management, creation/find, expansion, default assignment, option parsing, id lookup, environment purge, and full-system cgroup reading.

Control flow: callers create or find cgroups, attach them to evsels/evlists, optionally expand an evlist over matched cgroups, and later release references or purge environment trees.

State and persistence: cgroup references persist through evsel attachment or perf env rb-trees. `read_cgroup_id` is available only with `HAVE_FILE_HANDLE`; otherwise it is an inline `-1` stub.

Dependencies and integration: includes Linux compiler/refcount/rbtree and `util/env.h`; forward-declares option, evlist, and rblist types. It bridges command-line cgroup selection with event opening and perf data metadata.

Risks: users must pair `cgroup__get`/`cgroup__put`, and must not assume `read_cgroup_id` works on all builds. Global counters make repeated parsing in one process sensitive to reset behavior elsewhere.

Test signals: compile with and without `HAVE_FILE_HANDLE`; run event-list cgroup attachment, expansion, lookup, purge, and v2 detection tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cgroup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/clockid.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/clockid.c

Purpose: parses perf record clock id options and maps supported clock names to kernel `clockid_t` values while recording clock resolution.

Important APIs/functions: exports `parse_clockid` and `clockid_name`. Internal `get_clockid_res` calls `clock_getres` and stores nanosecond resolution. The clock map supports monotonic, monotonic_raw, realtime, boottime, tai, and short aliases.

Control flow: `parse_clockid` handles unset by clearing `use_clockid`, rejects duplicate settings, accepts numeric ids via `sscanf`, strips an optional `CLOCK_` prefix for names, stores the selected id and resolution in `record_opts`, and warns on unknown names.

State and persistence: mutates the `record_opts` supplied through the parse-options `option` value. No global mutable state.

Dependencies and integration: uses subcmd parse-options, `record_opts`, `clock_getres`, Linux `NSEC_PER_SEC`, and perf UI warning/debug infrastructure. It controls the `perf_event_attr.use_clockid` recording behavior indirectly through record options.

Risks: numeric parsing accepts any integer even if later unsupported by the kernel. `clock_getres` failure only warns and leaves resolution zero. Duplicate detection depends on `opts->use_clockid` already being accurate.

Test signals: parse each alias, `CLOCK_` prefix variants, numeric ids, unset behavior, duplicate option error, unknown name warning, and systems missing some clock ids at compile time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/clockid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/clockid.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/clockid.h

Purpose: exposes clock id parsing and display helpers for perf record options.

Important APIs/types: declares `parse_clockid(const struct option *opt, const char *str, int unset)` and `clockid_name(clockid_t clk_id)`.

Control flow: the parser is intended for subcmd option callbacks; the lookup converts stored ids back to known names.

State and persistence: no state in the header.

Dependencies and integration: includes `<time.h>` and forward-declares `struct option`. Used by record command option tables and reporting of selected clock ids.

Risks: consumers must pass an option whose `value` points to `struct record_opts`.

Test signals: compile option tables and run parse-options tests for named, numeric, and unset clock ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/clockid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cloexec.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/cloexec.c

Purpose: probes whether `perf_event_open` supports `PERF_FLAG_FD_CLOEXEC` and returns the correct flag to use on the current kernel.

Important APIs/functions: exports `perf_event_open_cloexec_flag`; internal `perf_flag_probe` opens a safe software event with and without `PERF_FLAG_FD_CLOEXEC`.

Control flow: the first caller triggers a static probe. The probe uses `sched_getcpu`, attempts `sys_perf_event_open` with pid `-1`, retries pid `0` on access errors to avoid unrelated jump-label changes, accepts a successful fd as support, and confirms fallback errors by trying without the flag. Unsupported or unexpected cases set the returned flag to zero.

State and persistence: static `flag` starts as `PERF_FLAG_FD_CLOEXEC`; static `probed` ensures the syscall probe runs once per process.

Dependencies and integration: depends on perf syscall wrapper, `perf_event_attr`, CPU scheduling helper, errno handling, warning macros, and `str_error_r`. Used by event-opening code to avoid passing an unsupported cloexec flag to old kernels.

Risks: probe results are process-global and assume kernel support will not change. Permission errors can mask support but are handled as nonfatal. Unexpected errors warn once. Thread races around the unsynchronized `probed` boolean are low risk but possible if multiple threads call first.

Test signals: run on kernels with and without flag support, with restrictive `perf_event_paranoid`, EACCES paths, and busy PMU conditions. Verify resulting fds are close-on-exec when support exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cloexec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cloexec.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/cloexec.h

Purpose: declares the cached `perf_event_open` cloexec flag probe.

Important APIs/types: `perf_event_open_cloexec_flag(void)` returns `PERF_FLAG_FD_CLOEXEC` or zero.

Control flow: callers add the returned flag to `perf_event_open` flags after the implementation probes support.

State and persistence: no header state; implementation caches the probe result.

Dependencies and integration: used by perf event-open paths that need close-on-exec behavior without breaking old kernels.

Risks: callers must not assume nonzero on all kernels and should still handle open failures.

Test signals: compile and runtime event-open tests on old/new kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cloexec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/color.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/color.c

Purpose: centralizes ANSI color emission for perf text output and percent/value threshold coloring.

Important APIs/functions: exports `color_vsnprintf`, `color_vfprintf`, `color_snprintf`, `color_fprintf`, `get_percent_color`, `percent_color_fprintf`, `value_color_snprintf`, `percent_color_snprintf`, and `percent_color_len_snprintf`.

Control flow: formatting helpers lazily auto-detect color use when `perf_use_color_default < 0`, based on TTY or pager state. They prepend the color sequence and append reset only when color is enabled and a non-empty color was requested. Percent helpers classify absolute values >= `MIN_RED` as red, > `MIN_GREEN` as green, otherwise normal.

State and persistence: global `perf_use_color_default` stores auto/forced color policy. No persistent files are touched.

Dependencies and integration: uses Linux `scnprintf`/`vscnprintf`, `isatty`, subcmd pager state, math `fabs`, and color constants from `color.h`. Integrated with report/stat/callchain output formatting.

Risks: global auto-detection is sticky and may be based on the first output stream used. Return values intentionally exclude color escape length for `color_vfprintf`, which callers must understand. `percent_color_snprintf` consumes varargs manually and assumes the first argument is a `double`.

Test signals: test TTY, pager, non-TTY, forced color settings, red/green/normal thresholds, snprintf truncation, and callers relying on visible width rather than byte count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/color.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/color.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/color.h

Purpose: declares color constants, threshold values, global color policy, and formatting helpers for perf output.

Important APIs/types: defines `COLOR_MAXLEN`, standard ANSI sequences, `MIN_GREEN`, `MIN_RED`, `PERF_COLOR_DELETE_LINE`, extern `perf_use_color_default`, and formatting/config functions.

Control flow: callers use color wrappers instead of raw `fprintf`/`snprintf` when output should respect perf color policy.

State and persistence: exposes mutable global `perf_use_color_default` representing auto/disabled/enabled color behavior.

Dependencies and integration: includes compiler printf annotations, stdio, and stdarg. Shared by reporting, UI, stat, and callchain value formatting.

Risks: visible length and byte length differ when color is enabled. Callers using varargs helpers must match expected argument types.

Test signals: compile-time format checking and runtime color/no-color output comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/color.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/color_config.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/color_config.c

Purpose: parses boolean-like color config values into an effective color policy.

Important APIs/functions: exports `perf_config_colorbool`.

Control flow: explicit `never` returns 0, `always` returns 1, and `auto` defers to terminal detection. Other values are parsed with `perf_config_bool`; false disables color, true behaves like auto. Auto enables color only when stdout or the pager is usable and `TERM` is not `dumb`.

State and persistence: no internal state; reads environment variable `TERM` and pager/TTY status.

Dependencies and integration: depends on perf config boolean parsing, `isatty`, subcmd pager state, environment access, and color policy users.

Risks: missing value is interpreted through `perf_config_bool` as true and therefore auto, matching Git-style config behavior. `stdout_is_tty` can be passed as precomputed state or `-1` to detect.

Test signals: config values `never`, `always`, `auto`, true/false aliases, unset value, `TERM=dumb`, pager active, and redirected stdout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/color_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/comm.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/comm.c

Purpose: represents thread command names (`comm`) with string interning, reference counting, and safe sharing across perf thread histories.

Important APIs/functions: exports `comm__new`, `comm__override`, `comm__free`, and `comm__str`. Internal functions manage `struct comm_str` allocation, refcounting, sorted lookup, insertion, and removal when the intern table holds the last reference.

Control flow: a process-wide intern table is initialized once with an rwsem and sorted pointer array. Lookups first take a read lock and use `bsearch`; misses take a write lock, recheck, grow capacity by 16 as needed, allocate a refcounted string object, and insert it in sorted order. `comm__new` creates a `comm` timeline entry with timestamp and exec flag. `comm__override` swaps interned strings and updates timestamp/exec state.

State and persistence: static `_comm_strs` stores the intern table for the process lifetime. Each `comm` owns a reference to a `comm_str`; the table also holds references until an entry becomes otherwise unused. No on-disk persistence.

Dependencies and integration: uses perf rwsem wrappers, Linux refcounting, rc-check helpers, `reallocarray`, list types from the public header, and thread/comm consumers in perf data processing.

Risks: table removal is subtle because `comm_str__put` may call `comm_strs__remove_if_last` while reference counts are changing. Sorted-array invariants must match `bsearch` and insertion logic. `comm__free` assumes non-NULL `comm`. The intern table itself is not freed, by design.

Test signals: create duplicate comm strings, override to existing/new strings, concurrent find/new/free patterns, capacity growth, refcount leak checks, and exec flag preservation when overriding with `exec=false`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/comm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/comm.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/comm.h

Purpose: declares the command-name timeline object used by perf thread metadata.

Important APIs/types: defines `struct comm` with interned string pointer, start timestamp, list node, exec marker, and a tool-specific union (`priv` or `db_id`). Declares `comm__new`, `comm__override`, `comm__free`, and `comm__str`.

Control flow: users allocate comm entries when COMM events or overrides are seen, place them in lists, query string text through `comm__str`, and release with `comm__free`.

State and persistence: `struct comm` instances are in-memory timeline records; implementation interns the string content.

Dependencies and integration: includes Linux list/types and bool. Integrated with thread histories, perf script/report, and database export via `db_id`.

Risks: ownership of list linkage is external; callers must unlink before freeing when needed. The tool-specific union requires consumers to coordinate interpretation.

Test signals: thread comm timeline updates, exec comm events, DB export ids, and lifecycle leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/comm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/compress.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/compress.h

Purpose: declares compression and decompression helpers for perf data streams with build-time support for gzip/zlib, lzma, and zstd.

Important APIs/types: declares gzip decompression/probing under `HAVE_ZLIB_SUPPORT`, lzma stream/file decompression and probing under `HAVE_LZMA_SUPPORT`, and zstd stream state in `struct zstd_data` plus `zstd_init`, `zstd_fini`, `zstd_compress_stream_to_records`, and `zstd_decompress_stream` under `HAVE_ZSTD_SUPPORT`. Inline stubs return failure/false or zero when support is unavailable.

Control flow: callers can compile unconditionally against lzma/zstd APIs and use return values to detect unsupported builds. Zstd state stores CStream/DStream pointers and compression level only when zstd is present.

State and persistence: `struct zstd_data` holds per-stream compression/decompression state. File decompression APIs write to caller-provided output fds.

Dependencies and integration: optional dependency on zstd headers, gzip/zlib and lzma implementation files elsewhere, stdio, sys/types, and Linux compiler annotations. Used by perf archive/data read/write paths handling compressed records.

Risks: stub semantics differ by API: lzma returns `-1`/false, zstd init/fini and stream calls return zero, so callers must interpret feature absence carefully. Function-pointer callback in zstd record compression must match the expected header processing contract.

Test signals: build matrix with each compression library enabled/disabled; decompress known gzip/lzma files; zstd round trips over record-sized chunks; unsupported-build fallback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/compress.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/config.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/config.c

Purpose: provides Git-style perf config file parsing, default config dispatch, typed conversion helpers, an in-memory config-set cache, and build-id/stat global defaults.

Important APIs/functions: exports `perf_default_config`, `perf_config`, `perf_config_scan`, `perf_config_get`, `perf_config_int`, `perf_config_u8`, `perf_config_u64`, `perf_config_bool`, `config_error_nonbool`, `perf_etc_perfconfig`, `perf_home_perfconfig`, `perf_config_system`, `perf_config_global`, `perf_config_set__new`, `perf_config_set__load_file`, `perf_config_set__collect`, `perf_config_set`, `perf_config_set__delete`, `perf_config__exit`, `perf_stat__set_big_num`, and `set_buildid_dir`.

Control flow: low-level parser reads one char at a time, skips UTF-8 BOM, handles sections including `[base "extension"]`, parses `key = value` with comments, quotes, escapes, and line continuations, and calls a supplied callback with `section.key` and value. Loading collects system and user config unless disabled by env or overridden by `config_exclusive_filename`. `perf_config` lazily initializes a global `config_set`, then iterates all collected items through the caller callback. Default dispatch recognizes `core`, `hist`, `ui`, `call-graph`, `buildid`, `stat`, and `addr2line` prefixes.

State and persistence: global `stat_config` is initialized here, `buildid_dir` stores cache root, parser globals track current file/line/eof, and `config_set` caches loaded config until `perf_config__exit`. Each config section/item stores ownership origin (`from_system_config`) for later rewriting decisions. `set_buildid_dir` also exports `PERF_BUILDID_DIR`.

Dependencies and integration: depends on perf callchain, hist, stat, evsel BPF-counter settings, srcline/addr2line, build-id, subcmd system paths, environment variables, Linux list/string/zalloc helpers, and standard file/stat parsing. It is a central integration point for perf command defaults.

Risks: `perf_config_set__init` initializes `ret` to `-1` and only changes behavior via file parse returns, so callers rely more on populated sets than the return value. Parser buffers cap names at 256 and values at 1024. Boolean parsing treats missing value as true. Numeric parsing accepts k/m/g suffixes but does not robustly check overflow. `perf_config_get` returns pointers owned by the global config set, invalid after exit.

Test signals: parse system/user/exclusive configs, env disables, BOM files, quoted section extensions, comments, escaped values, missing values, bad lines, typed ints with suffixes, default dispatch side effects, duplicate item replacement, and config set deletion under leak checking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/config.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/config.h

Purpose: declares perf config data structures, callback signatures, loading/iteration APIs, typed parsers, and iteration macros.

Important APIs/types: defines `struct perf_config_item`, `struct perf_config_section`, `struct perf_config_set`, `config_fn_t`, and extern `config_exclusive_filename`. Declares config load/apply/get/scan APIs, typed conversion helpers, path helpers, config-set lifecycle, collection/set-variable APIs, and `perf_config__exit`.

Control flow: config users either call `perf_config` to apply the cached global set to a callback or explicitly load/manipulate `struct perf_config_set` instances and iterate sections/items with macros.

State and persistence: config set structures own section/item strings and values in memory. `config_exclusive_filename` redirects loading to one file.

Dependencies and integration: includes Linux list and bool; relies on perf-wide `u8`/`u64` availability from common includes. Used by command setup, UI/color, stat, callgraph, build-id, and subsystem config callbacks.

Risks: iteration macros expand to nested loops, so early exit requires `goto` style as seen in implementation. Value pointers are owned by config sets. `perf_config_get` result lifetime is tied to the global config cache.

Test signals: compile users of iteration macros, load explicit config sets, apply callbacks with failures, and delete sets under leak checking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/copyfile.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/copyfile.c

Purpose: copies files for perf utilities, including namespace-aware source access, atomic-ish temporary destination handling, mode setting, and offset-based mmap copying.

Important APIs/functions: exports `copyfile`, `copyfile_mode`, `copyfile_ns`, and `copyfile_offset`. Internal `slow_copyfile` handles zero-size/proc-like files by line-based stdio copying through a mount namespace.

Control flow: `copyfile_mode_ns` stats the source in the requested namespace, creates a hidden temp file in the destination directory using `mkstemp`, uses slow copy for zero-sized sources, otherwise opens the source in the namespace and copies bytes with `copyfile_offset`, sets mode with `fchmod`, links the temp path to the final destination, unlinks the temp file, and closes fds. `copyfile_offset` mmaps from a page-aligned input offset and writes with `pwrite` until the requested size is copied.

State and persistence: writes the destination file through a temporary sibling path and hard link. No global state beyond `page_size` from util infrastructure.

Dependencies and integration: uses namespace helpers `nsinfo__mountns_enter/exit`, mmap, stat/open/link/unlink, internal lib page size, and Linux types. Used when perf copies build-id, DSO, or proc/sys files.

Risks: `copyfile_offset` calls `munmap(ptr, off_in + size)` after mutating `off_in` and `size`, so correctness depends on the final expression still matching the mapped length, which is fragile. `link(tmp, to)` fails if destination already exists. Slow copy is text-line based and may not preserve binary zero-sized virtual files. Namespace enter/exit must bracket only source-side operations.

Test signals: copy regular files, empty files, proc-like files, existing destination, interrupted `pwrite`, non-page-aligned offsets, large files, namespace source paths, and permission/mode propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/copyfile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/copyfile.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/copyfile.h

Purpose: declares perf file-copy helpers.

Important APIs/types: declares `copyfile`, `copyfile_mode`, `copyfile_ns`, and `copyfile_offset`; forward-declares `struct nsinfo`.

Control flow: callers choose default mode, explicit mode, namespace-aware copy, or fd/offset copy.

State and persistence: functions create/copy destination files or write to output fds.

Dependencies and integration: includes Linux types, sys/types, and fcntl mode definitions. Used by build-id and file cache code needing copies from normal or container namespaces.

Risks: callers must handle `-1` errors and destination-exists behavior. `copyfile_offset` requires valid fds and coherent offsets/size.

Test signals: compile namespace and non-namespace callers; run offset and full-file copy tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/copyfile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/counts.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/counts.c

Purpose: allocates, resets, and frees per-CPU/per-thread perf counter value arrays attached to evsels.

Important APIs/functions: exports `perf_counts__new`, `perf_counts__delete`, `perf_counts__reset`, `evsel__reset_counts`, `evsel__alloc_counts`, and `evsel__free_counts`.

Control flow: `perf_counts__new` allocates a `struct perf_counts`, then two `xyarray` matrices: one for `struct perf_counts_values` and one for loaded booleans. Error paths free earlier allocations. Evsel allocation sizes the arrays from `evsel__cpus(evsel)` and `evsel->core.threads`. Reset zeroes both arrays; free deletes both and nulls `evsel->counts`.

State and persistence: `struct perf_counts` persists in memory on an evsel. The `scaled` field and xyarrays represent current read status and values; no disk persistence.

Dependencies and integration: depends on evsel CPU/thread maps, libperf thread maps, `xyarray`, Linux zalloc, and perf count value structures from libperf.

Risks: callers must allocate before reset/read. `evsel__reset_counts` assumes `evsel->counts` is non-NULL. Array dimensions must match current CPU/thread maps; topology changes after allocation require reallocation by higher layers.

Test signals: allocate/free for multiple CPU/thread dimensions, allocation failure unwinding, reset loaded flags, and evsel lifecycle tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/counts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/counts.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/counts.h

Purpose: defines the perf counts container and inline accessors for per-CPU/per-thread counter values and loaded flags.

Important APIs/types: defines `struct perf_counts` with `scaled`, `values`, and `loaded` xyarrays. Provides inline `perf_counts`, `perf_counts__is_loaded`, and `perf_counts__set_loaded`, plus lifecycle declarations.

Control flow: users index xyarrays by CPU map index and thread index to read/write count values and loaded state.

State and persistence: in-memory count matrices attached to evsels.

Dependencies and integration: includes Linux types, internal xyarray, libperf evsel values, and bool. Used by stat/read paths that cache counter reads.

Risks: inline accessors do no bounds or NULL checks. Loaded array entries are stored as bool objects inside xyarray storage.

Test signals: bounds-aware callers, matrix dimension tests, and loaded flag transitions around counter reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/counts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cpumap.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/cpumap.c

Purpose: converts perf-recorded CPU map data into libperf CPU maps, formats CPU maps, builds aggregation maps, and discovers CPU/NUMA topology ids from sysfs.

Important APIs/functions: exports `perf_record_cpu_map_data__test_bit`, `perf_cpu_map__empty_new`, `cpu_map__new_data`, `cpu_map__snprint`, `cpu_map__snprint_mask`, `cpu_map__fprintf`, `cpu_map__online`, `cpu_aggr_map__empty_new`, `cpu_aggr_map__new`, `cpu__setup_cpunode_map`, `cpu__max_node`, `cpu__max_cpu`, `cpu__max_present_cpu`, `cpu__get_node`, `cpu__get_socket_id`, `cpu__get_die_id`, `cpu__get_cluster_id`, `cpu__get_core_id`, aggregation id constructors, and `aggr_cpu_id` comparison helpers.

Control flow: recorded data is decoded from explicit CPU entries, bit masks, or ranges into `perf_cpu_map`. Aggregation map construction calls a supplied id callback for every CPU, removes duplicates by equality, trims allocation, and optionally sorts. Sysfs helpers read topology ids from `/sys/devices/system/cpu/cpuX/topology/*`, parse possible/present CPU and node ranges to size sparse arrays, and fill a CPU-to-node map by walking `/sys/devices/system/node/node*/cpu*` symlinks. Formatting functions emit range lists or hexadecimal masks.

State and persistence: static globals cache max possible CPU, max present CPU, max node count, and `cpunode_map`. `cpu_map__online` caches an online CPU map and returns refcounted references. No file writes occur.

Dependencies and integration: depends on libperf cpumap internals, Linux bitmap helpers, sysfs API helpers, dirent traversal, perf debug logging, and `struct perf_record_cpu_map_data` from event records. Used by perf stat aggregation, record header decoding, CPU selection, and topology-aware reporting.

Risks: CPU ids are constrained to `INT16_MAX` in map storage. Sysfs reads can fail or be absent, leading to defaults such as 4096 CPUs or 8 nodes. `cpu__get_node` requires `cpu__setup_cpunode_map` first and does not bounds-check the CPU index. `cpu_map__snprint` uses `snprintf` with accumulated offsets and can compute lengths beyond buffer size. `cpu_map__online` is explicitly thread unsafe.

Test signals: decode cpumap record types, 32-bit and 64-bit masks on endian variants, dummy CPU `-1`, sparse CPU ranges, sysfs-missing fallback, NUMA map setup, aggregation duplicate removal/sorting, and mask/list formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cpumap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cpumap.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/cpumap.h

Purpose: declares CPU map conversion, formatting, topology lookup, and aggregation-id APIs.

Important APIs/types: defines `struct aggr_cpu_id`, `struct cpu_aggr_map`, `aggr_cpu_id_get_t`, `cpu_aggr_map__for_each_idx`, and declares cpumap creation/formatting, online map, max CPU/node, CPU topology id accessors, aggregation map construction, and aggregation id constructors.

Control flow: stat/report code builds `cpu_aggr_map` instances by passing a `perf_cpu_map` and a getter such as socket, die, cluster, core, CPU, node, or global.

State and persistence: header exposes in-memory CPU and aggregation map objects. Implementation has cached topology state.

Dependencies and integration: includes stdio, bool, and libperf `perf/cpumap.h`. Used broadly by perf stat aggregation, event headers, and topology display.

Risks: `cpu_map__is_dummy` assumes exactly one CPU entry of `-1`. Aggregation ids use `-1` sentinels, so equality and empty checks must stay in sync with struct fields. Some comments duplicate names inaccurately, but function contracts are clear.

Test signals: compile all aggregation modes, dummy CPU maps, map formatting, and topology lookup callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cpumap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cputopo.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/cputopo.c

Purpose: discovers and owns CPU, NUMA, and hybrid-core topology summaries from sysfs and PMU metadata.

Important APIs/functions: exports `online_topology`, `cpu_topology__new`, `cpu_topology__delete`, `cpu_topology__smt_on`, `cpu_topology__core_wide`, `numa_topology__new`, `numa_topology__delete`, `hybrid_topology__new`, and `hybrid_topology__delete`. Internal helpers build unique package/die/core CPU-list sets and load NUMA/hybrid nodes.

Control flow: CPU topology allocation sizes pointer arrays by max present CPU and by whether die topology exists for the architecture. It builds an online CPU map, scans online CPU numbers, reads package/die/core sibling lists with old-file fallbacks, and stores only unique strings. SMT detection checks whether any core sibling list contains more than one CPU. Core-wide validation parses a user CPU list and ensures every SMT sibling set is either entirely included or excluded. NUMA topology reads node online list, then each node's meminfo and cpulist. Hybrid topology scans core PMUs and reads each PMU `cpus` file.

State and persistence: `online_topology` caches a static topology pointer for process lifetime. Allocated topology objects own strings read from sysfs/PMU files. No persistent writes.

Dependencies and integration: depends on sysfs mountpoint helpers, libperf cpumaps, cpumap max-present CPU, PMU scanning/open-file APIs, debug logging, and Linux zalloc. Used by perf stat/report to describe packages, dies, cores, NUMA nodes, SMT coverage, and hybrid PMU CPU sets.

Risks: topology discovery depends on sysfs ABI files that vary by kernel and architecture. `numa_topology__delete` and `hybrid_topology__delete` assume non-NULL pointers. `cpu_topology__core_wide` does not check failed CPU-map allocations before iteration. The cached online topology does not update after CPU hotplug.

Test signals: sysfs fixture tests for package/core old and new names, die topology present/absent, SMT on/off, core-wide user CPU subsets, NUMA meminfo/cpulist parsing, hybrid PMU cpus files, CPU hotplug expectations, and allocation failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cputopo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cputopo.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/cputopo.h

Purpose: declares topology summary structures and constructors/destructors for CPU, NUMA, and hybrid PMU layouts.

Important APIs/types: defines `struct cpu_topology`, `struct numa_topology_node`, `struct numa_topology`, `struct hybrid_topology_node`, and `struct hybrid_topology`. Declares `online_topology`, CPU topology lifecycle, SMT/core-wide checks, NUMA lifecycle, and hybrid lifecycle.

Control flow: callers create topology snapshots, inspect unique CPU-list strings or node/PMU arrays, and free with matching delete functions.

State and persistence: structures own strings allocated from sysfs/PMU reads. `online_topology` returns a cached online-CPU snapshot.

Dependencies and integration: includes Linux types. Used by topology display and stat validation paths.

Risks: delete functions in the implementation expect valid pointers for NUMA/hybrid. Snapshots are not live-updating after CPU topology changes.

Test signals: construction/deletion under valgrind, SMT/core-wide logic, and hybrid/NUMA absence paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cputopo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cs-etm-base.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/cs-etm-base.c

Purpose: handles OpenCSD-independent CoreSight ETM auxtrace metadata validation and optional dump printing before delegating full processing.

Important APIs/functions: exports `cs_etm__process_auxtrace_info`. Internal helpers `cs_etm__print_cpu_metadata_v0`, `cs_etm__print_cpu_metadata_v1`, and `cs_etm__print_auxtrace_info` format global and per-CPU metadata for ETMv3, ETMv4, and ETE records.

Control flow: processing verifies the auxtrace info record is large enough, reads the private u64 header, rejects unsupported header versions above `CS_HEADER_CURRENT_VERSION`, optionally prints metadata when `dump_trace` is set, and calls `cs_etm__process_auxtrace_info_full` for the OpenCSD-backed path. Printing chooses v0 vs v1/v2 layouts and validates magic numbers for ETMv3/ETMv4/ETE.

State and persistence: no mutable state beyond stdout output during dump. It consumes event metadata in memory.

Dependencies and integration: depends on `cs-etm.h` constants, perf event auxtrace record layout, session type, `dump_trace`, and the full ETM processor provided elsewhere. It allows basic metadata debugging even when full decoder details are separated.

Risks: metadata printing indexes into `val` based on trusted counts and header version, so malformed records could expose bounds issues if earlier size validation is insufficient. Unknown future parameters print as generic only for v1/v2 supported layouts. Output goes directly to stdout.

Test signals: ETMv3, ETMv4, and ETE auxtrace info records across header versions 0, 1, and 2; bad magic; too-small records; unsupported future version; dump_trace on/off; and full processor delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cs-etm-base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cs-etm-decoder/cs-etm-decoder.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/cs-etm-decoder/cs-etm-decoder.c

Purpose: wraps the OpenCSD C API to decode CoreSight ETM/PTM/ETE trace streams into perf packet queues, including memory access callbacks, timestamp handling, discontinuities, exceptions, PE context updates, and decoder lifecycle.

Important APIs/functions: exports `cs_etm_decoder__new`, `cs_etm_decoder__free`, `cs_etm_decoder__process_data_block`, `cs_etm_decoder__reset`, `cs_etm_decoder__add_mem_access_cb`, `cs_etm_decoder__get_packet`, and `cs_etm_decoder__get_name`. Internal helpers build ETMv3/ETMv4/ETE configs, create OpenCSD decoders, initialize logging, buffer packet/range/exception/discontinuity events, estimate timestamps, and handle PE context TID/EL updates.

Control flow: construction creates an OpenCSD decode tree for formatted or single-source trace, configures frame flags, initializes default logging with perf's packet printer, and creates one protocol decoder per trace parameter block. Decode mode installs a generic trace element callback; print mode installs protocol packet printers. Data processing alternates `OCSD_OP_DATA` with `OCSD_OP_FLUSH` when the previous return asked to wait, stops when packet queues fill or data is consumed, records consumed bytes, and stores the current OpenCSD response for the next call. Trace element callbacks map instruction ranges to `CS_ETM_RANGE` packets, discontinuities to reset markers, exceptions to exception packets, timestamps to hard/soft timestamp state, and PE contexts to trace-id queue TID/EL state.

State and persistence: `struct cs_etm_decoder` holds caller data, packet printer, suppression flag, OpenCSD tree handle, memory callback, previous datapath response, and decoder name. Packet queue state lives in caller-owned `cs_etm_packet_queue` objects retrieved through ETM queue helpers: head/tail/count, buffered packet array, timestamp fields, and instruction count remainder.

Dependencies and integration: depends on OpenCSD C API, CoreSight PMU UAPI, `cs-etm.h` queue helpers, packet structures, timestamp conversion, intlist/debug utilities, and Linux zalloc/bug helpers. It is the bridge between raw AUX trace bytes and perf's synthesized instruction/branch samples.

Risks: queue ring management intentionally increments head/tail before use and requires `CS_ETM_PACKET_MAX_BUFFER` to be power-of-two compatible. Timestamp estimation assumes `INSTR_PER_NS = 10`, clamps or warns on zero/underflow, and can affect sample ordering. OpenCSD fatal responses propagate as generic errors. Memory access callback must be installed before decode needs memory. `cs_etm_decoder__new` requires a packet printer even in decode paths because logging initialization returns failure without it.

Test signals: construct decoders for ETMv3, PTM, ETMv4i, and ETE; decode formatted and unformatted streams; exercise print vs decode operations; packet queue full/wait handling; discontinuity reset; hard and soft timestamps including zero/underflow cases; PE context TID formats; memory callback ranges; reset after partial decode; and OpenCSD error/fatal response handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cs-etm-decoder/cs-etm-decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cs-etm-decoder/cs-etm-decoder.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/cs-etm-decoder/cs-etm-decoder.h

Purpose: declares CoreSight ETM decoder configuration structures, protocol/operation enums, callback types, and lifecycle/data APIs.

Important APIs/types: defines `cs_etm_mem_cb_type`, trace parameter structs for ETMv3, ETMv4, and ETE, `struct cs_etm_trace_params`, `struct cs_etm_decoder_params`, protocol constants `CS_ETM_PROTO_*`, and `enum cs_etm_decoder_operation`. Declares decoder creation, free, data-block processing, memory callback registration, packet retrieval, reset, and name lookup.

Control flow: callers prepare one trace parameter block per trace source, prepare decoder parameters including operation, packet printer, memory access callback, formatter flags, and caller data, create a decoder, feed AUX data blocks, drain packet queues with `cs_etm_decoder__get_packet`, and reset/free as needed.

State and persistence: decoder objects are opaque; packet queues and ETM queues are external forward-declared types. Trace parameter structures carry hardware register snapshots from AUX metadata.

Dependencies and integration: includes Linux types, OpenCSD interface types, and stdio. Integrated with perf's CS-ETM auxtrace session code and packet queue processing.

Risks: enum protocol values intentionally start at 1 to align with OpenCSD, so changing numbering would break ABI assumptions. Callback signatures must match OpenCSD memory space semantics and perf ETM queue context. Callers must supply coherent register sets for the selected protocol.

Test signals: compile with OpenCSD headers, create decoders for each protocol, feed data in chunks, register memory callbacks, reset, and verify packet retrieval semantics for empty and non-empty queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cs-etm-decoder/cs-etm-decoder.h -->
