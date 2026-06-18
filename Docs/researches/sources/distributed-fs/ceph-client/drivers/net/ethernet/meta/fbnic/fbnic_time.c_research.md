# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_time.c

## Purpose
`fbnic_time.c` implements FBNIC PTP clock support and timestamp conversion support. The hardware clock free-runs, while the driver maintains software offset and cached high bits to turn 40-bit descriptor timestamps into full nanosecond PHC time.

## Important APIs, Types, And Functions
Public functions are `fbnic_time_init()`, `fbnic_time_start()`, `fbnic_time_stop()`, `fbnic_ptp_setup()`, and `fbnic_ptp_destroy()`. PTP callbacks include `fbnic_ptp_adjfine()`, `fbnic_ptp_adjtime()`, `fbnic_ptp_gettimex64()`, `fbnic_ptp_settime64()`, and `fbnic_ptp_do_aux_work()`. Internal helpers read stable 64-bit hardware time, program the addend, refresh cached high bits, and reset PTP hardware.

## Control Flow
PTP setup initializes `time_lock`, resets PTP registers, copies the static `ptp_clock_info`, and registers the PHC. Open calls `fbnic_time_start()`, which refreshes cached high bits and schedules periodic PTP auxiliary work. Aux work warns if refresh is stale, reads the hardware high register, intentionally caches a slightly older high value, and reschedules. Stop cancels the worker and checks for refresh stalls.

PTP adjfine computes a 600 MHz clock period in Q16.32 fixed-point ns, applies scaled ppm adjustment, writes addend registers, and triggers hardware addend set. Adjtime and settime update the software offset under lock and `u64_stats_sync`. Gettime reads high/low/high registers around system timestamp capture to produce a stable PHC reading plus offset.

## State And Persistence
Hardware state includes PTP control, addend, init, adjust, and counter registers. Driver state includes `fbd->ptp`, `fbd->ptp_info`, `fbd->time_lock`, `fbd->last_read`, and per-netdev `fbn->time_high`, `fbn->time_offset`, and `fbn->time_seq`. The free-running counter is not stepped for settime/adjtime; only addend and software offset change.

## Dependencies And Integration Points
This file depends on Linux PTP clock APIs, jiffies/timers, CSR helpers, and `fbnic_net` private state. `fbnic_txrx.c` uses the `time_high`/`time_offset` scheme to convert RX/TX descriptor timestamps. Netdev open/stop controls the aux worker lifecycle.

## Risks
The timestamp conversion design assumes periodic high-bit refresh with large margin before 40-bit wrap. If the worker stalls long enough, descriptor timestamp conversion can become ambiguous. Offset updates need `u64_stats_sync` on 32-bit systems. MMIO disappearance returns `-EIO` from hardware-touching PTP callbacks only after reads/writes notice `fbnic_present()` is false.

## Test Signals
Signals include successful PHC registration, stable gettimex reads, adjfine addend changes, settime/adjtime offset behavior, aux worker refresh warnings when delayed, correct conversion of RX/TX timestamps across 40-bit low wrap, and clean PTP unregister on remove.
