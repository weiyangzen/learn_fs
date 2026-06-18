# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/digitv.h

Purpose: private header for the Nebula uDigiTV driver. It defines the log prefix, device private state, and command bytes for the 7-byte USB control protocol.

Important APIs/types: `struct digitv_state` stores the NXT6000/MT352 frontend choice and reusable `sndbuf`/`rcvbuf`. Command macros include EEPROM read, COFDM read/write, tuner write, remote read/write/type, and device init.

Control flow: `digitv.c` uses the protocol constants in `digitv_ctrl_msg()`, I2C transfer, tuner programming, RC polling, and probe-time remote setup.

State and persistence: private buffers persist for the lifetime of the USB device. The command constants encode device firmware state transitions but do not allocate state themselves.

Dependencies and integration: includes `dvb-usb.h` and is private to the Digitv driver.

Risks: the protocol is documented as reverse-engineered/SDK-derived and only supports up to four payload bytes in the C implementation. Adding new commands requires preserving the fixed seven-byte packet ABI.

Test signals: compile the driver and trace USB control packets for COFDM read/write, remote reads, remote type setup, and NXT6000 tuner writes.
