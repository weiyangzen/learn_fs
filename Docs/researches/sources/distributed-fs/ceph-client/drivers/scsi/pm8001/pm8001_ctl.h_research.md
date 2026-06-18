# sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_ctl.h

## Purpose
`pm8001_ctl.h` is the small support header for the pm8001 sysfs/control implementation. It defines fixed buffer sizes, firmware/NVMD update status values, event-log read window parameters, queue-size constants, and one helper for reading dwords from the AAP1 event-log memory map.

## Important APIs, Types, And Constants
The header defines `IOCTL_BUF_SIZE` as 4096, `HEADER_LEN` as 28, and firmware-image offsets used by `pm8001_update_flash()`. BIOS display logic uses `BIOSOFFSET` and `BIOS_OFFSET_LIMIT` to emit a narrow version string from NVMD data. Status codes such as `FLASH_OK`, `FAIL_OPEN_BIOS_FILE`, `FAIL_FILE_SIZE`, `FAIL_PARAMETERS`, `FAIL_OUT_MEMORY`, and `FLASH_IN_PROGRESS` are written into `pm8001_ha->fw_status` and interpreted by `pm8001_show_update_fw()`.

Diagnostic read constants include `IB_OB_READ_TIMES` for the number of dwords emitted per queue-log read, `SYSFS_OFFSET` for the 1024-byte cursor increment, and queue memory-size constants for PM80xx and PM8001 hardware. The single inline helper, `pm8001_ctl_aap1_memmap(u8 *ptr, int idx, int off)`, reads a `u32` from `ptr + idx * 32 + off` and is used by the AAP1 log sysfs show function.

## Control Flow
The header has no independent control flow. Its constants parameterize control paths in `pm8001_ctl.c`: firmware flashing slices input into 4 KiB chunks with a 28-byte header, BIOS version reads select bytes 56-60, and queue-log sysfs reads emit 256 dwords then advance by 1024 bytes.

## State And Persistence Behavior
No state is stored in this header. Its status values describe in-memory state held by `struct pm8001_hba_info`, and its queue/log sizes describe DMA/MMIO-backed regions whose cursors are stored in the HBA object.

## Dependencies And Integration Points
The header assumes Linux integer typedefs are available through including C files and is tightly coupled to `pm8001_ctl.c`. It also indirectly coordinates with firmware response status constants declared elsewhere because `pm8001_ctl.c` mixes local failure codes from this header with flash-update codes returned by firmware.

## Risks And Edge Cases
`pm8001_ctl_aap1_memmap()` casts a byte pointer to `u32 *`, which assumes alignment and native CPU access semantics suitable for the mapped buffer. The helper does not bounds-check `idx` or `off`; callers must keep indices inside the event-log window. Buffer-size constants are embedded protocol assumptions, so changing them without checking firmware IOMB and sysfs buffer limits can create truncation or overflow risks.

## Test Signals
Compile coverage should catch users of these macros. Behavioral tests should exercise firmware image sizes around 28 bytes, 4096 bytes, and multi-partition boundaries, plus repeated queue-log reads to confirm the `SYSFS_OFFSET` and `IB_OB_READ_TIMES` contract.
