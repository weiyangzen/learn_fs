# sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/gef_sbc610.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/gef_sbc610.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/gef_sbc610.c

### Purpose
GE SBC610 86xx board support. It initializes core 86xx interrupt/SMP/PCI subsystems, maps board FPGA registers, exposes CPU info, and applies NEC USB host fixups.

### Important APIs, Types, And Functions
Important functions are `gef_sbc610_init_irq()`, `gef_sbc610_setup_arch()`, `gef_sbc610_get_pcb_rev()`, `gef_sbc610_get_board_rev()`, `gef_sbc610_get_fpga_rev()`, `gef_sbc610_show_cpuinfo()`, `gef_sbc610_nec_fixup()`, and `define_machine(gef_sbc610)`.

### Control Flow
IRQ init calls common 86xx MPIC init, finds `gef,fpga-pic`, and initializes the GE PIC cascade. Setup maps `gef,sbc610-fpga-regs`, initializes SMP, assigns PCI, and logs. The PCI fixup adjusts NEC USB registers only on this machine.

### State, Persistence, And Dependencies
State includes `sbc610_regs`, interrupt domains, PCI configuration changes, SMP ops, and platform devices. No durable data. Dependencies include OF, GE PIC, MPIC, FSL PCI, and common 86xx device publication.

### Integration Points
Provides board-management FPGA and USB-controller integration for Linux drivers on the SBC610.

### Risks
Register mapping failure changes CPU info and may hide board revision diagnostics. Interrupt cascade and PCI fixup must stay board-specific.

### Test Signals
Boot SBC610, check board/PCB/FPGA revision output, FPGA IRQ delivery, NEC USB, PCI, SMP, and OF devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/gef_sbc610.c -->
