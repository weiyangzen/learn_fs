# sources/distributed-fs/ceph-client/arch/mips/dec/int-handler.S

Purpose: DECstation low-level interrupt dispatch assembly. It maps CP0 pending interrupt bits and cascaded CSR/I/O ASIC interrupt-status bits to Linux IRQ numbers or secondary assembly dispatch helpers.

Important labels: `plat_irq_dispatch`, `kn02_io_int`, `kn02xa_io_int`, `kn03_io_int`, `cpu_all_int`, `kn02_all_int`, `asic_all_int`, `asic_dma_int`, `dec_intr_unimplemented`, and `asic_intr_unimplemented`. It consumes global priority tables `cpu_mask_nr_tbl` and `asic_mask_nr_tbl` initialized in `dec/setup.c`.

Control flow: dispatch reads CP0 Cause/Status, masks pending bits, immediately handles FPU interrupt where applicable, scans the CPU priority table for the first matching mask, then either dispatches a direct IRQ number or jumps to a helper address. Cascaded helpers read KN02 CSR or IOASIC SIR/SIMR, mask enabled bits, scan ASIC priority tables, and dispatch direct IRQs or helper routines. DMA and low-priority helpers use bit-search logic to pick the highest relevant IRQ.

State and integration: no local persistent state; it relies on global tables and hardware status registers. It calls `dec_irq_dispatch()` to enter generic IRQ handling and calls panic helpers for unimplemented vectors.

Risks and test signals: table contents and assembly pointer/integer union layout must match exactly. An uninitialized table entry can panic. Test boot on each DECstation machine type, exercise cascade, DMA, RTC, FPU, halt, and bus interrupts, and inspect priority ordering.
