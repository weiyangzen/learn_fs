# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dibusb-common.c

Purpose: shared implementation for older DiBUSB receivers. It supplies firmware command wrappers for streaming, power, I2C master transfers, EEPROM reads, PID filter control, and legacy remote-control decoding used by both DiB3000M-B and DiB3000M-C/P device drivers.

Important APIs/functions: exported symbols include `dibusb_streaming_ctrl()`, `dibusb_pid_filter()`, `dibusb_pid_filter_ctrl()`, `dibusb_power_ctrl()`, `dibusb2_0_streaming_ctrl()`, `dibusb2_0_power_ctrl()`, `dibusb_i2c_algo`, `dibusb_read_eeprom_byte()`, `rc_map_dibusb_table`, and `dibusb_rc_query()`. The internal `dibusb_i2c_msg()` builds `DIBUSB_REQ_I2C_READ`/`WRITE` bulk messages.

Control flow: frontend drivers attach demods that fill `struct dibusb_state.ops`. Streaming starts by optionally enabling the demod FIFO, then for USB2 devices asks firmware to select streaming mode and enable/disable the FX2 stream. PID helpers delegate to demod ops. I2C transfers are serialized with `d->i2c_mutex`, combine write-then-read pairs, reject oversized writes, and protect EEPROM address `0x50` from raw reads without an offset. RC polling sends `DIBUSB_REQ_POLL_REMOTE`, decodes the five-byte NEC-like buffer via `dvb_usb_nec_rc_key_to_event()`, and reports legacy input events.

State and persistence: state is stored in per-adapter `struct dibusb_state` ops/tuner flags and in USB firmware power/streaming/PID tables. `rc_map_dibusb_table` is a static keymap shared by all supported remotes. No persistent storage is written; EEPROM reads are read-only calibration/config inputs.

Dependencies and integration: depends on `dibusb.h`, generic `dvb_usb_generic_rw()`/`write()`, I2C core, demod operation callbacks from DiB3000 drivers, and the DVB USB legacy RC helper.

Risks: `MAX_XFER_SIZE` limits are manual and the code only checks write length, so unusual I2C shapes depend on caller behavior. `dibusb_i2c_xfer()` returns the number of processed messages, which can be partial on error. Legacy keymap size is hard-coded by users to 111 entries. USB2 power-off returns success without writing sleep state.

Test signals: DiBUSB MB/MC probe, I2C scan through demod/tuner, EEPROM byte reads for IF calibration, streaming start/stop with PID filter toggles, full-speed USB operation requiring hardware PID filtering, RC key and repeat decoding, and disconnect while polling/streaming.
