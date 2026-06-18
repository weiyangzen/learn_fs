# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-robotfuzz-osif.c

Purpose: USB-to-I2C bridge driver for the RobotFuzz OSIF adapter. It registers an I2C adapter over USB vendor control messages and exposes I2C plus SMBus emulation.

Important APIs/types/functions: `struct osif_priv` stores the USB device/interface, I2C adapter, and last status byte. USB helpers are `osif_usb_read()` and `osif_usb_write()`, using vendor interface control requests. `osif_xfer()` implements the adapter transfer loop, `osif_func()` advertises functionality, `osif_probe()` sets bit rate and registers the adapter, and `osif_disconnect()` removes it. `osif_quirks` rejects zero-length reads because they would create invalid control messages.

Control flow: probe allocates private state, binds it to the USB interface, fills adapter fields, sends `OSIFI2C_SET_BIT_RATE` with divider 52 for roughly 100 kHz, registers the adapter, and logs firmware version. Every I2C message is translated to `OSIFI2C_READ` or `OSIFI2C_WRITE`, followed unconditionally by `OSIFI2C_STOP` and a status read through `OSIFI2C_STATUS`. A non-ACK address status or short USB transfer returns `-EREMOTEIO`.

State and persistence: there is no persistent bus state beyond adapter registration, the USB device pointer, and `priv->status`. The firmware owns actual bus sequencing and status. The driver sends STOP after each message, so Linux multi-message repeated-start semantics are not preserved.

Dependencies/integration: USB core, I2C core, control endpoint zero, HWMON class scanning, and the OSIF vendor protocol. It uses managed allocation for private state, while adapter lifetime is explicit through `i2c_add_adapter()`/`i2c_del_adapter()`.

Risks: `osif_probe()` does not check the return value from `i2c_add_adapter()`, so registration failure would still report success. Forced STOP after every message can break clients requiring repeated starts. USB control timeout is fixed at 2000 ms. Status interpretation only accepts `STATUS_ADDRESS_ACK`; all other firmware states collapse to `-EREMOTEIO`.

Test signals: plug/unplug lifecycle, adapter registration failure injection, read/write short USB transfers, address NAK status, bit-rate command failure, zero-length read rejection, SMBus emulation that does not require repeated starts, and behavior on USB disconnect during active transfer.
