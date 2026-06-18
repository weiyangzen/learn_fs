# sources/distributed-fs/ceph-client/drivers/misc/genwqe/genwqe_driver.h

## Purpose
`genwqe_driver.h` is the shared GenWQE driver header for versioning, minor-number constants, public DDCB request allocation/free prototypes, CRC32 declaration, and debug hexdump support.

## Important APIs, Types, and Functions
It defines `DRV_VERSION` as `2.0.25`, `GENWQE_MAX_MINOR`, declares `ddcb_requ_alloc()`, `ddcb_requ_free()`, and `genwqe_crc32()`, and provides `genwqe_hexdump()` as a thin wrapper around `print_hex_dump_debug()` with GenWQE/PCI prefixing.

## Control Flow
No standalone control flow exists. Callers include this header to allocate DDCB requests, use the GenWQE-specific CRC, and print debug hex dumps in queue/device paths.

## State and Persistence
The header stores no state. Its constants influence device numbering and user-visible version reporting.

## Dependencies and Integration Points
It includes core kernel structures, PCI/cdev/list/kthread/scatterlist/IOMMU/platform headers, byteorder helpers, and the public user ABI header `linux/genwqe/genwqe_card.h`.

## Risks and Edge Cases
Static minor allocation caps devices at 128. Version changes must remain synchronized with sysfs/debugfs reporting. Header breadth can hide unnecessary dependencies in compile units.

## Test Signals
Build coverage across all GenWQE files, ABI include compatibility, and debug dump invocation under dynamic debug are the main validation signals.
