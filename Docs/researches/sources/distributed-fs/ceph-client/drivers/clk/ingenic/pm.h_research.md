# sources/distributed-fs/ceph-client/drivers/clk/ingenic/pm.h Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/pm.h -->
## sources/distributed-fs/ceph-client/drivers/clk/ingenic/pm.h

### Purpose
`pm.h` is the small interface between Ingenic SoC CGU drivers and the shared syscore PM helper.

### Important APIs, Types, And Functions
It forward-declares `struct ingenic_cgu` and declares `ingenic_cgu_register_syscore(struct ingenic_cgu *cgu)`.

### Control Flow, State, And Persistence
The header carries no runtime state. It lets each SoC-specific `*-cgu.c` file register the shared suspend/resume low-power-mode hook after the common CGU object is created.

### Dependencies, Integration Points, Risks, And Test Signals
Its integration point is narrow but important: every Ingenic CGU driver includes it to opt into the PM hook. Risks are mostly declaration drift if the implementation changes. Test signals are compile coverage of all SoC CGU files and PM suspend/resume paths using the registered syscore ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/pm.h -->
