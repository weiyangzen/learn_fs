# sources/distributed-fs/ceph-client/drivers/ssb/embedded.c

## Purpose
Embedded SSB glue exposing watchdog/GPIO convenience APIs and PCI BIOS callbacks that route PCI platform initialization and IRQ mapping to SSB PCI core or GigE pseudo-PCI devices.

## Important APIs, Types, and Functions
Exports `ssb_watchdog_timer_set`, GPIO helpers (`ssb_gpio_in/out/outen/control/intmask/polarity`), and implements `ssb_watchdog_register`, `ssb_pcibios_plat_dev_init`, and `ssb_pcibios_map_irq`. GigE callback helpers search registered buses for active GigE cores.

## Control Flow
Watchdog registration picks ChipCommon or EXTIF backend, fills a `bcm47xx_wdt` descriptor, and registers a `bcm47xx-wdt` platform device. GPIO helpers lock `bus->gpio_lock`, dispatch to ChipCommon or EXTIF backend, and return the masked result. PCI BIOS init first tries PCI core handling, then optional GigE callbacks via `ssb_for_each_bus_call`. IRQ mapping follows the same order.

## State and Persistence
Stores `bus->watchdog` platform device and changes backend watchdog/GPIO registers. PCI callbacks do not store new state except through downstream PCI resource and IRQ fixups.

## Dependencies and Integration Points
Requires embedded SSB, BCM47xx watchdog interface, platform devices, SSB PCI core, optional GigE driver, and global SSB bus list iteration.

## Risks
GPIO helpers warn but otherwise return zero when no backend exists. Watchdog registration assumes max timer fields were initialized by ChipCommon/EXTIF. PCI BIOS callbacks depend on SSB buses and built-in core drivers already being registered.

## Test Signals
On BCM47xx SoCs, watchdog platform device should register and set timers through correct backend. GPIO exported helpers should be serialized and reflect hardware. PCI devices behind SSB PCI/GigE should receive fixed resources and IRQs.
