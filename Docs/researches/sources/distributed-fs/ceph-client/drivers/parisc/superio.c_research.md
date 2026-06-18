# sources/distributed-fs/ceph-client/drivers/parisc/superio.c

## Purpose
This file supports the National Semiconductor NS87560 Super I/O controller used in HP B/C/J-class workstations. It works around the chip’s non-standard PCI interrupt routing, programs its legacy PIC and internal routing registers, fixes IDE PCI class mode, registers serial and parallel legacy devices, and lets normal IDE/USB drivers bind their functions.

## Important APIs, Types, And Functions
Core functions are `superio_interrupt()`, `superio_init()` as a final PCI fixup, `superio_mask_irq()`, `superio_unmask_irq()`, `superio_fixup_irq()`, `superio_serial_init()`, `superio_parport_init()`, `superio_fixup_pci()` as an early PCI fixup, and `superio_probe()`. State is held in global `struct superio_device sio_dev` from `asm/superio.h`. The IRQ chip is `superio_interrupt_type`.

## Control Flow
PCI IRQ fixup calls `superio_fixup_irq()` during IOSAPIC processing. Function 1, the legacy I/O bridge, is saved and returns no local IRQ; function 2, USB, is saved and returns a SuperIO-local USB IRQ; function 0, IDE, returns the IDE local IRQ. A final PCI fixup on function 1 calls `superio_init()` once both function 1 and USB are known. It borrows the IOSAPIC IRQ found for USB INTD as the parent interrupt for the legacy PIC, rewrites USB to its local IRQ, reads BARs, claims PIC/ACPI I/O regions, enables the LIO PCI function, writes routing config dwords, initializes both 8259 PICs, powers the USB regulator, requests the parent IRQ, and marks the PIC enabled. The parent IRQ handler polls PIC1, dispatches the highest local IRQ with `generic_handle_irq()`, and sends a specific EOI.

## State And Persistence
`sio_dev` stores PCI device pointers, BAR bases for serial/parallel/floppy/ACPI, and whether the legacy interrupt path is enabled. The driver installs irq chips for local IRQs 0-15 and hardware PIC masks persist through mask/unmask operations. Serial and parport registrations persist through their respective subsystems.

## Dependencies And Integration Points
The file integrates PCI fixup ordering, IOSAPIC SuperIO special handling, Linux IRQ core, 8259-style port I/O, serial 8250 early setup, parport PC probing, IDE/USB device binding, and HP-specific SuperIO constants. It is tightly coupled to `iosapic.c` through `is_superio_device()` and `superio_fixup_irq()`.

## Risks
Initialization order is critical: the legacy PIC must be configured before IDE and USB drivers use interrupts. Many failures call `BUG()` because there is little recovery once PCI fixups are in progress. Only IRQs 1,3,4,5,6,7 are accepted; IRQ 2 and slave PIC interrupts are treated as errors. The handler polls only the master PIC and treats some no-active cases as spurious. BAR/resource claims are not checked for failure. The source contains an unserious debug message in an unreachable default branch, but it has no runtime effect unless an unexpected device ID reaches probe.

## Test Signals
Signals include SuperIO discovery log with parent IRQ, correct serial/parallel/floppy/ACPI BARs, USB regulator enabled, functioning ttyS0/ttyS1, parallel port probe, IDE native-mode fixup, USB IRQ remapping, and local IRQ mask/unmask behavior. Regression tests should verify final fixup runs after both LIO and USB functions are saved and that spurious IRQ7 handling does not break active devices.
