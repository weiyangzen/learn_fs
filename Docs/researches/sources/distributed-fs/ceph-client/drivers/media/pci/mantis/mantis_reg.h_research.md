# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_reg.h

- Purpose: Register map and bit definitions for Mantis interrupts, DMA, I2C, control, GPIF, PCMCIA, and UART-adjacent blocks.
- Important APIs/types/functions: Defines `MANTIS_INT_*`, `MANTIS_DMA_CTL` bits, `MANTIS_I2CDATA_CTL` fields, `MANTIS_CONTROL`, GPIF timing/status/address/data registers, and smart-buffer/card event bits.
- Control flow: All Mantis implementation files use these offsets with `mmread/mmwrite` to acknowledge interrupts, program DMA/RISC, drive I2C, route streams, manage CAM HIF, and handle PCMCIA events.
- State and persistence: No state; constants describe volatile device MMIO hardware.
- Dependencies and integration points: Central dependency for Mantis PCI, DMA, I2C, DVB, IOC, UART, HIF, and PCMCIA code.
- Risks: Duplicate macro names for `MANTIS_GPIF_PCMCIAREG/IOM` appear in different address contexts but same values. Any wrong bit definition can corrupt hardware state across multiple subsystems.
- Test signals: Compile coverage is necessary but insufficient; hardware register access tests through stream, I2C, CAM, and IRQ paths are required.
