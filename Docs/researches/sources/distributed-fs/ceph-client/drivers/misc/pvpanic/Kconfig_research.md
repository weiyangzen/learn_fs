# sources/distributed-fs/ceph-client/drivers/misc/pvpanic/Kconfig

Purpose: defines configuration switches for QEMU pvpanic support and its MMIO and PCI transport front ends.

Important symbols: `PVPANIC` is the bool parent option. `PVPANIC_MMIO` is tristate and depends on `HAS_IOMEM`, `(ACPI || OF)`, and `PVPANIC`. `PVPANIC_PCI` is tristate and depends on `PCI` and `PVPANIC`.

Control flow: build selection requires enabling the parent before either concrete transport can be built. Help text describes guest-to-host panic event notification.

State and persistence: no runtime state; it controls build inclusion.

Dependencies and integration points: drives `pvpanic/Makefile`, selecting shared `pvpanic.o` plus either transport object.

Risks and test signals: configuration tests should ensure transports cannot be selected without the parent and that MMIO honors ACPI/OF and IOMEM dependencies. Build matrix should include built-in and module combinations.
