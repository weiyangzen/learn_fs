<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/consumer.h -->
# sources/distributed-fs/ceph-client/include/linux/gpio/consumer.h

Purpose: Defines the descriptor-based GPIO consumer API for drivers that acquire, configure, read, write, and release GPIO lines without using global GPIO numbers.

Important APIs/types/functions: `gpio_descs` represents arrays from `gpiod_get_array()`. `enum gpiod_flags` describes initial direction/value/open-drain requests. Acquisition APIs include plain, indexed, optional, array, devm, and fwnode variants. Release APIs include `gpiod_put()`, array put, and devm put/unhinge. Direction/value APIs include raw and logical get/set, array variants, and cansleep variants. Other helpers cover debounce/config, active-low toggling/query, sleep capability, IRQ mapping, consumer naming, shared descriptor checks, legacy conversion, hardware GPIO number, equality, hardware timestamp enable/disable, ACPI GPIO mapping, sysfs export, and `gpiod_multi_set_value_cansleep()`.

Control flow: Consumers acquire descriptors by device/connection ID or fwnode, optionally setting initial direction. Runtime paths choose non-sleeping or cansleep accessors based on descriptor capability, use logical APIs for active-low aware values or raw APIs for physical levels, then release descriptors manually or via devm.

State and persistence behavior: Descriptor ownership, direction, active-low, debounce, timestamping, and exported sysfs state are maintained by gpiolib/controller drivers. The header defines acquisition and access contracts.

Dependencies and integration points: Depends on errors, bit macros, GPIO defs, device/fwnode/ACPI declarations, gpiolib, ACPI, HTE, and GPIO sysfs configs. It is the primary consumer integration point for device drivers.

Risks: Non-optional getters return error pointers while optional getters return `NULL` for absent GPIOs. Non-sleeping accessors are invalid for `gpiod_cansleep()` descriptors. Raw APIs bypass active-low translation. Disabled `CONFIG_GPIOLIB` stubs often warn and return `-ENOSYS`, `NULL`, or zero, so callers must distinguish absence from infrastructure failure.

Test signals: GPIO mock/controller tests for acquisition forms, optional absent lines, active-low logical versus raw values, array set/get, cansleep misuse detection, debounce/config, IRQ mapping, fwnode and ACPI mappings, HTE timestamp config, sysfs export, and disabled-config compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/consumer.h -->
