<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/gpio.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/gpio.c

Purpose: implements a gpiolib driver for PPC4xx GPIO controllers with 32 GPIOs per controller, supporting input/output direction, value get/set, and OF platform binding.

Important APIs/types/functions: `struct ppc4xx_gpio` models the big-endian register block; `struct ppc4xx_gpio_chip` wraps `gpio_chip`, MMIO base, and spinlock; `ppc4xx_gpio_get()`, `ppc4xx_gpio_set()`, `ppc4xx_gpio_dir_in()`, and `ppc4xx_gpio_dir_out()` implement gpiolib operations; `ppc4xx_gpio_probe()` maps registers and registers the chip; `ppc4xx_gpio_driver` matches `ibm,ppc4xx-gpio`.

Control flow: arch init registers the platform driver. Probe allocates device-managed chip state, sets dynamic GPIO base and 32 lines, labels from the OF node, maps the first register resource, and calls `devm_gpiochip_add_data()`. Direction functions lock, disable open drain, set or clear TCR, and clear alternate-source/three-state mux bits in low or high source registers.

State and persistence: per-controller driver state is devm-managed; hardware output, direction, open-drain, and mux registers persist until changed. The spinlock serializes read-modify-write register updates.

Dependencies and integration: depends on OF platform bus creation by board files, big-endian MMIO helpers, gpiolib, and consumers such as LEDs or board fixups.

Risks and test signals: GPIO numbering uses MSB-first masks; mux clearing can override alternate functions when requesting GPIO mode; no IRQ support is implemented. Test GPIO input/output via libgpiod/sysfs consumers, concurrent set/direction changes, high GPIO numbers 16-31, and board consumers such as Warp LEDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/gpio.c -->
