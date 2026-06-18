# sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/firmware.c

## Purpose
`firmware.c` implements Samsung S3FWRN5 bootloader communication and firmware download. It parses the firmware image header, determines hardware-specific base address/signature selection, compares versions, hashes image data, sends update commands, and completes request/response transactions using inbound firmware frames.

## Important APIs, types, and functions
- `s3fwrn5_fw_init()`, `s3fwrn5_fw_request_firmware()`, `s3fwrn5_fw_setup()`, `s3fwrn5_fw_check_version()`, `s3fwrn5_fw_download()`, `s3fwrn5_fw_cleanup()`, and `s3fwrn5_fw_recv_frame()` are the core-facing API.
- `s3fwrn5_fw_prep_msg()` builds firmware headers, toggling the parity bit in `fw_info->parity`.
- `s3fwrn5_fw_send_msg()` writes through the physical layer and waits up to one second for `fw_info->completion`.
- Bootloader commands include GET_BOOTINFO, ENTER_UPDATE_MODE, UPDATE_SECTOR, and COMPLETE_UPDATE_MODE.
- The image header contains date, version, signature offsets/sizes, image offset/sector count, and custom-signature offsets/sizes.

## Control flow
The core first initializes `fw_info`, requests a named firmware blob, and parses fixed offsets. Setup sends GET_BOOTINFO in firmware mode, maps hardware version to a base address, records sector size, and chooses standard or custom signature based on `hw_version[2]`. Version comparison treats larger major, build1, or build2 fields as needing update. Download computes SHA1 over `sector_size * image_sectors`, enters update mode with hash and signature, then writes each sector as one UPDATE_SECTOR command followed by sixteen 256-byte data packets. Completion sends COMPLETE_UPDATE_MODE.

## State and persistence
`struct s3fwrn5_fw_info` stores the requested firmware object, parsed pointers into the firmware blob, selected signature, sector/base metadata, completion, pending response skb, firmware name, and parity. The firmware blob is read-only external persistent input and is released by cleanup; no persistent state is stored by the driver.

## Dependencies and integration points
The file depends on `request_firmware()`, `release_firmware()`, SHA1 from `crypto/sha1.h`, sk_buffs, completions, and `s3fwrn5_write()`. It expects the physical layer to be in firmware mode and inbound frames to call `s3fwrn5_fw_recv_frame()`.

## Risks
Firmware header offsets and sizes are copied from the blob but not fully bounds-checked beyond the 44-byte minimum; malformed images could create out-of-range pointers or image sizes. `s3fwrn5_fw_update_sector()` sends fixed sixteen 256-byte packets, assuming sector size and bootloader expectations align. Version comparison is lexicographic but does not check target field. A stale `fw_info->rsp` triggers `WARN_ON` and drops a frame, so duplicate/unexpected responses can derail an update.

## Test signals
Exercise malformed firmware headers, unknown hardware versions, custom-signature selection, no-update version comparison, update success over multiple sectors, timeout from `s3fwrn5_fw_send_msg()`, non-success bootloader return codes, duplicate response handling, and cleanup after setup failure.
