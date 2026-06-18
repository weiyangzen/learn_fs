# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/liquidio_image.h

## Purpose
Defines the on-disk LiquidIO firmware image header consumed by the console firmware download path. It describes firmware naming conventions, image limits, boot command storage, and the network-byte-order file format for one or more binary images.

## Important APIs, Types, and Functions
Important constants are `LIO_FW_DIR`, `LIO_FW_BASE_NAME`, `LIO_FW_NAME_SUFFIX`, firmware type strings `nic`, `auto`, and `none`, maximum filename/type/version lengths, `LIO_MAX_BOOTCMD_LEN`, `LIO_MAX_IMAGES`, and `LIO_NIC_MAGIC`. `struct octeon_firmware_desc` stores big-endian load address, image length, and per-image CRC. `struct octeon_firmware_file_header` stores magic, version, boot command, image count, image descriptors, padding, and header CRC.

## Control Flow
There is no direct control flow. `octeon_download_firmware` in `octeon_console.c` reads this format, validates the magic, validates the header CRC, checks the version prefix against `LIQUIDIO_BASE_VERSION`, copies each image to the requested Octeon memory address, appends host UTC boot time to the boot command, and sends the command through the bootloader PCI console.

## State and Persistence Behavior
The header defines persistent firmware file layout. Numeric fields are network byte order, and the boot command is stored inside the firmware header then modified in memory before command submission. The firmware version string is copied into `oct->fw_info.liquidio_firmware_version`.

## Dependencies and Integration Points
Included by `octeon_console.c`. It depends on Linux fixed-endian integer types and CRC handling in the consumer. The constants align firmware file naming and loading behavior with host driver version negotiation in `liquidio_common.h`.

## Risks
The format is security- and reliability-sensitive because bad lengths or addresses could drive large PCI memory writes. The consumer validates header CRC and image count but does not validate a total file size for all image payloads in this header itself; callers must provide sane firmware data. Version prefix matching is strict to the base version string.

## Test Signals
Valid firmware load, invalid magic, bad header CRC, mismatched version, too many images, short file, long boot command after time append, multiple images, boundary chunk writes, and bootloader command failure are the primary signals.
