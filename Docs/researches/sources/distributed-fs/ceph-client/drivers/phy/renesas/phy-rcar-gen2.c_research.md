# sources/distributed-fs/ceph-client/drivers/phy/renesas/phy-rcar-gen2.c

Purpose: Implements the Renesas R-Car Gen2/RZ-G1C USB PHY mux and power driver. It exposes two PHY choices per channel and programs `UGCTRL2` selection fields so PCI/USBHS/USB20/USB3 users get exclusive access to the shared hardware path.

Important APIs/types/functions: Core types are `struct rcar_gen2_phy`, `struct rcar_gen2_channel`, `struct rcar_gen2_phy_driver`, and `struct rcar_gen2_phy_data`. PHY ops are `rcar_gen2_phy_init()`, `_exit()`, `_power_on()`, `_power_off()` plus RZ/G1C-specific power ops. `rcar_gen2_phy_xlate()` maps child-node phandles and argument indexes to the correct PHY.

Control flow: Probe requires DT, gets the `usbhs` clock, maps MMIO, selects match data, allocates channel objects for child nodes, reads each child `reg`, derives the selection mask and two select values, creates two PHYs per channel, registers a provider, and stores driver data. Init uses `cmpxchg()` to reserve a channel exclusively, enables the clock, and writes the selected mux field under a spinlock. Power-on only performs PLL/connect sequencing for USBHS selections; RZ/G1C uses a different delay and USB20 suspend behavior. Exit disables the clock and releases the selected PHY.

State and persistence: `selected_phy` is per-channel exclusivity state, initialized to `-1`. `UGCTRL2`, `UGCTRL`, and `LPSTS` hardware fields persist until another PHY selection or power transition. A spinlock serializes shared register updates.

Dependencies and integration points: Depends on generic PHY, OF child nodes, clocks, platform MMIO, atomics, and spinlocks. Consumers are PCI/USB controller nodes that reference child PHYs.

Risks: `cmpxchg()` exclusivity assumes balanced `phy_exit()` calls. Child `reg` values index sparse arrays; invalid values fail probe. Only USBHS paths get PLL lock polling, so other selections rely on downstream controllers for validation.

Test signals: Probe all compatibles, validate phandle translation for each child/argument, attempt concurrent users on one channel and expect `-EBUSY`, verify UGCTRL2 mux bits, test USBHS PLL lock timeout behavior, and power-cycle PCI/USBHS/USB20 paths.
