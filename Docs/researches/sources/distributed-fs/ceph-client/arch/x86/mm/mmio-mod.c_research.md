# sources/distributed-fs/ceph-client/arch/x86/mm/mmio-mod.c

## Purpose
This file implements the higher-level mmiotrace module logic around KMMIO: tracking ioremap/iounmap events, decoding MMIO instructions, emitting trace records, and optionally reducing the system to one CPU to avoid missed events.

## Important APIs, Types, and Functions
- `mmiotrace_ioremap()` and `mmiotrace_iounmap()` are called from ioremap/iounmap paths.
- `enable_mmiotrace()` and `disable_mmiotrace()` control tracing lifetime.
- `mmiotrace_printk()` emits formatted trace messages while tracing is enabled.
- `pre()` and `post()` are KMMIO probe callbacks that decode instruction type, width, value, PC, and physical address.
- `struct trap_reason` stores per-CPU active instruction context; `struct remap_trace` couples a KMMIO probe to physical mapping metadata.

## Control Flow and State
When tracing is enabled, each ioremap call can allocate a `remap_trace`, emit an `MMIO_PROBE` mapping record, add it to `trace_list`, and register a KMMIO probe unless `nommiotrace` is set. Fault pre-handling decodes reads/writes/immediate writes and fills per-CPU trace state. Post-handling captures read results and emits `mmio_trace_rw()`. Iounmap unregisters the probe, emits `MMIO_UNPROBE`, waits for RCU, and frees the trace. Enable/disable is serialized by `mmiotrace_mutex`; trace list and enabled state are protected by `trace_lock`.

## Dependencies and Integration Points
The module depends on kmmio, ioremap hooks, instruction decoder helpers in `pf_in.h`, debugfs/trace mmiotrace core APIs, CPU hotplug, percpu storage, and page-table lookup for diagnostics. Module parameters `filter_offset`, `nommiotrace`, and `trace_pc` tune behavior.

## Risks
Tracing can miss events on other CPUs during KMMIO single-step windows; CPU hotplug downshifting mitigates this when available. Pre/post nesting must match exactly or the code BUGs. Recording PCs can taint clean-room reverse engineering, so it is optional. Failing to unregister probes on disable would leave non-present mappings armed.

## Test Signals
Enable/disable logs, mapping/unmapping records, read/write trace records, CPU offline/online logs, and cleanup purges for leaked mappings are primary signals. Tests include `nommiotrace`, `filter_offset`, `trace_pc`, hotplug enabled/disabled builds, and MMIO reads/writes through traced ioremaps.
