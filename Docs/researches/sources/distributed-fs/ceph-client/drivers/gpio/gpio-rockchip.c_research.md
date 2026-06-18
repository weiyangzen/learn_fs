# sources/distributed-fs/ceph-client/drivers/gpio/gpio-rockchip.c

## Purpose
This driver registers GPIO banks that are owned by the Rockchip pinctrl controller. It exposes bank GPIO operations, debounce support, IRQ domains, and interrupt demultiplexing for v1 and v2 register layouts.

## Important APIs, Types, and Functions
The driver operates on `struct rockchip_pin_bank` from the Rockchip pinctrl subsystem rather than defining a separate private bank type. `gpio_regs_v1` and `gpio_regs_v2` describe register offsets. Helpers `rockchip_gpio_writel()`, `rockchip_gpio_readl()`, and bit variants abstract v2 write-enable halfword semantics. Gpiolib callbacks are collected in `rockchip_gpiolib_chip`; IRQ setup uses `rockchip_interrupts_register()` and `irq_alloc_domain_generic_chips()`.

## Control Flow
Probe locates the parent pinctrl device, resolves the bank by DT alias or fallback counter, maps the bank resource, enables the clock, reads version ID, selects register layout, registers the gpio chip, attaches pin ranges when old DT lacks `gpio-ranges`, registers interrupts, then applies deferred pin configurations queued by pinctrl. IRQ demux reads `int_status`, optionally toggles polarity for emulated both-edge mode on v1, and dispatches domain IRQs.

## State and Persistence
Bank state is mostly hardware-backed. Software fields include `toggle_edge_mode`, `saved_masks`, clocks, deferred pin lists, pin range metadata, and debounce clock state. IRQ suspend saves the mask register and masks non-wakeup lines; resume restores it. Debounce can enable/disable a second clock and program shared divider registers on v2.

## Dependencies and Integration Points
This file is tightly coupled to `pinctrl-rockchip.h`, `struct rockchip_pinctrl`, OF address/IRQ parsing, clocks, pinctrl generic config, gpiolib, irqdomain generic chips, and postcore initialization so GPIO banks are available early enough for pinctrl users.

## Risks
Register version detection depends on reading the v2 version register after enabling the clock; unsupported IDs fail probe. V1 both-edge interrupts are emulated by polarity toggling and can miss rapid transitions. Debounce divider is shared and only increased when a larger value is requested, which may affect earlier consumers. Error paths after pin range setup require chip removal.

## Test Signals
Test v1 and v2 banks, deferred output/input configuration, `gpio-ranges` and old pin-range fallback, all IRQ trigger types including v1 both-edge emulation and v2 hardware both-edge, suspend/resume mask behavior, debounce enable/disable and invalid debounce ranges, and clock failure paths.
