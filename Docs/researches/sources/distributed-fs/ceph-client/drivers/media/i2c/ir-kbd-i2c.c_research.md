# sources/distributed-fs/ceph-client/drivers/media/i2c/ir-kbd-i2c.c

## Purpose
`ir-kbd-i2c.c` is a Linux media I2C remote-control driver for several IR receiver chips used by TV/video capture hardware, plus optional Hauppauge/Zilog IR transmitter support. It binds as `ir-kbd-i2c`, creates an `rc_dev` input device, polls receiver chips through I2C, decodes vendor-specific key formats into rc-core scancodes, and exposes raw IR transmit callbacks when a Zilog blaster is present.

## Important APIs, Types, And Functions
The driver depends on `media/rc-core.h` and the platform data contract from `media/i2c/ir-kbd-i2c.h`. The central runtime object is `struct IR_i2c` from that header; this file fills its I2C clients, `rc_dev`, delayed work, protocol/keymap metadata, polling interval, lock, optional TX client, carrier, and duty cycle. Receiver decoders include `get_key_haup_common()`, `get_key_haup()`, `get_key_haup_xvr()`, `get_key_pixelview()`, `get_key_fusionhdtv()`, `get_key_knc1()`, `get_key_geniatech()`, and `get_key_avermedia_cardbus()`. Polling flows through `ir_key_poll()`, `ir_work()`, `ir_open()`, and `ir_close()`. Zilog TX uses packed `struct code_block`, `send_data_block()`, `zilog_init()`, `zilog_ir_format()`, `zilog_tx()`, `zilog_tx_carrier()`, and `zilog_tx_duty_cycle()`.

## Control Flow
`ir_probe()` rejects HDPVR unless `enable_hdpvr` is set, allocates `struct IR_i2c`, chooses a decoder/keymap/protocol set by I2C address, then lets platform data override name, keymap, `rc_dev`, protocol mask, polling interval, and key decoder. It allocates an `rc_dev` if needed, initializes rc-core fields, delayed work, and optional Zilog TX at dummy address `0x70`, then registers the rc device. Open schedules immediate delayed work. The worker takes `ir->lock` opportunistically, polls one key, reports via `rc_keydown()`, and reschedules itself. Remove cancels work, unregisters the optional TX client, and unregisters/frees the rc device.

For TX, `zilog_tx()` formats a pulse/space buffer into the Zilog table-limited encoding, transfers the packed code block in small I2C chunks, commands the chip to send, retries readiness for up to about one second, then returns the transmitted sample count on success.

## State And Persistence
State is volatile kernel/device state only. The delayed work loop persists while the rc device is open. `ir->old` suppresses Geniatech repeats. `ir->lock` serializes polling with transmit. Carrier and duty cycle are cached in memory. There is no nonvolatile persistence; device registers and TX RAM are programmed as needed.

## Dependencies And Integration Points
The driver integrates with the I2C core, rc-core keymaps/protocols, bridge-driver platform data, delayed workqueues, module parameters, and optional Zilog I2C dummy clients. `i2c_device_id` entries include generic `ir_video`, `ir_z8f0811_haup`, and HDPVR-specific Zilog support.

## Risks
Address-based autodetection is fragile and relies on board topology or platform overrides. Polling uses `mutex_trylock()`, so receive events may be skipped during long transmit operations. Zilog encoding has strict limits on pulse/space cardinality and maximum duration; recorded IR can fail with `-EINVAL`. Error handling around optional `tx_c` should be regression-tested because the client is only created for TX-capable paths but unregistered on remove/error cleanup. The worker unregisters/frees the rc device on `-ENODEV`, which is an unusual lifetime path that needs careful race coverage with remove/close.

## Test Signals
Useful tests include probing all known addresses with and without platform data, validating open/close cancellation, injecting I2C short reads/errors for each decoder, checking rc-core protocol/scancode output for RC5/RC6/vendor formats, and exercising Zilog transmit with too many distinct pulse/space lengths, excessive durations, carrier bounds, duty changes, and I2C NAK retries. Module parameter coverage should confirm HDPVR is disabled by default and enabled only when requested.
