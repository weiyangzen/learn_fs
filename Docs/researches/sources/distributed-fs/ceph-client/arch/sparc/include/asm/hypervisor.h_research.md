# sources/distributed-fs/ceph-client/arch/sparc/include/asm/hypervisor.h

## sources/distributed-fs/ceph-client/arch/sparc/include/asm/hypervisor.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/hypervisor.h` defines the sun4v/SPARC64 hypervisor ABI: trap numbers, error codes, service function ids, data-layout structs, and C prototypes for domain, CPU, MMU, interrupt, PCI, LDC, performance, and API-version hypercalls. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 3527 lines, 117692 bytes. Primary surface: `HV_FAST_TRAP`, `HV_CORE_TRAP`, `HV_E*` status codes, `sun4v_mach_*`, `sun4v_cpu_*`, `sun4v_mmu_*`, `sun4v_intr_*`, `sun4v_vintr_*`, PCI/IOMMU/MSI service ids, `sun4v_ldc_*`, `sun4v_*_perf*`, `sun4v_hvapi_*`, `struct hv_tsb_descr`, `struct hv_fault_status`, `struct ldc_mtable_entry`, `struct hv_mmu_statistics`, and NCS/CCB/trap-trace structs. Symbol scan highlights: `_SPARC64_HYPERVISOR_H`, `HV_FAST_TRAP`, `HV_MMU_MAP_ADDR_TRAP`, `HV_MMU_UNMAP_ADDR_TRAP`, `HV_TTRACE_ADDENTRY_TRAP`, `HV_CORE_TRAP`, `HV_EOK`, `HV_ENOCPU`, `HV_ENORADDR`, `HV_ENOINTR`, `HV_EBADPGSZ`, `HV_EBADTSB`, `HV_EINVAL`, `HV_EBADTRAP`, `HV_EBADALIGN`, `HV_EWOULDBLOCK`, `HV_ENOACCESS`, `HV_EIO`, `HV_ECPUERROR`, `HV_ENOTSUPPORTED`, `HV_ENOMAP`, `HV_ETOOMANY`, `HV_ECHANNEL`, `HV_EBUSY`, and 447 more.

### Control Flow
callers marshal up to five 64-bit arguments in outgoing registers and enter fast traps or hyper-fast traps; the hypervisor returns status in `%o0` and optional return values in the remaining registers. Higher-level SPARC64 code uses the declared wrappers to configure CPUs and mondo queues, install MMU/TSB state, manipulate interrupts, configure PCI IOMMU/MSI queues, exchange LDC data, and negotiate hypervisor API versions. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
the header stores no data itself, but its layouts describe persistent hypervisor-owned or guest-owned real-memory state such as machine descriptions, CPU queues, fault-status blocks, trap-trace buffers, PCI IOTSBs, LDC queues/map tables, and reboot/performance metadata. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: no direct include directives. Integration dependencies: `linux/bitops.h`-style bit macros through included kernel headers, assembler callers, SPARC64 trap assembly, sun4v kernel code, PCI, LDC, perf, NCS, and machine-description parsing.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
ABI drift is the main risk: trap ids, bit positions, struct offsets, register volatility, real-address alignment, and page-size encodings must match firmware. Hypercall wrappers must handle nonzero `HV_E*` statuses and partial delivery semantics such as mondo-send CPU-list updates.

### Test Signals
sun4v defconfig cross-build, boot on sun4v/LDOM capable systems, hypervisor API version negotiation tests, CPU hotplug/mondo/interrupt tests, PCI DMA/MSI validation, LDC link bring-up, and sparse/build coverage for assembler/C offset users. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
