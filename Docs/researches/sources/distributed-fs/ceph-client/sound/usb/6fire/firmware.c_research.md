# sources/distributed-fs/ceph-client/sound/usb/6fire/firmware.c

## Purpose
Loads and validates the 6Fire device firmware chain: EZ-USB loader firmware, FPGA bitstream, and EZ-USB application firmware. It also checks runtime firmware version and passes endpoint packet-size data needed by later PCM altsettings.

## Important APIs, Types, and Functions
Public API is `usb6fire_fw_init()`. Important helpers are Intel HEX parser functions `usb6fire_fw_ihex_hex()`, `usb6fire_fw_ihex_next_record()`, `usb6fire_fw_ihex_init()`, vendor control helpers `usb6fire_fw_ezusb_write()`/`read()`, `usb6fire_fw_fpga_write()`, upload helpers `usb6fire_fw_ezusb_upload()` and `usb6fire_fw_fpga_upload()`, and `usb6fire_fw_check()`.

## Control Flow
`usb6fire_fw_init()` reads an 8-byte firmware state block. State `0x01` uploads the loader firmware and returns `FW_NOT_READY`. State `0x02` verifies current version, uploads FPGA firmware with bytes bit-reversed in 512-byte chunks, then uploads application firmware with endpoint packet-size postdata at address `0x0003`, returning `FW_NOT_READY`. State `0x03` verifies the known firmware version and returns ready. Unknown signatures or states fail.

Intel HEX upload validates the whole firmware by scanning records and CRCs, stops the EZ-USB CPU, writes all data records to addresses, optionally writes postdata, then restarts the CPU.

## State and Persistence
No long-lived driver state. Firmware persists on the USB device until power cycle or reset. The static `ep_w_max_packet_size` table must match PCM packet sizes and control rate altsettings.

## Dependencies and Integration Points
Uses Linux firmware loader, USB control/bulk APIs, `bitrev8()`, and module firmware declarations for `6fire/dmx6firel2.ihx`, `6fire/dmx6fireap.ihx`, and `6fire/dmx6firecf.bin`. Called before ALSA card creation in `chip.c`.

## Risks
Firmware files are external runtime dependencies; missing files prevent device startup. HEX parser accepts only data and EOF records, so extended-address records are unsupported. Packet-size table synchronization is critical for high-rate ISO transfers. Upload returns `FW_NOT_READY`, relying on device reconnect/reprobe semantics.

## Test Signals
Test all firmware states with valid/missing/corrupt firmware files, HEX CRC failure, short bulk transfer from FPGA upload, unknown version rejection, and ready-state probe without upload. Confirm dmesg firmware requests match `MODULE_FIRMWARE`.
