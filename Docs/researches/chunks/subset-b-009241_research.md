# sources/test-tools/iozone/src/current/iozone.c lines 7580-16679

Chunk `subset-b-009241` covers a large middle section of Iozone's benchmark driver. It begins in the tail of the normal sequential write test, then defines single-process stdio, raw, random, reverse, record-rewrite, stride, positional, and vector I/O benchmark routines, report/table helpers, shared-memory allocation and process helpers, throughput orchestration, cache purge support, and the first group of threaded or child-process throughput workers. The chunk ends inside the setup path of `thread_stride_read_test()`, so that worker's actual stride loop and cleanup continue in a later chunk.

## Purpose

This section implements the benchmark operations that produce most of Iozone's per-record-size throughput cells:

- Buffered stdio write/read tests through `fwrite_perf_test()` and `fread_perf_test()`.
- Raw sequential read and write-family tests through the tail of `write_perf_test()` and all of `read_perf_test()`.
- Access pattern tests: random read/write, reverse read, rewrite-one-record, and stride read.
- Positional I/O tests, when compiled in: `pwrite_perf_test()`, `pread_perf_test()`, `pwritev_perf_test()`, and `preadv_perf_test()`.
- Reporting helpers that print headers, store measured values, and dump Excel-style throughput and CPU-utilization matrices.
- Memory/process helpers for shared allocations, sleeps, min/max, kill behavior, repeated throughput runs, and cache purging by unmount/remount.
- Thread/process worker routines for write, pwrite, rewrite, read, pread, reread, reverse read, and the setup of stride read throughput tests.

The code is controlled almost entirely by global options parsed elsewhere: direct I/O, mmap, async I/O, verification, dedup data patterns, trajectory files, operation-rate limiting, latency output, CPU accounting, file locking, record locking, cache purge, close/fsync inclusion, distributed-client operation, thread/process mode, and output format flags.

## Important APIs, Types, and Functions

Single-process benchmark routines:

- The leading boundary section is the end of `write_perf_test()`. It writes each record through mmap, async, no-copy async, Windows unbuffered `WriteFile()`, or POSIX `write()`, optionally driven by a write trajectory file. It records latency data to `wol.dat`/`rwol.dat`, histograms, operation counts, byte counts, and final write/rewrite rates.
- `fwrite_perf_test()` performs first write and re-write passes with `FILE *`, `I_FOPEN()`, `setvbuf()`, `fwrite()`, `fflush()`, `fsync()`, and `fclose()`. It returns early for mmap or async modes because stdio is not meaningful for those modes.
- `fread_perf_test()` performs first read and reread passes with `FILE *` and `fread()`, then verifies buffer contents when requested.
- `read_perf_test()` is the raw sequential read benchmark. It supports normal read, mmap copy, async read, no-copy async read, Windows unbuffered reads, read trajectory files, per-operation latency output, histograms, disruption hooks, direct I/O setup, file/record locking, and verification.
- `random_perf_test()` builds a random record order, preferably with a unique shuffled `recnum` array. Pass 0 randomly reads records; pass 1 randomly writes records unless `no_write` suppresses the write pass.
- `reverse_perf_test()` reads records from the end toward the start, using backward seeks for normal reads or direct offsets for mmap/async.
- `rewriterec_perf_test()` repeatedly rewrites the same record at offset zero while still counting the configured file-size worth of operations.
- `read_stride_perf_test()` reads through the file using a stride pattern based on global `stride`, `next64`, and wrap state. It measures how well storage handles non-contiguous but deterministic read access.
- `pwrite_perf_test()` and `pread_perf_test()` use `I_PWRITE()` and `I_PREAD()` to avoid changing the descriptor's file position. Both support trajectory-driven offsets and record sizes.
- `pwritev_perf_test()` and `preadv_perf_test()` use `pwritev()` and `preadv()` with the global `piov` vector array. `create_list()` supplies unique random offsets for vector elements, either through per-vector offsets when `PER_VECTOR_OFFSET` exists or a single base offset otherwise.

Report and utility helpers:

- `print_header()` emits the benchmark table header, choosing compact read/write-only, extended, or mmap/async-compatible layouts based on `Eflag`, `RWONLYflag`, `mmapflag`, `async_flag`, `HAVE_PREAD`, and `HAVE_PREADV`.
- `store_value()` writes one measurement into `report_array[current_x][current_y]`, advances `current_x`, and enforces `MAX_X`/`MAX_Y`.
- `store_times()` stores wall time, CPU time, and computed CPU utilization into the parallel `runtimes` matrix for the same logical cell.
- `dump_report()`, `dump_excel()`, `dump_times()`, and `dump_cputimes()` print stored matrices and, when `bif_flag` is active, also emit spreadsheet cells through `do_label()` and `do_float()`.
- `alloc_mem()` returns either ordinary heap memory, SysV shared memory, or anonymous/file-backed shared mmap memory depending on distributed/thread mode, `trflag`, `shared_flag`, `SHARED_MEM`, and platform macros.
- `Poll()` implements a short sleep with `select()`.
- `l_max()` and `l_min()` provide long-long min/max helpers.
- `Kill()` suppresses process termination when stonewalling is disabled through `xflag`.
- `multi_throughput_test()` runs `throughput_test()` over a child-count range or explicit `t_range`, updating the report grid after each run.
- `purge_buffer_cache()` unmounts and remounts `mountname` with retry loops to reduce filesystem-cache effects.

Thread/process throughput workers:

- `thread_write_test()` creates or opens the per-child output file, optionally truncates for mixed delete tests, waits for parent/master start, writes the file sequentially, and publishes `THREAD_WRITE_TEST` stats.
- `thread_pwrite_test()` is the positional-write variant. It pre-creates/truncates unless `notruncate` is set, then writes each record via `I_PWRITE()` or the async/mmap equivalents, publishing `THREAD_PWRITE_TEST`.
- `thread_rwrite_test()` rewrites an existing per-child file sequentially and publishes `THREAD_REWRITE_TEST`.
- `thread_read_test()` reads a per-child file sequentially, with optional read trajectories, verification, disruption, latency output, and `THREAD_READ_TEST` stats.
- `thread_pread_test()` is the positional-read variant. It uses `I_PREAD()` for normal I/O and also supports async/mmap paths.
- `thread_rread_test()` repeats the read path for reread statistics and publishes `THREAD_REREAD_TEST`.
- `thread_reverse_read_test()` seeks to the final record and reads backward, maintaining both descriptor position and a `current_position` value for mmap/async verification. It publishes `THREAD_REVERSE_READ_TEST`.
- `thread_stride_read_test()` begins in this chunk. The visible portion chooses child identity, CPU binding, per-child filename, read/direct flags, Windows unbuffered handle, `I_OPEN()`, async setup, VxFS/Solaris direct-I/O setup, and mmap setup; its actual stride loop is outside this chunk.

## Control Flow

The single-process benchmark routines follow a common pattern:

1. Compute `numrecs64` and `filebytes64`, optionally replacing them with trajectory file operation count and file size.
2. Build open flags from global settings such as `oflag`, `odsync`, `read_sync`, `direct_flag`, and platform-specific direct I/O flags.
3. Run one or two passes, depending on `noretest`. Pass 0 is the primary test; pass 1 is the repeat, rewrite, reread, or random-write side depending on the function.
4. Optionally purge cache with `purge_buffer_cache()`, open the target file, initialize async state or mmap state, prefetch buffers with `fetchit()`, seed fill patterns with `fill_buffer()`, and start wall/CPU timers.
5. Loop over records, optionally adjust offsets and record lengths from `get_traj()`, acquire record locks with `mylockr()`, burn synthetic compute time via `do_compute()`, rotate through `mbuffer` when `multi_buffer` is enabled, purge cache lines with `purgeit()`, execute the I/O operation, verify data with `verify_buffer()`, collect latency/histogram samples, and release locks.
6. End async queues with `end_async()`, flush/mmap-sync when requested, close or defer close according to `include_close`, subtract `time_res` and synthetic compute time, clamp tiny measurements to `time_res`, and store rates through `store_value()` and optional `store_times()`.

The rate calculation is consistent across routines. Normal throughput is bytes divided by elapsed time and then shifted from bytes/sec to KB/sec. `OPS_flag` reports operations/sec by using record counts. `MS_flag` reports microseconds per operation by calculating `1000000 * elapsed / operations`.

The threaded workers follow the same structure but add process/thread orchestration. Each worker derives a slot `xx` from the thread argument or global `chid`, optionally binds the thread to a CPU, selects a per-child filename from `filearray[]` with `share_file` and `mfflag` rules, initializes `struct child_stats` in `shmaddr[xx]`, marks itself `CHILD_STATE_READY`, then waits either for distributed master commands (`tell_master_ready()`, `wait_for_master_go()`) or for the parent to set `CHILD_STATE_BEGIN`. On completion or controlled stop, workers set throughput, actual work completed, CPU times, distributed stats, and `CHILD_STATE_HOLD`.

Stonewalling and stop behavior are important. Many throughput workers set `*stop_flag` when one child finishes unless `xflag` disables that behavior. Write workers still try to complete the write even after a stop signal because later read workers need the full test file; they record the pre-stop completed amount but continue writing to avoid downstream read failures.

## State and Persistence Behavior

Persistent filesystem state is the benchmark target files and per-child throughput files. Single-process tests use global `filename`. Throughput workers use `filearray[xx]` directly under multi-file mode or append `.DUMMY.<slot>` otherwise; `share_file` forces multiple workers onto slot zero's file name. Several error paths unlink child files unless `no_unlink` is set.

Optional sidecar output files are created in the working directory:

- Single-process latency logs such as `wol.dat`, `rwol.dat`, `rol.dat`, and `rrol.dat` are opened elsewhere or in this chunk depending on test type.
- Thread workers create files such as `Child_<n>_wol.dat`, `Child_<n>_pwol.dat`, `Child_<n>_rwol.dat`, `Child_<n>_rol.dat`, `Child_<n>_prol.dat`, `Child_<n>_rrol.dat`, and `Child_<n>_revol.dat` for latency traces.
- When `L_flag` is active, workers append start/finish timestamps to `Child_<n>.log`.

In-memory global benchmark state is extensive. This chunk reads and writes `report_array`, `runtimes`, `current_x`, `current_y`, `max_x`, `max_y`, `numrecs64`, `filebytes64`, `rec_prob`, `res_prob`, trajectory counters, random offset `offset64`, shared child stats in `shmaddr`, global stop flags, global buffers (`mainbuffer`, `buffer`, `mbuffer`, `barray`), and spreadsheet cursor state (`bif_row`, `bif_column`).

The mmap path persists dirty writes via `msync()` depending on `mmapasflag`, `mmapssflag`, `mmapnsflag`, `include_flush`, and final cleanup. The normal file path persists according to `fsync()` and `close()` inclusion options. The async path depends on `end_async()` to drain queued requests before measuring final state.

## Dependencies and Integration Points

This code integrates with the rest of `iozone.c` through many globals, macros, and helpers defined outside this chunk:

- Portability wrappers: `I_OPEN`, `I_CREAT`, `I_FOPEN`, `I_LSEEK`, `I_PREAD`, `I_PWRITE`, and platform macros for Windows, HPUX, Linux, AIX, IRIX, FreeBSD, DragonFly, TRU64, Solaris, VxFS, and SysV shared memory.
- Async I/O helpers: `async_init()`, `async_write()`, `async_write_no_copy()`, `async_read()`, `async_read_no_copy()`, `async_release()`, and `end_async()`.
- Mmap helpers: `initfile()`, `mmap_end()`, and `fill_area()`.
- Verification and data-pattern helpers: `fill_buffer()`, `verify_buffer()`, `pattern`, `sverify`, `dedup`, `dedup_interior`, `diag_v`, and `multi_buffer`.
- Timing and CPU accounting: `time_so_far()`, `utime_so_far()`, `stime_so_far()`, `cputime_so_far()`, `cpu_util()`, `time_res`, `cputime_res`, and `sc_clk_tck`.
- Locking and disruption: `mylockf()`, `mylockr()`, `disrupt()`, `disruptw()`, `file_lock`, `rlocking`, and `DISRUPT`.
- Trajectory support: `open_w_traj()`, `open_r_traj()`, `get_traj()`, `w_traj_*`, and `r_traj_*`.
- Reporting and spreadsheet helpers: `CONTROL_STRING*`, `create_xls()`, `close_xls()`, `do_label()`, `do_float()`, record-size list helpers, and include masks such as `WRITER_MASK`, `READER_MASK`, `PREADV_MASK`.
- Distributed throughput control: `tell_master_ready()`, `wait_for_master_go()`, `tell_master_stats()`, `send_stop()`, `client_error`, `client_iozone`, and `chid`.

The code also depends directly on OS APIs such as `read()`, `write()`, `fread()`, `fwrite()`, `fsync()`, `close()`, `fclose()`, `select()`, `mmap()`, SysV `shmget()`/`shmat()`/`shmctl()`, `system("umount ...")`, `system("mount ...")`, `pthread_setaffinity_np()`, VxFS `ioctl(VX_SETCACHE)`, Solaris `directio()`, and Windows `CreateFile()`, `ReadFile()`, `WriteFile()`, `SetFilePointer()`, and `CloseHandle()`.

## Risks and Edge Cases

- Many routines mutate `reclen` inside trajectory loops. Later calculations that recompute `filebytes64 = numrecs64 * reclen` can be wrong if a trajectory changed `reclen`; some write/read tests instead use trajectory byte and operation counters to compensate.
- Several no-copy async paths allocate an aligned buffer per operation and pass the original allocation pointer to the async layer. Correct cleanup depends on `async_write_no_copy()`/`async_read_no_copy()` and `async_release()`.
- Direct I/O requires alignment and size discipline. The code uses aligned buffers in no-copy paths and global buffers elsewhere, but any change to buffer allocation can break `O_DIRECT`/Windows unbuffered operation.
- Error handling is inconsistent by historical design: some paths call `signal_handler()`, some `exit()`, some `perror()` and continue only for stop-flag cases. This matters for automation because failures may terminate the whole process from deep inside a worker.
- `random_perf_test()` uses a shuffled record array if allocation succeeds, but falls back to pseudo-random draws that can repeat records. That changes the semantic from unique random coverage to sampled random access.
- `create_list()` uses a `goto again` collision loop and can become inefficient when `PVECMAX` approaches `numrecs64`; it relies on earlier clamping of vector count.
- Worker stop accounting subtracts the current record from completed KB/bytes when `*stop_flag` is set. With small `reclen` values below 1024, KB counters based on `reclen/1024` can lose sub-KB progress.
- `purge_buffer_cache()` builds shell commands by concatenating `mountname` into fixed-size buffers and invokes `system()`. It assumes trusted configuration and a mountpoint string that fits.
- `alloc_mem()` has several platform paths with temporary files and anonymous mmap. Some paths do not close temporary file descriptors in this chunk, relying on process cleanup or neighboring code assumptions.
- The per-thread CPU binding code differs by platform. `thread_pread_test()` only shows an HPUX binding block in this chunk, while other workers include Linux affinity handling.
- The read and reread workers sometimes report positional pread stats using `THREAD_READ_TEST` in distributed reporting, while local log names distinguish pread. That coupling needs care when interpreting distributed results.
- `thread_stride_read_test()` is incomplete in this chunk; any analysis of its runtime loop must be merged with the following chunk.

## Test Signals

Useful validation signals for this chunk include:

- Matrix output tests that compare column count and labels for normal, `-e` extended, read/write-only, mmap, async, `HAVE_PREAD`, and `HAVE_PREADV` builds.
- Throughput rate tests under normal KB/sec, `OPS_flag`, and `MS_flag`, including `noretest` cases where second-pass values should be zero.
- Verification-mode runs across write/read/rewrite/random/reverse/stride paths with `diag_v`, `dedup`, `dedup_interior`, and `multi_buffer` enabled.
- Trajectory-file runs for read, write, pwrite, and pread paths, checking variable offsets, sizes, latency output, operation counts, and byte totals.
- Async and no-copy async runs with verification enabled, confirming `async_release()` and buffer ownership paths do not corrupt data.
- Mmap runs with sync, async-sync, and no-sync options, checking `msync()` and cleanup behavior.
- Direct I/O runs on Linux, Solaris, VxFS, and Windows-unbuffered builds, especially with varying record sizes and alignment-sensitive buffers.
- File-lock and record-lock runs that exercise both read-lock and write-lock modes.
- Random access tests with file sizes smaller than `PVECMAX`, plus forced allocation failure or small-memory environments to cover random fallback behavior.
- Thread/process throughput runs with multiple child counts, `share_file`, `mfflag`, `xflag` stonewalling, distributed client mode, CPU-utilization reporting, per-child latency files, and operation-rate limiting.
- Failure-path tests for short read/write, missing files for reread/rewrite, direct I/O setup failure, inability to open sidecar logs, and cache-purge mount command failure.

## Chunk Boundaries

The chunk begins after the setup and opening portion of `write_perf_test()`, so final synthesis should merge it with the previous chunk to describe initial write flags, file creation, mmap initialization, and `wqfd` setup. It ends immediately after `thread_stride_read_test()` maps or opens the file; the stride-read wait, loop, verification, accounting, cleanup, and stats publishing continue in a later chunk.
