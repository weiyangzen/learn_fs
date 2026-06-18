# sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-input.c

## Purpose
Adds remote-control support for AU0828 boards with an AU8522-based I2C IR receiver, exposing raw IR events through rc-core.

## Important APIs, types, and functions
`struct au0828_rc` stores device, `rc_dev`, names, polling work, I2C address, and key-read callback. `au8522_rc_read()`, `au8522_rc_write()`, and `au8522_rc_andor()` access AU8522 IR registers over I2C. `au0828_get_key_au8522()` polls interrupt status, reads 40 bytes of encoded pulse/space data, fakes the missing first pulse for NEC/RC5, and stores raw events. `au0828_rc_start()` enables IR and starts delayed work; `au0828_rc_stop()` cancels work and disables IR. `au0828_rc_register()` probes address `0x47`, allocates/registers `rc_dev`, and selects Hauppauge map for supported boards.

## Control flow and state
Core probe calls RC register after DVB/analog setup. rc-core open starts polling every 100 ms. Each work item reads a key and reschedules itself. Disconnect unregisters RC before clearing `usbdev`; key reads check `DEV_DISCONNECTED`. Suspend cancels work and disables IR; resume reenables and restarts polling.

## Dependencies and integration points
Depends on I2C adapter from `au0828-i2c.c`, rc-core raw event decoders, board flags from `au0828-cards.c`, and AU8522 register behavior.

## Risks and test signals
Risks include polling after disconnect, protocol-specific first-pulse reconstruction, double-free concerns if `rc_unregister_device()` and `rc_free_device()` semantics change, and unsupported boards with `has_ir_i2c`. Test signals are rc device registration, raw NEC/RC5 key events with Hauppauge map, clean suspend/resume, and no I2C errors after unplug.
