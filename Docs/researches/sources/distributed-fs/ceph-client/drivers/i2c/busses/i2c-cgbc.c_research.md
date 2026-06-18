# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-cgbc.c

## Purpose
I2C bus driver for Congatec Board Controller child buses. It tunnels I2C transactions through the parent MFD command interface and exposes separate general-purpose and power-management adapters.

## APIs, Control Flow, and State
`struct cgbc_i2c_data` stores parent `cgbc_device_data`, adapter, active message pointer/count/position, and a small transfer state machine. Frequency helpers encode/decode controller speed registers and size the read polling timeout. `cgbc_i2c_xfer_to_cmd()` builds command packets with START/STOP, read length, last-ACK flag, address, and write payload. `cgbc_i2c_xfer_msg()` checks board-controller status, chunks reads to 31 bytes and writes to 32 bytes, starts new messages when needed, polls read completion, fetches read data through `CGBC_I2C_CMD_DATA`, and advances state. `cgbc_i2c_xfer()` loops until done, error, or one-second inactivity timeout. Probe clones one of two static adapter templates based on platform ID, configures 100 kHz, and registers a numbered adapter.

## Dependencies and Integration
Depends on the Congatec MFD `cgbc_command()` transport, platform child IDs, I2C core, and `read_poll_timeout()`. It advertises I2C plus SMBus emulation except quick command.

## Risks and Test Signals
Risks include command-packet length encoding, START/STOP across chunk and message boundaries, timeout sizing from effective bus frequency, no 10-bit support despite raw I2C function claim, and parent-command failures. Test both bus IDs, read/write lengths at 31/32 and larger, write-then-read transactions, busy status retry, invalid speed fallback, parent MFD error injection, and adapter removal.
