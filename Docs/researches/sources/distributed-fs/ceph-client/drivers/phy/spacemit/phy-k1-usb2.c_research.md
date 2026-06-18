# sources/distributed-fs/ceph-client/drivers/phy/spacemit/phy-k1-usb2.c

Purpose: SpacemiT K1 USB2 PHY provider that programs PLL divider values, releases internal resets, enables internal clocks, and clears host-disconnect state.

Important APIs, types, and functions: `struct spacemit_usb2phy` stores PHY, prepared clock, and MMIO regmap. `spacemit_usb2phy_init()` enables the clock, waits for controller reset settling, programs `PHY_PLL_DIV_CFG` for 24 MHz, polls `PHY_PLL_RDY`, writes reset/clock/mode bits, enables HSTXP hardware, and sets host disconnect auto-clear. `spacemit_usb2phy_disconnect()` sets a host disconnect clear bit. `spacemit_usb2phy_exit()` disables the clock.

Control flow: probe gets a prepared clock, maps resource 0, wraps it in a 32-bit regmap, creates the PHY, and registers simple xlate. Init uses `clk_enable()` because the clock was already prepared. On PLL timeout it disables the clock and returns error.

State and persistence: no software mode cache. Hardware register state persists until reset/power. Clock enable state is held between init and exit.

Dependencies and integration points: generic PHY, regmap MMIO, common clock, USB core `.disconnect` PHY callback, compatible `spacemit,k1-usb2-phy`.

Risks: on `clk_enable()` failure the code calls `clk_disable()`, which may be harmless but is unusual for a failed enable. Error after `update_disc_vol` equivalent does not unwind reset bits because only PLL timeout can fail before writes. The `.disconnect` callback ignores port argument and assumes one hardware port.

Test signals: USB2 host/device enumeration, PLL-ready timeout injection, disconnect/reconnect behavior, clock enable balance, regmap register dump for PLL divider and reset mode registers.
