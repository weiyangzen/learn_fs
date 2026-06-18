# sources/distributed-fs/ceph-client/drivers/gpio/gpio-spacemit-k1.c

## Purpose
This driver supports SpacemiT K1/K3 GPIO controllers with four 32-line banks. It uses generic GPIO MMIO helpers for data/direction and custom nested IRQ handling for edge-detect interrupts.

## Important APIs, Types, and Functions
`struct spacemit_gpio_data` describes per-SoC register offsets and bank offsets. `struct spacemit_gpio_bank` contains a generic GPIO chip, parent controller pointer, bank base, and software IRQ masks for enabled/rising/falling edges. `spacemit_gpio_add_bank()` initializes one bank. IRQ callbacks include handler, ack, mask/unmask, set_type, and print_chip.

## Control Flow
Probe selects match data, maps the shared register resource, gets the shared parent IRQ, enables core and bus clocks, and registers four banks. Each bank initializes a `gpio_generic_chip` with data/set/clear/direction registers, configures a threaded simple IRQ chip, resets interrupt mask and edge-detect registers, requests the shared threaded parent IRQ, registers the gpio chip, and marks the IRQ domain as wired for three-cell selection.

## State and Persistence
GPIO values/directions live in hardware. IRQ enable and selected edge types are shadowed in `irq_mask`, `irq_rising_edge`, and `irq_falling_edge`; mask/unmask materializes those shadows into GAPMASK and edge set/clear registers. There are no PM callbacks.

## Dependencies and Integration Points
The driver uses platform DT compatibles, two clocks named `core` and `bus`, one shared IRQ, gpiolib generic helpers, GPIO OF three-cell matching through `of_node_instance_match`, nested threaded IRQ handling, and seq_file chip printing.

## Risks
All four banks request the same shared IRQ and clear per-bank status; incorrect bank offsets would cause cross-bank interference. `irq_set_type()` accepts any type bits and only considers rising/falling, so level types effectively disable both edge masks without returning `-EINVAL`. The K1 bank offsets are nonuniform, making table correctness critical.

## Test Signals
Test K1 and K3 offset tables, four-bank registration, shared IRQ dispatch to the correct bank/domain, rising/falling/both edge enable and mask interactions, invalid or level trigger behavior, three-cell OF GPIO selection, clock failure paths, and boundary lines around each 32-line bank.
