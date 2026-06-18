# sources/distributed-fs/ceph-client/drivers/gpio/gpio-aggregator.c

## Purpose
This module creates virtual GPIO chips by aggregating existing GPIO descriptors. It provides a modern configfs interface, a legacy sysfs `new_device`/`delete_device` interface, a platform driver that consumes generated lookup tables, and exported GPIO forwarder APIs for other drivers.

## Important APIs, types, and functions
User-facing state is represented by `struct gpio_aggregator` and `struct gpio_aggregator_line`; forwarding state is `struct gpiochip_fwd`. Important lifecycle helpers are `gpio_aggregator_alloc()`, `gpio_aggregator_activate()`, `gpio_aggregator_deactivate()`, `gpio_aggregator_parse()`, `gpio_aggregator_probe()`, and module init/exit. Exported forwarder APIs include `devm_gpiochip_fwd_alloc()`, `gpiochip_fwd_desc_add()`, `gpiochip_fwd_register()`, and directional/get/set/config/IRQ helpers in the `GPIO_FORWARDER` namespace.

## Control flow
Configfs users create an aggregator group, create sequential `lineN` groups, set `key`, `offset`, and optional `name`, then write `live=1`. Activation builds a software node with line names, creates a lookup table, registers a platform device, waits for probing, and locks configfs entries while live. Legacy sysfs parses a flat argument string into the same line structures and immediately registers the platform device. The platform probe resolves all GPIO descriptors and registers a forwarding gpiochip.

## State and persistence behavior
State lives in configfs/sysfs-created kernel objects, an IDR, lookup tables, platform devices, GPIO descriptors, valid masks, and optional per-line delay timings. It is runtime-only and removed on deactivation or module unload. Forwarded GPIO values remain owned by the original GPIO providers.

## Dependencies and integration points
The file integrates configfs, platform devices, software nodes, gpiod lookup tables, gpiolib descriptor consumers, optional OF GPIO translation for `gpio-delay`, IDR allocation, and exported symbols for external forwarder users. It forwards operations to `gpiod_*` APIs and preserves sleep semantics for descriptor arrays.

## Risks and edge cases
Major risks are lifetime and locking bugs between configfs, sysfs, module references, and platform device probing. Configfs activation rejects nonsequential or incomplete line definitions, and config entries become busy while live. Forwarders with any sleeping or not-yet-populated line mark the whole chip `can_sleep`. The delay feature mutates per-line timing during OF translation and sleeps or busy-waits after set operations.

## Test signals
Test configfs creation, invalid line names/order, live activation/deactivation, legacy sysfs parsing for chip+offset lists and named lines, deferred probe handling, forwarded get/set/get_multiple/set_multiple/config/to_irq behavior, active-low delay timing, and module unload cleanup of legacy aggregators.
