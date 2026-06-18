<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-footbridge/include/mach/hardware.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-footbridge/include/mach/hardware.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/mach-footbridge/include/mach/hardware.h` belongs to Intel/DEC Footbridge ARM platform support in the Ceph-client kernel source snapshot. It exports register definitions, physical/virtual address helpers, IRQ constants, or prototypes consumed by adjacent platform C/assembly files.

### Important APIs, Types, And Functions
Important macros/register names include `__ASM_ARCH_HARDWARE_H`, `XBUS_SIZE`, `XBUS_BASE`, `ARMCSR_SIZE`, `ARMCSR_BASE`, `WFLUSH_SIZE`, `WFLUSH_BASE`, `PCIIACK_SIZE`, `PCIIACK_BASE`, `PCICFG1_SIZE`, `PCICFG1_BASE`, `PCICFG0_SIZE`, `PCICFG0_BASE`, `PCIMEM_SIZE`, `PCIMEM_BASE`, `XBUS_CS2`, `XBUS_SWITCH`, `XBUS_SWITCH_SWITCH`, `XBUS_SWITCH_J17_13`, `XBUS_SWITCH_J17_11`, `XBUS_SWITCH_J17_9`, `UNCACHEABLE_ADDR`, `PIC_LO`, `PIC_MASK_LO`, and 18 more.

### Control Flow
There is no executable control flow; consumers include the header or build metadata.

### State, Persistence, And Dependencies
Dependencies include none. Local/static state or exported register data includes none. Compatible strings or firmware/device-tree identifiers observed: none. There is no private runtime persistence in this header; it defines constants and declarations used by compiled platform code.

### Integration Points
Integration points are PCI host/fixup code. Callers should treat none as platform hooks rather than generic APIs when those symbols are visible.

### Risks
Primary risks include interrupt masking/wakeup regressions.

### Test Signals
Useful test signals include ARM build coverage for the relevant CONFIG symbols, interrupt storm, mask/unmask, and wake-capable IRQ tests, PCI enumeration and board-specific fixup checks, GPIO/LED state readback on target hardware. Source reading signal: 90 lines; 0 includes; 0 function/entry points; 42 macro/defines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-footbridge/include/mach/hardware.h -->
