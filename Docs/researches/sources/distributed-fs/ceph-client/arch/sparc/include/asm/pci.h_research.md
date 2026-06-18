# sources/distributed-fs/ceph-client/arch/sparc/include/asm/pci.h

Purpose: SPARC PCI policy header defining platform PCI bus defaults and, on sparc64, IOMMU bypass and `/proc/bus/pci` mmap integration.

Important APIs/types/functions: functions/helpers `pci_domain_nr`, `pci_proc_domain`; macros/constants `___ASM_SPARC_PCI_H`, `pcibios_assign_all_busses`, `PCIBIOS_MIN_IO`, `PCIBIOS_MIN_MEM`, `PCI_IRQ_NONE`, `PCI64_REQUIRED_MASK`, `PCI64_ADDR_BASE`, `HAVE_PCI_MMAP`, `arch_can_pci_mmap_io`, `HAVE_ARCH_PCI_GET_UNMAPPED_AREA`, `ARCH_GENERIC_PCI_MMAP_RESOURCE`, `get_pci_unmapped_area`.

Control flow: The file is driven by preprocessor gates such as `___ASM_SPARC_PCI_H`, `CONFIG_SPARC64`; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, PCI paths rather than through standalone functions.

State and persistence behavior: State is compile-time policy only; the runtime domain number is supplied by `pci_domain_nr()`, and framebuffer-style unmapped-area selection is delegated to `get_fb_unmapped_area`.

Dependencies and integration points: Includes/dependencies: none beyond compiler-visible SPARC/kernel types. Integration points include memory-management, PCI; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are configuration-specific build gaps. Test signals: PCI probing, resource mmap tests, 64-bit DMA mask negotiation, and controller-domain enumeration are the relevant signals.
