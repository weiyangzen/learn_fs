# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dvb-usb-firmware.c

Purpose: firmware download support for Cypress AN2135/AN2235/FX2 based DVB USB devices and generic Intel HEX line parsing for firmware images.

Important APIs/functions: `usb_cypress_load_firmware()` stops the Cypress CPU, writes firmware records, and restarts it. `dvb_usb_download_firmware()` requests the firmware file and dispatches by controller type or device-specific callback. `dvb_usb_get_hexline()` parses one firmware record into `struct hexline`. `usb_cypress_writemem()` wraps vendor request `0xa0`.

Control flow: cold-device probe calls `dvb_usb_download_firmware()`. The firmware loader requests `props->firmware`, selects Cypress or `download_firmware`, parses records from `fw->data`, writes each record to the target address, and restarts the controller CPU after EOF. Device-specific controller types require a callback.

State and persistence: firmware bytes are transient kernel firmware objects. Persistent effects are in the USB controller RAM and CPU run state until device reset/replug. No local persistent state is retained after release.

Dependencies and integration: depends on Linux firmware loader, USB control messages, Cypress controller IDs in DVB USB properties, and the public `struct hexline` contract from DVB USB headers.

Risks: `cypress[type]` indexes by controller ID, so enum values must remain dense and valid. HEX parsing is minimal and does not validate checksums. Extended linear address handling leaves record length/data offset behavior commented, so nonstandard records may parse incorrectly. Firmware failure returns before warm-state initialization.

Test signals: missing firmware error path, valid AN2135/AN2235/FX2 firmware upload, USB traces for CPUCS stop/start addresses `0x7f92` and `0xe600`, HEX parser malformed-record rejection, and device reconnect or `no_reconnect` warm initialization.
