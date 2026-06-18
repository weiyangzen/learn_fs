# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-isch.c

Purpose: implements an SMBus-only platform adapter for Intel SCH chipsets such as AF82US15W/US15L/UL11L. It provides SMBus quick, byte, byte-data, word-data, and block-data transactions through IO port mapped host controller registers.

Important APIs, types, and functions: `struct sch_i2c` embeds an `i2c_adapter` and `smba` IO mapping. `sch_access()` is the `smbus_xfer` implementation. `sch_transaction()` starts the host transaction, polls for busy clear, interprets completion/error bits, and clears completion status. Small helpers wrap 8-bit and 16-bit IO reads/writes.

Control flow: probe maps the IORESOURCE_IO range, fills the adapter metadata, and registers it with devm. For each SMBus access, the driver checks the host busy bit, initializes clock divider defaults if needed, writes address/command/data registers according to transaction size, writes the encoded protocol into `SMBHSTCNT`, calls `sch_transaction()`, and copies readback data from the data/block registers on read transactions.

State and persistence: persistent state is only the adapter and mapped SMBus base. Hardware persists the host clock divider, which the driver initializes lazily from the `backbone_speed` module parameter when the divider is zero. There is no interrupt state, DMA state, or runtime PM.

Dependencies and integration points: integrates as platform driver `isch_smbus`, uses IO port mapping, the I2C SMBus algorithm interface, module parameter `backbone_speed`, and HWMON class scanning.

Risks: status bits are packed into the low nibble of `SMBHSTSTS`; clearing or interpreting them incorrectly can leave the host unusable. Bus collision is reported as a condition that may lock the SMBus until hard reset. Block read length must be validated against `I2C_SMBUS_BLOCK_MAX`. Unsupported SMBus protocol sizes return `-EOPNOTSUPP`.

Test signals: SMBus quick/byte/byte-data/word/block read and write transactions, uninitialized clock divider path, busy host rejection, timeout path from `read_poll_timeout`, no-response and bus-collision status handling, invalid block lengths, and platform probe with IO region conflicts.
