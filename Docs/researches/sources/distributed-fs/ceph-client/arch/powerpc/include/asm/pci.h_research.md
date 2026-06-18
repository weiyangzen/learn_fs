<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pci.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pci.h

## Purpose
This header provides the PowerPC architecture-facing PCI API for probing policy, legacy IO, DMA ops, OF scanning, resource setup, and PCI mmap support.

## Important APIs, Types, And Functions
It defines `PCI_PROBE_NONE/NORMAL/DEVTREE`, `PCIBIOS_MIN_IO`, `PCIBIOS_MIN_MEM`, `IOBASE_*`, `pcibios_assign_all_busses()`, `pci_get_legacy_ide_irq()`, `set_pci_dma_ops()`, `PCI_DISABLE_MWI` on PPC64, `pci_domain_nr()`, `pci_proc_domain()`, mmap capability macros, legacy read/write/mmap/attribute helpers, bus/resource survey helpers, dynamic PHB init/remove, OF PCI device/bus scan/rescan helpers, `pci_parse_of_flags()`, `pci_phys_mem_access_prot()`, IO-space offset/setup, and `pcibios_scan_phb()`.

## Control Flow
PCI core calls these hooks during bus discovery, resource assignment, device enabling, legacy IO access, mmap setup, and dynamic host bridge changes. Legacy IDE IRQ falls back to 14/15 unless `ppc_md` overrides.

## State And Persistence Behavior
The header owns no state. It exposes persistent PCI domain, PHB, DMA ops, and OF-derived device state owned by PCI architecture code.

## Dependencies And Integration Points
It depends on PCI bridge definitions, machdep hooks, DMA mapping ops, OF scanning, and generic PCI core.

## Risks And Edge Cases
PPC64 disables MWI/cacheline touching because firmware and hardware semantics differ. Reassign-all-bus policy is architecture flagged. Legacy mmap must preserve caching/protection rules.

## Test Signals
Run PCI probe from OF and normal scanning, domain display, legacy IO syscalls, PCI mmap, DMA ops selection, dynamic PHB add/remove, and legacy IDE IRQ routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pci.h -->
