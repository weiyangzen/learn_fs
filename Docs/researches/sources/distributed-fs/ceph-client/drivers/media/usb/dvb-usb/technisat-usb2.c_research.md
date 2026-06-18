# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/technisat-usb2.c

## Purpose
This driver supports TechniSat SkyStar USB HD DVB-S/S2 devices. It implements a bulk-message I2C bridge, firmware state detection, STV090x/STV6110x frontend stack, LNB voltage via demod GPIOs, EEPROM MAC with LRC validation, raw IR decoding, LED control, and delayed LED status work.

## Important APIs, types, and functions
`struct technisat_usb2_state` stores the device pointer, delayed green LED work, power state, last scancode, and a 64-byte scratch buffer. `technisat_usb2_i2c_access()` performs bulk out/in I2C commands and handles firmware status codes. `technisat_usb2_set_led()`, `technisat_usb2_set_led_timer()`, and `technisat_usb2_green_led_control()` manage red/green LEDs. `technisat_usb2_frontend_attach()` attaches STV090x and STV6110x and copies tuner control callbacks into the demod config.

## Control flow and state
Probe initializes the device and, when warm, schedules green LED polling every 500 ms unless disabled. `identify_state` sets alternate setting 1 and uses a version vendor request to decide cold/warm. I2C transfers combine write/read pairs. MAC reads use four LRC-checked attempts. RC polling asks firmware for timing samples, converts durations into `ir_raw_event`s, and lets rc-core decode protocols.

## Dependencies and integration
The driver depends on DVB USB, `stv090x`, `stv6110x`, rc-core raw IR, Cypress FX2 firmware `dvb-usb-SkyStar_USB_HD_FW_v17_63.HEX.fw`, isochronous endpoint `0x02`, and USB control/bulk primitives.

## Risks and test signals
Risks include shared `i2c_mutex` for LED/IR/I2C vendor requests, delayed work after disconnect, buffer truncation to 62 bytes, accepted tuner NAK special case, and global mutation of the STV090x config. Test firmware detection, frontend attach, MAC LRC failure, raw IR decode, LED disabled/enabled modes, delayed work cancellation on unplug, and sustained isoc streaming.
