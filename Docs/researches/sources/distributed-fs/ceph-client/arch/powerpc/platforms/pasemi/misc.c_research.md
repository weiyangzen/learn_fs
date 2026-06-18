# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/misc.c

Purpose: PA Semi miscellaneous device registration, currently I2C board-info population from PCI I2C controller child nodes.

Important APIs and control flow: under `CONFIG_I2C_BOARDINFO`, `find_i2c_driver` maps OF compatible `dallas,ds1338` to I2C type `ds1338`. `pasemi_register_i2c_devices` iterates PA Semi I2C PCI functions (`0xa003`), walks child OF nodes, validates 10-bit addresses from `reg`, maps optional IRQs, fills `i2c_board_info`, and registers it for the PCI function number.

State, dependencies, and risks: state is registered I2C board info. Dependencies include PCI device discovery, OF child nodes, I2C board-info support, and IRQ mapping. Risks include limited compatible table, leaked PCI references in iteration edge cases, address validation only by raw `reg`, and silent skip for unknown devices. Test signals are DS1338 RTC client creation, correct adapter numbering by PCI function, and warnings for invalid I2C child entries.
