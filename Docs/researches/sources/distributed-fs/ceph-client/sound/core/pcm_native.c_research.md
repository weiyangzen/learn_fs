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
