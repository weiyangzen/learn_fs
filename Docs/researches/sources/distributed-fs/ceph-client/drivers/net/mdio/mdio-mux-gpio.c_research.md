<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-gpio.c

Purpose: generic GPIO-controlled MDIO mux driver that selects child buses by driving a GPIO array.

Important APIs/types/functions: `struct mdio_mux_gpio_state` stores GPIO descriptors and mux handle. Core functions are `mdio_mux_gpio_switch_fn`, probe, and remove.

Control flow: probe obtains a GPIO descriptor array as outputs, allocates state, and calls `mdio_mux_init` with no explicit parent bus, so the core locates `mdio-parent-bus`. The switch function compares current/desired child values, places `desired_child` into a bitmap, and calls `gpiod_multi_set_value_cansleep`.

State and persistence: runtime state is GPIO output levels, mux handle, and mdio-mux child bus state. No persistent storage exists.

Dependencies/integration: depends on OF_GPIO, OF MDIO, mdio-mux core, GPIO consumer API, and platform bus. Supports `mdio-mux-gpio` and legacy `cavium,mdio-mux-sn74cbtlv3253`.

Risks and test signals: risks include child values wider than available GPIOs, bitmap sizing by `desired_child` type, sleeping GPIO operations under MDIO mux lock, and missing parent bus defer. Tests should cover multi-bit selections, repeated same-child no-op, missing GPIOs, and parent bus deferral.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-gpio.c -->
