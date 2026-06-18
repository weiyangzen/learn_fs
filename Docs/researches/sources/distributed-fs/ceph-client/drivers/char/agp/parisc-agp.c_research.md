# sources/distributed-fs/ceph-client/drivers/char/agp/parisc-agp.c

## Purpose

`parisc-agp.c` implements HP Quicksilver AGPGART support for PA-RISC systems. It shares the SBA IOMMU page directory, discovers a Pluto/Quicksilver platform path, creates a fake PCI bridge device, and exposes a fixed-size AGP aperture whose GATT entries are PA-RISC I/O PDIR entries.

## Important APIs, Types, And Functions

- `parisc_agp_info` stores IOC/LBA MMIO bases, AGP capability offset, shared GATT pointer, GART base/size, I/O page size, and I/O pages per kernel page.
- `parisc_agp_fetch_size()`, `parisc_agp_configure()`, `parisc_agp_tlbflush()`, `parisc_agp_create_gatt_table()`, and `parisc_agp_free_gatt_table()` implement bridge callbacks.
- `parisc_agp_insert_memory()` and `parisc_agp_remove_memory()` write multiple I/O PDIR entries per kernel page when required.
- `parisc_agp_mask_memory()` builds a valid SBA PDIR entry including coherent index bits.
- `parisc_agp_enable()` performs PA-RISC MMIO AGP command programming.
- `agp_ioc_init()`, `agp_lba_init()`, `parisc_agp_setup()`, `find_quicksilver()`, and `parisc_agp_init()` handle platform discovery.

## Control Flow

Module init finds a Pluto SBA device and a child Quicksilver LBA. IOC init reads IOTLB page-size configuration, computes the GART window at the end of Pluto IOVA space, locates the shared PDIR, and requires an `SBA_AGPGART_COOKIE` reservation. LBA init locates AGP capability registers. Setup allocates a fake PCI device, allocates an AGP bridge with the PA-RISC driver, and registers it. Insert converts AGP page starts into I/O page starts, verifies empty PDIR slots, writes endian-correct masked entries, flushes each entry with `asm_io_fdc()`, and triggers IOC TLB invalidation.

## State And Persistence Behavior

Software state is the single `parisc_agp_info` instance and bridge registration. Hardware-visible state is shared SBA IOMMU PDIR content and IOC/LBA registers. `free_gatt_table()` restores the cookie in the first GATT entry rather than freeing memory, because the table belongs to the IOMMU. The driver sets `cant_use_aperture` to indicate CPU aperture access limitations.

## Dependencies And Integration Points

This file depends on PA-RISC platform headers, `sba_iommu`/rope platform structures, IOC register definitions, AGP core helpers, and PCI-style AGP command conventions. It integrates platform discovery rather than a normal PCI driver registration path.

## Risks And Edge Cases

Incorrect IOTLB page-size decoding or missing cookie disables the driver. For I/O page sizes smaller than kernel pages, insertion fans out each page into multiple entries, so off-by-one bounds are high impact. The driver assumes shared PDIR layout and Pluto constants. Endianness and coherent-index packing in `parisc_agp_mask_memory()` must match hardware exactly. `parisc_agp_init()` ignores the return from `parisc_agp_setup()` and returns zero once a Quicksilver path is found, which can hide setup failure from module init.

## Test Signals

Boot on PA-RISC Pluto/Quicksilver hardware, confirm GART size and sysfs/AGP registration, verify missing cookie disables support, bind/unbind memory and inspect PDIR entries, and check IOC `IOC_PCOM` TLB flushes complete. Static review should cover `parisc_agp_setup()` error propagation, fake PCI device lifetime, and I/O page fanout arithmetic.
