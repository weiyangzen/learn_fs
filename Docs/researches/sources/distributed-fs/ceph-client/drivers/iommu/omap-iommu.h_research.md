# sources/distributed-fs/ceph-client/drivers/iommu/omap-iommu.h

## Purpose
This header defines the private OMAP IOMMU data model, MMIO register layout, bit fields, and page-size conversion helpers consumed by `omap-iommu.c` and related OMAP IOMMU support code.

## Important APIs, Types, And Functions
`struct omap_iommu` describes one hardware MMU instance: MMIO base, syscon handle, device pointer, attached domain, debugfs directory, IOTLB/page-table locks, current I/O page directory, DMA address, TLB count, saved register context, saved CAM/RAM entries, bus-error behavior, IOMMU core object, and power-state token. `struct omap_iommu_domain` embeds `struct iommu_domain` and tracks a single client device plus an array of `struct omap_iommu_device` entries. `struct omap_iommu_arch_data` is stored as per-client private data and binds a client to its IOMMU devices. `struct iotlb_entry`, `struct cr_regs`, and `struct iotlb_lock` model CAM/RAM entries and TLB lock register fields.

Register definitions cover `MMU_REVISION`, IRQ status/enable, walk/control, fault address, table base, lock, TLB load/CAM/RAM/flush/read registers, emulation fault address, and general-purpose bus-error-back control. Bit definitions cover IRQ categories, table-walk enable, MMU enable, CAM valid/preserved/page-size fields, RAM address/endian/element-size/mixed fields, and DRA7 DSP system MMU config.

## Control Flow
The header has no runtime control flow, but it encodes control decisions used by the C file. `for_each_iotlb_cr()` iterates hardware TLB entries by repeatedly invoking `__iotlb_read_cr()`. `get_cam_va_mask()`, `iopgsz_max()`, and `bytes_to_iopgsz()` drive size validation and CAM encoding in map/TLB paths.

## State And Persistence
The types in this header define all long-lived driver state: domain attachment, per-instance hardware context, saved TLB context across PM, and per-client private links. Register and bit definitions are stable ABI-like hardware contracts for OMAP IOMMU blocks.

## Dependencies And Integration Points
The header depends on `linux/bitops.h` and `linux/iommu.h`. It is tightly coupled to OMAP platform data, OMAP DT binding properties, and `omap-iopgtable.h` for descriptor layout.

## Risks
Incorrect register bit definitions would directly corrupt hardware programming. The private structs are shared between generic IOMMU paths, runtime PM, fault handling, and debug paths, so field lifetime and locking expectations must stay aligned with the implementation. The page-size macros only support the four OMAP hardware sizes; callers must reject other sizes.

## Test Signals
Compile coverage of `omap-iommu.c` is the main signal. Runtime signals include correct TLB iteration, correct page-size encoding for map requests, and successful suspend/resume context save/restore.
