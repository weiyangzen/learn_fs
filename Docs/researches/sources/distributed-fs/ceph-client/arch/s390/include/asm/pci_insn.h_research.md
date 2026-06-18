# sources/distributed-fs/ceph-client/arch/s390/include/asm/pci_insn.h

Purpose: This header defines zPCI privileged instruction status codes, request encodings, function/interrupt information blocks, and low-level instruction wrappers.

Important APIs/types/functions: It includes status/condition-code constants, address-space identifiers, modify-function controls, FIB control bits, `struct zpci_fib` and format unions, SIC operation controls, directed-interrupt blocks, `union zpci_sic_iib`, static key `have_mio`, and wrappers such as `zpci_mod_fc()`, `zpci_refresh_trans()`, `zpci_load()`, `zpci_store()`, `__zpci_store_block()`, `zpci_barrier()`, and `zpci_set_irq_ctrl()`.

Control flow: zPCI core prepares FIB/SIC blocks, issues modify-function-control instructions, registers IOAT/MSI state, performs load/store/store-block MMIO operations, refreshes translations, and uses barriers for ordering.

State and persistence: Persistent state is in firmware/device function controls, registered interrupt vectors, IOAT state, FMB address, and static MIO capability key; structures here are command blocks passed to instructions.

Dependencies and integration points: It depends on Linux jump labels and integrates with `pci.h`, `pci_io.h`, DMA/IOMMU, MSI, and zPCI firmware/hardware instruction handlers.

Risks and test signals: Instruction status handling must distinguish busy, invalid handle, and function error cases. Tests should cover MMIO loads/stores of all sizes, store-block, MIO on/off, IOAT registration, MSI direct/all modes, translation refresh, and error status propagation.
