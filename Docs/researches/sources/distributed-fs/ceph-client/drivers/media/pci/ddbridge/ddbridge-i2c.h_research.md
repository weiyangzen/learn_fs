# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-i2c.h

Purpose: declares ddbridge I2C lifecycle APIs and provides small helper wrappers for common I2C register operations.

Important APIs/types/functions: `ddb_i2c_init()` and `ddb_i2c_release()` are implemented in `ddbridge-i2c.c`. Inline helpers include `i2c_io`, `i2c_write`, `i2c_read`, `i2c_read_regs`, `i2c_read_regs16`, `i2c_write_reg16`, `i2c_write_reg`, `i2c_read_reg16`, and `i2c_read_reg`.

Control flow: helpers are used heavily during port probing, frontend attachment, LED/SNR/temp sysfs reads, and board-specific initialization. They translate successful `i2c_transfer()` message counts into zero and failures into `-1`.

State and persistence: no state beyond stack `i2c_msg` arrays.

Dependencies/integration: includes Linux I2C and `ddbridge.h`; used by core, MAX, and hardware-probing code.

Risks and test signals: helpers collapse all transfer failures to `-1`, so diagnostics come from callers or adapter logs. Test by compiling all call sites, probing known I2C devices, and checking that 8-bit versus 16-bit register addressing matches each frontend/tuner chip.
