# subset-b-006749 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/parse-no-sample-id-all.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/parse-no-sample-id-all.c

## Purpose

This perf selftest verifies that perf can parse old-kernel event streams where `sample_id_all` is not set. The target case is multiple selected events followed by a non-sample record, where no trailing sample id exists to disambiguate event ownership.

## Research

Important functions are `process_event`, `process_events`, and `test__parse_no_sample_id_all`. `process_event` first feeds `PERF_RECORD_HEADER_ATTR` records to `perf_event__process_attr`, rejects user-private record types, requires an initialized `evlist`, then initializes a `perf_sample` and calls `evlist__parse_sample`. The synthetic test creates two attribute records with ids 1 and 2 plus a `PERF_RECORD_MMAP` record, then validates that the parser does not fail when the mmap record lacks appended id data. State is only in the transient `evlist` built from attr records and the stack-allocated synthetic events. Dependencies are `event.h`, `evlist.h`, `header.h`, and `util/sample.h`. Integration is direct with perf's sample parser and suite registration through `DEFINE_SUITE`. Risks include false regressions if synthetic record sizes stop matching kernel layout, and missed coverage for newer non-sample records. Test signal is `TEST_OK` when all three records parse without relying on `sample_id_all`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/parse-no-sample-id-all.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/pe-file-parsing.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/pe-file-parsing.c

## Purpose

This selftest validates perf's PE/COFF support when libbfd is enabled: reading a PE build-id, resolving a GNU debuglink, loading external debug symbols, and finding `main` in a Windows binary fixture.

## Research

The main helper is `run_dir`, which builds paths for `pe-file.exe` and `pe-file.exe.debug`, calls `filename__read_build_id`, checks the fixed 16-byte CodeView build id, verifies `filename__read_debuglink`, creates a `dso`, loads BFD symbols with `dso__load_bfd_symbols`, sorts by name, and uses `dso__find_symbol_by_name`. `test__pe_file_parsing` searches `./tests` first, then the installed perf tests directory from `get_argv_exec_path`. If `HAVE_LIBBFD_SUPPORT` is absent, the suite skips. State is limited to local buffers and a temporary DSO object. Dependencies include libbfd, `util/build-id.h`, `util/symbol.h`, and `util/dso.h`. Risks are fixture drift, missing installed test data, platform builds without libbfd, and build-id byte-order mistakes. Strong test signals are exact build-id equality, debuglink name equality, successful BFD symbol loading, and finding `main`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/pe-file-parsing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/pe-file.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/pe-file.c

## Purpose

This tiny C source is the origin for the PE fixture consumed by `pe-file-parsing.c`. It exists to produce `pe-file.exe` and `pe-file.exe.debug` with a deterministic build-id and debuglink setup.

## Research

The file exports only `main`, returning zero. The comments document the exact MinGW and objcopy commands used to create the checked-in PE binary, split debug file, compressed debug sections, stripped executable, and GNU debuglink. There is no runtime state or persistence in the program itself; the persistent artifact is the generated PE/debug fixture stored beside perf tests. Dependencies are external to compilation: `x86_64-w64-mingw32-gcc` and `x86_64-w64-mingw32-objcopy`. Integration is indirect through PE build-id/debuglink tests. Risks are that rebuilding with different toolchain versions, alignment options, or build-id implementation changes can invalidate the expected bytes in `pe-file-parsing.c`. Test signal is simply that the generated binary has a discoverable symbol named `main` and matching debug file metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/pe-file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/perf-hooks.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/perf-hooks.c

## Purpose

This selftest exercises perf's hook framework recovery path when an installed hook crashes. It ensures a bad hook is invoked, recovery runs after SIGSEGV, and the hook is removed.

## Research

`the_hook` receives a pointer to an integer flag, writes `1234`, then raises `SIGSEGV`. `sigsegv_handler` logs recovery, calls `perf_hooks__recover`, restores the default handler, raises SIGSEGV again, and exits if control unexpectedly returns. `test__perf_hooks` installs the handler, registers `the_hook` under hook name `test`, invokes `perf_hooks__invoke_test`, checks the flag, then verifies `perf_hooks__get_hook("test")` is null. State is the hook registry in `perf-hooks.h` and one stack `hook_flags` variable. Dependencies are process signal handling and perf's hook API. Integration is suite-level coverage for hook isolation in developer/testing builds. Risks include platform signal semantics, brittle behavior if recovery longjmps differently, and accidental masking of real crashes. Passing signals are flag mutation and automatic hook removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/perf-hooks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/perf-record.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/perf-record.c

## Purpose

This selftest records a controlled `sleep 1` workload and validates `PERF_RECORD_*` records plus parsed `perf_sample` fields such as cpu, pid, tid, and monotonic sample time.

## Research

`sched__get_first_possible_cpu` trims the workload affinity mask to one CPU. `test__PERF_RECORD` creates a dummy or default evlist, prepares a workload, enables CPU/TID/TIME sample bits, configures and opens events, mmaps rings, starts the workload, and drains mmap buffers until `PERF_RECORD_EXIT` or timeout. It validates time ordering, cpu affinity, pid/tid consistency, expected comm name, and presence of mappings for the executable or coreutils wrapper, libc, dynamic loader, and vDSO. State includes a prepared workload pid, evlist maps and mmaps, a mutable `perf_sample`, event counters, and booleans for required mmap records. Dependencies include `sys_perf_event_open` permission, scheduler affinity, `sleep`, mmap ring helpers, and kernel record generation. Integration covers record pipeline correctness for workload setup, event parsing, and metadata records. Risks are environment-specific mappings, permissions (`-EACCES` skips), non-coreutils sleep locations, and slow systems hitting the wakeup limit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/perf-record.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/perf-targz-src-pkg -->
# sources/distributed-fs/ceph-client/tools/perf/tests/perf-targz-src-pkg

## Purpose

This shell test validates the kernel `make perf-targz-src-pkg` target by building perf from the generated source tarball outside the full kernel tree.

## Research

The script takes the perf binary path as `$1`, changes to the kernel root via `${PERF}/../..`, runs `make perf-targz-src-pkg`, selects the newest `perf-*.tar.gz`, extracts it to a temporary directory, deletes the tarball, returns to the original directory, and runs `make -C $TMP_DEST/perf*/tools/perf`. State is the generated tarball and temporary extraction directory, both removed after use. Dependencies are `make`, `tar`, a valid perf source tree, and a complete `tools/perf/MANIFEST`. Integration tests source package completeness after files move between `tools/perf`, `tools/include`, and related locations. Risks include `ls -rt` ambiguity if multiple tarballs exist, broad cleanup of `perf-*.tar.gz`, and build failures from host dependency gaps rather than manifest omissions. Test signal is the build exit code from the extracted package.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/perf-targz-src-pkg -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/perf-time-to-tsc.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/perf-time-to-tsc.c

## Purpose

This selftest verifies that perf mmap metadata can convert between perf time and hardware TSC/counter time while preserving event ordering around two synthetic `COMM` events.

## Research

The file gates support to x86, i386, and arm64. `test__tsc_is_supported` skips unsupported architectures. `test__perf_time_to_tsc` builds a single-thread, online-CPU evlist for `cpu-cycles:u`, sets `comm`, disabled, and no enable-on-exec on each evsel, opens/mmaps, reads `perf_tsc_conversion` from the mmap page, enables events, changes process name to `Test COMM 1`, reads `rdtsc`, changes name to `Test COMM 2`, disables, and scans mmap records for both `COMM` times. It converts the intermediate TSC to perf time and both perf times back to TSC, requiring the intermediate point to fall between them in both domains. State is ring-buffer data and conversion coefficients. Dependencies include TSC support in kernel mmap page, `prctl(PR_SET_NAME)`, parse-events, and PMU availability. Risks include unsupported kernels, hybrid `cpu-cycles` creating multiple evsels, missing comm events, and conversion precision around close timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/perf-time-to-tsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/pfm.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/pfm.c

## Purpose

This selftest validates perf's optional libpfm4 event parser for plain event lists and grouped event expressions.

## Research

When `HAVE_LIBPFM` is enabled, `count_pfm_events` walks a `perf_evlist`. `test__pfm_events` feeds strings such as empty input, `instructions`, repeated events, unknown `stereolab`, and mixed known/unknown entries to `parse_libpfm_events_option`, then checks event count and zero groups. `test__pfm_group` covers `{}` groups, repeated groups, mixed invalid groups, unmatched braces, and nested braces, verifying both evsel count and group count. Without libpfm support both tests skip. State is per-case newly allocated evlists. Dependencies are libpfm integration in `util/pfm.h`, the option callback ABI, and perf grouping semantics. Integration catches regressions in command-line `--pfm-events` parsing. Risks are libpfm event availability differences and permissive parser behavior that intentionally accepts some malformed tails. Test signals are exact expected event and group counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/pfm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/pmu-events.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/pmu-events.c

## Purpose

This large selftest validates generated PMU event and metric tables, alias creation for core and uncore PMUs, and parseability/evaluability of metric expressions and thresholds.

## Research

Static `perf_pmu_test_event` fixtures describe expected core, uncore, and sys events. `compare_pmu_events` and `compare_alias_to_test_event` compare generated table fields and runtime alias fields. `test__pmu_event_table` finds test tables and iterates events with callbacks. Alias tests instantiate fake `perf_pmu` objects, add CPU/sys aliases, and verify event lookup for core PMUs, named uncore PMUs, PMU ids, compat regexes, and hyphenated names. Metric tests use `metricgroup__parse_groups_test`, allocate fake stats, assign values, and evaluate expressions; fake parsing separately extracts ids from metric formulas, parses ids using fake PMUs, and evaluates with synthetic values. Threshold parsing walks all core and sys metrics. State is all heap-local fake PMUs, evlists, stats, expr contexts, and generated tables. Dependencies include `pmu-events`, `metricgroup`, `expr`, `parse-events`, and test architecture tables. Risks include fixture drift after JSON schema changes, special handling for intentionally broken metrics `M1/M2/M3`, divide-by-zero workarounds, and alias matching across heterogeneous PMU names. Test signals are field-for-field event equality, alias counts, and zero metric parse failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/pmu-events.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/pmu.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/pmu.c

## Purpose

This selftest validates sysfs PMU format parsing, sysfs event parsing, event name rules, PMU name normalization/comparison, wildcard matching, and user config preservation.

## Research

`test_pmu_get` creates a temporary fake sysfs PMU with `type`, `format`, and `events/test-event` files, then loads it through `perf_pmus__add_test_pmu`; `test_pmu_put` removes the temp tree and deletes the PMU. `test__pmu_format` parses explicit terms and checks exact `config`, `config1`, and `config2` bit packing. `test__pmu_events` parses the fake sysfs event and checks the same packed values. `test__pmu_usr_chgs` verifies `evsel__set_config_if_unset` does not overwrite raw/user-provided fields but fills unset fields. `test__pmu_event_names` walks real sysfs PMU events and enforces all-lower/all-upper naming except legacy cache names. Name tests cover suffix stripping, numeric ordering, and `perf_pmu__wildcard_match`. State includes fake sysfs directories under `/tmp` and global PMU list entries. Dependencies are sysfs helpers, parse-events, file availability, and cleanup. Risks are `system("rm -fr")` path safety, real sysfs naming exceptions, and bitfield expectations if format parser semantics change. Passing signals are exact config values and successful naming/matching assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/sample-parsing.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/sample-parsing.c

## Purpose

This selftest synthesizes perf sample records for every supported `PERF_SAMPLE_*` bit and verifies parsing reproduces the original `perf_sample` fields, including read formats, regs, stacks, branch stacks, and AUX data.

## Research

`samples_same` conditionally compares fields based on `sample_type`, `read_format`, and endian-swap expectations. `do_test` fills a rich `perf_sample`, computes the expected sample event size, allocates a padded event buffer, calls `perf_event__synthesize_sample`, verifies the written size by checking untouched `0xff` tail bytes, then parses via `evsel__parse_sample`. For branch stacks it repeats parsing with `needs_swap` and checks known big/little-endian flag values. `test__sample_parsing` requires updates when new sample bits exceed `PERF_SAMPLE_WEIGHT_STRUCT`, tests each sample bit alone, iterates read-format variants for `PERF_SAMPLE_READ`, and tests all bits together with mutually exclusive weight variants. State is only synthetic stack/heap data. Dependencies include sample synthesis, evsel sample size calculation, branch-stack flag encoding, and register mask helpers. Risks are brittle assumptions around new sample bits, endian flag constants, and read-format LOST handling. Passing signal is exact structural equality for every exercised sample layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/sample-parsing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/sdt.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/sdt.c

## Purpose

This selftest validates SDT probe discovery by embedding a DTrace-style probe in perf itself, adding perf's build-id to a temporary cache, and confirming the probe appears in the probe cache.

## Research

When both `HAVE_SDT_EVENT` and `HAVE_LIBELF_SUPPORT` are enabled, `target_function` fires `DTRACE_PROBE(perf, test_target)`. `build_id_cache__add_file` reads the executable build-id and calls `build_id_cache__add_s`. `get_self_path` reads `/proc/self/exe`. `search_cached_probe` opens `probe_cache__new` and looks for `sdt_perf:test_target`. `test__sdt_event` creates `./test-buildid-XXXXXX`, resolves an absolute build-id dir, sets it globally, adds the perf binary, searches the cached probe, calls the target function, and removes the temporary directory. Without support it skips. State is the temporary build-id cache and global buildid dir setting. Dependencies are libelf, sys/sdt.h, build-id cache, probe cache, and filesystem cleanup. Risks include missing build-id, unsupported SDT compilation, relative tempdir cleanup, and no actual probe recording despite cache validation. Test signal is finding the cached SDT event and returning `TEST_OK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/sdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/addr2line_inlines.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/addr2line_inlines.sh

## Purpose

This shell test checks inline source-line unwinding in `perf script` using frame-pointer, DWARF, and LBR call graphs against the `inlineloop` perf test workload.

## Research

The script creates a temp directory, records `perf test -w inlineloop 1` into `perf.data`, runs `perf script --fields +srcline`, and greps for inlined `inlineloop.c:2.` entries plus a non-inlined parent on line `3.`. `test_fp`, `test_dwarf`, and `test_lbr` share the same validation; LBR skips when neither `cpu/caps/branches` nor `cpu_core/caps/branches` exists. State is temporary perf data and script output removed by traps. Dependencies are perf record/script, inline debug information, addr2line/srcline support, and architecture LBR support for the third case. Risks include compiler line-number changes, insufficient samples, and only DWARF truly supporting inline callchains despite fp/lbr coverage. Test signals are required grep matches and accumulated `err`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/addr2line_inlines.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/amd-ibs-swfilt.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/amd-ibs-swfilt.sh

## Purpose

This shell test validates AMD IBS PMU software filtering (`swfilt`) behavior for user/kernel exclude modifiers and sample classification.

## Research

`ParanoidAndNotRoot` combines uid and `/proc/sys/kernel/perf_event_paranoid` checks. The script skips if `/sys/bus/event_source/devices/ibs_op` or its `format/swfilt` file is absent. It expects `ibs_op//u` with a modifier but no swfilt to fail, then verifies `ibs_op/swfilt/u`, `ibs_op/swfilt=1/k`, `ibs_fetch/swfilt/u`, and system-wide `ibs_op/swfilt/k` where permissions allow. It pipes recording output to `perf script -F misc` and counts unexpected kernel or user samples. State is kernel PMU/sysfs and perf output streams only. Dependencies are AMD IBS hardware, perf paranoid policy, root privileges for some paths, and sample misc classification. Risks include skip-heavy behavior on non-AMD systems, zero samples reducing confidence, and permission-dependent partial skips. Test signals are correct reject/accept behavior and zero excluded-domain samples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/amd-ibs-swfilt.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/annotate.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/annotate.sh

## Purpose

This shell test verifies basic `perf annotate` output for file and pipe input modes, including target symbol visibility and disassembly output from default and explicit objdump disassemblers.

## Research

The script sources `lib/perf_has_symbol.sh` and skips unless the perf test binary has `noploop`. `test_basic` records `perf test -w noploop` either to a temp file or stdout pipe, runs `perf annotate --stdio --percent-limit 10`, checks for the `noploop` symbol and disassembly lines matching a percent/offset/instruction regex, repeats with an explicit symbol argument, then forces `--objdump=objdump`. State is temporary perf data and output, removed by traps. Dependencies are perf record/annotate, objdump, symbol availability, and sample generation in the workload. Integration covers annotate's input handling and disassembler plumbing. Risks include regex mismatch for nonstandard disassembly, low sample counts below percent limit, and missing debug/symbol setup. Passing signal is success in both Basic and Pipe modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/annotate.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/attr.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/attr.sh

## Purpose

This wrapper runs the Python perf attribute expectation suite against the current `perf` binary.

## Research

The script sets a trap cleanup function, discovers `shelldir` and `perf_path`, then invokes `python "$shelldir/lib/attr.py" -d "$shelldir/attr" -v -p "$perf_path"`. It does not itself inspect output; the Python runner loads attribute expectation files, executes perf with `PERF_TEST_ATTR`, and validates generated event attribute files. State is delegated to `attr.py` temp directories and expected config files. Dependencies are Python, `which perf`, the `attr` expectation directory, and perf's `PERF_TEST_ATTR` instrumentation. Integration is a suite entry point for perf event attribute regression tests. Risks are using `python` rather than `python3` on hosts without a compatible default, and all failure reporting being delegated. Test signal is the Python command exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/attr.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_probe/test_adding_blacklisted.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_probe/test_adding_blacklisted.sh

## Purpose

This exclusive perf-probe test verifies blacklisted kernel functions cannot be added as kprobes and do not appear in `perf list`.

## Research

The script sources `common/init.sh`, reads the first blacklist functions from `/sys/kernel/debug/kprobes/blacklist`, skips if none are available, detects vmlinux used for symbols, and clears existing probes. It iterates blacklisted functions, runs `perf probe`, expects failure, and validates stderr against skip, not-found, invalid-argument, symbol-fail, out-of-section, or broken-DWARF patterns. A special path identifies MIPS assembler DWARF pollution. It then runs `perf list probe:*` and requires only empty/header/metric-group lines. State includes kernel tracing probe files and logs under `LOGS_DIR`. Dependencies are debugfs tracing, kprobe blacklist, perf probe, readelf for the MIPS check, and shared regex checkers. Risks include destructive clearing of user probes, architecture-specific DWARF noise, and blacklist content variability. Test signals are failed add attempts with whitelisted diagnostics and no listed probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_probe/test_adding_blacklisted.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_probe/test_adding_kernel.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_probe/test_adding_kernel.sh

## Purpose

This exclusive perf-probe test exercises kernel probe add/list/use/delete workflows, dry-run, force-add, wildcard probes, invalid variable handling, and return-value probing.

## Research

After sourcing common init and probe helper code, it defaults `TEST_PROBE` to `inode_permission`, detects missing debuginfo, checks kprobe availability, and clears probes between stages. It tests plain, `-a`, and `--add` probe creation; `perf list` and `perf probe -l`; `perf stat` use with nonzero counts; deletion; removed-list absence; dry-run non-persistence; duplicate rejection and `--force` suffixing; equal counts from duplicate probes; wildcard deletion; wildcard adding of `vfs_* $params`; an intentionally missing variable that must not segfault; and `%return $retval` recording plus `perf script` argument output. State is kernel tracing probe state, perf.data under current test dir, and logs. Dependencies include debugfs, debuginfo for several checks, `/proc` workloads, and regex helpers. Risks are intrusive probe mutation, kernel symbol/name drift, permission failures, and sample count flakiness. Test signals combine perf exit codes with strict output pattern checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_probe/test_adding_kernel.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_probe/test_basic.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_probe/test_basic.sh

## Purpose

This perf-probe smoke test validates basic command availability, help/usage text, and quiet-mode behavior.

## Research

The script sources common init, skips if kprobes are unavailable, optionally checks `perf probe --help` for expected manual sections and options when `PARAM_GENERAL_HELP_TEXT_CHECK=y`, always checks invoking `perf probe` without arguments for usage text, and verifies `--quiet --add vfs_read` plus `--quiet --del vfs_read` produce no stdout/stderr. State includes logs in `LOGS_DIR` and temporary kernel probe mutations for the quiet test. Dependencies are debugfs tracing, shared regex checkers, and optional man/help generation. Integration ensures user-facing command option text and output suppression remain stable. Risks include clearing/leaking probes if quiet add/delete fails, help text wording changes, and root/debugfs requirements. Passing signals are regex matches for help/usage and zero log lines under quiet mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_probe/test_basic.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_probe/test_invalid_options.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_probe/test_invalid_options.sh

## Purpose

This perf-probe test checks diagnostics for missing arguments, optional argument handling, and mutually exclusive option combinations.

## Research

After common initialization and kprobe availability checks, the script records a hint if DWARF support is missing. It loops over `-a`, `-d`, `-L`, and `-V` expecting “requires a value” errors. It then tests `-F` and `-l` without explicit arguments, expecting no stderr. Finally it enumerates incompatible option pairs among add/delete/line/vars/list/functions modes and requires an “cannot be used with” diagnostic for each. State is log files under `LOGS_DIR`, including an aggregate mutually-exclusive error log. Dependencies are perf probe option parsing and shared pattern checkers. Integration targets CLI error handling rather than kernel probe state. Risks include help/error wording changes and one apparent loop bug that always runs `perf probe -F` while naming both `-F` and `-l`. Test signal is successful rejection or acceptance with expected diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_probe/test_invalid_options.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_probe/test_line_semantics.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_probe/test_line_semantics.sh

## Purpose

This perf-probe test validates semantic parsing of `--line` descriptions for acceptable and unacceptable line patterns.

## Research

The script sources common init, skips without kprobe support, and records a DWARF hint when unavailable. It tests valid forms such as `func`, `func:10`, ranges, offsets, `func@source.c`, and `source.c:1+1`, requiring no “Semantic error”. It tests invalid forms such as nonnumeric line/range parts and a malformed lazy-pattern expression, requiring a semantic error. State is only accumulated test result and logs emitted by shared result helpers. Dependencies are perf probe parser, optional DWARF/source lookup, and regex output. Integration protects user-facing line syntax accepted by `perf probe --line`. Risks include valid syntax that still fails due to missing debuginfo, source file ambiguity, and wording changes around semantic errors. Test signal is matching parser acceptance/rejection for each pattern.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_probe/test_line_semantics.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_report/setup.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_report/setup.sh

## Purpose

This setup script prepares perf.data fixtures consumed by the base report tests, including a normal system-wide profile and a latency/context-switch profile.

## Research

The script sources common init, ensures `HEADER_TAR_DIR` exists, records `cpu-clock` with `perf record -asdg` while running `CMD_LONGER_SLEEP`, and validates standard record output patterns. It then records `perf.data.1` with `--latency` using a simple parallel workload that spawns many `cat /proc/cpuinfo` jobs and sleeps. State is `$CURRENT_TEST_DIR/perf.data`, `$CURRENT_TEST_DIR/perf.data.1`, header tar dir, and logs. Dependencies include perf record permissions, software event availability, shell job fan-out, and shared regex patterns. Integration is upstream for `base_report/test_basic.sh`, which assumes these files exist. Risks include permission failures for system-wide recording, low/no samples, host load changing record output, and noisy `cat` logging around the latency setup. Passing signal is both record commands matching standard output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_report/setup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_report/test_basic.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_report/test_basic.sh

## Purpose

This perf-report test validates help text, basic stdio report output, sample-count and CPU-utilization columns, header metadata, filtering, latency report layout, and parallelism sorting.

## Research

The script sources common init and consumes `perf.data` plus `perf.data.1` produced by setup. Optional help validation checks major manual sections and option names. Basic report checks total lost samples, sample header, table header, and kernel symbol rows while whitelisting stderr. Further cases validate `--show-nr-samples`, `--header-only` fields, header timestamp stability after tar/xz round-trip, `--showcpuutilization`, `--pid=1`, empty output for a nonexistent symbol, substring symbol filtering, context-switch flag in latency profile headers, default versus `--latency` column ordering, and `--hierarchy --sort latency,parallelism,comm,symbol --parallelism=1,2`. State is report logs, tarred perf.data copy, and header extraction dir. Dependencies are kernel symbols, environment variables from common settings, xz/tar, and regex helpers. Risks include distro init naming, kernel symbol availability, host CPU count differences, and output format churn. Test signal is strict pattern acceptance for each report mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_report/test_basic.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/buildid.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/buildid.sh

## Purpose

This shell test validates build-id cache add/remove/purge operations and build-id collection during `perf record` for ELF SHA1, ELF MD5, and optionally PE binaries.

## Research

The script requires `readelf` and `cc`, conditionally enables PE testing based on libbfd and wine, builds two tiny busy-loop binaries with different linker build-id styles, and references the checked-in `pe-file.exe`. `get_build_id` extracts ELF ids via readelf and PE ids by dumping `.buildid` with objcopy and rearranging CodeView GUID bytes. `check` validates `.build-id` symlink layout, cached file existence/permissions/content, `perf buildid-cache -l`, and optional `perf buildid-list -i`. `test_add`, `test_remove`, `test_purge`, and `test_record` exercise manual cache commands and post-record cache population. State includes temporary sources, binaries, perf.data, logs, build-id dirs, wine prefix, and `/tmp/jitted`-style artifacts for PE only indirectly. Dependencies include compiler, binutils, perf buildid cache, optional libbfd/wine. Risks include shell-generated source via heredoc, PE extraction fragility, permission-bit checks, and qemu/wine environment noise. Passing signals are exact cache symlink/file validation and removal/purge absence checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/buildid.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/c2c.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/c2c.sh

## Purpose

This shell test smoke-tests `perf c2c record` and `perf c2c report` on a workload with memory operations.

## Research

`check_c2c_support` attempts `perf c2c record -- true` to determine hardware/permission availability. `test_c2c_record_report` skips when support probing fails, records `perf test -w datasym 1`, then runs `perf c2c report --stdio` and `perf c2c report -N`. State is one temporary perf.data file and `.old` cleanup. Dependencies are cache-to-cache PMU support, perf c2c command availability, and the `datasym` workload. Integration covers the c2c record/report command path without checking detailed table contents. Risks include skip on most non-supporting hardware, record failure during workload being treated as skip rather than fail, and no validation of specific sharing metrics. Passing signal is successful report generation in both normal and `-N` modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/c2c.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/check_all_lines_matched.pl -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/check_all_lines_matched.pl

## Purpose

This Perl helper validates that every input line matches at least one supplied regular expression.

## Research

The script stores command-line regexes, sets quiet mode unless `TESTLOG_VERBOSITY >= 2`, and caps diagnostics with `TESTLOG_ERR_MSG_MAX_LINES` defaulting to 20. It reads stdin line by line, strips newline, tests all regexes, prints unmatched lines when verbose, marks failure, and exits with nonzero if any line did not match. State is local counters and no persistent files. Dependencies are Perl regex semantics and environment variables set by the shell test framework. Integration is broad across base probe/report tests where unexpected output should fail even when required patterns are present. Risks include regex portability, unanchored patterns accepting too much, and quiet default hiding useful failure context. Test signal for callers is exit code 0 only when every line is whitelisted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/check_all_lines_matched.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/check_all_patterns_found.pl -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/check_all_patterns_found.pl

## Purpose

This Perl helper validates that every supplied regular expression appears at least once in stdin.

## Research

The script builds `%found` as it scans input lines, sets quiet mode from `TESTLOG_VERBOSITY`, and after reading reports any missing regex before exiting nonzero. It does not require every line to match and does not count occurrences. State is in-memory found flags only. Dependencies are Perl regex matching and caller-provided patterns. Integration is used for positive evidence checks such as required report headers, record messages, probe diagnostics, and help text sections. Risks include loose regexes matching unintended text, duplicate regexes collapsing to one hash entry, and quiet mode suppressing missing-pattern messages. Test signal is exit code 0 only when all expected patterns were observed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/check_all_patterns_found.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/check_errors_whitelisted.pl -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/check_errors_whitelisted.pl

## Purpose

This Perl helper validates stderr output against a whitelist file, failing on any line that does not match one of the file's regexes.

## Research

The script accepts one whitelist path, reads regex lines from it, honors `TESTLOG_ERR_MSG_MAX_LINES` and `TESTLOG_VERBOSITY`, then scans stdin line by line. Each input line must match at least one whitelist regex after chomp; unmatched lines are optionally printed and cause nonzero exit. State is local arrays and counters. Dependencies are readable whitelist files and Perl regex behavior. Integration is used by report tests where stderr may contain known benign warnings but unknown errors should fail the case. Risks include an absent whitelist causing a hard die, overly broad whitelist entries masking real failures, and newline/comment handling in whitelist files. Test signal is exit code 0 when stderr is empty or fully whitelisted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/check_errors_whitelisted.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/check_no_patterns_found.pl -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/check_no_patterns_found.pl

## Purpose

This Perl helper asserts that none of the supplied regular expressions appear in stdin.

## Research

The script scans every input line against every command-line regex, records any found pattern, then reports found regexes in verbose mode and exits nonzero if any appeared. State is a `%found` hash and a pass flag. Dependencies are Perl regex semantics and the shared verbosity environment. Integration protects negative assertions, for example no segfault text, no manual-page lookup failure, and absent probe/event output. Risks include regexes that are too broad, duplicate regex collapse, and lack of line context for found patterns in quiet mode. Test signal is exit code 0 only when none of the forbidden patterns matched.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/check_no_patterns_found.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/init.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/init.sh

## Purpose

This shared shell initializer provides result reporting, environment detection, runmode skipping, kprobe/uprobe cleanup helpers, and SDT support checks for the perf shell testsuite.

## Research

It sources `settings.sh` and `patterns.sh`, derives `THIS_TEST_NAME`, and defines `_echo`, `print_results`, `print_overall_results`, skip/warn printers, and `consider_skipping`. Detection helpers include `detect_baremetal`, `detect_intel`, and `detect_amd`. Probe helpers check debugfs tracing files, clear all kprobes/uprobes by disabling tracing and emptying probe event files, and test SDT presence with `perf list sdt`. State is primarily exported variables from sourced settings plus mutations to `/sys/kernel/debug/tracing` when clearing probes. Dependencies include systemd-detect-virt, `/proc/cpuinfo`, debugfs tracing, and the configured `CMD_PERF`. Integration is central for base_probe and base_report scripts. Risks include destructive probe cleanup, sourcing path assumptions based on `$0`, and result functions treating any nonzero check as failure even for expected skip unless caller handles it. Test signal is standardized PASS/FAIL/SKIP output and exit status propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/init.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/patterns.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/patterns.sh

## Purpose

This shared shell file exports regular-expression fragments used by the perf shell testsuite to validate perf output consistently.

## Research

The file defines patterns for decimal and hex numbers, dates/times, addresses, process names, event names, file/path/DSO forms, empty/comment lines, perf-record success lines, trace output, report lines, task names, and segfault diagnostics. These variables are composed by test scripts and passed to Perl checkers. State is a set of exported environment variables; there is no runtime logic beyond assignments. Dependencies are Perl-compatible regex syntax as consumed by `grep -P` or Perl helpers, and `LC_ALL=C` from settings to stabilize text classes. Integration is broad across base_probe/report and other scripts. Risks are regex drift when perf output changes, patterns that are over-specific to English/C locale, and broad patterns masking malformed output. Test signals are indirect: scripts pass when these expressions correctly match expected outputs and reject unexpected lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/patterns.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/settings.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/settings.sh

## Purpose

This shared shell file defines perf testsuite defaults for command paths, workloads, runmodes, logging, locale, colors, directory layout, and optional parametrization.

## Research

It exports `CMD_PERF`, common sleep/true workloads, runmode constants, default runmode, verbosity, color flags, `LC_ALL=C`, terminal color escape variables, `TEST_NAME`, architecture, and run directories. When `PERFSUITE_RUN_DIR` is set, it creates per-test `CURRENT_TEST_DIR`, `MAKE_TARGET_DIR`, `LOGS_DIR`, and `HEADER_TAR_DIR`; otherwise it uses the current directory. It then sources runmode-specific and default parametrization files from `../common` when applicable. State is exported environment and created directories. Dependencies are `which perf`, `readlink`, `arch`, shell path layout, and optional parametrization files. Integration provides stable configuration for all tests sourcing `init.sh`. Risks include global locale override, default `which perf` picking the wrong binary, directory creation in shared paths, and `$0`-based path inference failing when sourced unconventionally. Test signal is consistent environment for downstream scripts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/settings.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/Makefile -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/Makefile

## Purpose

This Makefile orchestrates building, installing, and cleaning CoreSight shell-test workload subdirectories.

## Research

It includes shared kernel tool make fragments, defines `SUBDIRS` as `asm_pure_loop`, `memcpy_thread`, `thread_loop`, and `unroll_loop_thread`, and delegates `all`, `install-tests`, and `clean` to each subdirectory. `INSTALLDIRS` and `CLEANDIRS` are generated from `SUBDIRS`; clean uses `QUIET_CLEAN`. State is build artifacts in child directories and installed test binaries under perf's install tree. Dependencies are the parent tools make infrastructure, architecture detection, and each child Makefile's `CORESIGHT`/`ARCH` gates. Integration ensures CoreSight workload binaries are available for shell wrappers. Risks include silent child build output hiding details, failure when shared make includes move, and no build on non-arm64/non-CoreSight configurations. Test signal is successful delegation to all child targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/asm_pure_loop.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/asm_pure_loop.sh

## Purpose

This CoreSight shell test records an arm64 assembly pure-loop workload and verifies the resulting AUX trace contains expected ETM packet evidence.

## Research

The script sets `TEST=asm_pure_loop`, sources `../lib/coresight.sh`, defines no workload arguments, writes data to `perf-asm_pure_loop-out.data`, runs `perf record $PERFRECOPT -o "$DATA" "$BIN"`, then calls `perf_dump_aux_verify "$DATA" 10 10 10`. State is the perf.data file and a transient AUX dump/stat CSV generated by the helper. Dependencies are an executable `asm_pure_loop` binary, `cs_etm` PMU availability, arm64 CoreSight tracing, and helper defaults `-m ,16M -e cs_etm//u`. Risks include lossy trace causing low packet counts, skip if binary or PMU missing, and exact thresholds being environment-sensitive. Test signal is at least 10 `I_ATOM_F`, 10 `I_ASYNC`, and 10 `I_TRACE_INFO` packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/asm_pure_loop.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/asm_pure_loop/Makefile -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/asm_pure_loop/Makefile

## Purpose

This Makefile builds and installs the `asm_pure_loop` CoreSight workload from raw arm64 assembly.

## Research

It includes `../Makefile.miniconfig`, sets `BIN=asm_pure_loop`, and compiles `asm_pure_loop.S` with `-nostdlib -static` only when `CORESIGHT` is defined and `ARCH=arm64`. `install-tests` creates the perf exec test subdirectory and installs the binary under its own named directory. `clean` removes the binary. State is the built static executable and installed copy. Dependencies are arm64 compiler support, install variables from perf's make system, and CoreSight build configuration. Integration supplies a deterministic no-libc workload for `asm_pure_loop.sh`. Risks are no target produced on non-arm64 builds, static link/toolchain failures, and install path variable quoting complexity. Test signal is existence of an executable binary for the shell wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/asm_pure_loop/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/asm_pure_loop/asm_pure_loop.S -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/asm_pure_loop/asm_pure_loop.S

## Purpose

This arm64 assembly workload creates a predictable branch-heavy loop for CoreSight ETM trace validation.

## Research

The `_start` entry sets `x0` to `0x0000ffff` as loop count and `x1` to zero. Each iteration executes nops, conditionally branches around more nops via `cbnz`, computes the `skip` address with `adrp/add`, performs an indirect `br`, decrements `x0`, and loops until zero. It exits through syscall 93 with status 0 and declares an empty GNU-stack note. There is no libc, heap, or persistent state; execution state is registers and instruction flow. Dependencies are arm64 instruction set and Linux syscall ABI. Integration provides a stable ETM packet source for `asm_pure_loop.sh`. Risks include assembler/linker differences affecting layout, branch predictor/trace compression variability, and being arm64-only. Test signals are sufficient branch/async/trace-info packets in the recorded AUX dump.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/asm_pure_loop/asm_pure_loop.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/memcpy_thread/Makefile -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/memcpy_thread/Makefile

## Purpose

This Makefile builds and installs the pthread-based `memcpy_thread` CoreSight workload.

## Research

It includes `../Makefile.miniconfig`, sets `BIN=memcpy_thread` and `LIB=-pthread`, and compiles the C source only for `CORESIGHT` arm64 builds. `install-tests` creates `$(perfexec_instdir)/$(INSTDIR_SUB)/memcpy_thread` and installs the binary there; `clean` removes it. State is the local executable and optional installed test binary. Dependencies are a C compiler, pthread library, arm64 CoreSight build gates, and perf install variables. Integration supports `memcpy_thread_16k_10.sh`. Risks are no-op build on unsupported architectures, pthread link failures in static/cross environments, and shell tests skipping if binary is absent. Test signal is successful binary creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/memcpy_thread/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/memcpy_thread/memcpy_thread.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/memcpy_thread/memcpy_thread.c

## Purpose

This workload spawns multiple threads that repeatedly copy memory, creating sustained user-space instruction and memory activity for CoreSight tracing.

## Research

`struct args` holds loop count, copy size in KiB, thread id, and return pointer. `thrfn` allocates source and destination buffers of `size * 1024`, exits on allocation failure, and calls `memcpy` for `loops` iterations. `new_thr` initializes pthread attributes and starts a thread. `main` validates three arguments: copy size 1 KiB to 1 GiB, threads 1 to 256, and loop count in hundreds up to 40,000,000,000; it multiplies loop count by 100, starts all threads, and joins them. State is per-thread heap buffers that are not freed before process exit and thread metadata in a fixed 256-entry array. Dependencies are pthreads, libc allocation, and memory bandwidth. Risks include very large memory allocation, uninitialized source contents being acceptable because data value is irrelevant, and long runtimes for high loop counts. Test signal is process completion with enough trace packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/memcpy_thread/memcpy_thread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/memcpy_thread_16k_10.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/memcpy_thread_16k_10.sh

## Purpose

This CoreSight shell test records the `memcpy_thread` workload with 10 threads copying 16 KiB blocks and verifies basic AUX trace packet counts.

## Research

The script sets `TEST=memcpy_thread`, sources `coresight.sh`, uses `ARGS="16 10 1"` and data variant `16k_10`, runs `perf record $PERFRECOPT -o "$DATA" "$BIN" $ARGS`, then calls `perf_dump_aux_verify "$DATA" 10 10 10`. State is the perf data file and helper-generated stat CSV. Dependencies are the installed/build `memcpy_thread` binary, `cs_etm` PMU, CoreSight ETM trace support, and enough system resources to allocate buffers for 10 threads. Risks are trace loss, skipped test on missing PMU/binary, and workload timing variance. Test signal is meeting minimum `I_ATOM_F`, `I_ASYNC`, and `I_TRACE_INFO` counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/memcpy_thread_16k_10.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/thread_loop/Makefile -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/thread_loop/Makefile

## Purpose

This Makefile builds and installs the pthread/inline-assembly `thread_loop` CoreSight workload.

## Research

It includes `../Makefile.miniconfig`, sets `BIN=thread_loop` and `LIB=-pthread`, and compiles `thread_loop.c` only when CoreSight is enabled on arm64. Installation mirrors other CoreSight workloads by placing the binary in a named perf exec test subdirectory, and `clean` removes the executable. State is the build artifact and optional installed binary. Dependencies are arm64 compiler support, pthreads, perf make variables, and CoreSight configuration. Integration supplies the workload for TID verification scripts. Risks are skipped/no-op builds outside arm64 CoreSight, pthread link issues, and missing install causing shell wrapper skip. Test signal is an executable binary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/thread_loop/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/thread_loop/thread_loop.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/thread_loop/thread_loop.c

## Purpose

This workload creates one or more threads executing a tight arm64 assembly loop and optionally prints each Linux TID for CoreSight CID/VMID trace validation.

## Research

The file defines `_GNU_SOURCE`, supplies a fallback `SYS_gettid` value for arm64, and wraps `gettid()` with `syscall`. `thrfn` prints the TID when `SHOW_TID` is set, then runs inline assembly that increments and compares registers until a loop count is reached. `new_thr` starts a pthread. `main` validates thread count 1 to 256 and loop count in millions 1 to 4000, multiplies by 1,000,000, starts threads, and joins them. State is fixed-size thread args and optional stdout TID list. Dependencies are pthreads, arm64 inline assembly syntax, Linux gettid syscall, and environment variable `SHOW_TID`. Integration is with `thread_loop_check_tid_*.sh` and `perf_dump_aux_tid_verify`. Risks include inline assembly operand constraints not updating C variable expectations, stdout buffering, syscall-number assumptions outside arm64, and long runtimes at high loop counts. Test signal is every printed TID found in AUX dump CID/VMID fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/thread_loop/thread_loop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/thread_loop_check_tid_10.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/thread_loop_check_tid_10.sh

## Purpose

This CoreSight test records `thread_loop` with 10 threads and verifies the AUX trace contains trace identifiers for every thread reported by the workload.

## Research

The script sets `TEST=thread_loop`, sources `coresight.sh`, uses `ARGS="10 1"`, captures perf data and stdout paths, runs `SHOW_TID=1 perf record -s $PERFRECOPT -o "$DATA" "$BIN" $ARGS > $STDO`, then calls `perf_dump_aux_tid_verify "$DATA" "$STDO"`. State is perf data plus a stdout file containing decimal TIDs. Dependencies are the `thread_loop` binary, CoreSight ETM, sample identifier recording via `-s`, and helper parsing of `CID=` or `VMID=` from perf dump output. Risks include missing CIDs due to kernel reporting differences, trace loss for short-running threads, and stdout/perf timing races. Passing signal is no missing TID in helper verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/thread_loop_check_tid_10.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/thread_loop_check_tid_2.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/thread_loop_check_tid_2.sh

## Purpose

This CoreSight test records `thread_loop` with 2 longer-running threads and verifies TID-to-AUX trace coverage.

## Research

The script is parallel to the 10-thread variant but uses `ARGS="2 20"` and data variant `check-tid-2th`. It enables `SHOW_TID`, records with `perf record -s` and the CoreSight event options, writes workload stdout to a file, then passes perf data and stdout to `perf_dump_aux_tid_verify`. State is temporary/current-directory perf data and stdout. Dependencies are `thread_loop`, CoreSight ETM, perf dump exposing `CID` or `VMID`, and enough runtime for both threads to produce trace. Risks include missing identifiers due to trace truncation or kernel format changes, and the longer loop increasing runtime on slow systems. Passing signal is every printed TID matched against AUX trace identifiers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/thread_loop_check_tid_2.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/unroll_loop_thread/Makefile -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/unroll_loop_thread/Makefile

## Purpose

This Makefile builds and installs the `unroll_loop_thread` CoreSight workload.

## Research

It includes `../Makefile.miniconfig`, sets `BIN=unroll_loop_thread`, links with `-pthread`, and compiles only for CoreSight-enabled arm64 builds. Installation creates the named perf exec test directory and installs the binary; clean removes it. State is the build artifact and installed copy. Dependencies are a C compiler, pthreads, perf make install variables, and arm64 CoreSight gating. Integration supports `unroll_loop_thread_10.sh`, which records a large unrolled instruction stream. Risks are skipped builds outside the supported environment and compiler behavior changes affecting inline assembly expansion. Test signal is executable availability for the wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/unroll_loop_thread/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/unroll_loop_thread/unroll_loop_thread.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/unroll_loop_thread/unroll_loop_thread.c

## Purpose

This workload creates threads that execute a very large unrolled sequence of arm64 `add` instructions, generating long contiguous code traces for CoreSight validation.

## Research

`struct args` holds a pthread, input seed, and return pointer. `thrfn` loops 10,000 times and executes inline assembly built from nested macros `SNIP1` through `SNIP5`, expanding to a large number of repeated `add %w[in], %w[in], #1` instructions. `new_thr` starts a pthread. `main` validates thread count 1 to 256, seeds each thread's input with `rand()`, starts all threads, and joins them. State is per-thread args only; the arithmetic result is intentionally not consumed. Dependencies are arm64 inline assembly, pthreads, and compiler macro expansion. Integration is with CoreSight AUX packet threshold tests. Risks include compiler optimizing or rejecting the asm constraints, very large generated text size, and runtime/trace volume variability. Test signal is enough decoded ETM packets from the unrolled workload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/unroll_loop_thread/unroll_loop_thread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/unroll_loop_thread_10.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/unroll_loop_thread_10.sh

## Purpose

This CoreSight shell test records the unrolled-loop workload with 10 threads and verifies basic AUX trace packet counts.

## Research

The script sets `TEST=unroll_loop_thread`, sources `coresight.sh`, uses `ARGS="10"` and `DATV="10"`, records with `perf record $PERFRECOPT -o "$DATA" "$BIN" $ARGS`, then calls `perf_dump_aux_verify "$DATA" 10 10 10`. State is a perf data file and helper statistics. Dependencies are the built workload, arm64 CoreSight ETM PMU, and perf report dump decoding. Risks include trace loss due to high instruction volume, skipped test on missing binary/PMU, and threshold sensitivity to hardware buffer configuration. Passing signal is packet counts meeting all three minimums.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/unroll_loop_thread_10.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/daemon.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/daemon.sh

## Purpose

This shell test validates `perf daemon` lifecycle and control operations: list, reconfig, stop, signal/switch-output, ping, and lock enforcement.

## Research

`check_line_first` and `check_line_other` parse colon-separated `perf daemon -x:` output fields and compare name, run command, base, output, lock/control/ack paths, and uptime. `daemon_start` starts a daemon from a generated config, installs signal cleanup, and polls `perf daemon ping`; `daemon_exit` stops it and waits for the pid. `test_list` checks daemon and session list lines. `test_reconfig` edits the config in place, waits for old sessions to exit and new sessions to start, tests empty config removal, then restores sessions. `test_stop` ensures session processes disappear. `test_signal` sends session/global signals and waits for rotated perf.data files. `test_ping` checks sessions respond OK. `test_lock` verifies a second daemon cannot start on the same base. State is temporary config files, daemon base directories with control/ack/output files, and background perf processes. Dependencies are `perf daemon`, `tail --pid`, `sleep`, and process table visibility. Risks include races in polling, awk colon parsing if paths contain colons, and cleanup on interruption. Passing signal is final `error=0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/daemon.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/data_type_profiling.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/data_type_profiling.sh

## Purpose

This shell test validates `perf annotate --code-with-type` data type profiling for Rust and C workloads, in file and pipe modes.

## Research

The script first probes `perf mem record` support and skips if no PMU supports memory events. `test_basic_annotate` selects Rust `perf test -w code_with_type` expecting `# data-type: struct Buf`, or C `perf test -w datasym` expecting `# data-type: struct buf`. It skips the Rust case when `perf check feature -q rust` fails, records with `perf mem record` either to a file or stdout pipe, runs `perf annotate --code-with-type --stdio --percent-limit 1`, and greps for the target data-type header. State is temporary perf data and annotate output. Dependencies are perf mem PMU support, Rust workload build for Rust cases, debug/type info, and annotate type decoding. Risks include memory-event permission gaps, insufficient samples, type-name changes, and pipe mode hiding record errors. Passing signal is expected data-type text in all supported modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/data_type_profiling.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/diff.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/diff.sh

## Purpose

This shell test validates `perf diff` output for two and three recorded profiles of the same workload.

## Research

The script sources `lib/perf_has_symbol.sh`, requires the `test_loop` symbol in perf's test binary, and uses `perf test -w thloop` as workload. `make_data` records to a supplied temp file and confirms `perf report -q` contains `test_loop`. `test_two_files` creates two profiles and requires `perf diff file1 file2` to show the symbol. `test_three_files` repeats with three profiles. State is three temporary perf.data files and `.old` cleanup. Dependencies are symbol availability, perf record/report/diff, and enough samples in `thloop`. Integration checks diff command-line handling for multiple input files rather than numeric diff correctness. Risks include sampling flakiness, missing symbols, and reuse of global `err` as both function status and test status. Passing signal is symbol presence in diff output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/diff.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/drm_pmu.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/drm_pmu.sh

## Purpose

This shell test validates that raw DRM PMU events listed by perf can be used with `perf stat` against the current process.

## Research

The script opens every character device under `/dev/dri` with major 226, stores fds in an associative array, and prints each `/proc/$$/fdinfo/$fd` so DRM statistics exist for the process. If no DRM devices are found it skips. It iterates `perf list --raw-dump drm-`, runs `perf stat -e "$p" --pid=$$ true`, and checks the event name appears in output. It closes all opened fds at the end. State includes live device file descriptors and one temporary output file. Dependencies are DRM devices, readable device nodes, fdinfo statistics, perf DRM PMU support, and Bash associative arrays. Risks include permission failures opening render/card nodes, empty raw-dump output, event names that require active GPU work, and leaking fds if interrupted before cleanup. Passing signal is every listed DRM event visible in perf stat output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/drm_pmu.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/evlist.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/evlist.sh

## Purpose

This shell test validates `perf evlist` for simple events, grouped events, and verbose event configuration.

## Research

`test_evlist_simple` records `cpu-clock` for `true` and checks `perf evlist -i` lists it. `test_evlist_group` records `{cpu-clock,task-clock}` against `perf test -w noploop`, skips on record failure, and requires `perf evlist -g` to show both events in group braces. `test_evlist_verbose` records `cycles` and checks `perf evlist -v` contains `config:`. State is one temporary perf.data file reused across cases. Dependencies are perf record/evlist, software and hardware event availability, grouping support, and the `noploop` workload. Risks include hardware `cycles` permission failure, group record skipped silently, and regex assumptions around grouping output. Passing signal is all non-skipped checks finding expected text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/evlist.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/ftrace.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/ftrace.sh

## Purpose

This root-only shell test validates `perf ftrace` list, trace, latency, and profile subcommands using `sleep 0.1`.

## Research

The script skips unless running as root. `test_ftrace_list` runs `perf ftrace -F`, stores sleep-related syscall functions, and prints them. `test_ftrace_trace` runs graph tracing for sleep, requires comment lines and `sleep()`, then selects a syscall function observed in trace output. `test_ftrace_latency` runs latency tracing for that function and checks header/summary markers. `test_ftrace_profile` runs profile mode and uses a regex to find a `clock_nanosleep` line with count 1 and about 0.1 seconds. State is a temporary output file and selected `target_function`. Dependencies are ftrace permissions, tracefs, syscall naming, and architecture-specific function prefixes. Risks include root requirement, sleep syscall naming changes, timing variance, and ftrace conflicts with existing tracing. Passing signal is all grep checks succeeding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/ftrace.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/header.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/header.sh

## Purpose

This shell test validates `perf report --header-only -I` header output for file and pipe input modes.

## Research

`check_header_output` requires fields including captured time, hostname, OS release, arch, cpuid, nrcpus, event, cmdline, perf version, sibling topology, and total memory. `test_file` records `perf test -w noploop` to a temp file, reports its header, and checks fields. `test_pipe` streams `perf record -o -` directly into `perf report --header-only -I -i -` and applies the same checks. State is temporary perf.data and script output. Dependencies are perf record/report, header feature collection, topology data, and `noploop` workload. Risks include missing cpuid/topology fields on some architectures, pipe-mode metadata differences, and record permission issues. Passing signal is all expected field regexes found in both modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/header.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/inject-callchain.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/inject-callchain.sh

## Purpose

This shell test verifies `perf inject --convert-callchain` can convert DWARF callchains to regular callchains without changing report output except for inlined-function differences.

## Research

The script skips if DWARF support is unavailable. It records `perf test -w noploop` with high frequency and DWARF call graph, runs `perf inject -i "$TESTDATA" --convert-callchain -o "$TESTDATA.new"`, produces quiet no-children reports for both original and converted data, then diffs them. Differences beginning with removed lines are allowed only when they mention `(inlined)`; any other removed difference fails. State is a temporary perf.data pair and report outputs. Dependencies are DWARF unwind support, perf inject, report stability, and sufficient samples. Risks include legitimate formatting differences beyond inlining, sampling nondeterminism between report generation not recording, and DWARF collection permissions. Passing signal is no non-inlined report differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/inject-callchain.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/jitdump-python.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/jitdump-python.sh

## Purpose

This shell test validates Python `-Xperf_jit` JIT dump integration with perf record, perf inject, build-id cache, and symbolized report output.

## Research

The script sources `lib/setup_python.sh`, probes `${PYTHON} -Xperf_jit` for `sys.is_stack_trampoline_active`, skips if unavailable, and records an inline Python program with nested `foo`, `bar`, and `baz` functions under `perf record -k 1 -g --call-graph dwarf`. It extracts the target PID from `perf report`, runs `DEBUGINFOD_URLS='' perf inject -j`, adds generated `/tmp/jitted-$PID-*.so` files to the build-id cache, counts `py::(foo|bar|baz):<stdin>` symbols in `perf report -s sym`, removes JIT DSOs from the cache, and cleans files. State includes perf data, `.jit` data, `/tmp/jit-$PID.dump`, generated JIT DSOs, and build-id cache entries. Dependencies are a Python with perf JIT support, DWARF call graphs, perf inject JIT support, and shell glob behavior. Risks include PID extraction ambiguity, missing generated DSOs causing glob literal issues, low samples, and global build-id cache mutation. Passing signal is at least one matching Python JIT symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/jitdump-python.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/kallsyms.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/kallsyms.sh

## Purpose

This shell test validates basic `perf kallsyms` lookup behavior for an expected kernel symbol and a deliberately absent name.

## Research

`test_kallsyms` skips if `/proc/kallsyms` is unreadable, uses `schedule` as a common function symbol, and runs `perf kallsyms schedule`. If output is empty or command fails, it checks whether `/proc/kallsyms` contains the symbol and skips on likely permission/kptr restriction issues; otherwise it fails if the output says not found. It then runs `perf kallsyms ErlingHaaland` and fails if it does not report not found. State is only command output and `err`. Dependencies are `/proc/kallsyms`, kernel symbol visibility, and perf kallsyms parsing. Risks include `schedule` not exported/visible on unusual kernels, kptr restrictions causing skip, and the negative sentinel name becoming a real symbol only in contrived builds. Passing signal is successful positive lookup and negative miss behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/kallsyms.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/kvm.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/kvm.sh

## Purpose

This shell test validates `perf kvm` stat, record/report, buildid-list, and live stat modes against a minimal QEMU/KVM process.

## Research

`setup_qemu` chooses a qemu-system binary by architecture, skips if qemu or `/dev/kvm` access is missing, probes permission with `perf kvm stat record -a`, then starts qemu daemonized with KVM, no display, no monitor, and a pidfile. `test_kvm_stat` records KVM events for that pid and requires `VM-EXIT` in stat report. `test_kvm_record_report` starts `perf kvm --host record -p` in the background, interrupts it, and requires `Event count` in report. `test_kvm_buildid_list` expects buildid-list output. `test_kvm_stat_live` runs live stat under timeout and greps a percentage. State includes qemu process, pidfile, perf data, and live log; cleanup kills qemu. Dependencies are QEMU, KVM access, perf KVM events, timeout, and host symbols. Risks include qemu failing without a machine/kernel, permission skips, live output timing, and background recorder interruption races. Passing signal is all KVM subcommands producing expected output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/kvm.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/kwork.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/kwork.sh

## Purpose

This root-only shell test validates `perf kwork` record, report, latency, timehist, and top modes.

## Research

The script skips without root because tracing events are required. `test_kwork_record` records one second of kernel work data to a temp file. `test_kwork_report` requires `Kwork Name`; `test_kwork_latency` requires `Avg delay`; `test_kwork_timehist` requires `Kwork name`; and `test_kwork_top` requires `COMMAND`. State is temporary perf data and `.old` cleanup. Dependencies are tracing permissions, kwork command support, tracepoints for workqueue/irq/softirq style events, and sufficient kernel activity during `sleep 1`. Risks include root-only execution, low activity causing sparse output, output header wording changes, and tracefs conflicts. Passing signal is each subcommand producing its expected header text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/kwork.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/attr.py -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/attr.py

## Purpose

This Python test runner validates perf event attributes emitted through `PERF_TEST_ATTR` against configparser-based expectation files.

## Research

`data_equal` supports exact, wildcard, and `|` alternatives. Exceptions `Fail`, `Notest`, and `Unsup` classify failures, skips, and unsupported perf exits. `Event` stores expected/result event terms and compares all configured perf_event_attr fields. `Test` loads a test file's `[config]`, arch/auxv/kernel gates, expected `[event*]` sections, optional base event inheritance, and then runs perf with `PERF_TEST_ATTR=<tempdir>`. It reloads generated `event*` files, resolves `group_fd` links by fd, and compares expected-to-result and result-to-expected, including group relationships. It can restore a too-low `perf_event_max_sample_rate`. `run_tests` iterates selected files; `main` handles options. State is temp directories containing perf-emitted attr files and optional sysctl sample-rate writes. Dependencies are configparser files under `shell/attr`, perf's `PERF_TEST_ATTR` instrumentation, auxv output, platform release, and root permission for sample-rate restoration. Risks include broad `except` handling, possible `sys.exit` without imported sys in `read_json`-like paths absent here, sysctl mutation, and strict term list needing updates for new attr fields. Passing signal is no unmatched expected/result events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/attr.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/coresight.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/coresight.sh

## Purpose

This sourced shell library centralizes CoreSight perf record options, workload discovery, skip logic, AUX packet sanity checks, and TID/CID validation.

## Research

It sets `PERFRECOPT` to `-m ,16M -e cs_etm//u`, derives `TOOLS`, `DIR`, and `BIN` from the caller's `TEST`, skips if the binary is not executable or `perf list pmu` lacks `cs_etm`, and honors `PERF_TEST_CORESIGHT_DATADIR` and `PERF_TEST_CORESIGHT_STATDIR`. `perf_dump_aux_verify` dumps perf data, counts `I_ATOM_F`, `I_ASYNC`, and `I_TRACE_INFO`, appends CSV stats, and enforces caller-supplied minimums. `perf_dump_aux_tid_verify` reads decimal TIDs from workload stdout and compares them to hex `CID=` or fallback `VMID=` identifiers in the AUX dump. State includes perf temp dump files and stats CSVs. Dependencies are ETMv4-style perf dump text, CoreSight PMU, and caller-defined `TEST`/`DATV`. Risks include packet-name changes, lossy trace causing false failures, use of `dirname $0` when sourced, and a typo in comments only. Passing signals are packet thresholds and complete TID coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/coresight.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/perf_has_symbol.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/perf_has_symbol.sh

## Purpose

This shell helper lets tests skip when the perf test binary lacks a required symbol.

## Research

`perf_has_symbol` runs `perf test -vv -F "Symbols"` and greps for the requested symbol at end of line, printing whether it exists. `skip_test_missing_symbol` calls it and exits 2 on absence. State is none beyond stdout. Dependencies are perf's Symbols selftest output format and grep character classes. Integration is used by annotate and diff tests before recording workloads that rely on named symbols like `noploop` or `test_loop`. Risks include output format changes, demangled/qualified symbol names not matching the simple end-of-line regex, and a missing symbol causing skip rather than fail even when the workload should be present. Test signal is function return 0 for found symbols or process exit 2 for skip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/perf_has_symbol.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/perf_json_output_lint.py -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/perf_json_output_lint.py

## Purpose

This Python linter validates line-delimited `perf stat -j` JSON output against expected keys, value types, and option-specific field counts.

## Research

The script parses flags describing the perf stat mode, reads JSON lines from stdin or `--file`, wraps them into an array, and validates each object. Helpers accept float/int, counter sentinel strings (`<not counted>`, `<not supported>`), metric `none`, and metric thresholds from a fixed set. `check_json_output` rejects unknown keys unless `--metric-only`, checks object length against expected counts for modes such as interval, system-wide, per-core/socket/node/die/cluster/cache, per-thread, event, and metric-only, with allowances for isolated metric values/groups and threshold fields. State is the input lines and parsed args. Dependencies are perf JSON schema documented in the man page and Python `json`. Risks include field-count churn as perf adds keys, `metric-unit`/metric-only exceptions masking unknown keys, and reading all input into memory. Passing signal is no RuntimeError; on failure it prints the original input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/perf_json_output_lint.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/perf_metric_validation.py -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/perf_metric_validation.py

## Purpose

This Python framework validates perf metrics numerically by collecting `perf stat -j -M` results, generating supported rules, checking positive values, single-metric bounds, and relationships among related metrics.

## Research

`TestError` formats missing, out-of-range, and relationship errors. `Validator` loads base rules, discovers metrics from `perf list -j --details metrics`, filters by CPU type, collects metric values through `_run_perf`, converts JSON stderr records into lowercase metric-name values, and stores per-workload results. `pos_val_test` checks nonnegative metrics and reruns a small failing set on a longer workload. `single_test` applies lower/upper/tolerance bounds per metric, also with rerun. `relationship_test` maps aliases, evaluates simple formulas with `+ - * /`, resolves bounds that may reference other metrics, and records failures. `create_rules` merges JSON relationship rules with an auto-generated percentage rule for metrics whose scale unit is `1%` or `100%`; unsupported/skipped metrics are removed. `test` iterates workloads, collects data, applies all rules, prints counts, optionally writes debug JSON, and exits nonzero when errors exist. State includes collected results, skip/ignore sets, output JSON files, and repeated system-wide perf runs. Dependencies are perf metric names/schema, JSON output on stderr, system-wide stat permission, and rule JSON. Risks include formula parser limitations, likely bug using `alias[ub]` while resolving lower-bound aliases, missing `sys` import in `read_json` error path until main imports it, command splitting of workloads by whitespace, and negative values from short workloads causing false errors. Test signals are total/passed counts and empty `errlist`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/perf_metric_validation.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/perf_metric_validation_rules.json -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/perf_metric_validation_rules.json

## Purpose

This JSON file provides base skip lists and metric validation rules consumed by `perf_metric_validation.py`.

## Research

Top-level `SkipList` names metrics excluded from validation, including TSX cycle metrics, package/core residency metrics, and selected TMA false-sharing/remote-cache/contention metrics. `RelationshipRules` define indexed rules with `Formula`, `TestType`, lower/upper ranges, error thresholds, descriptions, and metric/alias lists. Rules validate PMEM and DDR read+write bandwidth totals, NUMA local+remote read percentages, CPI lower bound, ratio metrics in `[0,1]`, TMA level 1 summing to 100%, TMA level 2 children equaling parents, memory page request percentages summing to 100%, CPU utilization relationships, L2/LLC miss-per-instruction relationships, and broad frequency ranges for uncore and CPU operating frequency. State is static validation policy only. Dependencies are exact lowercase metric names emitted by perf metric catalogs and the validator's simple alias/formula grammar. Risks include stale metric names, hardware-specific metrics absent on many systems, tolerance too tight for noisy counters, and rule descriptions carrying product-specific assumptions. Test signal is that supported rules generated from this file pass on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/perf_metric_validation_rules.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/probe.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/probe.sh

## Purpose

This small shell helper provides skip checks for optional `perf probe` and `perf trace` commands.

## Research

`skip_if_no_perf_probe` runs `perf probe` and returns 2 if stderr/stdout contains `is not a perf-command`. `skip_if_no_perf_trace` runs `perf trace -h` and returns 2 for either `is not a perf-command` or `trace command not available`. State is none. Dependencies are user PATH resolving the intended perf binary and command help/error wording. Integration lets shell tests conditionally skip when perf was built without probe or trace support. Risks include localized or changed diagnostic messages, checking the default `perf` rather than `CMD_PERF`, and returning 0 for commands that exist but fail later due to permissions. Test signal is return code 2 for unavailable commands and 0 otherwise.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/probe.sh -->
