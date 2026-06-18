# Research Report: subset-b-006794

Grouped research for Linux BPF selftest benchmark, helper, fixture, and map-test files under `sources/distributed-fs/ceph-client/tools/testing/selftests/bpf`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_local_storage.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_local_storage.c

Purpose: defines three benchmark-harness entries for task local-storage lookup cost: sequential cache lookup, interleaved hot-map lookup, and a prepopulated hash-map control. It compares `BPF_MAP_TYPE_TASK_STORAGE` against ordinary hash maps through an array-of-maps populated from user space.

Important APIs and functions: `bench_local_storage_argp` parses `--nr_maps` and `--hashmap_nr_keys_used`; `validate()` enforces one producer, no consumers, `MAX_NR_MAPS`, and `HASHMAP_SZ`; `prepopulate_hashmap()` fills hash maps; `__setup()` opens/loads the skeleton, builds inner maps with BTF metadata, updates the map-in-map, and attaches `get_local`; setup variants select hash map versus local storage and sequential versus interleaved rodata flags. `producer()` repeatedly triggers the attached BPF program with `getpgid`.

Control flow: benchmark setup initializes libbpf, opens `local_storage_bench.skel.h`, configures rodata, loads the skeleton, creates requested maps, updates the map array, and attaches the selected BPF program. During execution, one producer loops forever; `measure()` atomically swaps BSS counters into `bench_res`.

State and persistence: all benchmark state is process-local except kernel BPF maps and links created for the run. BSS counters `hits` and `important_hits` are reset on each measurement. Created map fds are inserted into the map-in-map and then owned by the benchmark process/skeleton lifetime.

Dependencies and integration points: depends on the generic `bench.h` runner, libbpf map creation/update APIs, generated `local_storage_bench` skeleton, BTF type IDs for map creation, and reporting helpers `local_storage_report_progress/final`.

Risks: `HASHMAP_SZ` prepopulation is expensive and can dominate setup for large runs; `bpf_map_create()` fds are not explicitly closed after insertion; BTF mismatch between inner-map template and created maps would fail load/update; benchmark validity depends on synchronized constants with the BPF side.

Test signals: successful runs print local-storage throughput/latency summaries and reject unsupported producer/consumer counts before load. Useful regressions show up as attach/load failures, map update failures, or changes in `hits` versus `important_hits`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_local_storage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_local_storage_create.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_local_storage_create.c

Purpose: benchmarks creation of BPF local storage owners, either socket storage by creating IPv6 UDP sockets or task storage by creating short-lived pthreads.

Important APIs and functions: argp options `--batch-size` and `--storage-type` select batch count and `BPF_MAP_TYPE_SK_STORAGE` versus `BPF_MAP_TYPE_TASK_STORAGE`. `setup()` loads `bench_local_storage_create.skel.h`, writes `bench_pid`, attaches either `socket_post_create` or `sched_process_fork`, and allocates per-producer fd/thread arrays. `sk_producer()` creates and closes socket batches; `task_producer()` creates and joins thread batches; `measure()` reads `create_cnts`; reporting computes create throughput and error totals.

Control flow: validation only rejects consumers. Setup attaches the BPF hook matching the chosen owner type. Each producer loops over creation batches, records owner-creation syscall failures separately, then destroys owners so the next batch can run.

State and persistence: global `skel`, `threads`, `create_owner_errs`, `storage_type`, and `batch_sz` hold process state. BPF BSS fields track successful storage creations and BPF-side errors; `create_cnts` is atomically reset at each sample.

Dependencies and integration points: uses pthreads, sockets, libbpf skeleton APIs, `bench.h`, and kernel hooks exposed by the BPF object. The BPF program filters using `bench_pid`, so process identity is part of correctness.

Risks: large batch sizes can exhaust file descriptors, memory, or thread limits; task mode creates many real pthreads and can stress scheduler limits; producer arrays are never freed during the benchmark; storage-type string validation is strict.

Test signals: progress lines report `creates k/s`, final summary reports standard deviation and total creates, and any socket/pthread or BPF create errors are printed explicitly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_local_storage_create.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_local_storage_rcu_tasks_trace.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_local_storage_rcu_tasks_trace.c

Purpose: stresses task-local-storage destruction paths that use RCU Tasks Trace and measures grace-period latency and optional kthread CPU ticks while many sleeper processes exist.

Important APIs and functions: `--nr_procs` sets sleeper process count and `--kthread_pid` identifies `rcu_tasks_trace_kthread`. `local_storage_tasks_trace_setup()` forks sleepers with `PR_SET_PDEATHSIG`, loads `local_storage_rcu_tasks_trace_bench`, attaches `get_local`, `pregp_step`, and `postgp`. `kthread_pid_ticks()` parses `/proc/<pid>/stat` stime. `measure()` collects `gp_hits`, `gp_times`, and tick deltas. Reports use `grace_period_*_basic_stats()`.

Control flow: setup forks many children that sleep randomly and call `getpgid`; then the parent attaches BPF probes. The benchmark producer also triggers `getpgid` repeatedly. BPF-side probes measure RCU grace-period boundaries, and user-space sampling computes averages.

State and persistence: child processes persist for the benchmark lifetime and should die with the parent via PDEATHSIG. `ctx.prev_kthread_stime` maintains the previous tick sample. BSS counters are reset at each measurement.

Dependencies and integration points: depends on `local_storage_rcu_tasks_trace_bench.skel.h`, `bench.h`, `/proc`, `prctl`, process forking, and the presence of RCU Tasks Trace symbols/probes in the kernel.

Risks: very high `nr_procs` can exhaust PID/process resources; missing or wrong `kthread_pid` aborts; the parser for `/proc/<pid>/stat` is fragile to unexpected layout; a stray duplicated `break;` after argument parsing is harmless but untidy. If BPF sees post-GP before pre-GP, reporting exits because data is invalid.

Test signals: valid runs print average grace-period latency and ticks per grace period, unless quiet. Failure signals include fork/prctl errors, attach failures, and `unexpected` ordering in BPF BSS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_local_storage_rcu_tasks_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_lpm_trie_map.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_lpm_trie_map.c

Purpose: provides LPM trie map benchmarks for no-op, baseline, lookup, insert, update, delete, and free behavior over dense key ranges, including random-access mode for supported operations.

Important APIs and functions: argp options parse `--nr_entries`, `--prefix_len`, and `--random`. `validate_common()` checks consumers, required entries, and prefix capacity; operation-specific validators reject unsupported producer counts or random mode. `attach_prog()` loads `lpm_trie_bench`, configures BSS, allocates key/value arrays, and attaches the skeleton. `fill_map()` and `empty_map()` use batch map APIs. Producers use `bpf_prog_test_run_opts()` or repeatedly load/fill/destroy `lpm_trie_map` to measure free cost.

Control flow: setup selects a BPF operation code in BSS and initializes map state as empty or full. The regular producer repeatedly test-runs `run_bench`, handles BPF return codes, and reinitializes maps for insert/delete when requested. Free benchmark creates a fresh skeleton, fills the map, then destroys it in a loop.

State and persistence: keys and values are heap arrays for the benchmark lifetime. BPF BSS counters track hits and active measured duration; map contents are reset between partial measurement windows for mutating operations.

Dependencies and integration points: depends on generated `lpm_trie_bench` and `lpm_trie_map` skeletons, `progs/lpm_trie.h` operation/return-code constants, libbpf batch APIs, and the common bench reporting helpers.

Risks: `(1UL << args.prefixlen)` can be undefined for oversized prefix lengths on some word sizes; batch update/delete failures abort; mutating operations need careful duration accounting because reset time is excluded; dense key layout measures worst-case behavior, not arbitrary sparse production use.

Test signals: operation summaries report throughput and latency. BPF errors, unexpected return codes, or failed batch updates/deletes are immediate failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_lpm_trie_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_rename.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_rename.c

Purpose: benchmarks overhead of different BPF attachment types on the task rename path by repeatedly writing to `/proc/self/comm`.

Important APIs and functions: `validate()` enforces one producer and no consumers. `setup_ctx()` loads `test_overhead.skel.h` and opens `/proc/self/comm`. Attachment setup variants attach `prog1` through `prog5` for kprobe, kretprobe, raw tracepoint, fentry, and fexit. `producer()` writes a fixed string and increments a user-space hit counter; `measure()` swaps the counter.

Control flow: each benchmark entry shares the same producer, setup context, and report functions. The base benchmark attaches no BPF program; other setups attach one specific BPF program before the producer loop starts.

State and persistence: process-local `ctx.fd` persists for repeated writes, and `ctx.hits` is reset every measurement interval. BPF links are owned by libbpf skeleton/link lifetime.

Dependencies and integration points: integrates with `bench.h`, `test_overhead` BPF skeleton, `/proc/self/comm`, and libbpf attach APIs.

Risks: requires permission and kernel support for the selected attach kinds; `/proc/self/comm` writes can fail in unusual procfs or namespace configurations; base hit counter measures user writes rather than BPF hits.

Test signals: `run_bench_rename.sh` expects summary throughput per attach type. Attach failure or write failure aborts the benchmark.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_rename.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_ringbufs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_ringbufs.c

Purpose: compares BPF ring buffer and perf buffer throughput across libbpf consumers, custom mmap/epoll consumers, back-to-back notification mode, sampling, reserve/commit versus output, overwrite mode, and producer-only ringbuf stress.

Important APIs and functions: argp flags configure back-to-back, batch count, sampling, sample rate, overwrite, output API, and producer-only mode. `bufs_validate()` enforces compatible producer/consumer counts. `ringbuf_setup_skeleton()` and `perfbuf_setup_skeleton()` load generated skeletons with rodata settings. `ringbuf_libbpf_setup()`, `ringbuf_custom_setup()`, and `perfbuf_libbpf_setup()` prepare consumers and attach BPF programs. Custom processing uses mmaped ringbuf pages, memory barriers, and epoll; perf custom processing reads perf mmap pages directly.

Control flow: producers trigger BPF via `getpgid`; consumers poll ring/perf buffers and count samples. In back-to-back mode, the consumer triggers the next batch after processing data. Measurements collect user-observed hits and BPF drop counters, or producer BSS hits in producer-only mode.

State and persistence: static contexts hold skeletons, libbpf buffers, custom ring mappings, epoll fds, and counters. Ring/perf buffer contents persist in kernel maps until consumed or overwritten.

Dependencies and integration points: depends on `ringbuf_bench.skel.h`, `perfbuf_bench.skel.h`, libbpf ring/perf buffer APIs, Linux perf mmap ABI, epoll, `asm/barrier.h`, and common hits/drops reporting.

Risks: custom consumers duplicate internal ABI assumptions and can break if layouts change; `args.ringbuf_sz` is assumed power-of-two for masking but not validated here; overwrite mode only supports producer benchmark; sampling config rejects sample rates larger than batch count for perfbuf. Back-to-back mode only makes sense with one producer.

Test signals: progress/final reports hits and drops. Regressions appear as poll failures, mmap failures, increased drops, incompatible argument exits, or divergent libbpf versus custom consumer throughput.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_ringbufs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_sockmap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_sockmap.c

Purpose: benchmarks sockmap/sk_msg forwarding and pass-through modes by moving deterministic data across two loopback TCP socket pairs and measuring producer, BPF, and receiver throughput.

Important APIs and functions: mode macros classify RX stream-verdict and TX sk_msg variants. `create_sockets()` builds `c1/p1` and `c2/p2` TCP pairs from one listener. `setup_rx_sockmap()` attaches stream parser/verdict/pass programs and populates `sock_map_rx`; `setup_tx_sockmap()` attaches sk_msg verdict/pass and populates `sock_map_tx`. `producer()` writes a repeated data file with `sendfile`; `consumer()` reads/forwards and verifies byte pattern. Argp options select RX/TX mode, strparser packet size, delayed consumer, and bounded producer duration.

Control flow: validation requires two consumers, one producer, and CPU affinity. Setup loads the skeleton, creates sockets, attaches the selected BPF path, and populates sock maps. The producer sends from the endpoint required by the selected mode. Consumer 0 reads final data from `c2`; consumer 1 is only relevant for RX normal proxy mode.

State and persistence: `ctx` owns skeleton, sockets, counters, mode, data sizes, and timing knobs. Counters are atomically swapped each measurement. Temporary file data persists for the producer lifetime.

Dependencies and integration points: integrates with `bench_sockmap_prog.skel.h`, libbpf `bpf_prog_attach`, BPF sockmap map updates, TCP loopback sockets, `sendfile`, and `bench.h`.

Risks: mode setup is subtle because ingress/egress endpoints differ; nonblocking sendfile can spin on `EAGAIN/ENOMEM/ENOBUFS`; data verification exits on the first mismatch; `set_non_block()` names its boolean inversely to behavior, which can confuse maintainers; resource cleanup only runs on setup error.

Test signals: progress reports Send, BPF, and Receive MB/s plus call rates. Correctness signals include byte-pattern verification and BPF `process_byte` matching transported data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_sockmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_strncmp.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_strncmp.c

Purpose: benchmarks BPF string comparison implemented manually versus through the strncmp helper.

Important APIs and functions: argp option `--cmp-str-len` sets comparison length. `strncmp_setup()` opens `strncmp_bench`, fills rodata target with random digits, copies a slightly smaller string into BSS, sets compare length, and loads the skeleton. `strncmp_no_helper_setup()` and `strncmp_helper_setup()` attach alternate BPF programs. Producer triggers the probe with `getpgid`; `measure()` swaps BSS `hits`.

Control flow: validation rejects consumers. Setup prepares deterministic mismatch-at-last-byte test data for the selected length. The producer loop causes repeated BPF comparisons, and common hit reports compute throughput.

State and persistence: random target string and BSS comparison string live in the skeleton. BSS hits reset per sample. No persistent kernel state beyond BPF link/map lifetime.

Dependencies and integration points: depends on `strncmp_bench.skel.h`, libbpf skeleton APIs, `bench.h`, and the kernel helper under test.

Risks: option parsing references `ctx.skel->bss->str` before `ctx.skel` is opened, which relies on generated skeleton field layout in `sizeof` context and can be surprising; random data makes exact input bytes non-reproducible though only length/mismatch pattern matters; invalid long lengths are rejected.

Test signals: `run_bench_strncmp.sh` sweeps lengths for `strncmp-no-helper` and `strncmp-helper`, reporting hit throughput.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_strncmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_trigger.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_trigger.c

Purpose: central benchmark collection for BPF trigger overhead across syscall counting, in-kernel batch drivers, kprobe/kretprobe/fentry/fexit/fmodret/tracepoint/raw tracepoint, kprobe-multi all-symbol attachment, uprobes/uretprobes, uprobe-multi, and x86 USDT probes.

Important APIs and functions: `bench_trigger_batch_argp` parses `--trig-batch-iters`. `setup_ctx()` opens `trigger_bench`, enables the driver program, and writes rodata. `trigger_producer()` triggers syscalls; `trigger_producer_batch()` repeatedly calls a BPF driver with `bpf_prog_test_run_opts`. Setup functions selectively autoload and attach programs. `attach_ksyms_all()` gets filtered kallsyms and attaches multi-kprobes. `usetup()` calculates target offsets and attaches uprobe or uprobe-multi. User target functions are carefully marked weak/noinline/nocf for stable probe points.

Control flow: setup selects the BPF path and optional driver fd. Producers either call `getpgid`, run a BPF driver, or call a user-space target function. `trigger_measure()` reads either user-mode sharded counters or BPF BSS hit counters. Macro blocks declare many `struct bench` entries.

State and persistence: `ctx` stores skeleton, selected counter source, and optional driver program fd. User counters are sharded by hashed tid into 256 counters to reduce contention. BPF links persist for the benchmark lifetime.

Dependencies and integration points: depends on `trigger_bench.skel.h`, `trace_helpers.h` for kallsyms/uprobe offsets, libbpf attach APIs, arch-specific x86 probe targets, and `bench.h`.

Risks: all-symbol kprobe-multi is kernel/config sensitive and intentionally skips problematic recursive functions; uprobe instruction choice affects measured overhead; USDT only builds under x86 section; missing feature support causes load/attach failures. Batch iteration values are capped at 1000.

Test signals: `run_bench_trigger.sh` and `run_bench_uprobes.sh` extract per-trigger summary throughput. Attach/load failures, verifier errors, or zero BPF hits indicate regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_trigger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_bloom_filter_map.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_bloom_filter_map.sh

Purpose: shell benchmark matrix for bloom filter map lookup/update/false-positive performance and hashmap-with-bloom versus hashmap-without-bloom throughput.

Important APIs and functions: sources `run_common.sh`, uses `header`, `subtitle`, `summarize`, `summarize_percentage`, and `summarize_total`. It invokes `$RUN_BENCH` with variable thread counts, hash function counts, entry counts, and value sizes.

Control flow: nested loops sweep value sizes, producer counts, hash function counts, and entry counts. For each point it runs bloom lookup, update, false-positive, and later hashmap comparison benchmarks.

State and persistence: no persistent state beyond shell variables and benchmark output. Kernel maps are created and destroyed by each `./bench` invocation.

Dependencies and integration points: assumes execution from selftests/bpf root with `./benchs/run_common.sh` available and `sudo ./bench -w3 -d10 -a` runnable.

Risks: very large sweep can take a long time; output parsing depends on stable summary text; `set -euo pipefail` makes any benchmark failure abort the whole matrix.

Test signals: formatted sections show per-entry throughput and false-positive percentages; missing parsed values indicate output format drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_bloom_filter_map.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_bpf_hashmap_full_update.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_bpf_hashmap_full_update.sh

Purpose: runs the `bpf-hashmap-full-update` benchmark using all but one detected CPU as producer threads.

Important APIs and functions: sources `run_common.sh`, computes `nr_threads` from `/proc/cpuinfo`, invokes `$RUN_BENCH -p $nr_threads bpf-hashmap-full-update`, and prints the raw summary.

Control flow: one CPU-count calculation, one benchmark invocation, one print.

State and persistence: shell-only; benchmark state is contained in the child `bench` process.

Dependencies and integration points: relies on Linux `/proc/cpuinfo`, GNU `expr`, `grep`, `wc`, and common runner defaults from `run_common.sh`.

Risks: CPU count parsing is x86/procfs-string dependent; on single-CPU systems `nr_threads` becomes zero; output is not parsed/normalized like other scripts.

Test signals: non-empty benchmark summary from `bpf-hashmap-full-update`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_bpf_hashmap_full_update.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_bpf_loop.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_bpf_loop.sh

Purpose: sweeps BPF loop helper throughput over multiple producer counts and loop iteration counts.

Important APIs and functions: sources `run_common.sh`, uses `subtitle` and `summarize_ops`, invokes `$RUN_BENCH -p $t --nr_loops $i bpf-loop`.

Control flow: nested loops over thread counts and `nr_loops` values, printing a subtitle and parsed throughput/latency for each run.

State and persistence: shell-local only; each benchmark child owns its BPF state.

Dependencies and integration points: depends on common summary regexes in `run_common.sh` matching `throughput` and `latency` text.

Risks: large iteration values can make individual runs long; parser fragility if `bpf-loop` report format changes; any run failure stops the script.

Test signals: each matrix point emits throughput and latency, enabling trend comparison by loop count and producer count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_bpf_loop.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_htab_mem.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_htab_mem.sh

Purpose: runs hash-table memory-use benchmarks for selected use cases with preallocated and normal allocation modes.

Important APIs and functions: `htab_mem()` parses per-producer operations, average memory, and peak memory from a summary; `summarize_htab_mem()` formats one row; `htab_mem_bench()` runs `htab-mem --use-case` for `overwrite`, `batch_add_batch_del`, and `add_del_on_diff_cpu`.

Control flow: prints `preallocated`, runs all use cases with `--preallocated`, prints `normal bpf ma`, and reruns without the flag.

State and persistence: shell variables only. Memory behavior is measured by the child benchmark.

Dependencies and integration points: sources `run_common.sh`; uses sed regexes tied to `htab-mem` final summary text.

Risks: typo-like header `normal bpf ma` may be intentional but unclear; regexes require exact units and `±` text; fixed `-p8` may be inappropriate on small systems.

Test signals: rows report per-prod-op, average memory, and peak memory for each use case/allocation mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_htab_mem.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_local_storage.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_local_storage.sh

Purpose: drives local-storage cache benchmarks and hashmap control across key/map-count sweeps.

Important APIs and functions: sources `run_common.sh`; calls `summarize_local_storage` around `./bench --nr_maps ...` local-storage benchmark names.

Control flow: first runs hashmap control with key counts from 10 to full `HASHMAP_SZ`; then runs local-storage sequential and interleaved get tests for map counts from 1 to 1000.

State and persistence: shell-only; each `./bench` invocation creates its own maps and BPF links.

Dependencies and integration points: assumes current directory contains `./bench`; unlike many scripts it bypasses `$RUN_BENCH`, so warmup/duration/affinity defaults differ.

Risks: full hashmap prepopulation with 4,194,304 keys is expensive; direct `./bench` calls may need root/capabilities depending on environment; parser depends on local-storage report text.

Test signals: output shows hits throughput, hits latency, and important-hit throughput for each configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_local_storage.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_local_storage_rcu_tasks_trace.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_local_storage_rcu_tasks_trace.sh

Purpose: convenience runner for the local-storage RCU Tasks Trace benchmark with a large process count and long duration.

Important APIs and functions: finds `rcu_tasks_trace_kthread` with `pgrep`, then runs `./bench --nr_procs 15000 --kthread_pid $kthread_pid -d 600 --quiet local-storage-tasks-trace`.

Control flow: one discovery step, validation of non-empty PID, then one benchmark invocation.

State and persistence: no shell persistence; the benchmark itself forks 15,000 child processes during its run.

Dependencies and integration points: depends on process name visibility, a kernel with `rcu_tasks_trace_kthread`, and ability to run the benchmark with enough privileges/resources.

Risks: `[ -z $kthread_pid ]` is unquoted and can misbehave if multiple PIDs or empty expansion occur; 15,000 processes and 600-second runtime are heavy; direct `./bench` bypasses `run_common.sh`.

Test signals: successful quiet run yields final benchmark summary; missing kthread prints an explicit error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_local_storage_rcu_tasks_trace.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_rename.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_rename.sh

Purpose: runs rename-trigger overhead benchmarks for base, kprobe, kretprobe, raw tracepoint, fentry, and fexit modes.

Important APIs and functions: loops over mode suffixes, invokes `sudo ./bench -w2 -d5 -a rename-$i`, extracts the final throughput field with `tail` and `cut`, and prints aligned rows.

Control flow: sequentially executes six benchmark variants.

State and persistence: shell-only; BPF links are created per child benchmark.

Dependencies and integration points: assumes sudo access, built `./bench`, stable summary format, and supported attach types.

Risks: output extraction is brittle; failures under `set -euo pipefail` abort the script; no shared `run_common.sh` means duplicated parsing logic.

Test signals: aligned rows allow quick comparison of base versus BPF attachment overhead.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_rename.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_ringbufs.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_ringbufs.sh

Purpose: benchmark matrix for ringbuf/perfbuf libbpf and custom consumers under multiple producer/consumer patterns.

Important APIs and functions: sources `run_common.sh`, sets `RUN_RB_BENCH="$RUN_BENCH -c1"`, and uses `summarize` for `rb-libbpf`, `rb-custom`, `pb-libbpf`, and `pb-custom` across sampling, back-to-back, sample-rate sweeps, output API, CPU affinity, multi-producer, and overwrite producer-only cases.

Control flow: prints themed headers, loops benchmark names and counts, and runs a child benchmark per point.

State and persistence: shell-only. Each run creates its own BPF maps/buffers.

Dependencies and integration points: depends on common runner defaults, ringbuf benchmark argp options, CPU affinity flags, and summary text containing hits/drops.

Risks: high producer counts up to 52 may exceed available CPUs or distort comparisons; long matrix runtime; parser fragility; consumer count is fixed to one except overwrite producer-only section.

Test signals: hit/drop summaries across modes reveal notification overhead, contention, and overwrite behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_ringbufs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_strncmp.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_strncmp.sh

Purpose: compares manual versus helper-based BPF string comparison across selected string lengths.

Important APIs and functions: sources `run_common.sh`; nested loops over lengths `1 8 64 512 2048 4095` and benchmark variants `no-helper`/`helper`; calls `summarize`.

Control flow: one benchmark invocation per length/variant pair.

State and persistence: shell-local only; BPF state is per child run.

Dependencies and integration points: relies on `bench_strncmp.c` argp and common hits/drops parser.

Risks: maximum length is close to the target buffer size and depends on BPF skeleton layout; no header/subtitle output may make long logs less grouped; output parsing can drift.

Test signals: rows show throughput for helper and non-helper implementations at each compare length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_strncmp.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_trigger.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_trigger.sh

Purpose: runs default or user-specified trigger benchmark variants and prints compact throughput rows.

Important APIs and functions: defines default tests for usermode/kernel/syscall counting and common tracing attach types; allows CLI override; reads producer count from `PROD_CNT`; invokes `sudo ./bench -w2 -d5 -a -p$p trig-$t`.

Control flow: selects test list, selects producer count, sequentially runs each trigger variant, and extracts the final throughput with `tail`/`cut`.

State and persistence: no persistent state beyond environment variable use.

Dependencies and integration points: depends on `bench_trigger.c` names, sudo, built `./bench`, and stable final summary formatting.

Risks: all-symbol kprobe tests can be expensive or unsupported; parser is brittle; default includes feature-sensitive attach kinds that may fail on some kernels.

Test signals: per-trigger row throughput enables quick overhead comparison across attach technologies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_trigger.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_uprobes.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_uprobes.sh

Purpose: runs user-space trigger overhead benchmarks for uprobes, uretprobes, and USDT probes.

Important APIs and functions: loops over `usermode-count`, `syscall-count`, `{uprobe,uretprobe}-{nop,push,ret,nop5}`, `usdt-nop`, and `usdt-nop5`; invokes `sudo ./bench -w2 -d5 -a trig-$i`; extracts final summary.

Control flow: sequential fixed matrix, one line per benchmark variant.

State and persistence: shell-only.

Dependencies and integration points: depends on x86-only variants being built when requested, `bench_trigger.c` benchmark names, sudo, and stable output format.

Risks: `nop5` and USDT variants are guarded in C for x86 but the shell script always lists them; non-x86 environments can fail; output parsing is duplicated and fragile.

Test signals: compact rows compare function-body instruction choice, retprobe overhead, and USDT overhead.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_uprobes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_common.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_common.sh

Purpose: shared shell library for benchmark runner scripts, defining a default `RUN_BENCH` command and parsers/formatters for common summary outputs.

Important APIs and functions: `RUN_BENCH="sudo ./bench -w3 -d10 -a"`; `header()` and `subtitle()` format sections; `hits()`, `drops()`, `percentage()`, `ops()`, `local_storage()`, and `total()` parse summary text with sed; `summarize*()` functions print aligned rows.

Control flow: no execution beyond definitions. Scripts source it and call functions with captured benchmark output.

State and persistence: sets shell variable `RUN_BENCH`; no file state.

Dependencies and integration points: assumes GNU-ish `sed`, `seq`, printf support for formatting, `sudo`, and stable bench report strings including units and `±`.

Risks: regex parsing is brittle and silently returns unparsed input if formats change; non-ASCII `±` can be locale-sensitive; default sudo command may not fit unprivileged CI.

Test signals: any script using these helpers should show compact parsed rows; malformed rows are a signal that benchmark output changed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_common.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_arena_alloc.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_arena_alloc.h

Purpose: provides a simple page-fragment allocator for BPF arena selftests, with no-op user-space stubs.

Important APIs and functions: defines `bpf_alloc(size)` and `bpf_free(addr)` under `__BPF__`; uses per-CPU `page_frag_cur_page` and `page_frag_cur_offset`; calls `bpf_arena_alloc_pages()` and `bpf_arena_free_pages()` from `bpf_arena_common.h`.

Control flow: allocation rounds size to 8 bytes, rejects near-page-size requests, refills a per-CPU arena page when needed, stores an object count in the last 8 bytes, and returns space from the end downward. Free masks the object pointer to page base and decrements the page object count, freeing the page when it reaches zero.

State and persistence: allocator state lives in arena-address-space global arrays and per-page object counters. User-space builds return NULL/do nothing.

Dependencies and integration points: depends on `struct cpumask`, `PAGE_SIZE`, arena map symbol `arena`, address-space casting, and BPF kfuncs declared by `bpf_arena_common.h`.

Risks: no individual allocation metadata beyond page object count, so invalid/double frees corrupt state; no cross-CPU ownership checks; allocations larger than `PAGE_SIZE - 8` fail; object count is not atomic.

Test signals: arena data-structure tests can validate successful allocation/free, page reuse, and failure on oversized allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_arena_alloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_arena_common.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_arena_common.h

Purpose: central compatibility layer for BPF arena address-space annotations, casts, page kfunc declarations, and user-space stubs.

Important APIs and types: defines `__arena`, `__arena_global`, `__arg_arena`, `cast_kern`, `cast_user`, `arena_container_of`, `arena_base(map)`, and weak kfunc declarations for `bpf_arena_alloc_pages`, `bpf_arena_reserve_pages`, and `bpf_arena_free_pages`.

Control flow: compile-time branches distinguish BPF and user-space builds. BPF builds use LLVM address-space attributes when available, otherwise emit `bpf_addr_space_cast`; user-space builds erase annotations and provide inert arena allocation stubs.

State and persistence: declares weak `arena` for user-space compatibility; real arena state is in BPF maps/kfunc-managed pages.

Dependencies and integration points: depends on `bpf_experimental.h` for casts in asm fallback, BPF feature macro `__BPF_FEATURE_ADDR_SPACE_CAST`, and kernel arena support.

Risks: behavior changes with compiler feature availability; older kernels may lack page-size assumptions or kfuncs; incorrect casts can lead to verifier rejection.

Test signals: successful compilation for both BPF and user-space consumers, and arena selftests that exercise address-space casts and page kfuncs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_arena_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_arena_htab.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_arena_htab.h

Purpose: implements a small arena-backed hash table for BPF arena tests using arena linked lists and the page-fragment allocator.

Important APIs and types: `struct htab_bucket`, `struct htab`, `struct hashtab_elem`; `htab_lookup_elem()`, `htab_update_elem()`, `htab_init()`, `select_bucket()`, and `lookup_elem_raw()`.

Control flow: `htab_init()` allocates two pages for buckets and sets bucket count. Lookup selects a bucket by `hash & (n_buckets - 1)` and walks the arena list. Update allocates a new element, inserts it at the bucket head, and removes/frees the old matching element if present.

State and persistence: table buckets and elements live in arena memory. Updates replace elements rather than mutating in place. No persistent state outside the arena map.

Dependencies and integration points: depends on `bpf_arena_alloc.h`, `bpf_arena_list.h`, errno, and the global arena map symbol.

Risks: hash is identity and bucket count must be power-of-two for masking; no locking or atomicity; allocation failure returns `-ENOMEM`; duplicate handling depends on successful new allocation before old removal.

Test signals: arena hash-table tests should verify insert, replace, lookup miss/hit, and behavior under allocator failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_arena_htab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_arena_list.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_arena_list.h

Purpose: provides intrusive singly-headed, doubly-linked arena list primitives for BPF arena data structures.

Important APIs and types: `struct arena_list_node`, `struct arena_list_head`, `arena_list_node_t`, `arena_list_head_t`, `list_entry`, `list_entry_safe`, `list_for_each_entry`, `list_add_head()`, `list_del()`, and `__list_del()`.

Control flow: `list_add_head()` casts between user/kernel arena address spaces, updates node `next`, previous first node `pprev`, head `first`, and new node `pprev` using `WRITE_ONCE`. `list_del()` unlinks and poisons pointers. The iterator caches next before allowing deletion and uses `can_loop` to satisfy bounded-loop/verifier requirements.

State and persistence: list topology lives entirely in arena pointers. User-space fallback stubs make compilation possible but do not implement real iterator behavior.

Dependencies and integration points: depends on `bpf_arena_common.h`, `cond_break/can_loop` from experimental helpers for BPF builds, and arena address-space casts.

Risks: no concurrency protection; corrupted `pprev` can corrupt arbitrary arena memory; poison values are fixed low addresses; iteration semantics differ in user-space stub mode.

Test signals: list tests should cover add, delete, delete-while-iterating, empty lists, and verifier acceptance of bounded traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_arena_list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_arena_strsearch.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_arena_strsearch.h

Purpose: supplies arena-string helpers, notably `bpf_arena_strlen()` and non-recursive shell-style `glob_match()` for BPF arena tests.

Important APIs and functions: `bpf_arena_strlen()` scans an arena string with `cond_break`; `glob_match(pat, str)` supports `?`, `*`, character classes, `!` class inversion, ranges, and backslash escaping over arena strings.

Control flow: `glob_match()` consumes pattern and string tokens in one loop. A single saved `*` backtrack point handles mismatch retries, making runtime at most quadratic without recursion. Character classes iterate ranges until `]`, falling back to literal handling on malformed input.

State and persistence: function-local pointers only; no persistent state.

Dependencies and integration points: depends on `bpf_arena_common.h` and `cond_break` for verifier-friendly loops.

Risks: intended semantics match `fnmatch(..., 0)` but do not special-case `/` or leading `.`; malformed brackets are literal; worst-case patterns can be quadratic; no preprocessing/cache for repeated patterns.

Test signals: string tests should include wildcard, class, inverted class, escaped literal, malformed class, trailing `*`, and mismatch backtracking cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_arena_strsearch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_atomic.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_atomic.h

Purpose: provides kernel-like atomic and memory-ordering helper macros for BPF programs used by selftests.

Important APIs and macros: `READ_ONCE`, `WRITE_ONCE`, `cmpxchg`, `try_cmpxchg*`, `smp_mb/rmb/wmb`, `smp_load_acquire`, `smp_store_release`, `smp_cond_load_*_label`, `atomic_read`, `atomic_cond_read_*`, and `atomic_try_cmpxchg_*`. `__unqual_typeof()` strips scalar qualifiers while preserving pointer behavior around an LLVM address-space issue.

Control flow: macros expand into volatile accesses, compiler barriers, and `__sync_*` builtins. X86 uses weaker barrier paths for rmb/wmb/load/store where appropriate; other architectures fall back to full memory barriers.

State and persistence: no runtime state except accessed atomic variables.

Dependencies and integration points: includes `vmlinux.h`, BPF helpers, `bpf_experimental.h`, and weak kconfig `CONFIG_X86_64`.

Risks: macro-heavy code is type-sensitive; behavior depends on target architecture config; full barriers may be more expensive on non-x86; misuse on non-atomic struct layout can fail verification or produce races.

Test signals: atomic selftests should compile and validate compare-exchange success/failure, acquire/release ordering, and conditional load loop behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_experimental.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_experimental.h

Purpose: collects experimental BPF kfunc declarations and verifier-oriented helper macros for selftests using new kernel features.

Important APIs and macros: declares kfuncs for object allocation, task/VMA/css/kmem/dmabuf iterators, exceptions (`bpf_throw`), file/path/xattr helpers, workqueue helpers, preempt guards, arena address-space casts, and context checks. Macros include `bpf_obj_new`, `bpf_percpu_obj_new`, `__exception_cb`, `bpf_assert*`, `bpf_cmp_likely/unlikely`, `can_loop`, `cond_break`, `bpf_nop_mov`, and `bpf_guard_preempt`.

Control flow: most content is declarations and inline/asm macros. Assertion macros emit conditional BPF branches that call `bpf_throw`; loop macros emit `may_goto` or raw instruction encodings depending on compiler feature and endianness. Interrupt-context helpers read architecture-specific preempt count state with CO-RE fallbacks.

State and persistence: no own state, but exposes APIs that acquire references, allocate objects, or disable preemption; users must release resources and allow cleanup destructors to run.

Dependencies and integration points: depends on `vmlinux.h`, libbpf helper/tracing/core-read headers, BPF target architecture macros, weak kconfig variables, and kernel kfunc availability.

Risks: explicitly experimental and feature-sensitive; missing kfuncs or changed BTF names cause verifier/load failures; inline assembly is architecture/compiler sensitive; exception assertions cannot be used with lingering refs/locks.

Test signals: compile/load success across feature matrices, verifier acceptance of assertions/loops/casts, and runtime tests for context detection and kfunc behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_experimental.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_kfuncs.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_kfuncs.h

Purpose: declares BPF kfunc prototypes used by selftests for dynptrs, sockaddr mutation, TCP reqsk assignment, casting, xattrs, fsverity, keys, and signature verification.

Important APIs and functions: dynptr constructors/slicers/adjusters, `bpf_sock_addr_set_sun_path`, `bpf_sk_assign_tcp_reqsk`, `bpf_cast_to_kern_ctx`, `bpf_rdonly_cast`, `bpf_get_file_xattr`, `bpf_get_fsverity_digest`, key lookup/put, PKCS#7 verification, and dentry xattr set/get/remove.

Control flow: header only; BPF verifier resolves weak/non-weak ksym references at load time.

State and persistence: kfuncs may return referenced objects or mutate kernel objects; callers own reference release obligations such as `bpf_key_put`.

Dependencies and integration points: assumes `vmlinux.h`/BPF context types are visible to includers and kernel exports matching these ksym names exist.

Risks: kernel-version and config sensitivity; incorrect dynptr buffer sizes or reference management can cause verifier errors; non-weak declarations require feature presence.

Test signals: selftests using this header validate kfunc availability, verifier type checking, and expected runtime return codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_kfuncs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_legacy.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_legacy.h

Purpose: exposes legacy BPF absolute/indirect packet load builtins under common names for GCC and Clang BPF program builds.

Important APIs and macros: `load_byte`, `load_half`, and `load_word` map to GCC `__builtin_bpf_load_*` or Clang `llvm.bpf.load.*` asm symbols.

Control flow: compile-time compiler branch only; no runtime logic in the header.

State and persistence: no state.

Dependencies and integration points: used by legacy socket-filter style BPF tests needing `BPF_LD_ABS`/`BPF_LD_IND` instruction emission.

Risks: these builtins are compiler-specific and not general memory loads; the skb argument is ignored under GCC mapping; misuse outside supported program contexts can fail verification.

Test signals: generated BPF bytecode should contain expected ABS/IND load instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_legacy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_rand.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_rand.h

Purpose: user-space helper for generating semi-random 64-bit values with edge-case bit patterns for BPF tests.

Important APIs and functions: `bpf_rand_mask()`, generated `bpf_rand_u8/u16/.../u64(shift)`, `bpf_semi_rand_init()`, and `bpf_semi_rand_get()`.

Control flow: initialization seeds `rand()` with current time. `bpf_semi_rand_get()` picks among 39 cases combining fixed masks, random low/high fields, shifts, all-zero/all-one, and sign-bit-heavy values.

State and persistence: uses libc global PRNG state seeded by `srand`.

Dependencies and integration points: includes stdint/stdlib/time; used by tests wanting varied immediate/register values.

Risks: not deterministic unless caller controls seed separately; uses weak libc `rand()` quality; some shift arguments are random modulo 64 and should remain within range.

Test signals: fuzz-like tests should see a mix of boundary and random values; reproducibility may require overriding seed behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_rand.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_sockopt_helpers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_sockopt_helpers.h

Purpose: small BPF helper routine to validate that a context supports `bpf_getsockopt` and `bpf_setsockopt`.

Important APIs and functions: `get_set_sk_priority(ctx)` reads `SOL_SOCKET/SO_PRIORITY` into `prio` and writes it back.

Control flow: returns 0 on either helper failure and 1 if both get and set succeed.

State and persistence: reads and writes socket priority with the same value, so intended to preserve observable socket state.

Dependencies and integration points: includes `<sys/socket.h>` and `bpf_helpers.h`; used by sockopt/cgroup program tests.

Risks: context must permit both helpers; socket option semantics can vary by hook; preserving value still exercises a write path that may be rejected.

Test signals: callers can assert return 1 in allowed contexts and 0 or verifier failure in disallowed contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_sockopt_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_util.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_util.h

Purpose: common user-space utility header for BPF selftests.

Important APIs and macros: `bpf_num_possible_cpus()` wraps `libbpf_num_possible_cpus()` with fatal error handling; `sized_strscpy()` and variadic `strscpy` macro provide bounded string copy; per-CPU value helpers `BPF_DECLARE_PERCPU` and `bpf_percpu`; `ARRAY_SIZE`, `sizeof_field`, `offsetofend`, `sys_gettid()`, and `ENOTSUPP` fallback.

Control flow: utility inline functions perform immediate checks/copies. `#pragma GCC poison gettid` forces tests to use the syscall fallback macro.

State and persistence: no persistent state.

Dependencies and integration points: includes libbpf, Linux args macro helpers, errno/syscall headers, and is included by many user-space test files.

Risks: `strscpy` macro depends on argument-count helpers; `bpf_num_possible_cpus()` exits the process on error; poisoning `gettid` can surprise includers.

Test signals: users should compile with the helper macros and correctly size per-CPU value arrays for map APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpftool_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpftool_helpers.c

Purpose: helper for running bpftool commands from selftests with automatic bpftool path discovery.

Important APIs and functions: `detect_bpftool_path()` checks `$BPFTOOL`, `./tools/sbin/bpftool`, and `../tools/sbin/bpftool`; `run_command()` caches the detected path, builds a command string, runs it with `popen`, optionally captures output, and closes it. Public wrappers are `run_bpftool_command()` and `get_bpftool_command_output()`.

Control flow: first command triggers path detection and cache fill. Commands without output redirect stdout/stderr to `/dev/null`; commands with output read up to caller-provided buffer length.

State and persistence: static `bpftool_path` persists for the process lifetime.

Dependencies and integration points: uses `bpf_util.h` `strscpy`, shell `popen`, environment variable override, and bpftool built in the kernel tools tree.

Risks: command construction is string-based and can be injection-prone if args are untrusted; `snprintf` return is not bounds-checked beyond local buffer; captured output may not be NUL-terminated by `fread`.

Test signals: tests should fail early with an explicit path error if bpftool is unavailable; command return status propagates from `pclose`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpftool_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpftool_helpers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpftool_helpers.h

Purpose: declares the bpftool helper interface for selftests.

Important APIs and macros: `MAX_BPFTOOL_CMD_LEN`, `run_bpftool_command(char *args)`, and `get_bpftool_command_output(char *args, char *output_buf, size_t output_max_len)`.

Control flow: header only.

State and persistence: no state in the header; implementation caches bpftool path.

Dependencies and integration points: includes stdlib/stdio/stdbool and pairs with `bpftool_helpers.c`.

Risks: exposes mutable `char *` argument type even though implementations do not intend to mutate; max command length constant is smaller than implementation's full command buffer and may only guide callers.

Test signals: compile-time inclusion and successful command execution through the C file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpftool_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/btf_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/btf_helpers.c

Purpose: BTF formatting and validation helpers for selftests that compare raw BTF or C dumps.

Important APIs and functions: `fprintf_btf_type_raw()` prints one BTF type by id; `btf_type_raw_dump()` returns a static-buffer raw dump; `btf_validate_raw()` compares all types against expected strings using test assertions; `btf_type_c_dump()` uses `btf_dump` to render C-like declarations. Static helpers map kind, int encoding, var linkage, func linkage, and string offsets.

Control flow: raw dump fetches the type, prints common header, then switches by BTF kind to emit kind-specific fields and children. C dump creates a `btf_dump`, iterates type ids, and writes into a static fmemopen buffer.

State and persistence: static 16 KiB buffers are overwritten on each dump call. No heap state persists beyond a call.

Dependencies and integration points: depends on libbpf BTF APIs, `test_progs.h` assertion macros, `fmemopen`, and BTF kind constants up to ENUM64.

Risks: static buffers are not thread-safe and can truncate large dumps; expected strings are tightly coupled to formatting; new BTF kinds need mapping updates.

Test signals: validation failures identify mismatched raw BTF strings; C dump errors print diagnostic messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/btf_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/btf_helpers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/btf_helpers.h

Purpose: public declarations and convenience macro for BTF helper functions.

Important APIs and macros: declares `fprintf_btf_type_raw`, `btf_type_raw_dump`, `btf_validate_raw`, `btf_type_c_dump`, and `VALIDATE_RAW_BTF(btf, raw_types...)`.

Control flow: header only; `VALIDATE_RAW_BTF` constructs an inline expected string array and count.

State and persistence: no header state.

Dependencies and integration points: includes stdio and libbpf BTF headers; pairs with `btf_helpers.c`.

Risks: variadic macro expects string literals/compatible pointers and counts by `sizeof(void *)`, matching pointer arrays.

Test signals: tests use `VALIDATE_RAW_BTF` to compare a whole BTF object in one call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/btf_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/cap_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/cap_helpers.c

Purpose: toggles effective Linux capabilities in selftests without requiring libcap development headers.

Important APIs and functions: declares libc `capget`/`capset` manually; `cap_enable_effective(caps, old_caps)` ORs requested bits into effective sets; `cap_disable_effective(caps, old_caps)` clears requested bits. Both can return previous effective mask.

Control flow: read current capability sets, optionally save old mask, fast-return if requested state already holds, modify two 32-bit effective words, and call `capset`.

State and persistence: modifies process effective capability state. `old_caps` lets callers restore externally but no automatic guard is provided.

Dependencies and integration points: uses Linux capability UAPI structs from `cap_helpers.h` and errno negation for error returns.

Risks: only effective set changes, not permitted/inheritable; callers must restore caps carefully; capability operations may fail under user namespaces or insufficient privileges.

Test signals: tests can assert zero return and use saved masks to verify/restore effective capability bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/cap_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/cap_helpers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/cap_helpers.h

Purpose: declares capability toggling helpers and compatibility constants for BPF-related capabilities.

Important APIs and macros: defines `CAP_PERFMON` and `CAP_BPF` if missing; declares `cap_enable_effective()` and `cap_disable_effective()`.

Control flow: header only.

State and persistence: no header state; implementation changes process capabilities.

Dependencies and integration points: includes Linux types/capability headers and errno.

Risks: fallback numeric constants must match kernel UAPI; old systems may lack the capabilities even if constants compile.

Test signals: compile compatibility on older headers and runtime capability toggling through the C implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/cap_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/cgroup_getset_retval_hooks.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/cgroup_getset_retval_hooks.h

Purpose: macro data table listing cgroup/BPF hook names, section strings, context types, and representative invalid return values for get/set retval tests.

Important APIs and types: repeated `BPF_RETVAL_HOOK(name, section, ctx_type, invalid_ret)` entries for skb ingress/egress, sock create/release, sockops, dev, bind/connect/sendmsg/recvmsg/getpeername/getsockname, sysctl, getsockopt, and setsockopt.

Control flow: header has no include guard by design for macro-list inclusion. The including file defines `BPF_RETVAL_HOOK` to generate code/data.

State and persistence: no state.

Dependencies and integration points: context type names must exist in BPF UAPI/vmlinux includes; section strings match libbpf cgroup program section names.

Risks: macro-list headers can be misincluded without defining the macro; hook return semantics can change, making invalid return values stale.

Test signals: generated tests should cover each listed hook and validate get/set retval behavior against invalid return handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/cgroup_getset_retval_hooks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/cgroup_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/cgroup_helpers.c

Purpose: creates and manages isolated cgroup v2 and cgroup v1 net_cls environments for BPF selftests.

Important APIs and functions: cgroup v2 helpers include `setup_cgroup_environment`, `cleanup_cgroup_environment`, `enable_controllers`, `write_cgroup_file`, `join_cgroup`, `join_root_cgroup`, `join_parent_cgroup`, `set_cgroup_xattr`, `create_and_get_cgroup`, `remove_cgroup`, `get_root_cgroup`, `get_cgroup_id`, and `cgroup_setup_and_join`. cgroup v1 helpers include `setup_classid_environment`, `cleanup_classid_environment`, `set_classid`, `join_classid`, `get_classid_cgroup_id`, `get_cgroup1_hierarchy_id`, and `open_classid`.

Control flow: v2 setup creates a new mount namespace, makes `/` private, mounts cgroup2 at `/mnt`, removes stale workdirs, creates a pid-scoped workdir, and enables controllers. Cleanup moves to root and recursively removes cgroups with `nftw`. Classid setup mounts tmpfs and net_cls under `/sys/fs/cgroup`, creates pid-scoped workdir, and writes classid.

State and persistence: thread-local `cgroup_workdir_mounted` tracks whether cleanup should unmount. Filesystem mount/cgroup state persists until cleanup and is pid-scoped under workdir names.

Dependencies and integration points: uses mount namespaces, cgroupfs, net_cls cgroup v1, `name_to_handle_at` for cgroup id, xattrs, and logging macro from `cgroup_helpers.h`.

Risks: requires privileges for unshare/mount; hard-coded `/mnt` and `/sys/fs/cgroup` can conflict; cleanup can fail if processes remain in cgroups; `get_cgroup1_hierarchy_id` inner loop appears to compare the wrong token variable in the multi-controller branch, risking missed matches.

Test signals: successful setup returns fds/ids and allows BPF cgroup attachment tests to run; cleanup errors are logged with file/line/errno.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/cgroup_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/cgroup_helpers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/cgroup_helpers.h

Purpose: public cgroup test helper declarations plus a common errno logging macro.

Important APIs and macros: `log_err`, `clean_errno`, v2 helper declarations for controller/file/cgroup lifecycle, joining, ids, xattrs, setup/cleanup, and v1 net_cls declarations.

Control flow: header only.

State and persistence: no header state; implementation manipulates cgroup mounts and process membership.

Dependencies and integration points: included by tests needing cgroup setup or attachment targets.

Risks: `log_err` depends on `fprintf` being available from includer order; helper calls can have broad process/environment side effects.

Test signals: compile-time interface for cgroup tests; runtime diagnostics include source file and line.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/cgroup_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/cgroup_iter_memcg.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/cgroup_iter_memcg.h

Purpose: shared query structure for cgroup memory iterator tests.

Important APIs and types: `struct memcg_query` contains selected memory cgroup node stats (`nr_anon_mapped`, `nr_shmem`, `nr_file_pages`, `nr_file_mapped`) and vm event `pgfault`.

Control flow: header only.

State and persistence: structure instances carry sampled memory counters between BPF/user-space test components.

Dependencies and integration points: included by cgroup iterator tests that need a stable ABI-like layout.

Risks: fields are a subset of kernel counters and depend on tests populating/interpreting them consistently; type widths assume unsigned long compatibility between sides.

Test signals: iterator tests can compare expected memory counter deltas in this structure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/cgroup_iter_memcg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/cgroup_tcp_skb.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/cgroup_tcp_skb.h

Purpose: defines a TCP socket state model for cgroup skb message tracking tests.

Important APIs and types: enum values from `INIT` through `TIME_WAIT`, with extra states like `SYN_RECV_SENDING_SYN_ACK`, `CLOSE_WAIT_SENDING_ACK`, and `TIME_WAIT_SENDING_ACK` to represent outbound control-message phases.

Control flow: header only; tests/BPF programs use enum values as state-machine labels.

State and persistence: no header state; enum values may be stored in maps/test state by consumers.

Dependencies and integration points: based on RFC 9293 states with modifications for tracking sent messages.

Risks: custom states are test-specific and should not be confused with kernel TCP enum values; changes must stay synchronized between BPF and user-space test logic.

Test signals: cgroup TCP skb tests can assert expected state transitions across SYN/ACK/FIN flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/cgroup_tcp_skb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/config

Purpose: kernel configuration fragment for enabling BPF selftest coverage and related networking, tracing, security, crypto, and filesystem features.

Important settings: enables core BPF (`CONFIG_BPF`, `BPF_SYSCALL`, `BPF_JIT`, `BPF_EVENTS`, `CGROUP_BPF`, `BPF_LSM`), debug/BTF (`DEBUG_INFO_BTF`), tracing (`FUNCTION_TRACER`, `DYNAMIC_FTRACE`, `FPROBE`, `FTRACE_SYSCALLS`), networking features for XDP/tunnels/netfilter/MPLS/MPTCP/SMC, IMA/fsverity/keys, modules, and test/sample support.

Control flow: not executable; consumed by kernel/selftest build or VM setup workflows.

State and persistence: persistent desired kernel config state when merged into a build.

Dependencies and integration points: aligns kernel feature availability with the selftests in this tree.

Risks: config can drift behind tests requiring newer options; enabling many subsystems increases build/runtime surface; `CONFIG_BPF_UNPRIV_DEFAULT_OFF` is explicitly not set, which matters for privilege assumptions.

Test signals: kernels built with this fragment should satisfy feature gates for broad BPF selftest execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/disasm.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/disasm.c

Purpose: BPF instruction disassembler shared with selftests, formatting eBPF bytecode into human-readable strings.

Important APIs and functions: `func_id_name()` maps helper ids; `print_bpf_insn()` formats one instruction using `struct bpf_insn_cbs` callbacks. Static tables map classes, ALU ops, signed div/mod, movsx, atomic ops, load/store widths, signed loads, and jumps. Special handling covers helper/pseudo/kfunc calls, ldimm64, address-space casts, percpu address moves, atomics, may_goto, gotox, and endian/bswap.

Control flow: `print_bpf_insn()` switches by BPF instruction class and submode, formats the corresponding syntax, invokes callbacks for helper names and immediate names, and masks pointer immediates unless allowed.

State and persistence: static string tables only.

Dependencies and integration points: uses Linux BPF UAPI, kernel-style stringify/build macros, and callback definitions from `disasm.h`. Kept close to kernel verifier/JIT disassembler behavior.

Risks: instruction set additions require updates; malformed/unknown encodings print `BUG_*`; pointer leak masking must be used correctly by callers; formatting changes can break string-comparison tests.

Test signals: tests can compare expected instruction strings for generated BPF programs, including new opcodes and pseudo-call handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/disasm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/disasm.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/disasm.h

Purpose: public interface for BPF instruction disassembly.

Important APIs and types: exports `bpf_alu_string`, `bpf_class_string`, `func_id_name()`, callback typedefs `bpf_insn_print_t`, `bpf_insn_revmap_call_t`, `bpf_insn_print_imm_t`, `struct bpf_insn_cbs`, and `print_bpf_insn()`.

Control flow: header only.

State and persistence: no state in the header.

Dependencies and integration points: includes BPF UAPI and kernel/stringify helpers; also includes stdio/string outside kernel builds.

Risks: callbacks must be valid for the duration of printing; `allow_ptr_leaks` policy is enforced by implementation, not type system.

Test signals: consumers compile against the callbacks and can capture disassembly output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/disasm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/disasm_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/disasm_helpers.c

Purpose: compact helper to disassemble one BPF instruction into a normalized string suitable for tests.

Important APIs and functions: `disasm_insn(insn, buf, buf_sz)` builds `bpf_insn_cbs`, calls `print_bpf_insn()`, strips the leading opcode prefix and trailing newline, simplifies call strings by removing `#id`, and advances over one or two instructions for ldimm64.

Control flow: callback `print_insn_cb()` writes into caller buffer; `print_call_cb()` prints pseudo-call offsets from `insn->off` because verifier subprog JIT rewrites `imm`.

State and persistence: only stack context and caller-provided buffer.

Dependencies and integration points: depends on `disasm.c` API and libbpf BPF definitions.

Risks: assumes disassembler prefix length of five characters; normalization can break if `print_bpf_insn()` formatting changes; buffer truncation is possible via `vsnprintf`.

Test signals: tests can iterate instructions by assigning returned pointer and compare short assembly strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/disasm_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/disasm_helpers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/disasm_helpers.h

Purpose: declares the single-instruction disassembly helper.

Important APIs and functions: forward-declares `struct bpf_insn` and declares `disasm_insn(struct bpf_insn *insn, char *buf, size_t buf_sz)`.

Control flow: header only.

State and persistence: none.

Dependencies and integration points: includes stdlib for `size_t`; pairs with `disasm_helpers.c`.

Risks: caller must provide a sufficiently sized writable buffer and valid instruction stream, including the second half of ldimm64.

Test signals: compile-time interface for tests comparing normalized disassembly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/disasm_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/flow_dissector_load.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/flow_dissector_load.c

Purpose: standalone helper program to attach or detach a BPF flow dissector program and pin the loaded object.

Important APIs and functions: global config variables hold pin path, prog-array map name, attach flag, section name, and object path. `parse_opts()` handles `-a`, `-d`, `-p`, and `-s`. `load_and_attach_program()` uses `bpf_flow_load()`, `bpf_prog_attach(..., BPF_FLOW_DISSECTOR)`, and `bpf_object__pin()`. `detach_program()` detaches and removes the pin directory.

Control flow: main parses options, then either loads/attaches/pins or detaches/unpins. Attach requires both object path and section name.

State and persistence: attaching persists a flow dissector program in kernel state and pins object under `/sys/fs/bpf/flow_dissector`; detach removes both.

Dependencies and integration points: depends on libbpf strict mode, `flow_dissector_load.h`, bpffs, and kernel flow dissector attach support.

Risks: `detach_program()` uses `system("rm -r ...")` with a global path; attach/detach are privileged operations; pin path is fixed; `error(1, ...)` exits immediately on failure.

Test signals: successful attach leaves pinned object and active flow dissector; successful detach removes it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/flow_dissector_load.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/flow_dissector_load.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/flow_dissector_load.h

Purpose: inline loader for flow dissector BPF objects with program-array population.

Important APIs and functions: `bpf_flow_load(obj, path, prog_name, map_name, keys_map_name, prog_fd, keys_fd)` loads an object as `BPF_PROG_TYPE_FLOW_DISSECTOR`, finds the main program by name, finds a prog-array map, optionally finds a keys map, and fills the prog-array with all non-main program fds.

Control flow: load object, resolve main program fd, resolve map fds, iterate all programs, and update the prog-array sequentially.

State and persistence: loaded BPF object and maps persist through the returned object pointer and file descriptors; caller owns lifetime.

Dependencies and integration points: uses `bpf_prog_test_load()` from `testing_helpers.h`, libbpf object/program/map iteration, and `bpf_map_update_elem`.

Risks: assumes all non-main programs should be inserted in iteration order; does not check `bpf_map_update_elem` errors; returns generic `-1` for many lookup failures.

Test signals: flow dissector tests can verify object load, main fd, optional keys map fd, and tail-call program array population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/flow_dissector_load.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/generate_udp_fragments.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/generate_udp_fragments.py

Purpose: generator script for deterministic IPv4 and IPv6 fragmented UDP packet byte arrays used by defragmentation tests.

Important APIs and functions: constants mirror `ip_check_defrag.c`; `print_header()`, `print_frags()`, and `print_trailer()` emit C header text; `main()` builds Scapy IPv4/UDP and IPv6/fragment/UDP packets, fragments them, and writes `ip_check_defrag_frags.h`.

Control flow: when run as a script, resolves its directory, opens the target header for writing, builds packets with fixed addresses/ports/message, fragments at fixed sizes, and emits arrays.

State and persistence: overwrites generated header file in the same directory. No runtime state after script exits.

Dependencies and integration points: requires Python 3 and Scapy; generated header is consumed by C defrag tests and must stay synchronized with constants.

Risks: wildcard `from scapy.all import *`; generated output changes if Scapy serialization changes; IPv4 source is `0.0.0.0` to be filled by `IP_HDRINCL`; maintainers must rerun after constant changes.

Test signals: generated `ip_check_defrag_frags.h` contains `frag_*` and `frag6_*` arrays with the magic payload split across fragments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/generate_udp_fragments.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/gnu/stubs.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/gnu/stubs.h

Purpose: dummy header to satisfy glibc `features.h` include expectations when compiling with `clang --target=bpf`.

Important APIs and functions: no APIs; contains only a comment.

Control flow: none.

State and persistence: none.

Dependencies and integration points: used through include path layout so BPF-target compilation can find `gnu/stubs.h`.

Risks: intentionally empty; if a build unexpectedly needs real glibc stubs, this only masks include resolution and not ABI support.

Test signals: successful BPF-target compilation where system headers include `gnu/stubs.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/gnu/stubs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/ima_setup.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/ima_setup.sh

Purpose: helper script for IMA-related BPF selftests to create a loopback ext2 filesystem, install an IMA measurement policy, run/modify/restore a copied test binary, and clean up.

Important APIs and functions: actions `setup`, `cleanup`, `run`, `modify-bin`, `restore-bin`, and `load-policy`; `ensure_mount_securityfs()` mounts securityfs if needed; setup uses `dd`, `losetup`, `mkfs.ext2`, `mount`, `blkid`, and writes `/sys/kernel/security/ima/policy`.

Control flow: validates two arguments, routes by action, captures logs to a temp file unless verbose, and uses an EXIT trap to print logs only on failure.

State and persistence: creates a loop image, loop device, mount directory, copied `/bin/true`, policy file, and possibly active IMA policy entries. Cleanup detaches loop devices, unmounts, and removes tmpdir.

Dependencies and integration points: requires root privileges, loop device support, ext2 tools, securityfs, IMA enabled, and writable IMA policy.

Risks: cleanup order detaches loop devices before unmounting, which can fail depending on kernel behavior; loop device discovery by grepping image path can match multiple stale devices; appending/truncating binary assumes `modify-bin` appends exactly four bytes.

Test signals: run action executes copied binary to trigger IMA; load-policy failures are intentionally suppressible; errors print captured command logs when not verbose.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/ima_setup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/io_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/io_helpers.c

Purpose: provides a timeout-enabled read helper for selftests.

Important APIs and functions: `read_with_timeout(fd, buf, count, usec)` uses `select()` on one fd with a microsecond timeout, then calls `read()` if ready.

Control flow: initializes `timeval` and fd set, waits for readability, returns select error if negative, returns read result if fd is set, otherwise returns `-EAGAIN`.

State and persistence: no persistent state.

Dependencies and integration points: depends on `select`, `read`, errno values, and declaration in `io_helpers.h`.

Risks: only monitors readability and a single fd; `select` fd limit applies; does not retry on `EINTR`; timeout mutability by `select` is local.

Test signals: callers can distinguish timeout (`-EAGAIN`), read bytes, EOF, and select errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/io_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/io_helpers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/io_helpers.h

Purpose: declares the timeout-enabled read helper.

Important APIs and functions: `read_with_timeout(int fd, char *buf, size_t count, long usec)`.

Control flow: header only.

State and persistence: none.

Dependencies and integration points: includes unistd for `size_t`/read-related declarations and pairs with `io_helpers.c`.

Risks: function returns negative errno-style `-EAGAIN` for timeout but raw negative `select` errors for select failure, so callers should handle both.

Test signals: compile-time declaration for tests that need bounded blocking reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/io_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/ip_check_defrag_frags.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/ip_check_defrag_frags.h

Purpose: generated C header containing byte arrays for fragmented IPv4 and IPv6 UDP packets used by IP defragmentation tests.

Important APIs and data: arrays `frag_0` through `frag_2` for IPv4 and `frag6_0` through `frag6_2` for IPv6. The bytes encode the UDP ports and magic message generated by `generate_udp_fragments.py`.

Control flow: header only; consumers include it and inject/use the fragments.

State and persistence: static byte arrays are compiled into tests.

Dependencies and integration points: generated by `generate_udp_fragments.py` and must stay aligned with `ip_check_defrag.c` constants.

Risks: file is marked do-not-edit; manual changes can desynchronize checksums, IDs, and payload; static arrays have internal linkage in each translation unit.

Test signals: defrag tests should reconstruct the original magic message from these fragments for IPv4 and IPv6 paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/ip_check_defrag_frags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/jit_disasm_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/jit_disasm_helpers.c

Purpose: obtains and disassembles JITed native code for loaded BPF programs when built with LLVM disassembler support.

Important APIs and functions: `get_jited_program_text(fd, text, text_sz)` fetches JITed bytes and per-function lengths with `bpf_prog_get_info_by_fd`, then disassembles each function. LLVM-backed helpers initialize targets, discover local branch labels, assign `L#` labels, and print addresses, bytes, labels, and instructions. Without LLVM support, the function returns `-EOPNOTSUPP`.

Control flow: first info query gets total JIT length and function count, buffers are allocated, second query fills bytes/lens, then each function is disassembled in two passes: label discovery and formatted output.

State and persistence: static `llvm_initialized` avoids repeated LLVM initialization. All buffers are freed per call.

Dependencies and integration points: depends on libbpf, `test_progs.h` assertions/env, LLVM C disassembler APIs under `HAVE_LLVM_SUPPORT`, and kernel JIT info exposure.

Risks: native disassembly target uses default host triple; JIT bytes may be unavailable without privileges/sysctls; local label capacity is capped at 32; output is architecture-specific.

Test signals: tests can compare or print JITed native text; missing LLVM support emits a verbose skip-style message and returns `-EOPNOTSUPP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/jit_disasm_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/jit_disasm_helpers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/jit_disasm_helpers.h

Purpose: declares JIT disassembly helper interface.

Important APIs and functions: `get_jited_program_text(int fd, char *text, size_t text_sz)`.

Control flow: header only.

State and persistence: no header state; implementation may initialize LLVM once.

Dependencies and integration points: includes stddef for `size_t`; used by tests that inspect native JIT output.

Risks: caller must provide adequate output buffer; function may be unsupported depending on build flags.

Test signals: compile-time declaration and runtime return code/text content.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/jit_disasm_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/json_writer.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/json_writer.c

Purpose: simple streaming JSON writer that manages commas, nesting, optional pretty printing, and primitive value formatting.

Important APIs and functions: `jsonw_new`, `jsonw_destroy`, `jsonw_pretty`, `jsonw_reset`, `jsonw_name`, `jsonw_printf`, `jsonw_vprintf_enquote`, object/array start/end functions, primitive writers, and field helpers. Internal helpers handle indentation, end-of-line, comma insertion, and JSON string escaping.

Control flow: writer tracks `depth` and `sep`. Starting a collection writes any needed comma, emits `{`/`[`, increments depth, and resets separator. Ending decrements depth and writes closing delimiter. Names and values manage separators so callers can stream JSON incrementally.

State and persistence: heap-allocated `json_writer` holds output file, depth, pretty flag, and separator. Destroy asserts balanced depth, writes newline, flushes, frees, and nulls caller pointer.

Dependencies and integration points: used by bpftool-derived or selftest output code needing JSON without external dependencies.

Risks: string escaping does not emit Unicode escapes for control characters beyond common C escapes; `jsonw_destroy` asserts rather than returning an error on unbalanced JSON; header declares `jsonw_float` while implementation keeps it under `#ifdef notused`.

Test signals: `#ifdef TEST` main exercises nested objects/arrays and escaping; consumers can validate emitted JSON syntax.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/json_writer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/json_writer.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/json_writer.h

Purpose: public interface for the streaming JSON writer.

Important APIs and types: opaque `json_writer_t`; lifecycle, pretty/reset, name, printf/string/bool/float/int/null writers, field helpers, object/array collection functions, and `jsonw_err_handler_fn` typedef.

Control flow: header only.

State and persistence: writer state is opaque and allocated by `jsonw_new`.

Dependencies and integration points: includes stdbool/stdint/stdarg/stdio and Linux compiler annotations for printf checking.

Risks: declares `jsonw_float` and `jsonw_float_field`, but implementation compiles those only inside `#ifdef notused`; users should prefer `jsonw_float_fmt`/`jsonw_float_field_fmt` unless build provides definitions.

Test signals: compile/link success for used writer APIs and valid JSON output from implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/json_writer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/map_tests/array_map_batch_ops.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/map_tests/array_map_batch_ops.c

Purpose: validates batch update and lookup operations for array and per-CPU array BPF maps.

Important APIs and functions: `map_batch_update()` fills keys/values and calls `bpf_map_update_batch`; `map_batch_verify()` checks key/value relationships and visited coverage; `__test_map_lookup_and_update_batch(is_pcpu)` creates map, allocates buffers, and performs lookup-batch loops with varying step sizes. Public test entry `test_array_map_batch_ops()` runs normal and per-CPU variants after detecting possible CPUs.

Control flow: for each step from 1 to max_entries - 1, the test repopulates the map, clears buffers, repeatedly calls `bpf_map_lookup_batch` using the returned batch cursor, verifies total count and values, and counts successful step sizes.

State and persistence: map fd lives for each test case and is closed at end. Heap buffers hold keys, visited flags, and values; per-CPU values are laid out as `max_entries * nr_cpus` `__s64`s.

Dependencies and integration points: uses libbpf map create/batch APIs, `test_maps.h` `CHECK` macro, and `libbpf_num_possible_cpus`.

Risks: pointer arithmetic on `void *values` in lookup call depends on compiler extension; fixed `max_entries=10` gives focused but small coverage; failures continue through `CHECK` semantics rather than immediate returns.

Test signals: prints `test_array_map_batch_ops:PASS` and `test_array_percpu_map_batch_ops:PASS` when both variants pass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/map_tests/array_map_batch_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/map_tests/htab_map_batch_ops.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/map_tests/htab_map_batch_ops.c

Purpose: validates lookup, delete, and lookup-and-delete batch operations for hash and per-CPU hash BPF maps.

Important APIs and functions: `map_batch_update()` fills normal or per-CPU values and calls `bpf_map_update_batch`; `map_batch_verify()` validates key/value pairs and coverage; `__test_map_lookup_and_delete_batch(is_pcpu)` runs empty-map, zero-count, full-count, stepped lookup/delete, and stepped lookup-and-delete scenarios. Public entries `htab_map_batch_ops`, `htab_percpu_map_batch_ops`, and `test_htab_map_batch_ops` run both variants.

Control flow: create a hash map, verify empty lookup-and-delete returns `ENOENT`, populate, test zero-count success, delete all entries, confirm map empty, then iterate step sizes. For each step, it tolerates `ENOSPC` for too-small buffers, otherwise verifies complete lookup, batch delete empties the map, and lookup-and-delete both returns all data and empties the map.

State and persistence: map fd and buffers are per test invocation. Per-CPU values use `BPF_DECLARE_PERCPU` layout, with stack array for `max_entries`.

Dependencies and integration points: uses libbpf batch APIs, `bpf_util.h` per-CPU helpers, possible CPU count, and `test_maps.h` `CHECK`.

Risks: `batch` cursor is not explicitly reset before every phase, relying on API behavior and assignment patterns; ENOSPC paths skip small step sizes, so total success check is important; fixed small map size limits scale coverage.

Test signals: pass messages for hash and per-CPU hash variants, plus `CHECK` failures on unexpected errno, count, value, or non-empty map state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/map_tests/htab_map_batch_ops.c -->
