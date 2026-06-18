# sources/distributed-fs/ceph-client/drivers/parisc/eisa.c

## Purpose
This file provides PA-RISC platform support for the Mongoose and Wax EISA bus adapters. It bridges EISA-style I/O port access, 8259-compatible interrupt handling, EEPROM discovery, and Linux EISA root registration into the PA-RISC `parisc_driver` model. It also exposes EISA port helpers for non-PCI builds and accepts the `eisa_irq_edge=` boot option for ISA cards installed in EISA slots.

## Important APIs, Types, And Functions
The main persistent object is the singleton `eisa_dev`, which embeds `struct pci_hba_data`, the EEPROM physical address, and an `eisa_root_device`. Port operations are `eisa_in8/16/32()` and `eisa_out8/16/32()`, backed by `eisa_permute()` and GSC MMIO accesses. Interrupt support is implemented by `eisa_mask_irq()`, `eisa_unmask_irq()`, `eisa_irq()`, `init_eisa_pic()`, and the `eisa_interrupt_type` irq chip. Probe and registration are handled by `eisa_probe()` and `parisc_eisa_init()`. Polarity helpers `eisa_make_irq_level()` and `eisa_make_irq_edge()` are called by the EEPROM enumerator and boot-parameter parser.

## Control Flow
`parisc_eisa_init()` registers a driver matching Mongoose and Wax bus adapters. `eisa_probe()` claims the EISA memory and I/O resources, registers the host bridge, requests the parent PA-RISC IRQ, installs irq chips for IRQs 0-15, sets `EISA_bus`, resolves and maps the EEPROM address, calls `eisa_enumerator()` to parse configured slots, initializes the PIC, and finally registers an EISA root device when enumeration succeeds. Runtime I/O uses `eisa_permute()` to translate legacy port numbers into the PA-RISC EISA MMIO window. Interrupt delivery enters through the Wax/Mongoose IRQ, reads the EISA interrupt acknowledge register, masks and acknowledges the selected 8259 line, calls `generic_handle_irq()`, then unmasks the line.

## State And Persistence
Driver state is global and effectively permanent after boot: the single adapter object, `eisa_eeprom_addr`, `master_mask`, `slave_mask`, `eisa_irq_level`, and `eisa_irq_configured`. Hardware state includes claimed address windows, the mapped EEPROM, PIC mask registers, and edge/level trigger registers. There is no removal path; failures during probe unwind IRQ/resource mapping only up to the failing point.

## Dependencies And Integration Points
This code depends on PA-RISC GSC MMIO helpers, `parisc_device` matching, CCIO resource routing, PCI HBA registration infrastructure, Linux generic IRQ handling, Linux EISA core registration, and the EISA EEPROM/enumerator interfaces. `eisa_eeprom.c` consumes `eisa_eeprom_addr`, and `eisa_enumerator.c` calls the IRQ polarity helpers before `init_eisa_pic()` programs the trigger registers.

## Risks
The driver assumes only one EISA adapter because the hardware cannot be flexed. PIC programming and the mask cache must remain synchronized under `eisa_irq_lock`; otherwise interrupts can be lost or left enabled. Error unwinding does not release every resource in every failure case, which is acceptable for boot-only hardware but risky for refactors. The boot parser loops on invalid values without advancing the cursor, so malformed input is worth checking carefully. EEPROM-derived IRQ polarity and user-forced edge polarity can conflict, producing warnings but still applying the last setting.

## Test Signals
Useful signals are adapter discovery logs, successful resource claims, `/proc/ioports` and `/proc/iomem` EISA ranges, registered EISA slots, readable EEPROM, and successful interrupt delivery for both ISA edge-triggered and EISA level-triggered cards. Regression tests should stress IRQ 2 cascade handling, boot-time `eisa_irq_edge=10,11`, failed EEPROM mapping, and slot enumeration failures.
