# sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/media5200.c

## Purpose
`media5200.c` supports Freescale Media5200 boards and their FPGA cascaded interrupt controller for external IRQs, especially PCI interrupts.

## Important APIs, Types, and Functions
`media5200_init_irq()` initializes the standard MPC52xx PIC, maps `"fsl,media5200-fpga"`, disables FPGA IRQs, creates a six-entry irq domain, and installs `media5200_irq_cascade()`. The `media5200_irq_chip` masks/unmasks FPGA enable bits. `media5200_setup_arch()` maps common devices, configures XLB arbitration, and adjusts GPIO port config for ATA chip selects.

## Control Flow, State, and Persistence
Global `media5200_irq` holds mapped FPGA registers, lock, and irq domain. The cascade masks the upstream interrupt, computes pending enabled FPGA IRQs, dispatches one child IRQ, then acks/unmasks upstream.

## Dependencies and Integration Points
It depends on MPC52xx PIC support, OF IRQ/address parsing, GPIO register layout, generic MPC52xx PCI/restart, and board FPGA interrupt semantics.

## Risks and Test Signals
Risks include possible confusion of status/enable variable names, one-child-per-cascade dispatch, missing FPGA causing PCI interrupt loss, and board-specific GPIO writes. Test signals are PCI IRQ delivery through FPGA, each of six child IRQs, no interrupt storm after mask/ack, and boot logs for missing FPGA.
