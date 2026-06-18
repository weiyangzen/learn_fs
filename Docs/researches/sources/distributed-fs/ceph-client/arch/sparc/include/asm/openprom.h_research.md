# sources/distributed-fs/ceph-client/arch/sparc/include/asm/openprom.h

## sources/distributed-fs/ceph-client/arch/sparc/include/asm/openprom.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/openprom.h` defines OpenBoot PROM vectors, device operations, memory lists, boot arguments, PROM node operations, and PROM property/register/range structures. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 280 lines, 7477 bytes. Primary surface: `LINUX_OPPROM_MAGIC`, `struct linux_romvec`, `linux_dev_v0_funcs`, `linux_dev_v2_funcs`, memory/boot-argument structs, `linux_nodeops`, `PROMREG_MAX`, `linux_prom_registers`, PCI range/register/intmap structs, and PROM device constants. Symbol scan highlights: `__SPARC_OPENPROM_H`, `LINUX_OPPROM_MAGIC`, `struct linux_dev_v0_funcs`, `struct linux_dev_v2_funcs`, `struct linux_mlist_v0`, `struct linux_mem_v0`, `struct linux_arguments_v0`, `struct linux_bootargs_v2`, `struct linux_romvec`, `struct linux_nodeops`, `PROMDEV_KBD`, `PROMDEV_SCREEN`, `PROMDEV_TTYA`, `PROMDEV_TTYB`, `int`, `PROMREG_MAX`, `PROMVADDR_MAX`, `PROMINTR_MAX`, `struct linux_prom_registers`, `struct linux_prom64_registers`, `struct linux_prom_irqs`, `struct linux_prom_ranges`, `struct linux_prom_pci_registers`, `struct linux_prom_pci_ranges`, and 2 more.

### Control Flow
early boot receives a PROM vector or client-interface handle, then PROM library code uses these structures to print, halt/reboot, traverse device trees, map devices, and collect memory/device properties. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
PROM vectors and memory lists are firmware-provided boot state; kernel copies or references selected values during early initialization. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<linux/of.h>`. Integration dependencies: `linux/of.h`, `oplib_32.h`, `oplib_64.h`, platform boot code, device tree conversion, and bus probing.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
structure layout is firmware ABI; pointer-size and 32/64-bit range differences must remain exact or early boot/device discovery fails.

### Test Signals
PROM boot on sun4c/sun4m/sun4u/sun4v, device tree traversal tests, property/range parsing validation, and early console/halt paths. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
