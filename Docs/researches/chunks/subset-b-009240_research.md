# sources/test-tools/iozone/src/current/iozone.c lines 1-7579

## Scope

This chunk covers the first 7,579 lines of `sources/test-tools/iozone/src/current/iozone.c`, the front half of the monolithic Iozone filesystem benchmark implementation. The file continues after this chunk, so this report describes only the visible chunk and calls out cross-chunk dependencies where behavior is declared or invoked here but implemented later.

## Purpose

The covered code initializes Iozone's portable benchmark runtime, parses the complete command-line surface, defines global state used by all benchmark modes, dispatches single-stream tests, implements auto-mode iteration, implements most of the multi-process/thread throughput orchestrator, defines timing/cache/data-verification helpers, and begins the single-stream write/rewrite benchmark implementation.

At a high level, this chunk turns user options into global flags and sizes, allocates aligned working buffers, decides between throughput, auto, speed-test, distributed-client, or one-shot benchmark execution, and funnels work into the function dispatch table or throughput worker functions. The later chunks contain many of the actual read/random/pread/pwrite/thread/distributed worker bodies referenced here.

## Important APIs, Types, and Constants

The source is heavily conditionalized for old Unix, Windows, large-file, direct-I/O, mmap, async-I/O, pthread, and distributed modes.

Key portability wrappers:

- `I_LSEEK`, `I_OPEN`, `I_CREAT`, `I_FOPEN`, `I_STAT`, `I_PREAD`, `I_PWRITE`, and `I_MMAP` map to 64-bit variants when `_LARGEFILE64_SOURCE` is available, otherwise to standard POSIX calls.
- `off64_t` is typedefed on platforms that do not provide it.
- `MAP_FAILED`, `MAP_ANONYMOUS`, `MAP_FILE`, `O_SYNC`, and `O_RSYNC` receive compatibility definitions for older or non-Linux targets.
- `MODE` records whether the build is compiled for 32-bit or 64-bit pointer/offset assumptions.

Important data types visible in this chunk:

- `struct child_stats`: shared-memory result/control cell for throughput children. Fields include `flag`, `walltime`, `cputime`, `throughput`, and `actual`.
- `struct runtime`: wall time, CPU time, and CPU utilization stored alongside report arrays for spreadsheet/report output.
- `struct client_command`: native in-memory command message sent from distributed master to clients.
- `struct client_neutral_command`: string-encoded portable version of `client_command`, constrained by comments to stay below 1448 bytes to avoid fragmentation.
- `struct master_command`: native client-to-master result/status message.
- `struct master_neutral_command`: string-encoded portable version of `master_command`.
- `struct size_entry`: linked-list node for file-size and record-size iteration lists.
- `struct child_ident`: distributed-mode registry entry for each client, including host/workdir/executable/file information, ports, socket indexes, and state.

Important constants and control values:

- Default benchmark sizing: `KILOBYTES`, `RECLEN`, `FILESIZE`, `NUMRECS`, `KILOBYTES_START`, `KILOBYTES_END`, `RECLEN_START`, `RECLEN_END`, `MULTIPLIER`.
- Limits: `MAXBUFFERSIZE`, `MINBUFFERSIZE`, `MAXSTREAMS`, `MAXTESTS`, `MAX_X`, `MAX_Y`, `MAXNAMESIZE`.
- Test indexes/masks: `WRITER_TEST`, `READER_TEST`, `RANDOM_RW_TEST`, `REVERSE_TEST`, `REWRITE_REC_TEST`, `STRIDE_READ_TEST`, `FWRITER_TEST`, `FREADER_TEST`, `RANDOM_MIX_TEST`, plus `PWRITER_TEST`, `PREADER_TEST`, `PWRITEV_TEST`, `PREADV_TEST` when available.
- Child barrier states: `CHILD_STATE_HOLD`, `CHILD_STATE_READY`, `CHILD_STATE_BEGIN`, `CHILD_STATE_DONE`.
- Distributed message commands: `R_CHILD_JOIN`, `R_STAT_DATA`, `R_FLAG_DATA`, `R_JOIN_ACK`, `R_STOP_FLAG`, `R_TERMINATE`, `R_DEATH`.
- Thread/child test codes: `THREAD_WRITE_TEST`, `THREAD_REWRITE_TEST`, `THREAD_READ_TEST`, `THREAD_REREAD_TEST`, `THREAD_STRIDE_TEST`, `THREAD_RANDOM_READ_TEST`, `THREAD_RANDOM_WRITE_TEST`, `THREAD_REVERSE_READ_TEST`, `THREAD_RANDOM_MIX_TEST`, `THREAD_PWRITE_TEST`, `THREAD_PREAD_TEST`, `THREAD_FWRITE_TEST`, `THREAD_FREAD_TEST`, `THREAD_CLEANUP_TEST`.

The `func[]` dispatch table maps single-stream test order to benchmark implementations:

- `write_perf_test`
- `read_perf_test`
- `random_perf_test`
- `reverse_perf_test`
- `rewriterec_perf_test`
- `read_stride_perf_test`
- `fwrite_perf_test`
- `fread_perf_test`
- `mix_perf_test`
- optional `pwrite_perf_test`, `pread_perf_test`, `pwritev_perf_test`, and `preadv_perf_test`

## Global State and Persistence Behavior

This chunk relies on a very large set of file-scope globals. The key behavior is not object-oriented; options and helpers mutate process-wide variables that are later consumed by benchmark loops and worker functions.

State categories:

- Sizing and iteration: `kilobytes64`, `reclen`, `numrecs64`, `min_file_size`, `max_file_size`, `min_rec_size`, `max_rec_size`, `r_range`, `s_range`, `t_range`, linked lists `size_list` and `rec_size_list`.
- Reporting: `report_array`, `report_darray`, `throughput_array`, `runtimes`, `current_x`, `current_y`, `max_x`, `max_y`, `Rflag`, `bif_flag`, `bif_filename`, `command_line`.
- Benchmark behavior flags: `aflag`, `trflag`, `include_tflag`, `include_test`, `include_mask`, `oflag`, `direct_flag`, `mmapflag`, `async_flag`, `verify`, `sverify`, `diag_v`, `dedup`, `dedup_interior`, `dedup_compress`, `noretest`, `notruncate`, `no_unlink`, `no_write`, `file_lock`, `rlocking`, `share_file`, `OPS_flag`, `MS_flag`, `cpuutilflag`.
- Buffer/cache state: `buffer`, `buffer1`, `mbuffer`, `mainbuffer`, `pbuffer`, `dedup_ibuf`, `dedup_temp`, `cache_size`, `cache_line_size`, `page_size`, `fetchon`, `purge`, `multi_buffer`.
- Throughput/parallel execution: `num_child`, `mint`, `maxt`, `childids`, `p_childids`, `barray`, `shmaddr`, `child_stat`, `stop_flag`, `stoptime`, `use_thread`.
- Distributed mode: `distributed`, `master_iozone`, `client_iozone`, `controlling_host_name`, `client_filename`, sockets/ports, `child_idents`, protocol buffers, and `proto_version`.
- Telemetry: `w_traj_flag`, `r_traj_flag`, trajectory file names, trajectory file descriptors, operation counts, byte counts, `compute_flag`, and `compute_time`.
- External side effects: temporary benchmark files, `.DUMMY` files, telemetry files, optional `wol.dat`/`rwol.dat`, Excel/report files, sockets, child processes/threads, shared memory, and optional external monitor commands.

Persistence is mostly via filesystem artifacts created during benchmarking:

- Main test file defaults to `iozone.tmp` or `-f`/`-F` filenames.
- Dummy files are built as `<filename>.DUMMY` or `<filearray[i]>.DUMMY.<i>`.
- `write_perf_test` opens `wol.dat` and `rwol.dat` when offset-latency output is enabled.
- Telemetry input/output files are opened by `open_w_traj()` and `open_r_traj()` declarations/uses.
- `record_command_line()` stores the command line in a static in-memory `command_line` buffer for later report output.
- Interrupt cleanup removes test files unless `no_unlink` is set and may dump Excel/throughput summaries before exit.

## Main Control Flow

### `main(argc, argv)`

`main` is the primary coordinator:

1. Initializes default filenames, stdout/stderr buffering, hostname, debug environment variables, random generation number, page size, clock ticks, file-name arrays, PID, external monitor command strings, splash lines, and signal handlers.
2. Allocates and cache-aligns the main I/O buffer and a dedup input buffer using `alloc_mem()`. It fills/touches dedup support state with `touch_dedup()`.
3. Initializes default filename and verification pattern. If no arguments are supplied, prints `USAGE` and exits with 255.
4. Parses options using `getopt()` with a large switch. Most options set globals and append splash text.
5. Parses `-+` extended options through a nested switch. This includes distributed mode, CPU utilization, diagnostics, multiplier, cluster host/port, no-retest, aggregate dataset, record/shared-file locking, existing-file read-only mode, short-circuit/compatibility data modes, dedup ratios/seeds, PIT timing server settings, histogram logging, and operation-rate limiting.
6. Finalizes timing resolution and optional speed-test mode.
7. Applies validation rules and incompatible-option checks, including telemetry limitations, throughput-vs-auto exclusion, `-f`/`-F` constraints, async-vs-mmap exclusion, missing async support, existing-file no-write restrictions, `-H`/`-k` exclusion, and dedup-vs-diagnostic exclusion.
8. Initializes record-size lists, prints resolution/cache/stride/process information, bounds record length to `MINBUFFERSIZE..MAXBUFFERSIZE`, and pre-fills/touches buffers for verification.
9. Optionally binds the parent thread to a CPU on supported platforms.
10. Chooses execution mode:
    - `multi_throughput_test(mint, maxt)` when throughput mode is enabled.
    - The immediately following `if (trflag && mint == maxt)` is effectively unreachable after the previous `trflag` branch because it already jumps to `out`.
    - `print_header(); auto_test();` for auto mode.
    - `print_header(); begin(kilobytes64, reclen);` for single-size mode.
11. Closes trajectory files, removes dummy file unless disabled, prints completion, warns about poor timer resolution, and dumps Excel output for non-throughput `Rflag`.

### `record_command_line()`

Prints the command line unless `silent`, and appends argv entries to `command_line` up to a fixed 1024-byte buffer. It reports truncation if the saved line would overflow.

### `begin(kilos64, reclength)`

Runs the single-stream benchmark dispatch table for a specific file size and record size.

Control flow:

1. Computes `num_tests` from `func[]`, subtracting optional tests not applicable to the current build or mode.
2. Handles `RWONLYflag`, flushes dirty data via two `sync()` calls, sets global `kilobytes64`, `reclen`, and `numrecs64`.
3. Stores file size and record size in the report arrays via `store_value()`, and prints the row prefix.
4. If specific tests were requested, calls only functions selected in `include_mask` and stores zero placeholders for skipped columns.
5. Otherwise calls every applicable function in `func[]`.
6. Emits newline, warns if write/read test timing was too fast, suggests a bigger file size, or suggests smaller record size after I/O failure.
7. Removes the main test file unless `no_unlink` is set.

### `auto_test()`

Implements automatic matrix testing:

1. Applies `-g`/`-n` max/min file-size overrides.
2. Rejects configurations where minimum record size exceeds minimum file size.
3. Sets crossover behavior, initializes file-size and record-size linked lists, and loops through every generated file size.
4. For large file sizes, it may skip small record sizes by switching `min_rec_size` to `LARGE_REC` and inserting dummy zero report entries for skipped record sizes.
5. For each record size that fits within the current file size, calls `begin(kilosi, recszi)`.

### `throughput_test()`

Implements most of the multi-child throughput workflow for one `num_child` setting. `multi_throughput_test()` is declared and is likely responsible for iterating `mint..maxt` in later lines.

Common pattern for each throughput subtest:

1. Allocate or reuse shared memory for `struct child_stats`.
2. Establish `stop_flag` either as `stoptime` in pthread mode or a slot at the end of shared memory in process mode.
3. Initialize child stats to `CHILD_STATE_HOLD`.
4. Optionally start external monitors and distributed-mode listener/client behavior.
5. Spawn one process/thread per child, using `start_child_proc()` for fork/distributed process paths or `mythread_create()` for pthread paths.
6. Parent waits until each child leaves `CHILD_STATE_HOLD`, sets `CHILD_STATE_BEGIN`, optionally staggers starts with `delay_start`, and signals distributed clients via `tell_children_begin()`.
7. Parent waits for process exit or thread join, or for distributed join messages.
8. Computes parent total time, corrects timer resolution edge cases, aggregates child `throughput`, `actual`, `cputime`, and maximum wall time.
9. Stores result values via `store_dvalue()` and optionally `store_times()`, prints child/parent throughput and min/max/avg per-child metrics, stops monitors, syncs, sleeps, applies rest delay, and tears down distributed listener/comm state.

Subtests visible in this chunk:

- Initial write: `THREAD_WRITE_TEST` / `thread_write_test`
- Rewrite: `THREAD_REWRITE_TEST` / `thread_rwrite_test`
- Read: `THREAD_READ_TEST` / `thread_read_test`
- Re-read: `THREAD_REREAD_TEST` / `thread_rread_test`
- Reverse read: `THREAD_REVERSE_READ_TEST` / `thread_reverse_read_test`
- Stride read: `THREAD_STRIDE_TEST` / `thread_stride_read_test`
- Random read: `THREAD_RANDOM_READ_TEST` / `thread_ranread_test`
- Mixed workload: `THREAD_RANDOM_MIX_TEST` / `thread_mix_test`
- Random write: `THREAD_RANDOM_WRITE_TEST` / `thread_ranwrite_test`
- Optional pwrite: `THREAD_PWRITE_TEST` / `thread_pwrite_test`
- Optional pread: `THREAD_PREAD_TEST` / `thread_pread_test`
- Fwrite: `THREAD_FWRITE_TEST` / `thread_fwrite_test`
- Fread: `THREAD_FREAD_TEST` / `thread_fread_test`
- Cleanup: `THREAD_CLEANUP_TEST` / `thread_cleanup_test`

The function uses `goto` labels (`next0` through `next10`) as skip points for include-mask filtering and optional feature availability. This makes the execution sequence stable but hard to modify safely.

### `signal_handler()`

Handles interrupt/termination:

- Distributed master runs `cleanup_children()`.
- The original master process removes the main file, per-child dummy files, and default dummy file unless `no_unlink`.
- Dumps Excel or throughput reports if requested.
- Emits timer-resolution warnings.
- Kills process-mode children on throughput runs.
- Closes trajectory files and speed-test sockets if open.
- Exits process with status 0.

## Data Pattern, Cache, and Timing Helpers

### `time_so_far()`

Returns elapsed wall time as a floating-point seconds value. Platform paths:

- Windows uses `QueryPerformanceFrequency()` / `QueryPerformanceCounter()` unless a PIT server is configured.
- OSF variants use `getclock(TIMEOFDAY)`.
- Other POSIX paths use `gettimeofday()` unless a PIT server is configured.

When `pit_hostname` is set, timing is delegated to `pit_gettimeofday()`, which is declared in this chunk and implemented later.

### `fetchit(buffer, length)`

Touches one byte per cache line to warm CPU cache lines for a buffer. It uses a volatile local array to discourage optimization away.

### `purgeit(buffer, reclen)`

Touches a corresponding range in `pbuffer` to make the target buffer cold relative to the CPU cache. It aligns the purge offset using `cache_size` and limits the number of cache lines to the smaller of the record and cache sizes.

### `prepage(buffer, reclen)`

Writes the benchmark pattern to one byte per cache line to fault pages in before timing, mainly to avoid copy-on-write or first-touch effects.

### `fill_buffer(buffer, length, pattern, sverify, recnum)`

Fills a buffer for write verification. Behavior changes by mode:

- Dedup mode calls `gen_new_buf()` using `dedup_ibuf` and returns.
- Diagnostic mode seeds `rand()` from `base_time + child-id + record-number` and generates evolving per-word data.
- Normal partial verification (`sverify == 1`) writes expected data only at page intervals.
- Full verification writes expected pattern or diagnostic pattern over cache-line-sized regions.

It also accounts for `share_file` by forcing the effective child id to zero so shared-file patterns are deterministic across children.

### `verify_buffer(buffer, length, recnum, recsize, patt, sverify)`

Validates a read buffer. Behavior mirrors `fill_buffer()`:

- `sverify == 2`: touches one word per page without checking.
- Dedup mode regenerates expected data with `gen_new_buf()` and compares a limited amount (`lite` is set to 1) to reduce validation overhead.
- Diagnostic mode reconstructs deterministic per-record pattern.
- `sverify == 1`: checks one word per page.
- `sverify == 0`: full cache-line walk and byte-level mismatch localization.

On mismatch, it prints file position, record number, record size, and expected/found values, then returns 1. Success returns 0.

## Write Benchmark Start: `write_perf_test()`

The chunk includes the first part of `write_perf_test(kilo64, reclen, data1, data2)`, which performs write and rewrite testing for single-stream mode. The function continues after this chunk.

Visible setup and open behavior:

- Determines `filebytes64` and `numrecs64` either from write telemetry (`w_traj_flag`) or from `kilo64 * 1024 / reclen`.
- Opens `wol.dat` and `rwol.dat` with headers when offset-latency logging is enabled by `Q_flag`.
- Builds open flags from `oflag`, optional `O_DSYNC`, read-sync flags, and direct-I/O flags.
- Contains a disabled/truncated sanity-check block guarded out by `#define FUSE`, intended to detect filesystems that fail a create/ftruncate/close/unlink sequence.
- Uses `noretest` to decide whether to run only write or both write and rewrite passes.
- Per pass, optionally records CPU/wall start times, purges buffer cache for remount mode, creates/truncates the file on first write pass unless `notruncate`, reopens with selected flags, and enables platform-specific direct I/O (`VX_SETCACHE` for VxFS or `directio()` on Solaris).
- Applies whole-file locking with `mylockf()` if `file_lock` is enabled.
- Initializes mmap file mapping via `initfile()` when `mmapflag` is set.
- Supports mixed mmap/file I/O by writing a page, seeking back, and syncing.
- Calls `fsync()` before timed operations and initializes async state when `ASYNC_IO` and `async_flag` are active.
- Warms and fills the main buffer before starting the timer.

The actual write loop and result storage are beyond line 7579 and must be covered by later chunk research.

## Dependencies and Integration Points

Internal functions declared or used here but implemented outside this chunk include:

- Benchmark implementations: `read_perf_test`, `random_perf_test`, `reverse_perf_test`, `rewriterec_perf_test`, `read_stride_perf_test`, `fwrite_perf_test`, `fread_perf_test`, `mix_perf_test`, `pread_perf_test`, `pwrite_perf_test`, `preadv_perf_test`, `pwritev_perf_test`.
- Thread workers: `thread_write_test`, `thread_rwrite_test`, `thread_read_test`, `thread_rread_test`, `thread_reverse_read_test`, `thread_stride_read_test`, `thread_ranread_test`, `thread_ranwrite_test`, `thread_mix_test`, `thread_pread_test`, `thread_pwrite_test`, `thread_fwrite_test`, `thread_fread_test`, `thread_cleanup_test`.
- Report helpers: `print_header`, `store_value`, `store_dvalue`, `store_times`, `dump_excel`, `dump_throughput`, `dump_cputimes`.
- Allocation and OS helpers: `alloc_mem`, `alloc_pbuf`, `purge_buffer_cache`, `mylockf`, `mylockr`, `mmap_end`, `initfile`, `async_*`, `do_compute`.
- Size/trajectory helpers: `init_file_sizes`, `get_next_file_size`, `init_record_sizes`, `get_next_record_size`, `open_w_traj`, `open_r_traj`, `w_traj_size`, `r_traj_size`, `traj_vers`, `get_traj`.
- Distributed-mode helpers: `start_child_proc`, `become_client`, `start_master_listen`, `start_master_listen_loop`, `wait_dist_join`, `tell_children_begin`, `stop_master_listen`, `cleanup_comm`, `cleanup_children`, `get_client_info`.
- Dedup/random helpers: `touch_dedup`, `gen_new_buf`, `init_by_array64`, `genrand64_int64`.

External dependencies:

- POSIX file APIs: `open`, `creat`, `close`, `read`, `write`, `fsync`, `ftruncate`, `unlink`, `lseek`, `stat`, `mmap`, `msync`, `sync`.
- Process/thread APIs: `fork` through `start_child_proc`, `wait`, `kill`, signals, pthreads, CPU affinity.
- Timing APIs: `gettimeofday`, `times`, platform-specific `getclock`, Windows performance counters, optional PIT socket time service.
- Networking APIs for distributed mode: sockets, `sockaddr_in`, DNS host lookup.
- Platform direct I/O APIs: `O_DIRECT`, `O_DIRECTIO`, VxFS ioctls, Solaris `directio`.
- Shell/popen integration: `uname -a` for `-M`, external monitor start/stop commands.

## Risks and Edge Cases

- The implementation is dominated by global mutable state. Many helpers depend on globals rather than parameters, making option interactions and distributed/thread behavior fragile.
- `main` uses unbounded `strcpy()` into fixed-size arrays for filenames, mount names, host names, telemetry names, and client filenames. Long user arguments can overflow buffers.
- `splash` is `80 x 80`, but many `sprintf()` calls can write more than 80 characters into a row, which is an overflow risk.
- The `-F` filename loop decrements `optind` and then reads `maxt` names, depending on `-t` having initialized `maxt` correctly. Off-by-one or insufficient-argument handling is brittle.
- The branch `if(trflag && (mint == maxt))` after an earlier unconditional `if(trflag) { multi_throughput_test(); goto out; }` appears unreachable in this chunk.
- Throughput orchestration repeats large blocks with manual `goto` labels, making it easy for fixes in one subtest path not to reach others.
- Parent/child synchronization uses shared-memory integer flags and polling with `Poll(1)`. There is no explicit memory-ordering primitive visible in this chunk beyond `VOLATILE`, which is not a complete cross-process/thread synchronization model on modern compilers/CPUs.
- Timer correction subtracts `time_res` and clamps to `time_res`; short tests can still produce misleading throughput and set `res_prob`.
- Direct I/O, mmap, async, locking, telemetry, and verification modes interact with strict constraints. The chunk rejects some invalid combinations, but more combinations are likely handled only by lower-level code.
- Dedup verification intentionally compares only a tiny slice in `lite` mode, which reduces overhead but can miss corruption outside the sampled word.
- `sync()` and `sleep(2)` are used as cache/settling controls; behavior is platform-dependent and can dominate small tests.
- Existing-file read-only mode (`-+E`) disables writes, verification, unlink, and requires explicit test selection, but write tests are rejected via hard-coded test indexes. Future dispatch-table changes would need synchronized updates.
- Some declarations use K&R compatibility and weak prototypes when `HAVE_PROTO`/`HAVE_ANSIC_C` are absent, increasing the chance of ABI/type mismatch on modern systems.
- The disabled sanity check is force-disabled by `#define FUSE` inside the function, so filesystem create/truncate correctness is not tested in this build path.

## Test Signals

Useful signals for validating this chunk:

- CLI parsing smoke tests:
  - `iozone -h` prints help and exits 0.
  - `iozone -v` prints version/header information and exits 0.
  - `iozone -s 64 -r 4 -i 0` reaches single-stream write dispatch.
  - Invalid combinations such as `-t 2 -f file`, `-a -F ...`, `-H 1 -k 1`, `-B -H 1`, telemetry plus auto mode, and no-write plus write tests should exit with documented errors.
- Auto-mode tests:
  - `-a -n <min> -g <max> -y <minrec> -q <maxrec>` should iterate file/record sizes and reject record size greater than file size.
  - Large file sizes should trigger crossover zero-fill report placeholders when applicable.
- Throughput tests:
  - `-t 2 -F file1 file2 -i 0 -i 1` should spawn two processes by default and aggregate child `child_stats`.
  - `-T -t 2 -F file1 file2 -i 0` should use pthread creation when threads are enabled.
  - Include masks should skip unselected subtests and preserve report-column placeholders.
- Cleanup behavior:
  - Normal completion removes `iozone.tmp` and `.DUMMY` files unless `-w`/`no_unlink`.
  - SIGINT/SIGTERM should remove temporary files, close trajectory files, and kill process-mode throughput children.
- Verification paths:
  - `-V <pattern>` should fill and verify data and label measurements invalid.
  - `-+d` diagnostic mode should produce deterministic per-record patterns.
  - `-+w`, `-+y`, and `-+C` should activate dedup buffer generation without diagnostics.
- Reporting:
  - `-R` should populate report arrays and call Excel dumping at normal exit or interrupt.
  - `-Q` should create `wol.dat` and `rwol.dat` headers in write paths.
- Platform/feature compile coverage:
  - Build variants with and without `HAVE_PREAD`, `HAVE_PREADV`, `NO_THREADS`, `ASYNC_IO`, `_LARGEFILE64_SOURCE`, `Windows`, and direct-I/O macros should compile because this chunk has many conditional prototypes and dispatch-table shapes.

## Cross-Chunk References

The following items are central to behavior visible here but are outside lines 1-7579:

- Completion of `write_perf_test()` write/rewrite loop and result storage.
- All read, random, reverse, stride, stdio, pread/pwrite, vector-I/O, and mixed workload single-stream functions.
- Worker thread/process functions used by `throughput_test()`.
- `multi_throughput_test()` and the per-child implementations that write `child_stats`.
- `alloc_mem()`, shared-memory allocation details, and thread wrapper details.
- Distributed-mode socket protocol implementation.
- Excel/report output serialization.
- Trajectory parsing and PIT timing implementation.
- Dedup buffer generation and Mersenne Twister functions.
