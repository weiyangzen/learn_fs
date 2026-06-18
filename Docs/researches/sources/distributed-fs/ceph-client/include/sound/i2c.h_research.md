# sources/distributed-fs/ceph-client/include/sound/i2c.h

Source read summary: 88 lines, ALSA legacy software/hardware I2C bus abstraction.

Purpose: provides bus, device, bit-bang, and mid-level operation structures for sound drivers that manage auxiliary I2C devices without using the generic Linux I2C core directly.

Important APIs, types, and functions: `struct snd_i2c_device` tracks list membership, bus, name, flags such as `SND_I2C_DEVICE_ADDRTEN`, address, private value/data/free. `struct snd_i2c_bit_ops` exposes start/stop/direction/setlines/getclock/getdata callbacks. `struct snd_i2c_ops` exposes send/read/probeaddr. `struct snd_i2c_bus` stores card, name, lock, master/slave bus list, devices, low-level ops, mid-level ops, and private data. Creation and transfer APIs are `snd_i2c_bus_create()`, `snd_i2c_device_create()`, `snd_i2c_device_free()`, `snd_i2c_sendbytes()`, `snd_i2c_readbytes()`, and `snd_i2c_probeaddr()`.

Control flow: a sound card creates a bus, optionally slaves it to a master sharing SCL/SCK, attaches devices, locks the master bus for transfers, and invokes send/read/probe through mid-level callbacks.

State and persistence behavior: state is in-memory card-lifetime bus/device lists and private driver data. External I2C device register changes persist only in hardware.

Dependencies and integration points: uses ALSA card structures, Linux list/mutex primitives, and codec/mixer drivers that need board-specific I2C access.

Risks and edge cases: master/slave locking must prevent shared-line contention, 10-bit addresses need correct flags, bit-bang callbacks can sleep or race if misused, and private_free order must match list removal.

Test signals: bus/device creation/free, shared master locking, byte send/read/probe, 7-bit and 10-bit addresses, concurrent transfers, and teardown with attached devices.
