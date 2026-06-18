# sources/distributed-fs/ceph-client/drivers/usb/musb/sunxi.c

## Purpose

`sunxi.c` is the Allwinner sunxi MUSB glue driver. It adapts the common MUSB core to Allwinner's nonstandard register layout, manages clocks/resets/SRAM/PHY/extcon state, supplies platform ops and FIFO configuration, handles role changes and VBUS, and registers a child `musb-hdrc` device. The source was read as a complete 870-line file.

## Important APIs, Types, and Functions

Important types are `struct sunxi_musb_cfg` and `struct sunxi_glue`. Key functions include `sunxi_musb_work`, `sunxi_musb_set_vbus`, root reset squelch hooks, `sunxi_musb_interrupt`, `sunxi_musb_host_notifier`, `sunxi_musb_init`, `sunxi_musb_exit`, `sunxi_musb_enable`, `sunxi_musb_disable`, `sunxi_musb_set_mode`, `sunxi_musb_recover`, register translation callbacks `sunxi_musb_readb/writeb/readw/writew`, offset callbacks, `sunxi_musb_probe`, and `sunxi_musb_remove`. `sunxi_musb_ops` exposes these to the MUSB core.

## Control Flow

Probe validates `dr_mode`, selects host/peripheral/OTG mode and initial PHY mode, loads SoC-specific config from OF match data, obtains clock/reset/extcon/PHY, registers a generic USB PHY, and registers a child `musb-hdrc` platform device using the parent resources. MUSB init claims SRAM where required, enables clock and reset, forces PIO mode, registers the extcon host notifier before `phy_init`, installs the custom ISR, and pins runtime PM active because sunxi does not support MUSB runtime PM. Extcon host notifications set pending host-mode state; `sunxi_musb_work` performs sleepable PHY power and mode changes and updates DEVCTL/session bits under the MUSB lock. Interrupt handling reads and clears sunxi-specific interrupt registers, forces FADDR to zero on peripheral reset, and calls common `musb_interrupt`.

## State and Persistence Behavior

State is in `struct sunxi_glue.flags`, PHY mode, clock/reset/SRAM ownership, extcon notifier, child platform device, and a file-scope `sunxi_musb` pointer used by register access callbacks. Hardware state includes translated register layout, DEVCTL session state, VBUS/PHY power, FIFO config, and endpoint index. No file-backed persistence exists.

## Dependencies and Integration Points

The driver depends on Allwinner SRAM claiming, clocks, resets, extcon, generic PHY, `phy-sun4i-usb` squelch control, generic USB PHY registration, OF match data, and MUSB platform ops. It integrates deeply through custom read/write callbacks because common MUSB offsets do not match the sunxi layout.

## Risks and Edge Cases

The global `sunxi_musb` limits assumptions around multiple controllers and is required because accessor callbacks lack a MUSB pointer. Register translation must handle generic, indexed endpoint, FIFO, busctl, missing configdata, missing testmode, and missing ULPI registers correctly. Role and PHY mode changes are deferred because PHY calls may sleep while callers may hold spinlocks. DMA is intentionally disabled by returning NULL controller ops. Runtime PM is pinned active.

## Test Signals

Signals include OF probe across supported compatibles, host/peripheral/OTG role selection, extcon ID changes, PHY mode switching, VBUS power sequencing, FADDR reset on peripheral reset, register trace validation against sunxi offsets, endpoint FIFO sizing for four- and five-endpoint SoCs, SRAM/reset variants, and root reset squelch behavior during enumeration.
