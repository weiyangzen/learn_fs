# sources/distributed-fs/ceph-client/drivers/reset/reset-gpio.c

Purpose: generic auxiliary reset provider for reset lines backed by GPIO descriptors.

Important APIs/types/functions: `struct reset_gpio_priv`, `reset_gpio_assert()`, `reset_gpio_deassert()`, `reset_gpio_status()`, `reset_gpio_fwnode_xlate()`, and `reset_gpio_probe()`.

Control flow: the reset core dynamically creates `reset.gpio` auxiliary devices for `reset-gpios` fallbacks. Probe obtains the `reset` GPIO as initially asserted (`GPIOD_OUT_HIGH`), configures reset ops, sets two fwnode cells to match GPIO specifiers, and registers one reset line. Assert sets GPIO value 1; deassert sets 0; status reads GPIO value.

State and persistence: GPIO output level is hardware-visible state; driver state is devm-managed.

Dependencies and integration: auxiliary bus, GPIO consumer API, property/fwnode matching, and reset framework fallback code in `core.c`.

Risks and test signals: polarity depends on GPIO descriptor flags created by the core, and probe starts asserted. Test active-low flags, device links, optional reset-gpio fallback, suspend/resume GPIO retention, and missing GPIO provider deferral.
