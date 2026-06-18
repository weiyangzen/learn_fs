# sources/distributed-fs/ceph-client/arch/sparc/include/asm/oplib_64.h

## sources/distributed-fs/ceph-client/arch/sparc/include/asm/oplib_64.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/oplib_64.h` declares the SPARC64/P1275 PROM client-interface API for boot, console, CPU control, power management, MMU mapping, memory retention, device-tree traversal, and direct CIF calls. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 253 lines, 8357 bytes. Primary surface: `prom_version`, `prom_root_node`, `prom_stdout`, `prom_chosen_node`, PROM method-name globals, `prom_init`, `prom_startcpu*`, `prom_sleepself/system`, `prom_retain`, `prom_itlb_load`, `prom_dtlb_load`, `PROM_MAP_*`, `prom_map/unmap`, property traversal, and `p1275_cmd_direct`. Symbol scan highlights: `__SPARC64_OPLIB_H`, `struct linux_mlist_p1275`, `struct linux_mem_p1275`, `prom_init`, `prom_init_report`, `prom_reboot`, `prom_feval`, `prom_cmdline`, `prom_halt`, `prom_halt_power_off`, `prom_get_idprom`, `prom_console_write_buf`, `prom_write`, `prom_startcpu`, `prom_startcpu_cpuid`, `prom_stopcpu_cpuid`, `prom_stopself`, `prom_idleself`, `prom_resumecpu`, `prom_sleepself`, `prom_sleepsystem`, `prom_wakeupsystem`, `prom_getunumber`, `prom_retain`, and 31 more.

### Control Flow
SPARC64 boot initializes the CIF handler, uses PROM services for early console and device tree access, may map/unmap client memory, starts/stops CPUs, and eventually minimizes PROM interaction after kernel services take over. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
PROM root/chosen/stdout handles and boot mapping globals persist as early-boot/platform state. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/openprom.h>`. Integration dependencies: `asm/openprom.h`, P1275 firmware, SPARC64 head/setup code, SMP boot, and OF/device-tree code.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
P1275 calls require exact argument cells and firmware-safe calling context; wrong map flags or TLB load parameters can corrupt early mappings.

### Test Signals
SPARC64/sun4v boot, early console, CPU bring-up, PROM property traversal, suspend/wakeup where supported, and map/unmap smoke tests. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
