# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_perf.c

## Purpose

`i915_perf.c` implements the i915-specific performance stream ioctl interface for GPU observability, primarily the OA/OAR/OAM hardware counters. It lets userspace open an anonymous stream fd through `DRM_IOCTL_I915_PERF_OPEN`, read OA report records from a driver-managed GGTT circular buffer, dynamically add/remove metric configurations, and control sampling through stream ioctls. It deliberately does not use Linux core perf for OA streams because the OA unit emits tightly coupled hardware-format report records, needs stream-level configuration, and may require CPU-side filtering before exposing reports.

## Important APIs, types, and functions

The external entry points are `i915_perf_init()`, `i915_perf_fini()`, `i915_perf_register()`, `i915_perf_unregister()`, `i915_perf_open_ioctl()`, `i915_perf_add_config_ioctl()`, `i915_perf_remove_config_ioctl()`, `i915_perf_sysctl_register()`, `i915_perf_sysctl_unregister()`, `i915_perf_ioctl_version()`, `i915_perf_oa_timestamp_frequency()`, `i915_perf_get_oa_config()`, `i915_oa_config_release()`, and `i915_oa_init_reg_state()`. Internally, the file revolves around `struct perf_open_properties`, `struct i915_oa_config_bo`, the callback tables in `struct i915_oa_ops` and `struct i915_perf_stream_ops`, and platform-specific helpers for Gen7, Gen8-11, and Gen12+ OA programming.

Core implementation clusters include OA buffer management (`alloc_oa_buffer()`, `gen7_init_oa_buffer()`, `gen8_init_oa_buffer()`, `gen12_init_oa_buffer()`), report consumption (`oa_buffer_check_unlocked()`, `gen7_append_oa_reports()`, `gen8_append_oa_reports()`, `gen7_oa_read()`, `gen8_oa_read()`), context filtering (`oa_pin_context()`, `oa_get_render_ctx_id()`, `gen12_get_render_context_id()`), metric programming (`alloc_noa_wait()`, `alloc_oa_config_buffer()`, `emit_oa_config()`, `lrc_configure_all_contexts()`), stream file operations (`i915_perf_read()`, `i915_perf_poll()`, `i915_perf_ioctl()`, `i915_perf_release()`), and user configuration validation (`read_properties_unlocked()`, `alloc_oa_regs()`).

## Control flow

Initialization chooses platform operations in `i915_perf_init()`, initializes GT perf locks, metric IDR state, rate limiters, NOA delay, OA engine groups, and supported formats. Later `i915_perf_register()` exposes `/sys/.../metrics` after the DRM device is visible. Stream creation starts in `i915_perf_open_ioctl()`, which validates open flags and copies property key/value pairs without holding `gt->perf.lock`; `read_properties_unlocked()` validates engine class/instance, OA format, sampling exponent, optional SSEU, poll period, media C6 constraints, and OA format compatibility. Under `gt->perf.lock`, `i915_perf_open_ioctl_locked()` checks context ownership and privilege requirements, allocates a stream, calls `i915_oa_stream_init()`, creates an anonymous fd, and optionally enables the stream.

`i915_oa_stream_init()` enforces one exclusive stream per OA group, resolves and pins context IDs for filtered streams, allocates the NOA wait batch, obtains the metric config, holds engine PM and forcewake references, allocates the 16 MiB OA buffer, stores the stream as `exclusive_stream`, and synchronously emits the metric set through a GPU request. Enabling resets OA buffer pointers, programs OA/OAR/OAM control registers, and starts the poll hrtimer when OA reports are requested. Read/poll flow is timer-driven: `oa_poll_check_timer_cb()` calls `oa_buffer_check_unlocked()`, wakes readers, and `i915_perf_read()` delegates to Gen7 or Gen8+ parsing under `stream->lock`. Close disables the stream, releases hardware state, frees buffers/config BOs, drops context references, and clears `exclusive_stream`.

## State and persistence behavior

The persistent driver state lives in `i915->perf`, per-GT `gt->perf`, and per-open `i915_perf_stream`. `perf->metrics_idr` stores dynamic OA configs keyed by ID, protected by `metrics_lock` and RCU/krefs for concurrent lookups from query/open paths. Dynamic configs also appear as sysfs metric groups named by UUID. The stream owns an OA buffer VMA and CPU map, cached OA config batch buffers, a pinned context if single-context filtering is active, an hrtimer, wait queue, head/tail state protected by `oa_buffer.ptr_lock`, and enable state protected by `stream->lock`.

Hardware state is intentionally reset on every OA enable to avoid forwarding stale reports and to preserve the tail-pointer race workaround that depends on zeroed report header/timestamp fields. Gen8+ context images are updated so periodic OA context-control and flex EU registers survive context switches. Runtime sysctl state controls `dev.i915.perf_stream_paranoid` and `dev.i915.oa_max_sample_rate`; debugfs can tune `perf->noa_programming_delay` through integration outside this file.

## Dependencies

This file depends on DRM ioctl plumbing, GEM contexts/VMAs/objects, Intel engine PM and request submission, uncore MMIO access, GT clock utilities, RPS/RC6 state, OA register definitions from `i915_perf_oa_regs.h`, MMIO allowlist helpers from `i915_mmio_range.h`, uAPI structs and constants from `i915_drm.h`, and type definitions from `i915_perf_types.h`. It is wired into device lifecycle and ioctl tables in `i915_driver.c`, module sysctl setup in `i915_module.c`, getparam reporting in `i915_getparam.c`, selftests under `selftests/i915_perf.c`, and GVT scheduling code that uses OA register constants.

## Integration points

The user ABI is split between DRM ioctls, anonymous stream file operations, sysfs metric IDs, and sysctl limits. Mesa and profiling tools use metric IDs from sysfs, open streams with OA properties, read `drm_i915_perf_record_header` records, and may reconfigure with `I915_PERF_IOCTL_CONFIG`. The query ioctl in `i915_query.c` reads the same metric IDR to enumerate configs and copy config register arrays. Context initialization calls `i915_oa_init_reg_state()` so new render contexts inherit active OA register state. `i915_perf_ioctl_version()` advertises feature level 7 except on early MTL media-C6-broken systems, where media OA support is hidden by returning version 6.

## Risks

The high-risk areas are privilege and data isolation, OA tail/head races, hardware register programming, and lifetime ordering. Gen8-11 single-context OA reports still expose global counter values through side-band `MI_REPORT_PERF_COUNT`, so the file treats most OA access as privileged unless a platform has safer per-context behavior. `alloc_oa_regs()` must keep tight MMIO allowlists and masks; a bad allowlist can let userspace program unsafe registers. The OA tail pointer can run ahead of memory writes, so changes to report clearing or tail aging can create invalid reads or lost data. Context image modification is delicate because GPU context save/restore may race with CPU updates, and the code relies on active waits, pinned contexts, and `gt->perf.lock` ordering. Stream cleanup must release PM/forcewake, VMA, krefs, hrtimers, and sysfs state in the right order to avoid use-after-free or stuck hardware.

## Test signals

Important signals include i915 perf selftests, live OA stream tests on Haswell through Gen12/MTL, `DRM_IOCTL_I915_PERF_OPEN` privilege tests with and without `CAP_PERFMON`, high sample-rate rejection tests, dynamic add/remove/query metric config tests, poll/read behavior with small buffers and `-ENOSPC`, OA buffer overflow/report-lost status record tests, single-context filtering and hold-preemption tests, suspend/resume or runtime-PM tests while streams are active, and platform-specific validation for OAM media engines and MTL media C6 gating.
