# sources/distributed-fs/ceph-client/arch/powerpc/platforms/amigaone/setup.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/amigaone/setup.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/amigaone/setup.c

### Purpose
Eyetech AmigaOne platform setup for MAI Logic Articia S based systems. It discovers PCI host bridges, initializes interrupts, reserves ISA I/O regions, handles restart, and registers the machine descriptor.

### Important APIs, Types, And Functions
Key functions are `amigaone_show_cpuinfo()`, `amigaone_add_bridge()`, `amigaone_setup_arch()`, `amigaone_discover_phbs()`, `amigaone_init_IRQ()`, `request_isa_regions()`, `amigaone_probe()`, `amigaone_restart()`, and `define_machine(amigaone)` with compatible `eyetech,amigaone`.

### Control Flow
Probe selects the platform. Setup discovers PCI host bridges compatible with `mai-logic,articia-s`, creates PCI controllers, and logs board info. IRQ init finds the interrupt controller and Articia PCI node and initializes interrupt routing. A machine device initcall reserves legacy ISA regions. Restart disables interrupts and performs the board reset sequence.

### State, Persistence, And Dependencies
State includes PCI controller objects, IRQ controller state, reserved I/O regions, and restart side effects. No durable storage. Dependencies include OF, PCI bridge APIs, interrupt setup, ioport resources, and udbg progress.

### Integration Points
Connects AmigaOne firmware/device tree to Linux PCI, ISA resource, interrupt, and machine callback infrastructure.

### Risks
Legacy PCI/ISA assumptions are fragile. Resource reservation conflicts or bridge discovery failures can break device enumeration.

### Test Signals
Boot AmigaOne, verify PCI host bridges, ISA I/O reservations, interrupts, restart, and `/proc/cpuinfo` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/amigaone/setup.c -->
