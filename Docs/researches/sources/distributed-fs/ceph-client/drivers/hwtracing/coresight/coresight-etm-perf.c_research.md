# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm-perf.c

## Purpose

This file implements the CoreSight ETM perf PMU front end. It registers the `cs_etm`-style PMU with perf, publishes perf format/sink/event sysfs attributes, allocates AUX trace session state, builds per-CPU CoreSight paths to compatible sinks, starts/stops ETM sources for perf events, supports AUX pause/resume, and translates perf address filters into ETM range or start/stop filters.

## Important APIs, Types, and Functions

- `struct etm_ctxt` stores the per-CPU `perf_output_handle` plus a stable `struct etm_event_data *`. The extra pointer is required because sink IRQ handlers may end and clear the perf handle before `etm_event_stop()` runs.
- `DEFINE_PER_CPU(struct etm_ctxt, etm_ctxt)` stores active perf tracing state per CPU.
- `DEFINE_PER_CPU(struct coresight_device *, csdev_src)` maps CPUs to ETM source devices registered by ETM3x/ETM4x drivers through `etm_perf_symlink()`.
- PMU format attributes are generated with `GEN_PMU_FORMAT_ATTR()` for `cycacc`, `timestamp`, `retstack`, `sinkid`, and ETM4x-only fields such as `contextid`, `preset`, `configid`, `branch_broadcast`, and `cc_threshold`.
- `etm_event_init()` validates the perf event type and allocates `event->hw.addr_filters`.
- `etm_setup_aux()` is the main session setup hook. It allocates `struct etm_event_data`, activates a selected CoreSight syscfg config, chooses a user-selected or default sink, builds a path from each eligible ETM source to that sink, assigns trace IDs, starts perf trace-ID allocation for the sink map, and allocates a sink AUX buffer.
- `etm_event_start()`, `etm_event_stop()`, and `etm_event_pause()` implement perf start, stop, and AUX pause semantics around CoreSight path/source enablement.
- `etm_addr_filters_validate()` rejects more than `ETM_ADDR_CMP_MAX` filters and rejects mixing range filters with start/stop filters.
- `etm_addr_filters_sync()` copies perf-resolved filter ranges into `struct etm_filters`.
- `etm_perf_symlink()` creates/removes `cpuN` symlinks from the PMU device to ETM source devices and updates `csdev_src`.
- `etm_perf_add_symlink_sink()` and `etm_perf_add_symlink_cscfg()` publish sink and CoreSight system configuration choices under the PMU `sinks` and `events` groups.
- `etm_perf_init()` registers the PMU with `PERF_PMU_CAP_EXCLUSIVE`, `PERF_PMU_CAP_ITRACE`, and `PERF_PMU_CAP_AUX_PAUSE`.

## Control Flow

Perf opens a CoreSight ETM event through `etm_event_init()`, which allocates filter storage and attaches `etm_event_destroy()` as the cleanup callback. During AUX setup, `etm_setup_aux()` builds the event's CPU mask from `event->cpu` or all present CPUs. It optionally resolves `sinkid`, activates `configid`, walks every CPU in the mask, skips CPUs without an ETM source or without required AUX pause callbacks, selects a compatible sink, builds the CoreSight path, assigns a trace ID, and stores the path in per-CPU storage inside `event_data`.

When perf schedules the event on a CPU, `etm_event_start()` begins perf AUX output, checks that the CPU survived setup filtering, enables the CoreSight path, calls the source driver's `enable()` operation in `CS_MODE_PERF`, and emits a `perf_report_aux_output_id()` record containing CoreSight AUX protocol version, trace ID, and sink ID once per CPU. Stop reverses that sequence: disable source, update the sink buffer when requested, end perf AUX output, and disable the CoreSight path. Pause disables the source and, for non-per-CPU sinks with `update_buffer`, rolls the AUX handle forward without fully destroying the path.

## State and Persistence

Session state lives in `struct etm_event_data`: CPU mask, per-CPU paths, AUX hardware-ID emission mask, sink buffer configuration, and active syscfg hash. Runtime per-CPU state lives in `struct etm_ctxt`, which preserves `event_data` independently of the perf AUX handle. Source registration state lives in `csdev_src` and is changed by ETM source drivers when devices are registered or removed.

## Dependencies and Integration Points

This file integrates the Linux perf PMU API, the CoreSight path framework, CoreSight sink/source operations, CoreSight trace-ID allocation, and CoreSight system configuration. ETM3x and ETM4x source drivers call `etm_perf_symlink()` to connect CPU sources to the PMU, and sink drivers call `etm_perf_add_symlink_sink()` to expose selectable sinks.

## Risks and Edge Cases

- Setup silently removes CPUs from the event mask when no source, sink, compatible sink, path, trace ID, or AUX pause support is available.
- Mixed default sinks are accepted only when sink subtype and sink ops match.
- `etm_event_pause()` avoids buffer updates for per-CPU sinks because IRQ/NMI update paths can race with pause-time updates.
- Error unwinding schedules asynchronous cleanup.
- Perf address filtering only supports all ranges or all start/stop filters, not a mix.

## Test Signals

Useful validation includes perf open/start/stop with single-CPU and all-CPU sessions; sink selection through PMU `sinks/*`; CoreSight syscfg selection through PMU `events/*`; AUX pause/resume; address range and start/stop filters; CPU masks with missing ETMs; concurrent perf sessions verifying trace-ID stability; and sink-buffer truncation paths where IRQ-side sink handling clears the AUX handle before stop.
