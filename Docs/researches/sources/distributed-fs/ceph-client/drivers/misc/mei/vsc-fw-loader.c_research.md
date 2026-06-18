# sources/distributed-fs/ceph-client/drivers/misc/mei/vsc-fw-loader.c

## Purpose
This file implements Visual Sensing Controller firmware loading over the VSC transport ROM protocol. It identifies the camera sensor and silicon stepping, selects CSI/ACE/SKU firmware blobs from `intel/vsc/`, validates image containers, downloads bootloader and firmware fragments, and boots the camera firmware.

## Important APIs, types, and functions
Important structures are `vsc_rom_cmd`, `vsc_rom_cmd_ack`, `vsc_fw_cmd`, `vsc_img`, `vsc_fw_sign`, `vsc_img_frag`, and `vsc_fw_loader`. Key helpers are `vsc_get_sensor_name()`, `vsc_identify_silicon()`, `vsc_identify_csi_image()`, `vsc_identify_ace_image()`, `vsc_identify_cfg_image()`, `vsc_download_bootloader()`, `vsc_download_firmware()`, and exported `vsc_tp_init()`. `vsc_sum_crc()` computes the protocol checksum.

## Control flow and state
`vsc_tp_init()` allocates loader and fixed-size command buffers, gets the sensor name from ACPI `SID`, queries silicon EFUSE and strap data through ROM dump commands, loads and validates the CSI image, ACE image named by sensor, and SKU config image, maps their fragments into `frags[]`, downloads the bootloader with ROM `DL_START`/`DL_CONT`, then sends firmware `DL_SET`, downloads each non-bootloader fragment in 512-byte chunks, and finally issues `CAM_BOOT`.

## State and persistence behavior
Firmware images are requested and released during initialization only. Loader state is transient heap state managed with cleanup attributes, and firmware contents are not persisted. Device firmware state changes from ROM to loaded runtime firmware after successful boot.

## Dependencies and integration points
It depends on ACPI, Linux firmware loader, unaligned access, bitfield helpers, string lowercasing, and the `vsc_tp_rom_xfer()` transport API. It is invoked by the VSC transport/MEI reset path through exported namespace `VSC_TP`.

## Risks and test signals
Risks include image bounds validation, flexible container parsing, sensor-name buffer length, protocol checksum offsets, fragment-location fallback, zero-size fragments, ROM vs firmware package size mismatch, and cleanup when one firmware request fails. Test signals include missing/invalid firmware files, ACPI SID variations, unsupported silicon stepping rejection, bootloader download chunking, firmware fragment download and boot success, and reset-triggered reinitialization.
