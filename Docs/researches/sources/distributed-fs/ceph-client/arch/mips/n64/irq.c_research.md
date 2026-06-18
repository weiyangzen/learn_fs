<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/n64/irq.c -->
## sources/distributed-fs/ceph-client/arch/mips/n64/irq.c

### Purpose
`n64/irq.c` initializes the Nintendo 64 platform's CPU interrupt controller.

### Important APIs, Types, And Functions
`arch_init_irq()` calls `mips_cpu_irq_init()`.

### Control Flow
During IRQ initialization, the generic MIPS CPU IRQ controller is initialized. N64-specific interrupt device details are left to platform devices/drivers.

### State, Persistence, And Dependencies
Persistent state is the CPU IRQ domain/descriptors created by `mips_cpu_irq_init()`. Dependencies include `asm/irq_cpu.h` and Linux IRQ core headers.

### Integration Points
The IRQ numbers used in `n64/init.c` for RCP and timer IRQs rely on this CPU IRQ setup.

### Risks
This minimal setup assumes all needed interrupts arrive through standard MIPS CPU interrupt lines. Additional cascade controllers would require more platform-specific code.

### Test Signals
Boot N64 platform and verify timer interrupt, RCP IRQ delivery, and platform device IRQ requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/n64/irq.c -->
