<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/st33zp24/Makefile -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/st33zp24/Makefile

## Purpose
Maps ST33ZP24 Kconfig symbols to the common TPM 1.2 core and I2C/SPI transport module objects.

## Important APIs, Types, And Functions
Build variables are `tpm_st33zp24-objs = st33zp24.o`, `tpm_st33zp24_i2c-objs = i2c.o`, and `tpm_st33zp24_spi-objs = spi.o`, with `obj-$(CONFIG_TCG_TIS_ST33ZP24*)` selecting each module.

## Control Flow
Kbuild compiles the shared core when the hidden core symbol is selected and compiles each physical-layer wrapper when the corresponding transport option is enabled.

## State And Persistence
There is no runtime state. The persistent build effect is module composition and module naming.

## Dependencies And Integration Points
Coupled to `st33zp24/Kconfig` and to exported symbols from `st33zp24.c` consumed by `i2c.c` and `spi.c`.

## Risks And Edge Cases
If the common core module is not selected with a bus wrapper, bus probe code will fail to link. Module names must stay consistent with Kconfig help text and udev/modprobe expectations.

## Test Signals
Build module and built-in variants for `TCG_TIS_ST33ZP24_I2C` and `TCG_TIS_ST33ZP24_SPI`, and verify symbol exports resolve between core and transport objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/st33zp24/Makefile -->
