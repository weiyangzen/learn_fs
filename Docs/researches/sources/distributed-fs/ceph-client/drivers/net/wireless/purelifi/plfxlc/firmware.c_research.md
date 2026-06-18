<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/firmware.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/firmware.c

## Purpose
This file handles pureLiFi firmware and device metadata transfers over USB vendor control and bulk endpoints. It downloads FPGA images for LiFi X/XC devices, downloads packed XL firmware for LiFi XL devices, and reads MAC address, serial number, and firmware version from the device.

## Important APIs, Types, And Functions
Internal helpers are `send_vendor_request()` for USB control IN and `send_vendor_command()` for USB control OUT. Public functions are `plfxlc_download_fpga()`, `plfxlc_download_xl_firmware()`, and `plfxlc_upload_mac_and_serial()`.

## Control Flow
`plfxlc_download_fpga()` selects `plfxlc/lifi-x.bin` or `plfxlc/lifi-xc.bin` from USB IDs, requests firmware, asks the device for FPGA setup status, sends a setup command, validates the magic endpoint byte, streams bit-reversed firmware blocks over bulk OUT to the indicated endpoint, reads FPGA state, validates success, sends the state command, and delays for device settle time.

`plfxlc_download_xl_firmware()` sends the XL firmware-start command, loads `plfxlc/lifi-xl.bin`, reads the packed file count and total size, rejects more than ten embedded files or oversized pieces, iterates embedded file offsets, sends file-select commands, sends 64-byte data chunks for each file, then sends the execute command. `plfxlc_upload_mac_and_serial()` reads MAC, serial, and firmware version through vendor requests and copies them into caller-provided buffers.

## State And Persistence
The function-local firmware metadata and DMA buffers are transient. Device firmware/FPGA state persists on the USB device after successful download until reset/disconnect. MAC and serial are copied into the `plfxlc_mac`/probe-local state managed by `usb.c`.

## Dependencies And Integration Points
Uses Linux firmware loader, USB control/bulk APIs, `bitrev8()`, and constants from `usb.h`/`intf.h`. Called from `usb.c` probe before USB reset/configuration and mac80211 hardware initialization.

## Risks
Firmware file parsing trusts embedded offsets enough that malformed files can produce out-of-range reads if not covered by size checks; XL size checks reject individual sizes over 60000 but do not comprehensively validate every offset before memcpy. FPGA transfer allocates and frees one block copy per chunk. Several vendor requests ignore return codes, so failed setup/status reads can become later validation errors. `plfxlc_download_xl_firmware()` logs intermediate failures but returns zero after the execute command path unless earlier fatal errors return, which can mask transfer issues.

## Test Signals
Test all supported USB IDs, missing firmware files, malformed XL pack headers, FPGA magic/state failures, bulk transfer errors, and metadata reads. Probe logs should show firmware version and selected image; successful probe should continue through radio enable and mac80211 registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/firmware.c -->
