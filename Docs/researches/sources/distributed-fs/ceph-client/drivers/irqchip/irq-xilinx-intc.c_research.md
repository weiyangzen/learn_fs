# sources/distributed-fs/ceph-client/drivers/irqchip/irq-xilinx-intc.c

## Purpose
Implements Xilinx OPB/XPS interrupt controller support for primary and cascaded use. It handles configurable endianness, edge-versus-level input classification, vector-register dispatch, and master enable setup.

## Important APIs, Types, And Functions
`struct xintc_irq_chip` stores MMIO base, root domain, edge mask, and number of inputs. `xintc_read()`/`xintc_write()` switch to big-endian access if MER readback indicates endian mismatch. Chip callbacks mask, unmask, ack, and mask-ack. `xil_intc_handle_irq()` and `xil_intc_irq_handler()` serve primary and chained modes.

## Control Flow
OF init maps registers, reads `xlnx,num-intr-inputs` and optional `xlnx,kind-of-intr`, disables inputs, acks pending bits, enables hardware interrupt/master bits, probes endianness, creates a linear domain, then either chains a parent IRQ or installs the primary handler/default domain. Dispatch reads IVR until the spurious value appears.

## State And Persistence
Per-controller state is allocated at init; primary mode is stored globally. Hardware state includes IER/IAR/MER and edge/level behavior configured by DT. There is no suspend/resume cache.

## Dependencies And Integration Points
Depends on OF address/IRQ parsing, irqdomain, chained handlers, jump labels for endian mode, and compatible `xlnx,xps-intc-1.00.a` or `xlnx,opb-intc-1.00.c`.

## Risks
`xintc_is_be` is a global static key, so mixed-endian instances are not supported. Edge mask width is 32 bits and must not exceed `nr_irq`. `BUG_ON(!base)` makes missing MMIO fatal. Level IRQ ack-on-unmask behavior is hardware-specific.

## Test Signals
Validate little- and big-endian hardware, primary and cascaded modes, edge and level inputs from `xlnx,kind-of-intr`, spurious IVR exit, master enable readback, and invalid DT properties.
