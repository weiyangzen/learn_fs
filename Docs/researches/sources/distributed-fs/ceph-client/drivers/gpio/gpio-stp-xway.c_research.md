<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-stp-xway.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-stp-xway.c

Purpose: implements the Lantiq XWAY Serial To Parallel controller as a GPIO output provider for external shift-register cascades, with up to three 8-bit groups and optional hardware ownership of selected DSL/PHY bits.

Important APIs, types, and functions: `struct xway_stp` stores the `gpio_chip`, MMIO base, shadow output value, enabled groups, edge mode, and hardware-reserved bit masks. GPIO callbacks are `xway_stp_get()`, `xway_stp_set()`, `xway_stp_dir_out()`, and `xway_stp_request()`. `xway_stp_hw_init()` programs STP registers and `xway_stp_probe()` parses Device Tree properties such as `lantiq,shadow`, `lantiq,groups`, `lantiq,dsl`, `lantiq,phy*`, and `lantiq,rising`.

Control flow: probe maps the register block, configures an output-only dynamic-base chip, reads board properties, enables the clock, initializes the STP hardware, and registers the gpiochip. Set operations update the software shadow and write `XWAY_STP_CPU0`; software update is triggered only when no hardware-driven bits are reserved.

State and persistence behavior: output state is cached in `shadow` and mirrored into MMIO. Hardware-reserved ownership is held in `reserved` for the device lifetime. No suspend/resume or persistent storage is implemented.

Dependencies and integration points: depends on platform Device Tree matching, Lantiq machine compatible checks, clock gating, MMIO access, and gpiolib. It is registered at `subsys_initcall()` for early platform use.

Risks and test signals: request rejects only reserved GPIOs below 8 even though `reserved` can encode higher PHY groups, so board mappings should be reviewed carefully. Group count comes from `fls(groups) * 8`, so sparse group masks expose intermediate GPIOs. Test with DT variants for group count, DSL/PHY reservation, clock failures, rising/falling edge configuration, and writes that update only software-controlled pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-stp-xway.c -->
