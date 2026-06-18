# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvpp2/mvpp2_tai.c Research

## Purpose
`mvpp2_tai.c` implements PTP hardware clock support for the Marvell PP2.2 Time Application Interface. It registers a `ptp_clock`, supports fine frequency adjustment, time adjustment, get/set time, periodic timestamp refresh, and conversion of compact RX/TX hardware timestamps into full kernel hardware timestamps.

## Important APIs, Types, And Functions
The local `struct mvpp2_tai` stores `ptp_clock_info`, the registered `ptp_clock`, MMIO base, a spinlock, the fixed-point clock period, and a cached full timestamp refreshed every two seconds. Register helpers are `mvpp2_tai_modify()`, `mvpp2_tai_write()`, `mvpp2_tai_read()`, `mvpp22_tai_read_ts()`, `mvpp2_tai_write_tlv()`, and `mvpp2_tai_op()`. PTP callbacks are `mvpp22_tai_adjfine()`, `mvpp22_tai_adjtime()`, `mvpp22_tai_gettimex64()`, `mvpp22_tai_settime64()`, and `mvpp22_tai_aux_work()`.

Driver-facing APIs are `mvpp22_tai_probe()`, `mvpp22_tai_ptp_clock_index()`, `mvpp22_tai_tstamp()`, `mvpp22_tai_start()`, and `mvpp22_tai_stop()`. The implementation also calculates fractional period adjustments through `mvpp22_calc_frac_ppm()` and initializes hardware step size with `mvpp22_tai_set_step()` and `mvpp22_tai_init()`.

## Control Flow
Probe allocates `struct mvpp2_tai`, points it at `priv->iface_base`, sets a nominal 3 ns period in 32.32 fixed point, releases the TAI reset, fills the PTP callback table, registers a cleanup action, registers the PTP clock, and stores it in `priv->tai`. `mvpp22_tai_start()` immediately reads the time through the aux worker and schedules periodic refreshes. `mvpp22_tai_tstamp()` combines the cached seconds with the 2-bit seconds and 30-bit nanoseconds in queue timestamps, adjusting by a small modulo delta.

PTP operations serialize register access with `tai->lock`. `gettimex64()` triggers a capture, records system pre/post timestamps around that trigger, reads the valid capture bank, and returns `-EBUSY` if neither capture valid bit is set. `settime64()` writes TLV registers and triggers an update with phase update enabled. `adjtime()` writes a delta and triggers increment or decrement. `adjfine()` converts scaled ppm to a signed fractional nanosecond period delta and triggers a frequency update.

## State, Persistence, And Dependencies
Persistent state includes the hardware TOD counter, TLV staging registers, frequency step registers, registered PTP clock, and cached `tai->stamp`. The cache is not a durable store; it is a reconstruction aid for compact packet timestamps. The code depends on Linux PTP clock infrastructure, `ptp_schedule_worker()`, `ptp_cancel_worker_sync()`, `ptp_read_system_prets/postts()`, MMIO helpers, spinlocks, and MVPP22 TAI register offsets from `mvpp2.h`.

## Integration Points
MVPP2 probe code calls `mvpp22_tai_probe()` for PP2.2 hardware, starts/stops the PTP worker with interface lifetime, exposes the PTP clock index to timestamping configuration paths, and uses `mvpp22_tai_tstamp()` from packet completion paths to populate `skb_shared_hwtstamps`.

## Risks
The file explicitly warns that external use of `PTP_EVENT_REQ` can trigger the currently programmed TCF operation and cannot be masked, so board mux configuration can corrupt time reads or updates outside driver control. `mvpp22_tai_tstamp()` depends on the aux worker refreshing `tai->stamp` often enough that the 2-bit seconds field can be reconstructed; long stalls can misplace timestamps by multiples of four seconds. Busy loops are avoided, but capture can fail with `-EBUSY`. The period is hardcoded for the 333.333333 MHz-derived clock as exactly 3 ns to avoid documented rounding error, so different clocking would need a new calculation.

## Test Signals
Useful tests include PTP clock registration/removal, `phc2sys`/`ptp4l` time read and adjustment paths, `adjfine()` at positive/negative extremes and `S64_MIN` rejection in `adjtime()`, RX/TX timestamp reconstruction around second wrap and after worker delays, settime followed by gettimex consistency, module unload cleanup, and board-level validation that PTP_EVENT_REQ muxes are not enabled while this driver owns the TAI.
