<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/usb.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/usb.c

## Purpose
Performs platform-level OMAP1 full-speed USB initialization for UDC, OHCI, and OTG, including pin muxing, transceiver mode programming, clock/power setup, and platform-device registration.

## Important APIs, Types, and Functions
Exports `omap1_usb_init()`. Important helpers are `omap_otg_init()`, `omap1_usb0_init()`, `omap1_usb1_init()`, `omap1_usb2_init()`, OMAP1510 local-bus setup/reset helpers, and device init functions for UDC/OHCI/OTG.

## Control Flow
`omap1_usb_init()` clones board USB config, installs port-init callbacks and platform-device pointers, then dispatches to OMAP16xx OTG init or OMAP1510 init. Port helpers mux pins and update `USB_TRANSCEIVER_CTRL`/SYSCON mode bits according to wire count, device/host role, alternate pin group, and CPU variant. OMAP16xx OTG init programs OTG_SYSCON registers, gates clocks idle, and registers UDC/OHCI/OTG devices as requested. OMAP1510 init programs HMC mode, DPLL/APLL USB clocking, optional local-bus MMU offset for OHCI DMA, and registers devices.

## State and Persistence Behavior
State persists in allocated copied `omap_usb_config`, static platform devices/resources, DMA masks, and hardware mux/transceiver/clock registers. OMAP1510 OHCI also uses local-bus MMU table state.

## Dependencies and Integration Points
Depends on board-supplied `omap_usb_config`, mux entries, `ocpi_enable()` for OHCI, USB UDC/OHCI/OTG configs, DMA direct offset APIs, IRQ macros, ULPD/MOD/OTG register definitions, and CPU predicates.

## Risks
USB pin wiring is board-specific and many wire counts are invalid for ports. UART/USB pin conflicts and documented USB2 errata can break devices. DPLL lock polling can hang if USB clock setup is wrong. OMAP1510 local-bus memory-size assumption is fixed at 32 MB.

## Test Signals
Test UDC, OHCI, and OTG modes on 1510, 1611/5912, and 1710 boards with 2/3/4/6-wire configs. Verify platform devices register only when requested, DPLL locks, OHCI DMA works, and invalid wire counts log errors.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/usb.c -->
