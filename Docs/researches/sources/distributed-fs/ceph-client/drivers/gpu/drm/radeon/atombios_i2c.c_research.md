# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/atombios_i2c.c

## Purpose
This file implements a Radeon I2C adapter backend that routes I2C transfers through the AtomBIOS `ProcessI2cChannelTransaction` command table. It provides hardware-assisted I2C for display DDC and related AtomBIOS-controlled buses.

## Important APIs, Types, and Functions
The exported adapter callbacks are `radeon_atom_hw_i2c_xfer` and `radeon_atom_hw_i2c_func`, declared in `atom.h` and installed in `radeon_i2c.c`. The key internal helper is `radeon_process_i2c_ch`, which builds `PROCESS_I2C_CHANNEL_TRANSACTION_PS_ALLOCATION`, locks the I2C channel and AtomBIOS scratch buffer, executes the AtomBIOS command, and copies read data back to the caller.

The file defines `TARGET_HW_I2C_CLOCK` as 50 kHz and enforces AtomBIOS command limits of three bytes per write transaction and 255 bytes per read transaction.

## Control Flow
`radeon_atom_hw_i2c_xfer` first detects the Linux I2C bus-probe pattern of a single zero-length message and turns it into a zero-byte hardware write transaction. For normal transfers it walks each `i2c_msg`, chooses read or write flags, selects the maximum chunk size based on AtomBIOS limits, and loops until the message length is consumed. Each chunk calls `radeon_process_i2c_ch`; any error aborts the whole transfer and a fully successful batch returns the original message count.

For writes, `radeon_process_i2c_ch` treats `buf[0]` as the register index, reduces the transaction byte count by one, copies up to the remaining two bytes into a little-endian 16-bit output field, and rejects attempts above the three-byte AtomBIOS write limit. For reads, it sets register index and output pointer to zero, lets AtomBIOS write read data into its scratch area, then uses `radeon_atom_copy_swap` to copy from scratch to the caller buffer. It shifts the 7-bit slave address left one bit for the AtomBIOS table and uses the channel record's I2C line number.

## State and Persistence Behavior
No long-lived software state is owned here. The code temporarily mutates the shared AtomBIOS scratch buffer and serializes it with `rdev->mode_info.atom_context->scratch_mutex`; it also serializes the I2C channel with `chan->mutex`. Hardware-visible effects are the I2C transactions performed by firmware on the selected I2C line. `radeon_atom_hw_i2c_func` advertises `I2C_FUNC_I2C | I2C_FUNC_SMBUS_EMUL` capability to the I2C core.

## Dependencies and Integration Points
This file depends on Linux I2C adapter/message types, Radeon I2C channel records, the DRM device's `dev_private` Radeon device, AtomBIOS command execution through `atom_execute_table_scratch_unlocked`, AtomBIOS scratch memory, and `radeon_atom_copy_swap` from `atombios_dp.c` for endian-safe data movement. It is integrated by the Radeon I2C layer as the master transfer implementation for AtomBIOS hardware I2C channels used by connector probing and DDC reads.

## Risks
The AtomBIOS write format supports only a register byte plus up to two payload bytes, so callers expecting arbitrary I2C block writes will fail with `-EINVAL`. Read and write chunking changes large Linux I2C messages into multiple firmware transactions, which may not be equivalent for devices requiring repeated-start semantics across a longer write. Error reporting is coarse: any non-success firmware status becomes `-EIO`. The helper assumes the channel record line number and scratch buffer are valid and depends on lock ordering matching other AtomBIOS users. Big-endian correctness depends on the shared `radeon_atom_copy_swap` behavior.

## Test Signals
Useful tests include DDC EDID reads over AtomBIOS hardware I2C, zero-length bus probes, multi-message register-read sequences, reads larger than 255 bytes split into chunks, write rejection above three bytes, concurrent DDC/AUX activity across multiple connectors, and logs showing `hw_i2c error` or oversized write attempts. Build coverage should also ensure the callbacks match the signatures in `atom.h` and the adapter setup in `radeon_i2c.c`.
