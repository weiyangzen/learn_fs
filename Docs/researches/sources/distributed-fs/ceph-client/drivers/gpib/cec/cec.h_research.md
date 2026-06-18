# sources/distributed-fs/ceph-client/drivers/gpib/cec/cec.h

## Purpose
`cec.h` defines the private data and register spacing for the Capital Equipment Corporation PCI-488 and Keithley KPCI-488 GPIB driver.

## Important APIs, Types, and Functions
`struct cec_priv` embeds `struct nec7210_priv`, stores the PCI device pointer, PLX9052 IO base, and IRQ number. `cec_reg_offset` is a constant register stride of 1 between NEC7210 registers.

## Control Flow and State Model
The header contains no runtime flow. It supplies the state layout used by the CEC implementation.

## Dependencies and Integration Points
It depends on NEC7210, GPIB common, and PLX9050 register definitions. The implementation uses these fields to map the PLX bridge and NEC7210 core.

## Risks and Test Signals
The private structure assumes a PLX-backed PCI design and NEC7210-compatible register spacing. Tests should cover resource setup, IRQ disable/free on detach, and correct register-offset use against actual CEC/KPCI hardware.
