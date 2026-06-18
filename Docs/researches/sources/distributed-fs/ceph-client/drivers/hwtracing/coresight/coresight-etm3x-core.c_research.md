# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm3x-core.c

## Purpose

This file implements the ETM3x/PTM CoreSight source driver. It probes AMBA ETM/PTM devices, discovers architecture capabilities, registers each CPU-affine source with CoreSight and perf, programs ETMv3 hardware for sysfs or perf tracing, handles CPU hotplug, and manages runtime clocks.

## Important APIs, Types, and Functions

- `boot_enable` starts sysfs tracing at boot after registration.
- `etmdrvdata[NR_CPUS]` maps CPUs to ETM3x driver data for hotplug callbacks.
- Power and lock helpers include `etm_os_unlock()`, `etm_set_pwrdwn()`, `etm_clr_pwrdwn()`, `etm_set_pwrup()`, `etm_clr_pwrup()`, `etm_set_prog()`, and `etm_clr_prog()`.
- `etm_set_default()` initializes a trace-all software config.
- `etm_config_trace_mode()` programs address comparator pair 0 as a full-range exception-level filter for exclude-kernel or exclude-user mode.
- `etm_parse_event_config()` maps perf attributes into `struct etm_config`.
- `etm_enable_hw()` claims the CoreSight device, powers/unlocks/programs the trace unit, writes config registers, writes the trace ID, and clears programming mode.
- `etm_disable_hw()` sets programming mode, reads back sequencer/counter state, powers down, and disclaims the CoreSight device.
- `etm_probe()` allocates driver data, maps resources, initializes architecture data on the target CPU, registers the CoreSight source, creates the perf symlink, and optionally boot-enables tracing.

## Control Flow

Probe maps the register resource, determines optional CP14 access from firmware, enables `atclk`, resolves CPU affinity, and calls `etm_init_arch_data()` on the target CPU. Architecture init unlocks the OS lock, powers the unit, sets programming mode, reads ETMIDR/ETMCCR/ETMCCER, derives comparator/counter/context counts, clears self-claim tags, and powers down. The driver then registers a CoreSight source with sysfs groups and links it into the perf PMU.

For perf, `etm_enable_perf()` verifies CPU affinity, takes CoreSight perf mode, parses perf config, stores the path trace ID, and programs hardware. For sysfs, `etm_enable_sysfs()` stores the trace ID and uses `smp_call_function_single()` so register writes execute on the CPU owning the trace unit. Disable follows the same mode split.

## State and Persistence

Persistent driver state is `struct etm_drvdata`: discovered capabilities, CPU ID, `sticky_enable`, `boot_enable`, `os_unlock`, `traceid`, and `struct etm_config`. `etm_disable_hw()` reads back sequencer and counter values into `config`, so sysfs can report post-run state. Sysfs trace IDs are released on reset rather than normal disable.

## Dependencies and Integration Points

The driver integrates AMBA bus matching, CoreSight source registration, CoreSight claim/disclaim, CoreSight trace-ID allocation, PM runtime clock management, CPU hotplug, perf ETM support, and sysfs attributes from `coresight-etm3x-sysfs.c`.

## Risks and Test Signals

Register access must happen on the owning CPU, especially for CP14-backed devices and powered-down CPUs. Timeout failures in programming mode transitions are logged but do not always abort. `etm_enable_perf()` calls `etm_parse_event_config()` without checking its return value, which is a risk for invalid perf config propagation. Test AMBA probe, sysfs boot enable, perf enable, mode exclusion, CPU hotplug, CP14/MMIO variants, trace ID behavior, and counter/sequencer readback.
