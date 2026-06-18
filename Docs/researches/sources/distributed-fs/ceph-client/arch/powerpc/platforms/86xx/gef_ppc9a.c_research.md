# sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/gef_ppc9a.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/gef_ppc9a.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/gef_ppc9a.c

### Purpose
GE Fanuc/GE PPC9A 86xx board support. It initializes MPIC plus GE FPGA PIC cascade, SMP, PCI, board register reporting, and NEC USB PCI fixups.

### Important APIs, Types, And Functions
Key functions are `gef_ppc9a_init_irq()`, `gef_ppc9a_setup_arch()`, board revision helpers, `gef_ppc9a_show_cpuinfo()`, `gef_ppc9a_nec_fixup()`, and `define_machine(gef_ppc9a)`. It uses compatible `gef,fpga-pic-1.00` for cascaded interrupts and `DECLARE_PCI_FIXUP_HEADER()` for NEC USB.

### Control Flow
IRQ init calls `mpc86xx_init_irq()` and then initializes the FPGA PIC if the node exists. Setup initializes SMP, maps board registers, assigns primary PCI, and logs. The PCI fixup adjusts NEC USB registers only when `machine_is(gef_ppc9a)`.

### State, Persistence, And Dependencies
State includes mapped board registers, MPIC/GE PIC IRQ domains, SMP ops, PCI host assignment, and PCI config writes. No durable persistence. Dependencies include GE PIC support, OF, FSL PCI, and 86xx shared helpers.

### Integration Points
Connects GE board FPGA IRQs and USB controller quirks to standard 86xx platform infrastructure.

### Risks
PCI fixup must remain machine-gated to avoid modifying unrelated NEC devices. Board register mapping affects CPU info output.

### Test Signals
Boot PPC9A, verify FPGA interrupts, NEC USB operation, PCI enumeration, SMP, and `/proc/cpuinfo` board revisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/gef_ppc9a.c -->
