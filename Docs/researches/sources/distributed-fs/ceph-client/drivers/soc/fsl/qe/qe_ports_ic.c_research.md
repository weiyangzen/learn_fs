# sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/qe_ports_ic.c

## Purpose
Implements a cascaded interrupt controller for QE I/O port interrupts, exposing 32 port interrupt lines through a linear irq_domain.

## Important APIs, types, and functions
`struct qepic_data` stores the mapped register base and irq_domain. The irq_chip `qepic` provides `qepic_mask`, `qepic_unmask`, `qepic_end`, and `qepic_set_type`. `qepic_get_irq` reads pending events and translates the first set bit to a virq. `qepic_cascade` handles the parent interrupt. `qepic_probe` maps resources, creates the domain, and installs the chained handler for compatible `"fsl,mpc8323-qe-ports-ic"`.

## Control flow and state behavior
Mask/unmask update `CEPIMR`, EOI writes the bit to `CEPIER`, and type programming updates `CEPICR` for falling-edge versus both-edge/none behavior. The cascade reads `CEPIER`; if no pending bit exists it returns `-1`, otherwise it maps `32 - ffs(event)` to a child IRQ and passes it to `generic_handle_irq`.

## Dependencies and integration points
Built with `CONFIG_QE_GPIO` alongside `gpio.o`. It integrates QE port events with Linux irq_domain and depends on the parent platform IRQ from device tree.

## Risks and test signals
`qepic_cascade` calls `generic_handle_irq(qepic_get_irq(desc))` without checking for `-1`, so a spurious parent interrupt can pass an invalid IRQ. Only falling-edge and both-edge/none are supported. Test signals include child IRQ delivery for each port bit, mask/unmask behavior in `CEPIMR`, EOI clearing in `CEPIER`, and safe behavior under spurious parent interrupts.
