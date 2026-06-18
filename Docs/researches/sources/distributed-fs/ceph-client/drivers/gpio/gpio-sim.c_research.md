# sources/distributed-fs/ceph-client/drivers/gpio/gpio-sim.c

## Purpose
`gpio-sim.c` is a GPIO simulator for testing. It exposes a configfs hierarchy for defining simulated devices, banks, lines, and GPIO hogs, then instantiates platform devices backed by software nodes. The platform side registers simulated gpio chips with sysfs controls and an `irq_sim` domain.

## Important APIs, Types, and Functions
Runtime chip state is `struct gpio_sim_chip`: gpio chip, request/direction/value/pull bitmaps, irq simulation domain, mutex, and per-line sysfs attribute groups. Configfs state is represented by `gpio_sim_device`, `gpio_sim_bank`, `gpio_sim_line`, and `gpio_sim_hog`. Important functions include GPIO callbacks, `gpio_sim_apply_pull()`, `gpio_sim_add_bank()`, software-node construction helpers, configfs live activation/deactivation, and configfs item/group operations.

## Control Flow
Module init registers the platform driver and the `gpio-sim` configfs subsystem. Users create configfs device groups, bank groups, optional line groups, and hog items, then write `live=1`. Activation validates that banks exist and labels are unique, creates a root software node, creates bank software nodes with `ngpios`, line names, and reserved ranges, adds hog child nodes, registers a `gpio-sim` platform device, waits for binding, and freezes dependent configfs items. Platform probe iterates child software nodes and creates a chip per bank.

## State and Persistence
Simulated line state is held in bitmaps. `direction_map` defaults to input, `value_map` changes through GPIO set and pull simulation, `pull_map` records pull-up/down, and `request_map` tracks active consumers. Configfs objects persist until removed; live platform devices hold software nodes and gpio chips until deactivated or released. Sysfs per-line `pull` writes can synthesize edge IRQs by setting irqchip pending state when an input value changes.

## Dependencies and Integration Points
The simulator depends on configfs, platform devices, software nodes/property entries, gpiolib provider and consumer semantics, gpio hog parsing, sysfs, `irq_sim`, IDA allocation, and debugfs when enabled.

## Risks
Configfs lifetime is complex: parent pointers are stored explicitly because configfs clears parent fields before release. Activation must unwind software nodes and platform devices correctly on partial failure. Pull changes only synthesize edge interrupts when the line is requested and configured as input. `valid` can be changed while live, but reserved ranges are built only during activation. Duplicate labels are rejected to avoid hogging ambiguity.

## Test Signals
Test configfs creation/removal for devices, banks, lines, and hogs; activation/deactivation; duplicate-label rejection; software-node properties for line names and reserved ranges; sysfs value/pull attributes; pull-triggered rising/falling IRQs; request/free effects; bitmap get/set multiple operations; invalid line counts above 1024; and cleanup on probe or activation failure.
