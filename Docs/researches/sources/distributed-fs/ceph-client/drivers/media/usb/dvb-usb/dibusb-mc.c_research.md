# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dibusb-mc.c

Purpose: USB driver for DiB3000M-C/P based DiBUSB USB2 DVB-T devices. It defines USB IDs, one device-property profile, and module registration using common MC attach helpers.

Important APIs/functions: `dibusb_mc_probe()` calls `dvb_usb_device_init()`. `dibusb_mc_properties` wires `dibusb2_0_streaming_ctrl()`, `dibusb_pid_filter()`, `dibusb_pid_filter_ctrl()`, `dibusb_dib3000mc_frontend_attach()`, `dibusb_dib3000mc_tuner_attach()`, `dibusb2_0_power_ctrl()`, `dibusb_i2c_algo`, and legacy `dibusb_rc_query()`.

Control flow: matching USB IDs enter probe, firmware `dvb-usb-dibusb-6.0.0.8.fw` is loaded for Cypress FX2 cold devices, a single adapter/frontend is initialized, and USB bulk endpoint `0x06` carries transport-stream data. Device descriptions cover DiBcom MOD3000P, Artec/Lite-On/MSI/Grandtec/Leadtek/Humax variants.

State and persistence: per-adapter `struct dibusb_state` stores demod ops and tuner flags. Device state is inherited from the DVB USB core: I2C adapter, demux, frontend, RC polling, stream URBs, and firmware-loaded bridge.

Dependencies and integration: integrates the DiBUSB common module, MC common attach module, Cypress firmware loader, DVB USB core, and Linux USB driver registration.

Risks: ID table order is explicitly fixed and used by property descriptions. `rc_map_size` is a numeric FIXME. All boards share one property profile, so board-specific quirks must live in common attach logic or USB ID checks.

Test signals: cold/warm enumeration for every listed USB ID, firmware download, endpoint `0x06` bulk streaming with 32 PID filters, remote polling, Lite-On calibration path, and driver disconnect cleanup.
