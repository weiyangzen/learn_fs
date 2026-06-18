# sources/distributed-fs/ceph-client/drivers/gpio/gpio-menz127.c

Purpose: provides GPIO support for MEN Mikroelektronik 16Z127-compatible MCB devices, including 16Z127, Z034, and Z037 variants. It builds on the generic MMIO GPIO helper and adds debounce and open-drain/push-pull pin configuration.

Important APIs/types/functions: `struct men_z127_gpio` wraps `gpio_generic_chip`, the MMIO register base, and the MCB memory resource. `men_z127_debounce()` programs debounce enable/count registers. `men_z127_set_single_ended()` controls open-drain enable. `men_z127_set_config()` accepts `PIN_CONFIG_DRIVE_OPEN_DRAIN`, `PIN_CONFIG_DRIVE_PUSH_PULL`, and `PIN_CONFIG_INPUT_DEBOUNCE`. Probe is `men_z127_probe()`.

Control flow: probe allocates state, requests MCB memory, registers a devm action to release it, maps the memory, chooses access size by MCB id (`sz = 4` for 16Z127 and `sz = 1` for Z034/Z037), initializes a generic chip with data, set, and direction-output registers, installs the set_config callback, then registers the gpiochip. Debounce converts microseconds to 50 us register units, clamps at the hardware max, toggles the debounce enable bit, and writes the per-GPIO count register under the generic chip lock.

State and persistence behavior: GPIO data/direction is managed by `gpio_generic_chip` shadow state and the hardware registers. Debounce and open-drain state live in DBER, per-line debounce count registers, and ODER. No PM save/restore is present; MCB resource lifetime is devm-managed with an explicit release action.

Dependencies and integration points: depends on the MCB bus, `gpio-mmio` generic chip helper, pinconf constants, and the `MCB` namespace import. Device matching is through MCB device IDs, not OF or ACPI.

Risks: debounce rounding uses `fls()`-based heuristics and rejects values outside 50 us to `0xffff * 50 us`; edge cases around zero and upper-bound rounding need coverage. Only model IDs with known register width are accepted. There is no IRQ support even though interrupt registers exist in the block definition. PM loss would drop debounce/open-drain configuration.

Test signals: register-width selection by ID, GPIO get/set/direction through the generic helper, debounce enable/disable and count rounding, open-drain versus push-pull ODER writes, error returns for out-of-range debounce and unsupported pinconf parameters, and MCB memory cleanup on probe failure.
