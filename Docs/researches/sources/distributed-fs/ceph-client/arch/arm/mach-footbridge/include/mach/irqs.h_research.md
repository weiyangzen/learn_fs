<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-footbridge/include/mach/irqs.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-footbridge/include/mach/irqs.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/mach-footbridge/include/mach/irqs.h` belongs to Intel/DEC Footbridge ARM platform support in the Ceph-client kernel source snapshot. It exports register definitions, physical/virtual address helpers, IRQ constants, or prototypes consumed by adjacent platform C/assembly files.

### Important APIs, Types, And Functions
Important macros/register names include `NR_IRQS`, `NR_DC21285_IRQS`, `_ISA_IRQ(x)`, `_ISA_INR(x)`, `_DC21285_IRQ(x)`, `_DC21285_INR(x)`, `IRQ_CONRX`, `IRQ_CONTX`, `IRQ_TIMER1`, `IRQ_TIMER2`, `IRQ_TIMER3`, `IRQ_IN0`, `IRQ_IN1`, `IRQ_IN2`, `IRQ_IN3`, `IRQ_DOORBELLHOST`, `IRQ_DMA1`, `IRQ_DMA2`, `IRQ_PCI`, `IRQ_SDRAMPARITY`, `IRQ_I2OINPOST`, `IRQ_PCI_ABORT`, `IRQ_PCI_SERR`, `IRQ_DISCARD_TIMER`, and 46 more.

### Control Flow
There is no executable control flow; consumers include the header or build metadata.

### State, Persistence, And Dependencies
Dependencies include `asm/mach-types.h`. Local/static state or exported register data includes none. Compatible strings or firmware/device-tree identifiers observed: none. There is no private runtime persistence in this header; it defines constants and declarations used by compiled platform code.

### Integration Points
Integration points are PCI host/fixup code. Callers should treat none as platform hooks rather than generic APIs when those symbols are visible.

### Risks
Primary risks include interrupt masking/wakeup regressions.

### Test Signals
Useful test signals include ARM build coverage for the relevant CONFIG symbols, interrupt storm, mask/unmask, and wake-capable IRQ tests, PCI enumeration and board-specific fixup checks. Source reading signal: 97 lines; 1 include; 0 function/entry points; 70 macro/defines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-footbridge/include/mach/irqs.h -->
