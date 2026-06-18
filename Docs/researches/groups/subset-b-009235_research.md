# Research: subset-b-009235

Grouped research for fio histogram/plot tools, fio verification/ZBD/workqueue/trim components, fio unit tests, fs-mark, and the IOR automake fragment.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/tools/hist/fiologparser_hist.py -->
# sources/test-tools/fio/tools/hist/fiologparser_hist.py

Purpose: Python 3 CLI that converts fio `*_clat_hist*` latency histogram logs into interval statistics: end time, sample count, min, average, median, configurable percentiles, and max. It supports mixed or per-direction output (`r`, `w`, `t`, `m`), coarse fio histogram bin layouts, weighted interval accounting, optional job-file interval discovery, and unit conversion through divisors/us-bin mode.

Important APIs/functions: `HistFileRdr` is a simple line reader for unweighted processing. `weighted_percentile()`, `weights()`, and `weighted_average()` implement weighted histogram math. `_plat_idx_to_val()` mirrors fio's platform histogram bin conversion and `plat_idx_to_val_coarse()` adapts reduced/coarsened bins. `histogram_generator()` merges chunked pandas readers in timestamp order. `process_interval()` and `process_weighted_interval()` aggregate bins into output rows. `main()` owns option normalization, column detection, bin-value initialization, direction selection, and output mode dispatch.

Control flow: CLI arguments are parsed, optional fio job config is scanned for `log_hist_msec`, output columns are generated, the first input line determines histogram column count and coarseness, then either unweighted interval aggregation or weighted interval aggregation runs. Weighted mode buffers rows until enough future data exists to account for latency overlap across interval boundaries.

State/persistence: global `percs`, `columns`, histogram column counts, and bin-value arrays are initialized once per run. The script reads log files only and writes CSV-like rows to stdout; warnings go to stderr. It does not write persistent state.

Dependencies/integration: depends on `pandas` and `numpy`; fio-specific integration is the expected log format of time, direction, block size, histogram bins and the histogram math from fio `stat.c`. The `--job-file` parser still uses legacy `SafeConfigParser/readfp` compatibility.

Risks/test signals: risks include `e.message` on `ValueError` not being portable in Python 3, memory growth from repeated `np.append()` in weighted mode, divide-by-zero if all weights are zero, and mis-detection if the first input line is malformed. Good tests would cover empty files, coarseness detection, weighted zero-length samples, direction splits, epoch timestamps, and old microsecond-bin logs.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/tools/hist/fiologparser_hist.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/tools/hist/half-bins.py -->
# sources/test-tools/fio/tools/hist/half-bins.py

Purpose: small Python 3 filter that reduces fio histogram log resolution by merging adjacent latency bins. It is intended for `*_clat_hist*` files and writes a compatible lower-bin-count log to stdout.

Important APIs/functions: `main(ctx)` computes `stride = 1 << ctx.coarseness`, opens the input file, preserves the first three comma-separated fields, parses remaining bins as integers, then emits sums over consecutive `stride`-sized groups. CLI arguments are `FILENAME` and `--coarseness/-c`.

Control flow: every input line is split on `", "`, the metadata fields are copied, histogram bins are transformed with a range step of `stride`, and the final group is emitted using the tail slice. There is no streaming generator abstraction; the file is read with `readlines()`.

State/persistence: read-only input file, stdout output, no persistent state. All per-line state is local lists and counters.

Dependencies/integration: only standard Python modules. Output is meant to feed `fiologparser_hist.py`, which auto-detects reduced histogram column counts.

Risks/test signals: assumes exact comma-space separators and integer bins. The loop `range(0, len(hist) - stride, stride)` plus a final tail sum works for typical evenly divisible fio bin counts but should be tested for one-stride, non-divisible, and very short histograms. Memory usage is proportional to file size because of `readlines()`.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/tools/hist/half-bins.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/tools/plot/fio2gnuplot -->
# sources/test-tools/fio/tools/plot/fio2gnuplot

Purpose: Python 2/3-compatible CLI that transforms fio bandwidth or IOPS logs into intermediate data files, summary statistics, and gnuplot scripts/images. It can select files by glob or predefined `_bw.log`/`_iops.log` patterns, aggregate traces, compute min/max/average/stddev files, optionally render gnuplot, and query prior `.global` summaries.

Important APIs/functions: `find_file()` performs local pattern selection. `compute_temp_file()` reads selected fio logs in lockstep, filters by time range, captures block size, and writes `gnuplot_temp_file.*`. `compute_aggregated_file()` concatenates temp files. `compute_math()` writes `.average`, `.min`, `.max`, `.stddev`, `.global`, and `mymath`. `generate_gnuplot_script()` writes `mygraph` plus compare scripts. `render_gnuplot()` shells out to `gnuplot`. `main()` parses getopt options and orchestrates selection, transformation, math, graph script generation, rendering, and cleanup.

Control flow: after locating fio `*.gpm` templates in `/usr/share/fio/` or `/usr/local/share/fio/`, options determine pattern/title/output paths. Matching logs are sorted, mode is inferred from filename, output basename may be derived from user glob, then global parsing or full data processing runs.

State/persistence: creates many files in the output directory: temp data, aggregate output, math summaries, graph scripts, and optional PNGs. Global lists `temporary_files`, `keep_temp_files`, and `verbose` coordinate cleanup and logging.

Dependencies/integration: uses standard Python plus `six`, filesystem gpm templates, and an external `gnuplot` executable. Expects fio log lines with at least time, performance, and block-size fields.

Risks/test signals: uses `os.system()` with output directory interpolation, has sparse error handling, and `average()` will divide by zero if a trace contributes no samples after filtering. Tests should cover no-match fallback for per-job logs, custom output dir cleanup, min/max filters, multi-file compare script content, missing gpm files, and global summary parsing.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/tools/plot/fio2gnuplot -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/tools/plot/samples/Makefile -->
# sources/test-tools/fio/tools/plot/samples/Makefile

Purpose: sample driver Makefile demonstrating how to unpack archived fio logs and run the plot tooling for IOPS and bandwidth examples.

Important targets: `all` depends on cleanup, extraction, `io`, and `bandwidth`. `m2sw1-128k-sdb-randwrite-para.results_bw.log` extracts `fio-logs.tar.gz`. `setup` symlinks plot scripts/templates from the parent directory. `io` and `bandwidth` call `./fio2gnuplot.py` with read-parallel IOPS or bandwidth glob patterns and `-g` rendering. `clean` removes generated PNGs, temp scripts, symlinks, math files, extracted log directories, and logs.

Control flow/state: Make target dependencies ensure scripts are symlinked before plot commands. The target writes only generated/symlinked sample artifacts in the sample directory.

Dependencies/integration: assumes `fio-logs.tar.gz`, parent `*py` and `*gpm` files, and a `fio2gnuplot.py` executable name even though this source tree also has `fio2gnuplot` without a `.py` suffix.

Risks/test signals: likely bit-rots if script names change, and cleanup is broad (`*log`, `*py`, `*gpm`). A smoke test would run `make -n` and, with sample archive present, ensure both graph paths produce outputs without deleting source files outside the sample directory.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/tools/plot/samples/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/trim.c -->
# sources/test-tools/fio/trim.c

Purpose: implements fio TRIM/DISCARD scheduling helpers when `FIO_HAVE_TRIM` is enabled. It selects pending trim extents, prepares an `io_u` for a discard operation, and decides probabilistically whether a completed write should later be trimmed.

Important APIs/functions: `get_next_trim(td, io_u)` pops the oldest `io_piece` from `td->trim_list`, fills offset/length/file, optionally removes it from verify history if `trim_zero` is disabled, opens and references the file, and configures `io_u` as `DDIR_TRIM`. `io_u_should_trim(td, io_u)` compares a random value from `td->trim_state` against `trim_percentage`.

Control flow: requeued `io_u`s with an existing file are accepted immediately. Empty trim lists return false. Otherwise the selected `io_piece` is either freed after removal from verify structures or marked `IP_F_TRIMMED` so later reads can verify zeroed data.

State/persistence: mutates `td->trim_list`, `td->trim_entries`, `td->io_hist_tree/list`, `td->io_hist_len`, `io_piece` flags, file references, and `io_u` transfer fields. No persistent files are written.

Dependencies/integration: depends on fio list/rbtree IO history, file open/reference helpers, `thread_options.trim_zero`, and verify paths that understand `IP_F_TRIMMED`/`IO_U_F_TRIMMED`.

Risks/test signals: list/tree accounting must stay consistent or verify queues corrupt. Error opening a file after removing the trim entry drops the operation. Tests should cover trim with and without `trim_zero`, requeue path, tree/list removal, and percentage boundaries.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/trim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/trim.h -->
# sources/test-tools/fio/trim.h

Purpose: public header for fio trim/discard support with compile-time stubs when trim is unavailable.

Important APIs/types: declares `get_next_trim()` and `io_u_should_trim()`. Defines `remove_trim_entry(td, ipo)`, which removes an `io_piece` from its trim list and decrements `td->trim_entries` if linked. When `FIO_HAVE_TRIM` is not defined, all three helpers are inline no-ops returning false or doing nothing.

Control flow/state: the real inline helper guards `flist_empty()` before deletion and uses `flist_del_init()` to avoid stale links. This is shared by trim selection and verify selection to keep trim-list membership independent from verify-list membership.

Dependencies/integration: includes fio list, iolog, compiler, type, and OS headers only in trim-enabled builds. Consumers can call the API unconditionally because the header supplies stubs.

Risks/test signals: correctness depends on `td->trim_entries` matching actual list membership. Tests should compile both trim-enabled and trim-disabled configurations and verify that no-op stubs do not evaluate unsupported fields.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/trim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/unittests/cgroup.c -->
# sources/test-tools/fio/unittests/cgroup.c

Purpose: CUnit tests for fio cgroup helper behavior around long paths. The file provides local stubs for fio allocation, logging, and semaphore symbols, includes `../cgroup.c` directly, and registers cgroup-specific tests on Linux/Android.

Important APIs/functions: `test_path_join()` builds dynamic path strings. `test_get_cgroup_root_long_path()` verifies `get_cgroup_root()` can concatenate a long cgroup name under a mount path and preserve lengths over 64 bytes without setting `td.error`. `test_write_int_to_file_long_path()` creates a temporary long directory, calls `write_int_to_file()`, then reads back `blkio.weight`.

Control flow/state: tests allocate temporary memory and directories under `/tmp/fio-cgroup-XXXXXX`, assert each operation, then unlink/rmdir cleanup. Stubbed `smalloc`, `scalloc`, `sfree`, and `smalloc_strdup` map to libc.

Dependencies/integration: uses CUnit, fio `thread_data`, direct inclusion of production cgroup code, libc filesystem APIs, and platform guards from `unittest.h`.

Risks/test signals: direct inclusion is fragile to new external symbols in `cgroup.c`. The long-path tests are good regression signals for fixed-size buffer truncation. Cleanup only runs after successful fatal assertions, so failures can leave temp directories.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/unittests/cgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/unittests/lib/memalign.c -->
# sources/test-tools/fio/unittests/lib/memalign.c

Purpose: CUnit smoke test for fio's internal aligned allocation helper.

Important APIs/functions: `test_memalign_1()` calls `__fio_memalign(4096, 1234, malloc)` and, if allocation succeeds, asserts the returned pointer is aligned to 4096 bytes. `fio_unittest_lib_memalign()` registers the suite as `lib/memalign.c`.

Control flow/state: one allocation is performed and checked. The test does not free the returned pointer in this file, so its scope is a short-lived unit-test process.

Dependencies/integration: includes `../../lib/memalign.h`, CUnit wrappers from `../unittest.h`, and libc `malloc`.

Risks/test signals: pointer alignment is checked by casting to `int`, which can truncate on 64-bit platforms; using `uintptr_t` without narrowing would be safer. It does not assert non-NULL, so allocation failure silently passes. Additional tests should cover multiple alignments, invalid alignments, and freeing.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/unittests/lib/memalign.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/unittests/lib/num2str.c -->
# sources/test-tools/fio/unittests/lib/num2str.c

Purpose: CUnit tests for numeric-to-string helpers in fio's `lib/num2str.h`.

Important APIs/functions: `test_num2str()` iterates table-driven cases for `num2str()` including `UINT64_MAX`, shortened SI output, and precision/length constraints. `test_bytes2str_simple()` checks fixed binary byte-unit formatting from bytes through EiB and asserts the returned pointer equals the caller buffer. `fio_unittest_lib_num2str()` registers both tests.

Control flow/state: table arrays define inputs and expected strings. Each `num2str()` result is freed after assertion; `bytes2str_simple()` uses a stack buffer.

Dependencies/integration: depends on fio compiler array-size macro, `num2str()` allocation semantics, `bytes2str_simple()` buffer semantics, and CUnit.

Risks/test signals: tests cover important boundary values but not every base/unit/power-of-two combination. They also assume exact decimal text, so formatting changes are caught. Missing cases include small buffer behavior and invalid units.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/unittests/lib/num2str.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/unittests/lib/pcbuf.c -->
# sources/test-tools/fio/unittests/lib/pcbuf.c

Purpose: CUnit tests for fio's producer/consumer circular buffer (`pcbuf.h`) using a deliberately small capacity to exercise full, empty, commit, and wrap-around behavior.

Important APIs/functions: `test_pcbuf_basic_ops()` allocates a buffer, checks initial state, stages `capacity - 1` values, verifies the reserved-slot full condition, commits, pops values in FIFO order, and checks empty state. `test_pcbuf_wraparound()` commits near-capacity data, pops one element, stages another value to wrap, then verifies the remaining sequence.

Control flow/state: staged entries are invisible to committed pop size until `pcb_commit()`. The tests explicitly distinguish `pcb_staged_size()` from `pcb_committed_size()`.

Dependencies/integration: includes `pcbuf.h` from the unit-test lib directory and CUnit wrappers.

Risks/test signals: strong regression coverage for ring-index arithmetic. Missing coverage includes allocation failure, multiple commits without pops, staged rollback if supported elsewhere, and concurrent producer/consumer use.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/unittests/lib/pcbuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/unittests/lib/strntol.c -->
# sources/test-tools/fio/unittests/lib/strntol.c

Purpose: CUnit tests for bounded string-to-long parsing.

Important APIs/functions: `test_strntol_1()` parses a simple decimal string. `test_strntol_2()` checks leading whitespace. `test_strntol_3()` parses a hexadecimal string with explicit base 16. Each verifies the numeric result, non-NULL end pointer, and end-of-string termination. `fio_unittest_lib_strntol()` registers the suite.

Control flow/state: each test uses a local mutable string and passes its exact `strlen()` length to `strntol()`.

Dependencies/integration: depends on `../../lib/strntol.h` and CUnit. It validates compatibility with libc-style `strtol` behavior while respecting a maximum length.

Risks/test signals: good basic parser coverage, but missing invalid input, overflow/underflow, truncated length, sign handling, base auto-detection, and end-pointer positioning before the provided length.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/unittests/lib/strntol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/unittests/oslib/strcasestr.c -->
# sources/test-tools/fio/unittests/oslib/strcasestr.c

Purpose: CUnit tests for either fio's fallback `strcasestr()` or the platform implementation, depending on `CONFIG_STRCASESTR`.

Important APIs/functions: three tests cover numeric haystacks, uppercase haystacks, and mixed-case needles. They assert matches at the start, matches at offset one, no match when needle is longer/nonmatching, and empty needle returning the haystack pointer.

Control flow/state: all tests use string literals and compare returned pointers directly against expected offsets.

Dependencies/integration: includes `../../oslib/strcasestr.h` when the platform lacks `strcasestr`; otherwise includes `<string.h>`. Registered by `fio_unittest_oslib_strcasestr()`.

Risks/test signals: tests encode GNU/BSD empty-needle behavior and case-insensitive semantics. Missing cases include NULL handling, locale-sensitive characters, repeated partial matches, and non-ASCII behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/unittests/oslib/strcasestr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/unittests/oslib/strlcat.c -->
# sources/test-tools/fio/unittests/oslib/strlcat.c

Purpose: CUnit tests for fio's fallback or platform `strlcat()`.

Important APIs/functions: `test_strlcat_1()` appends `"test"` into an empty 32-byte destination and expects destination text plus return value 4. `test_strlcat_2()` passes `strlen(dst)` as size while `dst` is empty, expecting no modification and return value equal to source length.

Control flow/state: stack buffers are reset per test. Pointer/string comparisons use CUnit assertions.

Dependencies/integration: includes fio fallback `../../oslib/strlcat.h` unless `CONFIG_STRLCAT` selects libc.

Risks/test signals: verifies basic append and zero-size semantics. Missing coverage includes truncation with non-empty destination, return value under truncation, exact-fit buffers, and unterminated destination edge cases.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/unittests/oslib/strlcat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/unittests/oslib/strndup.c -->
# sources/test-tools/fio/unittests/oslib/strndup.c

Purpose: CUnit tests for fallback or platform `strndup()`.

Important APIs/functions: tests duplicate `"test"` with lengths 3, 4, and 5, expecting truncation to `"tes"`, exact copy, and copy limited by source NUL respectively. `fio_unittest_oslib_strndup()` registers the suite.

Control flow/state: each test allocates with `strndup()` and only asserts if the pointer is non-NULL. The allocated buffers are not freed, which is acceptable for short test execution but not leak-clean.

Dependencies/integration: includes `../../oslib/strndup.h` unless `CONFIG_HAVE_STRNDUP` selects libc.

Risks/test signals: validates NUL-termination and length limiting. Missing cases include zero length, allocation failure behavior, embedded NULs, and freeing in tests to satisfy leak checkers.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/unittests/oslib/strndup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/unittests/oslib/strsep.c -->
# sources/test-tools/fio/unittests/oslib/strsep.c

Purpose: CUnit tests for fallback or platform `strsep()`.

Important APIs/functions: `test_strsep_1()` checks NULL `*stringp` returns NULL. `test_strsep_2()` verifies no-delimiter cases return the whole string and set `stringp` NULL. `test_strsep_3()` uses delimiters `"ABC"` against `"ABCDEFG"` to verify delimiter overwrite with NUL and pointer advancement through consecutive delimiters.

Control flow/state: mutable stack strings are modified in place, matching `strsep()` semantics. Returned token pointers and updated `string` values are asserted after each call.

Dependencies/integration: includes `../../oslib/strsep.h` unless `CONFIG_STRSEP` selects libc.

Risks/test signals: good coverage for NULL, empty delimiter, no delimiter, and delimiter overwrite behavior. Missing cases include repeated delimiters in the middle, trailing delimiters, and multi-character delimiter sets beyond first-character positions.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/unittests/oslib/strsep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/unittests/unittest.c -->
# sources/test-tools/fio/unittests/unittest.c

Purpose: main CUnit test runner for fio unit tests.

Important APIs/functions: `fio_unittest_add_suite()` wraps `CU_add_suite()` and iterates a NULL-terminated `fio_unittest_entry` array to add tests. `fio_unittest_register()` exits on registration failure. `main()` initializes the CUnit registry, registers all lib/oslib suites and platform cgroup suite, runs tests in verbose basic mode, cleans up, and returns the CUnit error code.

Control flow/state: failures during suite creation clean up the CUnit registry immediately. Registration order is fixed and mirrors prototypes in `unittest.h`.

Dependencies/integration: depends on CUnit Basic, all suite registration functions, and Linux/Android guards for cgroup tests.

Risks/test signals: if a suite function has unresolved production dependencies, the entire binary fails to link. Returning `CU_get_error()` after `CU_basic_run_tests()` reports framework errors rather than necessarily failed assertions, so CI integration must inspect CUnit behavior. Tests should verify nonzero exit on failed registration.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/unittests/unittest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/unittests/unittest.h -->
# sources/test-tools/fio/unittests/unittest.h

Purpose: shared declaration header for fio's CUnit test binary.

Important APIs/types: defines `struct fio_unittest_entry { const char *name; CU_TestFunc fn; }`, declares `fio_unittest_add_suite()`, and declares registration functions for lib, oslib, and cgroup suites. The cgroup registration is guarded to Linux/Android.

Control flow/state: suite arrays are expected to be NULL-terminated by `name == NULL`; `fio_unittest_add_suite()` relies on that contract.

Dependencies/integration: includes `<sys/types.h>`, CUnit core, and CUnit Basic. It is included by every unit-test implementation and the runner.

Risks/test signals: adding a new unit-test file requires adding a prototype here and a registration call in `unittest.c`. A malformed test vector without a NULL terminator can overrun memory during registration.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/unittests/unittest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/verify-state.h -->
# sources/test-tools/fio/verify-state.h

Purpose: wire-format and helper declarations for fio verify-state save/load files. These files allow later verification runs to know random offset state, inflight writes, failed writes, and stop thresholds.

Important APIs/types: `thread_rand32_state`, `thread_rand64_state`, and `thread_rand_state` serialize random generator state. `inflight_write` stores `numberio`. `thread_io_list` is a variable-length per-thread record with depth, threshold `numberio`, thread index, RNG state, job name, and inflight array. `all_io_list` aggregates thread records. `verify_state_hdr` stores version, size, and CRC. Inline helpers compute record sizes, walk to the next record, and generate escaped state filenames.

Control flow/state: consumers write a header followed by one `thread_io_list`; sizes are little-endian on disk. `verify_state_gen_name()` replaces `/` with `.` and emits `<prefix>-<escaped-name>-<num>-verify.state`.

Dependencies/integration: includes endian helpers indirectly from fio headers, `PATH_MAX`, and `nowarn_snprintf`. Implemented by `verify.c`.

Risks/test signals: variable-length structs require exact size calculations and endian conversion. State-file compatibility depends on `VSTATE_HDR_VERSION`. Tests should cover filename escaping, CRC rejection, version rejection, and mixed-depth state walking.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/verify-state.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/verify.c -->
# sources/test-tools/fio/verify.c

Purpose: core fio data verification implementation. It generates verify patterns/checksum headers for writes, verifies read data against headers/patterns/zeroed trim results, offloads verification to async threads, and saves/loads verify state for offline or interrupted verification.

Important APIs/functions: exported entry points include `fill_buffer_pattern()`, `fill_verify_pattern()`, `populate_verify_io_u()`, `get_next_verify()`, `verify_io_u()`, `verify_io_u_async()`, `fio_verify_init()`, `verify_async_init()/exit()`, `paste_blockoff()`, `get_all_io_list()`, `verify_save_state()/load_state()/assign_state()/free_state()`, and verify-state skip/stop helpers. Internal checksum handlers cover MD5, CRC7/16/32/32C/64, SHA1, SHA256, SHA512, SHA3 variants, XXHASH, header-only, pattern, pattern-no-header, zero verification, and trimmed-zero verification.

Control flow: write preparation calls `populate_verify_io_u()`, which fills data and places headers at each verify interval. Read verification skips null/fake/device-verified cases, handles trimmed/zeroed flags, then walks every verify interval, validates the common header, selects the verify type, computes checksum or pattern comparison, logs detailed failures, and optionally dumps received/expected buffers. Async mode queues `io_u`s on `td->verify_list`; detached verifier threads drain lists, call `verify_io_u()`, update nonfatal errors, and signal exit.

State/persistence: mutates `io_u` flags, file refs, verify queues, `td->io_hist_tree/list`, `td->io_hist_len`, RNG seeds, async thread counters, and failure counts. Persistent verify-state files are named by `verify_state_gen_name()`, written with `O_SYNC`, include header CRC/version/size, and serialize inflight plus failed `numberio` values. Dump files may be written under `aux_path` on verify failures.

Dependencies/integration: deeply coupled to fio thread/job options, IO history, trim, file lifecycle, CRC/hash libraries, random/pattern helpers, pthreads, endian helpers, and global thread iteration macros.

Risks/test signals: high-risk areas are header-size vs block-size validation, `verify_offset` header swaps, async pattern formatting with offset placeholders, `np` not applicable here but C buffer bounds, failure dump filenames, detached-thread shutdown, and verify-state compatibility. Strong tests should cover every verify type, partial intervals, trim-zero reads, verify-fatal termination, fsynced policy thresholds, failed-numberio skip, corrupted state CRC, and cross-version header rejection.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/verify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/verify.h -->
# sources/test-tools/fio/verify.h

Purpose: public definitions for fio verification modes, verify headers, checksum-specific private header payloads, and exported verify APIs.

Important APIs/types: `FIO_HDR_MAGIC`, `VERIFY_HEADER_VERSION`, `enum VERIFY_*` modes, `VERIFY_POLICY_*` bits, `struct verify_header`, and `vhdr_*` checksum payload structs. Declares write-population, next-verify selection, sync/async verification, pattern filling, verifier initialization, async thread lifecycle, and pattern format callback `paste_blockoff()`.

Control flow/state: the common header precedes optional checksum payload and data for most verify modes. `VERIFY_PATTERN_NO_HDR` is explicitly headerless. The high bit in the version distinguishes versioned headers from older formats.

Dependencies/integration: includes `verify-state.h` and compiler annotations. Consumed by fio IO path, ZBD code, trim handling, and state save/load users.

Risks/test signals: enum value changes can affect media compatibility; header layout is on-disk/on-media ABI. Tests should ensure `__hdr_size()` expectations match these structs and that old configurations mapping `verify=meta` to header-only remain compatible.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/verify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/workqueue.c -->
# sources/test-tools/fio/workqueue.c

Purpose: generic pthread-backed workqueue used by fio to offload submit/work processing to a bounded set of worker threads.

Important APIs/functions: `workqueue_init()` initializes locks/conds, allocates workers, starts threads, and waits until all are running. `workqueue_enqueue()` chooses an idle or least-recent worker, appends work, updates sequence, and signals. `workqueue_flush()` waits until all workers report idle. `workqueue_exit()` signals exit, joins workers, runs callbacks, and frees resources. Internal `worker_thread()` initializes per-worker state, optionally applies nice value, loops over work lists, calls pre-sleep hooks, executes `ops.fn`, and updates accounting.

Control flow/state: workers own `work_list`, flags (`IDLE`, `RUNNING`, `EXIT`, `ACCOUNTED`, `ERROR`), sequence, and callback-private state. The queue tracks `next_free_worker`, `work_seq`, `wake_idle`, and synchronization objects. Flush is caller-serialized with enqueue.

Dependencies/integration: depends on fio smalloc/sfree, pshared mutex/cond helpers, `flist`, `sk_out` assignment, pthreads, and callback vtable from `workqueue_ops`.

Risks/test signals: start failure after `alloc_worker_fn` may leak callback-private resources if mutex init failed before cleanup. Race safety depends on documented caller serialization. Tests should cover enqueue distribution, flush with pre-sleep callbacks, worker init failure, callback error accounting, and exit with pending work.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/workqueue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/workqueue.h -->
# sources/test-tools/fio/workqueue.h

Purpose: public interface and data structures for fio's generic submit workqueue.

Important APIs/types: `workqueue_work` embeds a list node. `submit_worker` stores thread, lock/cond, list, flags, index, sequence, parent queue, private pointer, and output routing. Function typedefs define callback contracts for work execution, pre-sleep flushing, worker allocation/free/init/exit, and accounting. `workqueue_ops` groups callbacks and nice value. `workqueue` stores worker array, locks/conds, max worker count, thread data, and scheduling fields.

Control flow/state: inline helpers invoke optional callbacks with safe defaults. `workqueue_exit_worker()` passes a temporary sum counter if the caller supplies none.

Dependencies/integration: includes pthreads, fio list/type headers, and forward declarations for `thread_data` and `sk_out`.

Risks/test signals: the header exposes internal structs, so callers can accidentally depend on flags and locking. Callback signatures must remain stable. Tests should compile at least one real workqueue user and verify optional callback omissions.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/workqueue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/zbd.c -->
# sources/test-tools/fio/zbd.c

Purpose: fio zoned block device (ZBD) implementation. It discovers or emulates zone geometry, validates job options, tracks per-zone write pointers and open/write-zone limits, adjusts IO offsets/lengths for zoned rules, handles zone resets/finishes/trims, and recovers selected write-pointer errors.

Important APIs/functions: setup exports include `zbd_init_files()`, `zbd_recalc_options_with_zone_granularity()`, `zbd_setup_files()`, `zbd_free_zone_info()`, and `zbd_file_reset()`. Runtime exports include `setup_zbd_zone_mode()`, `zbd_adjust_ddir()`, `zbd_adjust_block()`, `zbd_do_io_u_trim()`, `zbd_queue_io_u()`/`zbd_put_io_u()` through callbacks, `zbd_write_status()`, `zbd_log_err()`, and `zbd_recover_write_error()`. Internals cover zone report/reset/finish/move/get-limit wrappers, write-zone get/put, zone locking, write-target selection, readable-zone search, and valid-data-byte accounting.

Control flow: initialization obtains the zoned model through ioengine or block helpers, parses real zone reports or creates emulated zones, shares `zbd_info` among identical files, sets max write-zone limits, validates direct I/O and block sizes, aligns ranges to zone boundaries, and records min/max zones. At IO time `zbd_adjust_block()` locks the target sequential zone, validates read/write/trim semantics, may select another zone, shrink length, reset zones, or return EOF. Accepted sequential-zone IOs leave the zone lock held and install queue/put callbacks; those callbacks advance write pointers and unlock on completion/busy/error.

State/persistence: persistent device state is affected through zone reset, finish, and write-pointer move operations. In-memory state lives in `zoned_block_device_info` and `fio_zone_info`: mutexes, wp, capacity, conditions, write target array, refcount, valid-data bytes, reset counters, inflight writes, and write-error repair fields.

Dependencies/integration: depends on fio file/thread/job options, ioengine zoned callbacks, `oslib/blkzoned`, verify/trim logic, direct-IO policy, smalloc/pshared, and fio statistics.

Risks/test signals: this is concurrency- and device-state-sensitive code. Risks include lock-order regressions between zone mutex and device mutex, stale zone reports, incorrect range alignment, data loss if resets occur while verify data remains, zone-limit off-by-one errors, and async write-error recovery assumptions. Tests should include emulated zones, host-managed devices, conventional-zone crossings, read-before-write, trim as reset, max_open/job_max_open limits, zone capacity smaller than size, verify-enabled random writes, and recovery paths.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/zbd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/zbd.h -->
# sources/test-tools/fio/zbd.h

Purpose: public ZBD interface and main in-memory zone/device state definitions.

Important APIs/types: `enum io_u_action` communicates accept/eof/completed decisions. `struct fio_zone_info` stores per-zone mutex, start, write pointer, capacity, inflight/error counters, type, condition, and flags (`has_wp`, `write`, `reset_zone`, `fixing_zone_wp`). `struct zoned_block_device_info` stores model, max write/active zones, mutex, zone size/log2, valid data bytes, write range, zone count, refcount, write target array, and flexible zone array. Function declarations expose setup, close, IO adjustment, trim, stats, error logging, and recovery.

Control flow/state: inline `zbd_close_file()` frees shared zone info. `zbd_queue_io_u()` and `zbd_put_io_u()` dispatch per-`io_u` callbacks set by `zbd_adjust_block()` and clear callback pointers afterward.

Dependencies/integration: includes fio `io_u`, ioengine, block-zoned abstraction, and `zbd_types.h`.

Risks/test signals: struct fields are mutated under specific locks documented mostly in `zbd.c`; callers must not bypass callback cleanup. Header tests should compile users with and without zoned IO engines and validate flexible-array sizing assumptions.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/zbd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/zbd_types.h -->
# sources/test-tools/fio/zbd_types.h

Purpose: standalone ZBD type and constant definitions shared by fio ZBD code and lower-level zoned abstractions.

Important APIs/types: `ZBD_MAX_WRITE_ZONES` caps tracked write target zones at 4096. `enum zbd_zoned_model` defines none, host-aware, and host-managed models. `enum zbd_zone_type` defines conventional, sequential-write-required, sequential-write-preferred, and sequential-before-required values. `enum zbd_zone_cond` mirrors zone conditions such as empty, implicit/explicit open, closed, read-only, full, and offline. `struct zbd_zone` is a zone-report descriptor with start, write pointer, length, capacity, type, and condition.

Control flow/state: no executable logic; used as ABI-like shared definitions.

Dependencies/integration: includes `<inttypes.h>`. Consumed by `zbd.c`, `zbd.h`, and `oslib/blkzoned` adapters.

Risks/test signals: enum values must match kernel/ioengine reports. Any change risks misinterpreting zone conditions. Compile-time tests should verify expected numeric constants when adapting to new platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/zbd_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/zone-dist.c -->
# sources/test-tools/fio/zone-dist.c

Purpose: precomputes lookup tables for fio zone split distributions so hot IO paths can map access percentages to size ranges quickly.

Important APIs/functions: `td_zone_gen_index(td)` checks whether any direction has zone splits, allocates `td->zone_state_index`, and builds 100-entry indexes per direction. `td_zone_free_index(td)` frees every direction index and clears pointers. Internal `__td_zone_gen_index()` expands each configured `zone_split` entry across its access-percentage range with cumulative size percentages and byte sizes. `has_zones()` checks configured split counts across read/write/trim directions.

Control flow/state: for each direction, cumulative previous size/access counters are advanced across configured split entries; each access-percent bucket records current and previous cumulative size boundaries.

Dependencies/integration: depends on `thread_data`, `thread_options.zone_split_nr`, `zone_split`, `zone_split_index`, and `DDIR_RWDIR_CNT` from fio core headers.

Risks/test signals: allocation assumes exactly 100 percentage buckets and does not check `malloc()` failure. Misconfigured access percentages not summing to 100 can leave uninitialized buckets or overrun. Tests should cover no splits, exact 100, under/over totals, and freeing after partial allocation.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/zone-dist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/zone-dist.h -->
# sources/test-tools/fio/zone-dist.h

Purpose: minimal public header for fio zone-distribution index lifecycle.

Important APIs/functions: declares `td_zone_gen_index(struct thread_data *td)` and `td_zone_free_index(struct thread_data *td)`.

Control flow/state: no implementation; callers allocate indexes before workloads that use `zone_split` and free them during teardown.

Dependencies/integration: relies on `struct thread_data` being visible or forward-declared by includers. Implemented by `zone-dist.c`.

Risks/test signals: because the header does not forward declare `struct thread_data`, include ordering matters. Compile coverage should include direct inclusion in translation units that already include fio core headers.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/zone-dist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fs-mark/Makefile -->
# sources/test-tools/fs-mark/Makefile

Purpose: simple build/test Makefile for the `fs_mark` filesystem metadata benchmark.

Important targets/variables: `COBJS` lists `fs_mark.o lib_timing.o`. `CC`, `CFLAGS`, and `LDFLAGS` are overrideable; `CFLAGS` adds `-Wall -D_FILE_OFFSET_BITS=64`. `all` builds `fs_mark`. `fs_mark.o` depends on source/header. `fs_mark` links both objects. `test` runs four benchmark variants against `DIR1` and `DIR2` with fixed size/count and optional random names/subdirectories. `clean` removes objects, binary, and `fs_log.txt`.

Control flow/state: build is conventional compile/link. The `test` target writes many files under `/test/dir1` and `/test/dir2` by default and can fill or stress those filesystems.

Dependencies/integration: requires a C compiler, Linux-oriented headers used by fs_mark, writable test directories, and `lib_timing.c`.

Risks/test signals: default test directories are absolute and may not exist or may be unsafe on shared systems. Build smoke tests should override `DIR1`/`DIR2` to temporary paths.
<!-- END_FILE_RESEARCH: sources/test-tools/fs-mark/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fs-mark/fs_mark.c -->
# sources/test-tools/fs-mark/fs_mark.c

Purpose: `fs_mark` benchmark for synchronous/asynchronous file creation and metadata operations. It creates many files across one or more directories/processes, writes fixed-size zero buffers, optionally fsyncs/syncs in several policies, optionally unlinks files, aggregates per-child timing logs, and reports files/sec plus syscall timing statistics.

Important APIs/functions: `process_args()` parses benchmark options and assigns directories/threads. `setup_file_name()` selects subdirectory policy and generates timestamp/random filenames. `setup()` opens per-child logs and prepares directories/buffers. `write_file()` chunks writes and records write latencies. `do_run()` performs one child iteration: create/write/fsync/close/post-fsync/unlink, then writes a 19-field child log row. `fork_threads()` forks child workers and waits. `process_child_log_file()` reads and removes per-child logs. `aggregate_thread_stats()` combines child stats. `print_run_info()` and `print_iteration_stats()` report headers/results. `main()` loops until requested iterations, fill mode, or SIGINT, then prints average and p50/p90/p99 files/sec.

Control flow: parent parses options, opens master log, installs SIGINT handler, then repeatedly forks children. Each child runs setup and one iteration, writing a private `<log>.<pid>` file. Parent waits, aggregates all child logs, prints to stdout and master log, records files/sec for final percentiles, then repeats.

State/persistence: global configuration and stats dominate the program. It creates benchmark directories/subdirectories, benchmark files, per-child transient logs, and an append-mode master log. `keep_files`, fill mode, and loop count determine whether files persist. `do_fill_fs` plus `check_space()` controls fill-until-full mode.

Dependencies/integration: Linux-focused C program using `statfs`, fork/wait, signals, `open/write/fsync/sync/close/unlink`, `gettimeofday`, and timing helpers from `lib_timing.c`. `fs_mark.h` owns constants, globals, structs, policy strings, and prototypes.

Risks/test signals: many fixed-size `sprintf`/`strncat` operations risk path/name overflow if validation misses combinations. Children inherit global state after fork; per-child log parsing is brittle to format changes. `files_per_sec` is stored as integer for percentile sorting despite float stats. Default cleanup on errors exits and removes only child logs, not benchmark files. Tests should run in temp dirs for single/multi-thread, keep/unlink, sync policies, subdir policies, loop count, SIGINT, and path-length boundaries.
<!-- END_FILE_RESEARCH: sources/test-tools/fs-mark/fs_mark.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fs-mark/fs_mark.h -->
# sources/test-tools/fs-mark/fs_mark.h

Purpose: shared constants, global configuration/state, structs, strings, buffer storage, and timing prototypes for `fs_mark.c`.

Important APIs/types: defines maximums (`MAX_IO_BUFFER_SIZE`, `MAX_FILES`, `MAX_THREADS`, path/name/string sizes), defaults, directory policies, sync policy bits and composite methods, global runtime options (`io_buffer_size`, `file_size`, `num_files`, subdir settings, sync method, logging, loop/file counts), static IO/name buffers, `struct name_entry`, `child_job_t`, and `fs_mark_stat_t`. Declares timing helpers `start()`, `stop()`, and `tvnow()`.

Control flow/state: because this header defines globals rather than declaring externs, it is intended for a small program with one main translation unit including it. Policy string arrays are also defined here and used by reporting.

Dependencies/integration: relies on `PATH_MAX` and `FILE` being available before inclusion via `fs_mark.c` includes. `lib_timing.c` supplies timing functions.

Risks/test signals: defining globals in a header would create multiple-definition problems if included by more than one linked source. Fixed-size buffers drive many fs_mark path risks. Compile/link tests should ensure only `fs_mark.c` includes it as a definition header.
<!-- END_FILE_RESEARCH: sources/test-tools/fs-mark/fs_mark.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fs-mark/lib_timing.c -->
# sources/test-tools/fs-mark/lib_timing.c

Purpose: small timing utility library for fs_mark/lmbench-style benchmarks using microsecond-resolution wall-clock time.

Important APIs/functions: `tvnow()` returns current epoch time in microseconds. `start(tv)` stores current time into caller-supplied `timeval` or a static default. `tvsub(tdiff, t1, t0)` subtracts timevals with underflow handling and clamps backwards time to zero. `tvdelta(start, stop)` returns microsecond delta. `stop(begin, end)` captures stop time if needed and returns elapsed microseconds.

Control flow/state: two static `timeval`s (`start_tv`, `stop_tv`) provide implicit timer storage when callers pass NULL. Most fs_mark calls use this implicit global timer around individual syscalls.

Dependencies/integration: includes POSIX time/filesystem headers and libc. Used by `fs_mark.c`.

Risks/test signals: static implicit timers are not thread-safe across real threads, but fs_mark uses forked processes so each child gets its own copy. Wall-clock `gettimeofday()` can move backwards; the code clamps to zero. Tests should verify null and explicit timer paths, negative adjustment behavior, and microsecond arithmetic.
<!-- END_FILE_RESEARCH: sources/test-tools/fs-mark/lib_timing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/Makefile.am -->
# sources/test-tools/ior/src/Makefile.am

Purpose: Automake build definition for IOR, mdtest, md-workbench, the shared `libaiori.a`, optional backend AIORI modules, capability-uppercase binaries, and build flag export.

Important targets/variables: `bin_PROGRAMS` builds `ior`, `mdtest`, and `md-workbench`, with uppercase variants under `USE_CAPS`. `noinst_HEADERS` lists internal headers. `libaiori_a_SOURCES` starts with core sources. Each program has source, flags, LDADD, and CPPFLAGS variables. Conditional blocks append backend sources and libraries for HDFS, CUDA/GPU Direct, HDF5, IME, MPIIO, NCMPI, MMAP, POSIX, AIO, PMDK, RADOS, CEPHFS, LIBNFS, DAOS, GFARM, CHFS, FINCHFS, S3 variants, and Lustre. Uppercase program variables mirror lowercase ones. `all-local: build.conf` writes effective LDFLAGS and CFLAGS. `.cu.o` compiles CUDA sources with `NVCC`.

Control flow/state: automake conditionals select optional modules at configure time, then shared `extra*` variables are appended to all main programs and the static library. `build.conf` is regenerated during local build.

Dependencies/integration: tied to autotools conditionals from configure scripts and external storage/HPC libraries. GPU Direct adds C++ linkage through `-lstdc++`.

Risks/test signals: optional backend flags can leak into all programs and duplicate sources in both program and library lists. Hard-coded HDFS paths are brittle. Build tests should exercise minimal POSIX, MPI, CUDA/GPU, and several optional backend configure combinations, plus distcheck for generated `build.conf`.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/Makefile.am -->
