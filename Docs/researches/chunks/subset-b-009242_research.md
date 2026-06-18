# sources/test-tools/iozone/src/current/iozone.c lines 16680-25345

## Scope and Purpose

This chunk is the late implementation section of Iozone's monolithic benchmark driver. It starts inside the tail of `thread_stride_read_test()` and then covers mixed/random threaded workloads, cleanup, pthread wrappers, throughput report formatting, mmap/timing/locking helpers, telemetry file parsing, file/record size list construction, distributed master/client socket orchestration, network speed checks, pattern and dedup buffer generation, the embedded 64-bit Mersenne Twister, PIT remote-time support, latency histogram output, and stdio-based `fwrite`/`fread` benchmark variants.

The code is C implementation, not an isolated library module. Most functions depend on process-wide benchmark globals (`numrecs64`, `reclen`, `filearray`, `shmaddr`, `stop_flag`, `chid`, flags such as `direct_flag`, `mmapflag`, `async_flag`, `Q_flag`, `hist_summary`, `distributed`, and many more). The functions primarily integrate Iozone's worker lifecycle with OS file APIs, pthreads, sockets, timers, and optional platform features.

## Major Function Areas

### Threaded Workload Workers

- `thread_stride_read_test()` is already in progress at the chunk start. The visible tail performs strided reads using normal `read()`, mmap copy via `fill_area()`, or async reads. It records optional per-operation latency (`Child_<id>_strol.dat`), histogram samples, operation-rate pacing, record/file locks, verification, CPU utilization, and final child statistics in `struct child_stats`.
- `thread_mix_test()` selects each child as a reader or writer based on `pct_read`, `Kplus_flag`/`Kplus_readers`, or round-robin parity. It dispatches either sequential mix (`thread_read_test()`/`thread_write_test()`) or random mix (`thread_ranread_test()`/`thread_ranwrite_test()`).
- `thread_ranread_test()` opens each worker file read-only, optionally enables direct I/O, mmap, async I/O, and CPU affinity, then reads each record in a deterministic random order. It precomputes a shuffled `recnum` array when memory permits; otherwise it falls back to per-iteration random offsets. It updates throughput, `actual`, CPU time, wall time, histograms, `Q_flag` latency logs, and distributed master stats.
- `thread_ranwrite_test()` mirrors random reads for writes. It opens/creates the target file read-write, initializes mmap or async support, fills buffers for verification/dedup modes, writes records in shuffled order, and deliberately lets writers finish after a stop flag so concurrent readers do not observe short files. It tracks both byte and operation counts so `OPS_flag` can report operations/sec.
- `thread_cleanup_test()` removes each worker's dummy file when `no_unlink` permits it, participates in the same ready/begin barrier, sends distributed stats for `THREAD_CLEANUP_TEST`, marks its `child_stats` slot held, and exits.
- `thread_fwrite_test()` and `thread_fread_test()` implement stdio-buffered benchmark variants using `I_FOPEN()`/`fopen()`, `setvbuf()`, `fwrite()`/`fread()`, optional `fsync()`, verification, histograms, `Q_flag` latency logs, and the same distributed/statistics lifecycle. They return immediately when mmap or async mode is active.

Common worker control flow is: derive child id, optionally bind CPU, choose per-thread or process buffer, build the dummy filename, open/configure the file, initialize optional logs, set `child_stat->flag = CHILD_STATE_READY`, wait for parent/master begin, run the timed loop, flush/close if requested, compute throughput after subtracting `time_res` and optional compute delay, set shared stop semantics, send distributed results if needed, mark `CHILD_STATE_HOLD`, clean up logs/buffers, and exit or `thread_exit()`.

### Thread, Reporting, Mmap, and Timing Helpers

- `mythread_create()`, `thread_exit()`, `mythread_self()`, and `thread_join()` wrap pthread creation, exit, identity, and join. `NO_THREADS` builds retain stubs that print unsupported messages.
- `dump_throughput()` and `dump_throughput_cpu()` print matrix-style throughput/CPU reports and optionally write BIFF/XLS cells through `create_xls()`, `do_label()`, `do_float()`, and `close_xls()`. `store_dvalue()` stores report values into `report_darray[current_x][current_y]` and updates bounds.
- `initfile()` prepares files for mmap tests. When `flag` is set it preallocates/touches the file, with special handling for `O_DIRECT` files that cannot be sparse on Linux. It maps with `I_MMAP()`/`mmap()`, chooses shared/private flags from `prot`, and applies optional `madvise()`.
- `mmap_end()` unmaps mapped regions, and `fill_area()` copies between mapped file memory and the user buffer using `bcopy()`.
- Non-`ASYNC_IO` builds provide fail-fast async stubs (`async_read`, `async_write`, `async_init`, etc.) that print a message and exit if an async path is reached.
- `my_nap()` and `my_unap()` implement millisecond/microsecond pacing. `get_resolution()` and `get_rusage_resolution()` measure timer and CPU accounting granularity. `time_so_far1()` returns microseconds from Windows performance counters, OSF `getclock()`, local `gettimeofday()`, or PIT remote time.
- `cputime_so_far()` uses `getrusage(RUSAGE_SELF)` on Unix, while `cpu_util()` converts CPU/wall deltas into a percentage.

### Locking, Telemetry, and Size Lists

- `mylockf()` applies or releases whole-file advisory locks with `fcntl(F_SETLKW)` and `F_RDLCK`/`F_WRLCK`. `mylockr()` does the same for a byte range.
- `do_compute()` busy-waits for synthetic compute delay, and `disrupt()`/Windows `disruptw()` intentionally perturb read patterns by reading small pieces at the start and page-size offset before restoring the original file position.
- `get_traj()` reads the next non-comment telemetry line, accepting two fields (`offset size`) or three (`offset size delay_ms`) and returning offset while setting transfer size and delay. Invalid format or early EOF aborts through `exit()` or `signal_handler()`.
- `open_r_traj()`, `open_w_traj()`, `r_traj_size()`, `w_traj_size()`, and `traj_vers()` open/scan telemetry files, count operations, determine maximum file extent, and detect the number of fields in the first data row.
- `init_file_sizes()`, `add_file_size()`, `get_next_file_size()`, `init_record_sizes()`, `del_record_sizes()`, `add_record_size()`, and `get_next_record_size()` maintain simple linked lists of file and record sizes from explicit ranges or multiplicative defaults.

### Distributed Master/Client Protocol

The distributed mode is a custom TCP control protocol with two message families: `client_command` from master to child and `master_command` from child to master. For portability, `master_send()` and `child_send()` serialize numeric fields into neutral string structs (`client_neutral_command`, `master_neutral_command`); receive paths `sscanf()` the fields back into native structs.

- `start_master_listen()`, `master_listen()`, `stop_master_listen()`, `start_master_send()`, `start_master_send_async()`, `master_send()`, and `stop_master_send()` implement the master-side listener and outbound sync/async channels. They bind from configured base ports and increment until success.
- `start_child_listen()`, `start_child_listen_async()`, `child_attach()`, `child_listen()`, `child_listen_async()`, `child_send()`, `stop_child_listen()`, and `O_stop_child_send()` implement client-side listeners and messages to the master.
- `start_child_proc()` forks locally or calls `pick_client()` in distributed master mode. `pick_client()` launches a remote Iozone via `rsh`/`remsh` or `$RSH`, waits for join, creates sync and async channels, populates a `client_command` with benchmark configuration, sends it, and waits for the child ready barrier.
- `become_client()` is the remote child entry point. It daemonizes, starts sync/async listeners, sends a join message, receives and imports all benchmark state, changes to the assigned work directory, starts the async listener loop, computes telemetry extents if needed, and dispatches the requested worker by `testnum`.
- `tell_master_ready()`, `wait_for_master_go()`, `tell_master_stats()`, `tell_children_begin()`, `start_master_listen_loop()`, `start_child_listen_loop()`, and `wait_dist_join()` implement distributed barriers, result collection, and async stop propagation.
- `get_client_info()` and `parse_client_line()` parse the client identity file as `host workdir executable [file_name]`, with the optional fourth field enabling `mfflag`.
- `terminate_child_async()`, `distribute_stop()`, `send_stop()`, `cleanup_children()`, `cleanup_comm()`, and `child_remove_files()` handle normal completion, stop flag fan-out, interrupt/death cleanup, socket cleanup, and remote temporary file deletion.

Protocol state is carried through `child_idents[]` states such as `C_STATE_ZERO`, `C_STATE_WAIT_WHO`, and `C_STATE_WAIT_BARRIER`; shared-memory `child_stats` flags; `master_join_count`; generation marker `mygen`; and the process-shared `stop_flag`.

### Network Speed Check

The `speed_main()` family implements a separate distributed network throughput probe:

- `speed_main()` starts either a child-mode speed endpoint or forks a remote command with `-+t`.
- `sp_do_master_t()` measures master-to-child writes and child-to-master reads.
- `sp_do_child_t()` measures child-side receive and send loops.
- `sp_start_master_send()`, `sp_start_master_listen()`, `sp_start_child_send()`, and `sp_start_child_listen()` create one-off TCP channels for the speed test.
- `sp_send_result()` and `sp_get_result()` exchange formatted result records, and `do_speed_check()` runs the probe for each parsed client.

This is integrated with the same remote shell and controller host configuration as distributed Iozone, but uses separate `SP_*` port bases and result sockets.

### Patterns, Dedup, Randomness, PIT, and Histograms

- `get_date()` wraps `time()`/`ctime()` for log timestamps. `get_pattern()` derives the default byte pattern from `THISVERSION`, with `Z_flag` forcing legacy `0xa5` and `X_flag` forcing `PATTERN1`.
- `alloc_pbuf()` allocates and cache-size-aligns the purge buffer. `check_filename()` uses `I_STAT()` to verify a path is a regular file before unlinking.
- `start_monitor()` and `stop_monitor()` run optional external monitor commands from `IMON_START`/`IMON_STOP`, with foreground/background controlled by `IMON_SYNC`.
- `gen_new_buf()` transforms an input buffer into a configured mixture of dedupable, compressible, and non-dedupable regions. It uses seeds based on block number, child id/skew, total records, and `dedup_mseed`; `touch_dedup()` fills an initial buffer with deterministic random longs.
- The embedded MT19937-64 implementation provides `init_genrand64()`, `init_by_array64()`, `genrand64_int64()`, `genrand64_int63()`, and real-valued generators. Random read/write workers use it when `MERSENNE` is defined; otherwise they use `rand()` or `lrand48()`.
- PIT remote-time support (`pit_gettimeofday()`, `openSckt()`, `pit()`) mimics `gettimeofday()` by connecting to a remote service configured by `pit_hostname`/`pit_service`, reading a microsecond timestamp, and converting it into `struct timeval`.
- `hist_insert()` buckets operation latency into 40 microsecond-to-second ranges. `dump_hist()` appends per-child reports to `Iozone_histogram_child_<id>.txt`.

## State and Persistence Behavior

- Worker-visible state is mostly global and mutable. Benchmark flags imported by `become_client()` directly overwrite globals before the selected test runs.
- Child progress is persisted in shared memory through `struct child_stats` slots, especially `throughput`, `actual`, `cputime`, `walltime`, and `flag`.
- Stop behavior is cooperative. A child may set `*stop_flag`, call `send_stop()` in distributed mode, and continue or abort depending on workload semantics. Random writes specifically continue after a stop to keep reader-visible files complete.
- Temporary files are named from `filearray[]`, `.DUMMY.<id>`, `mfflag`, and `share_file`. Deletion is gated by `no_unlink` and `check_filename()` to avoid unlinking non-regular files.
- Optional outputs include per-child operation latency files (`Child_<id>_*ol.dat`), per-child start/finish logs (`Child_<id>.log`), histogram summaries (`Iozone_histogram_child_<id>.txt`), XLS/BIFF report output, and external monitor side effects.
- mmap tests persist file initialization by writing/touching file contents before mapping; `include_flush`, `include_close`, and mmap sync flags control when file data is synchronized or descriptors are closed.
- Distributed mode creates multiple TCP sockets and forked listener processes. It also relies on remote shell execution and remote working directories, so process/socket cleanup is part of benchmark correctness.

## Dependencies and Integration Points

- POSIX/Unix APIs: `open`/`read`/`write`/`close`, `lseek`, `fsync`, `fcntl` locks, `mmap`/`munmap`/`msync`, `madvise`, `gettimeofday`, `getrusage`, `times`, `select`, `usleep`, `nanosleep`, `fork`, `wait`, `kill`, `chdir`, `system`, `stat`, and sockets.
- Platform-specific paths: Windows `CreateFile`, `ReadFile`, `SetFilePointer`, `QueryPerformanceCounter`; HP-UX `prealloc` and processor binding; Solaris `directio`; VxFS `VX_SETCACHE`; OSF `getclock`; IRIX mmap flags; TRU64 direct I/O.
- Iozone-local wrappers and globals: `I_OPEN`, `I_FOPEN`, `I_LSEEK`, `I_MMAP`, `I_STAT`, `Poll`, `alloc_mem`, `purgeit`, `fetchit`, `fill_buffer`, `verify_buffer`, `signal_handler`, `purge_buffer_cache`, `create_xls`, `do_label`, `do_float`, `close_xls`, and numerous benchmark flags.
- Threading integration: pthread creation/join/exit and optional CPU affinity on Linux/HP-UX.
- Network integration: DNS resolution with `gethostbyname()`/`getaddrinfo()`, IPv4/IPv6 socket setup, fixed protocol command codes (`R_JOIN_ACK`, `R_CHILD_JOIN`, `R_STAT_DATA`, `R_FLAG_DATA`, `R_STOP_FLAG`, `R_TERMINATE`, `R_DEATH`), and configurable port bases.

## Risks and Edge Cases

- The code uses many unchecked `malloc()` results for per-worker filenames, telemetry random arrays, and stdio buffers. Some paths handle allocation failure (`recnum` fallback), while others assume success.
- Several fixed-size buffers are populated with `sprintf()`, `strcpy()`, and `strcat()` using filenames, hostnames, commands, and environment variables. Long paths or client file fields can overflow local arrays such as `tmpname[256]`, command buffers, or identity strings.
- Socket reads/writes generally assume whole neutral command structs or result payloads arrive in one or a few blocking calls. Partial writes, zero reads outside special async handling, interrupted syscalls, or network partitions can corrupt protocol progress or hang.
- Port binding loops increment indefinitely until bind succeeds. In exhausted or permission-limited port ranges this can spin for a long time.
- `start_master_listen()` retries bind inside a `while (rc < 0)` loop and has an unreachable post-loop `if(rc < 0)` check; similar patterns appear elsewhere.
- Distributed cleanup is state-sensitive. A child in `C_STATE_WAIT_WHO` lacks an async listener, while a barrier child has both sync and async processes; wrong state tracking can leave remote processes or files behind.
- `become_client()` imports remote config via `%s`, so paths with spaces are not supported and overlong fields can overflow command struct members.
- Random access tests seed PRNGs deterministically (`srand48(0)`, `srand(0)`, or fixed Mersenne seed array), which is good for repeatability but can produce identical access patterns across children unless other state changes the sequence.
- Direct I/O and mmap paths have strict alignment and sparse-file constraints; `initfile()` attempts to handle these but depends on `reclen` alignment and platform-specific flags.
- Histogram buckets are global and not reset in this chunk before each dump. In multi-test or multi-thread contexts, bucket reuse can contaminate later histogram output unless reset elsewhere.
- `my_unap()` truncates requested sleep to millisecond granularity before busy-waiting; very small or huge values can produce inaccurate pacing or CPU spin.
- `get_date()` copies `ctime()` output including its trailing newline into a fixed 30-byte buffer. Current ctime strings fit, but the API style is brittle.
- `check_filename()` returns false on stat failure and only unlinks regular files, protecting devices but also leaving failed-stat temporary files behind.
- The stdio tests open a separate descriptor only to `fsync()` before reads, then close it while using the `FILE *`; failures from this pre-read `I_OPEN()` are not checked before `fsync(fd)`.
- `gen_new_buf()` writes using `long *` across byte counts that may not be multiples of `sizeof(long)` and assumes sufficient alignment of the input/output buffers.

## Test Signals

- Random read/write tests should be run with verification, `Q_flag`, `hist_summary`, `OPS_flag`, `op_rate_flag`, `file_lock`, `rlocking`, `direct_flag`, `mmapflag`, async/no-copy modes, and distributed mode to exercise their divergent branches.
- Stop propagation should be tested with mixed readers/writers to ensure random writers finish file population while reported throughput/actual only count pre-stop work.
- Telemetry tests should cover comments, blank lines, two-field and three-field rows, invalid token counts, early EOF, max-offset calculation, and large offsets/sizes.
- Distributed tests should cover join, barrier, begin, stats, stop flag fan-out, terminate, death cleanup, protocol version mismatch, stale child generation (`mygen`) mismatch, and remote client errors.
- Socket robustness tests should force partial reads/writes, port collisions, slow accept/connect, and abrupt async-channel closure.
- mmap tests should cover `O_DIRECT` and non-direct file initialization, read-only/private versus write/shared mappings, `madvise` options, `include_flush`, `include_close`, and explicit mmap sync modes.
- Stdio `fwrite`/`fread` tests should verify direct and buffered `setvbuf()` modes, first-run file creation versus retest open behavior, `include_flush`/`include_close`, verification failure, and `restf` delay.
- Histogram tests should confirm bucket boundaries, per-child output naming, and whether buckets are reset between tests in the wider file.
- Dedup generation tests should compare expected identical, child-local, and randomized buffer regions across `dedup`, `dedup_interior`, `dedup_compress`, `chid_skew`, and `dedup_mseed` settings.
- PIT/time tests should cover local fallback, remote service success, DNS failure, socket failure, malformed PIT responses, and behavior under Windows and Unix timing paths.

## Cross-Chunk Notes

- The chunk begins inside `thread_stride_read_test()`, so that function's setup and initial open logic are defined in the previous chunk.
- Many worker functions invoked here (`thread_write_test`, `thread_read_test`, `thread_pwrite_test`, `thread_pread_test`, reverse read, reread, rewrite, async implementations, and buffer verification/fill helpers) are defined outside this line range.
- This chunk ends at the close of `thread_fread_test()`. Any following tests or final program teardown continue in later chunks.
