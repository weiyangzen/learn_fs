# sources/distributed-fs/ceph-client/drivers/gpio/gpio-merrifield.c

Purpose: binds Intel Merrifield SoC GPIO hardware as a PCI device and delegates the actual GPIO/IRQ implementation to the shared Tangier GPIO core.

Important APIs/types/functions: `MRFLD_NGPIO` defines 192 lines. `mrfld_gpio_ranges[]` maps GPIO offsets to pinctrl pin numbers. `mrfld_gpio_get_pinctrl_dev_name()` locates ACPI device `INTC1002` and returns its name, falling back to `"pinctrl-merrifield"`. `mrfld_gpio_probe()` sets up `struct tng_gpio` and calls `devm_tng_gpio_probe()`.

Control flow: probe enables the PCI device, maps BAR1 to read the firmware-provided IRQ base and GPIO base, unmaps BAR1, allocates `struct tng_gpio`, maps BAR0 for controller registers, fills pin range metadata and base/ngpio/first IRQ info, allocates one PCI IRQ vector, stores wake-register offsets for Merrifield, then calls the Tangier common probe. The PCI driver matches Intel device ID `0x1199`.

State and persistence behavior: this file owns no line state directly; state is held by the Tangier GPIO core and hardware registers. PCI mappings and IRQ vectors are managed by pcim/devm helpers. Pin-range metadata is static and persistent for the device lifetime.

Dependencies and integration points: depends on PCI, ACPI, `gpio-tangier.h`, the `GPIO_TANGIER` namespace, and the Merrifield pinctrl device. It uses ACPI lookup to avoid hard-coding the pinctrl device instance name when firmware exposes one.

Risks: failure to find or duplicate the ACPI pinctrl name falls back to a string, which may not match all firmware. BAR1 is read only for two base values; incorrect BAR layout breaks IRQ/GPIO numbering. Most behavior and risks are in the shared Tangier core, so this wrapper must keep the Merrifield-specific pin range table and wake offsets accurate.

Test signals: PCI probe with valid BAR0/BAR1, correct extraction of `irq_base` and `gpio_base`, successful IRQ vector allocation, pinctrl range registration via the Tangier core, wake-register offset use, and ACPI lookup/fallback behavior for the pinctrl device name.
