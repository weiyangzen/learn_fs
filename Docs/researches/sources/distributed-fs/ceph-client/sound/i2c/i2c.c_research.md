## sources/distributed-fs/ceph-client/sound/i2c/i2c.c

Purpose: provides ALSA's legacy generic I2C abstraction and a default bit-banged implementation for sound-card helper chips.

Important APIs, types, and functions: `snd_i2c_bus_create()`, `snd_i2c_device_create()`, `snd_i2c_device_free()`, `snd_i2c_sendbytes()`, `snd_i2c_readbytes()`, `snd_i2c_probeaddr()`, `snd_i2c_bit_ops`, and the bit helpers for start, stop, send byte, read byte, and ACK.

Control flow: bus creation registers a `SNDRV_DEV_BUS` with the ALSA card and links optional slave buses under a master. Device creation links an addressable device under a bus. Send/read/probe dispatch through bus ops, defaulting to bit operations that toggle caller-provided line callbacks, send 7-bit address plus direction, and stop on completion or error.

State and persistence: bus state includes card, name, device list, slave bus list, master pointer, mutex, ops, hardware callbacks, and private free hook. Device state includes address, name, list linkage, bus pointer, flags, private data, and private free hook.

Dependencies and integration points: used by CS8427, TEA6330T, PT2258, and card-specific low-level line callbacks. It is separate from Linux's I2C core.

Risks: 10-bit addressing is unimplemented. Error paths sometimes call hardware stop instead of full bit stop after address/data failure. Correct behavior depends entirely on board-specific `setlines/getdata/direction` timing and locking by callers.

Test signals: probe valid/invalid addresses, exercise send/read with ACK/NACK, create/free buses with slave buses and devices, lockdep around `snd_i2c_lock()`, and board-level signal traces for start/stop timing.
