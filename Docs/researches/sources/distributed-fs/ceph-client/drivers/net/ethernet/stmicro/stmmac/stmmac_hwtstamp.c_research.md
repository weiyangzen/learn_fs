# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_hwtstamp.c

Purpose: Implements hardware timestamp and PTP timecounter register operations shared by GMAC and XGMAC stmmac cores.

Important APIs and flow: Exported `stmmac_ptp` and `dwmac1000_ptp` provide `stmmac_hwtimestamp` callbacks for timestamp configuration, sub-second increment, system time init/adjust/read, addend update, auxiliary PTP time read, timestamp interrupt handling, and latency correction. GMAC1000 uses legacy `dwmac1000_get_ptptime` and interrupt helpers for part of the table.

Control flow and state: PTP commands write update registers, set command bits in `PTP_TCR`, and poll until hardware clears them. `config_sub_second_increment()` chooses fine/coarse and digital/binary rollover scaling. `timestamp_interrupt()` handles internal snapshot wakeups or external timestamp events, reading auxiliary snapshot time under `ptp_lock` and emitting `ptp_clock_event()`. Latency correction writes ingress and egress correction registers based on hardware latency registers and timestamp format.

Dependencies and integration: Depends on PTP register definitions, platform snapshot flags, wait queues, `ptp_clock_kernel`, and selected PTP ops from `hwif.c`. Ethtool timestamp info and PTP clock code consume these callbacks.

Risks and test signals: Polling timeouts and rollover-format conversions affect PHC correctness. Test fine/coarse adjustment, digital and binary rollover, init/addend/adjust timeout paths, get_systime stable seconds read, external timestamp events, internal snapshot wakeup, latency correction on i.MX-style hardware, and legacy GMAC1000 behavior.
