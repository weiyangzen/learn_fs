# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ath79/irq.h

**Purpose:** Defines the ATH79 Linux IRQ number layout layered on top of MIPS CPU IRQs.

**Important APIs/types/functions:** Exports `MIPS_CPU_IRQ_BASE`, `NR_IRQS`, and mapping macros `ATH79_CPU_IRQ(x)`, `ATH79_MISC_IRQ(x)`, `ATH79_PCI_IRQ(x)`, `ATH79_IP2_IRQ(x)`, and `ATH79_IP3_IRQ(x)`. It reserves 32 misc IRQs after CPU IRQs, 6 PCI IRQs, 2 IP2 IRQs, and 3 IP3 IRQs, then includes `<asm/mach-generic/irq.h>`.

**Control flow:** Interrupt controller setup and drivers use these macros to allocate fixed Linux IRQ numbers. Runtime interrupt flow is in controller code; this header fixes the numbering boundaries that demultiplexers and platform devices rely on.

**State and persistence behavior:** No software state. It creates a compile-time ABI between board files, irqchip code, and drivers through numeric IRQ assignments.

**Dependencies and integration points:** Depends on the generic MIPS IRQ header and is consumed by ATH79 interrupt, PCI, GPIO, timer, and device registration code.

**Risks:** `NR_IRQS` must cover all ranges. Changing a base or count breaks platform-device resources and interrupt demux assumptions. Fixed numbering can conflict with newer dynamic irqdomain patterns if mixed carelessly.

**Test signals:** Build with all ATH79 interrupt users, boot with PCI/WMAC/GPIO/misc interrupts active, inspect `/proc/interrupts`, trigger each interrupt source class, and check for out-of-range IRQ warnings.
