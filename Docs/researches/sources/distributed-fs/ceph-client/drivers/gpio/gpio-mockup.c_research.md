# sources/distributed-fs/ceph-client/drivers/gpio/gpio-mockup.c

Purpose: provides a synthetic GPIO controller for testing GPIO consumers, libgpiod behavior, line naming, pull simulation, and IRQ/event handling without real hardware.

Important APIs/types/functions: `struct gpio_mockup_line_status` stores direction, value, pull, and requested state. `struct gpio_mockup_chip` stores the gpiochip, line array, irq simulation domain, debugfs directory, and mutex. Module parameters `gpio_mockup_ranges` and `gpio_mockup_named_lines` define synthetic chips. GPIO callbacks include get/set, get_multiple/set_multiple, direction, get_direction, set_config, to_irq, request, and free. Debugfs callbacks expose per-line read/write. Init helpers register software-node-backed platform devices.

Control flow: module init validates range pairs, creates `/sys/kernel/debug/gpio-mockup`, registers a platform driver, then registers one platform device per range with software-node properties for chip label, optional base, `nr-gpios`, and optional line names. Probe reads those properties, initializes all lines as input, creates an irq simulation domain, registers cleanup actions, adds the gpiochip, and creates debugfs line files. Debugfs writes change the simulated pull; if a requested input line changes and its IRQ mapping/type matches the edge, the code sets the simulated IRQ pending state.

State and persistence behavior: all state is memory-resident and protected by `chip->lock`. Line value differs from pull while a line is requested as output; freeing a line restores value to the pull. IRQ mappings are created lazily in `to_irq()` and disposed by a devm action. No state persists across module unload.

Dependencies and integration points: depends on platform devices, software nodes, debugfs, irq_sim, gpiolib, pinconf bias constants, and module parameters. It is directly useful for GPIO selftests and userspace ABI testing because it can synthesize chips and line events.

Risks: `gpio_mockup_range_ngpio()` is interpreted as an end value when base is nonnegative and as a count when base is negative, which is easy to misuse. Debugfs setup depends on finding a child GPIO device after registration. IRQ event delivery only models edge changes caused by pull writes on requested input lines; it is not a full electrical simulator. The per-line debugfs file changes pull, not necessarily currently driven output value.

Test signals: module parameter validation, generated chip count/base/ngpio, optional line names, get/set_multiple, output value versus pull restoration on free, pinconf pull-up/pull-down, debugfs read/write, irq_sim pending events for rising/falling/both edges, and teardown of platform devices, fwnodes, debugfs, and IRQ mappings.
