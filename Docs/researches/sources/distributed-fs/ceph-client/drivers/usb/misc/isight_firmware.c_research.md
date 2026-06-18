# sources/distributed-fs/ceph-client/drivers/usb/misc/isight_firmware.c

Purpose: Firmware loader for Apple built-in USB iSight cameras that enumerate as `05ac:8300` before UVC firmware is loaded. After loading `isight.fw`, the device detaches and returns as a UVC-compatible camera for `uvcvideo`.

Important APIs and types: `isight_firmware_load()` is the probe routine and only substantial function. It uses `request_firmware()`, vendor control request `0xa0`, a 50-byte staging buffer, and a simple firmware record format with 4-byte length/address headers.

Control flow: probe requests `isight.fw`, writes `1` to CPUCS-like address `0xe600` to initialize/hold the loader, iterates firmware records until `len == 0x8001`, skips zero-length records, writes each record in up-to-50-byte chunks to the requested address, then writes `0` to `0xe600` to complete/run the firmware.

State and persistence: no device state is retained in the driver after probe; loaded firmware changes the device's runtime identity. Risks include `release_firmware(firmware)` in the out path even when firmware request failed and `firmware` was never initialized, raw `printk()` diagnostics, no exact final success marker enforcement if the loop ends by size, and no class-device state. Test signals include missing/malformed firmware, chunk boundary handling, expected disconnect/re-enumeration, and UVC driver bind after load.
