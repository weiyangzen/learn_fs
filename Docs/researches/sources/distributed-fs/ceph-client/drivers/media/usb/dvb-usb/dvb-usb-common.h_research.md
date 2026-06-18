# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dvb-usb-common.h

Purpose: internal header for the DVB USB library implementation files. It centralizes debug macros and prototypes for firmware, power, URB, I2C, DVB adapter/frontend, and remote-control helpers.

Important APIs/types: debug macros map `dvb_usb_debug` bits to info/xfer/pll/ts/error/rc/firmware/memory/USB-transfer channels. Prototypes include `dvb_usb_download_firmware()`, `dvb_usb_device_power_ctrl()`, `usb_urb_*()`, `dvb_usb_adapter_stream_*()`, `dvb_usb_i2c_*()`, `dvb_usb_adapter_dvb_*()`, `dvb_usb_adapter_frontend_*()`, and `dvb_usb_remote_*()`.

Control flow: library C files include this header to call each other without exposing all internals through the public `dvb-usb.h`.

State and persistence: declares module globals `dvb_usb_debug` and `dvb_usb_disable_rc_polling`; no state is allocated here.

Dependencies and integration: includes `dvb-usb.h` and ties together `dvb-usb-init.c`, `dvb-usb-dvb.c`, `dvb-usb-i2c.c`, `dvb-usb-remote.c`, `dvb-usb-urb.c`, and `dvb-usb-firmware.c`.

Risks: internal prototypes must match exported symbols. Debug bit assignments are ABI-like for module users setting `debug=`.

Test signals: full DVB USB library build, module parameter debug output for every bit, and link coverage across all internal helper files.
