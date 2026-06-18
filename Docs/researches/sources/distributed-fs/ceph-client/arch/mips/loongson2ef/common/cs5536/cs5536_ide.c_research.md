# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/cs5536_ide.c

Purpose: virtualizes PCI configuration space for the CS5536 IDE controller.

Important APIs/functions: `pci_ide_write_reg` and `pci_ide_read_reg`.

Control flow: command writes control bus mastering through `GLIU_PAE`; BAR4 writes support sizing through soft flags or program IDE IO BAR plus GLIU IOD mapping; IDE config/timing/control/power registers map directly to IDE MSRs; a flash signature write toggles DIVIL ball options. Reads synthesize PCI identity/status/class/cache/BAR/capability/interrupt fields and return IDE MSR-backed control registers.

State and persistence: IDE, GLIU, GLCP, DIVIL, and SB MSRs store emulated PCI state.

Dependencies and integration: used by CS5536 VSM for IDE PCI config; integrates with Linux IDE/ATA probing.

Risks: only BAR4 is meaningful; incorrect IO range packing can break IDE register decoding. Flash-signature special case has hidden hardware side effects.

Test signals: IDE PCI config enumeration, BAR sizing/programming, timing register read/write, bus-master enable, and storage probe.
