# sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/usb_831x.c

## Purpose
`usb_831x.c` configures MPC831x/MPC8308/MPC8315 USB clocking, pinmux, and PHY control before USB controller drivers probe.

## Important APIs, Types, and Functions
`mpc831x_usb_cfg()` finds `"fsl-usb2-dr"`, reads `phy_type`, maps IMMR, chooses SCCR USB clock settings based on parent IMMR compatible, programs ULPI pinmux bits when needed, maps USB controller registers, and writes the USB control register for UTMI, ULPI, and optional OTG mode.

## Control Flow, State, and Persistence
It performs one-shot IMMR and USB register writes; no local state persists. OF node references and mappings are released before return.

## Dependencies and Integration Points
It depends on `mpc83xx.h` bit definitions, OF USB nodes/properties, `get_immrbase()`, optional `CONFIG_USB_OTG`, and board setup functions that call it.

## Risks and Test Signals
Risks include parent-node lifetime after early `of_node_put`, unsupported PHY strings, 8308 special-case behavior, and mismatched ULPI/UTMI muxing. Test signals are USB DR probe, PHY clock selection, OTG mode on supported boards, and warning-free setup for each 831x-family SoC.
