# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dibusb-mb.c

Purpose: USB driver for DiB3000M-B based DiBUSB devices, covering many early USB1.1 and USB2 DVB-T sticks. It selects one of several `dvb_usb_device_properties` profiles during probe and binds board-specific firmware, endpoints, tuner selection, PID filtering, I2C, and legacy RC behavior.

Important APIs/functions: `dibusb_probe()` tries `dibusb1_1_properties`, `dibusb1_1_an2235_properties`, `dibusb2_0b_properties`, and `artec_t1_usb2_properties`. `dibusb_dib3000mb_frontend_attach()` attaches the DiB3000MB demod and installs `dib3000mb_i2c_gate_ctrl()`. Tuner helpers attach Thomson TUA6010XS, Panasonic TDA665X, or probe between them by reading tuner address `0x60`.

Control flow: USB IDs in `dibusb_dib3000mb_table[]` describe cold/warm devices. Probe delegates firmware download and initialization to `dvb_usb_device_init()`. Frontend attach sets demod address `0x8`, attaches via `dib3000mb_attach()`, and installs the gate callback. Tuner attach either fixes `st->tuner_addr` or probes Panasonic versus Thomson through an I2C write/read while the demod gate is open. Property blocks wire firmware names, Cypress controller type, stream endpoint `0x02` or `0x06`, power control, DiBUSB I2C algorithm, PID controls, and legacy RC map.

State and persistence: `struct dibusb_state` holds the tuner address and demod xfer ops. Persistent hardware state is firmware-loaded Cypress controller state, demod/tuner I2C programming, PID filter entries, power mode, and streaming mode. Module state includes adapter-number options only.

Dependencies and integration: depends on `dibusb-common.c`, DiB3000MB demod, `dvb_pll_attach()`, Cypress firmware loading, and the DVB USB core.

Risks: the driver relies on USB ID table order. Tuner probing assumes the Panasonic response can distinguish board populations. Multiple property profiles are tried sequentially; probe failures must leave no partial device state. Optional faulty Anchor IDs are hidden behind `CONFIG_DVB_USB_DIBUSB_MB_FAULTY`.

Test signals: cold and warm probe for each firmware profile, USB1.1 with hardware PID filter, endpoint `0x02` and `0x06` streaming, Thomson/Panasonic tuner detection, RC key events, firmware reconnect/no-reconnect behavior, and unload/reload without stale USB halts.
