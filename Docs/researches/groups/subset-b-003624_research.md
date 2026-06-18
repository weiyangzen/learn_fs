# Research group subset-b-003624

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_perf.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_perf.c

### Purpose

`i915_perf.c` implements the i915-specific performance stream ioctl interface for GPU observability, primarily the OA/OAR/OAM hardware counters. It lets userspace open an anonymous stream fd through `DRM_IOCTL_I915_PERF_OPEN`, read OA report records from a driver-managed GGTT circular buffer, dynamically add/remove metric configurations, and control sampling through stream ioctls. It deliberately does not use Linux core perf for OA streams because the OA unit emits tightly coupled hardware-format report records, needs stream-level configuration, and may require CPU-side filtering before exposing reports.

### Important APIs, types, and functions

The external entry points are `i915_perf_init()`, `i915_perf_fini()`, `i915_perf_register()`, `i915_perf_unregister()`, `i915_perf_open_ioctl()`, `i915_perf_add_config_ioctl()`, `i915_perf_remove_config_ioctl()`, `i915_perf_sysctl_register()`, `i915_perf_sysctl_unregister()`, `i915_perf_ioctl_version()`, `i915_perf_oa_timestamp_frequency()`, `i915_perf_get_oa_config()`, `i915_oa_config_release()`, and `i915_oa_init_reg_state()`. Internally, the file revolves around `struct perf_open_properties`, `struct i915_oa_config_bo`, the callback tables in `struct i915_oa_ops` and `struct i915_perf_stream_ops`, and platform-specific helpers for Gen7, Gen8-11, and Gen12+ OA programming.

Core implementation clusters include OA buffer management (`alloc_oa_buffer()`, `gen7_init_oa_buffer()`, `gen8_init_oa_buffer()`, `gen12_init_oa_buffer()`), report consumption (`oa_buffer_check_unlocked()`, `gen7_append_oa_reports()`, `gen8_append_oa_reports()`, `gen7_oa_read()`, `gen8_oa_read()`), context filtering (`oa_pin_context()`, `oa_get_render_ctx_id()`, `gen12_get_render_context_id()`), metric programming (`alloc_noa_wait()`, `alloc_oa_config_buffer()`, `emit_oa_config()`, `lrc_configure_all_contexts()`), stream file operations (`i915_perf_read()`, `i915_perf_poll()`, `i915_perf_ioctl()`, `i915_perf_release()`), and user configuration validation (`read_properties_unlocked()`, `alloc_oa_regs()`).

### Control flow

Initialization chooses platform operations in `i915_perf_init()`, initializes GT perf locks, metric IDR state, rate limiters, NOA delay, OA engine groups, and supported formats. Later `i915_perf_register()` exposes `/sys/.../metrics` after the DRM device is visible. Stream creation starts in `i915_perf_open_ioctl()`, which validates open flags and copies property key/value pairs without holding `gt->perf.lock`; `read_properties_unlocked()` validates engine class/instance, OA format, sampling exponent, optional SSEU, poll period, media C6 constraints, and OA format compatibility. Under `gt->perf.lock`, `i915_perf_open_ioctl_locked()` checks context ownership and privilege requirements, allocates a stream, calls `i915_oa_stream_init()`, creates an anonymous fd, and optionally enables the stream.

`i915_oa_stream_init()` enforces one exclusive stream per OA group, resolves and pins context IDs for filtered streams, allocates the NOA wait batch, obtains the metric config, holds engine PM and forcewake references, allocates the 16 MiB OA buffer, stores the stream as `exclusive_stream`, and synchronously emits the metric set through a GPU request. Enabling resets OA buffer pointers, programs OA/OAR/OAM control registers, and starts the poll hrtimer when OA reports are requested. Read/poll flow is timer-driven: `oa_poll_check_timer_cb()` calls `oa_buffer_check_unlocked()`, wakes readers, and `i915_perf_read()` delegates to Gen7 or Gen8+ parsing under `stream->lock`. Close disables the stream, releases hardware state, frees buffers/config BOs, drops context references, and clears `exclusive_stream`.

### State and persistence behavior

The persistent driver state lives in `i915->perf`, per-GT `gt->perf`, and per-open `i915_perf_stream`. `perf->metrics_idr` stores dynamic OA configs keyed by ID, protected by `metrics_lock` and RCU/krefs for concurrent lookups from query/open paths. Dynamic configs also appear as sysfs metric groups named by UUID. The stream owns an OA buffer VMA and CPU map, cached OA config batch buffers, a pinned context if single-context filtering is active, an hrtimer, wait queue, head/tail state protected by `oa_buffer.ptr_lock`, and enable state protected by `stream->lock`.

Hardware state is intentionally reset on every OA enable to avoid forwarding stale reports and to preserve the tail-pointer race workaround that depends on zeroed report header/timestamp fields. Gen8+ context images are updated so periodic OA context-control and flex EU registers survive context switches. Runtime sysctl state controls `dev.i915.perf_stream_paranoid` and `dev.i915.oa_max_sample_rate`; debugfs can tune `perf->noa_programming_delay` through integration outside this file.

### Dependencies

This file depends on DRM ioctl plumbing, GEM contexts/VMAs/objects, Intel engine PM and request submission, uncore MMIO access, GT clock utilities, RPS/RC6 state, OA register definitions from `i915_perf_oa_regs.h`, MMIO allowlist helpers from `i915_mmio_range.h`, uAPI structs and constants from `i915_drm.h`, and type definitions from `i915_perf_types.h`. It is wired into device lifecycle and ioctl tables in `i915_driver.c`, module sysctl setup in `i915_module.c`, getparam reporting in `i915_getparam.c`, selftests under `selftests/i915_perf.c`, and GVT scheduling code that uses OA register constants.

### Integration points

The user ABI is split between DRM ioctls, anonymous stream file operations, sysfs metric IDs, and sysctl limits. Mesa and profiling tools use metric IDs from sysfs, open streams with OA properties, read `drm_i915_perf_record_header` records, and may reconfigure with `I915_PERF_IOCTL_CONFIG`. The query ioctl in `i915_query.c` reads the same metric IDR to enumerate configs and copy config register arrays. Context initialization calls `i915_oa_init_reg_state()` so new render contexts inherit active OA register state. `i915_perf_ioctl_version()` advertises feature level 7 except on early MTL media-C6-broken systems, where media OA support is hidden by returning version 6.

### Risks

The high-risk areas are privilege and data isolation, OA tail/head races, hardware register programming, and lifetime ordering. Gen8-11 single-context OA reports still expose global counter values through side-band `MI_REPORT_PERF_COUNT`, so the file treats most OA access as privileged unless a platform has safer per-context behavior. `alloc_oa_regs()` must keep tight MMIO allowlists and masks; a bad allowlist can let userspace program unsafe registers. The OA tail pointer can run ahead of memory writes, so changes to report clearing or tail aging can create invalid reads or lost data. Context image modification is delicate because GPU context save/restore may race with CPU updates, and the code relies on active waits, pinned contexts, and `gt->perf.lock` ordering. Stream cleanup must release PM/forcewake, VMA, krefs, hrtimers, and sysfs state in the right order to avoid use-after-free or stuck hardware.

### Test signals

Important signals include i915 perf selftests, live OA stream tests on Haswell through Gen12/MTL, `DRM_IOCTL_I915_PERF_OPEN` privilege tests with and without `CAP_PERFMON`, high sample-rate rejection tests, dynamic add/remove/query metric config tests, poll/read behavior with small buffers and `-ENOSPC`, OA buffer overflow/report-lost status record tests, single-context filtering and hold-preemption tests, suspend/resume or runtime-PM tests while streams are active, and platform-specific validation for OAM media engines and MTL media C6 gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_perf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_perf.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_perf.h

### Purpose

`i915_perf.h` is the public internal header for the i915 OA performance subsystem. It exposes lifecycle hooks, DRM ioctl handlers, OA config reference helpers, context-state initialization, metric config lookup, and OA timestamp frequency reporting to the rest of the i915 driver while keeping implementation details in `i915_perf.c` and state layout in `i915_perf_types.h`.

### Important APIs, types, and functions

The header declares `i915_perf_init()`, `i915_perf_fini()`, `i915_perf_register()`, `i915_perf_unregister()`, `i915_perf_ioctl_version()`, `i915_perf_sysctl_register()`, `i915_perf_sysctl_unregister()`, `i915_perf_open_ioctl()`, `i915_perf_add_config_ioctl()`, `i915_perf_remove_config_ioctl()`, `i915_oa_init_reg_state()`, `i915_perf_get_oa_config()`, `i915_oa_config_release()`, and `i915_perf_oa_timestamp_frequency()`. Inline helpers `i915_oa_config_get()` and `i915_oa_config_put()` wrap `kref_get_unless_zero()` and `kref_put()` for `struct i915_oa_config`.

### Control flow

There is no runtime control flow in the header beyond the inline kref helpers. Driver lifecycle code includes this header to call init/register during device bring-up and unregister/fini during teardown. The DRM ioctl table points directly at the declared ioctl handlers. Context creation and reset paths call `i915_oa_init_reg_state()` to synchronize logical-ring context images with any active OA stream.

### State and persistence behavior

The header owns no storage. It defines the access contract for `struct i915_perf` and `struct i915_oa_config` state. The kref helpers are important for persistence: dynamic metric configs can be removed from the IDR/sysfs while still referenced by open streams or query paths, and the actual memory is released only when the final reference reaches `i915_oa_config_release()`.

### Dependencies

It depends on Linux `kref`, fixed-width types, and `i915_perf_types.h`. It forward-declares DRM and i915 structures to avoid pulling heavy headers into all users. Consumers include `i915_driver.c`, `i915_getparam.c`, `i915_module.c`, `i915_query.c`, and `i915_debugfs.c`.

### Integration points

The declared ioctls are registered as render-node-allowed DRM ioctls. `i915_perf_ioctl_version()` feeds `I915_PARAM_PERF_REVISION`, and `i915_perf_oa_timestamp_frequency()` feeds timestamp-frequency getparam/query paths. The config lookup helpers are shared with query code so userspace can inspect dynamic metric register programming without opening a stream.

### Risks

The main risk is reference lifetime misuse: callers that obtain configs through `i915_perf_get_oa_config()` must eventually call `i915_oa_config_put()`. The inline `get` only succeeds if the kref is nonzero, so callers must handle `NULL`. Any prototype drift between this header and `i915_perf.c` would break ioctl or lifecycle registration.

### Test signals

Build coverage of driver lifecycle, query, and ioctl files validates the declarations. Dynamic OA config add/remove while streams or queries hold references exercises the kref helpers. Module load/unload and bind/unbind paths exercise the init/register/sysctl/fini declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_perf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_perf_oa_regs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_perf_oa_regs.h

### Purpose

`i915_perf_oa_regs.h` defines the OA/OAR/OAM MMIO register addresses and bit fields used by the i915 performance subsystem. It is a hardware-contract header: the macros describe where to program OA buffers, head/tail pointers, control/status registers, trigger registers, context controls, and selected workarounds across Gen7, Gen8, Gen12 OAG/OAR, and Gen12 OAM units.

### Important APIs, types, and functions

The exported API is entirely preprocessor macros. Major groups include Gen7 `GEN7_OACONTROL`, `GEN7_OABUFFER`, `GEN7_OASTATUS1`, `GEN7_OASTATUS2`; Gen8 `GEN8_OACONTROL`, `GEN8_OACTXCONTROL`, `GEN8_OA_DEBUG`, `GEN8_OABUFFER`, `GEN8_OAHEADPTR`, `GEN8_OATAILPTR`, `GEN8_OASTATUS`; Gen12 OAR `GEN12_OAR_OACONTROL` and `GEN12_OACTXCONTROL(base)`; Gen12 OAG `GEN12_OAG_*`; and OAM offset/function macros such as `GEN12_OAM_HEAD_POINTER(base)`, `GEN12_OAM_CONTROL(base)`, `GEN12_OAM_STATUS(base)`, trigger ranges, CEC ranges, and `GEN12_OAM_PERF_COUNTER_B(base, idx)`.

### Control flow

The header has no executable control flow. Consumers select the appropriate macro family by platform and OA unit type. `i915_perf.c` stores these registers in `struct i915_perf_regs`, programs head/tail/buffer/control/status during stream enable/disable, checks overflow/report-lost bits during read, and builds MMIO allowlists for dynamic OA config validation.

### State and persistence behavior

The file owns no mutable state but names stateful hardware locations. OA buffer state persists in hardware head/tail registers and GGTT buffer base registers. Control bits enable counters, select formats, configure periodic timers, include/disable clock ratio or context-switch reports, and invalidate OA TLBs. Status bits report buffer overflow, counter overflow, report loss, and pointer wrap state. Wrong values affect persistent GPU counter collection until reset or reprogramming.

### Dependencies

It depends on `i915_reg_defs.h` for `_MMIO()` and `REG_BIT()` helpers. It is consumed by `i915_perf.c` and GVT scheduler code, and it aligns with context-control and engine register definitions from the GT headers.

### Integration points

The register constants are the bridge between uAPI metric configuration and hardware programming. `i915_perf.c` uses them to derive OAG/OAM register sets, validate userspace-supplied register addresses, enable/disable OA units, initialize circular buffers, and emit context-control updates. GVT scheduling uses the header to understand OA state in virtualized execution.

### Risks

Incorrect offsets or bit definitions can corrupt unrelated MMIO registers, fail to stop OA counters, misreport lost data, or hang the engine. Gen12 has multiple OA units with similar but distinct register layouts; mixing OAG, OAR, and OAM macros is a likely source of platform bugs. Buffer size and pointer masks must stay consistent with `OA_BUFFER_SIZE` and report alignment assumptions in `i915_perf.c`.

### Test signals

Compile coverage of `i915_perf.c` and GVT users validates macro names. Runtime tests should open OA streams on Gen7, Gen8-11, DG2, and MTL, verify status handling on overflow/report loss, and confirm OAG/OAM register programming through register dumps or selftests. Static checks can compare MMIO allowlist ranges in `i915_perf.c` with the trigger/CEC offsets defined here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_perf_oa_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_perf_types.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_perf_types.h

### Purpose

`i915_perf_types.h` defines the shared state model for i915 OA performance streams, metric configurations, platform operation callbacks, OA register groups, and per-GT performance groups. It is included from `i915_drv.h`, so it provides the embedded `struct i915_perf` layout used across the driver.

### Important APIs, types, and functions

Important definitions include perf group IDs (`PERF_GROUP_OAG`, `PERF_GROUP_OAM_SAMEDIA_0`), `enum report_header`, `enum oa_type`, `struct i915_perf_regs`, `struct i915_oa_format`, `struct i915_oa_reg`, `struct i915_oa_config`, `struct i915_perf_stream_ops`, `struct i915_perf_stream`, `struct i915_oa_ops`, `struct i915_perf_group`, `struct i915_perf_gt`, and `struct i915_perf`. There are no functions.

`struct i915_perf_stream` is the central per-fd state: it links to `perf`, uncore, engine, optional context, stream lock, sample flags/size, enable/preemption state, OA config, cached config BOs, pinned context, specific context ID/mask, poll hrtimer/wait queue, periodic sampling settings, OA buffer VMA/vaddr/head/tail/format, NOA wait VMA, and polling period. `struct i915_perf` stores global metric sysfs/IDR state, rate limiters, cached context-image offsets, valid context bit, operation callbacks, supported format mask, and NOA programming delay.

### Control flow

The header does not execute code, but it encodes callback-driven control flow. `i915_perf.c` fills `struct i915_oa_ops` at init based on platform, then stream operations call `enable_metric_set`, `oa_enable`, `read`, `oa_disable`, and validation callbacks. `struct i915_perf_stream_ops` abstracts stream fd operations so future stream types could share open/read/poll/ioctl/release plumbing.

### State and persistence behavior

The structs describe both persistent device-level state and transient stream state. `metrics_idr` and sysfs metric groups persist for the device lifetime or until removed by ioctl. `exclusive_stream` persists while an OA group is claimed and prevents concurrent incompatible streams. The OA buffer state tracks driver-owned head and verified tail instead of trusting hardware head updates. Krefs and RCU in `i915_oa_config` allow configs to outlive removal while streams or query calls still use them.

### Dependencies

The header depends on Linux atomic, hrtimer, llist, poll, sysfs, UUID, waitqueue, and uAPI types; GT engine/SSEU types; register definitions; uncore; and wakeref types. It is intentionally broad because `struct drm_i915_private` embeds `struct i915_perf`.

### Integration points

`i915_perf.c` is the primary implementation user. `i915_drv.h` embeds `struct i915_perf`, GT and engine structures reference `i915_perf_gt` and OA groups, `i915_query.c` reads `metrics_idr` and `i915_oa_config` register arrays, and debugfs touches `noa_programming_delay`.

### Risks

Changing these layouts has wide blast radius because they are embedded in core device/GT objects. Locking comments are part of the contract: `metrics_lock`, per-GT `perf.lock`, `stream->lock`, and `oa_buffer.ptr_lock` cover different concurrency domains. Adding fields without clear ownership can introduce stream teardown races, hrtimer use-after-free, or config lifetime bugs. Format metadata must match report parsing assumptions, including header width and report size.

### Test signals

Build all i915 objects that include `i915_drv.h`, run OA stream open/read/reconfigure tests, dynamic config add/remove/query tests, context filtering tests, and lockdep-enabled stress tests around stream close while polling or reading. ABI-sensitive changes should be checked against Mesa/tool expectations for report sizes and formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_perf_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_pmu.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_pmu.c

### Purpose

`i915_pmu.c` implements the Linux perf PMU provider for i915 counters that fit the perf scalar-counter model: per-engine busy/wait/semaphore residency, requested and actual GT frequency, interrupts, RC6 residency, and software GT awake time. Unlike OA streams in `i915_perf.c`, these are read as perf events through `/sys/bus/event_source/devices/i915`.

### Important APIs, types, and functions

The external functions are `i915_pmu_register()`, `i915_pmu_unregister()`, `i915_pmu_gt_parked()`, and `i915_pmu_gt_unparked()`. Perf callbacks include `i915_pmu_event_init()`, `i915_pmu_event_add()`, `i915_pmu_event_del()`, `i915_pmu_event_start()`, `i915_pmu_event_stop()`, and `i915_pmu_event_read()`. Sampling helpers include `i915_sample()`, `engines_sample()`, `engine_sample()`, `frequency_sample()`, `get_rc6()`, and `init_rc6()`. Sysfs event construction is handled by `create_event_attributes()` and `free_event_attributes()`.

### Control flow

Registration initializes `pmu->lock`, hrtimer state, initial RC6 samples, a unique PMU name for dGPU devices, sysfs format/events attributes, perf callback pointers, and then calls `perf_pmu_register()`. Event initialization rejects unsupported perf modes, validates event type/config/cpu, looks up engine events or non-engine counter support, and holds a DRM device ref for top-level events. Starting an event increments global and per-engine refcounts under `pmu->lock`, sets enable bits, possibly starts the hrtimer, and snapshots the current counter. Stopping reads an update if requested, decrements refcounts, clears enable bits when last users disappear, and disables the timer when no sampled counters need it.

The hrtimer runs at `FREQUENCY` 200 Hz when needed. It samples awake GTs, engine wait/sema/busy state from ring registers when hardware busy stats are unavailable, and frequency counters from RPS. RC6 is special: if the GT is asleep, `get_rc6()` approximates residency by adding time since park to the last real hardware value while keeping the reported value monotonic.

### State and persistence behavior

`struct i915_pmu` tracks registration state, PMU name, enable bitmask, per-bit refcounts, timer state, last timer timestamp, unparked GT mask, current samples for up to `I915_PMU_MAX_GT`, sleep timestamps for RC6 approximation, interrupt count, and dynamically allocated sysfs attributes. Per-engine PMU state lives in each `intel_engine_cs` and stores engine sample counters/refcounts. The perf core stores per-event `prev_count` and accumulated `event->count`.

### Dependencies

The file depends on Linux perf_event and hrtimer APIs, runtime PM, DRM logging, Intel GT/engine/RPS/RC6 helpers, engine user lookup, and uAPI PMU config encoding from `i915_drm.h`. It is built only when `CONFIG_PERF_EVENTS` enables the declarations in `i915_pmu.h`.

### Integration points

`i915_driver.c` registers and unregisters the PMU during driver registration. GT park/unpark hooks notify this file so RC6 state and timer activity remain accurate across runtime power transitions. Userspace discovers event names and units via perf sysfs attributes such as `actual-frequency`, `rc6-residency`, `interrupts`, and per-engine `busy`, `wait`, and `sema`.

### Risks

The main risks are counter correctness under runtime PM, timer/refcount races, and platform-specific register access. Gen7 requires exclusive MMIO cacheline access to avoid hangs, so engine sampling takes the uncore lock. Frequency sampling intentionally avoids forcewake and may fall back to requested/current values when reads return zero. The fixed `I915_PMU_MAX_GT` and config bit packing must match uAPI and platform limits. Incorrect enable_count handling can leave timers running forever or stop sampling while events are active.

### Test signals

Use `perf list` and `perf stat -e i915/.../` to validate sysfs discovery and event reads. Exercise engine busy/wait/sema with GPU workloads, RC6 while idle and across runtime suspend, frequency counters during RPS changes, multi-GT naming on platforms with extra GTs, and register/unregister during driver unload. Lockdep and timer stress around rapid perf event open/close is valuable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_pmu.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_pmu.h

### Purpose

`i915_pmu.h` defines the i915 perf-event PMU state and public hooks used by driver lifecycle and GT power-management code. It describes which non-engine events need enable/disable tracking and how the sampling timer stores global samples.

### Important APIs, types, and functions

The header defines `enum i915_pmu_tracked_events`, sampler indices such as `__I915_SAMPLE_FREQ_ACT`, `__I915_SAMPLE_FREQ_REQ`, and `__I915_SAMPLE_RC6`, `I915_PMU_MAX_GT`, `I915_PMU_MASK_BITS`, `I915_ENGINE_SAMPLE_COUNT`, `struct i915_pmu_sample`, and `struct i915_pmu`. When `CONFIG_PERF_EVENTS` is enabled it declares `i915_pmu_register()`, `i915_pmu_unregister()`, `i915_pmu_gt_parked()`, and `i915_pmu_gt_unparked()`; otherwise it provides empty inline stubs.

### Control flow

The header itself has only conditional compilation flow. In perf-enabled builds, driver registration calls into `i915_pmu.c`; in non-perf builds, callers compile away the hooks. The event bit layout described here drives `config_bit()`, refcount arrays, timer enable decisions, and per-GT sample indexing in the implementation.

### State and persistence behavior

`struct i915_pmu` stores the registered PMU object, name, spinlock, unparked mask, hrtimer, global enable bitmask, timer timestamp, per-event refcounts, timer-enabled flag, per-GT sample arrays, RC6 sleep timestamps, interrupt counter, and sysfs attribute storage. These fields persist for the device lifetime between PMU registration and unregister.

### Dependencies

It depends on Linux hrtimer, perf_event, spinlock types, and i915 uAPI PMU constants. It forward declares `drm_i915_private` and `intel_gt` so lifecycle users do not need the full implementation.

### Integration points

`struct drm_i915_private` embeds `struct i915_pmu`. Driver registration calls `i915_pmu_register()` after core device setup and `i915_pmu_unregister()` during teardown. GT runtime PM calls parked/unparked hooks to synchronize RC6 approximation and sampling timers.

### Risks

Bit layout changes are ABI-sensitive because event configs map to enable bits and refcount indexes. `I915_PMU_MAX_GT` must match the implementation's supported GT indexing. Stubs must remain side-effect free for non-perf builds. Because `irq_count` is intentionally an unsigned long rather than atomic, writers/readers rely on tolerant wraparound semantics.

### Test signals

Build with and without `CONFIG_PERF_EVENTS`. Run perf event discovery and sampling tests on single-GT and multi-GT platforms. Exercise GT park/unpark paths and verify no unresolved symbols or dead code assumptions in non-perf builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_priolist_types.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_priolist_types.h

### Purpose

`i915_priolist_types.h` defines the request-priority constants and the scheduler priority-list node used by i915 request scheduling. It is small but important because it encodes special internal priorities above and below the user-visible context priority range.

### Important APIs, types, and functions

The exported constants are `I915_PRIORITY_MIN`, `I915_PRIORITY_NORMAL`, `I915_PRIORITY_MAX`, `I915_PRIORITY_HEARTBEAT`, `I915_PRIORITY_DISPLAY`, `I915_PRIORITY_INVALID`, `I915_PRIORITY_UNPREEMPTABLE`, and `I915_PRIORITY_BARRIER`. `struct i915_priolist` contains a `requests` list, an RB-tree `node`, and the integer `priority`.

### Control flow

There is no executable control flow. Scheduler code inserts priolist nodes into RB trees by priority and keeps requests with the same priority on the embedded list. Special priorities influence preemption and barrier behavior when the scheduler chooses runnable requests.

### State and persistence behavior

The priolist nodes are in-memory scheduler state. They persist while requests are queued at a priority level and are freed when no longer needed. `I915_PRIORITY_UNPREEMPTABLE` is specifically used for performance-query requests that must not be preempted once active, which ties this header to the OA/perf query safety model.

### Dependencies

The header depends on Linux list and rbtree types plus i915 uAPI priority constants from `i915_drm.h`. It is included by `i915_scheduler_types.h` and scheduler helpers.

### Integration points

Scheduler structures embed `struct i915_priolist`, and scheduler code uses the constants to order normal user requests, heartbeat pulses, display-critical work, barriers, and unpreemptable perf-query work. The perf-query comment documents why some requests need to remain active until completion.

### Risks

Changing numeric ordering can break preemption semantics, starve user workloads, or allow performance queries to be preempted in a way that corrupts measurements. `I915_PRIORITY_INVALID` relies on `INT_MIN`, and `I915_PRIORITY_UNPREEMPTABLE`/`BARRIER` rely on the top of the integer range, so arithmetic around priorities must avoid overflow.

### Test signals

Scheduler selftests, heartbeat tests, display pageflip latency tests, and OA/perf query tests that require unpreemptable execution are the main signals. Stress tests with mixed user priorities should verify no starvation or incorrect RB-tree ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_priolist_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_ptr_util.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_ptr_util.h

### Purpose

`i915_ptr_util.h` provides low-level pointer tagging and conversion helpers used by i915 code that stores small bitfields in naturally aligned pointers or needs sparse-friendly container calculations for `__user` pointers.

### Important APIs, types, and functions

The macro API includes `ptr_mask_bits()`, `ptr_unmask_bits()`, `ptr_unpack_bits()`, `ptr_pack_bits()`, `ptr_dec()`, `ptr_inc()`, page-specific wrappers `page_mask_bits()`, `page_unmask_bits()`, `page_pack_bits()`, `page_unpack_bits()`, `u64_to_ptr(T, x)`, and `container_of_user()`. The only function is `static __always_inline ptrdiff_t ptrdiff(const void *a, const void *b)`.

### Control flow

All helpers expand inline at call sites. Pack/unpack helpers cast through `unsigned long`, mask low bits using `BIT(n)`, and cast back to the original pointer type. `ptr_pack_bits()` asserts with `GEM_BUG_ON()` if the supplied bits do not fit in the low `n` bits. `container_of_user()` performs compile-time member type checks and returns a `type __user *`.

### State and persistence behavior

The header stores no state. It defines reversible encodings where low pointer bits carry flags and the remaining high bits carry the aligned pointer. The correctness depends on callers only packing bits into alignment-guaranteed zero bits, especially page-aligned addresses for the page wrappers.

### Dependencies

It depends on Linux types and standard kernel helper macros such as `BIT`, `typecheck`, `BUILD_BUG_ON_MSG`, `__same_type`, `typeof_member`, `offsetof`, and i915 `GEM_BUG_ON` from included contexts.

### Integration points

This is a utility header for i915 internals. It is suitable for GEM/VM data structures that tag flags in object or page pointers, uAPI conversion code that receives 64-bit pointer values, and sparse-checked user-pointer container calculations.

### Risks

Pointer tagging is architecture- and alignment-sensitive. Packing too many bits, passing unaligned pointers, or applying `ptr_inc()`/`ptr_dec()` to tagged pointers can corrupt addresses. `ptrdiff()` subtracts `void *`, which is accepted as a kernel/GNU extension but should not be treated as portable ISO C. `u64_to_ptr()` should not be used for unchecked userspace addresses when `u64_to_user_ptr()` is the correct API.

### Test signals

Build coverage with sparse is important for `container_of_user()`. Unit-style checks should round-trip pack/unpack for aligned pointers, assert rejection of out-of-range tag bits in debug builds, and verify page tag helpers preserve page addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_ptr_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_pvinfo.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_pvinfo.h

### Purpose

`i915_pvinfo.h` defines the paravirtualized vGPU shared-info page layout used between an i915 guest driver and a host emulator/GVT device model. It assigns the MMIO page offset, magic/version values, guest-to-host notification IDs, capability bits, and the packed `struct vgt_if` shared memory ABI.

### Important APIs, types, and functions

Important constants include `VGT_PVINFO_PAGE`, `VGT_PVINFO_SIZE`, `VGT_MAGIC`, `VGT_VERSION_MAJOR`, `VGT_VERSION_MINOR`, guest-to-vGPU notification enum values for PPGTT and execlist context create/destroy, capability bits `VGT_CAPS_FULL_PPGTT`, `VGT_CAPS_HWSP_EMULATION`, and `VGT_CAPS_HUGE_GTT`, display-ready values, plus `vgtif_offset(x)` and `vgtif_reg(x)`. `struct vgt_if` is the central packed ABI structure.

### Control flow

The header has no executable flow. Guest and host code map or emulate the PVINFO MMIO page, validate magic/version, read capability/resource fields, and write notification or response fields. The `vgtif_reg()` macro converts structure fields into `_MMIO()` register addresses.

### State and persistence behavior

The shared page persists as virtual MMIO state. The upper half contains host-provided identity, capabilities, and assigned aperture/non-mappable GMADR/fence resources. The lower half contains guest-to-host state such as display readiness, notification type, cursor hot spots, PDP values, and execlist context descriptor fields. The structure is `__packed`, so field offsets are ABI and must not drift.

### Dependencies

It depends on Linux types, `_MMIO()` availability from including contexts, and host/guest agreement on GVT ABI semantics. Observed consumers include GVT MMIO tables, GTT handling, vGPU setup, firmware, command parser, scheduler, framebuffer decoder, and `i915_vgpu.c`.

### Integration points

GVT code uses this header to expose PVINFO registers to guests and interpret guest notifications. Guest-side i915 vGPU detection and setup use `VGT_MAGIC`, capabilities, and resource ballooning fields. Display handoff uses `display_ready`, and execlist/PPGTT virtualization uses the notification and descriptor fields.

### Risks

Any layout change breaks guest/host ABI compatibility. The historical misspelling of "balooning" is present in comments only, but field meaning is fixed. Incorrect offset calculations can cause guest writes to hit the wrong virtual register. Resource fields describe only one contiguous region per VM, so code assuming scattered regions would be incompatible with this ABI.

### Test signals

GVT guest boot, vGPU resource ballooning, PPGTT create/destroy notifications, execlist context lifecycle, display owner switch, and migration/restore tests are relevant. Static layout checks against expected offsets are valuable because the structure is a packed MMIO ABI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_pvinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_query.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_query.c

### Purpose

`i915_query.c` implements `DRM_IOCTL_I915_QUERY`, a multiplexed read-only ioctl for userspace discovery of i915 topology, engines, OA metric configs, memory regions, hardware configuration blobs, geometry subslices, and GuC submission version. It follows the common query pattern where a zero length asks for the required size and a nonzero length copies structured data to userspace.

### Important APIs, types, and functions

The external entry point is `i915_query_ioctl()`. Query handlers are stored in `i915_query_funcs[]` and include `query_topology_info()`, `query_engine_info()`, `query_perf_config()`, `query_memregion_info()`, `query_hwconfig_blob()`, `query_geometry_subslices()`, and `query_guc_submission_version()`. Supporting helpers include `copy_query_item()`, `fill_topology_info()`, `query_perf_config_data()`, `query_perf_config_list()`, and register-copy helpers for OA configs.

### Control flow

`i915_query_ioctl()` validates top-level flags, iterates user-provided `drm_i915_query_item` entries, rejects query ID zero and out-of-range IDs, applies `array_index_nospec()`, calls the selected handler, and writes the handler return value back to `item.length` when it differs. Each handler validates item flags, handles length-zero size discovery, validates reserved fields in user-provided headers, and copies output with `copy_to_user()` or unsafe user access blocks where appropriate.

Topology queries fill slice, subslice, and EU masks from `sseu_dev_info`; geometry-subsslice queries are restricted to XeHP-style render engines. Engine queries enumerate UABI engines and report class, instance, logical instance, flags, and capabilities. Perf config queries either list config IDs or return register arrays for a config by ID or UUID. Memory-region queries enumerate non-private regions and only report live unallocated sizes to `perfmon_capable()` callers. HW config returns the GT hwconfig blob if available. GuC submission version returns zero branch plus GuC major/minor/patch when GuC submission is active.

### State and persistence behavior

The ioctl is read-only from the driver's perspective except for copying lengths back to userspace. It snapshots mutable driver state: engine lists, memory-region availability, GT SSEU info, GuC version, hwconfig blobs, and `perf->metrics_idr`. OA configs are protected by RCU/krefs through `i915_perf_get_oa_config()` or explicit RCU scanning for UUID lookup. The returned data is not persistent; userspace must tolerate changes between size query and data query.

### Dependencies

The file depends on DRM user-copy helpers, nospec indexing, `i915_drv.h`, `i915_perf.h`, `i915_query.h`, engine user lookup, SSEU copy helpers, memory-region helpers, GuC state, and uAPI structures from `i915_drm.h`.

### Integration points

`i915_driver.c` registers this handler as render-node allowed. Mesa, compute runtimes, and diagnostics use it to discover engine topology, memory regions, and metric configs. The perf-config paths integrate tightly with dynamic OA config management in `i915_perf.c`, while memory-region reporting integrates with region accounting and perf capability policy.

### Risks

The main risks are ABI validation, user-copy correctness, and stale snapshots. Query handlers must reject nonzero reserved fields and invalid flags to preserve forward compatibility. Size calculations must avoid overflow and match uAPI struct layout. Perf config listing grows dynamically, so the allocation loop must tolerate concurrent config changes. Returning unallocated memory to unprivileged callers would leak system activity, so the capability check is security-relevant.

### Test signals

IGT query tests should cover zero-length size discovery, undersized buffers, reserved-field rejection, invalid IDs, topology mask sizes, engine enumeration, memory-region visibility with and without `CAP_PERFMON`, perf config list/data by ID and UUID, concurrent config add/remove during queries, hwconfig absence, geometry subslice validation, and GuC submission disabled/enabled behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_query.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_query.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_query.h

### Purpose

`i915_query.h` declares the DRM query ioctl entry point for the i915 driver. It is a narrow internal header used by the driver ioctl table to expose the implementation in `i915_query.c`.

### Important APIs, types, and functions

The only exported function is `int i915_query_ioctl(struct drm_device *dev, void *data, struct drm_file *file);`. The header forward declares `struct drm_device` and `struct drm_file` and uses an include guard.

### Control flow

There is no runtime control flow in the header. `i915_driver.c` includes it and registers `i915_query_ioctl` as the handler for `DRM_IOCTL_I915_QUERY`; all dispatch to individual query IDs happens in the C file.

### State and persistence behavior

The header owns no state. It defines the call boundary for a read-only discovery ioctl that snapshots driver state into userspace buffers.

### Dependencies

It depends only on DRM forward declarations. The implementation pulls in i915 and uAPI details separately.

### Integration points

The sole integration point is the i915 DRM ioctl table. Keeping this header small limits rebuild coupling for code that only needs to register the ioctl handler.

### Risks

Risks are limited to prototype drift or accidental inclusion of heavy dependencies. Any signature change must match the DRM ioctl handler convention exactly.

### Test signals

Build coverage of `i915_driver.c` and `i915_query.c` validates the declaration. Runtime query ioctl tests validate the actual implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_query.h -->
