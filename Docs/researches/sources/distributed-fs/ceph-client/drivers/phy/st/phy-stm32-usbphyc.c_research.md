# sources/distributed-fs/ceph-client/drivers/phy/st/phy-stm32-usbphyc.c

Purpose: STM32 USB High-Speed PHY Controller provider managing the shared USBPHYC PLL, two UTMI+ PHY ports, per-port tuning, optional VBUS, UTMI switch selection, and an exported 48 MHz clock.

Important APIs, types, and functions: `struct stm32_usbphyc` stores shared MMIO, input clock, reset, regulators, PHY array, atomic PLL consumer count, clk48 hardware, and switch state. `struct stm32_usbphyc_phy` stores per-port PHY, index, VBUS, active flag, and tuning word. `stm32_usbphyc_pll_enable/disable()` manage regulators and PLL with `n_pll_cons`. `stm32_usbphyc_phy_tuning()` builds the per-port TUNE value from DT properties while preserving OTP compensation. `stm32_usbphyc_of_xlate()` validates port cell counts and configures the UTMI switch for port 1. `stm32_usbphyc_clk48_register()` exposes `ck_usbo_48m` backed by the same PLL.

Control flow: probe maps MMIO, enables input clock, resets or clears PLL, ensures PLL disabled, allocates child PHY state, obtains analog regulators, creates child PHYs, reads child `reg`, optional VBUS, applies tuning, registers OF provider, registers clk48, and logs version. PHY init enables the shared PLL and verifies port lock monitor; exit marks inactive and drops a PLL consumer. Power on/off toggles per-port VBUS. Remove exits active PHYs, unregisters clk48, and disables input clock. Resume reapplies switch and tuning registers.

State and persistence: `n_pll_cons` persists shared PLL ownership across PHY ports and clk48 consumers. Per-port active/tune state is kept in memory and replayed on resume. UTMI switch setup is stored and prevents conflicting second requests.

Dependencies and integration points: generic PHY, common clock provider, regulators `vdda1v1`/`vdda1v8`, optional VBUS per child, reset controller, USB host/OTG consumers, DT child nodes with port indices.

Risks: regulator disable returns can block PLL disable and leave partial state. `nphys` is child-count based but port `reg` can be sparse; `usbphyc->phys[port]` stores by iteration order while index selects registers, so assumptions in resume use iteration port for TUNE offset rather than stored index. Tuning validation warns and ignores invalid values rather than failing probe.

Test signals: both ports active simultaneously plus clk48 consumer, PLL reference counting under errors, UTMI switch conflict handling, tuning register readback, regulator failure injection, suspend/resume replay, and USB HS enumeration on host and OTG paths.
