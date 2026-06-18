<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-imsic-state.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-imsic-state.c

## Purpose
`irq-riscv-imsic-state.c` owns the global and per-CPU state for the RISC-V IMSIC, including firmware parsing, MMIO page mapping, vector allocation, local enable/pending synchronization, vector migration, and IRQ matrix management.

## Important APIs, Types, and Functions
It exports global `imsic`, `imsic_get_global_config()`, low-level EIx update, local synchronization/delivery, vector mask/unmask/move/free/allocation, debug helpers, CPU online/offline state hooks, `imsic_setup_state()`, and matrix initialization. Firmware parsing is split among DT/ACPI global population, parent hartid lookup, MMIO resource lookup, and `imsic_parse_fwnode()`.

## Control Flow
Setup rejects multiple IMSIC instances and platforms without AIA, allocates global/per-CPU local config, parses firmware for interrupt IDs and MSI address layout, maps all MMIO register sets, allocates per-CPU local private vectors/dirty bitmaps, associates each parent interrupt with a CPU MSI page, computes minimum guest files, initializes the vector matrix, and frees temporary MMIO arrays. Mask/unmask mark vector IDs dirty and synchronize locally or by pinned timer on target CPU. Move support disables the old vector, enables the new vector, checks pending bits on old and temporary IDs, retriggers on the new CPU by MMIO write, and frees old vectors after synchronization completes.

## State and Persistence
State includes `imsic->global`, per-CPU `imsic_local_priv`, per-vector `enable` and move pointers, dirty bitmaps, timers, and the global IRQ matrix. It is all in RAM plus per-hart IMSIC CSRs/MMIO pages; no filesystem persistence exists. CPU offline deletes synchronization timers and marks matrix CPUs offline.

## Dependencies and Integration Points
The file depends on RISC-V AIA ISA detection, OF/ACPI interrupt and MMIO descriptions, irq matrix allocator, per-CPU storage, timers, SMP, KVM-facing IMSIC global config, and CSR access through `ISELECT`/`IREG`.

## Risks and Edge Cases
The loop that finds MMIO location uses firmware-derived sizing and must handle holes by aligned subtraction. Vector move logic is subtle for non-atomic MSI writes and pending interrupts can be lost if dirty synchronization does not complete. ID 0 and optional IPI ID are reserved in the matrix.

## Test Signals
Validate DT and ACPI parsing, invalid address-layout rejection, multiple MMIO regions, per-CPU MSI page calculation, guest-file minimum calculation, vector allocation exhaustion, mask/unmask synchronization, CPU hotplug, pending interrupt preservation during affinity moves, and debugfs summaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-imsic-state.c -->
