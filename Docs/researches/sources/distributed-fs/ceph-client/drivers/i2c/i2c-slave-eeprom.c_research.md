# sources/distributed-fs/ceph-client/drivers/i2c/i2c-slave-eeprom.c

Purpose: I2C slave-mode EEPROM simulator for testing controllers and peer masters. It emulates several 24xx EEPROM sizes and read-only variants, exposes the backing memory through a sysfs binary attribute, and can initialize from firmware.

Important APIs/types: `struct eeprom_data` stores the binary attribute, spinlock, current buffer index, address mask, address-byte count, read-only flag, and flexible backing buffer. The driver binds IDs such as `slave-24c02`, `slave-24c32`, `slave-24c64`, and `slave-24c512` with RO variants.

Control flow: probe decodes size and addressing flags from `driver_data`, allocates backing storage, optionally loads `firmware-name` into the buffer or fills `0xff`, creates `slave-eeprom`, then registers `i2c_slave_eeprom_slave_cb()`. Write events first collect one or two address bytes, then write data when not read-only. Read-request events return the current byte; read-processed increments after the previous byte was accepted. STOP and write-request reset address-byte collection.

State and persistence: EEPROM contents persist in kernel memory for the client lifetime and can be read/written through sysfs. No data survives driver unload or device removal unless reloaded from firmware.

Dependencies and integration: depends on I2C slave core, firmware loader, sysfs binary attributes, bitfield helpers, and spinlocks.

Risks: behavior for incomplete 16-bit addresses is explicitly uncertain. Address wrapping relies on power-of-two sizes. Sysfs writes bypass EEPROM write-protect timing semantics. Callback and sysfs access share a spinlock, but index counters are not themselves locked.

Test signals: slave event sequences, RO write suppression, sysfs binary read/write, firmware preloading, address wraparound, 8-bit vs 16-bit address modes, and unregister cleanup.
