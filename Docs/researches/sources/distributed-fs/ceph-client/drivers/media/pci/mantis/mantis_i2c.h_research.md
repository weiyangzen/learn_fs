# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_i2c.h

- Purpose: Public declarations and simple flags for the Mantis I2C adapter.
- Important APIs/types/functions: `I2C_STOP`, `I2C_READ`, `mantis_i2c_init`, and `mantis_i2c_exit`.
- Control flow: Probe calls init before EEPROM/frontend access; remove calls exit after DVB teardown.
- State and persistence: No direct state; lifecycle functions operate on the I2C fields in `struct mantis_pci`.
- Dependencies and integration points: Depends on Linux I2C core through implementation files.
- Risks: Unused flag definitions can diverge from hardware register names in `mantis_reg.h`; lifecycle ordering remains the main concern.
- Test signals: Compile and board frontend attach tests.
