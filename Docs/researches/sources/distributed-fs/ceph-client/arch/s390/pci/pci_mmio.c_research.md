<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_mmio.c -->
# sources/distributed-fs/ceph-client/arch/s390/pci/pci_mmio.c

Purpose: This file implements the s390-specific user-space PCI MMIO syscalls, including fast MIO in-user access and fallback access through PFN-mapped VMAs.

Important APIs/types/functions: Syscall entry points are `s390_pci_mmio_write` and `s390_pci_mmio_read`. Internal helpers include `__memcpy_toio_inuser`, `__memcpy_fromio_inuser`, `__pcistb_mio_inuser`, `__pcistg_mio_inuser`, `__pcilg_mio_inuser`, and `zpci_err_mmio`.

Control flow: Both syscalls first require zPCI to be enabled and constrain requests to a positive length within one page. On systems with MIO, they directly run PCI load/store instructions while temporarily enabling secondary-address-space user access. Without MIO, writes copy user data into a kernel buffer, validate that the supplied address belongs to a readable/writable `VM_IO|VM_PFNMAP` VMA, fault in and pin the PFN map, translate PFN plus page offset into a zPCI I/O address, verify it is in the zPCI IOMAP range, and call kernel `zpci_memcpy_toio/fromio`. Reads then copy the kernel buffer back to user space.

State and persistence: The file does not maintain persistent state. It temporarily changes SACF access mode during in-user MIO instructions, takes the current process mmap read lock, uses transient buffers, and logs MMIO errors with condition-code/status/offset data.

Dependencies and integration points: It depends on s390 PCI I/O instruction helpers, exception tables, `have_mio` static branch, zPCI address layout, Linux VMA/PFNMAP APIs, user copy helpers, and syscall registration. It is the user-visible path for applications that need raw PCI MMIO on s390.

Risks and test signals: User-address handling is high risk: SACF mode must always be restored, partial copy counts must turn into `-EFAULT`, and VMA permission checks must reject non-MMIO mappings. The one-page length restriction prevents crossing mappings. MIO and fallback paths must agree on error semantics. Tests include read/write sizes 1-64 and larger, invalid pointers, unmapped or wrong-permission VMAs, addresses below `ZPCI_IOMAP_ADDR_BASE`, page-boundary rejection, MIO fast path, fallback path, and fault injection in follow_pfnmap/copy_to_user/copy_from_user.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_mmio.c -->
