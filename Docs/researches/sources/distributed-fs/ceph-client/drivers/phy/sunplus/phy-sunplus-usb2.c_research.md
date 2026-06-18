# sources/distributed-fs/ceph-client/drivers/phy/sunplus/phy-sunplus-usb2.c

Purpose: Sunplus SP7021 USB2 PHY provider that initializes UPHY and MOON4 register blocks, applies OTP-derived disconnect voltage, battery-charger settings, chirp mode, and PLL power cycling.

Important APIs, types, and functions: `struct sp_usbphy` stores device, two MMIO resource regions (`phy`, `moon4`), reset, clock, and OTP bit offset. `update_disc_vol()` reads nvmem cell `disc_vol`, extracts `J_DISC` bits, and programs disconnect level with a default fallback. `sp_uphy_init()` enables clock/reset and writes many certification and charger settings. `sp_uphy_power_on/off()` toggle PLL power bits with 1 ms delays. `sp_uphy_exit()` asserts reset and disables clock.

Control flow: probe maps named `phy` and `moon4` resources, obtains clock/reset, reads `sunplus,disc-vol-addr-off`, creates one PHY, and registers simple xlate. Init enables resources, writes MOON4 defaults, updates disconnect voltage, disables ECO/power-saving bits, programs charger and chirp settings. Power-on cycles PLL off/on twice then clears override; power-off powers down PLL and clears override.

State and persistence: hardware state persists in UPHY/MOON4 registers. OTP-derived disconnect level is not cached. Clock/reset state is held from init to exit.

Dependencies and integration points: generic PHY, clock/reset frameworks, nvmem consumer, named MMIO resources, SP7021 USB controller.

Risks: `update_disc_vol()` can call `nvmem_cell_read()` even when `nvmem_cell_get()` returned an error other than defer, which is risky. If `update_disc_vol()` returns an error after clock/reset enable, init returns without unwinding. Non-posted write note suggests ordering matters, but the driver uses ordinary writes without readbacks except delays.

Test signals: OTP present/missing/defer cases, disconnect threshold register readback, USB certification tests, PLL power-cycle timing, init error unwind testing, and USB enumeration at LS/FS/HS.
