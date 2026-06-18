# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_ptp.c

## Purpose
`igc_ptp.c` implements PTP hardware clock support for Intel IGC i225-class devices. It exposes PHC time adjustment, read, set, periodic output, external timestamp, PPS, hardware Rx/Tx timestamping, AF_XDP timestamp completion, PCIe PTM cross timestamping, and reset/suspend preservation for the device time registers.

## Important APIs, Types, and Functions
The public driver entry points are `igc_ptp_init()`, `igc_ptp_stop()`, `igc_ptp_suspend()`, `igc_ptp_reset()`, `igc_ptp_hwtstamp_set()`, `igc_ptp_hwtstamp_get()`, `igc_ptp_tx_tstamp_event()`, `igc_ptp_tx_hang()`, `igc_ptp_rx_pktstamp()`, and `igc_ptp_clear_xsk_tx_tstamp_queue()`. PTP clock operations are wired through `adapter->ptp_caps`: `igc_ptp_adjfine_i225()`, `igc_ptp_adjtime_i225()`, `igc_ptp_gettimex64_i225()`, `igc_ptp_getcyclesx64()`, `igc_ptp_settime_i225()`, `igc_ptp_feature_enable_i225()`, and optionally `igc_ptp_getcrosststamp()`. TX timestamp state lives in `adapter->tx_tstamp[]` entries with register masks, register addresses, backing `skb` or XSK metadata, and timeout counters.

## Control Flow
Initialization configures the four hardware TX timestamp register slots, creates SDP pin descriptors, fills PTP clock capabilities, initializes locks, seeds time preservation state, and registers the PHC. Timestamp mode changes pass through `igc_ptp_set_timestamp_mode()`, which toggles TX and RX hardware register bits and per-ring `IGC_RING_FLAG_TX_HWTSTAMP`. TX completion is interrupt driven: `igc_ptp_tx_tstamp_event()` takes `ptp_tx_lock`, reads `TSYNCTXCTL`, drains timestamp registers, applies link-speed latency corrections, reports timestamps to `skb_tstamp_tx()` or AF_XDP metadata, then frees the held buffer. A special register-0 workaround reads `TXSTMPH_0` even when register 0 was not initially ready, then detects races by comparing `TXSTMPL_0` before and after the workaround read.

## State and Persistence Behavior
PTP time is hardware state in `SYSTIM*`, `TIMINCA`, `TIMADJ`, `TSAUXC`, `TSSDP`, timestamp control registers, and PTM registers. Driver shadow state includes `tstamp_config`, `perout[]`, `pps_sys_wrap_on`, `prev_ptp_time`, `ptp_reset_start`, `ptp_flags`, timeout counters, and pending TX timestamp buffers. Suspend saves PHC time and stops PTM when the PCI device is present. Reset restores timestamp mode, PTM/PTP registers, and PHC time by adding elapsed wall time to the saved timestamp.

## Dependencies and Integration Points
The file integrates with Linux PTP, netdev hwtstamp configuration, PCIe PTM, X86 ART cross timestamping, AF_XDP metadata, IGC register accessors, TX/RX ring flags, NAPI wakeups through `igc_xsk_wakeup()`, and netdevice logging. It depends heavily on constants from IGC register and bitfield headers.

## Risks and Edge Cases
PTP paths are concurrency-sensitive: `tmreg_lock`, `free_timer_lock`, `ptm_lock`, and `ptp_tx_lock` protect different register sets and request queues. TX timestamp register 0 has an explicit hardware interrupt erratum workaround. XSK pending timestamp cleanup must run before XDP pool teardown to avoid stale buffer references. Periodic output start times are forced into the future to avoid programming an already elapsed target. Cross timestamping is disabled for unsupported PTM paths and i225-V because of noted lockup risk.

## Test Signals
Useful tests include PHC register/get/set/adjfine checks, hwtstamp set/get for supported and unsupported filters, TX timestamp timeout injection, AF_XDP metadata timestamp completion, XSK pool disable with pending timestamps, reset/suspend/resume PHC continuity, PPS/perout/extts pin assignment conflicts, and PTM cross timestamp success/failure on PTM-capable systems.
