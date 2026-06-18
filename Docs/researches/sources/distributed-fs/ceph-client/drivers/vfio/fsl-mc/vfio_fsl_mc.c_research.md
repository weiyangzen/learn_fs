# sources/distributed-fs/ceph-client/drivers/vfio/fsl-mc/vfio_fsl_mc.c

## Purpose

`vfio_fsl_mc.c` implements VFIO access for NXP/Freescale Management Complex bus devices, including DPRC containers and child objects. It exposes MC object regions, command portal read/write operations, reset, interrupts, MMIO mapping, iommufd physical binding, and DPRC container scanning/driver-override handling.

## Important APIs, Types, and Functions

`vfio_fsl_mc_ops` is the VFIO device-ops table. Key functions are `vfio_fsl_mc_open_device()`, `vfio_fsl_mc_close_device()`, `vfio_fsl_mc_ioctl()`, `vfio_fsl_mc_read()`, `vfio_fsl_mc_write()`, `vfio_fsl_mc_mmap()`, `vfio_fsl_mc_reset_device()`, `vfio_fsl_mc_init_device()`, `vfio_fsl_mc_scan_container()`, and the fsl-mc driver probe/remove functions. `vfio_fsl_mc_bus_notifier()` helps force children of a VFIO-bound DPRC toward the VFIO driver.

## Control Flow

Probe allocates a VFIO device, registers it with VFIO, scans a DPRC container if applicable, and stores driver data. Init assigns the device set: DPRCs use themselves, non-DPRC children use their parent, so related objects share VFIO serialization. DPRC init registers a bus notifier and performs `dprc_setup()` to open the container and allocate an MC portal; non-DPRC init reuses the parent `mc_io`.

Open allocates region metadata from `obj_desc.region_count`, disables mmap for DPRC portals, marks page-aligned non-DPRC regions mmap-capable, and sets read/write flags from fsl-mc resources. Userspace ioctls obtain device info, IRQ info, configure IRQs through `vfio_fsl_mc_intr.c`, or reset the object. Reads and writes are restricted to 64-byte offset-zero command portal accesses; writes submit an MC command and poll for completion, while reads fetch the 8 qwords in reverse order. Close unmaps regions, resets the object, cleans IRQs, and cleans the container IRQ pool.

## State and Persistence Behavior

Per-device state includes `mc_dev`, bus notifier, region table with optional `ioaddr` mappings, interrupt gate mutex, and IRQ array managed by the companion file. DPRC scans can create/remove child devices and set driver overrides; reset operations affect MC object hardware state. No state is file-backed.

## Dependencies and Integration Points

The driver integrates with VFIO core, IOMMUFD physical helpers, fsl-mc object APIs, DPRC setup/scan/remove/reset, MC command portal layout, Linux MMIO remapping, eventfd interrupts, and fsl-mc bus notifications. It sets `driver_managed_dma = true`.

## Risks and Edge Cases

Portal read/write requires exactly 64 bytes at offset zero; partial or misaligned userspace accesses fail. `vfio_fsl_mc_send_command()` uses fixed udelay polling up to 5 seconds, which can block the calling task. DPRC close resets before IRQ cleanup and then cleans the parent container IRQ pool; failure ordering should be tested. The bus notifier sets driver override on new children but only warns if a non-VFIO driver binds. Region `ioaddr` mappings are lazy and cleaned on close.

## Test Signals

Test DPRC and non-DPRC probe/init, container scan failure unwind, region flag generation, mmap denial for DPRC, command portal 64-byte read/write, command timeout, reset ioctl, IRQ setup/cleanup, close with reset failure warning, bus notifier driver override, remove with child cleanup, and iommufd attach/detach.
