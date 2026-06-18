<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/serial.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/serial.h

Purpose: declares x86 legacy serial-port defaults and early serial support constants. Important content includes UART base/IRQ defaults and `BASE_BAUD` configuration used by 8250/legacy serial setup.

Control flow: serial core and early console setup consume these constants when probing standard PC COM ports. State is owned by serial drivers and platform resources. Dependencies include legacy ISA I/O port layout and serial driver configuration.

Risks: wrong defaults break early console or legacy serial devices; modern platforms often use firmware-described ports, so this file must remain conservative. Test signals include earlyprintk/earlycon on COM ports, 8250 probe, ISA serial devices, and builds with/without serial support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/serial.h -->
