<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_insn.c -->
# sources/distributed-fs/ceph-client/arch/s390/pci/pci_insn.c

Purpose: This file wraps s390 PCI-specific instructions for function modification, translation refresh, interrupt control, load/store, block store, MIO access, and PCI write barriers.

Important APIs/types/functions: Exported APIs are `zpci_mod_fc`, `zpci_set_irq_ctrl`, `__zpci_load`, `zpci_load`, `__zpci_store`, `zpci_store`, `__zpci_store_block`, `zpci_write_block`, and `zpci_barrier`. Internal instruction wrappers include `__mpcifc`, `__rpcit`, `____pcilg`, `__pcilg`, `zpci_load_fh`, `__pcilg_mio`, `__pcistg`, `zpci_store_fh`, `__pcistg_mio`, `__pcistb`, `zpci_write_block_fh`, `__pcistb_mio`, and `__pciwb_mio`.

Control flow: Callers pass a function-handle request or MIO address/length. The wrapper emits inline assembly, translates s390 condition codes, extracts status bytes, logs failures with request/address context, and returns Linux error codes for instruction failures. Public load/store APIs choose legacy function-handle instructions or MIO instructions depending on whether the I/O address is a zPCI encoded address and the MIO static branch is active. Block writes loop through instruction-sized chunks when needed.

State and persistence: The file itself owns no persistent state. It mutates device/host hardware state by issuing zPCI instructions, refreshes DMA translations with RPCIT, registers interrupt control through SIC, performs MMIO loads/stores, and orders writes with the MIO write barrier.

Dependencies and integration points: It depends on s390 inline-asm instruction encodings, exception-table handling, condition-code helpers, zPCI address encoding, MIO static key state, and zPCI debug logging. It is used by CLP enable paths, MSI setup, DMA translation flushing, PCI config/MMIO accessors, and user-space MMIO syscalls.

Risks and test signals: Instruction operand packing and status interpretation are architecture ABI-sensitive. MIO versus function-handle address selection must be exact, and partial transfer lengths must not cross instruction-imposed boundaries. Tests include config/MMIO reads and writes of 1/2/4/8/block sizes, MIO enabled/disabled systems, RPCIT refresh failures, SIC IRQ mode changes, exception injection, and write-barrier ordering on real or emulated s390 PCI hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_insn.c -->
