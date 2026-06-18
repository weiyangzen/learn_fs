# Research Group subset-b-009231

This grouped report covers the requested fio source files. Each section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/server.c -->
# sources/test-tools/fio/server.c

## Purpose
`server.c` implements fio's client/server transport endpoint. It listens on TCP, IPv6, or Unix-domain sockets, accepts client connections, parses network commands, starts backend jobs, forwards text/statistics/disk-util/log data back to the client, and supports daemon pidfile mode. It is a central integration point between fio's job parser/backend, shared-memory allocator, statistics subsystem, verify-state exchange, disk-util reporting, and optional zlib log compression.

## Important APIs, Types, And Functions
The file exports `fio_start_server()`, `fio_server_text_output()`, `fio_net_send_cmd()`, `fio_net_send_simple_cmd()`, `fio_server_parse_string()`, `fio_server_parse_host()`, `fio_server_op()`, `fio_server_got_signal()`, `fio_net_recv_cmd()`, `fio_send_iolog()`, `fio_server_send_ts()`, `fio_server_send_gs()`, `fio_server_send_du()`, `fio_server_send_job_options()`, `fio_server_get_verify_state()`, `fio_server_send_add_job()`, `fio_server_send_start()`, `fio_net_send_quit()`, and pthread key setup/destruction helpers. Internally, `struct sk_entry` represents queued outbound commands and linked vector fragments; `struct fio_fork_item` tracks connection/job child processes or Windows handles; `struct cmd_reply` synchronizes sendfile/verify-state replies.

The core wire helpers are `__fio_init_net_cmd()`, `fio_init_net_cmd()`, `fio_net_cmd_crc()`, `verify_convert_cmd()`, `fio_recv_data()`, `fio_sendv_data()`, and `fio_net_recv_cmd()`. They enforce little-endian protocol fields, command CRCs, payload CRCs, payload fragment limits, and protocol version matching. `fio_net_recv_cmd()` also defragments commands marked `FIO_NET_CMD_F_MORE` and null-terminates text/job buffers after receipt.

Connection lifecycle is handled by `fio_server()`, `fio_init_server_connection()`, `accept_loop()`, `handle_connection()`, `handle_command()`, and `handle_run_cmd()`. Outbound asynchronous sending is managed through `sk_out_assign()`, `sk_out_drop()`, `fio_net_queue_cmd()`, `fio_net_queue_entry()`, `handle_xmits()`, `handle_sk_entry()`, `send_vec_entry()`, and `finish_entry()`.

## Control Flow
Startup enters `fio_start_server()`. Without a pidfile it calls `fio_server()` directly; with a pidfile it checks for an existing live server, forks into a daemon, redirects standard streams to `/dev/null`, enables syslog logging, and unlinks the pidfile on exit. `fio_server()` parses the configured bind argument, installs signal handlers, opens the listening socket, and enters `accept_loop()`.

For each accepted connection, Unix builds fork a child and Windows starts a child process through a pipe/duplicated socket. The child assigns the connection `sk_out` to thread-specific storage, then `handle_connection()` repeatedly flushes outbound queue entries, polls for inbound commands, receives one `fio_net_cmd`, and dispatches it. Job definition commands call `parse_jobs_ini()` or `parse_cmd_line()` and then send `FIO_NET_CMD_START`; `FIO_NET_CMD_RUN` forks/runs `fio_backend()`; `FIO_NET_CMD_SEND_ETA` sends ETA data; `FIO_NET_CMD_UPDATE_JOB` converts packed options into a running job; `FIO_NET_CMD_VTRIGGER` exports all I/O state, terminates threads, and executes the trigger.

When the fio backend is running in server mode, stats calls in other modules enqueue network messages. `fio_server_send_ts()` converts `thread_stat` and `group_run_stats`, appends optional per-priority latency arrays and steady-state ring buffers, and queues `FIO_NET_CMD_TS`. `fio_send_iolog()` builds a vector command: header first, then plain log chunks, pre-compressed chunks, or zlib-compressed chunks. `fio_server_send_du()` sends one disk-util PDU per disk.

## State And Persistence Behavior
Global state includes `fio_net_port`, `exit_backend`, `fio_server_arg`, `bind_sock`, socket address globals, zlib capability flags, the remote server name `me`, and the pthread-specific `sk_out_key`. `struct sk_out` holds a reference count, socket fd, semaphores, and a queued outbound list; reference count discipline is essential across connection children and backend children. `exit_backend` is the process-wide shutdown flag used by loops and send/recv retry paths.

Persistent filesystem state is limited to server pidfiles and Unix socket paths. `fio_start_server()` writes and later unlinks the pidfile in daemon mode; signal handling unlinks `bind_sock`. Verify-state transfer requests a file from the client via `FIO_NET_CMD_SENDFILE`, validates `verify_state_hdr`, copies only the `thread_io_list`, and stores it in caller-owned memory.

## Dependencies And Integration Points
This file depends heavily on `server.h`, `stat.h`, `diskutil.h`, `fio.h`, `options.h`, `verify-state.h`, `smalloc.h`, endian helpers, CRC16, semaphores, fork/wait or Windows process APIs, sockets, poll, and optional zlib. It is called by the fio backend/stat/logging layers whenever server-mode output is needed. It also consumes `thread_options_pack` conversion routines and fio global job/thread lists.

## Risks And Edge Cases
The protocol is bounded by `FIO_SERVER_MAX_FRAGMENT_PDU` and `FIO_SERVER_MAX_CMD_MB`, but the maximum command limit is very large and still relies on allocation success. Pointer arithmetic on `void *` is a GNU C assumption. `fio_server_parse_string()` mutates the supplied string when splitting on comma, so callers must pass mutable storage. `fio_server_send_ts()` must keep `thread_stat` layout and offset fields synchronized with client-side decode logic; packed structs with pointer/offset unions are ABI-sensitive. Asynchronous queue ownership depends on `SK_F_FREE`, `SK_F_COPY`, and `SK_F_VEC`; mismatched flags would leak or double-free memory. Signal handling is minimal and `fio_server_got_signal()` asserts that a `sk_out` exists. zlib histogram log sending mutates histogram entries by subtracting previous buckets before transfer.

## Test Signals
Useful tests are client/server probe/version mismatch tests, fragmented command CRC failure tests, job/jobline/load-file command round trips, ETA/update-job/verify-state reply tests, zlib and non-zlib iolog transfer tests, daemon pidfile conflict tests, Unix socket binding tests, IPv4/IPv6 parse tests, and process cleanup tests where job children exit by status or signal.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/server.h -->
# sources/test-tools/fio/server.h

## Purpose
`server.h` defines fio's network protocol contract and public server API. It is the shared header for encoding/decoding server commands, payload structures, feature flags, and server-mode function entry points.

## Important APIs, Types, And Functions
`struct sk_out` describes a server output channel: reference count, socket fd, lock, pending transmit list, wait semaphore, and transmit semaphore. `struct fio_net_cmd` is the wire header with protocol version, opcode, flags, tag, payload length, command CRC, payload CRC, and flexible payload. The comment states that on-wire encoding is little-endian.

The command enum defines `FIO_SERVER_VER`, fragmentation and maximum command limits, all `FIO_NET_CMD_*` opcodes, `FIO_NET_CMD_F_MORE`, CRC coverage size, name limits, timeout, and probe flags. Payload structs include job/jobline/load-file PDUs, text output, thread-stat and disk-util PDUs, probe request/reply, start/end messages, iolog descriptors, sendfile replies, and job option notifications.

Exports include startup/configuration (`fio_start_server()`, `fio_server_set_arg()`, `fio_server_internal_set()`), parsing (`fio_server_parse_string()`, `fio_server_parse_host()`), transport (`fio_net_send_cmd()`, `fio_net_send_simple_cmd()`, `fio_net_recv_cmd()`, `fio_server_poll_fd()`, `fio_net_send_quit()`), output (`fio_server_text_output()`, `fio_server_send_ts()`, `fio_server_send_gs()`, `fio_server_send_du()`, `fio_send_iolog()`), job notifications, verify-state retrieval, and socket-key lifecycle.

## Control Flow
Callers configure the bind string, initialize the socket key, and start the server. During runtime, backend code uses the exported send functions to serialize stats/logs to the connected client. Client and server agree on opcodes and PDU layouts through this header; `server.c` performs endian conversion before sending and after receiving.

## State And Persistence Behavior
The header exposes `exit_backend` and `fio_net_port`, making server shutdown and port configuration globally visible. The protocol embeds variable-length data with flexible arrays, so payload lifetime and size are managed by callers rather than the header itself.

## Dependencies And Integration Points
It includes `stat.h` and `diskutil.h` because network payloads embed `thread_stat`, `group_run_stats`, and disk-util data. It also requires socket address types and fio sem/list definitions indirectly through included project headers.

## Risks And Edge Cases
Packed or flexible payload structs are ABI-sensitive. Any change to `FIO_SERVER_VER`, `thread_stat`, `group_run_stats`, or payload field order requires matching conversion code and client support. The typo in the `pdu_len` comment is harmless, but it highlights that comments should not be treated as protocol proof. Fixed name/value arrays in `cmd_job_option` can truncate data and rely on explicit truncation flags.

## Test Signals
Compile-time protocol tests should ensure struct sizes/offsets match client decode expectations. Runtime tests should cover each opcode, payload fragmentation, CRC failures, little/big endian conversion, zlib probe negotiation, and older-client version rejection.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/server.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/smalloc.c -->
# sources/test-tools/fio/smalloc.c

## Purpose
`smalloc.c` implements fio's simple shared allocator backed by `mmap()`. It provides zeroed allocations that are visible across forked processes and threads, which is important for fio structures shared between the main process, job workers, and server/backend code.

## Important APIs, Types, And Functions
The public API is `sinit()`, `scleanup()`, `smalloc()`, `scalloc()`, `sfree()`, `smalloc_strdup()`, and `smalloc_debug()`. The allocator divides each pool into 32-byte blocks (`SMALLOC_BPB`) tracked by an unsigned-int bitmap. `struct pool` stores the mmap region, bitmap address, free/total counts, next non-full bitmap word, mmap size, and a semaphore lock. `struct block_hdr` stores the allocated size and, when redzones are enabled, a pre-redzone marker.

Allocation walks pools starting from `last_pool`. `smalloc_pool()` computes the allocation size including header/redzones, calls `__smalloc_pool()` to find contiguous free bitmap bits, writes the header, fills redzones, and zeroes user memory. `sfree()` finds the owning pool by range check, verifies redzones, clears bitmap bits, and updates free counters.

## Control Flow
`sinit()` maps the pool descriptor array once and then adds up to `INITIAL_POOLS` pools using `add_pool()`. `add_pool()` rounds the pool to block/bitmap boundaries, maps shared anonymous memory, places the bitmap at the end of the data area, and initializes the lock. Allocation scans bitmap words with `find_best_index()`, `find_next_zero()`, and `blocks_free()` before marking bits with `set_blocks()`. Freeing reverses the block calculation and calls `clear_blocks()`.

## State And Persistence Behavior
Allocator state is process memory mapped with `MAP_SHARED` except ESX builds use `MAP_PRIVATE`. Globals `mp`, `nr_pools`, and `last_pool` track pool descriptors and the preferred pool. `smalloc_pool_size` is externally configurable. There is no persistent on-disk state; `scleanup()` unmaps pools and descriptor storage.

## Dependencies And Integration Points
The file depends on fio semaphores, OS mmap flags, logging, and utility alignment/bit helpers. It is used by server queue entries, stats per-priority arrays, and other fio data that must survive or be visible after fork. Callers must pair `smalloc`/`scalloc` with `sfree`, not `free`, except for data explicitly allocated by libc in other modules.

## Risks And Edge Cases
`scalloc(nmemb, size)` does not check multiplication overflow. `ptr_valid()` and several allocation/free paths use `void *` arithmetic, which assumes compiler extensions. `sfree()` only logs if a pointer is not from any pool and does not abort, which can hide ownership bugs. Redzone checks assert on corruption but cannot detect all overwrites. The allocator never grows beyond `MAX_POOLS`; OOM only logs and returns NULL. `scleanup()` does not reset globals, so repeated cleanup/reinit lifecycles would be risky unless process exit follows.

## Test Signals
Tests should cover allocations around block boundaries, large allocation pool sizing, redzone corruption detection, freeing in different order, multi-pool fallback, shared visibility after fork, concurrent allocations under locks, `smalloc_strdup()` contents, and OOM behavior with small `--alloc-size`.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/smalloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/smalloc.h -->
# sources/test-tools/fio/smalloc.h

## Purpose
`smalloc.h` declares fio's shared-memory allocation API.

## Important APIs, Types, And Functions
It exports `smalloc(size_t)`, `scalloc(size_t, size_t)`, `sfree(void *)`, `smalloc_strdup(const char *)`, `sinit()`, `scleanup()`, `smalloc_debug(size_t)`, and the configurable `smalloc_pool_size`.

## Control Flow
Users initialize the allocator with `sinit()` before shared allocations, allocate zeroed memory with `smalloc()` or `scalloc()`, release with `sfree()`, and call `scleanup()` during shutdown.

## State And Persistence Behavior
The header exposes only the pool-size knob. The implementation owns all pool state and uses mmap-backed memory rather than durable storage.

## Dependencies And Integration Points
Consumers include server transport objects, stats aggregation arrays, and any fio code needing allocations visible across process boundaries.

## Risks And Edge Cases
The API resembles libc but ownership is distinct: `sfree()` must be used for `smalloc` memory. `scalloc()` has libc-like parameters but the implementation does not guarantee overflow checking. Callers must handle NULL returns.

## Test Signals
Compile coverage should verify all users include this header rather than redeclaring allocator APIs. Runtime tests should verify initialization ordering and correct free-family use.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/smalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/sprandom.c -->
# sources/test-tools/fio/sprandom.c

## Purpose
`sprandom.c` implements fio's SPRandom offset generator for SSD steady-state style workloads. It models a physical device with over-provisioning, divides it into regions with a validity distribution derived from Desnoyers' SSD write-amplification model, and generates writes plus replayed invalidations to approximate region-level steady-state data validity.

## Important APIs, Types, And Functions
The public functions are `sprandom_init()`, `sprandom_get_next_offset()`, and `sprandom_free()`. Distribution helpers include `compute_waf()`, `compute_gc_validity()`, `compute_validity_dist()`, `sample_curve_equally_on_x()`, `linear_interp()`, `linspace()`, and `reverse()`. Capacity/layout helpers include `sprandom_physical_size()`, `estimate_inv_capacity()`, and `sprandom_setup()`.

Mutable write scheduling is centered on `struct sprandom_info` from `sprandom.h`: over-provisioning, region size/count, cache size, per-region invalid percentages, a two-phase `pc_buf`, invalid counts per phase, current region, current phase, region write counts, remaining writes, and random state. `sprandom_add_with_probability()` probabilistically stages offsets for later invalidation; `sprandom_get_next_offset()` alternates between replaying invalid offsets and consuming the file LFSR.

## Control Flow
`sprandom_init()` exits early when the job option is disabled. Otherwise it allocates `sprandom_info`, determines logical size from file size and requested I/O size, computes physical `td->o.io_size`, stores the fio random state, and calls `sprandom_setup()`. Setup computes the validity distribution, converts validity to invalid percentages at `PCT_PRECISION`, validates optional cache size against region size, estimates invalid buffer capacity with a six-sigma margin, allocates the `pc_buf`, and initializes region/phase counters.

During generation, `sprandom_get_next_offset()` first replays pending invalid offsets either before entering the next region or, when cache deferral is configured, at the end of the current region. When region writes are exhausted, it prints invalidation diagnostics, flips phase, commits staged offsets, advances `current_region`, and sets `writes_remaining` to region capacity minus pending invalidations for that phase. It then pulls a fresh LFSR offset, decrements writes remaining, and may stage that offset for future invalidation based on the current region's invalid probability.

## State And Persistence Behavior
All state is in-memory per file through `f->spr_info`. The generator mutates `td->o.io_size` to the modeled physical size. `invalid_buf` is a staged/committed two-phase buffer, so generated offsets depend on prior calls and cannot be recomputed statelessly from a position alone. There is no persistent state across process runs.

## Dependencies And Integration Points
The file depends on fio job options (`sprandom`, `spr_over_provisioning`, `spr_num_regions`, `spr_cache_size`, block size), `struct fio_file`, the file LFSR, `pcbuf`, fio random helpers, logging buffers, `bytes2str_simple()`, math functions, and pow2 utilities. It integrates with file offset selection by attaching `sprandom_info` to `fio_file`.

## Risks And Edge Cases
`compute_waf()` divides by over-provisioning and assumes valid nonzero input. `compute_gc_validity()` asserts WAF > 1.0. `compute_validity_dist()` calls `reverse(validity_distribution, n_regions)` at `out`; if allocation failed before `validity_distribution` is assigned, this can pass NULL with nonzero size and dereference it. Several allocation failures in `sprandom_setup()` free only part of the initialized state; `invalid_buf` is not freed on all later setup failures. `sprandom_free()` uses `free(info->invalid_buf)` even though allocation is through `pcb_alloc()`, which is correct only if `pcbuf` promises libc-compatible allocation. Buffer capacity overflow asserts rather than returning an error.

## Test Signals
Tests should validate distribution generation for one, many, and invalid region counts; over-provisioning boundary handling; cache size rejection; deterministic offset streams for a fixed seed; invalidation percentages within statistical tolerance; LFSR exhaustion with and without cache deferral; and leak/error-path behavior under forced allocation failures.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/sprandom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/sprandom.h -->
# sources/test-tools/fio/sprandom.h

## Purpose
`sprandom.h` defines the state and API for SPRandom SSD steady-state offset generation.

## Important APIs, Types, And Functions
`struct sprandom_info` carries configuration (`over_provisioning`, `region_sz`, `cache_sz`, `num_regions`), invalidation probability/state (`invalid_pct`, `invalid_buf`, `invalid_capacity`, `invalid_count`, `current_region`, `curr_phase`), progress counters (`region_write_count`, `writes_remaining`), and fio random state. It declares `sprandom_init()`, `sprandom_free()`, and `sprandom_get_next_offset()`.

## Control Flow
The fio file/job initialization path calls `sprandom_init()`, offset selection repeatedly calls `sprandom_get_next_offset()`, and cleanup calls `sprandom_free()`.

## State And Persistence Behavior
The state struct is mutable and per-file. It does not describe durable storage; it controls one in-memory sequence of generated and replayed offsets.

## Dependencies And Integration Points
The header depends on `lib/rand.h` and `pcbuf.h`, and its function signatures depend on fio's `thread_data` and `fio_file` types from surrounding project headers.

## Risks And Edge Cases
The comments contain minor typos, but the larger risk is that callers must not copy `sprandom_info` shallowly because it owns heap pointers and staged buffer state. The API returns integer status but does not encode detailed terminal reasons.

## Test Signals
Compile tests should ensure all users see a consistent struct definition. Runtime tests should validate lifecycle pairing and that `sprandom_get_next_offset()` returns 1 only at expected end-of-sequence conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/sprandom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/stat.c -->
# sources/test-tools/fio/stat.c

## Purpose
`stat.c` is fio's main statistics engine. It collects per-I/O latency, bandwidth, IOPS, depth, error, CPU, disk-util, steady-state, and trim-block-lifetime samples; aggregates them across jobs/groups; renders normal, terse, and JSON output; and in backend mode serializes final stats to the server transport.

## Important APIs, Types, And Functions
Public collection APIs include `add_clat_sample()`, `add_slat_sample()`, `add_lat_sample()`, `add_bw_sample()`, `add_iops_sample()`, `add_sync_clat_sample()`, `add_agg_sample()`, `calc_log_samples()`, `finalize_logs()`, `regrow_logs()`, and `reset_io_stats()`. Public reporting and aggregation APIs include `__show_run_stats()`, `__show_running_run_stats()`, `show_running_run_stats()`, `check_for_running_stats()`, `show_thread_status()`, `show_group_stats()`, `sum_thread_stats()`, `sum_group_stats()`, `init_thread_stat()`, `init_group_run_stat()`, `alloc_clat_prio_stat_ddir()`, `free_clat_prio_stats()`, and disk-util JSON/text helpers.

Core statistical helpers include `add_stat_sample()` for online mean/variance, `__sum_stat()` for parallel variance merge, `plat_val_to_idx()` and `plat_idx_to_val()` for latency percentile buckets, `calc_clat_percentiles()`, `stat_calc_dist()`, latency distribution calculators, and block lifetime percentile helpers.

## Control Flow
I/O paths call `add_slat_sample()`, `add_clat_sample()`, `add_lat_sample()`, `add_bw_sample()`, and `add_iops_sample()` as work is issued/completed. These update `thread_stat` fields, percentile histograms, per-priority stats, and optional log buffers. Periodic logging flows through `calc_log_samples()`, which samples bandwidth and IOPS windows when threads are in logging states and returns the next wakeup delay. `finalize_logs()` flushes averaged log windows at job end.

Final reporting starts in `__show_run_stats()`: it allocates one `group_run_stats` per group and enough `thread_stat` slots for either per-thread or group-reporting mode, initializes per-priority behavior, folds each `thread_data` into the selected aggregate, builds group bandwidth/runtime summaries, and writes normal/terse/JSON buffers or server messages depending on `is_backend`. Running-stat snapshots use `__show_running_run_stats()`, which asks workers to refresh rusage outside `stat_sem`, temporarily adds current runtime deltas, calls `__show_run_stats()`, then rolls back temporary runtime changes.

## State And Persistence Behavior
`stat_sem` is a shared semaphore protecting out-of-band stat snapshots. `agg_io_log[]`, `write_bw_log`, fio global thread lists, disk lists, output format globals, and status-file state are external/global integration points. Persistent behavior is limited to the trigger file `/tmp/fio-dump-status` or `$TMPDIR/fio-dump-status`: when present, it is unlinked and causes running stats to be emitted. Logs are accumulated in memory as `struct io_logs` chunks and later written/transmitted by iolog code/server code.

## Dependencies And Integration Points
The file integrates with `fio.h`, `iolog`, `server.c`, `diskutil`, JSON output, helper thread signaling, idletime, zbd status, `steadystate`, `smalloc`, OS rusage, and fio job/thread data. In backend mode it calls server send functions instead of printing locally. It relies on `stat.h` for struct layout shared with network payloads.

## Risks And Edge Cases
Several paths assume initialized min values and valid sample counts; direct struct zeroing without `init_thread_stat()` would skew minima. `stat_calc_lat_nu()` divides by total without an explicit zero guard after `stat_calc_lat()`. Per-priority aggregation allocates with `smalloc`; callers must free with `free_clat_prio_stats()`. `calc_block_percentiles()` computes percentile indexes without an obvious upper-bound clamp for 100% edge cases. Running stats temporarily mutate thread runtimes and require careful rollback under `stat_sem`. Output compatibility is fragile: terse field order and JSON key names are externally consumed. Histogram log code stores pointers requiring later cleanup in iolog processing.

## Test Signals
Tests should cover percentile bucket round trips, percentile sorting, online variance and merged variance, group reporting with mixed read/write/trim, per-priority stats aggregation, terse versions 2-5, JSON and JSON+ bins, steady-state data rendering, disk-util slave aggregation, status-file-triggered running stats, averaged log windows, compressed/uncompressed iolog transfer integration, and async/offload locking paths.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/stat.h -->
# sources/test-tools/fio/stat.h

## Purpose
`stat.h` defines fio's statistics data model, constants, macros, and public stat/reporting API. It is shared by local reporting, backend server serialization, JSON/terse output, and consumers that update per-I/O counters.

## Important APIs, Types, And Functions
`struct group_run_stats` stores per-direction run time, bandwidth extrema, I/O bytes, aggregate bandwidth, base/unit formatting, group id, significant figures, and unified read/write reporting mode. `struct thread_stat` is the packed central per-job/per-group statistics record, including names/errors, latency stats, bandwidth/IOPS stats, rusage, I/O depth maps, latency buckets, totals, errors, block lifetime data, unit formatting, ZBD stats, latency-target state, steady-state fields and data pointers/offsets, per-priority latency stats, and cache hit/miss counts.

Macros define latency bucket sizes, percentile-list size, trim block-info encoding, job name/description sizes, and unified reporting modes. `struct jobs_eta` and `struct jobs_eta_packed` define ETA payload shape. `struct clat_prio_stat` stores a per-priority latency histogram plus summary stat.

Public functions include stat lifecycle, ETA/status display, aggregation, initialization, percentile calculation, distribution calculation, sample addition, log handling, per-priority allocation/free, disk-util output, and `io_u_block_info()`.

## Control Flow
Workers update `thread_stat` through stat.c functions during I/O. Reporting code initializes and sums `thread_stat`/`group_run_stats`, then prints locally or serializes over the server protocol. Inline helpers `nsec_to_usec()` and `nsec_to_msec()` normalize display units.

## State And Persistence Behavior
The header declares `stat_sem`, `agg_io_log[]`, and `write_bw_log`. `thread_stat` contains pointer/offset unions so the same packed struct can represent in-process pointers or network payload offsets for steady-state/per-priority arrays.

## Dependencies And Integration Points
It includes `iolog.h`, `lib/output_buffer.h`, `diskutil.h`, and `json.h`. It is directly embedded in `server.h` network PDUs, so layout changes require protocol conversion updates.

## Risks And Edge Cases
`struct thread_stat` and `group_run_stats` are packed and networked, so alignment, endian conversion, pointer-size assumptions, and field additions are high-risk. Fixed array sizes such as `MAX_NR_BLOCK_INFOS` cap collected detail. The pointer/offset unions are powerful but easy to misuse if code reads a network offset as an in-process pointer.

## Test Signals
ABI tests should check expected struct sizes/offsets and protocol conversion coverage. Functional tests should verify percentile constants, block-info macros, unit conversion helpers, initialization minima, and per-priority allocation/reporting behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/steadystate.c -->
# sources/test-tools/fio/steadystate.c

## Purpose
`steadystate.c` implements fio's steady-state termination logic. It tracks bandwidth, IOPS, and latency over a configured duration and ends jobs when either a slope criterion or maximum-deviation criterion falls below the configured limit.

## Important APIs, Types, And Functions
Public functions are `steadystate_free()`, `steadystate_setup()`, `steadystate_check()`, `td_steadystate_init()`, `steadystate_bw_mean()`, `steadystate_iops_mean()`, and `steadystate_lat_mean()`. Globals are `steadystate_enabled` and `ss_check_interval`. Internal algorithms are `steadystate_slope()` and `steadystate_deviation()`, both of which update ring buffers and criteria in `struct steadystate_data`.

## Control Flow
`td_steadystate_init()` translates job options into per-thread steady-state fields, converts duration/check interval units, initializes regression sums, sets ramp-over state if no ramp time exists, and rejects inconsistent options inside a reporting group. After all jobs are initialized, `steadystate_setup()` allocates ring buffers either per job or on the last thread in each group-reporting group. Periodic `steadystate_check()` skips inactive/exited/attained jobs, computes deltas since the previous check, aggregates group values, waits for ramp time, applies slope or deviation logic, marks `FIO_SS_ATTAINED`, and asks fio to terminate affected threads.

## State And Persistence Behavior
Each `thread_data` owns a `steadystate_data` with ring buffers, head/tail indexes, previous I/O counters, prior latency sums, regression sums, and final criterion values. In group-reporting mode, only one thread per group stores data (`FIO_SS_DATA`), while attainment is propagated to every thread in the group. State is in-memory only but copied into `thread_stat` for final reports.

## Dependencies And Integration Points
The file depends on `fio.h`, `steadystate.h`, thread iteration macros, async I/O locks, `fio_gettime()`, `fio_mark_td_terminate()`, and stat fields for completion latency means/samples. `stat.c` uses the exported mean helpers and report fields to render steady-state output.

## Risks And Edge Cases
Interval count is computed by dividing duration by `ss_check_interval / 1000L`; invalid small intervals or durations can produce zero or divide-by-zero risks if option validation elsewhere fails. Allocation failures in `steadystate_alloc()` are not checked before setting `FIO_SS_DATA`. Slope calculations assume equally spaced x-values even though comments admit real intervals may drift. Group aggregation depends on thread iteration order by group id. Latency uses completion-latency mean deltas, so jobs with no latency samples get zero group latency.

## Test Signals
Tests should cover slope and deviation attainment, percent and absolute criteria, ramp-time delay, group-reporting propagation, inconsistent group option rejection, zero/short duration validation, allocation failure behavior, and final report ring ordering after wraparound.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/steadystate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/steadystate.h -->
# sources/test-tools/fio/steadystate.h

## Purpose
`steadystate.h` declares steady-state configuration/state and public helpers used by fio job setup, periodic checking, and statistics reporting.

## Important APIs, Types, And Functions
`struct steadystate_data` stores limit, duration, ramp time, state flags, ring-buffer head/tail, IOPS/bandwidth/latency data buffers, computed slope/deviation/criterion, regression sums, previous sample time/counters, and previous latency accumulators. It declares allocation/free/check/init/reporting helpers and exposes `steadystate_enabled` and `ss_check_interval`.

The enum values define bit positions and masks for IOPS, bandwidth, slope mode, attained/ramp/data state, percent criterion, buffer-full state, latency mode, and combined slope presets.

## Control Flow
Job initialization fills `steadystate_data`; setup allocates buffers; runtime checks mutate the ring and may terminate jobs; final stats copy steady-state fields into `thread_stat` and call mean helpers.

## State And Persistence Behavior
All state is per thread or per reporting group and in-memory. Data pointers are later mirrored into `thread_stat` for output and network transport.

## Dependencies And Integration Points
The header includes `thread_options.h` and is consumed by `steadystate.c`, `stat.c`, and server stat serialization. Its flag definitions must align with job option parsing and report rendering.

## Risks And Edge Cases
The bitmask API allows invalid combinations unless option parsing rejects them. Duration and interval units are not self-evident from the struct alone, so callers must follow initialization conventions.

## Test Signals
Tests should assert expected flag combinations, initialized default state, mean helper behavior, and compatibility between option parser state bits and report output.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/steadystate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/arch.c -->
# sources/test-tools/fio/t/arch.c

## Purpose
`t/arch.c` is a tiny test-support definition file that provides architecture globals needed by fio library code when building standalone tests.

## Important APIs, Types, And Functions
It includes `../arch/arch.h` and defines `unsigned long arch_flags = 0;` and `int arch_random;`.

## Control Flow
There is no runtime control flow. The file satisfies linker requirements for tests that include code expecting these globals.

## State And Persistence Behavior
The globals are process-local test state and start at zero/default initialization. No persistent state exists.

## Dependencies And Integration Points
Standalone test binaries can link this file when they use fio architecture helpers without linking the full fio runtime.

## Risks And Edge Cases
Because it hardcodes neutral values, tests using it may not exercise architecture-specific flags or random-device behavior. If production code starts requiring initialized `arch_random`, this stub may mask missing setup.

## Test Signals
The primary signal is successful linking/running of standalone tests. Architecture-specific tests should avoid this stub or explicitly set the globals.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/arch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/axmap.c -->
# sources/test-tools/fio/t/axmap.c

## Purpose
`t/axmap.c` is a standalone executable test for fio's `axmap` bit map and LFSR interaction. It validates bit setting, duplicate detection, multi-bit set behavior, overlap handling, and `axmap_next_free()` wraparound/full-map behavior.

## Important APIs, Types, And Functions
The tests call `lfsr_init()`, `lfsr_next()`, `axmap_new()`, `axmap_free()`, `axmap_set()`, `axmap_isset()`, `axmap_set_nr()`, and `axmap_next_free()`. Test functions are `test_regular()`, `check_next_free()`, `test_next_free()`, `test_multi()`, `test_overlap()`, and `main()`. `struct overlap_test` defines table-driven expected return values for overlapping range sets.

## Control Flow
`main()` accepts optional map size and seed, then runs regular single-bit coverage, multi-bit range tests at offsets 0 and 17, overlap table tests, next-free tests at the chosen size, and two additional next-free stress cases sized to exercise deeper axmap levels. It returns distinct nonzero codes for each failing phase.

## State And Persistence Behavior
Each test creates a fresh `struct axmap`, mutates bits, prints progress to stdout, and frees the map. There is no persistent state. The LFSR seed controls deterministic pseudo-random traversal for repeatability.

## Dependencies And Integration Points
The file depends on fio's `lib/lfsr.h` and `lib/axmap.h`. It is a direct test signal for allocator/map code used by fio random offset selection and other bit-tracking logic.

## Risks And Edge Cases
There appears to be a suspicious check in `test_multi()` using `axmap_isset(map, val + i)` inside a loop where `i` already ranges from `val` to `val + 127`, which tests `2 * val` onward for nonzero offsets rather than the intended range. Default `size` is cast to `unsigned int map_size` in `test_multi()`, so very large user-provided sizes can truncate. Some loops use `int i` for values derived from `uint64_t size`, which can be unsafe for huge inputs.

## Test Signals
Expected successful output is each phase printing `pass!` or table rows marked `PASS`, with process exit 0. Failures identify duplicate bits, missing set bits, short LFSR loops, incorrect `set_nr()` counts, incorrect next-free values, full-map handling failures, or out-of-bounds next-free behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/axmap.c -->
