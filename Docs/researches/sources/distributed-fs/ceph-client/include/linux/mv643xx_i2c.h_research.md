# sources/distributed-fs/ceph-client/include/linux/mv643xx_i2c.h

Purpose: defines the platform data contract for the Marvell MV64xxx I2C controller driver.

Important APIs and types: `MV64XXX_I2C_CTLR_NAME` names the controller driver, and `struct mv64xxx_i2c_pdata` carries clock divider fields `freq_m`, `freq_n`, and transfer timeout in milliseconds.

Control flow: platform code provides divider and timeout values at device creation; the I2C controller driver converts them into bus timing and timeout behavior during probe and transfers.

State and persistence: no runtime state is owned here. The structure is boot-time configuration for hardware registers and transfer policy.

Dependencies and integration points: depends on fixed-width Linux types and integrates board/platform data with the MV64xxx I2C adapter driver.

Risks and test signals: risks include invalid clock divisors, timeout values that are too short or too long, and mismatched platform-data naming. Test probe with platform data, expected bus frequency, transfer timeout paths, and error recovery on stuck buses.
