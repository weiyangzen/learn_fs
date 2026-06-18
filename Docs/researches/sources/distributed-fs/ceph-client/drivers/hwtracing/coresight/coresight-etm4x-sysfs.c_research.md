# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm4x-sysfs.c

## Purpose

This file defines the ETMv4/ETE sysfs interface. It exposes discovered hardware capabilities, an extensive editable `struct etmv4_config` surface, context/VMID/address/counter/resource/single-shot/sequencer controls, trace metadata, and filtered management register groups that adapt to ETM4 vs ETE and MMIO vs sysreg access.

## Important APIs, Types, and Attributes

Read-only capability attributes include `nr_pe_cmp`, `nr_addr_cmp`, `nr_cntr`, `nr_ext_inp`, `numcidc`, `numvmidc`, `nrseqstate`, `nr_resource`, `nr_ss_cmp`, `cpu`, and `ts_source`. `reset` clears ETM4 config state and resets syscfg feature state. `mode` maps `ETMv4_MODE_ALL` flags to `TRCCONFIGR`, `TRCEVENTCTL1R`, `TRCSTALLCTLR`, and `TRCVICTLR` bits. Other attributes cover events, timestamps, cycle threshold, branch broadcast, exception-level ViewInst control, address comparators, sequencers, counters, resources, single-shot controls, context IDs, VMIDs, and management registers.

## Control Flow

Sysfs stores parse input, validate against capability fields discovered by the ETM4 core, and mutate `drvdata->config`, usually under `raw_spin_lock`. Index attributes select array elements for later show/store operations. Address range setup requires even indices and paired comparators. Context and VMID mask setters clear masked bytes in comparator values because the architecture requires zeroed masked bytes for predictable behavior.

Management register reads use `pm_runtime_get_sync()`, then `etmv4_cross_read()` issues `smp_call_function_single()` to read registers on the CPU that owns the trace unit. Attribute visibility is dynamic for sysreg common registers, ETM4-only registers, ETE-only registers, and MMIO-only registers.

## State and Persistence

All editable sysfs state is the software register image in `struct etmv4_config`; hardware is updated on the next sysfs enable. Reset clears arrays according to discovered hardware counts and returns ViewInst to trace-all/start state where address comparators exist. Trace ID is allocated on read of `trctraceid` if necessary so decode metadata remains consistent before enable.

## Dependencies and Integration Points

This file depends on ETM4 register/config definitions, CoreSight syscfg reset APIs, CoreSight private sysfs helpers, PID namespace helpers, PM runtime, and the ETM4 core's trace-mode behavior. The attribute groups are installed by `etm4_add_coresight_dev()`.

## Risks and Test Signals

The sysfs surface allows low-level register-image construction, so many combinations are valid only if users understand ETM4 programming. Some setters silently ignore unsupported string values after parsing. Cross-CPU management reads assume the target CPU can service the SMP call. Tests should cover reset defaults, mode bit mapping, address include/exclude and start/stop validation, context/VMID mask byte clearing, namespace rejection, index bounds, management register visibility, trace ID allocation on read, PM runtime wrapping, and concurrent sysfs writes.
