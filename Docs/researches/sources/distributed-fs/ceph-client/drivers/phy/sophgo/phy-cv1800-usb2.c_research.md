# sources/distributed-fs/ceph-client/drivers/phy/sophgo/phy-cv1800-usb2.c

Purpose: Sophgo CV1800/SG2000 USB2 PHY provider that controls USB mode ID override and required USB clocks through a parent syscon.

Important APIs, types, and functions: `struct cv1800_usb_phy` stores the generic PHY, parent syscon, three clocks, and OTG capability flag. `cv1800_usb_phy_set_mode()` implements host/device/OTG mode switching by setting ID override and VBUS power bits in `REG_USB_PHY_CTRL`. `cv1800_usb_phy_set_clock()` sets app, LPM, and standby clock rates.

Control flow: probe requires a parent device, obtains parent syscon regmap, enables clocks named `app`, `lpm`, and `stb` with devm helpers, creates the PHY, sets clock rates to 125 MHz, 12 MHz, and roughly 333 kHz, stores driver data, and registers simple xlate. `set_mode` clears VBUS power for device mode, sets it for host mode, and in OTG mode returns without change unless `support_otg` is true.

State and persistence: runtime mode is not cached, but syscon bits persist in hardware. `support_otg` is currently initialized false, so OTG mode is effectively a no-op success.

Dependencies and integration points: generic PHY, common clock, syscon parent MFD, DWC2 USB controller consumers, compatible `sophgo,cv1800b-usb2-phy`.

Risks: `devm_kmalloc()` leaves fields uninitialized unless assigned; most fields are assigned, but future fields may be unsafe. `spinlock_t lock` is initialized but unused. `dev_info()` logs every mode switch and may be noisy. OTG support flag is hardcoded false, so consumers expecting dynamic ID behavior will not get it.

Test signals: host/device mode switching with DWC2, syscon bit readback for ID and VBUS power bits, clock rate verification, compile-test warnings for unused lock/debugfs include, and probe deferral on missing clocks/syscon.
