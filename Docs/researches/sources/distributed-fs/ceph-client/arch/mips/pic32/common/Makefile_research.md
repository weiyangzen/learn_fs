## sources/distributed-fs/ceph-client/arch/mips/pic32/common/Makefile

### Purpose
This Makefile builds the common PIC32 reset and IRQ initialization objects.

### Important APIs, Types, And Functions
It unconditionally builds `reset.o` and `irq.o` whenever the parent PIC32 common directory is selected.

### Control Flow
There is no runtime flow. The parent Makefile controls entry into this directory.

### State, Persistence, And Dependencies
No runtime state exists. The build assumes all PIC32 machine variants need these common hooks.

### Integration Points
The objects provide `arch_init_irq()` and reboot/poweroff hook setup for the PIC32 platform.

### Risks
If a future PIC32 variant uses a different IRQ or reset mechanism, unconditional inclusion may be too broad.

### Test Signals
Build logs should show `reset.o` and `irq.o` for `CONFIG_MACH_PIC32`; boot should reach IRQ initialization and reboot hooks.
