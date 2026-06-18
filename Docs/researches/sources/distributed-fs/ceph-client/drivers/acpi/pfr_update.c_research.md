<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pfr_update.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/pfr_update.c

## Purpose
`pfr_update.c` implements the ACPI Platform Firmware Runtime Update interface for `INTC1080` devices. It exposes a miscdevice that accepts EFI capsule images, copies them into a firmware communication buffer, verifies basic applicability against firmware capabilities, and starts stage/activate operations through `_DSM`.

## Important APIs, Types, and Functions
`struct pfru_device` stores revision ID, IDA index, parent device, and miscdevice. Core helpers are `query_capability()`, `query_buffer()`, `get_image_type()`, `adjust_efi_size()`, `applicable_image()`, `start_update()`, `pfru_ioctl()`, `pfru_write()`, and platform probe/remove. UAPI commands include `PFRU_IOC_QUERY_CAP`, `PFRU_IOC_SET_REV`, `PFRU_IOC_STAGE`, `PFRU_IOC_ACTIVATE`, and `PFRU_IOC_STAGE_ACTIVATE`.

## Control Flow and State
Probe checks ACPI `_DSM`, allocates an ID, defaults revision to 1, creates miscdevice `pfruN` with node `acpi_pfr_updateN`, and stores device state. `write()` queries the communication buffer, rejects oversize capsules, maps firmware physical memory with `memremap(MEMREMAP_WB)`, copies userspace bytes through an `iov_iter`, queries capability, parses EFI manage-capsule headers, checks image GUID and monotonic runtime/SVN version, unmaps, and returns either an error or the byte count. Ioctls query capability to userspace, set revision after validation, or call `_DSM` start function with stage/activate action and parse update timing/status results.

## State and Persistence
The driver persists only per-device revision/index/miscdevice state. Firmware owns capability state, communication buffer contents, authentication/execution timing, update staging, and activation state. The communication buffer is transiently mapped for each write.

## Dependencies and Integration Points
Dependencies include ACPI `_DSM` package formats for the PFRU GUID, EFI capsule header structures, UAPI `pfrut.h`, miscdevice operations, IDA, uaccess/iov iterators, physical memory mapping, and platform ACPI matching. Telemetry can be observed separately through `pfr_telemetry.c`.

## Risks and Test Signals
Risks include complex capsule pointer arithmetic with limited length validation beyond `len <= buf_size`, package buffer `memcpy()` using firmware-reported lengths into fixed UAPI fields, concurrent writers with no per-device mutex, WB mapping assumptions for firmware memory, and firmware update operations that can be costly or irreversible. Test signals are capability query output, communication buffer query failures, rejection of invalid revision/image GUID/old versions/oversize writes, successful stage/activate `_DSM` status, debug timing logs, and cleanup of miscdevices/IDA indices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pfr_update.c -->
