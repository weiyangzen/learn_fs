# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_ptp.c

## Purpose
`wx_ptp.c` implements Precision Time Protocol hardware clock support for libwx devices. It registers a PHC, maintains cyclecounter/timecounter conversion, supports frequency and time adjustment, configures hardware timestamp filters, handles TX/RX timestamps, detects timestamp hangs, supports 1PPS/perout on capable MACs, and integrates timestamp stats with ethtool.

## Important APIs, types, and functions
Exported functions are `wx_ptp_check_pps_event`, `wx_ptp_reset_cyclecounter`, `wx_ptp_reset`, `wx_ptp_init`, `wx_ptp_suspend`, `wx_ptp_stop`, `wx_ptp_rx_hwtstamp`, `wx_hwtstamp_get`, and `wx_hwtstamp_set`. Important internal callbacks populate `struct ptp_clock_info`: `wx_ptp_adjfine`, `wx_ptp_adjtime`, `wx_ptp_gettimex64`, `wx_ptp_settime64`, `wx_ptp_do_aux_work`, and conditionally `wx_ptp_feature_enable`. Timestamp conversion uses `wx->hw_cc`, `wx->hw_tc`, and `wx->hw_tc_lock`. PPS support uses `wx_ptp_setup_sdp()`, `wx_ptp_trigger_calc()`, and firmware `wx_set_pps()`.

## Control flow and behavior
`wx_ptp_init()` initializes the seqlock, creates or reuses a PTP clock, clears timestamp counters, resets PTP hardware, and marks PTP running. `wx_ptp_reset()` reapplies timestamp mode, recalculates the cyclecounter increment for current MAC/link speed, clears SYSTIME registers, initializes the timecounter to real time, schedules auxiliary work, and re-enables SDP PPS if configured. TX timestamp flow begins in `wx_lib.c` when a TX SKB requests hardware timestamping; this file's aux worker polls `WX_TSC_1588_CTL_VALID`, reads timestamp registers, converts to hwtstamp, completes the SKB, or times out and clears state. RX timestamp flow is called from RX packet processing when a descriptor has the timestamp bit, reads latched registers if valid, and attaches the converted timestamp. Hardware timestamp set/get validate netdev running state and configure TX/RX filters.

## State and persistence
PTP state lives in `struct wx`: `ptp_clock`, `ptp_caps`, `hw_cc`, `hw_tc`, `hw_tc_lock`, `base_incval`, `tstamp_config`, `ptp_tx_skb`, `ptp_tx_start`, PPS fields, last overflow/RX check timestamps, PTP flags, and timestamp counters. Hardware state includes SYSTIME, increment, TX/RX timestamp control/message/filter registers, SDP target registers, and interrupt enables. Timecounter state is protected by a seqlock and must be refreshed periodically to avoid wrap issues.

## Dependencies and integration points
It depends on Linux PTP clock, clocksource/timecounter, timestamping, SKB hwtstamp, PCI, and ptp classifier constants. It integrates with `wx_lib.c` for TX and RX timestamp hooks, `wx_ethtool.c` for timestamp capability/stat reporting, and `wx_hw.c` firmware host-interface PPS command. Device-specific interrupt handlers must call `wx_ptp_check_pps_event()` when relevant PTP/PPS interrupt status is present.

## Risks and edge cases
Only one TX hardware timestamp can be in flight; concurrent timestamp requests increment skipped counters. If hardware never latches TX valid, `wx_ptp_tx_hang()` clears state after one second and increments timeouts. RX timestamp registers can latch after a dropped packet; `wx_ptp_rx_hang()` clears the high register after five seconds without RX progress. `wx_ptp_readtime()` retries high/low reads, but the second rollover path calls `ptp_read_system_prets()` twice, which should be reviewed against expected pre/post timestamp pairing. PPS supports only 1 second periods and no absolute phase; invalid duty cycle or phase requests fail. `wx_hwtstamp_get/set()` reject calls while the netdev is down.

## Test signals
Use `phc2sys`, `ptp4l`, `testptp`, and `hwstamp_ctl` to validate PHC registration, get/set/adjfine/adjtime behavior, TX and RX timestamp delivery, filter normalization, suspend/resume, reset after link speed changes, and PPS/perout on supported MACs. Watch ethtool PTP stats for `tx_hwtstamp_pkts`, skipped, timeout, error, and RX-cleared counters. Kernel logs should not show repeated timestamp hang clearing under normal PTP traffic.
