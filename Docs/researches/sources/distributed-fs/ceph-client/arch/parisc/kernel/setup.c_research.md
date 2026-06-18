<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/setup.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/setup.c

### Purpose
`setup.c` handles early PA-RISC architecture boot setup, command-line construction, memory/cache/paging initialization, resource registration, and the final handoff into `start_kernel()`.

### Important APIs, Types, And Functions
Key routines are `setup_cmdline()`, `setup_arch()`, `parisc_init_resources()`, `parisc_init()`, `start_parisc()`, and `cpuinfo_op` sequence callbacks.

### Control Flow
Early boot validates initial kernel mappings, detects QEMU/SeaBIOS, initializes topology and FP, initializes trap vectors, then calls `start_kernel()`. `setup_arch()` initializes unwind data, per-CPU modes, PDC, command line/default console/earlycon, boot CPU data, memory inventory, caches, paging, and scheduler clock stability. Later `parisc_init()` claims bus resources, inventories devices, sets chassis state and OS ID, flushes local caches/TLB, registers CPUs, applies alternatives, and calibrates cache timing.

### State, Persistence, And Dependencies
Boot command line, initrd bounds, resource reservations, `running_on_qemu`, topology, and boot CPU data persist. Dependencies include PDC, PAGE0 firmware data, cache/TLB setup, memory inventory, alternatives, proc cpuinfo, and SMP.

### Integration Points
Called by architecture entry code and generic initcall flow; provides `/proc/cpuinfo` sequencing through `cpuinfo_op`.

### Risks
Command-line defaults can affect console availability. Early mapping warnings occur before printk is reliable. Init ordering matters because PDC, traps, memory inventory, and paging depend on one another.

### Test Signals
Boot with/without bootloader command line, initrd, QEMU marker, serial/graphics console autodetect, large kernels near initial mapping limits, SMP, and resource reservation conflicts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/setup.c -->
