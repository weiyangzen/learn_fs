# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_pmu.c

## Purpose

`i915_pmu.c` implements the Linux perf PMU provider for i915 counters that fit the perf scalar-counter model: per-engine busy/wait/semaphore residency, requested and actual GT frequency, interrupts, RC6 residency, and software GT awake time. Unlike OA streams in `i915_perf.c`, these are read as perf events through `/sys/bus/event_source/devices/i915`.

## Important APIs, types, and functions

The external functions are `i915_pmu_register()`, `i915_pmu_unregister()`, `i915_pmu_gt_parked()`, and `i915_pmu_gt_unparked()`. Perf callbacks include `i915_pmu_event_init()`, `i915_pmu_event_add()`, `i915_pmu_event_del()`, `i915_pmu_event_start()`, `i915_pmu_event_stop()`, and `i915_pmu_event_read()`. Sampling helpers include `i915_sample()`, `engines_sample()`, `engine_sample()`, `frequency_sample()`, `get_rc6()`, and `init_rc6()`. Sysfs event construction is handled by `create_event_attributes()` and `free_event_attributes()`.

## Control flow

Registration initializes `pmu->lock`, hrtimer state, initial RC6 samples, a unique PMU name for dGPU devices, sysfs format/events attributes, perf callback pointers, and then calls `perf_pmu_register()`. Event initialization rejects unsupported perf modes, validates event type/config/cpu, looks up engine events or non-engine counter support, and holds a DRM device ref for top-level events. Starting an event increments global and per-engine refcounts under `pmu->lock`, sets enable bits, possibly starts the hrtimer, and snapshots the current counter. Stopping reads an update if requested, decrements refcounts, clears enable bits when last users disappear, and disables the timer when no sampled counters need it.

The hrtimer runs at `FREQUENCY` 200 Hz when needed. It samples awake GTs, engine wait/sema/busy state from ring registers when hardware busy stats are unavailable, and frequency counters from RPS. RC6 is special: if the GT is asleep, `get_rc6()` approximates residency by adding time since park to the last real hardware value while keeping the reported value monotonic.

## State and persistence behavior

`struct i915_pmu` tracks registration state, PMU name, enable bitmask, per-bit refcounts, timer state, last timer timestamp, unparked GT mask, current samples for up to `I915_PMU_MAX_GT`, sleep timestamps for RC6 approximation, interrupt count, and dynamically allocated sysfs attributes. Per-engine PMU state lives in each `intel_engine_cs` and stores engine sample counters/refcounts. The perf core stores per-event `prev_count` and accumulated `event->count`.

## Dependencies

The file depends on Linux perf_event and hrtimer APIs, runtime PM, DRM logging, Intel GT/engine/RPS/RC6 helpers, engine user lookup, and uAPI PMU config encoding from `i915_drm.h`. It is built only when `CONFIG_PERF_EVENTS` enables the declarations in `i915_pmu.h`.

## Integration points

`i915_driver.c` registers and unregisters the PMU during driver registration. GT park/unpark hooks notify this file so RC6 state and timer activity remain accurate across runtime power transitions. Userspace discovers event names and units via perf sysfs attributes such as `actual-frequency`, `rc6-residency`, `interrupts`, and per-engine `busy`, `wait`, and `sema`.

## Risks

The main risks are counter correctness under runtime PM, timer/refcount races, and platform-specific register access. Gen7 requires exclusive MMIO cacheline access to avoid hangs, so engine sampling takes the uncore lock. Frequency sampling intentionally avoids forcewake and may fall back to requested/current values when reads return zero. The fixed `I915_PMU_MAX_GT` and config bit packing must match uAPI and platform limits. Incorrect enable_count handling can leave timers running forever or stop sampling while events are active.

## Test signals

Use `perf list` and `perf stat -e i915/.../` to validate sysfs discovery and event reads. Exercise engine busy/wait/sema with GPU workloads, RC6 while idle and across runtime suspend, frequency counters during RPS changes, multi-GT naming on platforms with extra GTs, and register/unregister during driver unload. Lockdep and timer stress around rapid perf event open/close is valuable.
