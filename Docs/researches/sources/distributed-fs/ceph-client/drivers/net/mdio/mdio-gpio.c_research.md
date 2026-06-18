<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-gpio.c

Purpose: generic GPIO-backed MDIO bus driver built on the bitbang MDIO library.

Important APIs/types/functions: `struct mdio_gpio_info` embeds `mdiobb_ctrl` and GPIO descriptors for MDC, MDIO, and optional separate MDO. GPIO-backed `mdiobb_ops` callbacks are `mdio_dir`, `mdio_get`, `mdio_set`, and `mdc_set`. Lifecycle is in `mdio_gpio_probe/remove`.

Control flow: probe allocates state, requests GPIOs by index, derives bus ID from OF alias or platform ID, calls `alloc_mdio_bitbang`, assigns name/parent/id, optionally overrides opcodes for `microchip,mdio-smi0`, and registers the bus with OF MDIO. Remove unregisters and frees the bitbang bus.

State and persistence: runtime state consists of GPIO descriptors, mii_bus, and bitbang control. GPIO values and direction change during transactions; no persistent storage exists.

Dependencies/integration: depends on GPIOLIB, MDIO_BITBANG, OF MDIO, platform bus, and phylib. Compatible strings are `virtual,mdio-gpio` and `microchip,mdio-smi0`.

Risks and test signals: risks include sleeping GPIO access under timing-sensitive bitbang paths, optional MDO semantics, alias collisions, and opcode override regressions. Tests should cover two-wire and three-wire GPIO layouts, OF registration, Microchip SMI0 opcodes, and removal cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-gpio.c -->
