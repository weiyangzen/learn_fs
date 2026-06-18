# sources/distributed-fs/ceph-client/drivers/firmware/microchip/mpfs-auto-update.c

Purpose: Implements firmware-upload support for Microchip PolarFire SoC Auto Update, writing bitstream images or bitstream-info descriptors to SPI flash and asking the system controller to verify upgrade images.

Important APIs/types/functions: `mpfs_auto_update_priv` stores system controller, MTD flash, uploader handle, calculated bitstream slot size, and cancel state. Upload ops are `mpfs_auto_update_prepare()`, `mpfs_auto_update_write()`, `mpfs_auto_update_poll_complete()`, and `mpfs_auto_update_cancel()`. Helpers query availability, set the SPI directory, write flash regions, and verify images.

Control flow: Probe gets the system controller and flash, checks Auto Update availability via a security-service command, then registers a firmware uploader named `mpfs-auto-update`. Prepare computes slot size from flash size/erase size and rejects oversized images. Write distinguishes bitstream-info headers from bitstreams, updates the SPI directory for bitstreams, erases/writes the target flash region, honors cancellation after write, and verifies bitstreams through the system controller.

State and persistence behavior: Driver state is per-platform-device. Persistent effects include erasing/writing SPI flash directory, design info, and upgrade image regions. Cancel state is boolean and does not interrupt an in-progress MTD operation.

Dependencies and integration points: Depends on Microchip system controller transactions, MTD, firmware upload framework, firmware loader, debugfs include, cleanup attributes, and flash layout conventions from PolarFire programming docs.

Risks and test signals: This path can brick/update FPGA boot images if offsets or slot sizing are wrong. Directory read-modify-write must preserve unrelated eraseblock contents. Availability bit interpretation is security-sensitive. Test with fake MTD/sys controller, insufficient flash, erase-size alignment, info-vs-bitstream detection, directory already correct, partial MTD writes, verification failure, cancellation, and remove unregistering uploader.
