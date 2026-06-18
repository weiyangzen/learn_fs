# sources/distributed-fs/ceph-client/drivers/net/ethernet/cadence/macb_ptp.c

## Purpose
`macb_ptp.c` implements IEEE 1588 Precision Time Protocol hardware timestamp support for Cadence GEM devices with DMA PTP descriptor extensions. It registers a PHC, initializes the GEM timestamp unit, adjusts and reads TSU time, converts descriptor timestamp words into skb hardware timestamps, and handles ethtool hardware timestamp configuration.

## Important APIs and functions
`macb_ptp_desc()` locates timestamp extension words. `gem_tsu_get_time()` and `gem_tsu_set_time()` read/write split TSU time with rollover handling. `gem_tsu_incr_set()`, `gem_ptp_adjfine()`, and `gem_ptp_adjtime()` implement PHC frequency/time adjustment. `gem_ptp_init()` registers the PHC and initializes TSU state; `gem_ptp_remove()` unregisters and clears it. `gem_ptp_rxstamp()` and `gem_ptp_txstamp()` attach timestamps to skbs. `gem_get_hwtst()` and `gem_set_hwtst()` expose timestamp configuration.

## Control flow and state
The main driver calls PTP init/remove during open/close and suspend/resume. TX completion and RX delivery call the stamp helpers through inline wrappers from `macb.h`. State lives in `struct macb` fields such as `ptp_clock`, `ptp_clock_info`, `tsu_rate`, `tsu_incr`, `tsu_clk_lock`, and `tstamp_config`, plus hardware TSU registers, descriptor timestamp words, `TXBDCTRL`, `RXBDCTRL`, and NCR timestamp bits. There is no disk persistence.

## Dependencies, risks, and test signals
This file depends on the PTP clock subsystem, skb timestamp APIs, kernel time helpers, spinlocks, and descriptor/register definitions from `macb.h`. Risks include TSU race/rollover handling, descriptor layout mismatch with 64-bit DMA, truncated seconds reconstruction, unsupported filter errors, one-step sync mode state, and PHC registration failure. Test with `ethtool -T`, hwtstamp configuration, `ptp4l`, TX/RX timestamp delivery, adjfine/adjtime, and suspend/resume.
