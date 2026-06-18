<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tangier.h -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-tangier.h

Purpose: declares the private/public contract for Intel Tangier-family GPIO platform wrappers that reuse `gpio-tangier.c`.

Important APIs, types, and functions: defines wake register constants for Elkhart Lake and Merrifield, `struct tng_wake_regs`, `struct tng_gpio_pinrange`, `GPIO_PINRANGE()`, `struct tng_gpio_pin_info`, `struct tng_gpio_info`, and the main `struct tng_gpio`. It declares `devm_tng_gpio_probe()` and `tng_gpio_pm_ops`.

Control flow: no runtime flow is implemented in the header. Platform drivers allocate or embed `struct tng_gpio`, fill MMIO base, IRQ, wake registers, pin information, and GPIO/IRQ numbering, then hand it to the core probe helper.

State and persistence behavior: describes the state owned by the core: gpiochip, MMIO base, raw spinlock, device pointer, suspend context pointer, wake register layout, pinctrl range data, and GPIO count/base metadata. Persistence is runtime-only except for PM snapshots allocated by the C file.

Dependencies and integration points: includes gpiolib, PM, spinlock types, and Linux integer types. The export declaration lets architecture/platform-specific modules reuse the shared implementation without duplicating GPIO logic.

Risks and test signals: the ABI between wrapper and core is structural, so incorrect `ngpio`, `first`, wake offsets, or pin ranges will create hard-to-debug line or IRQ mismatches. Test by building all wrappers that include this header, verifying exported namespace use, and validating that pin range and wake register constants match the target SoC data sheet.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tangier.h -->
