# sources/distributed-fs/ceph-client/arch/sparc/include/asm/parport_64.h

## sources/distributed-fs/ceph-client/arch/sparc/include/asm/parport_64.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/parport_64.h` implements SPARC64 parport_pc platform probing and EBus DMA shims for ECPP/parallel OpenFirmware devices. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 255 lines, 5863 bytes. Primary surface: `PARPORT_PC_MAX_PORTS`, DMA shim functions `request_dma/free_dma/enable_dma/disable_dma/set_dma_*`, `get_dma_residue`, `ecpp_probe`, `ecpp_remove`, `ecpp_match`, `ecpp_driver`, and `parport_pc_find_nonpci_ports`. Symbol scan highlights: `_ASM_SPARC64_PARPORT_H`, `PARPORT_PC_MAX_PORTS`, `HAS_DMA`, `DEFINE_SPINLOCK`, `claim_dma_lock`, `release_dma_lock`, `struct ebus_dma_info`, `struct parport`, `DECLARE_BITMAP`, `request_dma`, `free_dma`, `enable_dma`, `disable_dma`, `clear_dma_ff`, `set_dma_mode`, `set_dma_addr`, `set_dma_count`, `get_dma_residue`, `ebus_dma_residue`, `ecpp_probe`, `struct device_node`, `ecpp_remove`, `parport_pc_find_nonpci_ports`, `platform_driver_register`.

### Control Flow
platform driver probe maps OF resources, optionally registers an EBus DMA channel, configures NS87303 ECP/IRQ mode, calls `parport_pc_probe_port`, and unregisters/unmaps resources on remove. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
static `sparc_ebus_dmas` and `dma_slot_map` persist per parport; EBus DMA registers and parport core state are live while devices are bound. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<linux/of.h>`, `<linux/platform_device.h>`, `<linux/string.h>`, `<asm/ebus_dma.h>`, `<asm/ns87303.h>`, `<asm/prom.h>`. Integration dependencies: `linux/of.h`, `linux/platform_device.h`, `asm/ebus_dma.h`, `asm/ns87303.h`, `asm/prom.h`, parport_pc, platform bus, and OF resources.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
slot allocation and cleanup must stay balanced; DMA lock shims are global; resource indexing assumes OF nodes provide expected register windows and IRQs.

### Test Signals
ECPP platform-device probe/remove, parport_pc transfer tests with FIFO/DMA enabled, OF resource failure injection, and lockdep around DMA lock usage. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
