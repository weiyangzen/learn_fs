# Research: subset-b-006781

Grouped source-tree-aligned research for the requested files. Each section is delimited for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_sdt.bpf.c -->
# sources/distributed-fs/ceph-client/tools/sched_ext/scx_sdt.bpf.c

Purpose: implements `scx_sdt`, a sched_ext BPF struct_ops scheduler derived from `scx_simple` whose main purpose is demonstrating BPF arena memory management for per-task scheduler data. It schedules tasks through a shared DSQ while allocating task stats from an mmapable `BPF_MAP_TYPE_ARENA`.

Important APIs, types, and functions: the file defines the `arena` map, `UEI_DEFINE(uei)`, allocator pools (`desc_pool`, `chunk_pool`), a global `scx_task_allocator`, `scx_task_map` task-storage map, and struct_ops callbacks `sdt_select_cpu`, `sdt_enqueue`, `sdt_dispatch`, `sdt_init_task`, `sdt_exit_task`, `sdt_init`, and `sdt_exit`. The allocator path is `scx_task_init()` -> `scx_alloc_init()` -> `pool_set_size()` plus `scx_alloc_chunk()`; task data comes from `scx_task_alloc()`, `scx_task_data()`, and `scx_task_free()`. Index management is a three-level bitmap/radix structure over `sdt_desc` and `sdt_chunk`, with `desc_find_empty()`, `chunk_find_empty()`, `set_idx_state()`, `mark_nodes_avail()`, and `scx_alloc_free_idx()`.

Control flow: `sdt_init()` initializes an arena-backed allocator sized for `struct scx_stats` and creates DSQ 0. For each task entering sched_ext, `sdt_init_task()` allocates arena payload, stores a task-local pointer in `BPF_MAP_TYPE_TASK_STORAGE`, initializes the pid, and increments init stats. `sdt_select_cpu()` asks the default selector for an idle CPU; idle selections are inserted directly to `SCX_DSQ_LOCAL`, while busy cases fall through to `sdt_enqueue()`, which inserts into `SHARED_DSQ`. `sdt_dispatch()` moves one task from the shared DSQ to the local DSQ. `sdt_exit_task()` updates global counters from the per-task arena stats, frees the allocator index, and deletes task storage. `sdt_exit()` records user-exit info.

State and persistence: allocator state lives in global BPF data and arena pages for the lifetime of the loaded scheduler. Per-task state is persistent across scheduling callbacks through task storage but is freed on exit. `alloc_stats` and the `stat_*` globals are visible to userspace through the skeleton BSS. The generation field in `union sdt_id` is incremented on recycle to distinguish reused indices. Spin locks serialize allocator metadata; the stats increments are per-task until exit and then atomically folded into globals.

Dependencies and integration points: depends on sched_ext helper APIs from `<scx/common.bpf.h>`, arena helpers from `<scx/bpf_arena_common.bpf.h>`, BPF spin locks, task storage, and verifier loop helpers such as `can_loop`. It shares data layout with `scx_sdt.h` and is loaded by `scx_sdt.c`. The `scx_arena_subprog_init()` printk hack exists to make the verifier associate arena state with subprograms that only use arena-derived pointers.

Risks: allocator correctness is subtle: bitmap propagation, `nr_free` accounting, and failure rollback in `scx_alloc()` must stay synchronized or task data can leak or be reused incorrectly. The code relies on verifier-sensitive idioms (`zero`, `can_loop`, arena pointer hack), so kernel verifier changes can break loading. `scx_task_data()` trusts stored arena pointers once task storage exists; stale storage or allocation/free imbalance would be serious. Global stat folding only happens at task exit, so live-task counters are not reflected in BSS totals.

Test signals: userspace can observe successful load, steady DSQ operation, growing init/enqueue/select counters, balanced `alloc_ops`/`free_ops` after workload exit, and no `UEI` error. Negative signals include verifier rejection, allocator `-ENOMEM`, BPF `scx_bpf_error()` messages for missing stats, and nonzero active allocations after all test tasks exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_sdt.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_sdt.c -->
# sources/distributed-fs/ceph-client/tools/sched_ext/scx_sdt.c

Purpose: userspace loader and monitor for the `scx_sdt` arena-backed sched_ext scheduler. It opens, loads, attaches, and restarts the BPF struct_ops scheduler while printing scheduler and allocator counters once per second.

Important APIs, types, and functions: uses the generated `scx_sdt.bpf.skel.h` skeleton, sched_ext helper macros `SCX_OPS_OPEN`, `SCX_OPS_LOAD`, `SCX_OPS_ATTACH`, and `UEI_REPORT`, plus libbpf logging via `libbpf_set_print()`. `libbpf_print_fn()` gates debug messages behind `-v`; `sigint_handler()` sets `exit_req`; `main()` drives argument parsing, attachment, stat reporting, link destruction, and restart on `UEI_ECODE_RESTART()`.

Control flow: `main()` installs SIGINT/SIGTERM handlers, opens the skeleton at the `restart:` label, parses `-v`/`-h`, loads and attaches `sdt_ops`, then loops until a signal or BPF exit info is reported. The loop reads BSS globals directly through `skel->bss`, prints scheduling counters and allocator counters, flushes stdout, and sleeps one second. On exit it destroys the BPF link, reports the UEI code, destroys the skeleton, and restarts if requested.

State and persistence: userspace state is minimal: `verbose`, `exit_req`, the skeleton pointer, and the link. BPF state is reset on a full skeleton destroy/reopen except when the kernel requests a controlled restart, in which case the program jumps back to load a fresh instance. Printed allocator `arena_pages_used` is read but, in the BPF source viewed here, not visibly updated, so it may stay zero unless maintained by included arena helpers.

Dependencies and integration points: depends on libbpf, generated skeletons, `scx/common.h`, `scx_sdt.h`, and kernel sched_ext support. It must run with privileges sufficient to attach sched_ext struct_ops.

Risks: the program does not validate the returned `link` pointer beyond the macro behavior, so failures are macro-dependent. Its stats are raw monotonic counters without rate calculation. Because it sleeps one second, shutdown has up to one second latency. It also assumes all expected BSS symbols exist and match the BPF object.

Test signals: `-h` should print usage, `-v` should enable libbpf debug logging, and a successful run should print both scheduling and allocation sections repeatedly. Restart behavior can be observed by causing sched_ext to request restart and checking the loader reopens instead of exiting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_sdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_sdt.h -->
# sources/distributed-fs/ceph-client/tools/sched_ext/scx_sdt.h

Purpose: shared BPF/userspace header defining the arena allocator data structures and scheduler statistics used by `scx_sdt`.

Important APIs, types, and functions: defines `struct scx_alloc_stats`, `struct sdt_pool`, `union sdt_id`, `struct sdt_desc`, `struct sdt_data`, `struct sdt_chunk`, `struct scx_allocator`, and `struct scx_stats`. Constants in `enum sdt_consts` configure a three-level tree of 512-entry chunks, bitmap word count, and minimum data elements per arena allocation. When compiled for BPF it declares allocator/task-data helpers such as `scx_task_data()`, `scx_task_init()`, `scx_task_alloc()`, `scx_task_free()`, `scx_alloc_init()`, and `scx_alloc_free_idx()`.

Control flow: this header does not execute code, but its layouts determine how `scx_sdt.bpf.c` indexes arena chunks, wraps per-task payloads behind `struct sdt_data`, stores generation-aware IDs, and presents `struct scx_stats` to both BPF and userspace skeleton readers.

State and persistence: `sdt_pool` tracks current slab, element size, capacity, and next index. `sdt_desc` persists allocation bitmaps and free counts. `sdt_data` stores the allocated index/generation ahead of the flexible payload. `scx_stats` is the per-task payload that accumulates scheduling counters until exit.

Dependencies and integration points: uses kernel fixed-width types and `pid_t`; defines `__arena` away for non-BPF compilation so userspace can include the same file. It is tightly coupled to verifier-friendly arena pointer annotations in the BPF program.

Risks: any structure layout change must preserve BPF/userspace skeleton ABI and the allocator's assumptions. `SDT_TASK_ENTS_PER_PAGE_SHIFT` and `SDT_TASK_LEVELS` set allocator capacity and bitmap sizes; changing them can break index math or verifier bounds. The header declares `scx_alloc_internal()` but the viewed BPF file implements `scx_alloc()`, so declarations should be checked against all build users.

Test signals: compile-time structure checks in the BPF source and successful skeleton generation are primary signals. Runtime signals include correct per-task stats layout in `scx_sdt.c` and allocator counters behaving consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_sdt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_show_state.py -->
# sources/distributed-fs/ceph-client/tools/sched_ext/scx_show_state.py

Purpose: drgn script that prints core sched_ext kernel state from a live kernel or dump.

Important APIs, types, and functions: imports `drgn` and relies on drgn's global `prog` object. Helper functions `read_int()`, `read_atomic()`, `read_static_key()`, and `state_str()` read symbols such as `scx_enable_state_var`, `__scx_enabled`, `__scx_switched_all`, and `scx_enable_state_str`. `err()` exists for fatal reporting but is unused in the current file.

Control flow: after helper definitions, the script reads `scx_root` and the enable-state atomic. It prints the active ops name when `scx_root` is non-null, followed by enabled/switching/switched state, decoded enable state, aborting flag, bypass depth, rejected count, and enable sequence.

State and persistence: the script has no persistent state; it reads kernel globals at one instant. Atomic counters are read through their internal `counter` fields, and static keys through `key.enabled.counter`.

Dependencies and integration points: requires drgn, matching kernel debug symbols, and sched_ext symbols. It integrates with sched_ext debugging by exposing kernel-private state without requiring a purpose-built kernel interface.

Risks: the script is fragile to kernel symbol or type layout changes. It assumes `prog` contains named globals and that `scx_enable_state_str[state]` is valid. It does not catch missing-symbol exceptions or validate state bounds.

Test signals: running under drgn on a kernel with sched_ext should print all fields. A disabled system should show empty `ops`; an attached scheduler should show its `ops.name`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_show_state.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_simple.bpf.c -->
# sources/distributed-fs/ceph-client/tools/sched_ext/scx_simple.bpf.c

Purpose: simple sched_ext BPF scheduler that demonstrates either global FIFO scheduling or weighted virtual-time scheduling using a shared DSQ.

Important APIs, types, and functions: defines read-only `fifo_sched`, global `vtime_now`, UEI state, shared DSQ ID 0, and a per-CPU array `stats` with local/global queue counters. Struct_ops callbacks are `simple_select_cpu`, `simple_enqueue`, `simple_dispatch`, `simple_running`, `simple_stopping`, `simple_enable`, `simple_init`, and `simple_exit`.

Control flow: `simple_init()` creates the shared DSQ. On wakeup, `simple_select_cpu()` uses the default selector; if it finds an idle CPU it inserts directly into the local DSQ and increments local stats. Otherwise `simple_enqueue()` inserts into the shared DSQ, either FIFO or by `p->scx.dsq_vtime`. In virtual-time mode it clamps idle credit to one default slice, uses `scx_bpf_dsq_insert_vtime()`, advances `vtime_now` when a task starts running, and charges consumed slice in `simple_stopping()` scaled by inverse task weight. `simple_dispatch()` pulls from the shared DSQ to the local CPU.

State and persistence: `vtime_now` persists while the BPF object is loaded and is intentionally racy but monotonic enough for a sample scheduler. Per-task virtual time is stored in sched_ext task state, not in custom maps. The per-CPU `stats` map persists until unload and is aggregated by userspace.

Dependencies and integration points: uses sched_ext BPF helpers, DSQ APIs, per-CPU BPF maps, task weight scaling helpers, and UEI. It is loaded by `scx_simple.c`.

Risks: FIFO mode can starve interactive workloads if CPU-saturating tasks dominate. Vtime updates are racy across CPUs by design, so fairness is approximate. There is no preemption implementation beyond sched_ext defaults. Built-in global DSQ is avoided because vtime insertion requires a custom priority-capable DSQ.

Test signals: successful attach, local/global stats increments, and stable workload progress are main signals. In vtime mode, weighted tasks should receive differentiated CPU shares; in FIFO mode, queue order should dominate. UEI errors or DSQ creation failure indicate scheduler failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_simple.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_simple.c -->
# sources/distributed-fs/ceph-client/tools/sched_ext/scx_simple.c

Purpose: userspace control program for `scx_simple.bpf.c`, with options for FIFO mode and libbpf verbosity.

Important APIs, types, and functions: uses generated `scx_simple.bpf.skel.h`, `SCX_OPS_*` macros, `UEI_REPORT`, `bpf_map_lookup_elem()`, and `libbpf_num_possible_cpus()`. `read_stats()` aggregates the two-entry per-CPU `stats` map across all possible CPUs.

Control flow: `main()` configures libbpf logging and signal handlers, opens the skeleton, parses `-f`, `-v`, and `-h`, sets `skel->rodata->fifo_sched` for FIFO mode before load, loads and attaches struct_ops, then prints `local` and `global` aggregate queue counts once per second until signal or UEI exit. It destroys the link and skeleton and restarts on `UEI_ECODE_RESTART()`.

State and persistence: userspace state is only process-local. The scheduler mode is fixed by BPF rodata before load and cannot be changed after attach. Stats are read from BPF map state and reset with a new BPF object instance.

Dependencies and integration points: depends on libbpf, sched_ext userspace helpers, the generated skeleton, and matching BPF map layout. Requires enough privilege and kernel support for sched_ext.

Risks: `read_stats()` uses a VLA sized by possible CPUs, which is convenient but stack-sensitive on very large CPU counts. Failed map lookups are silently skipped, potentially under-reporting stats. The signal handler name argument is unused and misleadingly named `simple`.

Test signals: `-f` should flip BPF rodata and produce FIFO scheduling; without `-f` vtime mode should load. Queue counters should grow under runnable workloads. Attach/load failures or UEI reports identify kernel-side issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_simple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_userland.bpf.c -->
# sources/distributed-fs/ceph-client/tools/sched_ext/scx_userland.bpf.c

Purpose: BPF half of a demonstration sched_ext scheduler that delegates scheduling of unrestricted tasks to a userspace scheduler while directly scheduling CPU-affine tasks in-kernel.

Important APIs, types, and functions: defines rodata `usersched_pid` and `num_possible_cpus`, stats counters (`nr_failed_enqueues`, `nr_kernel_enqueues`, `nr_user_enqueues`), shared work counters (`nr_queued`, `nr_scheduled`), queue maps `enqueued` and `dispatched`, task storage map `task_ctx_stor`, and struct_ops callbacks `userland_select_cpu`, `userland_enqueue`, `userland_dispatch`, `userland_update_idle`, `userland_init_task`, `userland_init`, and `userland_exit`.

Control flow: `userland_init()` validates userspace initialized CPU count and scheduler pid. Each task gets `task_ctx` storage. CPU-affine tasks (`nr_cpus_allowed < num_possible_cpus`) are handled in kernel: `select_cpu` tries previous or any idle CPU and marks `force_local`; `enqueue` inserts to local or global DSQ and counts kernel enqueues. Non-affine tasks, except the scheduler task itself, are encoded as `scx_userland_enqueued_task` records and pushed to the `enqueued` queue map. The userspace scheduler later pushes selected PIDs to `dispatched`; `userland_dispatch()` pops those PIDs, looks up live tasks, and inserts them into the global DSQ. `usersched_needed` wakes the scheduler task through `dispatch_user_scheduler()` and idle CPU kicks.

State and persistence: kernel/user coordination is through queue maps and BSS counters. `usersched_needed` is an atomic-style flag. Per-task `force_local` is task-local. `nr_queued` is incremented in BPF-side enqueue and is expected to be decremented/cleared by userspace after draining; `nr_scheduled` is written by userspace to show outstanding user-scheduled tasks.

Dependencies and integration points: depends on sched_ext helpers, task storage, BPF queue maps, `bpf_task_from_pid()`, and the shared layout in `scx_userland.h`. It is paired with `scx_userland.c`, which must keep the scheduler task itself under sched_ext.

Risks: queue overflow falls back to global DSQ and increments failed enqueue stats, reducing fidelity. The BPF side trusts userspace to maintain `nr_queued` and `nr_scheduled`; stale counters may cause unnecessary or missing scheduler wakeups. PID dispatch races are tolerated by dropping missing tasks, but PID reuse remains a conceptual risk in simple examples. Userspace scheduler failure can strand unrestricted tasks.

Test signals: successful init requires positive `usersched_pid` and CPU count. Counters should show kernel enqueues for affinity-constrained tasks and user enqueues for unrestricted tasks. `nr_failed_enqueues` should stay zero under normal queue sizes. Idle CPUs should trigger scheduler wakeups when work remains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_userland.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_userland.c -->
# sources/distributed-fs/ceph-client/tools/sched_ext/scx_userland.c

Purpose: userspace scheduler component for `scx_userland.bpf.c`, implementing a simple vruntime-sorted list for tasks delegated by the BPF scheduler.

Important APIs, types, and functions: uses generated `scx_userland.bpf.skel.h`, queue map file descriptors, `sched_setscheduler(..., SCHED_EXT, ...)`, `mlockall()`, pthread stats printing, and BSD `LIST_*` macros. Important functions include `init_tasks()`, `dispatch_task()`, `update_enqueued()`, `vruntime_enqueue()`, `drain_enqueued_map()`, `dispatch_batch()`, `run_stats_printer()`, `pre_bootstrap()`, `bootstrap()`, and `sched_main_loop()`.

Control flow: `pre_bootstrap()` allocates a PID-indexed task array sized from `/proc/sys/kernel/pid_max`, installs signals, moves the scheduler process to `SCHED_EXT`, parses `-b`/`-v`, and locks memory to avoid allocation stalls later. `bootstrap()` resets state, opens and loads BPF, sets rodata CPU count and scheduler pid, captures queue map FDs, starts the stats thread, and attaches struct_ops. The main loop drains the BPF `enqueued` queue with lookup-and-delete, updates each task's vruntime from kernel-provided `sum_exec_runtime` and weight, inserts into sorted order, dispatches up to `batch_size` lowest-vruntime tasks to the `dispatched` queue, updates BPF counters, and yields.

State and persistence: `tasks` persists across restarts but is zeroed in `bootstrap()`. Each PID slot stores last runtime and accumulated vruntime. `min_vruntime` bounds new/returning tasks. BPF BSS counters and queue maps are shared live state. The stats thread reads BPF and userspace atomics until shutdown.

Dependencies and integration points: depends on libbpf, sched_ext userspace helpers, pthreads, syscall availability for `SCHED_EXT`, and the shared `scx_userland_enqueued_task` layout. Kernel pid_max drives memory use.

Risks: the PID-indexed array can be large and the help text explicitly warns about OOM if pid_max is high. The vruntime queue is an O(n) sorted list, acceptable for demonstration but not scalable. PID reuse and missing lifecycle callbacks can confuse per-PID slots. Dispatch failures reinsert the task and stop the batch, potentially limiting progress. A userspace scheduler crash can affect unrestricted task scheduling.

Test signals: successful run prints BPF enqueue and userspace vruntime counters. Changing `-b` should alter dispatch batch behavior. Under mixed affinity workloads, kernel and user enqueue counters should both move. `UEI_ECODE_RESTART()` should tear down and re-bootstrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_userland.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_userland.h -->
# sources/distributed-fs/ceph-client/tools/sched_ext/scx_userland.h

Purpose: shared header for the userland sched_ext example, defining the message payload sent from BPF to userspace.

Important APIs, types, and functions: defines `struct scx_userland_enqueued_task` with `pid`, `sum_exec_runtime`, and `weight`. There are no functions.

Control flow: BPF fills this structure in `enqueue_task_in_user_space()` and pushes it onto the `enqueued` BPF queue map. Userspace reads the same structure in `drain_enqueued_map()` and uses it to update its per-PID vruntime state.

State and persistence: each record is transient queue data. `sum_exec_runtime` and `weight` are snapshots from the kernel at enqueue time; userspace persists derived vruntime in its own task array.

Dependencies and integration points: must compile in both BPF and userspace contexts, so it relies on available integer aliases such as `__s32` and `u64` from included sched_ext/libbpf headers. Layout compatibility with the BPF queue map is critical.

Risks: adding fields or changing types requires updating BPF map value size and userspace consumers together. The record uses PID rather than a stable task reference, so consumers must tolerate exit and reuse races.

Test signals: skeleton generation and queue map operations validate layout. Userspace counters increasing after BPF enqueues confirm producer/consumer agreement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_userland.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/scripts/utilities.mak -->
# sources/distributed-fs/ceph-client/tools/scripts/utilities.mak

Purpose: GNU make utility library for string/newline escaping, shell quoting, executable discovery, and three-component version comparison.

Important APIs, types, and functions: defines the `newline` variable, `nl-escape`, `escape-nl`, `unescape-nl`, `shell-escape-nl`, `shell-unescape-nl`, `escape-for-shell-sq`, `shell-sq`, `shell-wordify`, `_sw-esc-nl`, `is-absolute`, `lookup`, `is-executable`, `get-executable`, `get-executable-or-default`, `_ge_attempt`, `_gea_err`, `version-ge3`, and `version-lt3`.

Control flow: these are make-expanded functions. Newline utilities replace embedded newlines with a sentinel before passing through contexts such as `$(shell ...)` that collapse output newlines, then restore them later. Shell quoting helpers produce single-quoted shell words or command substitutions for multi-line text. Executable helpers decide whether a path is absolute, use `command -v` through `sh -c` for relative names, validate executable files, and emit make errors for missing required tools. Version helpers encode `major.minor.patch` triples into comparable integers with awk.

State and persistence: no persistent state beyond make variables and function expansions. The default newline sentinel is a long unusual string intended to avoid collisions.

Dependencies and integration points: depends on GNU make features, POSIX shell, `awk`, `grep`, `test`, and `command -v`. It is meant to be included by other kernel tools makefiles.

Risks: quoting helpers are sensitive to shell quoting and sentinel collisions. Some functions use helper macros without explicitly passing arguments in the local call sites, relying on make's expansion context; changes can easily break them. Version comparison assumes exactly three numeric components. The comments note bash brace-expansion pitfalls around awk.

Test signals: makefile users can validate by round-tripping multi-line variables, resolving absolute and PATH executables, and comparing known version triples such as 2.6.4 >= 2.6.2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/scripts/utilities.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sound/dapm-graph -->
# sources/distributed-fs/ceph-client/tools/sound/dapm-graph

Purpose: shell tool that converts ALSA ASoC DAPM debugfs state into a Graphviz dot graph, optionally rendering it to an image format.

Important APIs, types, and functions: functions are `usage()`, `grab_remote_files()`, `process_dapm_widget()`, `process_dapm_component()`, `process_dapm_tree()`, and `main()`. Style variables define colors and node attributes for powered/unpowered components and widgets. The tool supports local card debugfs (`-c`), remote collection over ssh/scp (`-c` plus `-r`), or a local debugfs mirror (`-d`), with `-o` output and `-D` debug logging.

Control flow: `main()` validates exactly one input mode, creates a temporary directory, optionally collects remote debugfs files into a tarball because direct recursive scp would copy empty debugfs files, then calls `process_dapm_tree()`. The tree processor writes a dot header, processes the root card DAPM directory and each component `*/dapm`, and appends widget nodes plus input-link edges. Widget parsing reads the first line for power state, scans for `widget-type` and `in` routes, and writes dot node/edge records. The final dot file is copied to the requested `.dot` path or rendered with `dot -T<ext>`.

State and persistence: persistent output is the dot file and optional rendered file. Temporary state lives under `mktemp -d` and is removed on INT/TERM/EXIT. Debugfs state is read-only except remote commands create temporary copies on the target path supplied by `tmp_dir`.

Dependencies and integration points: depends on `/sys/kernel/debug/asoc/<card>`, shell utilities (`find`, `tar`, `awk`, `sed`, `grep`, `basename`), ssh/scp for remote mode, and Graphviz `dot` for non-dot output. It integrates with ASoC DAPM debugfs file formats.

Risks: widget and route parsing is text-format sensitive and only escapes newline labels via a `%` placeholder, not general Graphviz special characters. The `usage` call on missing output extension is invoked without an explicit status in one path. Remote collection assumes the local temp path is also valid on the remote target. The `for w_file in ${c_dir}/*` loop can mis-handle names with whitespace.

Test signals: with a saved debugfs tree, `-d <tree> -o dapm.dot` should produce valid dot. Non-dot output should also create the dot sidecar and rendered image. Debug mode should list components, widget types, and routes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sound/dapm-graph -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/spi/Makefile -->
# sources/distributed-fs/ceph-client/tools/spi/Makefile

Purpose: builds, cleans, and installs the SPI userspace test utilities `spidev_test` and `spidev_fdx`.

Important APIs, types, and functions: variables include `bindir`, `srctree`, `CFLAGS`, `ALL_TARGETS`, `ALL_PROGRAMS`, `SPIDEV_TEST_IN`, and `SPIDEV_FDX_IN`. Targets are `all`, `prepare`, object aggregation targets, final program link targets, `clean`, `install`, and `FORCE`.

Control flow: if `srctree` is unset, it is inferred two directories above `CURDIR`. Built-in make rules are disabled with `MAKEFLAGS += -r`. `prepare` creates `$(OUTPUT)include/linux/spi` and symlinks UAPI SPI headers from the kernel tree so the utilities can build outside the source tree. Per-program intermediate objects are produced through `tools/build/Makefile.include`; final binaries are linked with `$(CC)`. `install` copies built programs into `$(DESTDIR)$(bindir)`.

State and persistence: generated binaries and object/dependency/cmd files live under `$(OUTPUT)` when set, otherwise the source directory. Header symlinks are generated under `$(OUTPUT)include/`. `clean` removes binaries, generated include directory, and object/dependency artifacts.

Dependencies and integration points: depends on kernel tools build infrastructure, UAPI SPI headers, GNU make, compiler/linker variables, and `../scripts/Makefile.include`.

Risks: symlink target `$@` is the directory path, so the commands rely on `ln -sf <file> <dir>` semantics. In-source builds can delete matching object files under the current directory. Header symlinks can become stale if the source tree moves.

Test signals: `make -C tools/spi` should produce `spidev_test` and `spidev_fdx`; `make install DESTDIR=...` should install both. `make clean` should remove generated include links and build outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/spi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/spi/spidev_fdx.c -->
# sources/distributed-fs/ceph-client/tools/spi/spidev_fdx.c

Purpose: small spidev full-duplex/read utility for inspecting SPI device settings, issuing a two-transfer SPI message, and reading bytes.

Important APIs, types, and functions: functions are `do_read()`, `do_msg()`, `dumpstat()`, and `main()`. It uses `open()`, `read()`, `ioctl()`, `SPI_IOC_MESSAGE(2)`, `SPI_IOC_RD_MODE32`, `SPI_IOC_RD_LSB_FIRST`, `SPI_IOC_RD_BITS_PER_WORD`, and `SPI_IOC_RD_MAX_SPEED_HZ`.

Control flow: `main()` parses `-m N`, `-r N`, `-v`, and `-h`, requires one `/dev/spidevB.D` path, opens it read/write, prints current SPI settings with `dumpstat()`, optionally sends a two-part message where byte `0xaa` is transmitted before receiving `N` bytes, optionally performs a direct read of `N` bytes, then closes the device.

State and persistence: process state is limited to parsed counts and an unused `verbose` flag. It does not modify device mode or speed; it only reads settings and performs transfers. Buffers are fixed 32-byte stack arrays, and requested lengths are clamped.

Dependencies and integration points: depends on Linux spidev UAPI and a device node backed by an SPI controller/driver. Output is raw hex for simple manual inspection.

Risks: no mode setup means behavior depends entirely on prior device configuration. `do_msg()` transmits only one command byte and then receives into the same buffer; device protocols needing chip-select changes or more setup are unsupported. `verbose` is parsed but not used. Direct `read()` support depends on the spidev driver and target device behavior.

Test signals: `spidev_fdx /dev/spidevX.Y` should print settings. `-m` should show a response from `SPI_IOC_MESSAGE`; `-r` should show direct read bytes or a short-read diagnostic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/spi/spidev_fdx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/spi/spidev_test.c -->
# sources/distributed-fs/ceph-client/tools/spi/spidev_test.c

Purpose: feature-rich spidev test utility for configuring SPI mode parameters and transferring default, escaped-string, file, or random buffers.

Important APIs, types, and functions: global options cover device, mode bits, speed, bits per word, delays, input/output files, transfer size, iterations, and verbosity. Functions include `hex_dump()`, `unescape()`, `transfer()`, `print_usage()`, `parse_opts()`, `transfer_escaped_string()`, `transfer_file()`, `show_transfer_rate()`, `transfer_buf()`, and `main()`. It uses `SPI_IOC_WR/RD_MODE32`, `SPI_IOC_WR/RD_BITS_PER_WORD`, `SPI_IOC_WR/RD_MAX_SPEED_HZ`, and `SPI_IOC_MESSAGE(1)`.

Control flow: `parse_opts()` maps short/long CLI options to mode flags such as CPHA/CPOL, loopback, dual/quad/octal, 3-wire, LSB-first, no-CS, ready, and MOSI idle. `main()` opens the device, writes and reads back mode/bits/speed, warns if the driver dropped requested mode bits, then selects one transfer path: escaped string (`-p`), input file (`-i`), random repeated buffers (`-S` with `-I`), or a built-in SD-card-like default sequence. `transfer()` builds `spi_ioc_transfer`, configures multi-lane tx/rx nbits, suppresses incompatible rx/tx buffers outside loopback, performs the ioctl, optionally writes received bytes to output file, and hex-dumps when verbose.

State and persistence: configuration globals hold the requested settings. `_read_count` and `_write_count` accumulate transfer-rate stats in random-buffer mode. Output file contents are persistent if `-o` is used; device configuration may persist according to spidev driver semantics.

Dependencies and integration points: depends on Linux spidev UAPI, getopt_long, and an SPI controller supporting the requested mode bits. It is built by `tools/spi/Makefile`.

Risks: many numeric options use `atoi()` without range validation. `iterations` defaults to zero, so `-S` without `-I` performs no transfers. `unescape()` assumes `\xNN` has two hex digits and advances four characters. Large input files allocate full-size tx/rx buffers. The code casts away `const` for rx pointer in `transfer()` but only writes through the kernel ioctl.

Test signals: readback prints the actual mode, bits, and speed. Loopback mode should validate random buffers and exit on mismatch. Verbose mode should dump TX/RX. Unsupported mode bits should produce the warning comparing requested and actual mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/spi/spidev_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/crypto/chacha20-s390/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/crypto/chacha20-s390/Makefile

Purpose: Kbuild wrapper for compiling the `test_cipher` kernel module used to compare generic, s390, and library ChaCha20 implementations.

Important APIs, types, and functions: sets `obj-m += test_cipher.o` and maps `test_cipher-y := test-cipher.o`. Targets `all` and `clean` invoke the running kernel build directory with `M=$(PWD)`.

Control flow: `make` builds an external module against `/lib/modules/$(uname -r)/build`; `make clean` asks that same kernel build tree to clean module artifacts.

State and persistence: generated module artifacts remain in the current directory until cleaned.

Dependencies and integration points: depends on an installed kernel build tree and headers matching the running kernel. It integrates with `run-tests.sh`, which expects `test_cipher.ko`.

Risks: hard-wires the running kernel rather than an explicit target kernel, so cross-builds or alternate test kernels require overriding the invocation manually. The object/module name differs in hyphen/underscore form, which is normal for Kbuild but worth preserving.

Test signals: successful build produces `test_cipher.ko`; clean removes module outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/crypto/chacha20-s390/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/crypto/chacha20-s390/run-tests.sh -->
# sources/distributed-fs/ceph-client/tools/testing/crypto/chacha20-s390/run-tests.sh

Purpose: root-side script that loads ChaCha20 implementations and repeatedly inserts the test module with varied plaintext sizes to exercise s390 ChaCha20 paths.

Important APIs, types, and functions: uses `lsmod`, `rmmod`, `modprobe chacha_generic`, `modprobe chacha_s390`, repeated `insmod test_cipher.ko size=<N>`, and `dmesg | tail -170`.

Control flow: removes currently loaded modules whose names match `chacha`, loads generic and s390 modules, inserts the test module for block-boundary sizes and large sizes, then prints recent kernel logs. The comments note that `insmod` failure is expected because the module init returns failure after running tests.

State and persistence: modifies loaded kernel modules and kernel log state. It does not keep local files except module build products produced elsewhere.

Dependencies and integration points: depends on root privileges, s390 ChaCha module availability, and `test_cipher.ko` in the working directory. It is paired with `test-cipher.c`.

Risks: `lsmod | grep chacha | xargs rmmod` can pass no arguments or remove broader modules than intended. There is no `set -e`, so failures may be obscured. It assumes dmesg access and sufficient permissions.

Test signals: dmesg should contain OK/FAILED comparison lines and timing for generic, s390, and library encryption/decryption across the tested sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/crypto/chacha20-s390/run-tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/crypto/chacha20-s390/test-cipher.c -->
# sources/distributed-fs/ceph-client/tools/testing/crypto/chacha20-s390/test-cipher.c

Purpose: kernel module self-test that compares `chacha20-generic`, `chacha20-s390`, and `chacha_crypt_arch()` outputs and decryptability for a configurable data size.

Important APIs, types, and functions: defines module parameters `size` and `debug`, `struct skcipher_def`, `test_lib_chacha()`, `test_skcipher_encdec()`, `test_skcipher()`, module init `chacha_s390_test_init()`, and exit `chacha_s390_test_exit()`. It uses crypto skcipher APIs, `chacha_init()`, `chacha_crypt_arch()`, scatterlists, `crypto_wait_req()`, `ktime_get_ns()`, vmalloc/vfree, and optional `print_hex_dump()`.

Control flow: init allocates plaintext, generic cipher, s390 cipher, and revert buffers; fills plaintext with mostly random first bytes; encrypts/decrypts through `chacha20-generic` and verifies plaintext recovery; repeats with `chacha20-s390`; compares generic and s390 ciphertext; then runs the low-level library implementation and compares recovery and ciphertext against generic. It prints timing for each encryption/decryption. The init function returns `-1` intentionally after freeing buffers so `insmod` unloads while still executing the test.

State and persistence: all buffers are transient. Module parameters determine data size and debug dumping. Kernel logs preserve test results.

Dependencies and integration points: depends on the kernel crypto API, s390 ChaCha implementation availability, and module loading. `run-tests.sh` drives multiple sizes.

Risks: returning `-1` is intentional but looks like load failure to automation. Large sizes allocate multiple vmalloc buffers and can stress memory. Fixed key/IV are test-only. Include list is broad, increasing compile sensitivity. The library path uses architecture implementation through `chacha_crypt_arch()`, so availability and behavior are architecture-dependent.

Test signals: dmesg should report generic, s390, and library en/decryption checks OK plus s390-vs-generic and lib-vs-generic OK. Any memcmp failure or crypto allocation error is a clear regression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/crypto/chacha20-s390/test-cipher.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/Kbuild -->
# sources/distributed-fs/ceph-client/tools/testing/cxl/Kbuild

Purpose: top-level Kbuild file for CXL test modules, compiling selected production CXL/DAX sources together with mock wrappers and test-specific watermarks.

Important APIs, types, and functions: uses linker `--wrap` flags for ACPI, CXL, nvdimm, hmem, and region functions. Defines source roots `DRIVERS`, `DAX_HMEM_SRC`, `CXL_SRC`, and `CXL_CORE_SRC`; adds include paths and `-D__mock=__weak`, `-DCXL_TEST_ENABLE=1`, and trace include path. Builds modules `cxl_acpi`, `cxl_pmem`, `cxl_port`, `cxl_mem`, `cxl_core`, `dax_hmem`, and recurses into `test/`.

Control flow: Kbuild composes each module from production driver files plus `config_check.c` and a module-specific watermark file. The `cxl_core` module includes core CXL objects conditional on Kconfig symbols. Linker wrapping redirects selected external symbols to `__wrap_*` functions implemented in `test/mock.c`.

State and persistence: no runtime state here; it determines module link composition and symbol interposition.

Dependencies and integration points: depends on kernel CXL, ACPI, dax/hmem, libnvdimm, tracing, and region Kconfig. It must be kept synchronized with production driver file names and wrapped symbol signatures.

Risks: stale `--wrap` entries or production source lists can break builds or silently stop mocking a path. Conditional core object inclusion must match exported symbols expected by tests. `KBUILD_CFLAGS` filters missing prototype/declaration warnings, which can hide interface drift.

Test signals: all CXL test modules should build as modules. Loading `cxl_test` should call watermarks from these mocked modules, proving the test linked against the intended objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/config_check.c -->
# sources/distributed-fs/ceph-client/tools/testing/cxl/config_check.c

Purpose: compile-time guard ensuring the kernel configuration supports the CXL test modules.

Important APIs, types, and functions: defines `check()` containing `BUILD_BUG_ON()` assertions for `CONFIG_64BIT`, CXL bus/acpi/pmem as modules, CXL region invalidation test, NVDIMM security test, debugfs, and memory hotplug.

Control flow: there is no runtime logic beyond the function body; Kbuild includes this object in multiple CXL test modules so build fails if required symbols are not configured.

State and persistence: none.

Dependencies and integration points: depends on Kconfig macros and `<linux/bug.h>`. It integrates with each mocked CXL module through Kbuild inclusion.

Risks: requirements are intentionally strict. If a valid new test configuration differs, this file must be updated or the build will fail. Because `check()` itself is not called, its value is in compile-time expression checking.

Test signals: a successful module build means required config predicates passed. Build failures identify missing module/test/debugfs/hotplug support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/config_check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/cxl_acpi_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/cxl/cxl_acpi_test.c

Purpose: watermark object for the mocked `cxl_acpi` module.

Important APIs, types, and functions: includes `watermark.h` and expands `cxl_test_watermark(cxl_acpi)` to define and export `cxl_acpi_test()`.

Control flow: callers invoke `cxl_acpi_test()` from `cxl_test_init()` to confirm the mocked module is linked/loaded. The function logs a debug message and returns zero.

State and persistence: none.

Dependencies and integration points: depends on `watermark.h` and is included in the `cxl_acpi-y` module composition.

Risks: if omitted or linked against the wrong module, `cxl_test` may fail to resolve or may not validate the intended mocked path.

Test signals: successful call from `cxl_test_init()` and resolved exported symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/cxl_acpi_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/cxl_core_exports.c -->
# sources/distributed-fs/ceph-client/tools/testing/cxl/cxl_core_exports.c

Purpose: exports CXL core symbols needed only by the test environment.

Important APIs, types, and functions: includes `cxl.h` and exports `cxl_num_decoders_committed` in namespace `CXL` with `EXPORT_SYMBOL_NS_GPL`.

Control flow: no runtime control flow; it makes an otherwise internal core helper available to CXL test modules.

State and persistence: none.

Dependencies and integration points: part of the mocked `cxl_core` module; consumed by `tools/testing/cxl/test/cxl.c` decoder commit/reset emulation.

Risks: exporting test-only internals can mask production encapsulation assumptions if used outside tests. Namespace and symbol name must track CXL core changes.

Test signals: modules using `cxl_num_decoders_committed()` should link and load with `MODULE_IMPORT_NS("CXL")`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/cxl_core_exports.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/cxl_core_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/cxl/cxl_core_test.c

Purpose: watermark object for the mocked `cxl_core` module.

Important APIs, types, and functions: expands `cxl_test_watermark(cxl_core)` to export `cxl_core_test()`.

Control flow: `cxl_test_init()` calls the function to validate test linkage; it logs debug output and returns zero.

State and persistence: none.

Dependencies and integration points: depends on `watermark.h`; linked into `cxl_core-y`.

Risks: minimal, but missing export breaks the setup module's linkage validation.

Test signals: exported `cxl_core_test()` resolves and returns zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/cxl_core_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/cxl_mem_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/cxl/cxl_mem_test.c

Purpose: watermark object for the mocked `cxl_mem` module.

Important APIs, types, and functions: expands `cxl_test_watermark(cxl_mem)` to define and export `cxl_mem_test()`.

Control flow: called from `cxl_test_init()` to prove that the test setup sees the mocked memory module, then returns zero.

State and persistence: none.

Dependencies and integration points: included in the `cxl_mem-y` module recipe.

Risks: missing or wrong symbol indicates the cxl_test module is not testing the intended module composition.

Test signals: successful symbol resolution and debug watermark message.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/cxl_mem_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/cxl_pmem_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/cxl/cxl_pmem_test.c

Purpose: watermark object for the mocked `cxl_pmem` module.

Important APIs, types, and functions: expands `cxl_test_watermark(cxl_pmem)` to export `cxl_pmem_test()`.

Control flow: invoked during CXL test setup to confirm the pmem module participating in the test is the mocked build.

State and persistence: none.

Dependencies and integration points: linked into `cxl_pmem-y` with production pmem/security sources and `config_check.c`.

Risks: low; its absence or wrong namespace breaks test validation.

Test signals: exported function resolves and logs debug watermark when called.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/cxl_pmem_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/cxl_port_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/cxl/cxl_port_test.c

Purpose: watermark object for the mocked `cxl_port` module.

Important APIs, types, and functions: expands `cxl_test_watermark(cxl_port)` to export `cxl_port_test()`.

Control flow: called from `cxl_test_init()` as part of linkage validation.

State and persistence: none.

Dependencies and integration points: linked into `cxl_port-y`.

Risks: only build/link risk if production/test module composition changes.

Test signals: successful load and callable `cxl_port_test()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/cxl_port_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/mock_acpi.c -->
# sources/distributed-fs/ceph-client/tools/testing/cxl/mock_acpi.c

Purpose: overrides CXL host-bridge discovery for mocked ACPI/platform devices.

Important APIs, types, and functions: defines `to_cxl_host_bridge(struct device *host, struct device *dev)`. It uses `get_cxl_mock_ops()`, `put_cxl_mock_ops()`, `ops->is_mock_bridge()`, `ACPI_COMPANION()`, `dev_is_platform()`, `to_acpi_device()`, `acpi_pci_find_root()`, and ACPI HID comparison to `"ACPI0016"`.

Control flow: obtains registered mock ops under SRCU. If a mock ops provider exists and marks the device as a mock bridge, the function returns the device's ACPI companion. Platform devices that are not mock bridges are ignored. For real ACPI devices, it checks that the device has a PCI root and HID `ACPI0016`, logs a debug message, and returns it. The mock ops reference is released before return.

State and persistence: no local persistent state; it consults the global mock-ops registry.

Dependencies and integration points: compiled into the mocked `cxl_acpi` module and works with `test/mock.c` operations supplied by `test/cxl.c`. It intercepts host bridge discovery in the production ACPI CXL driver path.

Risks: assumes mock bridge devices have a valid ACPI companion. If `dev_is_platform()` filters new legitimate cases, discovery can fail. Mock ops must remain registered while discovery runs; SRCU protects this.

Test signals: mock host bridges should be discovered as CXL host bridges during `cxl_test` topology enumeration. Real ACPI `ACPI0016` devices should still fall back to normal logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/mock_acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/test/Kbuild -->
# sources/distributed-fs/ceph-client/tools/testing/cxl/test/Kbuild

Purpose: Kbuild file for the CXL test-side setup, mock dispatcher, mock memory device, and translation test modules.

Important APIs, types, and functions: adds include paths for `drivers/cxl` and `drivers/cxl/core`. Builds `cxl_test.o` from `cxl.o` and `hmem_test.o`, `cxl_mock.o` from `mock.o`, `cxl_mock_mem.o` from `mem.o`, and standalone `cxl_translate.o`. Filters missing prototype/declaration warnings.

Control flow: Kbuild compiles these modules under the top-level CXL testing Kbuild. `cxl_mock` provides wrapped-symbol dispatch; `cxl_test` creates platform topology; `cxl_mock_mem` probes fake memory devices; `cxl_translate` tests address translation helpers.

State and persistence: no runtime state in the build file.

Dependencies and integration points: depends on the top-level Kbuild's wrapped symbol setup and CXL driver headers.

Risks: module names and split object lists must stay synchronized with source files and symbols expected by wrapper code. Warning filtering can hide interface drift.

Test signals: `make M=tools/testing/cxl` should emit all four test modules from this directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/test/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/test/cxl.c -->
# sources/distributed-fs/ceph-client/tools/testing/cxl/test/cxl.c

Purpose: main CXL test setup module that constructs fake CXL platform topology, mock ACPI CEDT tables, decoder emulation, CXL memory devices, optional hmem resources, and mock operations consumed by wrapper functions.

Important APIs, types, and functions: module parameters include `interleave_arithmetic`, `extended_linear_cache`, and `fail_autoassemble`. Major state includes platform device arrays for host bridges, root ports, switch ports, memory devices, RCH/RCD devices, `mock_cedt`, `mock_cfmws`, `mock_cxims`, `cxl_mock_pool`, `mock_res`, and `decoder_registry`. Key functions include mock classifiers (`is_mock_dev`, `is_mock_adev`, `is_mock_bridge`, `is_mock_port`, `is_mock_bus`), ACPI callbacks (`mock_acpi_table_parse_cedt`, `mock_acpi_evaluate_integer`, `mock_acpi_pci_find_root`), decoder helpers (`mock_cxl_setup_hdm`, `mock_cxl_enumerate_decoders`, `mock_init_hdm_decoder`, `mock_decoder_commit`, `mock_decoder_reset`), resource hooks (`mock_walk_hmem_resources`, `mock_region_intersects`, `mock_region_intersects_soft_reserve`), topology init/exit functions, and `cxl_test_init()`/`cxl_test_exit()`.

Control flow: module init validates mocked module watermarks, registers `cxl_mock_ops`, creates a gen_pool near the top of pluggable memory, selects modulo or XOR CFMWS windows, allocates CHBS/CFMWS resources, creates multi-host bridge topology, root ports, switch upstream/downstream ports, a single-host topology, RCH topology, the `cxl_acpi` platform device with sysfs attributes, then memory devices and optional hmem test device. Wrapped production code calls into mock ops for ACPI table parsing, PCI root discovery, decoder setup, dport lookup, CDAT parsing, hmem walking, and region intersections. Exit tears down in reverse, frees resources, unregisters ops, and destroys the decoder registry.

State and persistence: platform devices and ACPI companion fwnodes persist while the module is loaded. The decoder registry is an xarray keyed by stable upstream port device pointer plus decoder id; it preserves enabled decoder programming across cxl_acpi unbind/bind and supports a sysfs `decoder_reset_preserve_registry` flag. Mock resource allocations are tracked in a list and returned to `gen_pool` on exit.

Dependencies and integration points: integrates deeply with CXL core APIs, ACPI CEDT parsing, platform bus, genalloc, memory hotplug ranges, CXL decoder APIs, CDAT/performance APIs, dax/hmem hooks, and wrapper dispatch from `mock.c`.

Risks: topology setup has many partial-failure unwind paths; ordering bugs can leak devices or leave stale sysfs links. Decoder replay keys rely on `port->uport_dev` pointer stability and id < 16. Mock CEDT table layouts and context hacks assume production CXL parser internals. Auto-region behavior is specialized to selected mock memory IDs. Resource allocation near high physical memory depends on system memory layout.

Test signals: loading the module should enumerate fake host bridges, ports, decoders, memdevs, and optional hmem resources. CXL tools should see auto-assembled regions unless `fail_autoassemble` is set. Unbind/rebind of `cxl_acpi` should replay committed decoder state. XOR mode should expose XOR CFMWS/CXIMS tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/test/cxl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/test/cxl_translate.c -->
# sources/distributed-fs/ceph-client/tools/testing/cxl/test/cxl_translate.c

Purpose: kernel module test for CXL address translation helpers, covering DPA-to-HPA, HPA-to-DPA, interleave position extraction, XOR interleave mapping, random round trips, and parameter validation.

Important APIs, types, and functions: module parameter array `table` accepts up to 128 space-separated test vectors. Key functions are `to_hpa()`, `to_dpa()`, `to_pos()`, `run_translation_test()`, `parse_test_vector()`, `setup_xor_mapping()`, `test_random_params()`, `test_cxl_validate_translation_params()`, `cxl_translate_init()`, and `cxl_translate_exit()`. It calls CXL helpers `cxl_calculate_hpa_offset()`, `cxl_calculate_dpa_offset()`, `cxl_calculate_position()`, `cxl_do_xormap_calc()`, `cxl_validate_translation_params()`, and `eiw_to_ways()`.

Control flow: if no `table` entries are supplied, init runs internal validation: fixed valid/invalid encoded interleave parameter tests and 10,000 random round-trip modulo translation checks. If table entries are supplied, it allocates static XOR map data, parses each vector as `dpa pos r_eiw r_eig hb_ways math expect_hpa`, runs forward and reverse translations, logs pass/fail per vector, frees XOR state, and returns success from module init.

State and persistence: `cximsd` is allocated only for table-driven tests and freed before init returns. Module parameters persist in module state while loaded. No sysfs attributes beyond module params.

Dependencies and integration points: depends on CXL core translation APIs and namespace import `CXL`. It is built as `cxl_translate` from the CXL test Kbuild.

Risks: table-driven test failures are logged but do not cause a nonzero module init return after processing all entries, so automation must inspect logs. XOR maps are static and comments note they must change for new datasets. Random test only covers modulo helpers and uses shifted random DPA values.

Test signals: no-param load should print internal validation success. Table loads should print PASS per vector and detailed errors on mismatch. Parameter validation failures should return negative errors in no-param mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/test/cxl_translate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/test/hmem_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/cxl/test/hmem_test.c

Purpose: optional hmem platform-device stub used by CXL tests to exercise dax_hmem integration.

Important APIs, types, and functions: module parameter `hmem_test` gates registration. Defines empty `hmem_test_work()`, `hmem_test_release()`, static `hmem_test_device`, `hmem_test_init()`, and `hmem_test_exit()`.

Control flow: `hmem_test_init()` returns zero without action unless the module parameter is true; when enabled it registers `hmem_platform.1`. `hmem_test_exit()` unregisters it only when enabled. The release callback clears the static device structure after unregister.

State and persistence: the static `hmem_platform_device` persists for the module lifetime. Registering it creates a platform device with initialized work item and release callback.

Dependencies and integration points: includes DAX bus internals and integrates with wrapped `walk_hmem_resources()` in `mock.c`/`cxl.c`, which recognizes `hmem_platform.1`.

Risks: the release callback `memset()` on a static object means re-registration after release depends on module lifecycle and reinitialization. The work function is intentionally empty.

Test signals: with `hmem_test=1`, a platform device named `hmem_platform.1` should exist and trigger the mock hmem resource path; without it, no device is registered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/test/hmem_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/test/mem.c -->
# sources/distributed-fs/ceph-client/tools/testing/cxl/test/mem.c

Purpose: mock CXL memory-device platform driver that emulates a CXL mailbox, events, label storage, security, poison injection, firmware update, features, and memdev registration for the CXL test topology.

Important APIs, types, and functions: constants define LSA, firmware, slot, and device capacities. `mock_cel` advertises supported command effects. `struct cxl_mockmem_data` stores LSA/FW buffers, FW slots, security state/passphrases/limits, event store, memdev state, timestamp, sanitize timeout, vendor test feature, and shutdown state. Command handlers include `mock_gsl`, `mock_get_log`, `mock_id`, `mock_rcd_id`, `mock_partition_info`, event handlers, security handlers, LSA handlers, health/shutdown handlers, poison handlers, firmware handlers, feature handlers, and dispatcher `cxl_mock_mbox_send()`. Probe path is `cxl_mock_mem_probe()`.

Control flow: probing sleeps briefly to widen async race windows, allocates managed mock data plus vmalloc LSA/FW buffers, creates CXL memdev state and mailbox, installs `cxl_mock_mbox_send`, initializes event buffer and delayed sanitize work, marks RCD devices, enumerates commands from the CEL, initializes poison/timestamp/identify/DPA/features, seeds event logs, registers a CXL memdev, sets up firmware upload, sanitize notifier, and optional fwctl, drains initial events, and initializes the vendor feature. Mailbox commands are switched by opcode and routed to mock handlers that validate payload sizes, mutate mock state, and set CXL return codes when needed.

State and persistence: each platform device owns `cxl_mockmem_data`. LSA contents, firmware buffer/checksum, selected/staged slots, security passphrases/lock/freeze/try-limit flags, event cursors, sanitize-active delayed work, shutdown state, and vendor feature data persist while the device exists. Poison state is a global fixed array keyed by `struct cxl_dev_state *`, with driver sysfs control for per-device injection max. Sysfs attributes expose `security_lock`, `event_trigger`, `fw_buf_checksum`, and `sanitize_timeout`.

Dependencies and integration points: depends on CXL mailbox/memdev APIs, crypto SHA-256, platform driver infrastructure, trace header, firmware upload/sanitize/fwctl helpers, and namespace `CXL`. It is instantiated by platform devices from `test/cxl.c`.

Risks: large and stateful emulation must track evolving CXL command structs and return-code semantics. Some commands deliberately emulate only enough behavior for tests. Global poison state must be empty before changing injection max. Security flows are complex and spec comments identify ambiguous cases. `cmd->size_out` expectations vary by command, so ABI drift can break tests.

Test signals: CXL tools should enumerate mock memdevs with CEL, LSA, partition, poison, FW, feature, health, and event support. Event trigger sysfs should regenerate event reads. Security sysfs plus mailbox commands should exercise passphrase limits and lock/unlock. FW upload should change checksum and slot state. Poison inject/clear/get should reflect mock list updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/test/mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/test/mock.c -->
# sources/distributed-fs/ceph-client/tools/testing/cxl/test/mock.c

Purpose: central wrapper dispatch module that lets CXL tests interpose selected ACPI, CXL, nvdimm, hmem, and region APIs with mock behavior.

Important APIs, types, and functions: maintains an SRCU-protected global `mock` list of `struct cxl_mock_ops`. Exports `register_cxl_mock_ops()`, `unregister_cxl_mock_ops()`, `get_cxl_mock_ops()`, and `put_cxl_mock_ops()`. Defines many `__wrap_*` functions: `is_acpi_device_node`, `acpi_table_parse_cedt`, `acpi_evaluate_integer`, `hmat_get_extended_linear_cache_size`, `acpi_pci_find_root`, `nvdimm_bus_register`, CXL decoder/dport/CDAT/media-ready helpers, `region_intersects`, `region_intersects_soft_reserve`, and `walk_hmem_resources`.

Control flow: wrapped functions acquire the current ops pointer with SRCU, decide whether the object belongs to the mock topology using ops predicates, call the mock implementation when applicable, otherwise call the real function, then release SRCU. Some wrappers augment real behavior, such as setting nvdimm provider name to `cxl_test` for mock parents or converting RCH dport creation into generic dport creation plus RCH metadata.

State and persistence: global list currently returns the first registered ops provider. SRCU protects readers across unregister. The module itself holds no per-device state.

Dependencies and integration points: requires top-level Kbuild linker `--wrap` flags so calls resolve to these functions. It imports ACPI and CXL namespaces and depends on CXL core, ACPI, PCI, hmem, libnvdimm, and resource APIs. `test/cxl.c` registers the concrete ops.

Risks: only one ops provider is effectively used despite list structure. Wrapper signatures must exactly track wrapped functions. Several wrappers assume object relationships, e.g. `dev->parent->parent` in nvdimm bus registration and memdev parent lookup in CDAT parsing. Missing fallback or wrong mock predicate can redirect real devices to test behavior or vice versa.

Test signals: loading `cxl_mock` plus `cxl_test` should cause production CXL drivers to consume mock CEDT/topology data. Removing ops should synchronize without use-after-free. Real paths should still fall back when devices are not mock-owned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/test/mock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/test/mock.h -->
# sources/distributed-fs/ceph-client/tools/testing/cxl/test/mock.h

Purpose: shared interface between the CXL mock dispatcher and concrete CXL test topology provider.

Important APIs, types, and functions: defines `struct cxl_mock_ops`, a callback table with predicates and mock implementations for ACPI device detection, CEDT parsing, bridge/bus/port/device classification, ACPI integer/root lookup, decoder setup, CDAT parsing, dport lookup, HMAT cache size, hmem resource walking, and region intersection tests. Declares hmem init/exit and mock ops registration/SRCU accessors.

Control flow: `test/cxl.c` fills a `cxl_mock_ops` instance and registers it. `test/mock.c` wrapper functions retrieve it and call the relevant callback.

State and persistence: the ops structure includes a `list_head` so providers can be linked into the global registry. Actual callback state is owned by the provider module.

Dependencies and integration points: includes Linux list, ACPI, DAX, and CXL headers. It is a contract between `mock.c`, `mock_acpi.c`, and `cxl.c`.

Risks: changes to wrapped production function signatures require corresponding callback changes. Several callbacks are optional only by convention; wrappers often assume non-null methods when ops exists.

Test signals: compile-time agreement between all CXL test modules and successful wrapper dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/test/mock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/watermark.h -->
# sources/distributed-fs/ceph-client/tools/testing/cxl/watermark.h

Purpose: helper macro for exporting module-specific watermark functions so `cxl_test` can verify it is linked against mocked CXL modules.

Important APIs, types, and functions: declares `cxl_acpi_test()`, `cxl_core_test()`, `cxl_mem_test()`, `cxl_pmem_test()`, and `cxl_port_test()`. Macro `cxl_test_watermark(x)` defines `x##_test()` to log a debug message containing `KBUILD_MODNAME`, return zero, and export the symbol.

Control flow: each small `*_test.c` file expands the macro. `cxl_test_init()` calls all watermark functions at load time.

State and persistence: none.

Dependencies and integration points: depends on module and printk headers. Integrated into mocked CXL modules through Kbuild.

Risks: the mechanism validates symbol presence, not complete behavioral correctness. Exported names must stay aligned with declarations and caller expectations.

Test signals: all five watermark functions resolve and return zero during `cxl_test` initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/cxl/watermark.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/fault-injection/failcmd.sh -->
# sources/distributed-fs/ceph-client/tools/testing/fault-injection/failcmd.sh

Purpose: root-only helper that runs a command with kernel slab or page-allocation fault injection enabled for that task.

Important APIs, types, and functions: functions are `usage()`, `exit_if_not_hex()`, `fault_attr_default()`, and `restore_values()`. It uses debugfs fault injection attributes under `$DEBUGFS/$FAILCMD_TYPE`, `/proc/sys/vm/oom_kill_allocating_task`, `getopt`, and `/proc/self/make-it-fail`. `FAILCMD_TYPE` selects `failslab` by default or `fail_page_alloc`.

Control flow: validates root and mounted debugfs, verifies the selected fault injector directory, builds long options based on injector type, parses options, resets default fault attributes, saves OOM setting, applies requested attributes, installs a trap to restore values, then runs `bash -c "echo 1 > /proc/self/make-it-fail && exec $@"` so the command's allocations are subject to task-filtered injection.

State and persistence: temporarily mutates global debugfs fault injection knobs and the VM OOM sysctl, then restores probability/times/task-filter and OOM setting on exit signals. The command itself may leave system state.

Dependencies and integration points: requires bash, root, mounted debugfs, kernel fault-injection support, and GNU `getopt`. Hex validation is applied to require/reject address range options.

Risks: global fault injection attributes can affect other tasks if task filtering is disabled or restore fails. The command construction via a string and `$@` can be fragile for complex arguments. `UID` should be available in bash; script declares bash shebang. It exits zero with no command after options, which may hide invocation mistakes.

Test signals: running a simple command should restore debugfs attributes afterward. With high probability/times, target allocations should fail and kernel fault-injection stats/logs should show activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/fault-injection/failcmd.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/compare-ktest-sample.pl -->
# sources/distributed-fs/ceph-client/tools/testing/ktest/compare-ktest-sample.pl

Purpose: maintenance script that compares option names used by `ktest.pl` with option names documented in `sample.conf`.

Important APIs, types, and functions: uses Perl hashes `%opt` and `%samp`. It scans `ktest.pl` for `$opt{...}`, hash key declarations, and `set_test_option("...")`; it scans `sample.conf` for uppercase assignment names.

Control flow: opens `ktest.pl`, records discovered option names; opens `sample.conf`, records documented/sample names; prints `opt = NAME` for implementation options missing from the sample and `samp = NAME` for sample entries not seen in implementation.

State and persistence: no file writes; output is diagnostic only.

Dependencies and integration points: assumes it is run from the ktest directory containing `ktest.pl` and `sample.conf`. Depends on Perl regex matching of current source style.

Risks: regexes can miss dynamically generated options or report false positives from comments/strings. It does not handle open failures explicitly. The comparison is name-only and does not validate semantics.

Test signals: a clean sync between script and sample should produce no output. New unmatched options should appear as `opt =` lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/compare-ktest-sample.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/config-bisect.pl -->
# sources/distributed-fs/ceph-client/tools/testing/ktest/config-bisect.pl

Purpose: Perl helper for bisecting kernel configuration differences between a known-good and known-bad `.config`, producing intermediate configs to test.

Important APIs, types, and functions: command options include `-l` linux tree, `-b` build dir, `-r` reset, and good/bad result labels. Utility functions include `usage()`, `run_command()`, prompt helpers, path expansion, config parsing/saving/comparison helpers, `make_oldconfig()`, `process_new_config()`, `make_half()`, `run_config_bisect()`, and `config_bisect()`.

Control flow: on a new run it copies input good/bad configs to `.tmp` files, optionally prompting before overwrite. On subsequent runs it copies the just-tested build `.config` to either good or bad `.tmp` based on the result label. It normalizes both configs through `make olddefconfig` with fallbacks to `oldnoconfig` or `yes '' | make oldconfig`, reads them into hashes, computes differences, attempts top or bottom halves of bad values into good config or good values into bad config, regenerates `.config`, and stops when it has a non-identical intermediate ready to test. If no further split is possible, it prints remaining differences and exits with failure.

State and persistence: persists bisection state in `<good>.tmp`, `<bad>.tmp`, and the build directory `.config`. It rewrites the temporary config files each run.

Dependencies and integration points: depends on Perl, kernel `make` config targets, a kernel tree/build dir, and user test feedback between runs. It is an adjunct to ktest/manual build bisection.

Risks: hash key order is unordered, so split halves may not be deterministic across Perl versions/settings. It may not isolate dependency-only differences well despite tracking configs that appear only in one file. It rewrites `.config` and temp files, so paths must not be the original only copies. Some variables (`config_ignore`, dependency helpers) are present but not fully used in the viewed control path.

Test signals: after initial invocation, the build `.config` should be ready to test and temp good/bad files should exist. Re-running with `good` or `bad` should narrow differences until a single or unsplittable set remains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/config-bisect.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/examples/bootconfigs/verify-boottrace.sh -->
# sources/distributed-fs/ceph-client/tools/testing/ktest/examples/bootconfigs/verify-boottrace.sh

Purpose: bootconfig verification script that checks a rich tracing setup under `/sys/kernel/tracing`.

Important APIs, types, and functions: helper functions `compare_file()`, `compare_file_partial()`, `file_contains()`, and `compare_mask()` validate exact values, prefix/regex partials, grep containment, and CPU masks. It checks task and kprobe event filters/enables, synthetic event triggers, histogram triggers, tracing instances `foo` and `bar`, snapshot allocation, tracer options, buffers, clocks, and global initcall enablement.

Control flow: changes to `/sys/kernel/tracing`, defines helpers, executes a linear sequence of assertions, prints a failure message and exits 1 on the first mismatch, otherwise exits 0.

State and persistence: no intentional writes. It reads tracefs/procfs state left by bootconfig.

Dependencies and integration points: depends on tracefs mounted at `/sys/kernel/tracing`, bootconfig having set the expected tracing state, and shell tools `cat`, `sed`, and `grep`. It is intended for ktest bootconfig examples.

Risks: exact string comparisons are sensitive to kernel formatting and tracefs representation changes. Some grep patterns are unquoted as filenames/values and could be brittle. CPU mask comparison accepts leading zero/space formatting but still expects specific masks.

Test signals: exit status 0 means the boottrace bootconfig applied all expected events, instances, hist triggers, clocks, masks, and options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/examples/bootconfigs/verify-boottrace.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/examples/bootconfigs/verify-functiongraph.sh -->
# sources/distributed-fs/ceph-client/tools/testing/ktest/examples/bootconfigs/verify-functiongraph.sh

Purpose: verifies a bootconfig scenario that enables function-graph tracing bounded by kprobe triggers.

Important APIs, types, and functions: helper functions match the boottrace verifier. Assertions check `tracing_on`, `current_tracer`, kprobe start/end event enables and triggers, and `kprobe_events` entries targeting `pci_proc_init`.

Control flow: changes to tracefs, defines helpers, checks that tracing starts off with `function_graph`, that a start kprobe has `traceon`, that an end return probe has `traceoff`, and exits 0 on success or 1 on first mismatch.

State and persistence: read-only verification of tracefs state.

Dependencies and integration points: requires tracefs, kprobe events, function_graph tracer, and a bootconfig that created `start_event` and `end_event`.

Risks: string and regex expectations are tightly coupled to tracefs output formatting and symbol naming. It assumes `/sys/kernel/tracing` exists.

Test signals: successful exit confirms the expected boot-time function graph setup is active and bounded by kprobe triggers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/examples/bootconfigs/verify-functiongraph.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/examples/bootconfigs/verify-tracing.sh -->
# sources/distributed-fs/ceph-client/tools/testing/ktest/examples/bootconfigs/verify-tracing.sh

Purpose: verifies a general tracing bootconfig setup, including global tracer options, event enables, kprobe instances, and kernel sysctls.

Important APIs, types, and functions: same helper assertion functions as the other bootconfig verifiers. Checks `function_graph`, `event-fork`, `sym-addr`, `stacktrace`, buffer size, snapshot, trace clock, initcall/task/sched/kprobe events, instance `bar` kprobe events, instance `foo` state, and proc sysctls `ftrace_dump_on_oops` and `traceoff_on_warning`.

Control flow: changes to tracefs and performs exact/partial/contains assertions in sequence, exiting 1 on failure and 0 on success.

State and persistence: reads tracefs and procfs only.

Dependencies and integration points: requires tracing bootconfig support, tracefs, kprobes, function_graph tracer, snapshots, and the expected proc sysctl state.

Risks: exact-value checks can fail due to kernel output changes even when semantics are equivalent. Hard-coded buffer sizes and clocks assume the example bootconfig and architecture behavior.

Test signals: exit 0 means the tracing bootconfig applied expected global and instance-specific tracing state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/examples/bootconfigs/verify-tracing.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/examples/crosstests.conf -->
# sources/distributed-fs/ceph-client/tools/testing/ktest/examples/crosstests.conf

Purpose: example `ktest.pl` configuration for cross-compiling many architectures with downloaded kernel.org crosstool toolchains.

Important APIs, types, and functions: defines ktest variables/options such as `THIS_DIR`, `BUILD_DIR`, `OUTPUT_DIR`, `BUILD_OPTIONS`, `DIE_ON_FAILURE`, `LOG_FILE`, `CLEAR_LOG`, `DO_FAILED`, `DO_DEFAULT`, `RUN`, `GCC_VER`, `MAKE_CMD`, `TEST_TYPE`, `BUILD_TYPE`, `TEST_NAME`, `CROSS`, and `ARCH`. It contains many `TEST_START IF ...` sections for alpha, arm, ia64, m68k, mips, parisc, powerpc, s390, sh, sparc, xtensa, UML, i386, x86_64, and a bisect example.

Control flow: ktest parses the file, expands variables, and creates build-only tests. Default tests run when `${DO_DEFAULT}` is true; known-failing tests are gated by `${DO_FAILED}` unless explicitly selected by `${RUN}`. Each section sets `CROSS` and `ARCH`, and the common `MAKE_CMD` uses the selected toolchain path. The final `DEFAULTS` block supplies required but unused boot/install/power options so ktest accepts build-only tests.

State and persistence: ktest writes builds under `OUTPUT_DIR`, logs to `cross.log`, and optionally stores failures if configured. The config itself is read-only input.

Dependencies and integration points: assumes a Linux source tree at `BUILD_DIR`, crosstools installed under `/usr/local/gcc-<ver>-nolibc/<cross>/bin`, and ktest option semantics. The bisect section integrates with ktest's bisect mode.

Risks: the documented toolchain versions are old and paths are environment-specific. `DO_DEFAULT=1` runs many builds by default, which can be expensive. Some architectures are marked failed and may need updating. Comments note that option assignment form matters for ktest persistence.

Test signals: ktest should generate build tests named by architecture and cross compiler, run `make ARCH=...` with the right `CROSS_COMPILE`, and produce a cross.log summarizing build results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/examples/crosstests.conf -->
