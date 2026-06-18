# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_ptp.c

Purpose: Linux PTP hardware clock implementation for STMMAC. It provides clock adjustment, get/set time, perout/PPS, external timestamping, cross timestamping, and registration/unregistration.

Important APIs and functions: `stmmac_adjust_freq()` writes a scaled-ppm-adjusted addend. `stmmac_adjust_time()` shifts hardware time and temporarily disables/reprograms EST/TAS when active. `stmmac_get_time()` and `stmmac_set_time()` read/write hardware system time under `ptp_lock`. `stmmac_enable()` handles `PTP_CLK_REQ_PEROUT` with flexible PPS and `PTP_CLK_REQ_EXTTS` with auxiliary snapshot registers. `stmmac_getcrosststamp()` uses an optional platform `crosststamp` callback. `stmmac_ptp_register()` customizes `ptp_clock_info` from hardware capabilities and registers it. `stmmac_ptp_unregister()` tears it down.

Control flow: hardware interface selection copies a PTP ops template into `priv->ptp_clock_ops`; registration updates per-out/ext-ts counts, max adjustment, CDC error, and crosststamp support; then PTP core callbacks enter this file. Unregister runs when the common driver removes PTP support.

State and persistence: `stmmac_priv` stores `ptp_clock_ops`, registered clock pointer, `ptp_lock`, `aux_ts_lock`, PPS config, addend, sub-second increment, systime flags, platform PTP clock rate, CDC adjustment, and EST state. External snapshot enable toggles a platform flag.

Dependencies and integration: Linux PTP core, STMMAC timestamp hardware callbacks, EST/TAS configuration, optional platform crosststamp, and GMAC1000-specific enable helpers.

Risks and test signals: EST reconfiguration failure during `adjtime` is logged but not returned. Perout times in the past are treated as offsets with a 500 us guard. Only one auxiliary snapshot channel is enabled at a time. Test with `ptp4l`, PPS/perout, external timestamps, crosststamp, EST under time adjustments, and driver unregister/re-register.
