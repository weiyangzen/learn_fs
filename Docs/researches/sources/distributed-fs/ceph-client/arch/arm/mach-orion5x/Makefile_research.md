<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/Makefile

### Purpose
`Makefile` selects Orion5x common, PCI, IRQ, MPP, and board setup objects for the kernel build.

### Important APIs, Types, And Functions
It always builds `common.o`, `pci.o`, `irq.o`, and `mpp.o`, and conditionally builds board setup objects based on `CONFIG_MACH_*` and `CONFIG_ARCH_ORION5X_DT`.

### Control Flow
There is no runtime flow. Build inclusion follows Kconfig symbols; TS209/TS409 also include shared `tsx09-common.o`.

### State, Persistence, And Dependencies
The file has no runtime state. It adds the legacy `plat-orion/include` path through `ccflags-y`.

### Integration Points
It connects Kconfig board selections to actual compiled machine and DT support.

### Risks
Selecting the same setup object for multiple machines, such as Kurobox Pro and Linkstation Pro, requires preprocessor guards inside the C file to avoid unintended machine descriptors.

### Test Signals
Build matrix should include each board config to verify expected object inclusion and no missing shared objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/Makefile -->
