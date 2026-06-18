# sources/distributed-fs/ceph-client/include/linux/clk/sunxi-ng.h

Purpose: This header exposes Allwinner sunxi-ng clock-control helpers for MMC timing mode and the sun6i RTC CCU probe.

Important APIs/types/functions: APIs are `sunxi_ccu_set_mmc_timing_mode(struct clk *clk, bool new_mode)`, `sunxi_ccu_get_mmc_timing_mode(struct clk *clk)`, and `sun6i_rtc_ccu_probe(struct device *dev, void __iomem *reg)`.

Control flow: MMC drivers or platform code call set/get timing mode on a `struct clk`; RTC CCU platform code probes with a device and mapped register base.

State and persistence behavior: State lives in CCU registers and clock-provider structures. The header itself stores none.

Dependencies and integration points: It relies on visible declarations for `struct clk`, `struct device`, and MMIO types from including contexts, and integrates sunxi-ng CCU providers with MMC and RTC subsystems.

Risks: Timing mode must match the MMC controller and card mode; a wrong setting can produce data corruption. The RTC CCU probe requires a valid MMIO base.

Test signals: MMC mode-switch tests, high-speed card I/O, CCU register readback, RTC clock availability, and Allwinner boot logs validate behavior.
