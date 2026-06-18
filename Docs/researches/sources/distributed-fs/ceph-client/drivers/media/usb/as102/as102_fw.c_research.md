# sources/distributed-fs/ceph-client/drivers/media/usb/as102/as102_fw.c

## Purpose
Loads AS102 firmware from Intel HEX files and uploads it to the device over the low-level firmware packet operation.

## Important APIs, types, and functions
Firmware filenames are split by single-tuner versus dual-tuner mode: `as102_data1_st.hex`, `as102_data2_st.hex`, `as102_data1_dt.hex`, and `as102_data2_dt.hex`. `atohx()` converts two ASCII hex digits. `parse_hex_line()` extracts line length, address bytes, record type, and data/address-extension bytes. `as102_firmware_upload()` iterates over firmware lines, builds `struct as10x_fw_pkt_t`, sends data records with request `0x0001`, and sends EOF request `0x0003`. `as102_fw_upload()` requests part 1, uploads it, waits 100 ms, then requests and uploads part 2.

## Control flow and state
The upload path is synchronous and temporary: firmware files are requested through the firmware loader, parsed linearly, and each data packet is sent through `bus_adap->ops->upload_fw_pkt()`. Dual-tuner mode chooses the alternate firmware pair. No persistent kernel state is stored beyond firmware side effects on the device.

## Dependencies and integration points
Depends on Linux firmware loader, AS102 driver state, firmware packet structures from `as102_fw.h`, and USB implementation of `upload_fw_pkt` in `as102_usb_drv.c` using endpoint 1 bulk OUT.

## Risks and test signals
Risks include weak HEX validation, no checksum verification, assumptions about newline-terminated records, and packet size/address-extension parsing. Upload failure in registration is tolerated by `try_then_request_module`, so test both available and missing firmware paths. Test signals are part1/part2 success logs, no leak of requested firmware on errors, correct dual-tuner filename selection, and device responding to later AS10x commands.
