# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dibusb.h

Purpose: common protocol and state header for DiBUSB receivers. It documents firmware request bytes, IOCTL command values, private state structs, exported helper prototypes, and the default RC polling interval.

Important APIs/types: request macros cover I2C read/write, remote polling, streaming mode, interrupt read, and power/stream IOCTLs. `struct dibusb_state` stores `struct dib_fe_xfer_ops`, MT2060 presence, and tuner address. `struct dibusb_device_state` holds legacy RC repeat bookkeeping. Externs expose I2C algorithm, MC attach helpers, stream/PID/power helpers, keymap, RC query, and EEPROM read.

Control flow: `dibusb-common.c`, `dibusb-mb.c`, and `dibusb-mc*.c` include this header so property tables and attach callbacks agree on firmware protocol bytes and private-state layout.

State and persistence: no state is allocated here, but the structures define adapter/device private memory persisted for a bound USB device.

Dependencies and integration: includes `dvb-usb.h`, DiB3000/DiB3000MC demod headers, and MT2060 tuner interfaces.

Risks: the header duplicates `MAX_XFER_SIZE` with the common C file. Protocol comments are the source of truth for firmware packet shapes, so drift between comments, macros, and firmware behavior is a maintenance risk.

Test signals: compile all DiBUSB modules, validate I2C and IOCTL request bytes with USB tracing, and exercise both MB and MC property paths using the shared prototypes.
