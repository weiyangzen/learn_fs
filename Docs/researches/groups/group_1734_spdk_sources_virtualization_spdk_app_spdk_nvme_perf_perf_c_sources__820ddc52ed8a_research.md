# Group Research: group_1734_spdk_sources_virtualization_spdk_app_spdk_nvme_perf_perf_c_sources__820ddc52ed8a

Scope checked against `Docs/research_subset_a.md`: `sources/virtualization/spdk` is included in subset A. Every source file listed for this group was read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/app/spdk_nvme_perf/perf.c -->
# File Research: sources/virtualization/spdk/app/spdk_nvme_perf/perf.c

This is SPDK's standalone NVMe performance benchmark application. It drives workloads against SPDK NVMe namespaces and, when compiled with the relevant support, kernel block/file devices through Linux AIO or io_uring. The file owns the full program lifecycle: command-line parsing, environment initialization, controller discovery, namespace registration, worker assignment, I/O submission/completion, latency accounting, reporting, and cleanup.

The core abstraction is `struct ns_entry` plus `struct ns_fn_table`. NVMe namespaces, AIO files, and io_uring files all expose `setup_payload`, `submit_io`, `check_io`, `verify_io`, and worker-context lifecycle functions. This lets `work_fn()` submit and poll I/O without caring whether the target is an SPDK NVMe namespace or a kernel file descriptor. Per-worker/per-namespace state lives in `struct ns_worker_ctx`, which tracks outstanding queue depth, counters, latency histogram data, backend-specific qpair/ring/AIO contexts, queued retry tasks, and drain status.

For kernel devices, `register_file()` opens paths with `O_DIRECT`, sizes them with SPDK fd helpers, adjusts alignment to block size when not explicitly set, and creates an AIO or io_uring namespace entry. io_uring uses `io_uring_queue_init`, SQEs for readv/writev, batched CQE peeking, and exact-length completion checks. AIO uses `io_setup`, `io_submit`, and `io_getevents`. Both treat `-EIO` as device removal and switch the namespace context into draining mode.

For SPDK NVMe, `register_controllers()` probes each parsed transport ID, `probe_cb()` applies controller options such as CMB SQ disabling, interrupts, digests, keepalive, TLS PSK, DH-HMAC-CHAP keys, source address/NQN, TOS, and queue counts, and `attach_cb()` registers controllers. `register_ns()` filters inactive or incompatible namespaces, computes request sizing, configures metadata/DIF/DIX details, records namespace geometry, optionally creates Zipf state, and inserts namespace entries. `nvme_init_ns_worker_ctx()` creates a poll group and one or more qpairs per namespace-worker pair, connects them asynchronously, and waits up to ten seconds for all qpairs to become connected.

I/O generation is queue-depth driven. `submit_single_io()` chooses an offset using sequential, uniform random, or Zipf distribution, chooses read/write according to workload mix, timestamps the task, and calls the backend submit function. `task_complete()` updates queue depth, I/O counters, min/max/total latency ticks, optional software histogram, metadata verification for protected namespaces, and either frees the task during drain or immediately resubmits it to maintain depth. `work_fn()` runs the benchmark loop on each SPDK lcore, handles warmup reset, prints terminal-only periodic stats from the main core, drains outstanding I/O fairly across namespaces, and optionally dumps transport statistics.

Reporting includes per-device/core IOPS, MiB/s, average/min/max latency, software latency percentiles and histograms, optional Intel SSD latency log pages, and transport-specific poll group statistics for RDMA, PCIe, and TCP. The code also has an admin-polling pthread for non-PCIe controllers, signal handlers for graceful stop, optional SPDK trace setup, and full cleanup of workers, namespaces, controllers, keyring keys, logging, environment, and mutexes.

Command-line handling is extensive. Required operands are queue depth, I/O size, workload, and duration; transport defaults to local PCIe enumeration when omitted. Advanced flags cover warmup, number of I/Os or namespace percentage, queue sizes, multiple qpairs, unused qpairs, every-core fanout, interrupts, VMD, metadata protection flags, FUA, TCP digests, socket implementation and zerocopy, TLS/KTLS/PSK, DHCHAP, RDMA SRQ/TOS, hugepage/env controls, tracing, log level, and error continuation/rate-limiting.

Notable implementation details and caveats:

- `g_io_unit_size` defaults to a 4-byte-aligned `UINT32_MAX` mask and may split large NVMe payloads into multiple iovecs.
- `--number-ios <N>%` is converted per namespace in `allocate_ns_worker()` using namespace size in I/O units.
- Error-continuation mode queues failed submissions instead of recursively resubmitting, avoiding stack overflow loops.
- The rate-limited logging macro deliberately uses a static non-thread-safe counter and warns when used across multiple workers.
- `unregister_namespaces()` closes file descriptors based on global `g_use_uring`/AIO state even though `g_namespaces` can also contain NVMe namespace entries whose union fields are controller pointers. In this file as read, that is a point to inspect before changing teardown behavior.
- `perf_set_sock_opts()` only handles selected socket fields; the `PERF_PSK_IDENTITY` parser branch passes `"psk_identity"`, which is not accepted by that helper in this file.
<!-- END FILE RESEARCH: sources/virtualization/spdk/app/spdk_nvme_perf/perf.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/app/spdk_tgt/Makefile -->
# File Research: sources/virtualization/spdk/app/spdk_tgt/Makefile

This makefile builds the `spdk_tgt` application from `spdk_tgt.c`. It sets `SPDK_ROOT_DIR` to two directories above the app, includes SPDK common make definitions and module definitions, and uses `mk/spdk.app.mk` for application build rules.

The library list is intentionally broad. It starts from `$(ALL_MODULES_LIST)`, then explicitly adds the event framework and the iSCSI and NVMe-oF event modules. If the configured environment is SPDK's in-tree DPDK environment, it adds `env_dpdk_rpc` so the target can expose DPDK environment RPCs.

Linux-specific modules are conditional. On Linux it adds `event_nbd`; when `CONFIG_UBLK=y`, it adds `event_ublk`; when `CONFIG_VHOST=y`, it adds `event_vhost_blk` and `event_vhost_scsi`; when `CONFIG_VFIO_USER=y`, it adds `event_vfu_tgt`. Separately, `CONFIG_FSDEV=y` adds `event_fsdev`.

The install and uninstall targets delegate to the standard `$(INSTALL_APP)` and `$(UNINSTALL_APP)` macros. Overall, this file defines `spdk_tgt` as the general SPDK target binary that links the enabled storage frontends/backends into one event-framework executable.
<!-- END FILE RESEARCH: sources/virtualization/spdk/app/spdk_tgt/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/app/spdk_tgt/spdk_tgt.c -->
# File Research: sources/virtualization/spdk/app/spdk_tgt/spdk_tgt.c

This is a small launcher for the general `spdk_tgt` application. It uses the SPDK event framework rather than implementing target behavior directly; the actual functionality comes from modules linked by the makefile and initialized through `spdk_app_start()`.

The file defines two app-specific options. `-f <file>` records a pidfile path in `g_pid_path`; `-S <path>` is compiled in when vhost or vfio-user support is enabled and sets the socket directory for both `spdk_vhost_set_socket_path()` and `spdk_vfu_set_socket_path()` as applicable. The option string is built with `SPDK_SOCK_PATH`, so `-S` is only accepted in builds with those features.

`spdk_tgt_save_pid()` writes the current process ID to the requested file and exits on failure. `spdk_tgt_started()` runs after the event application starts; it writes the pidfile if requested and dumps SPDK memory zones to stdout when the `MEMZONE_DUMP` environment variable is present. This is a diagnostic/startup hook rather than the main target loop.

`main()` initializes `spdk_app_opts`, sets `opts.name` to `spdk_tgt`, lets the SPDK app framework parse common and custom arguments, starts the app, finalizes it with `spdk_app_fini()`, and returns the app result code. The file is therefore a conventional SPDK event-app wrapper with pidfile and socket-path conveniences.
<!-- END FILE RESEARCH: sources/virtualization/spdk/app/spdk_tgt/spdk_tgt.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/app/spdk_top/Makefile -->
# File Research: sources/virtualization/spdk/app/spdk_top/Makefile

This makefile builds the `spdk_top` terminal monitor from `spdk_top.c`. It includes SPDK common rules, sets `APP = spdk_top`, and links only the SPDK `rpc` library from `SPDK_LIB_LIST`.

The app also links ncurses UI libraries through `LIBS=-lpanel -lmenu $(shell pkg-config --libs ncurses)`, matching the source file's use of curses windows, panels, and menus. It uses the standard `mk/spdk.app.mk` application rule file and standard install/uninstall macros.

The narrow SPDK library dependency is significant: `spdk_top` does not embed target functionality. It connects to a running SPDK application's JSON-RPC socket and displays runtime state.
<!-- END FILE RESEARCH: sources/virtualization/spdk/app/spdk_top/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/app/spdk_top/spdk_top.c -->
# File Research: sources/virtualization/spdk/app/spdk_top/spdk_top.c

This file implements `spdk_top`, an ncurses-based interactive monitor for a running SPDK application. It connects to the target's JSON-RPC socket, periodically fetches framework/thread/poller/reactor data, and displays sortable, filterable tabs for threads, pollers, and cores.

The data model is built around decoded RPC structures: `rpc_thread_info`, `rpc_poller_info`, `rpc_core_info`, and `rpc_scheduler`. Global arrays hold the current snapshot for up to 1024 RPC threads, 8192 pollers, and 1024 cores. The code tracks previous counter values to show interval deltas as well as total counters. Poller history is kept in a `TAILQ` keyed by poller ID and thread ID so run and busy counters can be compared across refreshes.

RPC handling is synchronous per request. `rpc_send_req()` creates a JSON-RPC request with no parameters, sends it, polls until a response is available, rejects error responses, and returns the response object. The monitor uses `thread_get_stats`, `thread_get_pollers`, `framework_get_reactors`, `framework_get_scheduler`, and `framework_wait_init`. JSON decoder tables map fields into the local structs, with custom handling for nested core lightweight-thread arrays.

The refresh flow is split across two threads. `wait_init()` initializes curses-visible state, waits for the remote app to finish framework initialization, fetches tick rate from `framework_get_reactors`, obtains initial thread/poller/core snapshots to avoid display races, and starts `data_thread_routine()`. The data thread repeatedly fetches cores, threads, pollers, and scheduler data, updating shared globals under `g_thread_lock` and sleeping according to `g_sleep_time`. The UI thread runs `show_stats()`, handles keyboard input, tab switching, sorting/filtering popups, page navigation, detail popups, and quit.

The UI has three main tabs. The threads tab displays thread name, core, active/timed/paused poller counts, idle/busy time, CPU percentage, and busy/idle status. The pollers tab displays name, type, owning thread, run count, period, and busy status/count. The cores tab displays lcore, thread count, poller count, idle/busy time, busy percentage, interrupt state, system/IRQ/CPU percentages, and frequency. Columns can be disabled through a menu, and sorting supports primary plus secondary sort columns.

Detail popups are implemented for threads, cores, pollers, scheduler state, refresh rate, sorting, filtering, and help. Thread details include pollers running on the thread. Core details include frequency, interrupt state, idle/busy time, poller count, and thread names; selecting a thread from a core popup can open the thread detail view. Poller details show type, owning thread, run count, period, and busy count/status. Scheduler details show scheduler, period, and governor.

The curses setup uses panels, menus, color pairs, nonblocking input via `timeout(1)`, hidden cursor, and resize-aware redraws. `finish()` ends curses mode, closes the JSON-RPC client, and exits; signal handlers for SIGINT, SIGPIPE, and SIGABRT call it. Memory for decoded strings and nested arrays is freed when snapshots are replaced and again on shutdown.

Notable implementation details and caveats:

- `sort_cores()` calls `subsort_cores()` with the primary column again when the first comparison ties, so the declared secondary core sort column is not used in this file as read.
- `draw_core_win_content()` unlocks `g_thread_lock()` internally, which is unusual because callers also manage lock state around popup drawing. This coupling should be considered before refactoring popup code.
- The monitor assumes some values, such as scheduler/governor names, are stable enough not to require dynamic popup resizing.
- Error display from the data thread uses bottom-message printing while curses drawing is active, so UI synchronization depends on the existing coarse mutex and screen refresh cadence.
<!-- END FILE RESEARCH: sources/virtualization/spdk/app/spdk_top/spdk_top.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/app/trace/Makefile -->
# File Research: sources/virtualization/spdk/app/trace/Makefile

This makefile builds the C++ `spdk_trace` tool from `trace.cpp`. It includes SPDK common and module definitions, sets `APP = spdk_trace`, and sets `SPDK_NO_LINK_ENV = 1`.

`SPDK_NO_LINK_ENV = 1` is important because the source intentionally avoids linking the full SPDK environment implementation. The makefile links `json` and `trace_parser`, while the source provides small aborting/no-op stubs for environment functions that are pulled in indirectly by utility code but not used by the tool's trace parsing path.

The build uses `CXX_SRCS := trace.cpp` and includes `mk/spdk.app_cxx.mk`. Install and uninstall use standard SPDK app macros.
<!-- END FILE RESEARCH: sources/virtualization/spdk/app/trace/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/app/trace/trace.cpp -->
# File Research: sources/virtualization/spdk/app/trace/trace.cpp

This file implements `spdk_trace`, a command-line trace display tool. It reads an SPDK trace shared-memory object or saved trace file through `spdk_trace_parser`, then prints events either in the default human-readable format or JSON.

The program supports selecting one lcore (`-c`), printing raw TSC offsets (`-t`), using time deltas between consecutive printed events (`-T`), selecting a shared-memory trace by app name plus shm ID or PID (`-s`, `-i`, `-p`), selecting a trace file (`-f`), and JSON output (`-j`). On Linux, if neither `-s` nor `-f` is provided, it scans `/dev/shm` with `nftw()` and chooses the newest path containing `SPDK_TRACE_SHM_NAME_BASE`.

Default text output prints TSC rate, per-lcore entry counts, then each parsed entry. `print_event()` prints thread name, lcore, event time in microseconds, optional TSC offset, owner description when valid for the event time, tracepoint name, optional size, object ID or object lifetime time, and tracepoint arguments. Argument rendering handles pointer, integer, and string types using tracepoint definitions.

JSON output starts a top-level object containing `tsc_rate`, tracepoint definitions, owner descriptions, and an `entries` array. Each entry includes lcore, tracepoint ID, TSC, optional owner/poller fields, size, object data, related object, and raw argument values. `print_json()` writes JSON output to stdout and aborts on write errors.

The file deliberately avoids linking the full env implementation. It defines `spdk_realloc()`, `spdk_free()`, and `spdk_get_ticks()` in an `extern "C"` block; the first two assert false and the tick function returns zero. A comment explains these exist only because `spdk_util` references env functions that this app does not actually use.

The main validation rules are simple: `-f` and `-s` are mutually exclusive; when using `-s`, either `-i` or `-p` must identify the shm object; lcore selection must not exceed `SPDK_TRACE_MAX_LCORE`. After parsing, the tool initializes the parser in file or shared-memory mode, prints in the selected format, cleans up the parser, and returns the print routine status.
<!-- END FILE RESEARCH: sources/virtualization/spdk/app/trace/trace.cpp -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/app/trace_record/Makefile -->
# File Research: sources/virtualization/spdk/app/trace_record/Makefile

This makefile builds `spdk_trace_record` from `trace_record.c`. It includes SPDK common rules, links the `util` and `log` libraries, and then uses the standard C application build include `mk/spdk.app.mk`.

The install and uninstall targets delegate to SPDK's standard app install macros. The linked library list matches the source: it uses SPDK trace structures and utility helpers, but it is a standalone recorder rather than a full event-framework app.
<!-- END FILE RESEARCH: sources/virtualization/spdk/app/trace_record/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/app/trace_record/trace_record.c -->
# File Research: sources/virtualization/spdk/app/trace_record/trace_record.c

This file implements `spdk_trace_record`, a recorder that copies trace entries from a running SPDK process's trace shared-memory object into a persistent aggregate trace file. It is complementary to `spdk_trace`: this program records, while `spdk_trace` displays/parses.

The main context is `struct aggr_trace_record_ctx`, which holds the output path, output fd, shared-memory fd, mapped trace file, and one `lcore_trace_record_ctx` per SPDK lcore. Each lcore context tracks a temporary per-lcore file path/fd, whether that lcore has trace history, input/output history headers, the next recorded entry index, first/last TSC values, and total copied entries.

`input_trace_file_mmap()` opens the trace shm object read-only, maps the header first to obtain TSC rate and total trace file size, remaps the entire trace file, and populates lcore contexts with per-lcore histories via `spdk_get_per_lcore_history()`. It rejects zero TSC rate and prints per-lcore entry counts when verbose mode is enabled.

The recorder writes to temporary per-lcore files first. `output_trace_files_prepare()` derives paths as `<aggregate_path>-<lcore>`, unlinks any existing aggregate and temp files, creates temp files for valid lcores, and allocates output history headers sized for each lcore's tracepoint count. `output_trace_files_finish()` frees those headers, closes temp fds, and unlinks temp files.

The hard part is copying from a circular trace buffer without losing order. `lcore_trace_record()` compares shared-memory `next_entry` with the last recorded index, uses a memory read barrier after observing `next_entry`, and appends either a contiguous segment, a wraparound segment, or the full circular buffer into the lcore temp file. It detects rollback, reports missed entries if producers advanced by more than the buffer size, updates copied entry counts, copies tracepoint counters into the output history header, records first/last TSC, and advances `rec_next_entry`.

`trace_files_aggregate()` creates the final trace file. It copies the original trace header and non-lcore sections, recalculates total file size and lcore offsets based on recorded entry counts, writes a new lcore-offsets section, then appends each valid lcore's output history header and copied trace entries from its temp file. It verifies temp-file byte count against `num_entries * sizeof(struct spdk_trace_entry)` and reports the aggregate output path.

The command line requires `-f` output file, `-s` app name, and either `-i` shm ID or `-p` PID. `-q` disables verbose logging, `-t` sets a recording duration in seconds, and `-h` prints usage. The program installs SIGINT and SIGTERM handlers that set `g_shutdown`, records until stopped or until duration expires, aggregates, prints a per-lcore summary in microseconds, unmaps/cleans up, and exits.

Notable caveats:

- `cont_write()` and `cont_read()` use `int` for byte counts derived from `size_t`; in this file their callers pass bounded chunk sizes or structure sizes, but the helper signatures are narrower than the POSIX types.
- Temp files are created with `O_EXCL` after the cleanup pass, so unexpected stale files that cannot be unlinked fail preparation.
- The recorder tolerates missed trace entries by copying the current full circular buffer and reporting the loss; it cannot reconstruct overwritten entries.
<!-- END FILE RESEARCH: sources/virtualization/spdk/app/trace_record/trace_record.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/app/vhost/Makefile -->
# File Research: sources/virtualization/spdk/app/vhost/Makefile

This makefile builds the legacy/specific `vhost` application from `vhost.c`. It includes SPDK common rules and module definitions, sets `APP = vhost`, and links a broad module set: `$(ALL_MODULES_LIST)`, the event framework, vhost block, vhost SCSI, and NBD event modules.

When using SPDK's in-tree DPDK environment, it adds `env_dpdk_rpc`. On Linux with `CONFIG_VFIO_USER=y`, it adds `event_vfu_tgt`. With `CONFIG_FSDEV=y`, it adds `event_fsdev`.

The build uses the standard C app make include and standard install/uninstall macros. Compared with `spdk_tgt`, this app links vhost-specific event modules unconditionally in the base library list, making it a vhost-oriented target wrapper.
<!-- END FILE RESEARCH: sources/virtualization/spdk/app/vhost/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/app/vhost/vhost.c -->
# File Research: sources/virtualization/spdk/app/vhost/vhost.c

This is a compact SPDK event-app launcher for the `vhost` application. The actual vhost functionality is provided by linked SPDK modules; this source handles app options, pidfile creation, socket path configuration, startup, and shutdown.

The custom options are `-f <path>` to save the process ID and `-S <path>` to set the vhost/vfio-user socket directory. `vhost_parse_arg()` stores the pidfile path or calls `spdk_vhost_set_socket_path()` and, when compiled with `SPDK_CONFIG_VFIO_USER`, `spdk_vfu_set_socket_path()`.

`save_pid()` writes the current PID to the configured path and exits on file creation failure. Unlike `spdk_tgt.c`, this file writes the pidfile before `spdk_app_start()`. The `vhost_started()` callback is empty, so all startup behavior comes from the SPDK app framework and linked modules.

`main()` initializes app opts with name `vhost`, parses SPDK common and custom arguments, writes the pidfile if requested, starts the app, finalizes with `spdk_app_fini()`, and returns the result. It exits immediately with the parser return code on argument failure.
<!-- END FILE RESEARCH: sources/virtualization/spdk/app/vhost/vhost.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/Makefile -->
# File Research: sources/virtualization/spdk/lib/Makefile

This is the top-level SPDK library directory makefile. It includes common make settings and library dependency definitions, then builds subdirectories through `mk/spdk.subdirs.mk`.

The always-enabled library directories include core SPDK infrastructure and storage subsystems: `bdev`, `blob`, `conf`, `dma`, `accel`, `event`, `json`, `jsonrpc`, `log`, `lvol`, `rpc`, `sock`, `thread`, `trace`, `util`, `nvme`, `vmd`, `nvmf`, `scsi`, `ioat`, `ut_mock`, `iscsi`, `notify`, `init`, `trace_parser`, `keyring`, and `ae4dma`.

Linux builds add `nbd`, `ftl`, and `vfio_user`; `CONFIG_UBLK=y` adds `ublk`. Unit-test support is conditional: `ut` is built only when either `CONFIG_TESTS` or `CONFIG_UNIT_TESTS` is enabled. Other feature gates add `env_ocf`, `idxd`, `vhost`, `virtio`, RDMA libraries (`rdma_cm`, `rdma_provider`, `rdma_utils`), `vfu_tgt`, and filesystem-device libraries (`fsdev`, `fuse_dispatcher`).

When `CONFIG_RDMA_PROV` is `mlx5_dv`, the `mlx5` directory is included. The makefile also detects whether `CONFIG_ENV` points to an in-tree library directory under `lib`; if so, it adds that environment directory, while out-of-tree env implementations are expected to be built separately.

The file declares `all`, `clean`, and every enabled subdir as phony, then delegates recursive build behavior to `spdk.subdirs.mk`. It is a build graph coordinator rather than a code-bearing module.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/accel/Makefile -->
# File Research: sources/virtualization/spdk/lib/accel/Makefile

This makefile builds the SPDK `accel` library. It sets shared-library version values `SO_VER := 18`, `SO_MINOR := 0`, and `SO_SUFFIX := $(SO_VER).$(SO_MINOR)`, names the library `accel`, and compiles `accel.c`, `accel_rpc.c`, and `accel_sw.c`.

Optional system libraries are added based on configuration. `CONFIG_HAVE_LZ4=y` adds `-llz4`. `CONFIG_ISAL_CRYPTO=y` attempts to add ISA-L Crypto library search paths and `-lisal_crypto`.

The makefile sets `SPDK_MAP_FILE` to the local `spdk_accel.map`, so symbol exports are controlled by that version map, then includes the standard SPDK library build rules through `mk/spdk.lib.mk`.

Notable caveat: the `CONFIG_ISAL_CRYPTO` line appears malformed as read: `LOCAL_SYS_LIBS += -L$(ISAL_CRYPTO_DIR/.libs -L$(ISAL_CRYPTO_DIR)/lib64 -lisal_crypto`. The first variable reference lacks the normal `)` placement around `ISAL_CRYPTO_DIR`, so this line should be verified before relying on that configuration path.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/accel/Makefile -->