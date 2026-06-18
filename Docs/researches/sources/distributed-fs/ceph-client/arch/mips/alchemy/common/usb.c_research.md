## sources/distributed-fs/ceph-client/arch/mips/alchemy/common/usb.c

Purpose: provides the Alchemy USB block power, clock, PHY, coherency, and suspend/resume abstraction for several CPU families. It hides differences between Au1000/Au1500/Au1100/Au1550 OHCI-only controllers, Au1200 combined OHCI/EHCI/UDC/OTG control, and Au1300 DWC-style USB control registers.

Important APIs and functions: `alchemy_usb_control(int block, int enable)` is exported and serializes all block changes with `alchemy_usb_lock`. CPU-specific helpers include `au1000_usb_init()`, `__au1xx0_ohci_control()`, `au1200_usb_control()`, `au1300_usb_control()`, and per-block Au1300 helpers for OHCI0/OHCI1/EHCI/UDC/OTG. `alchemy_usb_init()` is an `arch_initcall()` that initializes the relevant controller state and registers `syscore` PM operations. `alchemy_usb_suspend()` and `alchemy_usb_resume()` save and restore hardware routing/configuration.

Control flow: early init switches on `alchemy_get_cputype()`. Older chips validate a 48 MHz `usbh_clk`, set coherency/endian bits, and leave OHCI disabled until requested. Au1200 writes an all-access/coherent `USBCFG_INIT_AU1200` default. Au1300 disables interrupts/clocks, clears errors/status, and enables coherent SBUS access. Runtime control switches by USB block enum and sets clocks, enables PHYs, and masks/unmasks interrupt sources in documented order.

State and persistence: static `alchemy_usb_pmdata[2]` stores a small amount of register state across suspend. Hardware state persists until reset or PM restore. There is no durable storage.

Dependencies and integration: depends on Linux clock APIs, raw MMIO, syscore PM, Alchemy CPU IDs and physical address constants, and exported USB block IDs. USB host/device drivers call the exported control API before using controller MMIO.

Risks: most routines manipulate undocumented or timing-sensitive bits; missing barriers or delays would break enumeration. The older OHCI reset-done wait has no timeout. Au1300 port 2 routing is intentionally not autodetected, so boot firmware or board code must configure it. Shared PHY shutdown depends on correctly observing active clocks.

Test signals: successful init returns from `arch_initcall` and allows USB controller drivers to probe. Suspend/resume should preserve Au1200/Au1300 port routing. Runtime block enable/disable can be validated by OHCI/EHCI/UDC probe, disconnect/reconnect, and no AHB faults.
