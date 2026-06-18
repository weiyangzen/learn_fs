## sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/Makefile

Purpose: object composition rules for ICM-426xx common and bus-specific modules.

Important APIs, types, and functions: `inv-icm42600.o` includes core, gyro, accel, temp, and buffer objects. I2C and SPI modules are separate wrapper modules built from `inv_icm42600_i2c.o` and `inv_icm42600_spi.o`.

Control flow: Kconfig symbols determine which composite objects are linked. The requested subset includes common header/core/accel/buffer, while the Makefile shows additional gyro/temp/bus files complete the full driver.

State and persistence behavior: no runtime state; build composition only.

Dependencies and integration points: ensures accel and buffer code can call gyro/temp symbols in the same common module and bus wrappers can import the common namespace.

Risks and edge cases: omitting gyro or temp objects would leave unresolved symbols used by buffer and accel. Module names use hyphenated object names while source files use underscores.

Test signals: full module link with all common objects, I2C/SPI wrapper link, and modpost namespace import checks.
