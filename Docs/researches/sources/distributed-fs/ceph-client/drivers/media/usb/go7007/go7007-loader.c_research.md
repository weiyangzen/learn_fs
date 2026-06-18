# sources/distributed-fs/ceph-client/drivers/media/usb/go7007/go7007-loader.c

Purpose: firmware-stage USB driver for GO7007 devices whose Cypress FX2 controller appears under pre-loader USB IDs. It downloads board-specific FX2 firmware so the runtime `go7007` driver can later bind to the operational device.

Important APIs and functions: `go7007_loader_probe()` matches VID/PID against `fw_configs`, requests the first firmware image, calls `cypress_load_firmware(..., CYPRESS_FX2)`, and optionally repeats for a second firmware stage. `go7007_loader_disconnect()` logs disconnect and clears interface data. `MODULE_FIRMWARE()` declares all supported firmware files.

Control flow: probe rejects devices with multiple configurations, derives vendor/product from descriptors, selects `fw_name1` and optional `fw_name2`, downloads each via the firmware class and Cypress helper, releases firmware buffers after each stage, and returns `-ENODEV` on any failure.

State and persistence: no driver-private state is retained. The only persistent effect is device-side firmware replacement, which normally causes USB re-enumeration.

Dependencies and integration points: depends on USB core, firmware loader, and `<cypress_firmware.h>`. Firmware names overlap with boards later defined in `go7007-usb.c`, especially Sensoray 2250 two-stage firmware and Plextor/Lifeview/Star Trek images.

Risks and test signals: risks include missing firmware files, partial two-stage download success followed by second-stage failure, unsupported multi-configuration devices, and silent assumptions that table match cannot fail. Test with all loader IDs, missing first/second firmware, cypress helper errors, and re-enumeration into the runtime driver.
