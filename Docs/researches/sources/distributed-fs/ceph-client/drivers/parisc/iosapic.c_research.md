# sources/distributed-fs/ceph-client/drivers/parisc/iosapic.c

## Purpose
This file manages PA-RISC I/O SAPIC interrupt routing for PCI line interrupts. It reads firmware Interrupt Routing Tables, registers integrated I/O SAPIC blocks exposed by LBA host bridges, translates PCI interrupt pins into I/O SAPIC input lines, allocates CPU transaction IRQs, and programs I/O SAPIC redirection table entries.

## Important APIs, Types, And Functions
External entry points are `iosapic_register()`, `iosapic_fixup_irq()`, and on 64-bit builds `iosapic_serial_irq()`. Initialization is `iosapic_init()` and `iosapic_load_irt()`. Routing helpers include `irt_find_irqline()`, `iosapic_xlate_pin()`, `iosapic_set_irt_data()`, `iosapic_rd_irt_entry()`, and `iosapic_wr_irt_entry()`. The IRQ chip `iosapic_interrupt_type` supplies mask, unmask, ack, eoi, and SMP affinity callbacks.

## Control Flow
At boot, `iosapic_init()` loads the firmware IRT through PAT PDC or legacy PDC calls. LBA probe later calls `iosapic_register()` with the integrated I/O SAPIC HPA and mapped address; registration verifies that the HPA exists in the IRT, reads the SAPIC version, allocates one `vector_info` per IRdT entry, and links the SAPIC into `iosapic_list`. During PCI bus fixup, `iosapic_fixup_irq()` translates the device’s interrupt pin, handles SuperIO quirks, locates the matching IRT entry, allocates a transaction IRQ for the SAPIC input if not already allocated, fills EOI data, claims the CPU IRQ with the I/O SAPIC irq chip, and assigns `pcidev->irq`. Unmasking programs the redirection entry from the saved IRT polarity/trigger data and transaction address/data, then sends an EOI.

## State And Persistence
Global state includes the firmware IRT pointer/count and the linked list of registered I/O SAPICs. Each `iosapic_info` persists mapped register base, HPA, version, vector count, and `vector_info` array. Each vector persists its IRT entry, transaction IRQ/address/data, EOI register/data, and INTIN number. Hardware redirection table entries persist until mask/unmask/affinity changes.

## Dependencies And Integration Points
The driver depends on PDC/PAT firmware interfaces, PCI interrupt-pin semantics, PA-RISC transaction IRQ helpers, CPU IRQ claim/eoi helpers, Linux IRQ core, LBA host bridge registration, SuperIO quirks, and `iosapic_private.h` structures. `lba_pci.c` relies on it during `lba_fixup_bus()`.

## Risks
The code assumes a single global IRT outside future multi-cell support. Many failures are handled by `BUG_ON()` or `panic()`, reflecting early boot expectations. If an IRT entry is missing, PCI devices may be left without usable interrupts. Vector allocation currently happens during PCI enumeration for every present device rather than when a driver requests the IRQ. Polarity/trigger correctness depends entirely on firmware IRT data. Affinity updates rewrite only the destination half and must preserve the low entry correctly.

## Test Signals
Signals include successful IRT loading, I/O SAPIC registration per LBA, correct IRQ assignment for devices behind PCI-PCI bridges, shared INTIN reuse without duplicate allocation, correct level-low programming, EOI delivery, SMP affinity migration, and SuperIO USB/legacy routing. Negative tests include devices with `INTERRUPT_PIN=0`, missing IRT entries, and legacy firmware without I/O SAPIC support.
