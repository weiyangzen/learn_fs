<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/n64/Makefile -->
## sources/distributed-fs/ceph-client/arch/mips/n64/Makefile

### Purpose
`n64/Makefile` builds Nintendo 64 platform initialization and IRQ support.

### Important APIs, Types, And Functions
It sets `obj-y := init.o irq.o`.

### Control Flow
When the N64 platform is selected, Kbuild links both objects into the kernel.

### State, Persistence, And Dependencies
Build state is the linked platform support objects. Dependencies are the surrounding MIPS platform Kbuild selection.

### Integration Points
The Makefile connects `init.c` platform setup and `irq.c` CPU IRQ initialization to the kernel build.

### Risks
No conditional object selection is present; any missing dependency must be handled by the C files or platform Kconfig.

### Test Signals
Build the N64 platform and verify both platform hooks link.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/n64/Makefile -->
