# sources/distributed-fs/ceph-client/drivers/iio/chemical/scd30_i2c.c

Purpose: I2C transport wrapper for the SCD30 core. It translates the abstract `enum scd30_cmd` command callback used by `scd30_core.c` into Sensirion I2C command words, argument framing, CRC8 protection, and separate send/receive transactions.

Important APIs, types, and functions: `scd30_i2c_cmd_lookup_tbl[]` maps core command ids to sensor command words. `scd30_i2c_xfer()` sends the command frame with `i2c_master_send()` and, when a response is expected, receives data with `i2c_master_recv()` because the device does not support repeated start. `scd30_i2c_command()` builds write frames with a big-endian argument and CRC byte, strips arguments for no-argument stop/reset commands, expands expected read length by one CRC byte per 16-bit word, validates received CRCs, and copies only payload bytes into the core response buffer. `scd30_i2c_probe()` checks `I2C_FUNC_I2C`, populates the CRC table, and calls `scd30_probe()`.

Control flow: probe is thin and delegates all IIO registration and power sequencing to the core. Runtime operations always enter via `state->command`; write commands send command plus optional argument, and read commands send command then receive response. Any short transfer or CRC mismatch returns `-EIO`.

State and persistence: this file keeps no per-device private state. The global CRC table is populated at probe. The I2C client, IRQ, name, and device are passed through to the core state.

Dependencies and integration: depends on Linux I2C, CRC8 helpers, unaligned big-endian accessors, and `scd30.h`. The OF compatible is `sensirion,scd30`; the PM ops come from the exported SCD30 core. It imports namespace `IIO_SCD30`.

Risks and test signals: the buffer maximum assumes current response sizes, so new commands need size review. CRC handling must match Sensirion polynomial 0x31 and initial value. Tests should exercise no-argument commands, write argument CRC construction, read payload deinterleaving, short send/recv failures, CRC mismatch, adapter functionality rejection, and operation with an IRQ supplied by firmware.
