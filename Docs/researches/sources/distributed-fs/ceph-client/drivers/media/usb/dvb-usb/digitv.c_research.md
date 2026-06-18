# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/digitv.c

Purpose: DVB USB driver for Nebula Electronics uDigiTV DVB-T USB2.0. It implements a device-specific 7-byte bulk control protocol, an I2C adapter for the COFDM demodulator, frontend/tuner attach, remote-control polling, and USB driver registration.

Important APIs/functions: `digitv_ctrl_msg()` is the central protocol helper. `digitv_i2c_algo` implements `digitv_i2c_xfer()`/`digitv_i2c_func()`. Frontend paths include `digitv_mt352_demod_init()`, `digitv_frontend_attach()`, `digitv_tuner_attach()`, and `digitv_nxt6000_tuner_set_params()`. `digitv_rc_query()` decodes the local RC table. `digitv_probe()` performs post-init remote setup.

Control flow: probe calls `dvb_usb_device_init()` with FX2 firmware `dvb-usb-digitv-02.fw`; on success it sets remote type and clears remote state. I2C transfers are serialized, support write and write-then-read transactions, and translate them to COFDM read/write commands. Frontend attach tries MT352 first, then NXT6000, recording `is_nxt6000`; tuner attach installs a TDED4 PLL and, for NXT6000, replaces tuner `set_params` with a USB tuner-write command. RC polling reads four bytes, acknowledges/clears the device buffer, and maps RC5 custom/data to keycodes.

State and persistence: `struct digitv_state` persists `is_nxt6000` and shared 7-byte send/receive buffers in device private memory. Hardware state includes firmware-loaded bridge, demod registers, tuner PLL registers, and remote mode.

Dependencies and integration: depends on `digitv.h`, MT352, NXT6000, DVB PLL, generic DVB USB bulk control, I2C core, and legacy DVB USB RC handling.

Risks: `digitv_ctrl_msg()` rejects lengths over four bytes and uses shared buffers protected only by higher-level locks where callers provide them. The I2C adapter warns but does not support more than two messages well. `identify_state()` infers cold state from missing manufacturer/product strings, which is device-specific.

Test signals: cold firmware load, warm probe, MT352 and NXT6000 variants, I2C register reads/writes, tuner retune on NXT6000, endpoint `0x02` streaming, RC key read/ack behavior, and unplug during RC polling.
