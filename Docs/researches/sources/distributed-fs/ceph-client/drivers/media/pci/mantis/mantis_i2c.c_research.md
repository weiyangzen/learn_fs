# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_i2c.c

- Purpose: Linux I2C adapter implementation for the Mantis bridge, supporting page-mode byte transfers and a combined byte-mode register read path.
- Important APIs/types/functions: `mantis_i2c_xfer()`, `mantis_i2c_read()`, `mantis_i2c_write()`, `mantis_i2c_func()`, `mantis_i2c_init()`, and `mantis_i2c_exit()`.
- Control flow: Transfers are serialized by `i2c_lock`. Byte-mode recognizes a one-byte write followed by one-byte read and performs a compact hardware transaction. Other reads/writes loop per byte, program `MANTIS_I2CDATA_CTL`, and poll interrupt status bits for done/ack. Init registers an adapter and masks I2C done IRQ; exit unregisters it.
- State and persistence: Stores adapter, return code, wait queue, and mutex in `struct mantis_pci`; no persistent state. Poll loops are bounded by `TRIALS`.
- Dependencies and integration points: Used by EEPROM reads, frontend/tuner attach and configuration, and board-specific tuner functions; depends on Mantis MMIO register definitions and Linux I2C core.
- Risks: Polling loops may spin hard and do not consistently fail if ack polling exhausts in helper paths. Functionality advertises SMBus emulation although hardware behavior is custom. I2C done IRQ is masked, so wait queue path is effectively unused here.
- Test signals: Test all frontend attach paths, EEPROM read, tuner parameter writes, NACK/timeouts, and mixed combined-message sequences.
