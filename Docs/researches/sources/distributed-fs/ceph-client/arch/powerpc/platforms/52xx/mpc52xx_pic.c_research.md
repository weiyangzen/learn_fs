# sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/mpc52xx_pic.c

## Purpose
`mpc52xx_pic.c` implements the MPC5200 interrupt controller and its Linux irq-domain mapping for critical, main, peripheral, and synthetic BestComm/SDMA task interrupts.

## Important APIs, Types, and Functions
`mpc52xx_init_irq()` maps PIC and SDMA registers, disables/masks sources, sets default priorities, creates a linear irq domain, and installs it as default. `mpc52xx_get_irq()` decodes encoded interrupt status and maps hardware IRQs to virqs. Separate irq chips handle external IRQs, main, peripheral, and SDMA sources. `mpc52xx_irqhost_xlate()` translates three-cell DT interrupt specs.

## Control Flow, State, and Persistence
Global `intr`, `sdma`, and `mpc52xx_irqhost` persist for all interrupt handling. External IRQ sense types are programmed through PIC `ctrl`; internal interrupts are level-handled and mask/unmask hardware groups.

## Dependencies and Integration Points
It integrates OF PIC and BestComm nodes, generic irq domains, the PowerPC `ppc_md.get_irq` hook, SDMA task interrupt demultiplexing, and external IRQ DT bindings.

## Risks and Test Signals
Risks include unsupported critical IRQs other than IRQ0, BestComm pending-bit decoding, sense-type translation errors, and panic on missing PIC/SDMA mappings. Test signals are external IRQ edge/level behavior, peripheral IRQs, SDMA task IRQs, no spurious interrupts after initialization, and correct `interrupts = <l1 l2 sense>` mapping.
