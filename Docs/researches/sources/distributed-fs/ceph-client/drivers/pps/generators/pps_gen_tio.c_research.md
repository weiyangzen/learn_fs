# sources/distributed-fs/ceph-client/drivers/pps/generators/pps_gen_tio.c

Purpose: Intel PMC Time-Aware IO PPS generator. It programs a hardware compare register against ART-derived time and uses an hrtimer to keep future pulses scheduled.

Important APIs/types/functions: `struct pps_tio`, `pps_gen_tio_probe()`, `pps_gen_tio_remove()`, `pps_tio_gen_enable()`, `hrtimer_callback()`, `pps_generate_next_pulse()`, `pps_tio_direction_output()`, `pps_tio_disable()`, and `pps_tio_enable()`.

Control flow: platform probe checks TSC known frequency and ART CPU features, allocates state, initializes generator callbacks, registers with PPS generator core, maps MMIO resource, disables hardware, initializes an absolute realtime hrtimer and spinlock, and stores drvdata. Enable verifies the clocksource has ART base, configures output/toggle mode, enables hardware, and starts the hrtimer for the first event just before the next second boundary. The hrtimer checks event counter progress, ensures it is not too late, converts the next realtime expiry to ART cycles, writes compare value minus hardware delay, and forwards by half a second. Missed events disable hardware and report `PPS_GEN_EVENT_MISSEDPULSE`.

State/dependencies: per-device MMIO base, hrtimer, previous event count, spinlock, generator device, and callback structure. Depends on ACPI IDs, platform resources, ART clocksource conversion, CPU feature bits, and `hi_lo_writeq()` ordering.

Risks: probe leaks a registered generator if MMIO mapping fails after registration; timing depends on realtime-to-ART conversion and `SAFE_TIME_NS`; event-count check disables on missed pulses; sysfs/core `enabled` state is updated both by core and driver; spinlock protects enable/timer races.

Test signals: ACPI match, feature-gated probe failure, MMIO resource failure cleanup, enable/disable, ART conversion failure, event-counter missed-pulse path, external observation of PPS pulse timing, and remove while enabled.
