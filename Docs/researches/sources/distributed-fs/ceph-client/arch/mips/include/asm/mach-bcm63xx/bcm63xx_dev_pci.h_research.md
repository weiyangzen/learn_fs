# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_dev_pci.h

**Purpose:** Publishes BCM63xx PCI enable state.

**Important APIs/types/functions:** Exports `extern int bcm63xx_pci_enabled`.

**Control flow:** Board and PCI setup code read or set this flag to decide whether to initialize PCI resources and register PCI devices.

**State and persistence behavior:** The extern integer is global boot-time state owned by implementation code. It persists after detection/setup and gates PCI availability.

**Dependencies and integration points:** Integrated by BCM63xx PCI host code, board setup, and possibly bootloader/NVRAM configuration.

**Risks:** A stale or incorrect enabled flag can skip real PCI hardware or probe absent/disabled hardware. The header exposes mutable global state without accessor validation.

**Test signals:** Boot PCI-capable and non-PCI boards, verify flag value, PCI host registration, resource windows, enumeration, and disabled-board behavior.
