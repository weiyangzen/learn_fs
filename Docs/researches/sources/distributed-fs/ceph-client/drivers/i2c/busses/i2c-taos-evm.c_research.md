# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-taos-evm.c

Purpose: exposes TAOS evaluation modules as I2C adapters over an RS232 serio link. The module firmware accepts ASCII commands for SMBus byte and byte-data transactions and can auto-instantiate a TSL2550 client on matching adapter names.

Important APIs/types/functions: `struct taos_data` stores the I2C adapter, optional instantiated client, serial parser state, cached address, command/response buffer, and buffer position. `taos_smbus_xfer()` translates I2C SMBus operations into ASCII protocol. `taos_interrupt()` is the serio receive parser. `taos_connect()` and `taos_disconnect()` bind/unbind serio devices.

Control flow: connect allocates state, opens the serio port, initializes the adapter, sends reset, waits for the module identification string ending in `:`, extracts the adapter name, turns echo off, registers the I2C adapter, and optionally creates a TSL2550 client. Each SMBus transfer encodes address/command/data into the shared buffer, skips resending the same address, writes the ASCII command to serio, starts read/write with `<` or `>`, waits up to 150 ms for a response ending in `]`, and interprets `ACK`, `NAK`, or `xHH` read data. The interrupt parser has states for reset identification, echo-off acknowledgement, and transaction receive.

State and persistence: adapter lifetime is tied to serio connection. The cached `addr` persists across transactions to reduce serial traffic. Parser state and buffer position are mutable global-per-device transfer state, while the wait queue is file-global.

Dependencies and integration: depends on serio RS232 protocol `SERIO_TAOSEVM`, Linux I2C core, wait queues, and optional sensor client instantiation. It advertises only `I2C_FUNC_SMBUS_BYTE | I2C_FUNC_SMBUS_BYTE_DATA`.

Risks: the global wait queue is shared across all devices, so multi-device scenarios rely on per-device state checks after wakeup. Transfers serialize through adapter locking but the driver itself has no explicit buffer lock. Response parsing assumes exactly five received bytes and fixed TAOS strings. Unsupported SMBus operations return `-EOPNOTSUPP`.

Test signals: serio connect/reset/identification, echo-off timeout, adapter-name parsing, byte and byte-data read/write translation, NAK handling, malformed read hex returning `-EPROTO`, timeout with partial response, auto-instantiation of TSL2550, and disconnect cleanup.
