# sources/distributed-fs/ceph-client/drivers/ptp/ptp_dfl_tod.c Research

## Purpose
`ptp_dfl_tod.c` exposes an Intel FPGA DFL Time-of-Day private feature as a PTP hardware clock. It maps the DFL MMIO feature, implements PHC time/frequency adjustment operations, and registers a PTP clock.

## Important APIs, Types, And Functions
`struct dfl_tod` holds PTP ops, device, PTP clock pointer, MMIO base, and spinlock. Helpers include `fine_adjust_tod_clock()`, `coarse_adjust_tod_clock()`, `dfl_tod_adjust_fine()`, `dfl_tod_adjust_time()`, `dfl_tod_get_timex()`, and `dfl_tod_set_time()`. `dfl_tod_clock_ops` advertises `adjfine`, `adjtime`, `gettimex64`, and `settime64` with `TOD_MAX_ADJ`.

## Control Flow
Probe allocates state, maps the DFL feature resource, initializes the spinlock, copies ops, and calls `ptp_clock_register()`. Fine frequency adjustment reads the clock frequency register, converts scaled ppm to period and drift-adjust values, and updates period/drift registers under lock. Time adjustment uses fine period adjustments when the delta fits hardware adjust-count limits, otherwise it performs a coarse read-modify-write of seconds/nanoseconds. Gettime reads nanoseconds first to trigger the hardware snapshot, then seconds low/high, while collecting system pre/post timestamps. Settime writes seconds high, seconds low, then nanoseconds, matching the hardware-required write order.

## State And Persistence
In-memory state is minimal. Hardware registers persist the ToD time, base period, drift adjustment, and in-progress adjust count. Spinlock protects register sequences.

## Dependencies And Integration Points
The driver depends on FPGA DFL bus support, MMIO accessors, PTP core, bitfield helpers, `readl_poll_timeout_atomic()`, and kernel time units. It binds to DFL feature id `0x22`.

## Risks
Adjustment math divides by `diff`; if the period is already at min/max, boundary handling must avoid zero divisors. Coarse negative adjustments convert through unsigned `now`, so large negative deltas need scrutiny. Polling is atomic under spinlock and can hold the lock for the adjustment timeout.

## Test Signals
Tests should cover DFL probe/remove, read snapshot ordering, set write ordering, positive/negative adjtime across fine and coarse thresholds, adjfine range checks, register polling timeout, and `PTP_SYS_OFFSET_EXTENDED` behavior using `gettimex64`.
