# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/pctv452e.c

## Purpose
This driver supports Pinnacle PCTV 452e HDTV USB and TechnoTrend TT-connect S2-3600/S2-3650-CI DVB-S/S2 devices. It implements the 0xaa/0x55 control envelope, I2C bridge, isochronous streaming, STB0899/STB6100 frontend stack, LNB power chips, Common Interface support, RC polling, MAC readout, and probe/disconnect handling.

## Important APIs, types, and functions
`struct pctv452e_state` stores the EN50221 CA object, CA mutex, transaction counter, initialization bit, and last RC key. `tt3650_ci_msg()` and the `tt3650_ci_*` callbacks implement CI attribute/control/slot operations. `pctv452e_i2c_msg()` and `pctv452e_i2c_xfer()` translate I2C to the device command. `pctv452e_power_ctrl()` selects isoc alternate setting and sends reset sequence. `pctv452e_frontend_attach()` attaches STB0899, either LNBP22 plus CI or ISL6423, and `pctv452e_tuner_attach()` attaches STB6100.

## Control flow and state
Probe tries PCTV and TT property tables. Power-on is one-shot via `initialized`. I2C and CI messages increment an 8-bit transaction counter and validate returned sync/id bytes. RC polling reads a 64-byte answer and uses RC5 scancodes. Disconnect releases CI before DVB USB teardown.

## Dependencies and integration
The file integrates `stb0899`, `stb6100`, `isl6423`, `lnbp22`, `dvb_ca_en50221`, `ttpci-eeprom`, rc-core, Linux Ethernet helpers, and USB isochronous transport. It uses source-local large STB0899 register tables.

## Risks and test signals
Risks include fixed 64-byte command envelopes, transaction wrap, partial I2C result interpretation, CI locking/lifetime, different isoc frame geometries per product, and MAC fallback between 24C16/24C64 EEPROMs. Test CI CAM insert/reset/TS enable, frontend/tuner attach, LNB chip attach, RC keyup/keydown, MAC decode, isoc streaming, reset idempotence, and disconnect after CA initialization.
