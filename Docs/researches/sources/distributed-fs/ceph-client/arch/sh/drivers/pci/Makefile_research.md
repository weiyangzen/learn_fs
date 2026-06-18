# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/Makefile



Source read size: 27 lines, 1181 bytes.



Purpose: object selection for SH PCI and PCIe host controller support plus board fixups.

Important APIs/types/functions: always builds `common.o` and `pci.o`; CPU subtype selects SH7751, SH7780/SH7763/SH7785, or SH7786 PCIe controller code; board symbols select IRQ/resource fixups.

Control flow: Kbuild links generic core plus exactly the CPU controller ops and any board-specific fixup files needed by the configured machine.

State and persistence: build-time object graph only.

Dependencies and integration points: ties CPU Kconfig, board Kconfig, PCI host bridge registration, and platform IRQ maps.

Risks and test signals: missing fixup object leaves weak/default IRQ or PCIC setup. Test every board defconfig with PCI enabled.
