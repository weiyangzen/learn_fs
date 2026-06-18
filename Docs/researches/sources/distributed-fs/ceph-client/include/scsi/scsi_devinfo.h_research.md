<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_devinfo.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_devinfo.h

## Purpose
This header defines typed blacklist/quirk flags for SCSI devices that need nonstandard scanning, probing, command, capacity, VPD, retry, or upper-driver behavior.

## Important APIs, Types, And Functions
Flags include LUN scan controls (`BLIST_NOLUN`, `FORCELUN`, `SPARSELUN`, `MAX5LUN`, `LARGELUN`, `REPORTLUN2`, `NOREPORTLUN`), broken protocol/feature controls (`BORKEN`, `NOTQ`, `INQUIRY_36`, `NO_VPD_SIZE`, `SKIP_VPD_PAGES`, `TRY_VPD_PAGES`, `NO_RSOC`, `NO_DIF`), removable/media quirks, capacity limits (`MAX_512`, `MAX_1024`), retry quirks, and upper-level-driver suppression. It also defines unused/high-unused masks.

## Control Flow
There is no executable flow. Scan and device-configuration code reads these bits and sets corresponding `scsi_device` and `scsi_target` fields that alter later command generation, probing, retry, and attachment behavior.

## State And Persistence
The flags are represented as `blist_flags_t`, a bitwise `__u64` type. Persistence is external to this header: device-info tables or module parameters assign flags, and `struct scsi_device::sdev_bflags` carries them at runtime.

## Dependencies And Integration Points
It depends on `blist_flags_t` from `scsi_device.h`. It integrates with device scanning, INQUIRY/VPD processing, REPORT LUNS, sd capacity logic, retry policy, and upper-level driver binding.

## Risks
Bits are ABI-like internal policy; reusing an unused bit incorrectly can collide with existing tables. Some flags are deprecated or compatibility-only but still affect real hardware. The `__BLIST_UNUSED_MASK` must reflect all reserved gaps.

## Test Signals
Table-driven tests should verify each flag maps to expected `scsi_device` or scan behavior, unused masks exclude active bits, and old quirk combinations still suppress/report LUNs, VPD, DIF, queueing, and capacity limits as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_devinfo.h -->
