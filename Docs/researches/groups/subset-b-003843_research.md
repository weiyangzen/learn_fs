# Research: subset-b-003843 CoreSight ETM perf, ETM3x, and ETM4x sources

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm-perf.c -->
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

Cleanup is deferred through `etm_free_aux()` and `free_event_data()` because perf may call `free_aux()` in contexts unsuitable for full CoreSight path and sink-buffer cleanup. The worker frees the sink buffer, deactivates any syscfg config, stops the perf trace-ID allocation for each sink, releases every path, frees the percpu path array, and frees the session object.

## State and Persistence

Session state lives in `struct etm_event_data`: CPU mask, per-CPU paths, AUX hardware-ID emission mask, sink buffer configuration, and active syscfg hash. Runtime per-CPU state lives in `struct etm_ctxt`, which preserves `event_data` independently of the perf AUX handle. Source registration state lives in `csdev_src` and is changed by ETM source drivers when devices are registered or removed. Sink/config sysfs entries store hashed names in `dev_ext_attribute::var`; those hashes are the values user space passes through perf config fields.

Perf trace IDs are intentionally not released per CPU during path release for perf sessions. Instead `coresight_trace_id_perf_start()` and `coresight_trace_id_perf_stop()` maintain sink-wide lifetime so a CPU trace ID cannot change while concurrent perf sessions depend on stable decode metadata.

## Dependencies and Integration Points

This file integrates the Linux perf PMU API, the CoreSight path framework, CoreSight sink/source operations, CoreSight trace-ID allocation, and CoreSight system configuration. ETM3x and ETM4x source drivers call `etm_perf_symlink()` to connect CPU sources to the PMU, and sink drivers call `etm_perf_add_symlink_sink()` to expose selectable sinks. The source driver's `enable`, `disable`, `pause_perf`, `resume_perf`, and `cpu_id` callbacks are consumed here but implemented in the ETM generation-specific files.

## Risks and Edge Cases

- Setup silently removes CPUs from the event mask when no source, sink, compatible sink, path, trace ID, or AUX pause support is available. Later scheduling on those CPUs yields a zero-sized record rather than trace.
- Mixed default sinks are accepted only when sink subtype and sink ops match. This protects single buffer configuration reuse but means heterogeneous sink topologies reduce CPU coverage.
- `etm_event_pause()` avoids buffer updates for per-CPU sinks because per-CPU sink IRQ/NMI update paths can race with pause-time updates.
- Error unwinding in `etm_setup_aux()` calls `etm_free_aux()`, which schedules asynchronous cleanup. Tests need to account for delayed path release.
- Perf address filtering only supports all ranges or all start/stop filters, not a mix.
- Hash-based sink/config selection depends on stable device/config names and `hashlen_hash()` collisions being practically absent.

## Test Signals

Useful validation includes perf open/start/stop with single-CPU and all-CPU sessions; sink selection through PMU `sinks/*`; CoreSight syscfg selection through PMU `events/*`; AUX pause/resume on ETM4x sources; address range and start/stop filters, including rejection of mixed filters; CPU masks with missing ETMs; concurrent perf sessions verifying trace-ID stability; and sink-buffer truncation paths where IRQ-side sink handling clears the AUX handle before `etm_event_stop()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm-perf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm-perf.h -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm-perf.h

## Purpose

This header defines the shared perf-facing CoreSight ETM contract used by ETM3x, ETM4x, sink drivers, and the CoreSight syscfg layer. It assigns perf event config bitfields, declares filter/session data structures, and exposes helpers for PMU sysfs links and sink configuration lookup.

## Important APIs, Types, and Constants

- `ETM_ADDR_CMP_MAX` sets the perf filter limit to 8, matching the maximum address comparator count used by both ETMv3 and ETMv4 perf filtering.
- `ATTR_CFG_FLD_*` macros define perf `config`, `config2`, and `config3` bit layouts for preset, timestamp, branch broadcast, cycle accuracy, context ID tracing, deprecated timestamp, return stack, sink ID, config ID, and cycle count threshold.
- `struct etm_filter` stores one range, start, or stop filter with start/stop addresses and `enum etm_addr_type`.
- `struct etm_filters` stores up to `ETM_ADDR_CMP_MAX` filters plus `nr_filters` and `ssstatus`, the saved ETM4 start/stop state used when perf reschedules a task.
- `struct etm_event_data` stores per-event CoreSight state: deferred cleanup work, CPU mask, AUX hardware-ID emission mask, sink buffer config, active syscfg hash, and a percpu path array.
- `etm_perf_sink_config()` extracts `struct etm_event_data` from a perf AUX handle and returns the sink-private buffer configuration.
- Exported declarations cover PMU initialization/exit, source/sink/syscfg sysfs link management, and configfs event registration.

## Control Flow and Integration

Perf event format definitions in this header are consumed by `coresight-etm-perf.c` to generate sysfs PMU format files and by ETM3x/ETM4x event parsers through `ATTR_CFG_GET_FLD()`. The filter structures are allocated and populated by the perf layer, then generation-specific source drivers consume them to program ETM address comparators. Sink drivers use `etm_perf_sink_config()` during AUX buffer handling to recover their private allocation from the active perf handle.

## State and Persistence

The header defines in-memory session state only; there is no persistent storage. `struct etm_event_data` lifetime is controlled by perf AUX setup/free and deferred work. `ssstatus` persists across task schedule-out within a perf event so ETM4 start/stop tracing can resume correctly.

## Dependencies

It depends on Linux percpu definitions, `struct perf_output_handle` from perf headers, CoreSight private definitions for `enum etm_addr_type`, and forward declarations for CoreSight devices and syscfg descriptors.

## Risks and Test Signals

The perf bit layout is an ABI surface exposed through PMU sysfs format files, so changes must preserve compatibility, including the deprecated timestamp bit. Filter count and address type assumptions must match ETM3x and ETM4x programming code. Test signals include PMU format file contents, sink/config selection through `config2`, timestamp via both current and deprecated positions, and start/stop filter rescheduling behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm-perf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm.h -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm.h

## Purpose

This header is the ETM3x/PTM private interface. It defines ETMv3/PTM register offsets, bit definitions, mode flags, event encodings, configuration state, driver state, register access helpers, and exported functions used by the ETM3x core and sysfs files.

## Important APIs, Types, and Constants

- Register macros cover ETM trace, management, comparator, counter, sequencer, context ID, sync, timestamp, trace ID, power, and OS lock registers.
- Bit macros such as `ETMCR_ETM_PRG`, `ETMCR_ETM_EN`, `ETMCR_CYC_ACC`, `ETMCR_TIMESTAMP_EN`, `ETMTECR1_INC_EXC`, `ETMTECR1_START_STOP`, and `ETMCCER_RETSTACK` are used to compose hardware programming.
- Mode flags `ETM_MODE_*` describe sysfs/perf requested behavior such as exclude, cycle accuracy, stall, timestamp, context ID, branch broadcast, return stack, exclude kernel, and exclude user.
- `struct etm_config` is the ETM3x in-memory register image for trace control, address comparators, counters, sequencer transitions, context ID comparators, sync frequency, and timestamp event.
- `struct etm_drvdata` stores per-device hardware and runtime state: register access, clock, CoreSight device, spinlock, CPU affinity, port size, architecture, CP14 access mode, boot/sticky enable flags, discovered resource counts, capability registers, trace ID, and current config.
- `etm_writel()` and `etm_readl()` abstract register access through CP14 or memory-mapped IO and log invalid CP14 accesses.
- Exported functions include `etm_set_default()`, `etm_config_trace_mode()`, `get_etm_config()`, and `etm_release_trace_id()`, plus `coresight_etm_groups[]` for sysfs registration.

## Control Flow and Integration

The ETM3x core fills `struct etm_drvdata` during AMBA probe and capability discovery, initializes `struct etm_config`, and writes config fields to hardware during enable. The ETM3x sysfs file presents controlled accessors for the fields in `struct etm_config`; it uses the same register constants and masks. Perf parsing also writes into the same config before `etm_enable_hw()` programs registers.

The CP14-vs-MMIO helper boundary is important: callers do not need to know how a specific ETM is accessed. The driver sets `use_cp14` from firmware and `etm_readl()`/`etm_writel()` route all trace-register accesses accordingly.

## State and Persistence

`struct etm_config` is the persistent software copy of user or perf configuration between runs. Disable paths read back sequencer and counter state into this structure. `traceid` is stored in `struct etm_drvdata` and released only in specific sysfs reset or teardown paths, preserving sysfs-readable trace ID after a session.

## Dependencies

The header depends on CoreSight private APIs for access wrappers and address type definitions, Linux spinlocks, clocks, and ARM local/CP14 helpers. It is tightly coupled to `coresight-etm3x-core.c` and `coresight-etm3x-sysfs.c`.

## Risks and Test Signals

Register offsets and bit encodings are hardware ABI and must remain exact. CP14 error paths log but still return a local value; tests on CP14-backed systems should cover invalid offsets. Config array bounds must stay aligned with capability counts read from ETMCCR. Test signals include sysfs register values, perf and sysfs enable programming, CP14 and MMIO variants, counter/sequencer readback, and trace mode exclusion programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm3x-core.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm3x-core.c

## Purpose

This file implements the ETM3x/PTM CoreSight source driver. It probes AMBA ETM/PTM devices, discovers architecture capabilities, registers each CPU-affine source with CoreSight and perf, programs ETMv3 hardware for sysfs or perf tracing, handles CPU hotplug, and manages runtime clocks.

## Important APIs, Types, and Functions

- `boot_enable` is a module parameter that starts sysfs tracing at boot after registration.
- `etmdrvdata[NR_CPUS]` maps CPUs to ETM3x driver data for hotplug callbacks.
- Power and lock helpers include `etm_os_unlock()`, `etm_set_pwrdwn()`, `etm_clr_pwrdwn()`, `etm_set_pwrup()`, `etm_clr_pwrup()`, `etm_set_prog()`, and `etm_clr_prog()`.
- `coresight_timeout_etm()` polls ETM status through the CP14-aware accessors.
- `etm_set_default()` initializes a trace-all software config with always-true events, default sequencer/counter values, and sync frequency.
- `etm_config_trace_mode()` programs address comparator pair 0 as a full-range exception-level filter for exclude-kernel or exclude-user mode.
- `etm_parse_event_config()` maps perf attributes into `struct etm_config`, including cycle accuracy, timestamp, deprecated timestamp, return stack, and exclude flags.
- `etm_enable_hw()` claims the CoreSight device, powers/unlocks/programs the trace unit, writes all relevant config registers, writes the trace ID, and clears programming mode.
- `etm_disable_hw()` sets programming mode, reads back sequencer/counter state, powers down, and disclaims the CoreSight device.
- `etm_enable_perf()` and `etm_enable_sysfs()` adapt perf and sysfs flows to `etm_enable_hw()`.
- `etm_disable_perf()` and `etm_disable_sysfs()` reverse those flows.
- CPU hotplug callbacks `etm_online_cpu()`, `etm_starting_cpu()`, and `etm_dying_cpu()` replay enable state or disable hardware during CPU lifecycle transitions.
- `etm_probe()` allocates driver data, maps resources, initializes architecture data on the target CPU, registers the CoreSight source, creates the perf symlink, and optionally boot-enables tracing.

## Control Flow

Probe starts from an AMBA device, maps the register resource, determines optional CP14 access from firmware, enables `atclk`, resolves CPU affinity, and calls `etm_init_arch_data()` on the target CPU. Architecture init unlocks the OS lock, powers the unit, sets programming mode, reads ETMIDR/ETMCCR/ETMCCER, derives comparator/counter/context counts, clears self-claim tags, and powers the unit back down. After support validation, the driver registers a CoreSight source with `etm_cs_ops` and sysfs groups from `coresight-etm3x-sysfs.c`, then links it into the perf PMU.

For perf, `coresight-etm-perf.c` calls source `enable()` on the current CPU. `etm_enable_perf()` verifies CPU affinity, takes CoreSight perf mode, parses perf config into the software register image, stores the path trace ID, and programs hardware. For sysfs, `etm_enable_sysfs()` stores the trace ID and uses `smp_call_function_single()` so register writes execute on the CPU owning the trace unit. Disable follows the same mode split.

CPU hotplug preserves logical CoreSight mode. On CPU starting, if the driver was unlocked or enabled, it unlocks and reprograms hardware. On CPU dying, it disables hardware if still logically enabled. Online callback supports boot-enable retry for not-yet-sticky devices.

## State and Persistence

Persistent driver state is `struct etm_drvdata`: discovered capabilities, CPU ID, `sticky_enable`, `boot_enable`, `os_unlock`, `traceid`, and `struct etm_config`. `etm_disable_hw()` reads back sequencer and counter values into `config`, so sysfs can report post-run state. Sysfs trace IDs are intentionally released on reset rather than normal disable, allowing users to read trace ID metadata after a session. Perf trace IDs are released by perf AUX cleanup at session end.

## Dependencies and Integration Points

The driver integrates AMBA bus matching, CoreSight source registration, CoreSight claim/disclaim, CoreSight trace-ID allocation, PM runtime clock management, CPU hotplug, perf ETM support through `coresight-etm-perf.c`, and sysfs attributes from `coresight-etm3x-sysfs.c`. It consumes register and config definitions from `coresight-etm.h`.

## Risks and Edge Cases

- Register access must happen on the owning CPU, especially for CP14-backed devices and powered-down CPUs.
- Timeout failures in programming mode transitions are logged but do not always abort the enable sequence.
- `etm_parse_event_config()` returns `-EINVAL` for invalid timestamp levels but callers should check parse errors; this file currently calls it in `etm_enable_perf()` without using the return value, which is a risk for invalid perf config propagation.
- CPU hotplug races are controlled by hotplug locks and per-device spinlocks; tests should stress remove vs CPU offline.
- `etm_enable_sysfs()` returns `-ENODEV` if the CPU is offline rather than deferring.
- Unsupported return stack requests are silently ignored when hardware lacks the feature.

## Test Signals

Key validation includes AMBA probe for supported ETM/PTM IDs, sysfs boot enable, perf enable on the correct CPU, rejection of simultaneous sysfs/perf modes, CPU hotplug re-enable/disable while tracing, CP14 and MMIO access variants, trace ID allocation/release behavior, config readback after disable, and perf options for cycle accuracy, timestamp, return stack, and kernel/user exclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm3x-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm3x-sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm3x-sysfs.c

## Purpose

This file defines the ETM3x/PTM sysfs interface. It exposes discovered hardware capabilities, editable trace configuration fields, selected live hardware status, trace ID metadata, and a small management register group for CoreSight ETM3x devices.

## Important APIs, Types, and Attributes

- Read-only capability attributes: `nr_addr_cmp`, `nr_cntr`, `nr_ctxid_cmp`, `cpu`, and `traceid`.
- Live/status attributes: `etmsr`, `cntr_val`, and `seq_curr_state` can read hardware when tracing is active.
- `reset` clears `struct etm_config`, restores defaults through `etm_set_default()`, marks address comparators unused, and releases the sysfs trace ID.
- `mode` maps user mode flags to ETMCR and trace mode config, including exclude, cycle accuracy, stall, timestamp, context ID, branch broadcast, return stack, and kernel/user exclusion.
- Address comparator attributes: `addr_idx`, `addr_single`, `addr_range`, `addr_start`, `addr_stop`, and `addr_acctype`.
- Counter attributes: `cntr_idx`, `cntr_rld_val`, `cntr_event`, `cntr_rld_event`, and `cntr_val`.
- Sequencer attributes: `seq_12_event`, `seq_21_event`, `seq_23_event`, `seq_31_event`, `seq_32_event`, `seq_13_event`, and `seq_curr_state`.
- Context ID attributes: `ctxid_idx`, `ctxid_pid`, and `ctxid_mask`.
- Timing/event attributes: `sync_freq` and `timestamp_event`.
- Attribute groups exported as `coresight_etm_groups[]`, including a `mgmt` group built with `coresight_simple_reg32()`.

## Control Flow

Most store handlers parse hexadecimal input, validate it against discovered capability counts or masks, and update the in-memory `struct etm_config`. Index attributes are protected by `drvdata->spinlock` because subsequent accesses dereference the selected index across multiple array fields. Address range setup requires an even comparator index and uses adjacent comparator slots; start and stop comparators set the ETM start/stop control bits; mode changes may call `etm_config_trace_mode()` to install kernel/user exclusion ranges.

For live register reads, `etmsr_show()` and `seq_curr_state_show()` acquire PM runtime, take the spinlock, unlock CoreSight registers, read hardware, relock, and release PM runtime. `cntr_val_show()` returns cached counter values when disabled and direct hardware counter values when enabled.

## State and Persistence

Sysfs writes persist only in `drvdata->config` until the next sysfs enable programs hardware. Some state is refreshed on disable by `coresight-etm3x-core.c`, notably counter and sequencer state. Context ID settings are rejected outside the initial PID namespace to avoid confusing namespaced PIDs and leaking kernel-global identifiers. Trace ID persists across sysfs disable and is released by `reset`.

## Dependencies and Integration Points

The file depends on `coresight-etm.h` for register/config definitions, `coresight-priv.h` for simple management register attributes, PM runtime, PID namespace helpers, and the ETM3x core's exported default/trace-ID functions. The exported attribute groups are consumed during CoreSight source registration in `coresight-etm3x-core.c`.

## Risks and Edge Cases

- Many attributes directly edit low-level register images, so invalid combinations can still be created if they pass local bounds checks.
- Address comparator type state prevents reusing a comparator for incompatible modes without reset.
- `addr_range` must use even indices and adjacent slots; off-by-one capability bugs would program the wrong comparator pair.
- Context ID sysfs is deliberately unavailable from non-init PID namespaces.
- Several setters do not take the spinlock when writing scalar fields, relying on mode separation and low contention; concurrent sysfs writes can still create confusing intermediate configs.

## Test Signals

Test sysfs reads for capability values after probe; reset restoring defaults and releasing trace ID; mode rejection for unsupported stall/timestamp; address single/range/start/stop validation; context ID access from initial vs nested PID namespaces; live vs cached counter/sequencer reads; and management register visibility/reads while the device is runtime suspended or active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm3x-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm4x-cfg.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm4x-cfg.c

## Purpose

This file connects ETMv4 devices to the generic CoreSight system configuration framework. It validates configuration feature register offsets and maps each allowed hardware register offset to the corresponding field inside `struct etmv4_config`, allowing generic syscfg feature loading to program ETMv4 trace behavior through driver-owned state rather than direct register writes.

## Important APIs, Types, and Functions

- `CHECKREG()` and `CHECKREGIDX()` are local mapping helpers that assign `cscfg_regval_csdev::driver_regval` to a scalar or indexed field in `struct etmv4_config`.
- `etm4_cfg_map_reg_offset()` is the core whitelist and mapper. It accepts only trace-capture configuration registers and maps offsets such as `TRCEVENTCTL0R`, `TRCSTALLCTLR`, `TRCTSCTLR`, `TRCVICTLR`, sequencer registers, single-shot registers, context/VMID comparators, resource selectors, address comparators, and counters.
- `etm4_cfg_load_feature()` sets the feature's `drv_spinlock` to the ETM driver lock and maps every register descriptor in the feature to a driver config field.
- `etm4_cscfg_register()` registers the ETM4 CoreSight device with class match flags for all source devices and ETM4-specific source devices.

## Control Flow

During ETM4 device registration, `coresight-etm4x-core.c` calls `etm4_cscfg_register()`. The CoreSight syscfg framework later calls `etm4_cfg_load_feature()` for matching features. For each feature register descriptor, the loader extracts the offset and asks `etm4_cfg_map_reg_offset()` to resolve it. If any offset is outside the allowed ranges, the function returns `-EINVAL` and feature loading fails. Valid descriptors receive direct pointers to ETM driver config storage, so generic syscfg code can copy parameterized values under the driver's spinlock.

## State and Persistence

This file does not allocate persistent state itself. It mutates `struct cscfg_feature_csdev` records by setting their lock pointer and per-register `driver_regval` pointers. The pointed-to values live in `drvdata->config` and are later programmed by normal ETM4 enable paths.

## Dependencies and Integration Points

It depends on ETM4 register macros and config structure definitions from `coresight-etm4x.h`, resource ID constants from `coresight-etm4x-cfg.h`, CoreSight syscfg APIs from `coresight-syscfg.h`, and generic config descriptors from `coresight-config.h`. It is called by ETM4 probe and consumed indirectly by perf/sysfs active config selection.

## Risks and Edge Cases

- Offset matching uses masks and index arithmetic; mistakes can map a valid-looking offset to the wrong array element.
- Resource selector registers 0 and 1 are intentionally skipped because they are fixed/reserved; features trying to control them fail.
- The whitelist excludes registers the ETM driver must own exclusively, reducing risk from syscfg but requiring feature definitions to stay aligned with this mapping.
- Feature load failure happens at descriptor load time rather than trace enable time, so bad config packs should be caught early.

## Test Signals

Tests should register syscfg features covering scalar registers, indexed counters, address comparators, context/VMID comparators, and invalid offsets. They should verify that mapped features update `drvdata->config` under the ETM spinlock and that invalid/reserved offsets fail feature load without touching driver state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm4x-cfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm4x-cfg.h -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm4x-cfg.h

## Purpose

This header declares ETMv4-specific CoreSight system configuration resource IDs and the registration entry point used by the ETM4x core driver.

## Important APIs and Constants

- Resource IDs classify ETM4 syscfg-controlled resources: counters, comparators, comparator pairs, resource selectors, selector pairs, sequencer, and timestamp.
- `ETM4_CFG_RES_MASK` masks the low nibble of resource IDs.
- `etm4_cscfg_register(struct coresight_device *csdev)` registers an ETM4 CoreSight source with the syscfg framework and loads matching features.

## Control Flow and Integration

`coresight-etm4x-core.c` calls `etm4_cscfg_register()` after CoreSight source registration and perf symlink creation. The implementation in `coresight-etm4x-cfg.c` uses this header's declaration and ETM4 resource identifiers to connect generic syscfg feature descriptors to ETM4 driver config storage.

## State and Persistence

The header defines constants only. Runtime state is maintained by `coresight-etm4x-cfg.c`, generic syscfg objects, and `struct etmv4_config`.

## Dependencies, Risks, and Test Signals

It depends on `coresight-config.h` and `coresight-etm4x.h`. The main risk is changing resource ID values in a way that breaks existing syscfg feature descriptors. Test signals include successful ETM4 syscfg registration and feature descriptors that refer to each resource class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm4x-cfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm4x-core.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm4x-core.c

## Purpose

This file implements the ETMv4/ETE CoreSight source driver. It supports AMBA memory-mapped ETMv4 devices and platform-described sysreg/ETE devices, discovers hardware capabilities, registers CPU-affine CoreSight sources, programs trace units for sysfs and perf sessions, handles perf filters and AUX pause/resume, integrates CoreSight syscfg, manages CPU hotplug and CPU power-management save/restore, and provides trace filtering for kernel/user/host/guest exception levels.

## Important APIs, Types, and Functions

- Module parameters: `boot_enable` and `pm_save_enable`, with firmware/self-hosted/never save modes.
- `etmdrvdata[NR_CPUS]` maps CPUs to ETM4 driver data; `delayed_probe` stores platform/sysreg probes that must wait for an offline CPU to come online.
- Sysreg accessors `etm4x_sysreg_read/write()` and `ete_sysreg_read/write()` back `struct csdev_access` for system-instruction-accessible ETM4/ETE devices.
- OS/software lock helpers manage ETM OS lock variants and CoreSight software lock.
- FEAT_TRF helpers `etm4x_prohibit_trace()` and `etm4x_allow_trace()` program `TRFCR_EL1` and KVM guest trace filtering.
- `etm4_enable_hw()` writes the complete `struct etmv4_config` image to hardware, claims the CoreSight device, handles ETE `TRCRSR`, power-up, and optionally enables the trace unit.
- `etm4_disable_hw()` disables tracing, reads single-shot and counter state back, powers down if allowed, and disclaims the CoreSight device.
- `etm4_parse_event_config()` maps perf attributes into ETMv4 config: exclude flags, address filters, cycle counting threshold, timestamp events, context ID/VMID tracing, return stack, syscfg config/preset, and branch broadcast.
- `etm4_config_timestamp_event()` builds a counter/resource-selector/timestamp-generator chain for periodic timestamp packets.
- `etm4_set_event_filters()` translates perf address filters into ViewInst include/exclude ranges or start/stop comparators.
- `etm4_resume_perf()` and `etm4_pause_perf()` implement AUX pause support.
- `etm4_init_arch_data()` detects access method, OS lock model, ETM/ETE architecture, capability registers, resource counts, timestamp/context sizes, errata fixups, and trace filtering support.
- `__etm4_cpu_save()` and `__etm4_cpu_restore()` snapshot and restore trace registers for CPU power-down when self-hosted context save is required.
- `etm4_probe_amba()`, `etm4_probe_platform_dev()`, and `etm4_probe_cpu()` support AMBA, platform, and delayed CPU-online probing.
- `etm4_add_coresight_dev()` registers the CoreSight source, perf symlink, and syscfg device.

## Control Flow

Initialization registers CPU PM/hotplug callbacks, then AMBA and platform drivers. Probe allocates driver data, maps MMIO if present, enables clocks/runtime PM, determines CPU affinity, and runs `etm4_init_arch_data()` on the target CPU. If the CPU is offline, probe stores a delayed init object and returns; the online hotplug callback completes discovery and registration later. Successful discovery selects MMIO when available, otherwise sysreg/ETE access if CPU debug feature registers support it.

Enable flow differs by caller but converges at `etm4_enable_hw()`. Perf enable verifies CPU affinity, takes CoreSight perf mode, parses perf config, stores the path trace ID, records initial AUX pause state, and programs hardware. Sysfs enable optionally enables an active configfs/syscfg preset, stores the trace ID, marks the session unpaused, and runs enable on the owning CPU. Hardware enable disables the trace unit, waits for idle, writes every supported config register family based on discovered counts, sets trace ID and power-up, and enables the trace unit unless the perf session starts paused.

Disable flow reads mode, dispatches to sysfs or perf teardown, disables the trace unit with architectural barriers and trace prohibition, saves counter/single-shot status, releases configfs active config where needed, and returns CoreSight mode to disabled. Perf disable also stores start/stop status in `event->hw.addr_filters` so rescheduled perf tasks resume acquisition correctly.

CPU hotplug starting re-unlocks and reprograms enabled hardware; dying disables enabled hardware. CPU PM save/restore locks OS lock, waits for PM stable/idle, snapshots trace registers into `struct etmv4_save_state`, optionally powers down, restores on exit, unlocks OS lock, and re-enables trace unless paused.

## State and Persistence

`struct etmv4_drvdata` stores discovered capability fields, access type, OS lock model, trace filtering value, clocks, CPU, CoreSight device, trace ID, paused flag, save-state pointer, boot/sticky enable flags, and the mutable `struct etmv4_config`. Sysfs and perf both write the config image; hardware enable consumes it. Disable updates cached single-shot status and counter values. Perf AUX cleanup owns final trace-ID release, while sysfs reset releases sysfs trace IDs. Delayed probe state persists per CPU until the CPU comes online or the device is removed.

## Dependencies and Integration Points

The driver integrates CoreSight source APIs, CoreSight trace-ID allocation, the perf ETM PMU layer, CoreSight syscfg (`etm4_cscfg_register()`), AMBA and platform buses, OF/ACPI matching, runtime PM, CPU hotplug, CPU PM notifiers, KVM tracing filter configuration, architecture sysreg accessors, and ETM4 sysfs groups from `coresight-etm4x-sysfs.c`.

## Risks and Edge Cases

- System-register trace access requires strict ISB/DSB ordering; missing barriers can produce stale programming or trace leakage.
- MMIO is preferred over sysreg to avoid broken sysreg systems, so device descriptions with both paths depend on correct MMIO resources.
- Perf timestamp event generation consumes a free counter and resource selector; sessions fail with `-ENOSPC` if none are available.
- Branch broadcast perf requests fail if unsupported because silent decode errors are possible.
- CPU PM save/restore is large and register-count dependent; any missed capability condition can access unimplemented registers.
- `__etm4_cpu_save()` and restore appear to write/read `trcvmidcctlr0` for the second VMID mask path where `trcvmidcctlr1` would be expected, which is a review-worthy risk.
- Delayed probe and remove interact through per-CPU state and hotplug locking; races here can leak unregistered delayed probes or double cleanup.
- Context/VMID tracing is constrained by PID namespace and EL2 state to prevent confusing or unsafe metadata.

## Test Signals

Validation should cover AMBA ETM4 and platform sysreg/ETE probe, delayed probe on offline CPUs, sysfs and perf enable/disable, AUX pause/resume, range and start/stop perf filters across reschedule, configfs preset activation/deactivation, timestamp levels with and without free counters/resources, branch broadcast rejection when unsupported, CPU hotplug while tracing, CPU PM save/restore with active and paused sessions, FEAT_TRF kernel/user/host/guest exclusion, trace ID stability, and register visibility for ETM4 vs ETE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm4x-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm4x-sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm4x-sysfs.c

## Purpose

This file defines the ETMv4/ETE sysfs interface. It exposes discovered hardware capabilities, an extensive editable `struct etmv4_config` surface, context/VMID/address/counter/resource/single-shot/sequencer controls, trace metadata, and filtered management register groups that adapt to ETM4 vs ETE and MMIO vs sysreg access.

## Important APIs, Types, and Attributes

- Read-only capability attributes include `nr_pe_cmp`, `nr_addr_cmp`, `nr_cntr`, `nr_ext_inp`, `numcidc`, `numvmidc`, `nrseqstate`, `nr_resource`, `nr_ss_cmp`, `cpu`, and `ts_source`.
- `reset` clears ETM4 config state, restores trace-all ViewInst defaults, clears indexed resource arrays, releases the sysfs trace ID, and resets syscfg feature state.
- `mode` maps `ETMv4_MODE_ALL` flags to `TRCCONFIGR`, `TRCEVENTCTL1R`, `TRCSTALLCTLR`, and `TRCVICTLR` bits, with feature checks for load/store P0 tracing, branch broadcast, cycle counting, context ID, VMID, conditional tracing, timestamp, return stack, Q elements, ATB trigger, low-power override, stall, no-overflow, start/stop, reset trace, and error trace.
- Event/timing attributes include `pe`, `event`, `event_instren`, `event_ts`, `syncfreq`, `cyc_threshold`, `bb_ctrl`, `event_vinst`, `s_exlevel_vinst`, and `ns_exlevel_vinst`.
- Address comparator attributes include `addr_idx`, `addr_instdatatype`, `addr_single`, `addr_range`, `addr_start`, `addr_stop`, `addr_ctxtype`, `addr_context`, `addr_exlevel_s_ns`, and `addr_cmp_view`.
- Sequencer, counter, resource, and single-shot controls are exposed through `seq_*`, `cntr_*`, `res_*`, and `sshot_*` attributes.
- Context/VMID attributes include `ctxid_idx`, `ctxid_pid`, `ctxid_masks`, `vmid_idx`, `vmid_val`, and `vmid_masks`.
- Management register helpers `coresight_etm4x_reg_show()`, `etm4x_register_implemented()`, and `coresight_etm4x_attr_reg_implemented()` expose only registers valid for the current hardware/access type.
- Exported `coresight_etmv4_groups[]` includes the main group, `mgmt`, and `trcidr`.

## Control Flow

Sysfs stores parse input, validate against capability fields discovered by `coresight-etm4x-core.c`, and mutate `drvdata->config`, usually under `raw_spin_lock`. Index attributes select array elements for later show/store operations. Address range setup requires even indices and paired comparators; include/exclude state is applied by `etm4_set_mode_exclude()`. Context and VMID mask setters also clear masked bytes in comparator values because the architecture requires zeroed masked bytes for predictable behavior.

Management register reads use `pm_runtime_get_sync()`, then `etmv4_cross_read()` issues `smp_call_function_single()` to read registers on the CPU that owns the trace unit. Attribute visibility is dynamic: sysreg common registers, ETM4-only registers, ETE-only registers, and MMIO-only registers are filtered before sysfs exposes them.

## State and Persistence

All editable sysfs state is the software register image in `struct etmv4_config`; hardware is updated on the next sysfs enable. Reset clears arrays according to discovered hardware counts and returns ViewInst to trace-all/start state where address comparators exist. Counter and single-shot status can be refreshed by core disable paths. Trace ID is allocated on read of `trctraceid` if necessary so decode metadata remains consistent before enable.

## Dependencies and Integration Points

This file depends on ETM4 register/config definitions from `coresight-etm4x.h`, CoreSight syscfg reset APIs, CoreSight private sysfs helpers, PID namespace helpers, PM runtime, and the ETM4 core's `etm4_config_trace_mode()` behavior. The attribute groups are installed by `etm4_add_coresight_dev()`.

## Risks and Edge Cases

- The sysfs surface allows low-level register-image construction; many combinations are architecturally valid only if users understand ETM4 programming.
- Some setters silently ignore unsupported string values after parsing, such as `addr_instdatatype_store()` only acting on `"instr"`.
- Capability checks must match ETM4/ETE discovered counts exactly to avoid out-of-bounds array access or unimplemented register programming.
- Context ID and VMID controls reject non-init PID namespaces to avoid leaking or confusing global identifiers.
- Cross-CPU management reads assume the target CPU can service the SMP call; offline or hotplug transitions are sensitive.
- Dynamic management visibility is essential for sysreg/ETE devices because some management registers are not accessible through system instructions.

## Test Signals

Tests should cover reset defaults, mode bit mapping for each supported/unsupported feature, address include/exclude and start/stop validation, context/VMID mask byte clearing, namespace rejection for context/VMID attributes, counter/resource/single-shot index bounds, management register visibility on ETM4 MMIO vs ETM4 sysreg vs ETE, trace ID allocation on `trctraceid` read, PM runtime wrapping of register reads, and concurrent sysfs writes guarded by `raw_spin_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm4x-sysfs.c -->
