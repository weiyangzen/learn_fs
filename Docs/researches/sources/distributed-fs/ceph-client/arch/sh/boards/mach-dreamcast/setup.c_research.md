<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-dreamcast/setup.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-dreamcast/setup.c

Purpose: This file supplies the Dreamcast machine-vector setup, including I/O port base configuration and System ASIC IRQ integration.

Important APIs/types/functions: It defines `dreamcast_setup` and `mv_dreamcast`.

Control flow: Setup sets the I/O port base to `P2SEG` because the GAPS PCI bridge uses P2-area relative addresses. The machine vector names the board and installs `systemasic_irq_demux` and `systemasic_irq_init`.

State and persistence: I/O port base configuration persists globally for port I/O translation. Machine-vector callbacks persist through boot.

Dependencies and integration points: It depends on SH address-space macros, generic I/O base setup, Dreamcast System ASIC IRQ functions, and SuperH machvec.

Risks and test signals: Incorrect I/O base breaks Dreamcast PCI/GAPS access. Tests include Dreamcast boot, PCI/device I/O access, System ASIC event IRQs, and machine-vector selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-dreamcast/setup.c -->
