# sources/distributed-fs/ceph-client/drivers/vfio/pci/ism/main.c

## Purpose

`main.c` implements the s390 IBM Internal Shared Memory VFIO PCI variant. It reuses VFIO PCI core but overrides region offsets and read/write paths because ISM devices cannot use PCI MIO instructions and require PCISTB store-block writes for BAR access.

## Important APIs, Types, and Functions

`struct ism_vfio_pci_core_device` extends `vfio_pci_core_device` with a store-block kmem cache. `ISM_READ()` generates `ism_read8/16/32/64()` wrappers using `__zpci_load()`. `ism_vfio_pci_do_io_r()` performs aligned function-handle-based reads; `ism_vfio_pci_do_io_w()` uses `__zpci_store_block()` with cache-allocated, page-aligned buffers. `ism_vfio_pci_rw()` dispatches config and BAR access. `ism_vfio_pci_ioctl_get_region_info()` reports region offsets using a 48-bit offset shift. `ism_pci_ops` is the VFIO ops table.

## Control Flow

Probe allocates the extended device, stores core driver data, and registers with VFIO PCI core. Init creates a per-function store-block kmem cache named by zPCI function id and sized/aligned to `zdev->maxstbl`, then calls core init. Open enables and finishes VFIO PCI core. Reads and writes decode the high 48-bit-style region index: config space uses common single-access config helpers because zPCI config access must not use MIO, while BAR access uses explicit zPCI load/store-block operations. Remove unregisters core and drops the device reference.

## State and Persistence Behavior

Runtime state is the per-device store-block cache and VFIO PCI core state. BAR/config accesses affect device hardware. There is no file-backed persistence.

## Dependencies and Integration Points

The driver depends on s390 zPCI internals, VFIO PCI private/core helpers, kmem cache APIs with usercopy metadata, and IOMMUFD physical helper ops through its VFIO ops.

## Risks and Edge Cases

BAR write size must be no larger than `zdev->maxstbl` and cannot cross a page boundary. The custom offset shift is 48 bits, larger than generic VFIO PCI's shift, to represent ISM's huge BAR0 write space. The read path chooses the widest aligned load possible; unaligned or small reads degrade to narrower loads. Mmap is not supplied, so access is via read/write.

## Test Signals

Test config read/write, BAR0 huge offset encoding, aligned and unaligned reads, writes at max store-block size, page-crossing write rejection, absent BAR rejection, kmem cache creation/destruction, core registration failure unwind, and probe/remove on IBM ISM device ids.
