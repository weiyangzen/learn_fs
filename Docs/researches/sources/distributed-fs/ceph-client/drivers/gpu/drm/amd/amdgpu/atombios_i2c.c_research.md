# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atombios_i2c.c

Purpose: provides a hardware-assisted I2C adapter implementation that executes AtomBIOS `ProcessI2cChannelTransaction` command-table calls. It lets AMDGPU perform DDC/AUX-adjacent legacy I2C transactions through BIOS-described I2C lines.

Important APIs and functions: `amdgpu_atombios_i2c_xfer()` is the Linux I2C adapter transfer callback. `amdgpu_atombios_i2c_func()` advertises `I2C_FUNC_I2C | I2C_FUNC_SMBUS_EMUL`. `amdgpu_atombios_i2c_channel_trans()` is a direct one-byte channel transaction helper. The internal `amdgpu_atombios_i2c_process_i2c_ch()` serializes a single AtomBIOS transaction and copies read data from Atom scratch space.

Control flow: `xfer()` handles zero-length bus probes as a write transaction, then iterates each `i2c_msg`. It chunks reads to `ATOM_MAX_HW_I2C_READ` and writes to `ATOM_MAX_HW_I2C_WRITE`, calls the internal transaction helper, and returns either the number of messages or the first error. The helper locks the channel mutex, prepares `PROCESS_I2C_CHANNEL_TRANSACTION_PS_ALLOCATION`, encodes register index/write payload for write transactions, sets I2C speed, slave address, byte count, and line number, executes the Atom table, checks BIOS status, copies swapped read bytes from Atom scratch, and unlocks.

State and persistence: there is no persistent file-local state. Runtime state includes the per-channel mutex, `chan->rec.i2c_id`, AtomBIOS scratch buffer contents, and the hardware I2C transaction state. Error status is returned as `-EINVAL` for invalid write lengths/buffers and `-EIO` for BIOS transaction failure.

Dependencies and integration points: depends on Linux I2C adapter/message APIs, DRM/AMDGPU device conversion, AtomBIOS command table indexes, `amdgpu_atom_execute_table`, and `amdgpu_atombios_copy_swap`. It integrates with connector probing and EDID/DDC paths that bind AMDGPU I2C channels to adapters.

Risks: write transactions are limited to three bytes because of the AtomBIOS helper, not necessarily hardware. The direct `amdgpu_atombios_i2c_channel_trans()` does not lock the channel mutex and uses the caller-provided slave address directly rather than left-shifting like the adapter path, so callers must match BIOS expectations. The transaction helper assumes Atom scratch is valid and large enough for the read. Chunking makes long writes multiple independent transactions, which may not match devices requiring combined transfers.

Test signals: EDID reads over DDC, monitor hotplug probing, I2C bus probe behavior, and dmesg absence of `hw_i2c error` or "tried to write too many bytes" messages. Compile should verify AtomBIOS parameter struct compatibility.
