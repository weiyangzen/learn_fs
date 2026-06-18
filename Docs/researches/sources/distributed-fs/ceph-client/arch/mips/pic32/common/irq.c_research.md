## sources/distributed-fs/ceph-client/arch/mips/pic32/common/irq.c

### Purpose
This file provides the PIC32 architecture IRQ initialization hook.

### Important APIs, Types, And Functions
`arch_init_irq()` calls `irqchip_init()`.

### Control Flow
During architecture interrupt initialization, control passes directly to generic irqchip OF probing. Device-tree interrupt-controller nodes determine the concrete IRQ chips.

### State, Persistence, And Dependencies
The function creates no local state. Persistent IRQ domains and chips are created by `irqchip_init()`. Dependencies are Linux irqchip infrastructure and MIPS `arch_init_irq()` expectations.

### Integration Points
PIC32MZDA device trees must describe interrupt controllers compatible with irqchip drivers.

### Risks
If the DT lacks a supported interrupt controller, the platform has no interrupt handling. There is no PIC32-specific fallback here.

### Test Signals
Boot should show irqchip initialization, timer interrupt mapping, and working device interrupts from DT-described controllers.
