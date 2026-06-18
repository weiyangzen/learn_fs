# sources/distributed-fs/ceph-client/arch/x86/include/asm/pci-functions.h

Purpose: provides conventional PCI BIOS function numbers for legacy PC BIOS interrupt/service interfaces.

Important APIs, types, and functions: defines constants such as `PCIBIOS_PCI_FUNCTION_ID`, `PCIBIOS_PCI_BIOS_PRESENT`, `PCIBIOS_FIND_PCI_DEVICE`, `PCIBIOS_FIND_PCI_CLASS_CODE`, special cycle generation, config byte/word/dword reads and writes, routing options, and interrupt assignment functions.

Control flow: there is no code. Legacy PCI BIOS callers use these constants when invoking BIOS services or decoding requests.

State and persistence: no state is owned. BIOS calls using these identifiers may read or modify firmware-managed PCI state.

Dependencies and integration points: consumed by `CONFIG_PCI_BIOS` x86 code and any compatibility logic that still talks to conventional PCI BIOS functions.

Risks: constants are firmware ABI values and must not be changed. This path is legacy but can matter on old systems without robust ACPI/MMCONFIG/direct PCI setup.

Test signals: build `CONFIG_PCI_BIOS`, boot legacy BIOS systems or emulators, validate `pci_pcbios_init()` detects BIOS presence and can read/write config space and routing information using these function IDs.
