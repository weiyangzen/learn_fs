<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/generic.h -->
# sources/distributed-fs/ceph-client/include/linux/gpio/generic.h

Purpose: This header defines the generic MMIO GPIO chip model used by simple register-backed GPIO controllers. It factors common register layout, endian, direction, set/clear, and shadow-state handling behind `struct gpio_generic_chip`.

Important APIs/types/functions: Flags such as `GPIO_GENERIC_BIG_ENDIAN`, `GPIO_GENERIC_UNREADABLE_REG_SET`, `GPIO_GENERIC_UNREADABLE_REG_DIR`, `GPIO_GENERIC_READ_OUTPUT_REG_SET`, `GPIO_GENERIC_NO_OUTPUT`, `GPIO_GENERIC_PINCTRL_BACKEND`, and `GPIO_GENERIC_NO_INPUT` parameterize hardware behavior. `struct gpio_generic_chip_config` supplies parent device, register size, data/set/clear/direction registers, and flags. `struct gpio_generic_chip` embeds `struct gpio_chip`, read/write callbacks, register pointers, bit order, direction/readability markers, bit count, a raw spinlock, and shadow registers `sdata` and `sdir`.

Control flow, state, and persistence: `gpio_generic_chip_init()` maps the config into a ready `gpio_chip` callback table. Runtime get/set/direction paths use `read_reg`/`write_reg`, shadow data for unreadable or read-modify-write registers, and raw spinlocks to keep hardware writes and shadow state synchronized. Inline wrappers protect against missing function pointers and return `-EOPNOTSUPP` or no-op on invalid setup.

Dependencies/integration: It builds on `gpio/driver.h`, MMIO `__iomem`, raw spinlocks, and optional pinctrl backend direction calls. It is the interface for drivers that otherwise would reimplement basic GPIO register operations.

Risks and test signals: Misdeclared register readability or endian/bit order corrupts line values. Locking matters because shadow registers and hardware writes must stay atomic relative to IRQ and concurrent GPIO users. Tests should cover set/clear layouts, single-register clear-by-zero layouts, unreadable direction/data registers, big-endian bit numbering, no-input/no-output constraints, and lockdep/atomic context use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/generic.h -->
