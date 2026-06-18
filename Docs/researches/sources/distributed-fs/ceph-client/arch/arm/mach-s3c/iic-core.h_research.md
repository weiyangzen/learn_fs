# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/iic-core.h

Purpose: Samsung I2C GPIO configuration declarations.

Important APIs/types/functions: declares I2C pin configuration helpers such as `s3c_i2c0_cfg_gpio()` and variant helpers for additional controllers.

Control flow: no local flow; I2C platform-data setters install these callbacks when board data lacks one.

State and persistence: callbacks mutate GPIO pinmux when I2C controllers probe.

Dependencies and integration points: used by `devs.c`, I2C setup files, and `s3c2410-i2c` platform data.

Risks: missing callback leaves I2C pins unconfigured on legacy boards.

Test signals: I2C bus probe and pinmux for bus 0/1 on S3C64xx boards.
