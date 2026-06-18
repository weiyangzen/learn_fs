
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-f7188x.c

Purpose: supports GPIO banks in several Fintek and Nuvoton Super-I/O chips by probing legacy Super-I/O configuration ports and registering one gpiochip per bank.

Important APIs/types/functions: `struct f7188x_sio` stores Super-I/O address, logical device, and chip type. `struct f7188x_gpio_bank` and `struct f7188x_gpio_data` describe bank layout. Key functions are `superio_enter()`, `f7188x_gpio_get_direction()`, `f7188x_gpio_direction_in()`, `f7188x_gpio_direction_out()`, `f7188x_gpio_get()`, `f7188x_gpio_set()`, `f7188x_gpio_set_config()`, `f7188x_find()`, and `f7188x_gpio_init()`.

Control flow: init probes Super-I/O ports 0x2e and 0x4e, unlocks with the double key, reads device/manufacturer IDs, chooses chip type and bank table, registers the platform driver, and creates a platform device with copied SIO data. Probe selects the static bank array for the chip and registers each bank as a separate can-sleep gpiochip. Each GPIO operation re-enters Super-I/O config mode, selects the GPIO logical device, reads/modifies/writes bank registers, then exits.

State and persistence behavior: static bank tables describe immutable layout. Hardware registers hold direction, data, and output mode. No mutex protects repeated Super-I/O access beyond `request_muxed_region()` inside `superio_enter()`. The platform device pointer is global for module exit.

Dependencies and integration points: depends on legacy I/O port access, Super-I/O IDs, platform device self-registration, gpiolib, and pinconf drive open-drain/push-pull config support.

Risks: static bank arrays are shared objects mutated with parent/data pointers at probe, making multi-instance assumptions weak. Super-I/O config access is slow and can conflict with firmware or other drivers if muxing is inadequate. Device list in module description lags supported Nuvoton/F81865 variants.

Test signals: chip detection at both standard ports, manufacturer validation, bank count/ngpio for each supported ID, direction inversion for NCT6126D, single data-register behavior for NCT6126D, drive mode config, and platform device cleanup.
