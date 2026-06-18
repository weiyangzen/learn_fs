# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-trbe.c

## Purpose

`coresight-trbe.c` implements Arm Trace Buffer Extension as a per-CPU CoreSight system-memory sink for ETE/ETM trace capture through perf AUX buffers. It configures TRBE system registers, handles per-CPU maintenance interrupts, applies CPU erratum workarounds, and registers one percpu sink per supported CPU.

## Important APIs, Types, and Functions

`struct trbe_buf` maps perf AUX pages into a contiguous virtual TRBE buffer and tracks base, hardware base, limit, write pointer, pages, snapshot mode, and CPU data. `struct trbe_cpudata` stores per-CPU alignment, flags, mode, current buffer, and errata bitmap. `struct trbe_drvdata` stores percpu data, percpu perf handles, hotplug node, IRQ, supported CPUs, and platform device. Core paths include `arm_trbe_alloc_buffer`, `arm_trbe_enable`, `arm_trbe_update_buffer`, `arm_trbe_disable`, `arm_trbe_irq_handler`, CPU probe/register helpers, IRQ setup, and hotplug setup.

## Control Flow

Probe rejects KPTI-style unmapped kernel-at-EL0 systems, allocates drvdata, obtains a percpu PPI IRQ and affinity mask, allocates per-CPU handles, probes each supported CPU via SMP calls, registers a CoreSight percpu sink, enables its IRQ, and registers CPU hotplug callbacks. Enable computes a writable AUX range from perf head/tail/wakeup, aligns/pads with ETE ignore packets, applies erratum-specific base/limit adjustments, stores the current handle, and programs TRBBASER/TRBPTR/TRBLIMITR. IRQ handling prohibits tracing, drains and disables TRBE, classifies status as wrap/spurious/fatal, updates perf AUX output and re-enables if possible, or truncates on fatal/no-space cases.

## State and Persistence Behavior

Per-CPU CoreSight devices and `trbe_cpudata` persist while the platform device is bound. Current perf handles are stored percpu during active sessions. TRBE hardware state is reset on CPU enable/disable and remove. Errata bits are cached per CPU after probing. Perf snapshot mode advances head directly; normal mode uses `perf_aux_output_skip/end/begin` to manage consumed space.

## Dependencies and Integration Points

The driver depends on arm64 TRBE/ETE system registers, CPU feature detection, KVM TRBE enable/disable hooks, CoreSight percpu sink APIs, perf AUX APIs, CPU hotplug, percpu IRQ affinity, vmalloc page mapping, and erratum cpucaps. It is matched by OF `arm,trace-buffer-extension` and ACPI platform ID `ARMV8_TRBE_PDEV_NAME`.

## Risks and Edge Cases

The buffer limit calculation is complex and must avoid overwriting unconsumed perf data. Errata can require PAGE alignment, skipped bytes, an extra guard page, additional barriers, or disabling broken CPUs. IRQ and update paths race with event stop, so local IRQ masking and handle clearing are critical. `arm_trbe_irq_handler` obtains the buffer before checking for a NULL handle, so the percpu handle must only be NULL when no IRQ is pending.

## Test Signals

Test minimum page rejection, normal versus snapshot AUX behavior, wakeup/tail alignment padding, wrap IRQ restart, spurious IRQ re-enable, fatal abort truncation, CPU hotplug register/unregister, per-CPU IRQ affinity, KPTI rejection, and each erratum path including overwrite-fill, out-of-range, drain-after-disable, context-sync-after-enable, and broken-CPU disable.
