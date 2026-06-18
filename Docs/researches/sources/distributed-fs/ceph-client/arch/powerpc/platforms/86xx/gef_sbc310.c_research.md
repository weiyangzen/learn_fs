# sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/gef_sbc310.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/gef_sbc310.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/gef_sbc310.c

### Purpose
GE SBC310 86xx board support. It is similar to other GE 86xx boards, combining MPIC, FPGA PIC cascade, SMP, PCI setup, board register reporting, and NEC USB fixup behavior.

### Important APIs, Types, And Functions
Functions include `gef_sbc310_init_irq()`, `gef_sbc310_setup_arch()`, board/FPGA revision helpers, `gef_sbc310_show_cpuinfo()`, PCI fixup logic, and `define_machine(gef_sbc310)`. It uses GE FPGA PIC compatible matching and FSL PCI helpers.

### Control Flow
Machine setup maps board registers, initializes SMP and primary PCI, and logs board details. IRQ init initializes MPIC and optional FPGA PIC. PCI fixup is machine-gated and writes NEC USB controller config registers.

### State, Persistence, And Dependencies
Runtime state includes mapped board register pointer, IRQ domains, PCI config changes, SMP ops, and platform devices. No durable persistence. Dependencies include OF, GE PIC, MPIC, FSL PCI, and 86xx common publication.

### Integration Points
Integrates GE board management FPGA and USB quirks with normal Linux IRQ/PCI/platform subsystems.

### Risks
Wrong board register interpretation misreports hardware; wrong cascade setup breaks FPGA interrupt consumers; ungated PCI fixup would affect non-board systems.

### Test Signals
Boot SBC310, verify FPGA interrupt children, board revision output, USB behavior, PCI enumeration, SMP, and common device publication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/gef_sbc310.c -->
