# sources/distributed-fs/ceph-client/arch/sparc/include/asm/intr_queue.h

## sources/distributed-fs/ceph-client/arch/sparc/include/asm/intr_queue.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/intr_queue.h` defines sun4v interrupt-queue head and tail register offsets for CPU mondo, device mondo, resumable error, and non-resumable error queues. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 16 lines, 794 bytes. Primary surface: `INTRQ_CPU_MONDO_HEAD/TAIL`, `INTRQ_DEVICE_MONDO_HEAD/TAIL`, `INTRQ_RESUM_MONDO_HEAD/TAIL`, and `INTRQ_NONRESUM_MONDO_HEAD/TAIL`. Symbol scan highlights: `_SPARC64_INTR_QUEUE_H`, `INTRQ_CPU_MONDO_HEAD`, `INTRQ_CPU_MONDO_TAIL`, `INTRQ_DEVICE_MONDO_HEAD`, `INTRQ_DEVICE_MONDO_TAIL`, `INTRQ_RESUM_MONDO_HEAD`, `INTRQ_RESUM_MONDO_TAIL`, `INTRQ_NONRESUM_MONDO_HEAD`, `INTRQ_NONRESUM_MONDO_TAIL`.

### Control Flow
low-level interrupt code uses these offsets to read or update queue producer/consumer pointers while handling hypervisor-delivered mondo and error events. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
state lives in per-CPU queue registers or queue memory configured through hypervisor CPU queue calls. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: no direct include directives. Integration dependencies: sun4v interrupt trap handling, hypervisor CPU queue configuration, and assembly register access paths.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
incorrect offsets break interrupt queue draining and can stall CPU, device, or error interrupt delivery.

### Test Signals
sun4v interrupt stress, CPU cross-call/mondo tests, error queue injection when available, and disassembly checks for register offsets. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
