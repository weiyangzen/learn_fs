# Research Group subset-b-006896

This grouped report covers the assigned thermal, time, latency, and RTLA tracing files. Each section is delimited for reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/tmon/sysfs.c -->
# sources/distributed-fs/ceph-client/tools/thermal/tmon/sysfs.c

## Purpose
`sysfs.c` is the Linux thermal sysfs backend for `tmon`. It probes `/sys/class/thermal`, records thermal zones, trip points, cooling devices, and zone-to-device bindings, then samples live temperatures and cooling-device states. It also provides the write path used by the controller and TUI to set `cooling_device*/cur_state`.

## Important APIs, Types, and Functions
The file owns global `struct tmon_platform_data ptdata`, the `trip_type_name[]` mapping, a fixed three-record `trec[]` thermal history ring, and `cur_thermal_record`. Public functions include `probe_thermal_sysfs()`, `update_thermal_data()`, `set_ctrl_state()`, `get_ctrl_state()`, `zone_instance_to_index()`, `sysfs_set_ulong()`, and `free_thermal_data()`. Internal helpers read sysfs files (`sysfs_get_ulong()`, `sysfs_get_string()`), parse instance numbers (`get_instance_id()`), map trip type strings, scan thermal zones and cooling devices, and collect binding data from thermal-zone `cdev*` symlinks.

## Control Flow
Startup calls `probe_thermal_sysfs()`, which scans `THERMAL_SYSFS`, counts zone/device instances while tracking maximum instance IDs, allocates `ptdata.tzi` and optional `ptdata.cdi`, then calls `scan_tzones()` and `scan_cdevs()`. `scan_tzones()` walks possible `thermal_zoneN` paths, reads each zone type, discovers valid `trip_point_*_temp` nodes below `MAX_TEMP_KC`, reads matching trip types, and records cooling-device symlink bindings and trip bindings. `update_thermal_data()` advances the circular thermal record, timestamps it, samples each zone temperature, refreshes each cooling device by re-reading type/max/current, and appends a row to `tmon_log` when logging is enabled.

## State and Persistence
State is mostly process-global and in-memory: `ptdata`, `trec`, `cur_thermal_record`, cooling-device flags, and trip/cdev binding bitmaps. Persistent external effects are writes to thermal sysfs `cur_state` through `sysfs_set_ulong()` and optional rows in `/var/tmp/tmon.log` managed by `tmon.c`. `set_ctrl_state()` scales a percentage-like controller output against each matching cooling device `max_state`, while `get_ctrl_state()` reads the first controlled device directly from sysfs.

## Dependencies and Integration Points
This file depends on the Linux thermal sysfs ABI, directory entry types, symlink targets like `../cooling_deviceN`, and fields declared in `tmon.h`. `tmon.c` calls the probe/update/control APIs; `tui.c` displays `ptdata` and calls the write helpers. The controller consumes `trec` temperature records.

## Risks and Edge Cases
Parsing uses `strtok()` destructively in `get_instance_id()`, so callers must not reuse the original string after parsing. Arrays are bounded by constants like `MAX_NR_TRIP`, `MAX_NR_CDEV`, and bitmap width assumptions; very large or sparse sysfs instance IDs could exceed practical display or bitmap expectations. `sysfs_get_ulong()` and `sysfs_set_ulong()` return success even when `fscanf()`/`fprintf()` fail after open, and many probe calls do not check read failures before using partially initialized fields. `nl->d_type == DT_LNK` can be unreliable on filesystems that do not fill `d_type`, though sysfs normally does. `set_ctrl_state()` silently disables display control if a matching device has `max_state < 10`.

## Test Signals
Useful tests require a system or fixture exposing thermal sysfs. Validate probe behavior with multiple zones, sparse instance IDs, missing cdevs, invalid trip temperatures, and cdev symlink bindings. Runtime tests should confirm that sampling updates `trec`, that logging emits zone/cdev columns, and that controlled devices receive scaled `cur_state` writes only when `no_control == 0` and `CDEV_FLAG_IN_CONTROL` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/tmon/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/tmon/tmon.c -->
# sources/distributed-fs/ceph-client/tools/thermal/tmon/tmon.c

## Purpose
`tmon.c` is the entry point and main runtime loop for the Thermal Monitor utility. It handles command-line options, privilege checks, syslog setup, optional daemonization, optional thermal data logging, initialization of sysfs/TUI/controller subsystems, periodic sampling, PID-controller invocation, and cleanup.

## Important APIs, Types, and Functions
The file defines global runtime knobs such as `ticktime`, `no_control`, `time_elapsed`, `target_temp_user`, `dialogue_on`, `tmon_exit`, `target_thermal_zone`, `ctrl_cdev`, `tmon_log`, `event_tid`, and `input_lock`. `usage()` and `version()` terminate after printing help/version text. `prepare_logging()` safely opens `/var/tmp/tmon.log`, rejects symlinks and files not owned by the current user, and writes configuration headers. `tmon_cleanup()` tears down the UI, thread, syslog, log file, control state, and thermal data. `main()` orchestrates the whole utility.

## Control Flow
`main()` requires effective root, parses options (`-c`, `-d`, `-t`, `-T`, `-l`, `-g`, `-z`, etc.), initializes `input_lock`, opens syslog, installs signal handlers, probes thermal sysfs, initializes curses windows, starts the TUI input thread, validates the target thermal zone, then loops until `tmon_exit`. Each loop sleeps `ticktime`, redraws title/sensor windows, samples sysfs data, updates data/cooling views when no dialog is active, increments elapsed time, calls `controller_handler()` using the selected zone temperature, stores PID output in `trec[0].pid_out_pct`, and redraws controls.

## State and Persistence
The process keeps global UI/control state and an optional log file. Daemon mode forks, creates a new session, changes to `/`, applies `umask`, disables TUI, sleeps, then closes standard descriptors. Cleanup always calls `set_ctrl_state(0)` to relax throttling. Signals set `tmon_exit` rather than performing full cleanup in the signal handler.

## Dependencies and Integration Points
`tmon.c` integrates with `sysfs.c` (`probe_thermal_sysfs()`, `update_thermal_data()`, `set_ctrl_state()`), `tui.c` (curses setup and drawing), and the controller implementation through `init_thermal_controller()` and `controller_handler()`. It depends on root access, pthreads, ncurses, syslog, signals, and the Linux thermal sysfs ABI.

## Risks and Edge Cases
`SIGKILL` is listed in the signal handler switch but cannot be caught. `strncpy(ctrl_cdev, optarg, CDEV_NAME_SIZE)` may leave no terminating NUL if the argument is exactly the buffer size. `tmon_cleanup()` exits with status 1 even for normal termination. The sampling loop calculates `target_tz_index` before later fallbacks but does not recompute the index after replacing `target_thermal_zone`, so an out-of-range initial target can leave a stale negative index for the controller path. Daemon mode still initializes curses functions after `disable_tui()` returns early, but cleanup also calls curses functions unconditionally after `set_ctrl_state()`, which can be sensitive if curses was never initialized.

## Test Signals
Exercise option parsing for root/non-root paths, daemon mode, invalid target temperature, sparse thermal zone IDs, target zone fallback, and log-file symlink/ownership checks. Runtime smoke tests should verify signal-triggered exit restores cooling state and that the controller loop calls update/display functions at the requested interval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/tmon/tmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/tmon/tmon.h -->
# sources/distributed-fs/ceph-client/tools/thermal/tmon/tmon.h

## Purpose
`tmon.h` defines the shared constants, structs, globals, and function prototypes used across the TMON thermal monitor. It is the contract between the sysfs backend, main loop, ncurses UI, and PID controller.

## Important APIs, Types, and Functions
Key limits include `MAX_NR_TZONE`, `MAX_NR_CDEV`, `MAX_NR_TRIP`, display sizing constants, thermal bounds, `THERMAL_SYSFS`, `CDEV`, `TZONE`, and log path `TMON_LOG_FILE`. Data types include `struct thermal_data_record`, `struct cdev_info`, `enum trip_type`, `struct trip_point`, `struct tz_info`, `struct tmon_platform_data`, `struct pid_params`, and small enums for cooling-device and thermal-zone categories. The header declares global runtime state (`ticktime`, `time_elapsed`, `target_temp_user`, `ctrl_cdev`, `ptdata`, `p_param`, `trec`, `no_control`) and public functions for controller, TUI, sysfs probing/sampling, and cleanup.

## Control Flow and Integration
The header itself contains no control flow, but it shapes interactions: `tmon.c` initializes and loops, `sysfs.c` fills `ptdata` and `trec`, `tui.c` reads those objects to draw windows and can write sysfs state, and the controller reads `p_param`/thermal records while writing cooling state.

## State and Persistence
All externally declared globals are process-local, but several represent persisted or externalized state: `tmon_log` points to `/var/tmp/tmon.log`, `ptdata` mirrors sysfs discovery, and control functions write back into sysfs.

## Dependencies and Integration Points
The header depends on `sys/time.h`, `pthread.h`, and `FILE` from standard headers included by consumers. Its constants assume Linux thermal sysfs naming and ncurses display layout.

## Risks and Edge Cases
Hard-coded array sizes and display dimensions can truncate or misrepresent systems with many thermal zones, many cooling devices, long type names, or large instance gaps. The fixed `thermal_data_record` design is simple but tightly couples sampling capacity to `MAX_NR_TZONE`. The header exposes many mutable globals, making thread-safety dependent on caller discipline rather than type-level enforcement.

## Test Signals
Build coverage should include all C files that include this header. Runtime tests should stress maximum zones/cooling devices, long names, and controller/UI behavior when no cooling device is in control.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/tmon/tmon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/tmon/tui.c -->
# sources/distributed-fs/ceph-client/tools/thermal/tmon/tui.c

## Purpose
`tui.c` implements TMON's ncurses interface. It creates and refreshes windows for the title/status bars, thermal zones, cooling devices, sampled thermal data, controller state, and a tunables dialog. It also runs the keyboard event loop that lets users toggle the dialog, set cooling-device states, adjust target temperature, or quit.

## Important APIs, Types, and Functions
Global/static UI objects include `WINDOW *` windows, `PANEL *` panels, terminal dimensions, `status_bar_slots`, and `tui_disabled`. Public functions are `initialize_curses()`, `setup_windows()`, `resize_handler()`, `close_windows()`, `disable_tui()`, drawing functions (`show_title_bar()`, `show_sensors_w()`, `show_cooling_device()`, `show_data_w()`, `show_control_w()`, `show_dialogue()`), `write_status_bar()`, and `handle_tui_events()`. Internal helpers draw bars, convert trip types to display characters, handle dialog choices/values, and calculate dialog rows.

## Control Flow
`setup_windows()` sizes subwindows based on current terminal dimensions and `ptdata` counts, then wraps cooling/dialog windows in panels. The main loop in `tmon.c` periodically calls drawing functions after sampling. The input thread reads from `cooling_device_window`, locks `input_lock`, handles dialog interactions when active, toggles panels on TAB, and sets `tmon_exit` on `q`/`Q`. Dialog value entry writes a cooling device `cur_state` through `sysfs_set_ulong()` or updates `p_param.t_target` after range validation.

## State and Persistence
UI state is process-local. External effects occur when dialog writes to sysfs cooling-device state. `dialogue_on` and `top` control whether periodic redraws update data windows or leave the dialog visible. The resize handler destroys and recreates all windows.

## Dependencies and Integration Points
The file depends on ncurses, panel library, pthreads, signals, and the globals in `tmon.h`. It reads `ptdata`, `trec`, `p_param`, `target_thermal_zone`, and `ctrl_cdev`; it calls sysfs write/read helpers and controller display state.

## Risks and Edge Cases
Many coordinates are derived from thermal instance IDs rather than compact indices, so large or sparse instance IDs can push columns off-screen. The file has defensive checks for disabled TUI and missing windows, but some functions assume windows exist after initialization. The input mutex protects event handling, yet the sampling/display loop reads the same globals without broad locking, so visual races are possible. Dialog choice labels are limited to alphabetic offsets and become awkward if cooling devices exceed `A-Z` practical bounds. `close_panel()` and `close_window()` set only local pointer copies to NULL, leaving stale static pointers until overwritten.

## Test Signals
Run TMON in terminals of varying sizes, with zero/many cooling devices, long names, sparse IDs, and repeated resize events. Verify TAB dialog navigation, target-temperature validation, cooling-state writes, quit handling, and daemon mode where TUI functions should return early.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/tmon/tui.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/time/udelay_test.sh -->
# sources/distributed-fs/ceph-client/tools/time/udelay_test.sh

## Purpose
`udelay_test.sh` is a shell-based kernel self-test driver for the `udelay_test` module. It writes delay values into `/sys/kernel/debug/udelay_test`, records the module's reported results, and fails if any reported line contains `FAIL`.

## Important APIs, Types, and Functions
The script defines `MODULE_NAME=udelay_test` and `UDELAY_PATH=/sys/kernel/debug/udelay_test`. `setup()` loads the module with `/sbin/modprobe -q` and creates a `mktemp` output file. `test_one()` writes one delay value and appends the sysfs output through `tee`. `cleanup()` removes the temp file and unloads the module. A trap runs cleanup on exit.

## Control Flow
After setup, the script tests delays from 1 to 199 by 1, 200 to 490 by 10, and 500 to 2000 by 100. It then counts lines containing `FAIL` in the temporary output. If `grep -c FAIL` succeeds, it prints an error and returns `1`; otherwise it exits with the default `retcode`.

## State and Persistence
Transient state is the temp file path and the loaded kernel module. Persistent system impact is limited to loading/unloading the module and writing debugfs control values. Cleanup is trap-based.

## Dependencies and Integration Points
The script needs bash, root or sufficient privileges, debugfs mounted at `/sys/kernel/debug`, `/sbin/modprobe`, the `udelay_test` kernel module, `mktemp`, `tee`, and `grep`.

## Risks and Edge Cases
`retcode` is not initialized before `exit $retcode`, so a fully passing run may exit with an empty argument, which shell treats like `exit` with the status of the last command. That is usually zero after a non-matching `grep`, but it is implicit. If setup fails, writes can fail later rather than giving a precise setup error. `mktemp` failure is not checked. Cleanup unloads the module even if it was loaded before the test.

## Test Signals
Run as root with debugfs mounted and confirm pass/fail exit status. Inject a fake `FAIL` line or use a debugfs fixture to verify failure reporting. Also test missing module, missing debugfs, and interrupted execution to verify cleanup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/time/udelay_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/Makefile -->
# sources/distributed-fs/ceph-client/tools/tracing/Makefile

## Purpose
This top-level tracing tools Makefile dispatches build, install, and clean targets to the `latency` and `rtla` subdirectories.

## Important APIs, Types, and Functions
It includes `../scripts/Makefile.include` and uses its `$(call descend,dir[,target])` helper. Public targets are `all`, `clean`, `install`, `latency`, `latency_install`, `latency_clean`, `rtla`, `rtla_install`, and `rtla_clean`.

## Control Flow
`all` depends on both `latency` and `rtla`. `install` depends on both install subtargets. `clean` depends on both clean subtargets. Each subtarget descends into the corresponding child directory and optionally passes `install` or `clean`.

## State and Persistence
The file itself does not persist state, but its targets delegate object, binary, installation, and cleanup behavior to child Makefiles. Install writes are controlled by those children and `DESTDIR`.

## Dependencies and Integration Points
The Makefile integrates with the Linux kernel tools build infrastructure through `Makefile.include`. It assumes the `latency/` and `rtla/` directories provide compatible Makefiles.

## Risks and Edge Cases
Any missing or incompatible child Makefile causes top-level tracing builds to fail. Because this wrapper has no feature probing of its own, child failures are surfaced only after descent.

## Test Signals
Run `make`, `make latency`, `make rtla`, `make clean`, and `make install DESTDIR=...` from `tools/tracing` and confirm the expected child targets are invoked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/latency/Makefile -->
# sources/distributed-fs/ceph-client/tools/tracing/latency/Makefile

## Purpose
This Makefile builds and installs the `latency-collector` tracing utility using the Linux tools build system and feature detection for `libtraceevent` and `libtracefs`.

## Important APIs, Types, and Functions
It derives `srctree`, normalizes `OUTPUT`/`O`, defines `LATENCY-COLLECTOR` and its intermediate `LATENCY-COLLECTOR_IN`, exports compiler tools, and declares feature probes in `FEATURE_TESTS`/`FEATURE_DISPLAY`. The core build target links `latency-collector-in.o` into the final binary with `$(EXTLIBS)`. The pattern rule `latency-collector.%: fixdep FORCE` and `$(LATENCY-COLLECTOR_IN): fixdep FORCE` invoke `tools/build/Makefile.build`.

## Control Flow
Normal builds include `tools/build/Makefile.include`, then feature detection and `Makefile.config` unless the requested goal is only `clean` or `install`. `all` builds the binary. `install` creates `$(DESTDIR)/usr/bin`, installs the binary mode 755, and strips it. `clean` deletes object files, command/dependency files, the binary, `fixdep`, `FEATURE-DUMP`, and feature output.

## State and Persistence
Build artifacts are written under `OUTPUT` or the current directory. Install writes to `$(DESTDIR)$(BINDIR)`; clean removes generated files from the build tree.

## Dependencies and Integration Points
It depends on GCC, LD, AR, pkg-config, the Linux tools build framework, `libtraceevent`, `libtracefs`, and local `Makefile.config`.

## Risks and Edge Cases
The Makefile forces `CC := gcc`, which may override cross-compilation expectations unless the broader tools build environment compensates. Feature probing is skipped for `install`, so installing without a prior successful build can fail late. Clean uses `find .`, which targets the current latency directory, not a separate output tree when `O=` points elsewhere.

## Test Signals
Build with and without `O=`, missing `libtracefs`, and staged `DESTDIR`. Verify `clean` removes generated local artifacts and that feature failures are reported during normal build goals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/latency/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/latency/latency-collector.c -->
# sources/distributed-fs/ceph-client/tools/tracing/latency/latency-collector.c

## Purpose
`latency-collector.c` is a standalone ftrace latency collector. It configures a selected latency tracer, watches `tracing_max_latency` with inotify, and prints snapshots of the trace file when new maximum latencies occur. It is designed to catch clusters of close latencies by optionally delaying trace reads with controlled randomization so the program does not always print only the first event in a burst.

## Important APIs, Types, and Functions
Important state includes selected tracer, ftrace option state, scheduling policy/priority, trace file paths, threshold, random sleep settings, verbosity, signal flag, and print-thread count. `struct ftrace_state` stores original tracer, threshold, and trace options for restoration. `struct print_state`, `struct queue`, and `struct entry` implement ordered request/ticket handling. Key functions include `scan_arguments()`, `find_default_tracer()`, `save_and_disable_tracer()`, `enable_tracer()`, `restore_ftrace()`, `cleanup_exit()`, `tracing_loop()`, `do_printloop()`, `print_tracefile()`, `set_priority()`, and queue/probability-table helpers.

## Control Flow
`main()` initializes save state and signals, opens stdout unbuffered, parses options, shows parameters, initializes print state, probability table if needed, sets scheduler priority, starts print threads, then enters `tracing_loop()`. The loop optionally saves/restores ftrace state around tracer setup, resets max latency, watches `debug_maxlat`, starts tracing, then reads inotify events. Each modification creates a ticketed request unless another print is ongoing or the bounded queue is full. Print threads consume queue entries, decide whether to sleep randomly, print skip/lost messages when races occur, or read `debug_tracefile` into a large buffer and write it atomically under `print_mtx`.

## State and Persistence
The utility changes global ftrace files: `current_tracer`, `tracing_thresh`, `tracing_max_latency`, and `trace_options`. Original values are saved and restored on cleanup unless `--no-ftrace`, `--tracefile`, or `--max-lat` puts the tool in externally managed mode. It may change its scheduler policy. Long-lived runtime state is in mutex-protected queues, counters, probability table, and thread-local random buffers.

## Dependencies and Integration Points
The code depends on libtracefs, pthreads, inotify, ftrace latency tracers (`preemptirqsoff`, `preemptoff`, `irqsoff`, wakeup variants), `/dev/urandom`, POSIX scheduling, and Linux tracing files. It integrates with kernel tracing by file writes/reads through libtracefs and direct `open/read` of the trace file.

## Risks and Edge Cases
Running as root or with tracing permissions is typically required. The program exits rather than restoring if it decides another tracer is active and `--force` is absent, leaving any state already changed before that point minimal but worth checking. The queue is intentionally small, so fast bursts can lose print requests. `print_tracefile()` uses a fixed 16 MiB buffer and truncates if the trace is larger than available space. Cleanup tries to lock the print mutex for one second but proceeds even if output races remain. The ring/ticket logic is intricate; missed-event messages depend on verbosity. Some `malloc_or_die_nocleanup()` paths avoid cleanup from restoration code to prevent recursion.

## Test Signals
Test `--list`, default tracer selection, invalid tracer, `--force`, `--no-ftrace`, custom trace/max-lat paths, immediate and random print modes, queue saturation, signal cleanup, and priority bounds. Use tracefs fixtures or a live kernel to verify original ftrace settings are restored and that trace output includes BEGIN/END markers and maximum latency summary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/latency/latency-collector.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/Makefile -->
# sources/distributed-fs/ceph-client/tools/tracing/rtla/Makefile

## Purpose
This Makefile builds the `rtla` realtime Linux analysis tool, optional BPF skeletons/actions, unit tests, documentation, and installation artifacts through the Linux tools build system.

## Important APIs, Types, and Functions
It derives `srctree`, normalizes `OUTPUT`, defines `RTLA`, `RTLA_IN`, `VERSION`, `DOCSRC`, feature probes for tracefs/traceevent/cpupower/check/libbpf/clang-bpf-co-re/bpftool-skeletons, and includes `Makefile.rtla` plus unit-test definitions. BPF-specific targets compile `src/timerlat.bpf.c` and example/test BPF objects with clang and generate `src/timerlat.skel.h` with bpftool when `BUILD_BPF_SKEL=1`; otherwise they create a disabled skeleton header or skip objects.

## Control Flow
Normal `all` builds `rtla`. Feature detection and `Makefile.config` are included for build/check goals but skipped for `clean`, `install`, tarball, and documentation-only goals. `$(RTLA_IN)` depends on `fixdep`, `FORCE`, and the generated skeleton header, then invokes `make $(build)=rtla`. Link targets produce dynamic and optional static binaries. `check` runs Perl `prove` tests with `RTLA` and `BPFTOOL` variables. `examples` builds the BPF action example.

## State and Persistence
Build output is placed in `OUTPUT` or the source directory. Generated artifacts include `src/timerlat.bpf.o`, `src/timerlat.skel.h`, BPF example/test objects, `rtla`, `rtla-static`, feature directories, and unit-test outputs. Install/doc targets are defined by included files.

## Dependencies and Integration Points
The Makefile integrates with the kernel tools build framework, libtraceevent, libtracefs, optional libcpupower, libcheck, libbpf, clang, bpftool, BPF CO-RE support, and RTLA documentation/test subtrees.

## Risks and Edge Cases
When BPF skeleton support is disabled, a stub skeleton header is generated, so C code must compile fallback paths cleanly. Cleaning removes generated skeletons and BPF objects in the source tree. Static linking depends on all external libraries having static forms. Feature detection skips some targets, so invoking install/check without prior build or dependencies can fail late.

## Test Signals
Run builds with and without BPF support, `make static`, `make examples`, `make check`, `make clean`, and out-of-tree `O=` builds. Verify generated skeleton handling and fallback compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/example/timerlat_bpf_action.c -->
# sources/distributed-fs/ceph-client/tools/tracing/rtla/example/timerlat_bpf_action.c

## Purpose
This is a minimal BPF action program example for RTLA timerlat. It demonstrates the required `action_handler` symbol that can be tail-called by the main timerlat BPF program when a latency threshold is hit.

## Important APIs, Types, and Functions
The file defines a GPL license section, a CO-RE-compatible `struct trace_event_raw_timerlat_sample` with `timer_latency`, and `SEC("tp/timerlat_action") int action_handler(...)`. The handler calls `bpf_printk()` with the latency value and returns zero.

## Control Flow
There is no userspace control flow. When loaded and registered through `timerlat_load_bpf_action_program()`, the main RTLA BPF program tail-calls this handler from its threshold path.

## State and Persistence
The program stores no state. Its only side effect is BPF trace output via `bpf_printk()`.

## Dependencies and Integration Points
It depends on clang BPF compilation, BPF helper headers, libbpf loading, and the userspace requirement that the object contain a program named `action_handler`.

## Risks and Edge Cases
The tracepoint section name is example-specific; the actual registration is through a `PROG_ARRAY`, so the function name is more important to the loader than normal auto-attachment. `bpf_printk()` is useful for demonstration but can be noisy and inappropriate for production threshold actions.

## Test Signals
Build via `make examples`, run RTLA timerlat with `--on-threshold`/BPF action support, and confirm BPF verifier acceptance plus expected `bpf_printk()` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/example/timerlat_bpf_action.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/example/timerlat_load.py -->
# sources/distributed-fs/ceph-client/tools/tracing/rtla/example/timerlat_load.py

## Purpose
`timerlat_load.py` is a sample userspace workload for timerlat's userspace timer interface. It pins itself to a CPU, optionally sets FIFO priority, waits on the per-CPU `timerlat_fd`, and performs a large read from `/dev/full` on each activation so RTLA can measure response time and auto-analysis data.

## Important APIs, Types, and Functions
The script uses `argparse` for CPU and optional priority, `os.sched_setaffinity()`, `os.sched_setscheduler()`, and opens `/sys/kernel/tracing/osnoise/per_cpu/cpuN/timerlat_fd`. It also opens `/dev/full` as an artificial data source.

## Control Flow
After parsing arguments, the script sets affinity and optional scheduler priority, opens the timerlat fd, opens `/dev/full`, then loops forever. Each iteration blocks on `timerlat_fd.read(1)` and then reads 20 MiB from `/dev/full`. It exits cleanly on Ctrl-C or I/O errors and closes both descriptors.

## State and Persistence
Runtime state is only open descriptors and process scheduling/affinity settings. It writes no files.

## Dependencies and Integration Points
It requires Python 3, sufficient privileges for scheduling and tracing file access, mounted tracefs, and a running `rtla timerlat -U` session that exposes the userspace fd.

## Risks and Edge Cases
The script assumes tracefs at `/sys/kernel/tracing`; systems using only debugfs tracing paths may need adaptation. Reading 20 MiB from `/dev/full` is a synthetic workload and may not represent application behavior. Scheduler and affinity setup failures terminate the script.

## Test Signals
Run with RTLA timerlat userspace mode active, pinned to a monitored CPU, and verify timerlat records user latency. Test permission errors, invalid CPU IDs, and optional FIFO priority failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/example/timerlat_load.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/actions.c -->
# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/actions.c

## Purpose
`actions.c` implements RTLA's threshold/end action list. Actions can save trace output, send a signal, run a shell command, or request measurement continuation after a threshold stop.

## Important APIs, Types, and Functions
Public functions are `actions_init()`, `actions_destroy()`, `actions_add_trace_output()`, `actions_add_signal()`, `actions_add_shell()`, `actions_add_continue()`, `actions_parse()`, and `actions_perform()`. Internal `actions_new()` grows the action array with `reallocarray_fatal()`. `extract_arg()` parses comma-delimited action tokens like `file=...`, `num=...`, `pid=...`, or `command=...`.

## Control Flow
Tool parsers initialize action sets and call `actions_parse()` for `--on-threshold` or `--on-end`. The parser copies the trigger string, tokenizes by comma, determines action type, validates required arguments, and appends a normalized action. Runtime calls `actions_perform()`, which walks the list in order. Trace actions call `save_trace_to_file()`, signal actions call `kill()` using parent PID when `pid=parent`, shell actions call `system()`, and continue actions set `continue_flag` and stop further action processing.

## State and Persistence
`struct actions` owns a heap array and duplicated strings. Trace actions persist trace snapshots to files; shell actions can have arbitrary side effects; signal actions affect external processes; continue actions mutate `continue_flag`.

## Dependencies and Integration Points
The implementation depends on `trace.h` for trace saving and `utils.h` fatal/string helpers. It is integrated by `common.c` threshold/end handling and by mode parsers that provide default trace filenames.

## Risks and Edge Cases
Action parsing uses `strtok()` and therefore supports only simple comma-separated syntax; shell commands containing commas are not supported. `system()` executes through the shell and carries command-injection risk if users pass untrusted strings. `actions_init()` does not explicitly clear `present[]`, so callers must allocate zeroed parent params, as current parsers do with `calloc_fatal()`. `ACTION_CONTINUE` returns immediately and suppresses later actions.

## Test Signals
Unit tests should cover valid/invalid parse strings for each action, dynamic growth, parent PID signal handling, continue ordering, trace-output instance requirements, and cleanup freeing duplicated strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/actions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/actions.h -->
# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/actions.h

## Purpose
`actions.h` defines the data structures and public API for RTLA threshold/end actions.

## Important APIs, Types, and Functions
`enum action_type` enumerates `ACTION_TRACE_OUTPUT`, `ACTION_SIGNAL`, `ACTION_SHELL`, and `ACTION_CONTINUE`. `struct action` stores type-specific data in a union. `struct actions` stores the dynamic action list, length/capacity, presence flags, a `continue_flag`, and the `trace_output_inst` external dependency used for saving trace buffers. The `for_each_action` macro iterates actions. Prototypes expose initialization, destruction, action additions, parsing, and execution.

## Control Flow and Integration
The header contains no runtime logic but is consumed by parsers in osnoise/timerlat modes and by `common_threshold_handler()`/end-of-run handling. `trace_output_inst` is filled in `run_tool()` when trace-output actions require an auxiliary trace instance.

## State and Persistence
The action list owns duplicated string data and can trigger persistent trace files or external side effects when performed.

## Dependencies and Integration Points
The header includes tracefs for `struct tracefs_instance` and `<stdbool.h>`. It is included by `common.h`, which places action sets in `struct common_params`.

## Risks and Edge Cases
The union layout requires callers to respect `type` before reading fields. `present[]` and `continue_flag` are part of runtime behavior and must be initialized consistently. `action_default_size` is a header-level `static const int`, giving each translation unit its own copy.

## Test Signals
Compile all action users, verify presence flags are set for each add function, and test trace-output actions with and without a valid `trace_output_inst`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/actions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/common.c -->
# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/common.c

## Purpose
`common.c` implements shared RTLA command execution: option parsing for common flags, signal handling, tool initialization/configuration, tracer enablement, workload setup, main-loop execution, threshold/end actions, cleanup, and shared top/hist loops.

## Important APIs, Types, and Functions
Key globals are `trace_inst`, `stop_tracing`, and `nr_cpus`. Important functions include `getopt_auto()`, `common_parse_options()`, `common_apply_config()`, `common_threshold_handler()`, `run_tool()`, `top_main_loop()`, `hist_main_loop()`, `osn_set_stop()`, and `common_usage()`. Signal helpers set `SIGINT` and optional `SIGALRM` to stop trace instances and event iteration.

## Control Flow
`run_tool()` sets `nr_cpus`, calls the mode parser and initializer, stores ops/params, applies config, enables the requested tracer, optionally adjusts scheduling/cgroup placement, creates auxiliary trace instances for trace-output actions, starts userspace timerlat workload threads when requested, enables the tool, installs stop signals, runs the mode main loop, stops user workload, prints stats, performs end actions, detects whether tracing stopped due to thresholds, optionally runs analysis, then frees everything and exits with pass/fail/error status. `top_main_loop()` and `hist_main_loop()` sleep between reads, iterate raw trace events, handle threshold stops, optionally restart tracing when a continue action was configured, and break when userspace workload exits.

## State and Persistence
The file mutates global stop state and may change process affinity, scheduling, cgroup membership, trace instances, trace buffers, event enables, and action output files. Cleanup destroys trace events and tools, action lists, and params.

## Dependencies and Integration Points
It depends on `common.h`, tracefs/libtraceevent wrappers, utilities for CPU parsing, scheduler/cgroup helpers, timerlat userspace dispatcher, and each mode's `tool_ops` implementation.

## Risks and Edge Cases
`run_tool()` exits directly, so callers cannot recover. The `out_trace` path calls `trace_events_destroy(&tool->record->trace, params->events)` even when `tool->record` is NULL in some failure paths; this relies on paths reaching that label only after record creation or on macro/function tolerance elsewhere. Cgroup error handling uses `if (!retval)` as failure, so the helper's return convention must match exactly. Signal handling uses global `trace_inst`, which supports only one active primary tool per process. Threshold continue restarts record/aa instances but assumes prior action side effects completed successfully.

## Test Signals
Exercise common options (`--cpus`, `--duration`, `--event`, filters/triggers via mode parsers, `--priority`, `--house-keeping`, `--cgroup`), signal and duration stop paths, trace-output/end actions, continue-on-threshold behavior, user workload exit, and cleanup after partial initialization failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/common.h -->
# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/common.h

## Purpose
`common.h` defines the shared RTLA data model and APIs used by osnoise, hwnoise, timerlat, top, hist, and action handling modes.

## Important APIs, Types, and Functions
`struct osnoise_context` tracks original/current tracefs osnoise settings for restoration. `struct hist_params` stores output shape flags and bucket sizing. `struct common_params` holds shared CLI state: CPU sets, trace events, buffers, timing, stop thresholds, scheduler/cgroup controls, workload choices, output formatting, action lists, and timerlat userspace parameters. `struct osnoise_tool` combines tool ops, trace instance, context, runtime data, params, start time, and auxiliary record/auto-analysis tools. `struct tool_ops` is the polymorphic command interface used by `run_tool()`.

## Control Flow and Integration
Mode modules supply a `tool_ops` table; `common.c` calls parse/init/apply/enable/main/print/analyze/free through that table. The `for_each_monitored_cpu` macro uses `common_params` CPU masks and global `nr_cpus`. Inline `should_continue_tracing()` checks threshold action state.

## State and Persistence
The header describes all persistent tracefs settings that must be saved/restored and all runtime parameters that can produce external effects such as trace files, cgroup moves, scheduler changes, and workload threads.

## Dependencies and Integration Points
It includes `actions.h`, `timerlat_u.h`, `trace.h`, and `utils.h`, so it sits at the center of RTLA's local helper stack and external tracefs/libtraceevent integration.

## Risks and Edge Cases
Large structs are shared mutable state across modules; initialization relies on zeroed allocations and sentinel constants used by `osnoise.c`. `for_each_monitored_cpu` treats a NULL `cpus` string as all CPUs even when `monitored_cpus` contents are not initialized, which is intentional but must be preserved. Adding fields requires updating parsers, cleanup, and restore paths.

## Test Signals
Compile all RTLA modes after struct changes, run mode parsers, validate CPU mask iteration, and check save/restore behavior for all `osnoise_context` fields under partial configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/osnoise.c -->
# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/osnoise.c

## Purpose
`osnoise.c` provides shared osnoise/timerlat tracefs configuration management and command dispatch for `rtla osnoise`, `rtla hwnoise`, and timerlat support. It reads, writes, saves, and restores osnoise tracefs knobs and manages `struct osnoise_tool` lifetimes.

## Important APIs, Types, and Functions
Configuration APIs include `osnoise_set_cpus()`, `osnoise_set_runtime_period()`, `osnoise_set_timerlat_period_us()`, `osnoise_set_stop_us()`, `osnoise_set_stop_total_us()`, `osnoise_set_print_stack()`, `osnoise_set_tracing_thresh()`, `osnoise_set_irq_disable()`, and `osnoise_set_workload()`, with matching restore/put helpers. Tool APIs include `osnoise_context_alloc()`, `osnoise_get_context()`, `osnoise_put_context()`, `osnoise_init_tool()`, `osnoise_init_trace_tool()`, `osnoise_destroy_tool()`, `osnoise_trace_is_off()`, `osnoise_report_missed_events()`, `osnoise_apply_config()`, `osnoise_enable()`, `osnoise_main()`, and `hwnoise_main()`.

## Control Flow
Setter functions lazily read original tracefs values, validate sentinel states, write new values, and store current values for restoration. Context reference counting defers restoration until the last user releases it. `osnoise_apply_config()` enables kernel workload, sets runtime/period defaults when absent, sets `tracing_thresh`, and delegates to `common_apply_config()`. `osnoise_enable()` starts record and primary trace instances, optionally runs warmup and clears buffers, then configures stop thresholds. Command dispatch selects top or hist mode or defaults to top.

## State and Persistence
The file mutates tracefs files under `osnoise/` plus `tracing_thresh`. It restores original values on context destruction: CPUs, runtime/period, stop thresholds, timerlat period, print stack, tracing threshold, IRQ-disable option, and workload option. Trace instances are created and destroyed through trace helpers.

## Dependencies and Integration Points
It depends on tracefs, utilities for parsing and errors, `osnoise.h`, `common.c` loops, mode ops (`osnoise_top_ops`, `osnoise_hist_ops`), and timerlat modules that reuse timerlat-specific setters.

## Risks and Edge Cases
Sentinel values use `0` or `-1` depending on field semantics; bugs can appear if a legitimate kernel value overlaps a sentinel. `osnoise_set_runtime_period()` must preserve `runtime <= period`, and its ordering logic is critical. Option parsing checks strings in `osnoise/options` with substring search, which can be sensitive to option-name overlap. `osnoise_put_irq_disable()` and workload put helpers reset original sentinels inside restore, so later checks can be redundant. Missing kernel support returns different negative values for workload handling, and callers rely on that distinction.

## Test Signals
Use tracefs fixtures or live kernels to test every setter/restore pair, partial failures, runtime/period ordering, missing osnoise options, no cdev-like optional files, command dispatch, warmup buffer cleanup, and missed-event reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/osnoise.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/osnoise.h -->
# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/osnoise.h

## Purpose
`osnoise.h` declares the osnoise/hwnoise parameter structure, sentinel constants, osnoise configuration APIs, command entry points, and external `tool_ops` tables.

## Important APIs, Types, and Functions
`enum osnoise_mode` distinguishes normal OS noise from hardware-related noise mode. `struct osnoise_params` embeds `struct common_params` and adds runtime, period, threshold, and mode. `to_osnoise_params()` converts a common pointer back to its container. Sentinel constants `OSNOISE_OPTION_INIT_VAL` and `OSNOISE_TIME_INIT_VAL` define invalid/uninitialized states. Prototypes cover context allocation, config get/set/restore, missed-event reporting, apply/enable, and command mains.

## Control Flow and Integration
The header lets top/hist mode files share the same apply/enable helpers. `rtla.c` reaches `osnoise_main()` and `hwnoise_main()`, while `timerlat.c` reuses timerlat-related osnoise setters.

## State and Persistence
The declared APIs manage tracefs-persisted osnoise settings and tool-local contexts that restore those settings on destruction.

## Dependencies and Integration Points
It includes `common.h`, which pulls in trace/action/util dependencies. It exposes `timerlat_top_ops`, `timerlat_hist_ops`, `osnoise_top_ops`, and `osnoise_hist_ops` across modules.

## Risks and Edge Cases
Sentinel semantics are part of the ABI between header and implementation; changing them can break restore logic. The container macro requires the `common` field to remain embedded in `struct osnoise_params`.

## Test Signals
Compile all osnoise/timerlat modes after changes and validate that default top/hist command dispatch still links against the declared ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/osnoise.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/osnoise_hist.c -->
# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/osnoise_hist.c

## Purpose
`osnoise_hist.c` implements `rtla osnoise hist`, a per-CPU histogram mode for OS noise samples. It configures tracefs hist triggers on `osnoise:sample_threshold`, reads the generated histogram, stores per-CPU buckets and summaries, and prints a tabular histogram.

## Important APIs, Types, and Functions
`struct osnoise_hist_cpu` stores bucket samples plus count/min/sum/max. `struct osnoise_hist_data` owns a tracefs histogram handle, per-CPU hist arrays, bucket size, and number of entries. Important functions include `osnoise_alloc_histogram()`, `osnoise_init_trace_hist()`, `osnoise_read_trace_hist()`, `osnoise_print_stats()`, `osnoise_hist_parse_args()`, `osnoise_hist_enable()`, and `osnoise_hist_main_loop()`. The file exports `struct tool_ops osnoise_hist_ops`.

## Control Flow
The parser initializes defaults of microsecond output, bucket size 1, and 256 entries, then handles osnoise runtime/period/threshold/stop options, trace actions, event filters/triggers, histogram formatting flags, warmup, buffer size, and action hooks. Enable creates the tracefs histogram before calling `osnoise_enable()`. The main loop delegates to `hist_main_loop()` and then pauses/reads the tracefs hist file. Printing emits optional headers, bucket rows, overflow counts, and summary lines.

## State and Persistence
Tracefs hist triggers are installed in the tool trace instance and destroyed by `osnoise_destroy_trace_hist()` through mode cleanup. Per-CPU samples live in heap arrays. Trace-output actions can persist trace files.

## Dependencies and Integration Points
The module depends on tracefs histogram APIs, osnoise trace events, `common_parse_options()`, `actions_parse()`, and `osnoise_apply_config()`.

## Risks and Edge Cases
Parsing the hist text uses string searches for `duration: ~`, `cpu:`, and `hitcount:`; format changes in tracefs hist output can break collection. `osnoise_destroy_trace_hist()` assumes a valid hist pointer when called on error. `--no-index` is rejected unless `--with-zeros` is set because sparse output would be ambiguous. Histogram memory scales with `nr_cpus * (entries + 1)`.

## Test Signals
Test with varying bucket/entry sizes, no samples, overflow samples, monitored CPU subsets, no-header/no-summary/no-index combinations, trace actions, threshold stops, and missing `osnoise:sample_threshold` support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/osnoise_hist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/osnoise_top.c -->
# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/osnoise_top.c

## Purpose
`osnoise_top.c` implements `rtla osnoise top` and `rtla hwnoise`, producing a live or final per-CPU summary of noise runtime, total noise, CPU availability, max samples, and noise source counts.

## Important APIs, Types, and Functions
`struct osnoise_top_cpu` stores cumulative runtime/noise, maximum noise/sample, source counters, and cycle count per CPU. `struct osnoise_top_data` owns the per-CPU array. Important functions include `osnoise_top_handler()`, `osnoise_top_header()`, `osnoise_top_print()`, `osnoise_print_stats()`, `osnoise_top_parse_args()`, `osnoise_top_apply_config()`, and `osnoise_init_top()`. The file exports `struct tool_ops osnoise_top_ops`.

## Control Flow
`osnoise_init_top()` allocates state and registers a raw event handler for `ftrace:osnoise`. The handler updates per-CPU sums and maxima from event fields. The parser handles osnoise runtime/period/threshold/stop options, auto mode, trace output, event filters/triggers, quiet/debug/duration/scheduling/cgroup options, warmup, trace buffer size, and threshold/end actions. `hwnoise` mode sets a shorter runtime than period and later enables `OSNOISE_IRQ_DISABLE`. `top_main_loop()` from `common.c` periodically collects events and calls `osnoise_print_stats()`.

## State and Persistence
Per-CPU counters are in memory. Configuration changes are applied through `osnoise_apply_config()` and restored by context cleanup. Trace actions may write snapshots.

## Dependencies and Integration Points
It depends on libtraceevent field extraction, trace sequence printing, common option parsing, actions, and osnoise tracefs configuration. Terminal color/clear behavior is enabled only for TTY output and non-quiet mode.

## Risks and Edge Cases
CPU availability percentage assumes `sum_runtime` is nonzero and uses integer scaling. Output columns depend on mode and may be wide for many CPUs or noninteractive terminals. The parser requires root and enforces runtime/period bounds, but invalid numeric strings depend on utility parsing behavior. `hwnoise` shares osnoise top ops with mode-specific configuration, so regressions in common top logic affect both tools.

## Test Signals
Run top and hwnoise modes with quiet/non-quiet output, CPU masks, auto/trace modes, threshold/end actions, terminal/non-terminal stdout, and missing event fields. Validate counters against known synthetic osnoise events where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/osnoise_top.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/rtla.c -->
# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/rtla.c

## Purpose
`rtla.c` is the top-level command dispatcher for the RTLA executable. It supports both direct aliases (`osnoise`, `hwnoise`, `timerlat`) and the normal `rtla COMMAND ...` form.

## Important APIs, Types, and Functions
`rtla_usage()` prints version, usage, and command list. `run_command()` checks an argument position and dispatches to `osnoise_main()`, `hwnoise_main()`, or `timerlat_main()`. `main()` handles alias mode, help flags, command dispatch, and usage failure.

## Control Flow
`main()` first tries `run_command(argc, argv, 0)` so an executable invoked as `osnoise` or `timerlat` can dispatch by `argv[0]`. If not an alias, it requires at least one command argument, handles `-h`/`--help`, then calls `run_command()` at position 1. Command mains generally exit directly.

## State and Persistence
This file owns no persistent state; it delegates all tracefs and runtime effects to command modules.

## Dependencies and Integration Points
It includes `osnoise.h` and `timerlat.h` and depends on those modules' command entry points. It uses the compile-time `VERSION` macro.

## Risks and Edge Cases
Alias dispatch compares the full `argv[0]` string, so invocation through a path like `/usr/bin/timerlat` may not match unless the executable name is stripped elsewhere by the environment. Unknown commands fall through to usage with exit status 1.

## Test Signals
Run `rtla -h`, `rtla --help`, `rtla osnoise -h`, `rtla timerlat -h`, unknown commands, and symlink/alias invocations to verify dispatch behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/rtla.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat.bpf.c -->
# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat.bpf.c

## Purpose
`timerlat.bpf.c` is the eBPF program used by RTLA timerlat to collect timer latency histograms and summary statistics in-kernel and to signal userspace when configured latency thresholds are reached.

## Important APIs, Types, and Functions
The program defines per-CPU array maps for IRQ/thread/user histograms and summaries, a `stop_tracing` array flag, a `signal_stop_tracing` ring buffer, and a `bpf_action` program array for optional threshold tail calls. Read-only configuration variables include `bucket_size`, `output_divisor`, `entries`, `irq_threshold`, `thread_threshold`, and `aa_only`. Helpers update map values, histograms, summaries, and stop state. The main program is `SEC("tp/osnoise/timerlat_sample") int handle_timerlat_sample(...)`.

## Control Flow
For each `osnoise:timerlat_sample` event, the program exits if `stop_tracing` is set, scales latency for output and threshold comparisons, computes a bucket, and branches by context: IRQ (`context == 0`), thread (`context == 1`), or user. It updates the appropriate histogram and summary maps unless disabled, checks thresholds in microseconds, and calls `set_stop_tracing()` on overflow. That function sets the stop flag, emits a ring-buffer notification, and tail-calls an optional action program.

## State and Persistence
All state is BPF map data scoped to the loaded object. The userspace side reads maps, updates the stop flag to restart, and can install an action program in the `PROG_ARRAY`.

## Dependencies and Integration Points
The program depends on BPF CO-RE tracepoint layout, libbpf skeleton generation, and `timerlat_bpf.c` userspace setup. It includes `timerlat_bpf.h` for summary field indexes.

## Risks and Edge Cases
Histogram overflow increments summary overflow but `update_main_hist()` drops bucket counts beyond `entries`; userspace must display overflow separately. `entries == 0` disables histograms. `aa_only` disables summary maps. Tail-call action failures are silent by design. Incorrect context values are treated as user context.

## Test Signals
Build skeletons with clang/bpftool, load on kernels with `osnoise:timerlat_sample`, verify map values for IRQ/thread/user samples, threshold ring-buffer wakeups, restart behavior, and optional action tail calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat.c -->
# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat.c

## Purpose
`timerlat.c` provides shared timerlat command behavior: applying timerlat-specific tracefs/BPF configuration, enabling trace instances and auto-analysis, handling DMA latency and CPU idle-state controls, cleanup, and command dispatch between top and hist modes.

## Important APIs, Types, and Functions
Key functions are `timerlat_apply_config()`, `timerlat_enable()`, `timerlat_analyze()`, `timerlat_free()`, and `timerlat_main()`. Static `dma_latency_fd` holds the `/dev/cpu_dma_latency` handle. The file uses `timerlat_params`, `timerlat_bpf_*()` APIs, osnoise setters for timerlat period and print stack, timerlat auto-analysis functions, and utility functions for CPU idle-state control.

## Control Flow
`timerlat_apply_config()` selects tracing mode: `RTLA_NO_BPF=1` forces tracefs mode, missing timerlat sample event disables BPF, otherwise it tries `timerlat_bpf_init()` and falls back on failure. It rejects BPF action programs in tracefs-only mode, loads action programs when requested, sets timerlat period and print-stack depth, auto-selects user workload when the kernel exposes `timerlat_fd`, otherwise selects kernel workload, then delegates common config. `timerlat_enable()` applies DMA latency and idle-state settings, creates and configures the auto-analysis trace instance unless disabled, performs warmup, starts record/AA/primary tracing or attaches BPF, and configures stop thresholds for non-BPF modes. Cleanup restores resources and destroys BPF/AA state.

## State and Persistence
The file can change `/dev/cpu_dma_latency`, CPU idle-state disable settings, tracefs timerlat/osnoise knobs, BPF maps/program attachments, and auxiliary trace instances. Cleanup closes/restores these resources.

## Dependencies and Integration Points
It integrates with `osnoise.c` context management, `common.c` run loop, timerlat top/hist ops, BPF skeleton userspace, timerlat auto-analysis, cpupower support, and timerlat userspace workload detection.

## Risks and Edge Cases
The BPF fallback path is intentionally permissive except when a BPF action was explicitly requested. Idle-state control requires libcpupower support and successful per-CPU save/restore. If `timerlat_enable()` fails after partially creating AA or changing DMA/idle settings, cleanup must still run through `run_tool()` paths. In BPF mode, stop handling differs from tracefs/mixed mode and depends on ring-buffer notifications.

## Test Signals
Test with `RTLA_NO_BPF=1`, missing BPF support, active BPF support, BPF action program loading, userspace and kernel workload modes, DMA latency, deepest idle state, warmup, AA disabled/enabled, threshold stops, and cleanup after early failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat.h -->
# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat.h

## Purpose
`timerlat.h` defines timerlat-specific parameters and tracing mode selection for RTLA, plus the shared timerlat APIs used by top/hist modes.

## Important APIs, Types, and Functions
`enum timerlat_tracing_mode` documents three modes: BPF-only, tracefs-only, and mixed mode. `struct timerlat_params` embeds `common_params` and adds timerlat period, stack printing, DMA latency, auto-analysis toggle, task dumping, deepest idle-state setting, selected tracing mode, optional BPF action program path, and stack formatting. `to_timerlat_params()` converts from embedded common params. Prototypes expose `timerlat_apply_config()`, `timerlat_main()`, `timerlat_enable()`, `timerlat_analyze()`, and `timerlat_free()`.

## Control Flow and Integration
Timerlat top/hist mode files allocate this struct and use the shared apply/enable/analyze/free functions in their `tool_ops`. `rtla.c` dispatches to `timerlat_main()`.

## State and Persistence
The struct records requested changes to tracefs timerlat period, print stack, CPU DMA latency, CPU idle states, and BPF behavior. Actual persistence is handled by implementation cleanup paths.

## Dependencies and Integration Points
It includes `osnoise.h`, and therefore inherits RTLA common/action/trace utility dependencies. `enum stack_format` comes from the local tracing/util header chain.

## Risks and Edge Cases
Mode selection must stay consistent with BPF support and action/auto-analysis requirements. Fields that use sentinel values, such as DMA latency or deepest idle state, require mode parsers to initialize them correctly.

## Test Signals
Compile timerlat top/hist and run parsers that set all fields, especially BPF action, AA-only, DMA latency, idle-state, and stack-format options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat_aa.c -->
# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat_aa.c

## Purpose
`timerlat_aa.c` implements timerlat auto-analysis. It collects timerlat, osnoise, stack, scheduler, and workqueue events in a separate trace instance, correlates them per CPU, and prints explanations for threshold-triggered IRQ or thread latency.

## Important APIs, Types, and Functions
`struct timerlat_aa_data` stores per-CPU state: current phase, IRQ/thread latency sequence and timestamps, blocking thread, timer IRQ timing, previous IRQ, interference sums, trace sequences for formatted details, current task, and kworker data. `struct timerlat_aa_context` stores global AA configuration, per-CPU data, and owning tool. Public APIs are `timerlat_aa_init()`, `timerlat_aa_destroy()`, and `timerlat_auto_analysis()`. Event handlers cover `ftrace:timerlat`, osnoise NMI/IRQ/softirq/thread noise, kernel stack, sched switch, and workqueue execute start.

## Control Flow
Initialization allocates global context, per-CPU data, trace sequences, enables/registers required events, and stores the context in a static pointer. During tracing, handlers maintain a state machine from waiting-for-IRQ to waiting-for-thread, capture IRQ latency, thread latency, blocking thread, interference durations, stack traces, and current tasks. On threshold stop, `timerlat_auto_analysis()` iterates collected events, scales thresholds to ns, selects CPUs that crossed IRQ or thread thresholds, prints per-CPU analysis, reports max exit-from-idle latency, and optionally dumps current tasks/kworker functions.

## State and Persistence
State is process-local but tied to enabled events in the AA trace instance. Cleanup unregisters handlers, disables events, destroys trace sequences, and frees per-CPU data/context. Output is printed to stdout.

## Dependencies and Integration Points
It depends on libtraceevent field extraction, tracefs event enabling, RTLA trace helpers, `timerlat.h`, and utility formatting functions. It is created by `timerlat_enable()` and invoked by `timerlat_analyze()` when tracing stopped.

## Risks and Edge Cases
The global singleton context means only one AA session is supported per process. Correlation relies on event ordering and timestamp relationships from different clocks; the code explicitly guards some negative timing cases. Many `tep_get_field_*()` calls assume expected event fields exist. `strncpy()` into fixed comm buffers may omit NUL termination for maximum-length names. `max_exit_from_idle_cpu` is printed only when a max value exists, but should still be initialized defensively if logic changes.

## Test Signals
Test IRQ-threshold and thread-threshold stops, idle-exit cases, NMI/IRQ/softirq/thread interference, stack formats, dump-tasks mode, missing optional events, unregister cleanup, and repeated init/destroy cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat_aa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat_aa.h -->
# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat_aa.h

## Purpose
`timerlat_aa.h` declares the timerlat auto-analysis interface.

## Important APIs, Types, and Functions
It exposes `timerlat_aa_init(struct osnoise_tool *tool, int dump_task, enum stack_format stack_format)`, `timerlat_aa_destroy()`, and `timerlat_auto_analysis(int irq_thresh, int thread_thresh)`.

## Control Flow and Integration
`timerlat.c` calls init while enabling timerlat, destroy during cleanup, and auto-analysis after a threshold stop. The implementation uses the passed `osnoise_tool` trace instance to register events and inspect collected trace data.

## State and Persistence
The header itself owns no state; the implementation creates a singleton context and per-CPU analysis data.

## Dependencies and Integration Points
It relies on `struct osnoise_tool` and `enum stack_format` being available through including translation units, normally via `timerlat.h`/`common.h`.

## Risks and Edge Cases
Because this header does not include the defining headers directly, include order matters. API users must pass thresholds in microseconds as expected by `timerlat_auto_analysis()`, which scales them internally.

## Test Signals
Compile consumers with strict include ordering and run timerlat with AA enabled/disabled and multiple stack formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat_aa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat_bpf.c -->
# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat_bpf.c

## Purpose
`timerlat_bpf.c` is the userspace libbpf wrapper for RTLA timerlat's BPF collection path. It opens, configures, loads, attaches, reads, restarts, and destroys the generated BPF skeleton, and can load an optional user-provided BPF action program.

## Important APIs, Types, and Functions
When `HAVE_BPF_SKEL` is defined, public functions include `timerlat_bpf_init()`, `timerlat_bpf_attach()`, `timerlat_bpf_detach()`, `timerlat_bpf_destroy()`, `timerlat_bpf_wait()`, `timerlat_bpf_restart_tracing()`, `timerlat_bpf_get_hist_value()`, `timerlat_bpf_get_summary_value()`, and `timerlat_load_bpf_action_program()`. Static globals hold the skeleton `bpf`, optional action `bpf_object *obj`, and `bpf_program *prog`.

## Control Flow
Initialization opens the skeleton, writes rodata parameters from `timerlat_params`, sizes or disables histogram maps, disables summary maps for AA-only mode, and loads/verifies the object. Attach calls skeleton attach. Wait creates a ring buffer on `signal_stop_tracing`, polls for timeout seconds, then frees it. Restart writes zero to the `stop_tracing` map. Map read helpers lookup per-CPU arrays for IRQ/thread/user maps. Action loading opens a BPF object file, loads it, finds a program named `action_handler`, and stores its fd in the skeleton `bpf_action` map.

## State and Persistence
BPF objects, maps, links, and ring buffers are kernel resources owned until destroy/detach. Action program objects remain open while registered. Restart mutates the BPF stop flag.

## Dependencies and Integration Points
It depends on generated `timerlat.skel.h`, libbpf APIs, `timerlat_params`, global `nr_cpus`, and the BPF program maps declared in `timerlat.bpf.c`. Header stubs provide no-op/failure behavior when skeleton support is absent.

## Risks and Edge Cases
`timerlat_bpf_destroy()` calls `timerlat_bpf__destroy(bpf)` without checking `bpf`, so callers should only destroy after successful or partially successful init paths that set it. Ring-buffer creation in `timerlat_bpf_wait()` is not checked before polling. Action program loading requires the exact `action_handler` function name. Per-CPU map lookups expect caller buffers sized for `nr_cpus` `long long` values.

## Test Signals
Test skeleton-enabled and disabled builds, rodata propagation, map sizing/disabling, attach/detach, threshold ring-buffer wakeup, restart map update, histogram/summary reads across CPUs, invalid action object, missing `action_handler`, and destroy after partial failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat_bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat_bpf.h -->
# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat_bpf.h

## Purpose
`timerlat_bpf.h` defines the shared summary-map indexes for timerlat BPF collection and provides the userspace BPF API, with real prototypes when BPF skeleton support is compiled in and inline failure stubs otherwise.

## Important APIs, Types, and Functions
`enum summary_field` indexes current, min, max, count, sum, overflow, and field count. Under `HAVE_BPF_SKEL`, the header declares init/attach/detach/destroy/wait/restart/map-read/action-load functions and `have_libbpf_support()`. Without skeleton support, it defines inline stubs returning failure or no-op values so the rest of RTLA can compile and fall back to tracefs.

## Control Flow and Integration
`timerlat.c` probes BPF availability by calling `timerlat_bpf_init()` and falls back when it fails. Timerlat top/hist modes use the map-read APIs when operating in BPF mode.

## State and Persistence
The header owns no state, but its APIs manage BPF skeleton kernel resources and summary/histogram maps in the implementation.

## Dependencies and Integration Points
The userspace declarations are hidden from BPF compilation with `#ifndef __bpf__`, while the enum remains available to `timerlat.bpf.c`. This keeps map indexes consistent across kernel BPF and userspace.

## Risks and Edge Cases
Consumers must tolerate stub failures and not assume libbpf support. Summary enum ordering is ABI-like between BPF program and userspace readers; reordering would corrupt interpretation of map values.

## Test Signals
Build with and without `HAVE_BPF_SKEL`, verify fallback behavior, and confirm BPF/userspace agree on every summary field index.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat_bpf.h -->
