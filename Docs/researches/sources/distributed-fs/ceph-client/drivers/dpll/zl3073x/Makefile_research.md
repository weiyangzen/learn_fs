# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/Makefile

## Purpose
This Makefile maps ZL3073x Kconfig symbols to kernel objects.

## Important build rules
`obj-$(CONFIG_ZL3073X)` builds `zl3073x.o` from `chan.o core.o devlink.o dpll.o flash.o fw.o out.o prop.o ref.o synth.o`. `CONFIG_ZL3073X_I2C` builds `zl3073x_i2c.o` from `i2c.o`; `CONFIG_ZL3073X_SPI` builds `zl3073x_spi.o` from `spi.o`.

## Integration, risks, and tests
The split keeps transport modules small while sharing the exported `ZL3073X` namespace from the common core. Risks are missing objects when new helpers are added or namespace/export mismatches between transport and core. Test signals are clean module builds and successful modpost namespace checks.
