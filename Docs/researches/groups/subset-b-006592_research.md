# subset-b-006592 research

Grouped research for Linux kernel LKMM litmus helper scripts, MM diagnostic tools, and SunRPC XDR generator modules under the Ceph client source tree. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/memory-model/scripts/cmplitmushist.sh -->
# sources/distributed-fs/ceph-client/tools/memory-model/scripts/cmplitmushist.sh

Purpose: Compares historical LKMM/herd7 litmus outputs against freshly generated `.out.new` files and reports whether the observable verification result changed.

Important APIs and functions: `comparetest oldpath newpath` is the only functional API. It detects unknown LKMM macros, timeout status 124, exact output equality after filtering volatile timing/resource lines, identical `Observation` lines, identical `Observation` result classes, and final result changes. The main body builds a temporary shell script from paths read on stdin and executes that generated script.

Control flow: The script creates a private `/tmp/cmplitmushist.sh.$$` directory, defines result counters, transforms each input pathname into `comparetest path.out path.out.new`, sources the generated script, prints per-test output, then emits a stderr summary. It exits nonzero only when a semantic result changed.

State and persistence behavior: State is transient shell counters and temporary comparison files. Persistent inputs and outputs are the caller-provided `.out` and `.out.new` files; this script does not mutate them.

Dependencies and integration points: It is part of the memory-model litmus history workflow, consuming outputs produced by `runlitmushist.sh`/`newlitmushist.sh`. It depends on POSIX shell tools `grep`, `sed`, `awk`, `cmp`, and `expr`.

Risks: The generated shell script is sourced, so unusual filenames from stdin can become shell syntax. Matching is text-pattern based and assumes herd7 output conventions. Timing/resource filtering is intentionally narrow and may not remove all nondeterministic lines.

Test signals: Feed known old/new pairs covering exact matches, count-only matches, Always/Sometimes/Never-only matches, missing observations, unknown macros, timeouts, and changed observations; assert summary counters and exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/memory-model/scripts/cmplitmushist.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/memory-model/scripts/hwfnseg.sh -->
# sources/distributed-fs/ceph-client/tools/memory-model/scripts/hwfnseg.sh

Purpose: Computes the hardware filename suffix used by LKMM history scripts when a hardware architecture map is selected.

Important APIs and functions: This is a sourced shell fragment, not a standalone command API. It sets one variable, `hwfnseg`, to the empty string for normal LKMM runs or `.$LKMM_HW_MAP_FILE` for hardware runs.

Control flow: A single `test -z "$LKMM_HW_MAP_FILE"` branch selects between empty suffix and architecture suffix.

State and persistence behavior: It mutates only the caller shell's `hwfnseg` variable and writes no files.

Dependencies and integration points: `runlitmushist.sh` sources it and passes the suffix to `runtest` so observation checks use either `.litmus.out` or `.litmus.<HW>.out`. It relies on `parseargs.sh` having exported `LKMM_HW_MAP_FILE`.

Risks: Because it is sourced, callers must avoid name collisions with `hwfnseg`. No validation is done here; malformed architecture names must be rejected earlier.

Test signals: Source it with `LKMM_HW_MAP_FILE` unset and set to `AArch64`, then verify `hwfnseg` is empty and `.AArch64` respectively.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/memory-model/scripts/hwfnseg.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/memory-model/scripts/initlitmushist.sh -->
# sources/distributed-fs/ceph-client/tools/memory-model/scripts/initlitmushist.sh

Purpose: Initializes a litmus history run by obtaining the external litmus-test corpus if needed, selecting C-language litmus tests up to a process-count threshold, and running herd7 on the selected set without judging results.

Important APIs and functions: The script sources `scripts/parseargs.sh` for `LKMM_DESTDIR`, `LKMM_PROCS`, jobs, timeout, hardware options, and herd options. It uses `mselect7 -arch C` to select C tests and `scripts/runlitmushist.sh` to execute them.

Control flow: After argument parsing it creates a temporary directory, ensures a `litmus` checkout exists by cloning `https://github.com/paulmckrcu/litmus` if absent, mirrors new litmus directories into `LKMM_DESTDIR` when a separate destination is used, creates a list of C tests, filters out tests containing process `P${LKMM_PROCS}` or above, then pipes that list into the parallel runner.

State and persistence behavior: It can persist a cloned `litmus` repository and `.litmus.out` result files under `LKMM_DESTDIR`. Temporary lists are deleted by trap.

Dependencies and integration points: Requires git, herdtools commands (`mselect7`, later herd7 through `runlitmushist.sh`), and the local LKMM scripts. It is the baseline-producing counterpart to `newlitmushist.sh`.

Risks: The clone path is unauthenticated network state and checkout is `origin/master`, so results depend on current upstream content. Process-count filtering via `grep -L "^P${LKMM_PROCS}"` is a convention rather than a parser. Runs can be CPU-expensive and timeout-heavy.

Test signals: Run with a small `--procs` value and temporary `--destdir`; verify directory mirroring, list construction, runner invocation, and no judged `!!!` output is required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/memory-model/scripts/initlitmushist.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/memory-model/scripts/judgelitmus.sh -->
# sources/distributed-fs/ceph-client/tools/memory-model/scripts/judgelitmus.sh

Purpose: Judges one litmus output against the expected `Result:` comment or, for hardware runs, against generated LKMM output.

Important APIs and functions: The command API is `judgelitmus.sh file.litmus`. It consumes environment variables `LKMM_DESTDIR` and optionally `LKMM_HW_MAP_FILE`. It parses `Result:` and `DATARACE` annotations, checks output files for `Observation`, unknown macros, timeout status 124, and verification errors, and appends `!!!` or forgiven markers to output files.

Control flow: The script validates the litmus source, determines output filename (`.out` or `.<HW>.out`), determines the expected outcome, reconciles predicted and modeled data-race markers, prints the observation, handles missing observation categories, then compares deadlock and Always/Sometimes/Never outcomes. Hardware Sometimes mismatches and modeled data-race outcome mismatches are forgiven.

State and persistence behavior: It reads source and result files and may append diagnostic lines to the result file. Exit status encodes success, expected mismatch, data-race inconsistency, unknown primitive, timeout, or generic verification failure.

Dependencies and integration points: Used after `runlitmus.sh`/`runlitmushist.sh` to validate results. It depends on herd7 output conventions and LKMM test comments.

Risks: Pattern matching can misclassify nonstandard comments or output. Appending diagnostics makes the output file stateful, so repeated runs can preserve old markers. Hardware data-race modeling is explicitly incomplete.

Test signals: Check litmus files with matching and mismatching `Result:`, `DATARACE`, `DEADLOCK`, unknown macro, timeout, and hardware `Sometimes` cases; verify exit codes and appended diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/memory-model/scripts/judgelitmus.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/memory-model/scripts/newlitmushist.sh -->
# sources/distributed-fs/ceph-client/tools/memory-model/scripts/newlitmushist.sh

Purpose: Runs only new or modified C-language litmus tests relative to an existing history directory, refreshing `.litmus.out` files without judging them.

Important APIs and functions: Like `initlitmushist.sh`, it sources `parseargs.sh`, uses `mselect7 -arch C`, process-count filtering, and delegates execution to `scripts/runlitmushist.sh`.

Control flow: It requires an existing `litmus` directory, mirrors litmus subdirectories into `LKMM_DESTDIR`, derives already-run tests from existing `.litmus.out` files, builds the full eligible test list, computes tests present in one set but not both with `sort | uniq -u`, detects source files newer than their output via a generated shell script, merges new and newer tests, and runs that list.

State and persistence behavior: Persistent state is the existing `litmus` tree and `LKMM_DESTDIR` output tree. It creates temporary list files and rewrites only selected output files through the runner.

Dependencies and integration points: Designed as the incremental partner to `initlitmushist.sh`; requires the same herdtools and local scripts.

Risks: Deletions are explicitly not handled. `uniq -u` set logic depends on exact path normalization. Filename shell generation for mtime checks assumes litmus paths are shell-safe.

Test signals: In a fixture destination, cover absent `litmus`, already-run unchanged tests, missing output tests, and source-newer-than-output tests; verify only required paths reach `runlitmushist.sh`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/memory-model/scripts/newlitmushist.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/memory-model/scripts/parseargs.sh -->
# sources/distributed-fs/ceph-client/tools/memory-model/scripts/parseargs.sh

Purpose: Provides common argument parsing and default `LKMM_*` environment setup for Linux Kernel Memory Model scripts.

Important APIs and functions: Intended to be sourced. `initparam name default` sets and exports defaults while preserving caller-provided values and recording `<name>_DEF`. `usagehelp`, `usage`, and `checkarg` implement shared diagnostics. Supported options include `--destdir`, `--herdopts`, `--hw`, `--jobs`/`-j`, `--procs`, and `--timeout`.

Control flow: The script initializes defaults, loops through argv, validates option arguments with regex allow/deny patterns, creates and permission-checks `LKMM_DESTDIR`, exports parsed variables, derives `LKMM_TIMEOUT_CMD`, and removes its temporary directory.

State and persistence behavior: It mutates the caller shell environment and can create the destination directory. Temporary shell snippets under `/tmp/parseargs.sh.$$` are removed at completion.

Dependencies and integration points: Sourced by init/new/run scripts; downstream scripts rely on exported `LKMM_DESTDIR`, `LKMM_HERD_OPTIONS`, `LKMM_HW_MAP_FILE`, `LKMM_JOBS`, `LKMM_PROCS`, `LKMM_TIMEOUT`, and `LKMM_TIMEOUT_CMD`.

Risks: It uses generated shell code in `initparam`. Some paths and options are only regex-validated, not shell-escaped. `mkdir $LKMM_DESTDIR` is unquoted in one spot, making whitespace paths risky.

Test signals: Source it with defaults and each option, including invalid numbers/timeouts and existing or new destination directories; assert exported variables and usage failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/memory-model/scripts/parseargs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/memory-model/scripts/runlitmus.sh -->
# sources/distributed-fs/ceph-client/tools/memory-model/scripts/runlitmus.sh

Purpose: Runs herd7 for a single litmus test, optionally translating C litmus to hardware assembly before hardware-model verification.

Important APIs and functions: Command API is `runlitmus.sh file.litmus`. It expects `LKMM_DESTDIR`, `LKMM_HERD_OPTIONS`, `LKMM_TIMEOUT_CMD`, and optional `LKMM_HW_MAP_FILE`/`LKMM_HW_CAT_FILE`. It calls `herd7`, `gen_theme7`, `jingle7`, and `scripts/simpletest.sh`.

Control flow: It validates the input file. For LKMM mode, or for hardware mode without a pre-existing LKMM output, it writes herd options into `litmus.out`, runs timed herd7, and exits in pure LKMM mode. Hardware mode then builds map/theme filenames, rejects complex synchronization tests, creates a theme, generates architecture litmus with jingle7, copies generation errors when no tests are produced, then runs herd7 on generated hardware litmus.

State and persistence behavior: Persists `.out`, hardware `.litmus.<HW>`, `.err`, and `.out` artifacts under `LKMM_DESTDIR`. Temporary theme and stderr files are removed by trap.

Dependencies and integration points: Called by `runlitmushist.sh`; hardware result filenames are coordinated with `hwfnseg.sh` and `judgelitmus.sh`.

Risks: Hardware path depends on external map/call/cat files. It skips complex synchronization for hardware rather than modeling it. Destination paths are only partly quoted. `jingle7` failure detection depends on a specific stderr phrase.

Test signals: Mock herd7/gen_theme7/jingle7 to cover LKMM success/failure, hardware simple/complex tests, generated-zero-tests, timeout propagation, and file naming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/memory-model/scripts/runlitmus.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/memory-model/scripts/runlitmushist.sh -->
# sources/distributed-fs/ceph-client/tools/memory-model/scripts/runlitmushist.sh

Purpose: Runs many litmus tests in parallel using the common LKMM environment and reports herd7 execution failures.

Important APIs and functions: Reads litmus file paths on stdin. It sources `hwfnseg.sh` and generates per-worker shell scripts containing `runtest`, which invokes `scripts/runlitmus.sh` and checks for `Observation` lines in the expected output file.

Control flow: After verifying the `litmus` directory, it creates one worker script per `LKMM_JOBS`. An awk pipeline estimates each test's process count from the last `P[0-9]+(` line, sorts by count, then distributes tests round-robin across worker scripts. Hardware runs skip tests rejected by `simpletest.sh`. It launches all worker scripts in background, waits, concatenates outputs, and summarizes `!!!` failures.

State and persistence behavior: Test result files are written by `runlitmus.sh`; this wrapper uses only temporary worker scripts and logs.

Dependencies and integration points: Used by init/new history scripts. Depends on bash arrays/arithmetic, awk, sort, grep, and the LKMM runner scripts.

Risks: Load balancing is heuristic. Generated shell lines assume safe filenames. Failure detection is tied to `!!!` marker text. In hardware mode, skipped complex tests may be invisible unless the caller separately tracks selection.

Test signals: Provide synthetic stdin with varying process counts and mock `runlitmus.sh`; verify distribution, observation checks, hardware simple filtering, failure summary, and exit code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/memory-model/scripts/runlitmushist.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/memory-model/scripts/simpletest.sh -->
# sources/distributed-fs/ceph-client/tools/memory-model/scripts/simpletest.sh

Purpose: Classifies a litmus test as simple enough for hardware translation by rejecting tests that use locking, RCU, or SRCU primitives.

Important APIs and functions: Command API is `simpletest.sh file.litmus`. It constructs one extended grep pattern covering `spin_lock`, `spin_unlock`, `spin_trylock`, `spin_is_locked`, RCU read-side and synchronize APIs, and SRCU variants.

Control flow: The script validates readability, runs grep for excluded primitives anchored after optional whitespace, exits 255 on a match, and exits 0 otherwise.

State and persistence behavior: Read-only; no persistent state.

Dependencies and integration points: Used by `runlitmus.sh` and `runlitmushist.sh` in hardware mode to avoid unsupported synchronization constructs.

Risks: It is lexical, so comments or unusual formatting can cause false positives or false negatives. New unsupported primitives require manually extending the pattern.

Test signals: Feed simple memory-access litmus files, lock/RCU/SRCU examples, commented primitives, and unreadable paths; verify exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/memory-model/scripts/simpletest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/mm/Makefile -->
# sources/distributed-fs/ceph-client/tools/mm/Makefile

Purpose: Builds and installs Linux VM/MM user-space tools in `tools/mm`.

Important APIs and targets: `BUILD_TARGETS` are `page-types`, `slabinfo`, `page_owner_sort`, and `thp_swap_allocator_test`; `INSTALL_TARGETS` additionally includes the script `thpmaps`. The generic `%: %.c` rule compiles C tools. `$(LIBS)` builds `../lib/api/libapi.a`. Targets are `all`, `clean`, and `install`.

Control flow: The default target builds all C tools after the shared libapi dependency. `clean` removes binaries and cleans libapi. `install` creates `$(DESTDIR)$(sbindir)` and installs binaries/scripts with mode 755.

State and persistence behavior: Produces local tool binaries and may install them under `/usr/sbin` or a supplied destination. It does not track generated dependency files.

Dependencies and integration points: Includes `../scripts/Makefile.include`, adds `-I../lib/`, links libapi and pthreads, and fits the kernel tools build/install conventions.

Risks: Every C target links pthread even when not needed. The pattern rule assumes target and source basename match. Installing `thpmaps` assumes script executable semantics.

Test signals: Run `make -C tools/mm`, `make clean`, and `make DESTDIR=<tmp> install`; verify expected binaries and installed script.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/mm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/mm/page-types.c -->
# sources/distributed-fs/ceph-client/tools/mm/page-types.c

Purpose: Inspects kernel page flags from `/proc/kpageflags`, optionally through process pagemap or file page-cache walks, and can mark pages idle or inject/forget hwpoison.

Important APIs and types: Global option state drives the tool. Key routines include `do_u64_read`, `pagemap_read`, `kpageflags_read`, `expand_overloaded_flags`, `well_known_flags`, `bit_mask_ok`, `add_page`, `walk_pfn`, `walk_vma`, `walk_task`, `walk_page_cache`, `parse_bits_mask`, and `show_summary`. Page flag names come from `kernel-page-flags.h` plus tool-local overloaded/raw bits.

Control flow: `main` parses options for raw mode, pid/file/address/cgroup filters, list modes, idle marking, hwpoison, and alternate kpageflags file. It opens required proc/sys/debugfs files, walks either PFN ranges or file cache/process mappings, accumulates page counts in a hash table keyed by normalized flags, optionally lists ranges or individual pages, then prints a summary.

State and persistence behavior: Most state is in global counters and hash tables. It can persist side effects by writing page-idle bitmap or debugfs hwpoison controls. File-cache walking mmaps files and touches cached pages to populate PTEs.

Dependencies and integration points: Uses Linux procfs, sysfs page-idle bitmap, debugfs hwpoison, cgroup inode IDs, `api/fs/fs.h` debugfs helpers, and UAPI page flag definitions.

Risks: Requires privileges for many files. Kernel ABI bit meanings and overloaded flags are version-sensitive. Fixed limits (`MAX_VMAS`, filter counts, hash size) can be exceeded. The file walker intentionally handles SIGBUS but still touches live files.

Test signals: Validate `--describe`, synthetic alternate `--kpageflags`, address-range filters, pid walks, file-cache walks, cgroup filtering, list/mapcount output, and privileged idle/hwpoison paths on controlled systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/mm/page-types.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/mm/page_owner_sort.c -->
# sources/distributed-fs/ceph-client/tools/mm/page_owner_sort.c

Purpose: Sorts and culls `/sys/kernel/debug/page_owner` dumps so repeated allocation records can be grouped and ordered by count, memory, process, command, stack, allocator, or timestamp.

Important APIs and types: `struct block_list` stores one parsed page-owner block plus parsed pid/tgid/comm/order/timestamp/allocator. `struct filter_condition` and `struct sort_condition` hold CLI state. Key functions are `read_block`, regex helpers, `get_page_num`, `get_pid`, `get_tgid`, `get_comm`, `get_allocator`, `parse_cull_args`, `parse_sort_args`, `add_list`, and comparator functions.

Control flow: `main` parses short and long options, configures default or custom sort, opens input/output, compiles regexes for page-owner fields, estimates capacity from input size, reads blocks separated by blank lines while carrying `PFN` metadata in `ext_buf`, filters records, sorts by cull key, coalesces adjacent equivalent records, sorts by requested output order, and writes either full records or culled summaries.

State and persistence behavior: All parsed records are held in memory. Output is a new sorted text file. The input page-owner dump is read-only.

Dependencies and integration points: Consumes the exact text format produced by kernel page_owner debugfs and references Documentation/mm/page_owner.rst conventions.

Risks: Capacity is estimated as `st_size / 100`, which can underallocate for small or unusual records. Regex assumptions can fail on format changes. `get_allocator` walks backward from `__vmalloc_node_range` and can be fragile. Some allocations are not freed individually before exit.

Test signals: Use fixture dumps with repeated stacks, different PIDs/TGIDs/comms, CMA/slab/vmalloc markers, custom `--cull` and `--sort`, malformed fields with `-d`, and large inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/mm/page_owner_sort.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/mm/show_page_info.py -->
# sources/distributed-fs/ceph-client/tools/mm/show_page_info.py

Purpose: A drgn-based diagnostic script that prints detailed kernel `struct page` state for a process virtual address.

Important APIs and functions: `format_page_data` emits a raw word dump of the `struct page`; `get_memcg_info` decodes `page.memcg_data` into cgroup name/path; `show_page_state` prints flags, PFN, physical/virtual addresses, refcount, mapcount, folio index, mapping, VMA, slab/compound status; `main` parses `pid` and hex `vaddr`, finds the task, and calls `follow_page`.

Control flow: The script validates the virtual address, resolves `task.mm`, obtains the page for the virtual address, and prints structured fields with guarded exception handling around fragile kernel memory reads.

State and persistence behavior: Read-only against a live kernel or crash dump through drgn. No files are written.

Dependencies and integration points: Requires drgn runtime globals such as `prog`, drgn Linux helpers for tasks, mm, cgroups, and page flags, plus kernel layout constants like `MEMCG_DATA_OBJEXTS`.

Risks: Kernel field names are version-sensitive (`__folio_index`, `memcg_data`, counters). Access can fault for invalid tasks, unmapped addresses, or unavailable debug info. The reported anon/file classification checks low bit of `mapping`, which depends on kernel encoding.

Test signals: Run against known anonymous, file-backed, slab, compound head/tail, unmapped, and invalid PID/address cases on kernels with matching debug info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/mm/show_page_info.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/mm/slabinfo-gnuplot.sh -->
# sources/distributed-fs/ceph-client/tools/mm/slabinfo-gnuplot.sh

Purpose: Converts repeated `slabinfo -X` samples into gnuplot-friendly intermediate files and PNG graphs for slab totals, loss, and size trends.

Important APIs and functions: `do_preprocess` extracts top slab-by-loss, slab-by-size, and total memory/loss series. `do_slabs_plotting` plots stacked size/loss bars for one preprocessed slab file. `do_totals_plotting` overlays memory usage/loss time series for one or more totals files. `parse_opts` selects preprocess, totals, or slabs mode and image/range options.

Control flow: Options set mode, size, and sample range. Preprocess mode loops over raw slabinfo samples and creates `basename-slabs-by-loss`, `basename-slabs-by-size`, and `basename-totals`, then plots each. Plot modes consume already-preprocessed files directly.

State and persistence behavior: Writes intermediate text files and PNGs in the current directory. It does not modify source sample files.

Dependencies and integration points: Expects output format from `slabinfo -X`; relies on bash arrays, grep, awk, wc, basename, and `gnuplot`.

Risks: Parsing is tightly coupled to headings and column positions. Backtick command substitutions around pipelines are unnecessary and may obscure errors. Output filenames are derived from basenames and can collide. Optional getopts declarations use `r::`/`s::`, so missing argument handling is shell/getopts-dependent.

Test signals: Use fixture `slabinfo -X` samples with multiple records, range and size options, totals comparison, empty files, and absent gnuplot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/mm/slabinfo-gnuplot.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/mm/slabinfo.c -->
# sources/distributed-fs/ceph-client/tools/mm/slabinfo.c

Purpose: Reports and optionally manipulates SLUB slab cache state exposed through `/sys/kernel/slab` or `/sys/slab`, with detailed totals, sorting, NUMA, activity, debug, validation, and shrink modes.

Important APIs and types: `struct slabinfo` mirrors many slab sysfs attributes, while `struct aliasinfo` maps symlink aliases to target slabs. Key routines include `read_slab_dir`, `link_slabs`, `rename_slabs`, `slabcache`, `report`, `totals`, `xtotals`, `slab_numa`, `show_tracking`, `slab_stats`, `slab_debug`, `slab_validate`, `slab_shrink`, and `sort_slabs`.

Control flow: `main` parses display/action/sort/debug options and an optional regex, reads all matching slab directories and aliases, then selects alias display, extended totals, simple totals, or per-slab output/action. Reading gathers sysfs attributes including object counts, NUMA lists, debug flags, and allocator counters. Some modes write to attributes such as `validate`, `shrink`, `sanity_checks`, `red_zone`, `poison`, `store_user`, and `trace`.

State and persistence behavior: Reporting is in-memory and stdout-only, but validation, shrinking, and debug toggles persist by writing kernel sysfs controls. Current working directory is changed into the slab sysfs root.

Dependencies and integration points: Consumes SLUB sysfs/debugfs layouts and optional `/sys/kernel/debug/slab/*` trace files. `slabinfo-gnuplot.sh` expects `-X` extended totals text.

Risks: Global fixed arrays cap slabs, aliases, and NUMA nodes. Sysfs attributes vary by kernel configuration. Debug toggles require empty slabs and privileges. The code has historical style and limited cleanup because process exit reclaims memory.

Test signals: Exercise default list, regex filtering, aliases, totals/extended totals, NUMA, activity, top-N, debug toggle failure on nonempty slabs, validate/shrink on test systems, and gnuplot preprocessing compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/mm/slabinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/mm/thp_swap_allocator_test.c -->
# sources/distributed-fs/ceph-client/tools/mm/thp_swap_allocator_test.c

Purpose: Stress test for multi-size THP swap-out allocation, checking that 64KB transparent huge pages obtain whole swap slots instead of falling back to split swap-out.

Important APIs and functions: `aligned_alloc_mem` wraps `posix_memalign`; `random_madvise_dontneed` randomly discards aligned regions then refaults them; `random_swapin` randomly touches regions; `read_stat` reads THP `swpout` and `swpout_fallback` sysfs counters. `main` implements `-s` for a small-folio comparison area and `-a` for aligned swap-in.

Control flow: The program allocates 60MB 64KB-aligned mTHP memory, marks it `MADV_HUGEPAGE`, optionally allocates a 4MB `MADV_NOHUGEPAGE` region, warms and pages out memory, then performs 100 iterations of reading counters, random swap-in/refault, optional small-folio activity, `MADV_PAGEOUT`, final counter read, and fallback-percentage print.

State and persistence behavior: Process memory and kernel swap/THP counters are the live state. The program does not write files, but it relies on externally configured zram/swap and THP sysfs state.

Dependencies and integration points: Uses Linux `madvise` flags and `/sys/kernel/mm/transparent_hugepage/hugepages-64kB/stats/*`. Intended for MM regression testing.

Risks: `read_stat` returns 0 on errors, which can hide missing sysfs counters. Fallback percentage divides by zero if no swpout counters change. Randomness is not seeded. Test assumptions depend on 64KB mTHP support and swap setup.

Test signals: Run with documented zram/THP setup, both with and without `-s` and `-a`; verify fallback remains near 0 percent and counter deltas are nonzero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/mm/thp_swap_allocator_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/mm/thpmaps -->
# sources/distributed-fs/ceph-client/tools/mm/thpmaps

Purpose: Python utility that prints smaps-like transparent hugepage and contiguous-block mapping statistics per VMA, per process/cgroup, or as a rollup.

Important APIs and types: `BinArrayFile` abstracts binary array reads from pagemap and kpageflags using `preadv`; `PageMap` and `KPageFlags` specialize it. `VMAList` parses `/proc/<pid>/smaps` into `VMA` namedtuples. `thp_parse`, `cont_parse`, and `vma_parse` derive THP/contiguous mapping statistics using numpy arrays. `do_main` selects pids and output mode.

Control flow: Module import reads base page size and PMD size from sysfs. CLI parsing validates `--pid`, `--cgroup`, `--rollup`, `--cont`, `--inc-smaps`, `--inc-empty`, and `--periodic`. Each VMA with RSS is mapped through pagemap to PFNs, present THP pages are filtered by kpageflags, contiguous ranges are identified, PMD-mapped pages from smaps are subtracted to avoid double counting, and stats are printed.

State and persistence behavior: Read-only against `/proc`, `/proc/kpageflags`, cgroup `cgroup.procs`, and THP sysfs. Periodic mode repeats with no persisted cache.

Dependencies and integration points: Requires Python 3, numpy, root privileges for pagemap/kpageflags, and Linux THP sysfs/procfs formats.

Risks: Races with process exit and VMA changes are partly handled but can skew counts. PFN visibility is privilege-dependent. Numpy operations assume same-sized arrays and power-of-two cont sizes. Import-time sysfs read fails on systems without THP hpage PMD size.

Test signals: Run on self, selected pids, cgroup subtrees, rollup, `--cont 64K`, `--inc-smaps`, periodic mode, and non-root error cases; compare totals against smaps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/mm/thpmaps -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/extract.sh -->
# sources/distributed-fs/ceph-client/tools/net/sunrpc/extract.sh

Purpose: Extracts embedded XDR protocol specification lines from RFC text.

Important APIs and functions: It is a stdin-to-stdout filter. It selects lines beginning with optional spaces followed by `///`, strips the marker and following space, and preserves empty marker lines.

Control flow: A single `grep '^ *///' | sed ... | sed ...` pipeline implements extraction.

State and persistence behavior: Stateless filter; no files are read except stdin or written except stdout.

Dependencies and integration points: Intended to produce `.x` XDR files for the SunRPC XDR generator from RFC documents using the convention described in RFC 8166.

Risks: Only lines using exactly the `///` convention are extracted. Leading spaces before markers are tolerated, but other comment styles are ignored.

Test signals: Feed RFC excerpts with `/// declaration`, `///` empty lines, indented markers, and non-marker text; verify only specification lines remain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/extract.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/__init__.py -->
# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/__init__.py

Purpose: Marks the `xdrgen` directory as a Python package for documentation tooling.

Important APIs and functions: No runtime APIs are defined; the file contains only SPDX and a note for `sphinx-apidoc`.

Control flow: None.

State and persistence behavior: No state.

Dependencies and integration points: Allows package discovery/import documentation for sibling modules such as `xdr_ast`, `xdr_parse`, `generators`, and `subcmds`.

Risks: None functionally, though package import behavior may depend on how the tool is executed because the generator modules use top-level imports.

Test signals: Import `xdrgen` or run sphinx-apidoc over the directory and verify package discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/__init__.py -->
# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/__init__.py

Purpose: Defines shared generator infrastructure for the XDR-to-C code generator.

Important APIs and functions: `create_jinja2_environment(language, xdr_type)` locates templates and installs globals (`annotate`, `public_apis`, `pass_by_reference`, `structs`). `get_jinja2_template` loads typed templates. `find_xdr_program_name`, `header_guard_infix`, and `kernel_c_type` provide naming and C type mapping. `Boilerplate` and `SourceGenerator` are abstract base classes for concrete emitters.

Control flow: Language selection currently supports only `C`; unsupported languages raise `NotImplementedError`. Concrete generators instantiate environments and render templates to stdout.

State and persistence behavior: No file writes here. It reads template files via Jinja2 and observes global AST/parser side-channel state.

Dependencies and integration points: Used by every generator module and by subcommands. Depends on Jinja2, pathlib, `xdr_ast`, and `xdr_parse`.

Risks: Imports are absolute/top-level, so execution path must include the xdrgen directory. The environment reads global state at creation; repeated parses in one process can inherit stale AST globals unless reset externally.

Test signals: Instantiate environments for each xdr type, render known templates, verify type mapping for builtins and defined types, and assert unsupported languages fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/constant.py -->
# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/constant.py

Purpose: Emits C header definitions for XDR constants.

Important APIs and functions: `XdrConstantGenerator` extends `SourceGenerator`. Its `emit_definition(node)` renders the `constants/definition.j2` template with `node.name` and `node.value`.

Control flow: Construction creates a C constants template environment and stores peer. Only definition emission is implemented; declarations, encoders, decoders, and maxsize are inherited unsupported operations.

State and persistence behavior: Stateless apart from the template environment. Output is printed to stdout.

Dependencies and integration points: Used by `subcmds/definitions.py` for `_XdrConstant` AST nodes. Relies on constants parsed and stored by `xdr_ast`.

Risks: No validation is performed at emit time; malformed values must be rejected by parsing/AST transformation. Peer is stored but unused.

Test signals: Parse a specification with `const FOO = 3;` and verify generated header definition matches the template.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/constant.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/enum.py -->
# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/enum.py

Purpose: Generates C definitions, optional public declarations, XDR encoders/decoders, and maxsize macros for XDR enum types.

Important APIs and functions: `XdrEnumGenerator` implements `emit_declaration`, `emit_definition`, `emit_decoder`, `emit_encoder`, and `emit_maxsize`. It consults `public_apis`, `big_endian`, `get_header_name`, and `get_xdr_enum_validation`.

Control flow: Public enums get declaration templates. Definitions emit open, one enumerator per AST enumerator, and either normal or big-endian close templates. Decoder and encoder templates switch for big-endian enums. Maxsize emits a macro named `<HEADER>_<enum>_sz` with symbolic width.

State and persistence behavior: Stateless output to stdout, reading global pragma state.

Dependencies and integration points: Called by declaration, definition, and source subcommands for `_XdrEnum` nodes. Template selection ties directly to C kernel XDR support routines.

Risks: Global `big_endian` and `public_apis` are process-wide. Header name defaults to `none`, which affects macro names if the pragma is absent. Enum validation can be disabled by source subcommand options.

Test signals: Generate normal, public, big-endian, and validation-disabled enum specs; compile generated C snippets where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/enum.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/header_bottom.py -->
# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/header_bottom.py

Purpose: Emits closing boilerplate for generated XDR declaration and definition headers.

Important APIs and functions: `XdrHeaderBottomGenerator.emit_declaration` and `.emit_definition` render bottom header templates with the header guard infix derived from the source filename. `.emit_source` is intentionally a no-op.

Control flow: Construction creates a C `header_bottom` template environment. Each header method loads the proper template subdirectory and prints rendered guard closure.

State and persistence behavior: Stateless stdout generation.

Dependencies and integration points: Used at the end of `subcmds/declarations.py` and `subcmds/definitions.py` after type-specific emission.

Risks: Header guard infix is based on filename stem only, so two specs with the same stem in different directories could collide in generated headers.

Test signals: Generate declaration and definition headers for sample filenames and verify guard closure matches the top generator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/header_bottom.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/header_top.py -->
# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/header_top.py

Purpose: Emits opening boilerplate for generated XDR declaration and definition headers.

Important APIs and functions: `XdrHeaderTopGenerator.emit_declaration` and `.emit_definition` render header templates with guard infix, filename, and source file modification time. `.emit_source` is a no-op.

Control flow: Construction creates a C `header_top` template environment. Emission calls `os.path.getmtime(filename)`, formats it with `time.ctime`, and prints the rendered template.

State and persistence behavior: Reads source file metadata but writes only stdout.

Dependencies and integration points: Used before type-specific emission by declaration and definition subcommands.

Risks: Generated output is time-dependent because it embeds source mtime, which can reduce reproducibility. Guard infix uses only the filename stem.

Test signals: Generate headers for a fixture file with known mtime and verify guard names and comment metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/header_top.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/passthru.py -->
# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/passthru.py

Purpose: Emits pass-through content from XDR specifications into generated headers or source files.

Important APIs and functions: `XdrPassthruGenerator.emit_definition` renders a header definition template, while `emit_decoder` renders a source template. Both pass `node.content` verbatim through the relevant template.

Control flow: Construction creates a C `passthru` environment. Source subcommands use `emit_decoder` for pass-through blocks because pass-through content is inserted before generated decode/encode functions.

State and persistence behavior: Stateless stdout output.

Dependencies and integration points: `_XdrPassthru` nodes are produced by `xdr_ast` from grammar pass-through lines and consecutive pass-through nodes are merged before generation.

Risks: Pass-through content is intentionally raw; invalid C or unsafe declarations are not validated by the generator.

Test signals: Parse adjacent pass-through lines and verify they are merged and emitted with newlines preserved in definitions and source output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/passthru.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/pointer.py -->
# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/pointer.py

Purpose: Generates C structures and XDR encode/decode/maxsize logic for self-referential optional-data structs represented as pointer-like XDR types.

Important APIs and functions: Helper functions emit declarations, member definitions, decoders, encoders, and maxsize macros. `XdrPointerGenerator` wraps those helpers for `_XdrPointer` AST nodes. Member emitters handle basic types, opaque data, strings, fixed/variable arrays, and optional data.

Control flow: Definitions open a struct-like template, emit all fields except the final optional self-reference sentinel, then close. Decoders and encoders similarly skip the final optional-data field after emitting a leading presence bool through pointer templates. Public declarations are emitted only when the pointer type is in `public_apis`.

State and persistence behavior: Stateless stdout generation, reading global header/public state.

Dependencies and integration points: `_XdrPointer` nodes are created by `xdr_ast.ParseToAst.struct` when the last field is optional data of the same type. Templates use `kernel_c_type`, `classifier`, `maxsize`, and `symbolic_width` values.

Risks: Skipping `node.fields[0:-1]` assumes the AST pointer invariant is correct. Optional-data typedefs are not generally implemented elsewhere. Template coverage is type-specific and new declaration variants require updates in multiple helper branches.

Test signals: Generate a recursive linked-list-like XDR struct, verify no final self field is emitted as a normal member, and compile generated encoder/decoder stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/pointer.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/program.py -->
# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/program.py

Purpose: Generates C RPC program/procedure constants plus procedure argument/result declarations and peer-specific encoder/decoder wrappers.

Important APIs and functions: Helpers emit version procedure definitions, declarations for unique argument/result types, server argument decoders, client result decoders, client argument encoders, server result encoders, and max-argument-size macros. `XdrProgramGenerator` dispatches by peer.

Control flow: Program names are lowercased with `_program`/`_prog` suffixes removed. Definitions emit procedure numbers for each version and the program number. Declarations deduplicate argument and result type names with dictionaries. Source generation switches on `peer`: server decodes arguments and encodes results; client encodes arguments and decodes results. `emit_maxsize` selects the largest non-void, non-excluded argument width.

State and persistence behavior: Stateless stdout output, reading global `excluded_apis`, `max_widths`, and header name.

Dependencies and integration points: Used for `_RpcProgram` nodes by all generator subcommands. Integrates AST procedure metadata with C template naming conventions.

Risks: Exclusion is by procedure name only and global. Missing `max_widths` entries silently skip max-args consideration. Client source has a TODO for procedure macros.

Test signals: Generate multi-version RPC specs with duplicate argument/result types, excluded procedures, void arguments, and varying max widths; verify server/client output differs correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/program.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/source_top.py -->
# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/source_top.py

Purpose: Emits top-of-file boilerplate for generated client or server XDR C source files.

Important APIs and functions: `XdrSourceTopGenerator.emit_source(filename, root)` finds the program/header name, selects the template named for `peer`, and renders program name, source filename, and source mtime.

Control flow: Program name comes from `find_xdr_program_name`, which prefers a header pragma and otherwise derives from the first RPC program definition. Peer selects `server.j2` or `client.j2`.

State and persistence behavior: Reads source file mtime and prints to stdout.

Dependencies and integration points: Used by `subcmds/source.py` before type-specific encoders/decoders. Depends on boilerplate templates and AST program discovery.

Risks: Output is time-dependent. If no RPC program exists and no header pragma is set, generated name falls back to `noprog`.

Test signals: Generate source for specs with header pragma, with program name suffixes, and with no program; verify selected template and name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/source_top.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/struct.py -->
# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/struct.py

Purpose: Generates C declarations, definitions, encoders, decoders, and maxsize macros for XDR struct types.

Important APIs and functions: Helper functions emit struct-level and field-level code for `_XdrBasic`, strings, fixed/variable opaque data, fixed/variable arrays, and optional data. `XdrStructGenerator` exposes the standard `SourceGenerator` methods.

Control flow: Public structs get declaration close templates. Definitions emit open, every field, and close templates. Decoders and encoders emit open templates, per-field code in source order, and close templates. Maxsize joins each field's symbolic width into `<HEADER>_<struct>_sz`.

State and persistence behavior: Stateless stdout output, reading global public/header state.

Dependencies and integration points: Called for `_XdrStruct` nodes by declaration, definition, and source subcommands. Shares much field handling logic with pointer and typedef generators.

Risks: Field support is duplicated across definition/decoder/encoder helpers, so adding a new declaration kind can leave one path incomplete. Template selection depends on each AST field's `template` string.

Test signals: Generate structs containing every supported field kind, public/nonpublic structs, optional data members, and arrays of defined types; compile and inspect maxsize macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/struct.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/typedef.py -->
# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/typedef.py

Purpose: Generates C typedef definitions plus optional public declarations, encoders, decoders, and maxsize macros for XDR typedefs.

Important APIs and functions: `emit_typedef_declaration`, `emit_type_definition`, `emit_typedef_decoder`, `emit_typedef_encoder`, and `emit_typedef_maxsize` handle declaration variants. `XdrTypedefGenerator` invokes them for `_XdrTypedef.declaration`.

Control flow: Public declarations are emitted only for names in `public_apis`. Definitions support basic, string, fixed/variable opaque, fixed/variable array declarations. Encoders and decoders parallel those variants. Optional-data typedefs raise `NotImplementedError`, and void typedefs raise `ValueError`.

State and persistence behavior: Stateless stdout generation, using header/public global state.

Dependencies and integration points: Used by definitions, declarations, and source subcommands after `xdr_ast` computes widths and pass-by-reference metadata.

Risks: Some template renders use `node.spec.type_name` while declarations use `kernel_c_type`, so generated C type spelling differs by context intentionally but must match templates. Optional-data typedef support is absent.

Test signals: Generate typedefs for all supported forms, public and nonpublic, arrays of defined types, and unsupported optional/void cases; verify errors and generated maxsize macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/typedef.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/union.py -->
# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/union.py

Purpose: Generates C structures and XDR encode/decode/maxsize logic for XDR discriminated unions.

Important APIs and functions: Helpers emit declarations, discriminant definitions, case/default arm definitions, decoders, encoders, and maxsize macros. `XdrUnionGenerator` implements the `SourceGenerator` interface. It consults `public_apis`, `big_endian`, and `get_header_name`.

Control flow: Definitions emit an open union wrapper, discriminant field, non-void case/default arms, and close. Decoders and encoders special-case boolean discriminants by emitting an `if` path for the TRUE case; otherwise they emit switch discriminants, all cases, a default block, and close. Big-endian discriminants select alternate case templates.

State and persistence behavior: Stateless stdout output with global pragma inputs.

Dependencies and integration points: Used for `_XdrUnion` AST nodes by subcommands. Supports only basic and string arm payloads in several paths, with assertions enforcing expected AST shapes.

Risks: Boolean union handling only emits the TRUE arm and relies on templates for the false/no-data path. Default handling asserts basic arms in some paths, so richer arm types are unsupported. `symbolic_width` in the AST must define a widest arm.

Test signals: Generate unions with enum, integer, big-endian, and bool discriminants; include void/default/string arms; compile generated code and verify decode switch cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/union.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/subcmds/__init__.py -->
# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/subcmds/__init__.py

Purpose: Marks the `subcmds` directory as a Python package for documentation tooling.

Important APIs and functions: No runtime subcommand registry is defined here.

Control flow: None.

State and persistence behavior: No state.

Dependencies and integration points: Helps sphinx-apidoc/package discovery for `declarations`, `definitions`, `lint`, and `source` modules.

Risks: None directly; actual command dispatch must be implemented elsewhere.

Test signals: Import `subcmds` and verify documentation tools include the package.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/subcmds/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/subcmds/declarations.py -->
# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/subcmds/declarations.py

Purpose: Implements the XDR generator subcommand that emits declaration headers for public XDR APIs and RPC procedure argument/result helpers.

Important APIs and functions: `emit_header_declarations(root, language, peer)` dispatches AST definitions to enum, pointer, typedef, struct, union, and program generators. `subcmd(args)` is the command entry point.

Control flow: The subcommand sets annotation mode, parses the input file with `xdr_parser` and `make_error_handler`, transforms the parse tree into an AST, emits header-top boilerplate, emits declarations for supported AST nodes in source order, emits header-bottom boilerplate, and returns 0 or 1 on parse/semantic errors.

State and persistence behavior: Reads one XDR file and writes generated header text to stdout. It mutates parser global `annotate` and AST globals through transformation.

Dependencies and integration points: Depends on Lark, generator modules, `xdr_ast`, and `xdr_parse`. Intended to be called by a higher-level CLI with `filename`, `language`, `peer`, and `annotate`.

Risks: The dispatch creates a new generator for each definition. Global AST side effects are not reset between invocations in the same process. Unsupported node types are silently skipped.

Test signals: Run on valid specs with public and nonpublic types, RPC programs, parse errors, and undefined types; verify output and return status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/subcmds/declarations.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/subcmds/definitions.py -->
# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/subcmds/definitions.py

Purpose: Implements the XDR generator subcommand that emits definition headers containing constants, type definitions, RPC program numbers, pass-through blocks, and maxsize macros.

Important APIs and functions: `emit_header_definitions` dispatches concrete definitions for constants, enums, pointers, programs, typedefs, structs, unions, and pass-through nodes. `emit_header_maxsize` emits size macros for type/program nodes. `subcmd(args)` handles parsing and output orchestration.

Control flow: The subcommand sets annotation mode, parses and transforms the XDR file, emits top header boilerplate, emits definitions in source order, prints a blank line then maxsize macros, and emits bottom boilerplate. Parse and transform errors return 1 after formatted diagnostics.

State and persistence behavior: Reads the XDR source and prints generated header content to stdout. It updates parser/AST global side-channel state during parsing.

Dependencies and integration points: Complements `declarations.py`; both must agree on header guards and public API handling. Uses pass-through generator only in definition headers.

Risks: Maxsize emission order is a second pass and skips constants/pass-through. Process-global AST state can leak across multiple invocations. Template or unsupported AST failures propagate as exceptions.

Test signals: Generate a mixed spec with constants, typedefs, structs, unions, enums, programs, pragmas, and pass-through text; verify definitions and maxsize macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/subcmds/definitions.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/subcmds/lint.py -->
# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/subcmds/lint.py

Purpose: Provides a syntax and semantic validation subcommand for XDR specifications without emitting code.

Important APIs and functions: `subcmd(args)` parses `args.filename` with `xdr_parser`, reports parse errors with `make_error_handler`, transforms the tree with `transform_parse_tree`, and reports semantic errors with `handle_transform_error`.

Control flow: The command reads the entire source file, parses with Lark, transforms to AST, returns 0 on success, and returns 1 on parse or transform failure.

State and persistence behavior: Read-only with diagnostics to stderr. AST transformation still mutates global metadata such as constants and pragmas in the current Python process.

Dependencies and integration points: Used as a lightweight gate before declaration/definition/source generation. Sets Lark logger to DEBUG for more parser detail.

Risks: Because transform side effects are global, repeated lint calls in one process can affect later generation unless the caller isolates processes or resets state.

Test signals: Lint valid specs, malformed syntax, undefined types, unsupported directives, and duplicate/global-state-sensitive specs; assert return status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/subcmds/lint.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/subcmds/source.py -->
# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/subcmds/source.py

Purpose: Implements the XDR generator subcommand that emits peer-specific C source files with XDR encoders and decoders.

Important APIs and functions: `emit_source_decoder` and `emit_source_encoder` dispatch one AST node to the correct generator. `generate_server_source` emits boilerplate, pass-through source blocks, decoders, then encoders. `generate_client_source` emits boilerplate, pass-through blocks, encoders, then decoders. `subcmd(args)` parses options and source.

Control flow: The command sets annotation and enum-validation modes, parses/transforms the XDR source, then switches on `args.peer`. Server output decodes RPC arguments and encodes results; client output encodes arguments and decodes results. Unsupported peers print a message but still return 0.

State and persistence behavior: Reads XDR input and writes C source text to stdout. It mutates global parser/AST side-channel state during parsing.

Dependencies and integration points: Complements generated declaration/definition headers and uses `XdrSourceTopGenerator` plus type/program generators.

Risks: Unsupported peer handling is not a hard error. Client procedure macro generation is marked TODO. Global state can leak across invocations. Pass-through is emitted before generated functions and can inject arbitrary C.

Test signals: Generate server and client source from the same RPC spec, with pass-through blocks, enum validation enabled/disabled, excluded procedures, and unsupported peer names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/subcmds/source.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/xdr_ast.py -->
# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/xdr_ast.py

Purpose: Defines the XDR abstract syntax tree, semantic side-channel tables, width calculation, pragma handling, and Lark parse-tree transformer for the SunRPC XDR generator.

Important APIs and types: Dataclasses model identifiers, values, constants, built-in/defined type specifiers, declarations, constants, enums, structs, pointer-like recursive structs, typedefs, union cases/defaults, RPC procedures/versions/programs, pragmas, pass-through lines, definitions, and specifications. Global tables include `big_endian`, `excluded_apis`, `header_name`, `public_apis`, `structs`, `pass_by_reference`, `constants`, `symbolic_widths`, and `max_widths`. `ParseToAst` transforms grammar productions. `transform_parse_tree` merges adjacent pass-through blocks.

Control flow: During transformation, constructors compute numeric and symbolic XDR widths and update global tables. Defined types consult `structs` to choose C classifiers. Structs ending in optional data of their own type become `_XdrPointer`. Pragmas mutate global code-generation controls. RPC productions collect procedures into versions/programs.

State and persistence behavior: Semantic state is process-global and persists across parses in one Python interpreter. No files are written.

Dependencies and integration points: Used by all subcommands and generators. Depends on Lark `ast_utils`, dataclasses, and the grammar's production names.

Risks: Global state is not reset per parse, which is risky for long-lived command drivers. Forward references depend on transformation order and `max_widths` entries. Some union width paths assume at least one arm initializes `width`. Unsupported optional typedefs and arm types surface later in generators.

Test signals: Transform specs with constants, arrays using symbolic constants, recursive optional structs, pragmas, pass-through merging, unions with defaults, RPC programs, undefined types, and repeated parses in one process.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/xdr_ast.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/xdr_parse.py -->
# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/xdr_parse.py

Purpose: Provides parser construction, parser/decoder option globals, and user-friendly parse/semantic error reporting for XDR generator subcommands.

Important APIs and functions: `set_xdr_annotate`, `get_xdr_annotate`, `set_xdr_enum_validation`, and `get_xdr_enum_validation` manage generation flags. `make_error_handler(source, filename)` returns a Lark `on_error` callback that prints filename/line/column, unexpected token, expected tokens, source line, and caret. `handle_transform_error` reports semantic transform failures. `xdr_parser()` opens `grammars/xdr.lark`.

Control flow: Subcommands set globals, call `xdr_parser`, parse with the error handler, and transform with `xdr_ast`. Parse errors raise `XdrParseError` to abort after the first formatted diagnostic. Transform errors unwrap `VisitError` and special-case undefined-type `KeyError`.

State and persistence behavior: `annotate` and `enum_validation` are process-global booleans. No persistent files are written.

Dependencies and integration points: Depends on Lark, `grammars/xdr.lark`, and subcommands/generators that read the option globals.

Risks: Global flags can leak across invocations. Error token mapping is partial and grammar changes may produce raw token names. Strict LALR parser construction may fail early if grammar conflicts appear.

Test signals: Parse valid files, unexpected identifiers/numbers/punctuation, EOF errors, undefined types, annotation on/off, enum validation on/off, and grammar path resolution from different working directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/xdr_parse.py -->
