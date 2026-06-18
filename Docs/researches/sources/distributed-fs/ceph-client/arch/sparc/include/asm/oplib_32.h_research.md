# sources/distributed-fs/ceph-client/arch/sparc/include/asm/oplib_32.h

## sources/distributed-fs/ceph-client/arch/sparc/include/asm/oplib_32.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/oplib_32.h` declares the SPARC32 PROM library API for boot arguments, console, reboot/halt, IDPROM, memory lists, CPU start, device-tree traversal, range translation, and CPU discovery. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 184 lines, 6062 bytes. Primary surface: `romvec`, `prom_vers`, `prom_root_node`, `prom_nodeops`, `prom_init`, `prom_getbootargs`, `prom_reboot`, `prom_feval`, `prom_cmdline`, `prom_halt`, `prom_get_idprom`, `prom_*property`, `prom_finddevice`, `prom_apply_*ranges`, and CPU lookup helpers. Symbol scan highlights: `__SPARC_OPLIB_H`, `enum prom_major_version`, `prom_init`, `prom_reboot`, `prom_feval`, `prom_cmdline`, `prom_halt`, `void`, `prom_setsync`, `prom_get_idprom`, `prom_version`, `prom_getrev`, `prom_getprev`, `prom_console_write_buf`, `prom_write`, `prom_startcpu`, `prom_meminit`, `prom_getchild`, `prom_getsibling`, `prom_getproplen`, `prom_getproperty`, `prom_getint`, `prom_getintdefault`, `prom_getbool`, and 12 more.

### Control Flow
early setup initializes `romvec`, determines PROM version, uses PROM calls for console and device tree/property discovery, initializes physical memory, and starts secondary CPUs on supported systems. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
global PROM version, root node, nodeops pointer, and `prom_lock` persist after initialization. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/openprom.h>`, `<linux/spinlock.h>`, `<linux/compiler.h>`. Integration dependencies: `asm/openprom.h`, `linux/spinlock.h`, PROM firmware, platform boot, memory initialization, and device probing.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
PROM calls are early-boot and often non-reentrant; missing locking or wrong property buffer handling can break boot discovery.

### Test Signals
SPARC32 boot on PROM V0/V2/V3 machines, PROM property traversal, memory list validation, and console/reboot/halt tests. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
