# sources/distributed-fs/ceph-client/kernel/trace/trace_hwlat.c

## Purpose
Implements the `hwlat` tracer, a hardware/firmware latency detector. It deliberately runs high-priority sampling loops with interrupts disabled to detect time discontinuities that can indicate SMIs or other hardware-induced stalls invisible to the OS.

## Important APIs, Types, And Functions
Persistent configuration is held in `hwlat_data`, which contains a mutex, total sample count, sample window, sample width, and thread mode. `struct hwlat_kthread_data` stores the active kthread and NMI timing counters, either globally for single-thread modes or per CPU. `struct hwlat_sample` is converted into `TRACE_HWLAT` ring-buffer entries by `trace_hwlat_sample()`.

Core sampling is in `get_sample()`, with NMI accounting in `trace_hwlat_callback()`. Thread management uses `kthread_fn()`, `start_single_kthread()`, `stop_single_kthread()`, `start_per_cpu_kthreads()`, `stop_per_cpu_kthreads()`, and CPU-specific helpers. Tracefs controls are created by `init_tracefs()` and include `hwlat_detector/window`, `hwlat_detector/width`, and `hwlat_detector/mode`. Tracer lifecycle is handled by `hwlat_tracer_init()`, `hwlat_tracer_start()`, `hwlat_tracer_stop()`, and `hwlat_tracer_reset()`.

## Control Flow
When the tracer initializes, it enforces single active use through `hwlat_busy`, records the trace array, resets counters and max latency, saves the previous `tracing_thresh`, and installs a default threshold if none is set. If tracing is already on, it starts sampler threads. Start chooses one kthread for `none` and `round-robin` modes or one kthread per allowed CPU for `per-cpu` mode.

Each sampler iteration optionally migrates to the next allowed CPU, disables local interrupts, calls `get_sample()`, re-enables interrupts, and sleeps for the inactive part of the sampling window. `get_sample()` repeatedly reads `trace_clock_local()` during the active width, compares inner and outer loop deltas against the threshold, tracks the largest observed latency, records NMI time/counts while callback collection is enabled, and emits a sample if the threshold was exceeded. It also updates `tr->max_latency` and notifies latency watchers.

Mode writes stop the tracer if busy, update `hwlat_data.thread_mode` under lock, and restart it. Round-robin mode pins the single thread to successive CPUs in the tracing cpumask; if user affinity changes unexpectedly, it switches to `none`. Per-CPU mode starts/stops CPU-bound kthreads and integrates with CPU hotplug callbacks to start a new thread on online CPUs and stop on dying CPUs.

## State And Persistence
Configuration persists globally in tracefs variables: sample width, sample window, thread mode, and remembered threshold. `last_tracing_thresh` preserves user threshold across tracer runs while `save_tracing_thresh` restores the prior global threshold on reset. `hwlat_busy` prevents more than one active tracer instance. Counts reset at init; max latency resets per run. Active kthread pointers persist in either `hwlat_single_cpu_data` or per-CPU storage until stop/reset/hotplug teardown.

## Dependencies And Integration Points
The tracer depends on trace arrays and ring buffers, tracefs, kthreads, CPU masks, CPU hotplug, local IRQ control, scheduler clock/trace clock, NMI trace callbacks, latency fsnotify, and generic `trace_min_max_fops`. It integrates with the global `tracing_thresh` value and the tracing cpumask.

## Risks
The tracer intentionally introduces latency and should not run in production low-latency environments. Incorrect width/window bounds can lead to excessive CPU hogging, though generic min/max controls constrain width versus window. CPU hotplug and mode changes must coordinate `trace_types_lock`, `hwlat_data.lock`, and CPU read locks to avoid orphaned kthreads. NMI timing depends on scheduler clock safety and is disabled for generic sched clock. Round-robin affinity changes by users can degrade mode behavior and force `none`.

## Test Signals
Smoke tests include selecting the `hwlat` tracer, changing width/window/mode files, observing `TRACE_HWLAT` entries after induced latency, and confirming `tracing_thresh` is restored after reset. Per-CPU mode should start one `hwlatd/%u` thread per allowed online CPU and handle CPU hotplug. Negative tests should reject overlong or unknown mode strings and invalid width/window bounds. Runtime diagnostics should check for stuck kthreads, unexpected max-latency updates, and lockdep issues during mode changes.
