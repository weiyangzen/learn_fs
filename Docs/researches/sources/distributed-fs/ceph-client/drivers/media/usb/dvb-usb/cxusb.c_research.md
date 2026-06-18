# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/cxusb.c

## Purpose
Implements the main DVB USB driver for Conexant CXUSB/Bluebird-style USB TV devices. It provides bridge control messaging, I2C master access, GPIO helpers, power and streaming callbacks, remote-control polling, frontend/tuner attachment for many board variants, Medion analog/digital mode arbitration, firmware state/download quirks, USB probe/disconnect, and the `dvb_usb_device_properties` tables consumed by the DVB USB framework.

## Important APIs, Types, And Functions
The exported/shared APIs are `cxusb_ctrl_msg()`, `cxusb_medion_get()`, and `cxusb_medion_put()`. `cxusb_ctrl_msg()` is the bridge command primitive: it bounds commands by `MAX_XFER_SIZE`, serializes through `d->data_mutex`, prepends the command byte, calls `dvb_usb_generic_rw()`, and copies the optional response.

Key internal APIs include:

- I2C and GPIO: `cxusb_i2c_xfer()`, `cxusb_i2c_algo`, `cxusb_gpio_tuner()`, `cxusb_bluebird_gpio_rw()`, `cxusb_bluebird_gpio_pulse()`, `cxusb_nano2_led()`, and `cxusb_d680_dmb_gpio_tuner()`.
- Power/streaming: `_cxusb_power_ctrl()`, `cxusb_power_ctrl()`, `cxusb_aver_power_ctrl()`, `cxusb_bluebird_power_ctrl()`, `cxusb_nano2_power_ctrl()`, `cxusb_d680_dmb_power_ctrl()`, `cxusb_streaming_ctrl()`, `cxusb_aver_streaming_ctrl()`, and `cxusb_d680_dmb_streaming_ctrl()`.
- Remote control: `cxusb_rc_query()`, `cxusb_bluebird2_rc_query()`, and `cxusb_d680_dmb_rc_query()`.
- Attachment callbacks: board-specific `*_frontend_attach()` and `*_tuner_attach()` functions for CX22702, LGDT3303, MT352, ZL10353, XC2028/XC3028, MXL5005S, DiB7000P/DiB0070, LGS8GXX, ATBM8830, and MAX2165 devices.
- Probe/lifetime: `cxusb_probe()`, `cxusb_disconnect()`, `bluebird_fx2_identify_state()`, `bluebird_patch_dvico_firmware_download()`, `cxusb_medion_priv_init()`, and `cxusb_medion_priv_destroy()`.

## Control Flow
The USB driver registers as `dvb_usb_cxusb` with `cxusb_table`. Probe tries Medion first because it has hybrid analog handling, then tries each Bluebird/Aver/Conexant property table until `dvb_usb_device_init()` accepts the device. For Medion, probe validates the analog isochronous alternate setting, powers the hardware, switches to analog, registers V4L2 analog devices through `cxusb_medion_register_analog()`, switches back to digital, powers down, then releases the initial `CXUSB_OPEN_INIT` state through `cxusb_medion_put()`.

Digital streaming generally enters `cxusb_streaming_ctrl()`. On Medion, starting digital streaming first acquires `CXUSB_OPEN_DIGITAL`; failure returns immediately if analog owns the device. It then sends `CMD_STREAMING_ON`; stopping sends `CMD_STREAMING_OFF` and releases the Medion open reference. Other boards use simpler bridge-specific streaming commands or drain USB pipes before enabling.

Frontend attachment selects USB alternate settings, sends `CMD_DIGITAL`, performs board-specific GPIO resets, and calls `dvb_attach()` for the expected demodulator. Tuner attach callbacks then attach or configure the matching tuner. Device property tables bind these callbacks to USB IDs, stream endpoint/buffer settings, firmware requirements, RC maps, and power callbacks.

Medion mode arbitration is centralized in `cxusb_medion_get()`/`cxusb_medion_put()`. The open lock protects `open_type` and `open_ctr`. First acquisition for a different mode powers the device, calls `cxusb_medion_set_mode()` to select USB altsetting 6 for digital or 1 for analog, clears bulk pipe halts, sends `CMD_DIGITAL` or `CMD_ANALOG`, marks GPIO state stale, and, for analog, calls `cxusb_medion_analog_init()`. Additional users of the same mode increment the count; opposite-mode acquisition returns `-EBUSY`.

## State And Persistence
`struct cxusb_state` holds cached GPIO write state/refresh flags, optional I2C client handles, a command buffer, a stream mutex, and saved frontend status hooks. Medion extends this through `struct cxusb_medion_dev` in `cxusb.h`. The driver persists no data to disk. Runtime state is held in kernel objects owned by the DVB USB framework, the I2C adapter, attached frontend/tuner modules, RC core, V4L2 analog devices, and USB device/interface settings. Firmware download patching creates a temporary in-memory firmware copy for some DViCO devices.

## Dependencies And Integration Points
This file sits at the intersection of USB core, DVB USB framework, Linux media frontend/tuner modules, I2C core, RC core, and optional V4L2 analog support. It includes many demod/tuner headers and uses `dvb_attach()` so module availability matters. `cxusb.h` provides shared state and debug definitions; `cxusb-analog.c` supplies analog hooks when configured. Firmware names include `dvb-usb-bluebird-01.fw`, `dvb-usb-bluebird-02.fw`, and Cypress FX2 paths via the DVB USB framework.

## Risks
Several board paths rely on reverse-engineered command values and magic register sequences, so regressions can be hardware-specific. `cxusb_i2c_xfer()` must keep transfer lengths within `MAX_XFER_SIZE`; unsupported transaction shapes or oversized messages return errors. Medion mode switching is sensitive because comments note switching during I2C transactions can crash the device, hence `cxusb_medion_set_mode()` serializes with `i2c_mutex`. Power-off is deliberately blocked while analog owns the device; mistakes there can reset active V4L2 capture. Firmware patching depends on hard-coded offsets. Probe tries many property tables in sequence, making USB-ID overlap and cold/warm identification important.

## Test Signals
Test signals include successful `dvb_usb_device_init()` for each supported USB ID, firmware download and cold/warm transition behavior for Bluebird devices, I2C scan/attach success for each demod/tuner pair, TS streaming start/stop on the expected endpoint, remote-control key events matching the configured RC map, Medion analog/digital mutual exclusion returning `-EBUSY` when expected, and clean disconnect that unregisters analog V4L2 devices and any I2C client devices without leaks or use-after-free reports.
