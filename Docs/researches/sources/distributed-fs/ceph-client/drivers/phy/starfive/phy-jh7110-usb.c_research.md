# sources/distributed-fs/ceph-client/drivers/phy/starfive/phy-jh7110-usb.c

Purpose: StarFive JH7110 USB2 PHY provider for the Cadence USB controller, handling 125 MHz clocks, low-speed keepalive, RX normal power, and syscon USB split selection.

Important APIs, types, and functions: `struct jh7110_usb2_phy` stores PHY, MMIO, sys syscon, `125m` and `app_125m` clocks, and current mode. `usb2_set_ls_keepalive()` toggles host keepalive. `usb2_phy_set_mode()` validates USB modes, updates keepalive, and sets `USB_PDRSTN_SPLIT` in syscon. `jh7110_usb2_phy_init/exit()` set clock rate, enable app clock, and toggle RX normal power.

Control flow: probe obtains clocks, maps MMIO, creates PHY, registers provider, and looks up sys syscon by compatible. Init sets the 125 MHz clock rate, enables app clock, and enables RX normal power. Set-mode handles host/device/OTG differences for keepalive. Exit disables app clock.

State and persistence: current mode is cached. Hardware state persists in local USB registers and syscon split bit. `usb_125m_clk` is rate-set but not explicitly enabled by this driver.

Dependencies and integration points: generic PHY, common clock, syscon/regmap, USB OF modes, Cadence USB controller on JH7110.

Risks: provider registration occurs before syscon lookup failure is returned, but devm cleanup handles probe failure. Syscon lookup by global compatible assumes one relevant syscon. Device mode clears keepalive but still sets split bit.

Test signals: host/device/OTG mode switching, LS device keepalive behavior, app clock balance, syscon split bit readback, and USB2 enumeration through Cadence controller.
