# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fec_ptp.c

### Purpose
`fec_ptp.c` provides IEEE 1588/PTP hardware clock support for FEC/ENET variants with enhanced buffer descriptors and a PTP clock. It registers a PHC, manages the FEC 31-bit nanosecond counter, supports frequency/time adjustment, PPS and periodic output, hardware timestamp configuration, and save/restore around MAC resets.

### Important APIs, Types, And Functions
The exported internal functions are `fec_ptp_init()`, `fec_ptp_stop()`, `fec_ptp_start_cyclecounter()`, `fec_ptp_save_state()`, `fec_ptp_restore_state()`, `fec_ptp_set()`, and `fec_ptp_get()`. The local PTP clock callbacks are `fec_ptp_adjfine()`, `fec_ptp_adjtime()`, `fec_ptp_gettime()`, `fec_ptp_settime()`, and `fec_ptp_enable()`. PPS/perout helpers include `fec_ptp_enable_pps()`, `fec_ptp_pps_perout()`, `fec_ptp_pps_perout_handler()`, `fec_ptp_pps_disable()`, `fec_pps_interrupt()`, and the periodic `fec_time_keep()` work item.

### Control Flow
Initialization fills `ptp_clock_info`, selects `fsl,pps-channel` or channel 0, derives cycle speed and increment from `clk_ptp`, initializes the spinlock/cyclecounter/timecounter, schedules keepalive work, sets up the perout hrtimer, optionally requests a `pps` IRQ or fallback IRQ index, and registers the PHC. `fec_ptp_start_cyclecounter()` programs `FEC_ATIME_INC`, `FEC_ATIME_EVT_PERIOD`, and `FEC_ATIME_CTRL`, then initializes a 31-bit `cyclecounter` and `timecounter`.

PTP get/set/adjust operations serialize with `ptp_clk_mutex` and/or `tmreg_lock`. `fec_ptp_adjfine()` computes correction increment/period values and programs `FEC_ATIME_INC`/`FEC_ATIME_CORR`; `adjtime()` adjusts the software timecounter; `settime()` writes `FEC_ATIME` and reinitializes the counter base. PPS enable programs compare channel mode, first/next compare counters, pin period mode, and interrupt bits. Periodic output validates period/start time, rejects overlap with PPS, and uses an hrtimer if the requested start is beyond the 31-bit hardware compare range. The PPS interrupt reloads the next compare value and emits `PTP_CLOCK_PPS` events.

### State, Persistence, And Dependencies
State is held in `struct fec_enet_private`: PHC pointer/caps, cyclecounter/timecounter, `tmreg_lock`, PTP clock state mutex, timestamp enable flags, PPS/perout channel and timing fields, delayed keepalive work, perout hrtimer, and `ptp_saved_state`. State is not persisted to storage, but `fec_ptp_save_state()` records PHC/system time and correction registers before MAC reset, and `fec_ptp_restore_state()` reconstructs PHC time and PPS state afterward. Dependencies include the Linux PTP clock API, timecounter/cyclecounter helpers, hrtimer, delayed work, MMIO, OF, platform IRQs, and the FEC private header.

### Integration Points
`fec_main.c` calls PTP init during probe when enhanced descriptors are available, starts/restores the cyclecounter on MAC restart, saves state before reset/stop, exposes hwtstamp get/set via netdev ops, and uses descriptor timestamps for RX/TX SKBs. Ettool timestamp info reports the PHC index when registered.

### Risks
The hardware counter is only 31 bits, so keepalive reads every second are required to avoid timecounter ambiguity. PPS and PEROUT are mutually exclusive on the selected channel; failure to enforce this would corrupt output timing. Clock gating is guarded by `ptp_clk_mutex`, but callers must respect clock state. The code handles a capture erratum with a delay, so missing the quirk can produce stale timestamps. There is a visible duplicated assignment of `reload_period = div_u64(period_ns, 2);`, harmless but suspicious.

### Test Signals
Test with `phc2sys`/`ptp4l`, `ethtool -T`, `SIOCSHWTSTAMP` TX/RX modes, TX/RX timestamp delivery, `phc_ctl` get/set/adjfine/adjtime, PPS enable/disable, PEROUT start periods up to 4 seconds, start times beyond the 31-bit compare range, MAC reset/link restart preserving PHC time, suspend/resume, PTP clock gating failure paths, and PPS IRQ delivery.
