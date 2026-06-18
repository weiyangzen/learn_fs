# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/cs5536_ehci.c

Purpose: virtualizes PCI configuration space for the CS5536 EHCI USB function.

Important APIs/functions: `pci_ehci_write_reg` and `pci_ehci_read_reg`.

Control flow: command writes update EHCI MSR memory/bus-master bits; status writes clear parity error flags; BAR0 writes either set the soft sizing flag or program EHCI base and GLIU P2D mapping; EHCI legacy SMI and frame-length adjustment registers map into EHCI MSR high bits. Reads synthesize standard PCI header fields plus EHCI-specific legacy status and FLADJ values.

State and persistence: EHCI USB MSRs, GLIU mapping registers, southbridge error state, and soft BAR flags.

Dependencies and integration: used by CS5536 VSM PCI dispatcher for the EHCI function; integrates with USB EHCI driver enumeration.

Risks: memory BAR handling must preserve MMIO vs IO-space semantics. Legacy SMI bit masks are partial and must match hardware layout.

Test signals: EHCI PCI enumeration, BAR sizing/programming, USB host controller probe, parity status clearing, and legacy register access tests.
