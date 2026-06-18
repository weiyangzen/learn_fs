<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tboot.h -->
# sources/distributed-fs/ceph-client/include/linux/tboot.h

## Purpose
defines the shared-memory ABI between Linux and Intel TXT/tboot for measured launch shutdown, S3 resume, ACPI sleep handoff, MAC regions, and DMAR-table retrieval.

## Important APIs, Types, and Functions
The file is 142 lines and exports these visible symbol families: types/enums `tboot_mac_region`, `tboot_acpi_generic_address`, `tboot_acpi_sleep_info`, `tboot`; macros/constants `TB_KEY_SIZE`, `MAX_TB_MAC_REGIONS`, `TBOOT_UUID`; function-like macros `tboot_enabled`, `tboot_probe`, `tboot_shutdown`, `tboot_sleep`, `tboot_get_dmar_table`; inline helpers none; external prototypes `tboot_enabled`, `tboot_probe`, `tboot_shutdown`.

## Control Flow
On TXT systems, `tboot_probe()` locates and validates the shared tboot page, runtime code asks `tboot_enabled()`, shutdown/suspend calls `tboot_shutdown()` with a `TB_SHUTDOWN_*` code, and IOMMU setup may use `tboot_get_dmar_table()`.

## State and Persistence Behavior
The packed `struct tboot` page holds versioned state supplied by tboot plus kernel-updated ACPI sleep info, shutdown type, S3 key, MAC regions, and wait-for-SIPI count. Non-TXT builds compile to stubs.

## Dependencies and Integration Points
It depends on ACPI table structures for CONFIG_INTEL_TXT and integrates with x86 TXT boot, ACPI sleep/shutdown, IOMMU DMAR discovery, and low-level CPU rendezvous. Direct includes are `linux/acpi.h`.

## Risks and Edge Cases
This is a firmware ABI: packing, alignment, version fields, physical addresses, and UUID values must not drift. Incorrect sleep/shutdown fields can break secure resume or leave measured state inconsistent.

## Test Signals
Build with and without CONFIG_INTEL_TXT, validate structure offsets against tboot documentation, boot TXT-capable hardware, and test reboot, S3/S4/S5, and DMAR handoff paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tboot.h -->
