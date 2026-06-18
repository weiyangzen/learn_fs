
# sources/distributed-fs/ceph-client/arch/x86/include/asm/e820/api.h

Purpose: public API for x86 E820 firmware memory map processing and reservation.

Important APIs and control flow: declares the active, kexec, and firmware E820 tables plus `pci_mem_start`. Query helpers test whether ranges are mapped by type. Range add/update/remove helpers mutate tables; update helpers sanitize/sort/merge. Additional APIs compute RAM PFN limits, allocate/reserve through memblock, finish early parameters, reserve resources, set up memory and PCI gaps, reallocate tables, register nosave regions, and query entry type. `is_ISA_range()` checks full containment in the legacy ISA window.

State, dependencies, and risks: state is global E820 table variants and memblock/resource reservations. Dependencies include boot params, EFI/firmware memory maps, kexec, and resource tree setup. Risks include overlapping ranges, wrong type conversion, losing firmware map fidelity, and ISA/PCI gap mistakes. Test signals are boot memory maps, kexec/kdump, memblock debug, hibernation nosave regions, and E820 parser tests.
