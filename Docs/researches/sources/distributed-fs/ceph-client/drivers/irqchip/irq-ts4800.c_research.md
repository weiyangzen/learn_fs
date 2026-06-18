# sources/distributed-fs/ceph-client/drivers/irqchip/irq-ts4800.c

## Purpose
Implements the Technologic Systems TS-4800 FPGA multiplexed interrupt controller. It exposes eight child IRQs behind one parent interrupt and masks/unmasks them through 16-bit FPGA registers.

## Important APIs, Types, And Functions
`struct ts4800_irq_data` stores MMIO base, platform device, and domain. The irq chip supplies mask/unmask and `irq_print_chip()`. `ts4800_ic_chained_handle_irq()` reads the FPGA status register and dispatches each set bit.

## Control Flow
Probe maps MMIO, masks all child IRQs, parses the parent IRQ, creates an eight-line one-cell domain, installs the chained handler, and saves drvdata. Runtime dispatch handles all set status bits or calls `handle_bad_irq()` if the parent fires with no status.

## State And Persistence
State is the domain and MMIO base, plus hardware mask bits. Remove removes the domain but does not explicitly clear the chained handler. Device-managed allocation covers memory and MMIO lifetime.

## Dependencies And Integration Points
Depends on platform-device probing, OF address/IRQ parsing, chained irqchip helpers, seq_file chip printing, and compatible `technologic,ts4800-irqc`.

## Risks
The hardware has only eight child bits but uses 16-bit masks/status reads; invalid DT child hwirqs beyond eight are not explicitly rejected in map. Parent spurious interrupts are treated as bad IRQs. Remove should be audited if hot-unbind matters.

## Test Signals
Trigger each of eight FPGA IRQs, verify mask/unmask bits, spurious parent interrupt handling, `/proc/interrupts` chip naming, and module remove/probe cycles if supported.
