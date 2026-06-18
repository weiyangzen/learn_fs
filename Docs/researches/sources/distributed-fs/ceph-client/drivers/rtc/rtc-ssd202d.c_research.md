# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ssd202d.c

Purpose: MMIO RTC driver for MStar/SigmaStar SSD202D SoCs. It reads and writes a base seconds value plus running counter through an isolation-control handshake.

Important APIs/types/functions: `struct ssd202d_rtc` stores RTC device and base MMIO. `ssd202d_rtc_isoctrl()` writes a fixed sequence to `REG_ISO_CTRL` and polls acknowledgement plus `iso_en`. `ssd202d_rtc_read_reg()` and `_write_reg()` transfer values through read/write data registers while gating isolation. `ssd202d_rtc_read_counter()` latches the running counter. RTC ops check SW enable, combine base and counter for read, and write base/reset counter/enable SW0 for set-time.

Control flow/state/persistence: probe maps MMIO, allocates/registers RTC, and sets a 32-bit range. The driver does not initialize time; `set_time` updates the base, resets counter, and marks SW0 enabled.

Dependencies/integration: compatible `mstar,ssd202d-rtc`, platform MMIO, polling helpers, RTC core. No clock or IRQ integration.

Risks/test signals: `ssd202d_rtc_isoctrl()` returns 0 even if the final `iso_en` poll fails after logging, and most callers ignore errors because read/write helpers are `void`. Test iso handshake timeouts, SW0 disabled reads, base+counter rollover, reset sequencing, and failure injection for delayed/absent acknowledgement.
