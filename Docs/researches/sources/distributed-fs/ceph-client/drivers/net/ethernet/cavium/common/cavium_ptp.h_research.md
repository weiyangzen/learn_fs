# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/common/cavium_ptp.h

## Purpose
This header declares the shared Cavium PTP clock object and provides enabled/disabled helper APIs for Cavium network drivers that use PTP timestamp conversion.

## Important APIs, Types, And Functions
`struct cavium_ptp` contains the PCI device, spinlock, cyclecounter, timecounter, MMIO base, clock rate, `ptp_clock_info`, and registered `ptp_clock`. When `CONFIG_CAVIUM_PTP` is reachable it declares `cavium_ptp_get()` and `cavium_ptp_put()`, defines `cavium_ptp_tstamp2time()` with locked `timecounter_cyc2time()`, and exposes `cavium_ptp_clock_index()`. When disabled, inline stubs return `-ENODEV`, `0`, or `-1`.

## Control Flow
Consumers call `cavium_ptp_get()`, use `cavium_ptp_tstamp2time()` to convert hardware cycle timestamps into nanoseconds, optionally query the PTP clock index, then call `cavium_ptp_put()`. Disabled builds compile through the same call sites without linking the PTP object.

## State And Persistence
The header describes in-memory and MMIO-backed clock state but does not allocate it. Timestamp conversion reads software timecounter state protected by `spin_lock`.

## Dependencies And Integration Points
It depends on `linux/ptp_clock_kernel.h` and `linux/timecounter.h` and is consumed by Cavium NIC drivers that need optional PTP support.

## Risks
Disabled stubs return plausible scalar values (`0` timestamp, `-1` index); callers must treat those as feature absence, not valid time. Consumers must balance `get`/`put` because the enabled accessor holds a PCI reference. Locking is internal to conversion, but lifetime is external.

## Test Signals
Compile with `CAVIUM_PTP=y/m/n`; verify consumers handle `ERR_PTR(-ENODEV)`, `-EPROBE_DEFER`, and successful conversion paths; validate reference cleanup on driver remove.
