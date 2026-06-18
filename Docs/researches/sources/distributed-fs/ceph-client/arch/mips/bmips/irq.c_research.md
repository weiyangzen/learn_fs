# sources/distributed-fs/ceph-client/arch/mips/bmips/irq.c

Purpose: BMIPS interrupt controller and IRQ-domain setup for Broadcom DT systems.

Important APIs and functions: initializes CPU/SoC interrupt routing, maps device-tree interrupts, and installs dispatch handlers for BMIPS platforms.

Control flow: `arch_init_irq`-style setup runs during boot, then runtime interrupts are dispatched through generic IRQ handling.

State and persistence: interrupt masks, domains, and descriptor state for current boot only.

Dependencies and integration points: integrates MIPS CPU IRQs, irqchip/irqdomain code, devicetree interrupt specifiers, and platform devices.

Risks and test signals: mapping mistakes show as missing UART/timer/network interrupts. Test `/proc/interrupts`, DT boot logs, and driver interrupt activity.
