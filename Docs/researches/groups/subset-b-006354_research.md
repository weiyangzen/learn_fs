# subset-b-006354 Research

Grouped source research for ALSA PCM core library, native file operations, memory management, format helpers, timer glue, and tracepoint declarations. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/pcm_lib.c -->
# sources/distributed-fs/ceph-client/sound/core/pcm_lib.c

## Purpose

`sources/distributed-fs/ceph-client/sound/core/pcm_lib.c` implements the reusable ALSA PCM library layer used by low-level sound drivers and by the native PCM file implementation. It handles playback silence insertion, XRUN detection, hardware pointer accounting, hardware-parameter interval arithmetic and constraints, generic PCM ioctls, period elapsed notification, read/write transfer loops, and channel-map controls. The source was read as a complete 2632-line file for this report.

## Important APIs, Types, and Functions

Key exported or cross-file APIs include `snd_pcm_set_ops`, `snd_pcm_set_sync_per_card`, `snd_pcm_update_hw_ptr`, `snd_pcm_update_state`, `snd_pcm_playback_silence`, `__snd_pcm_xrun`, `snd_pcm_lib_ioctl`, `snd_pcm_period_elapsed_under_stream_lock`, `snd_pcm_period_elapsed`, `pcm_lib_apply_appl_ptr`, `__snd_pcm_lib_xfer`, `snd_pcm_add_chmap_ctls`, `snd_pcm_std_chmaps`, and `snd_pcm_alt_chmaps`. The hardware-parameter helper set includes `snd_interval_refine`, `snd_interval_mul`, `snd_interval_div`, `snd_interval_muldivk`, `snd_interval_mulkdiv`, `snd_interval_ratnum`, `snd_interval_list`, `snd_interval_ranges`, and the `snd_pcm_hw_constraint_*` family for masks, integer/minmax/list/ranges/rational/msbits/step/power-of-two/no-resample rules.

## Control Flow

The period/update path starts from driver IRQs or process-context callbacks calling `snd_pcm_period_elapsed()` or `snd_pcm_period_elapsed_under_stream_lock()`. These call `snd_pcm_update_hw_ptr0()`, which samples the driver `pointer` callback, correlates it with jiffies and timestamps, normalizes ring-buffer wrapping against `runtime->boundary`, detects explicit `SNDRV_PCM_POS_XRUN`, invalid positions, lost interrupts, and jiffies anomalies, updates `runtime->status->hw_ptr`, and then calls `snd_pcm_update_state()`. `snd_pcm_update_state()` computes available frames, updates `avail_max`, completes draining, triggers XRUN when `stop_threshold` is reached, and wakes the appropriate wait queue.

The read/write path is centralized in `__snd_pcm_lib_xfer()`. It validates the runtime and access mode, chooses interleaved or noninterleaved copy helpers, selects a driver `copy` callback or default DMA-area copy, waits for `avail_min` via `wait_for_avail()` unless nonblocking, temporarily drops the stream lock during user/kernel buffer transfer, syncs explicit DMA buffers for CPU or device access, advances `runtime->control->appl_ptr` through `pcm_lib_apply_appl_ptr()`, and auto-starts playback/capture when thresholds are satisfied. Playback silence is inserted either to maintain a threshold ahead of the hardware pointer or to support free-running modes where the application pointer is not updated.

Hardware constraint flow is rule-driven. Drivers and PCM core add `struct snd_pcm_hw_rule` entries with dependencies, then `snd_pcm_hw_refine()` in `pcm_native.c` repeatedly applies mask and interval refinement until no dependent parameter changes. The interval helpers in this file provide the arithmetic and list/rational reduction primitives used by those rules.

## State and Persistence Behavior

All state is runtime memory in `struct snd_pcm_runtime`, `struct snd_pcm_substream`, control/status mmap records, wait queues, and ALSA control elements. This file mutates volatile stream state such as `hw_ptr_base`, `hw_ptr_interrupt`, `hw_ptr_wrap`, `hw_ptr_jiffies`, `status->hw_ptr`, `control->appl_ptr`, silence tracking fields, timestamp fields, `avail_max`, `overrange`, and `twake`. It creates channel-map kcontrols whose lifetime is tied to the PCM/card control layer. It does not persist state to disk.

## Dependencies and Integration Points

Direct dependencies include Linux allocation, scheduler/signal, time, math64, trace, and ALSA core/control/TLV/info/PCM/PCM-params/timer APIs. It relies on driver-provided `struct snd_pcm_ops` callbacks such as `pointer`, `trigger`, `copy`, `fill_silence`, `ack`, and `get_time_info`. It is tightly coupled to `pcm_native.c` for stream locks, start/stop actions, hw-param refinement, and ioctl dispatch, to `pcm_memory.c` for DMA buffer sync semantics, to `pcm_misc.c` for format widths and silence patterns, and to `pcm_trace.h` when XRUN debug tracing is enabled.

## Risks and Edge Cases

The highest-risk paths are ring-buffer wrap arithmetic, jiffies-based lost-interrupt correction, and boundary handling because wrong pointer deltas can create false XRUNs or hide real underruns/overruns. Transfer paths must preserve locking order while dropping the stream lock for user copies, and must keep `buffer_accessing` balanced. Explicit DMA sync must be present when `SNDRV_PCM_INFO_EXPLICIT_SYNC` is set or users can observe stale audio data. Constraint helpers use saturated arithmetic and open interval flags; small mistakes can make valid hardware configurations impossible or accept invalid ones. Channel-map controls assume stable runtime channel counts and valid channel masks.

## Test Signals

Useful signals include ALSA PCM playback/capture tests that exercise blocking and nonblocking reads/writes, mmap and RW access modes, linked streams, XRUN injection, pause/resume, drain/drop, silence thresholds, and no-period-wakeup hardware. Constraint tests should refine common and edge hardware configurations, rational sample rates, odd frame widths, and power-of-two/list/range constraints. Trace validation should confirm `hwptr`, `xrun`, `hw_ptr_error`, and `applptr` events under `CONFIG_SND_PCM_XRUN_DEBUG`. Static and lockdep coverage is valuable around stream locks, wait queues, user copies, and DMA sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/pcm_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/pcm_local.h -->
# sources/distributed-fs/ceph-client/sound/core/pcm_local.h

## Purpose

`sources/distributed-fs/ceph-client/sound/core/pcm_local.h` is the private header shared by the ALSA PCM core implementation files in this directory. It exposes internal interval arithmetic, hardware constraint, pointer update, timer, XRUN, linked-group, and DMA synchronization helpers that are not part of the public ALSA PCM UAPI. The source was read as a complete 83-line file for this report.

## Important APIs, Types, and Functions

The header declares `snd_pcm_known_rates`, interval helpers (`snd_interval_mul`, `snd_interval_div`, `snd_interval_muldivk`, `snd_interval_mulkdiv`), the internal mask constraint helper `snd_pcm_hw_constraint_mask`, application and hardware pointer helpers (`pcm_lib_apply_appl_ptr`, `snd_pcm_update_state`, `snd_pcm_update_hw_ptr`), `snd_pcm_playback_silence`, optional timer hooks, `__snd_pcm_xrun`, `snd_pcm_group_init`, and `snd_pcm_sync_stop`. Inline helpers include `snd_pcm_avail()`, `snd_pcm_hw_avail()`, `snd_pcm_dma_buffer_sync()`, `PCM_RUNTIME_CHECK`, and `for_each_pcm_substream`.

## Control Flow

This header has no standalone runtime flow. It wires call sites across `pcm_lib.c`, `pcm_native.c`, `pcm_memory.c`, `pcm_misc.c`, and `pcm_timer.c`: native ioctl/action paths call pointer and silence helpers from `pcm_lib.c`; transfer and mmap paths use `snd_pcm_dma_buffer_sync()`; open/close and suspend flows use group and sync-stop helpers; timer calls compile to real functions only under `CONFIG_SND_PCM_TIMER`.

## State and Persistence Behavior

No storage is owned by the header. The inline availability helpers read `runtime->control->appl_ptr`, `runtime->status->hw_ptr`, and stream direction indirectly through public ALSA helpers. `snd_pcm_dma_buffer_sync()` conditionally synchronizes the current runtime DMA buffer when `runtime->info` advertises `SNDRV_PCM_INFO_EXPLICIT_SYNC`.

## Dependencies and Integration Points

The header depends on public ALSA PCM definitions being available before inclusion. Its main integration role is to avoid exporting internal PCM core symbols through public headers while keeping implementation files source-compatible across optional timer builds. It also centralizes the explicit DMA sync policy used by transfer and pointer-control code.

## Risks and Edge Cases

Because this header provides inline helpers, semantic changes affect many PCM paths at once. `PCM_RUNTIME_CHECK` is intentionally a bug-on style guard and is not a substitute for full state validation. `snd_pcm_dma_buffer_sync()` assumes a valid runtime and DMA buffer, so callers must avoid using it before hw params or after detach. Availability helpers depend on correct stream direction and boundary-aware runtime pointer state.

## Test Signals

Compile coverage across `CONFIG_SND_PCM_TIMER`, `CONFIG_SND_PCM_XRUN_DEBUG`, explicit-sync DMA buffer configurations, playback and capture streams, and nonatomic PCM drivers is the key signal. Runtime transfer tests that exercise explicit sync and timer-disabled builds indirectly validate the header's inline choices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/pcm_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/pcm_memory.c -->
# sources/distributed-fs/ceph-client/sound/core/pcm_memory.c

## Purpose

`sources/distributed-fs/ceph-client/sound/core/pcm_memory.c` manages ALSA PCM DMA buffer preallocation, managed runtime buffer allocation, free paths, procfs tuning hooks, and per-card allocation accounting. It is the memory backend used by PCM drivers that ask the core to allocate hardware buffers before `hw_params` and release them after `hw_free`. The source was read as a complete 501-line file for this report.

## Important APIs, Types, and Functions

Module parameters include `preallocate_dma`, `maximum_substreams`, and writable `max_alloc_per_card`; `snd_minimum_buffer` sets the fallback floor. Exported APIs include `snd_pcm_lib_preallocate_free_for_all`, `snd_pcm_lib_preallocate_pages`, `snd_pcm_lib_preallocate_pages_for_all`, `snd_pcm_set_managed_buffer`, `snd_pcm_set_managed_buffer_all`, `snd_pcm_lib_malloc_pages`, and `snd_pcm_lib_free_pages`. Internal helpers include `do_alloc_pages`, `do_free_pages`, `preallocate_pcm_pages`, `preallocate_pages`, and optional verbose-procfs read/write callbacks for `prealloc` and `prealloc_max`.

## Control Flow

Preallocation starts with driver setup calling `snd_pcm_lib_preallocate_pages*()` or `snd_pcm_set_managed_buffer*()`. `preallocate_pages()` records the DMA type/device, optionally allocates an initial buffer, falls back by halving the requested size down to `snd_minimum_buffer` when allowed, stores `buffer_bytes_max` and `dma_max`, and creates procfs entries when verbose procfs is enabled. Managed mode sets `substream->managed_buffer_alloc`, causing `pcm_native.c` `snd_pcm_hw_params()` to call `snd_pcm_lib_malloc_pages()` and `snd_pcm_hw_free()` to call `snd_pcm_lib_free_pages()`.

Allocation uses `do_alloc_pages()` to reserve bytes against `card->total_pcm_alloc_bytes` under `card->memory_mutex`, choose DMA direction from playback/capture, call `snd_dma_alloc_dir_pages()`, then correct accounting if the allocator returned a larger actual buffer. Runtime allocation prefers an existing runtime buffer if large enough, then a preallocated substream buffer if sufficient, otherwise dynamically allocates a new `struct snd_dma_buffer` unless the preallocation was fixed-size. Freeing releases only dynamically allocated runtime buffers; preallocated buffers remain on the substream until explicit preallocate-free.

## State and Persistence Behavior

Persistent state is in kernel memory only: `substream->dma_buffer`, `substream->dma_max`, `substream->buffer_bytes_max`, `substream->managed_buffer_alloc`, `runtime->dma_buffer_p`, `runtime->dma_bytes`, and `card->total_pcm_alloc_bytes`. Procfs writes can change a substream's preallocated buffer while the PCM is closed, but there is no disk persistence. Allocation accounting is card-wide and protected by `card->memory_mutex`.

## Dependencies and Integration Points

The file depends on Linux DMA allocation helpers, module parameters, ALSA info/procfs support, and `pcm_local.h` for substream iteration and runtime checks. It integrates with `pcm_native.c` hw-param and hw-free paths, with `snd_pcm_mmap_data()` and transfer code through `runtime->dma_area` and `runtime->dma_bytes`, and with drivers that declare managed buffers rather than implementing their own allocation policy.

## Risks and Edge Cases

Accounting must remain balanced when allocation size differs from requested size or allocation fails. Procfs resize is blocked while `substream->runtime` exists, avoiding live buffer replacement, but changes to `buffer_bytes_max` still affect future hw-params negotiation. Fixed-size preallocation (`max == 0`) rejects dynamic larger allocations. Fallback allocation can silently provide smaller buffers than the requested preallocation, so callers must still honor `buffer_bytes_max`. Incorrect DMA direction or missing explicit sync metadata can cause coherency issues in transfer and mmap paths.

## Test Signals

Test with preallocation enabled/disabled, multiple substreams beyond `maximum_substreams`, per-card allocation caps, fixed-size managed buffers, fallback allocation under memory pressure, procfs resize while closed and busy rejection while open, and hw_params/hw_free cycles that reuse preallocated buffers then force dynamic allocation. Leak/accounting checks should verify `card->total_pcm_alloc_bytes` returns to baseline after frees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/pcm_memory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/pcm_misc.c -->
# sources/distributed-fs/ceph-client/sound/core/pcm_misc.c

## Purpose

`sources/distributed-fs/ceph-client/sound/core/pcm_misc.c` provides ALSA PCM format metadata and sample-rate helper functions. It maps every `snd_pcm_format_t` to logical width, physical width, endian property, signedness, and silence fill pattern, and exposes rate-mask conversion/intersection helpers used by hardware capability setup. The source was read as a complete 573-line file for this report.

## Important APIs, Types, and Functions

The central type is internal `struct pcm_format_data`, and the central table is `pcm_formats[]`. Exported functions include `snd_pcm_format_signed`, `snd_pcm_format_unsigned`, `snd_pcm_format_linear`, `snd_pcm_format_little_endian`, `snd_pcm_format_big_endian`, `snd_pcm_format_width`, `snd_pcm_format_physical_width`, `snd_pcm_format_size`, `snd_pcm_format_silence_64`, `snd_pcm_format_set_silence`, `snd_pcm_hw_limit_rates`, `snd_pcm_rate_to_rate_bit`, `snd_pcm_rate_bit_to_rate`, and `snd_pcm_rate_mask_intersect`.

## Control Flow

Most helpers validate that the format enum is in range, then return a field from `pcm_formats[]` or `-EINVAL` when the property is undefined. `snd_pcm_format_set_silence()` fills signed or byte-wide formats with `memset`, and fills wider unsigned or special silence patterns by copying 2-, 3-, 4-, or 8-byte samples in a loop. Rate helpers scan `snd_pcm_known_rates` from `pcm_native.c`, compute `rate_min`/`rate_max` from rate masks, convert between exact rates and bit masks, and sanitize/intersect masks with special handling for `SNDRV_PCM_RATE_CONTINUOUS` and `SNDRV_PCM_RATE_KNOT`.

## State and Persistence Behavior

The file owns immutable compile-time metadata only. It mutates caller-provided buffers in `snd_pcm_format_set_silence()` and caller-provided `struct snd_pcm_hardware` in `snd_pcm_hw_limit_rates()`. No file-backed or long-lived dynamic state is created.

## Dependencies and Integration Points

It depends on public ALSA PCM format enums and on `snd_pcm_known_rates` declared in `pcm_local.h` and defined in `pcm_native.c`. It is used by `pcm_lib.c` for silence insertion and FIFO/channel-size calculations, by `pcm_native.c` hardware constraint rules for sample bits and subformats, and by drivers that derive hardware rate min/max or validate format properties.

## Risks and Edge Cases

The metadata table is effectively ABI behavior for all PCM formats; incorrect width, endian, signedness, or silence bytes affects buffer sizing, mmap offsets, silence insertion, and user-visible capability reporting. Some formats intentionally have undefined width or endian metadata, so callers must handle `-EINVAL` or `NULL`. `snd_pcm_format_set_silence()` assumes physical widths map to supported byte loop cases; adding an unusual physical width requires updating the fill logic. Rate-mask special values are order-sensitive: continuous and knot masks collapse to the other side during intersection.

## Test Signals

Tests should enumerate all `SNDRV_PCM_FORMAT_*` values, verify widths/physical widths/endian/signedness for common linear and packed formats, validate silence buffers for unsigned linear and DSD formats, and check `snd_pcm_format_size()` overflow-sensitive inputs. Rate tests should cover known rates, unknown rates returning `SNDRV_PCM_RATE_KNOT`, single-bit reverse conversion, invalid empty masks for `snd_pcm_hw_limit_rates()`, and intersections involving continuous and knot masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/pcm_misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/pcm_native.c -->
# sources/distributed-fs/ceph-client/sound/core/pcm_native.c

## Purpose

`sources/distributed-fs/ceph-client/sound/core/pcm_native.c` is the native ALSA PCM character-device implementation. It owns stream locking, open/release, hardware/software parameter negotiation, the PCM runtime state machine, linked-substream actions, ioctl dispatch, read/write file operations, poll/fasync, status/control/data mmap, compat/old API conversion, and exported kernel ioctl/open/release helpers. The source was read as a complete 4256-line file for this report.

## Important APIs, Types, and Functions

Important exports include `snd_pcm_stream_lock`, `snd_pcm_stream_unlock`, `snd_pcm_stream_lock_irq`, `_snd_pcm_stream_lock_irqsave`, `_snd_pcm_stream_lock_irqsave_nested`, `snd_pcm_stream_unlock_irqrestore`, `snd_pcm_hw_refine`, `snd_pcm_set_state`, `snd_pcm_get_state`, `snd_pcm_sync_stop`, `snd_pcm_stop`, `snd_pcm_stop_xrun`, `snd_pcm_suspend_all`, `snd_pcm_release_substream`, `snd_pcm_open_substream`, `snd_pcm_kernel_ioctl`, `snd_pcm_lib_default_mmap`, `snd_pcm_lib_mmap_iomem`, `snd_pcm_mmap_data`, and `snd_pcm_f_ops`. Core internal structures and helpers include `struct snd_pcm_hw_params_old`, `snd_pcm_link_rwsem`, `struct action_ops`, hardware-rule helpers (`snd_pcm_hw_rule_mul`, `div`, `muldivk`, `mulkdiv`, `format`, `sample_bits`, `rate`, `buffer_bytes_max`, `subformats`), and linked-group helpers around `struct snd_pcm_group`.

## Control Flow

Open flow enters through playback/capture file operations, looks up the PCM minor, registers the file with the card, pins the module, waits for an available substream under `pcm->open_mutex`, attaches a runtime with `snd_pcm_attach_substream()`, initializes hardware constraints, calls driver `open`, completes constraints from `runtime->hw`, and records the `snd_pcm_file` in `file->private_data`. Release drops or frees hardware state, calls driver `close`, removes latency QoS, unlinks linked streams through `pcm_release_private`, detaches the runtime, wakes open waiters, unpins the module, and unregisters the card file.

Hardware-parameter flow starts with user or kernel `HW_REFINE`/`HW_PARAMS`. `snd_pcm_hw_refine()` applies mask constraints, interval constraints, and dependency rules until stable. `snd_pcm_hw_params()` serializes against live buffer access, validates state and mmap counts, chooses a concrete configuration, allocates managed buffers, calls driver `hw_params`, writes runtime format/rate/period/buffer fields, computes byte/frame alignment and boundary, clears DMA memory to avoid information leaks, updates timer resolution, moves to `SETUP`, and installs CPU latency QoS based on period time. `SW_PARAMS` then validates timestamp, threshold, avail, and silence values and updates runtime software policy.

Runtime state transitions are implemented with `struct action_ops` and shared helpers that apply pre/do/undo/post callbacks to a single stream or linked group. Start, stop, pause, suspend, resume, reset, prepare, and drain all use this mechanism with correct locking for atomic and nonatomic PCMs. Linked streams are protected by `snd_pcm_link_rwsem`, group locks, and reference-counted `struct snd_pcm_group` objects.

User interaction flows through `snd_pcm_common_ioctl()` and read/write/mmap file operations. Ioctls dispatch to info, hw/sw params, status, channel info, prepare/reset/start/link/unlink/resume/xrun/hwsync/delay/sync_ptr/drain/drop/pause/transfer/rewind/forward. Read/write convert byte counts to frames and call the library transfer helpers in `pcm_lib.c`. Poll reports readiness based on stream state and available frames. Mmap routes special offsets to status/control pages where supported and all other offsets to DMA data mapping.

## State and Persistence Behavior

State lives in `struct snd_pcm_runtime`, `struct snd_pcm_substream`, `struct snd_pcm_file`, `struct snd_pcm_group`, wait queues, mmap counters, and card/module references. Runtime fields mutated here include hardware constraints, selected hw/sw params, state, suspended state, trigger timestamps, latency QoS request, `stop_operating`, `trigger_master`, `control->appl_ptr`, `status->hw_ptr`, `boundary`, mmap status/control records, and fasync waiters. No disk persistence is used; mmap exposes kernel runtime status/control pages directly to user space on coherent architectures.

## Dependencies and Integration Points

This file depends on Linux VFS, compat, mm, file, scheduler/signal, PM QoS, DMA mapping, vmalloc, user access, poll, and ALSA core/control/info/PCM/timer/minor APIs. It integrates with low-level PCM drivers via `struct snd_pcm_ops` callbacks (`open`, `close`, `hw_params`, `hw_free`, `prepare`, `trigger`, `pointer`, `mmap`, `page`, `sync_stop`). It calls `pcm_lib.c` for pointer updates, XRUN handling, generic transfers, silence, interval math, and library ioctls; `pcm_memory.c` for managed buffer allocation; `pcm_misc.c` for format/rate metadata; `pcm_timer.c` for PCM timer notifications; `pcm_param_trace.h` for constraint tracing; and `pcm_compat.c` when `CONFIG_COMPAT` is enabled.

## Risks and Edge Cases

This file has a large concurrency surface: stream locks can be spinlocks or mutexes depending on `pcm->nonatomic`, linked-group operations must avoid ABBA deadlocks, and buffer access locks must exclude hw_params/hw_free from live read/write/mmap operations. State-machine validation is critical because many ioctls are legal only in specific states. Mmap status/control exposure is architecture and protocol-version dependent, with explicit-sync and sync-applptr flags disabling unsafe mappings. Draining linked playback streams must handle concurrent close by caching runtime fields before unlocking. Hardware constraints can reject valid devices if rule dependencies or info-derived masks are wrong. Old/compat ioctl conversion must preserve 32-bit boundaries and legacy masks.

## Test Signals

High-value tests include open contention and nonblocking open, repeated hw_params/hw_free with mmap present, all legal/illegal state transitions, linked playback/capture start/stop/drain, pause/resume/suspend fallback, sync_ptr 32/64-bit behavior, mmap status/control/data offsets, explicit-sync fallback to ioctl, read/write/readv/writev frame alignment, poll readiness across prepared/running/draining/xrun states, and `snd_pcm_kernel_ioctl()` callers such as OSS compatibility. Lockdep, KASAN, fault-injection for user copies and driver callback failures, and ALSA userspace tests (`aplay`, `arecord`, mmap clients, stress open/close) are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/pcm_native.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/pcm_param_trace.h -->
# sources/distributed-fs/ceph-client/sound/core/pcm_param_trace.h

## Purpose

`sources/distributed-fs/ceph-client/sound/core/pcm_param_trace.h` declares debug tracepoints for ALSA PCM hardware-parameter refinement. It lets developers observe mask and interval parameter changes as constraints and rules are applied during `snd_pcm_hw_refine()`. The source was read as a complete 143-line file for this report.

## Important APIs, Types, and Functions

The header defines `TRACE_SYSTEM snd_pcm`, `HW_PARAM_ENTRY`, `hw_param_labels`, and two trace events: `hw_mask_param` and `hw_interval_param`. `hw_mask_param` records device identity, stream direction, parameter type, rule index, total rules, and previous/current mask bits. `hw_interval_param` records device identity, parameter type, rule index, total rules, and previous/current interval fields including min, max, openmin, openmax, integer, and empty.

## Control Flow

There is no normal control flow beyond Linux tracepoint generation. When `CONFIG_SND_DEBUG` enables `CREATE_TRACE_POINTS` in `pcm_native.c`, the trace macros become real tracepoints. The constraint code calls `trace_hw_mask_param()` and `trace_hw_interval_param()` before/after refinements when tracepoints are enabled.

## State and Persistence Behavior

The header owns no persistent state. Trace events snapshot runtime and parameter fields into the tracing ring buffer when enabled. The captured data is diagnostic and transient.

## Dependencies and Integration Points

It depends on Linux `tracepoint.h`, ALSA hardware parameter enums, `struct snd_pcm_substream`, `struct snd_mask`, and `struct snd_interval`. It is included by `pcm_native.c` under debug builds and terminates with `TRACE_INCLUDE_PATH .`, `TRACE_INCLUDE_FILE pcm_param_trace`, and `trace/define_trace.h` for tracepoint code generation.

## Risks and Edge Cases

Tracepoint field layouts are consumed by tracing tools, so renaming or changing fields can break diagnostics. The mask trace copies eight 32-bit words and prints four, matching current mask sizing assumptions. The events dereference `substream->runtime`, so they must only be used while a valid runtime and constraints exist. Excessive tracing during hw-param refinement can be noisy on complex devices.

## Test Signals

Build with `CONFIG_SND_DEBUG` and confirm trace events are registered under the `snd_pcm` trace system. Run hw-refine and hw-params operations while enabling `hw_mask_param` and `hw_interval_param`, then verify parameter names, rule indices, previous/current values, card/device/subdevice, and playback/capture direction are coherent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/pcm_param_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/pcm_timer.c -->
# sources/distributed-fs/ceph-client/sound/core/pcm_timer.c

## Purpose

`sources/distributed-fs/ceph-client/sound/core/pcm_timer.c` implements the optional ALSA PCM timer backend. It creates one slave timer per PCM substream, computes timer resolution from runtime rate and period size, and tracks whether the timer is running so period elapsed notifications can generate timer interrupts. The source was read as a complete 129-line file for this report.

## Important APIs, Types, and Functions

Cross-file APIs are `snd_pcm_timer_resolution_change`, `snd_pcm_timer_init`, and `snd_pcm_timer_done`. Internal callbacks are `snd_pcm_timer_resolution`, `snd_pcm_timer_start`, `snd_pcm_timer_stop`, and `snd_pcm_timer_free`. The static `snd_timer_hardware snd_pcm_timer` advertises `SNDRV_TIMER_HW_AUTO | SNDRV_TIMER_HW_SLAVE`, one tick, dynamic resolution callback, and start/stop hooks.

## Control Flow

`snd_pcm_timer_init()` builds a `snd_timer_id` from card, PCM device, substream number, and stream direction, creates an ALSA timer named for the PCM direction and identifiers, assigns the PCM timer hardware callbacks, registers it as a sound device, and stores it in `substream->timer`. `snd_pcm_timer_resolution_change()` is called after hw params choose rate and period size; it reduces the nanosecond/rate/period fraction with `gcd()` and stores `runtime->timer_resolution`, or marks it invalid on overflow/out-of-range. `snd_pcm_period_elapsed_under_stream_lock()` in `pcm_lib.c` later calls `snd_timer_interrupt()` when `substream->timer_running` is set. `snd_pcm_timer_done()` frees the timer device.

## State and Persistence Behavior

State is limited to `substream->timer`, `substream->timer_running`, and `runtime->timer_resolution`. Timer objects are registered kernel sound devices tied to the card lifetime and freed during substream cleanup. No disk persistence is used.

## Dependencies and Integration Points

The file depends on Linux time/gcd and ALSA core/PCM/timer APIs. It is conditionally referenced through `pcm_local.h` when `CONFIG_SND_PCM_TIMER` is enabled. It integrates with `pcm_native.c` hw_params for resolution updates and timer event notifications, and with `pcm_lib.c` period elapsed handling for timer interrupts.

## Risks and Edge Cases

Resolution calculation must avoid arithmetic overflow and division by zero; the code guards zero rate and period size with `snd_BUG_ON()` and scales the multiplier when needed. Timer registration failure leaves `substream->timer` NULL and must be tolerated by callers. Incorrect subdevice encoding would collide playback/capture timer IDs. `timer_running` is a simple substream flag, so callers rely on stream locking and ALSA timer serialization.

## Test Signals

Build with `CONFIG_SND_PCM_TIMER`, open playback and capture substreams, verify PCM timer devices are registered with unique card/device/subdevice IDs, exercise hw_params at common and extreme rates/period sizes, confirm resolution changes after reconfiguration, start/stop timer clients, and observe timer interrupts on period elapsed. Also test timer creation failure paths through fault injection if available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/pcm_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/pcm_trace.h -->
# sources/distributed-fs/ceph-client/sound/core/pcm_trace.h

## Purpose

`sources/distributed-fs/ceph-client/sound/core/pcm_trace.h` declares ALSA PCM runtime tracepoints used mainly for XRUN and hardware/application pointer debugging. It captures hardware pointer positions, XRUN events, pointer error reasons, and application pointer movement. The source was read as a complete 149-line file for this report.

## Important APIs, Types, and Functions

The header defines `TRACE_SYSTEM snd_pcm`, `TRACE_INCLUDE_FILE pcm_trace`, and four trace events: `hwptr`, `xrun`, `hw_ptr_error`, and `applptr`. The events capture card/device/substream identifiers, stream direction, pointer positions, period and buffer sizes, current `hw_ptr_base`, availability, and string reasons for hardware pointer errors.

## Control Flow

There is no standalone algorithm. When `CONFIG_SND_PCM_XRUN_DEBUG` causes `pcm_lib.c` to define `CREATE_TRACE_POINTS`, the trace events are generated and invoked from hardware-pointer update, XRUN handling, hardware pointer anomaly reporting, and application-pointer update paths. Without that config, `pcm_lib.c` compiles trace calls to no-ops.

## State and Persistence Behavior

The header does not own state. It snapshots selected runtime fields into the kernel tracing ring buffer when events are enabled. Captured trace records are transient diagnostic data and do not affect PCM runtime state.

## Dependencies and Integration Points

It depends on Linux tracepoint infrastructure and ALSA PCM runtime structures. Integration is almost entirely with `pcm_lib.c`: `trace_hwptr()` is called after driver pointer sampling and alignment, `trace_xrun()` is called from `__snd_pcm_xrun()`, `trace_hw_ptr_error()` is called on pointer anomalies, and `trace_applptr()` is called from `pcm_lib_apply_appl_ptr()`.

## Risks and Edge Cases

Tracepoints dereference runtime/control/status fields, so call sites must only fire while the stream runtime is valid and locked appropriately. Field names and formats are part of diagnostic tooling expectations. Pointer values can wrap at `runtime->boundary`, so consumers must interpret them with buffer and period sizes. Enabling these events on busy streams can generate high event volume.

## Test Signals

Build with `CONFIG_SND_PCM_XRUN_DEBUG`, enable `snd_pcm:hwptr`, `snd_pcm:xrun`, `snd_pcm:hw_ptr_error`, and `snd_pcm:applptr` through ftrace/perf, then run playback/capture with normal period interrupts, forced XRUN, application pointer rewinds/forwards, and invalid pointer simulation from a test driver. Verify event fields match stream identity and runtime pointer state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/pcm_trace.h -->
