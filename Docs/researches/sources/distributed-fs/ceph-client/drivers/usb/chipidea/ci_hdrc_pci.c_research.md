# sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci_hdrc_pci.c

Purpose: provides PCI glue for ChipIdea controllers, turning supported PCI devices into `ci_hdrc` platform children and registering a generic NOP USB PHY.

Important APIs/types/functions: defines `struct ci_hdrc_pci`, static platform data variants for generic, Langwell, and Penwell devices, `ci_hdrc_pci_probe`, `ci_hdrc_pci_remove`, and a PCI ID table for MIPS/Intel devices.

Control flow: probe validates driver data, enables the PCI device with managed PCI helpers, checks IRQ, enables bus mastering/MWI, registers a generic PHY, builds MEM and IRQ resources from BAR0 and PCI IRQ, then calls `ci_hdrc_add_device`. Remove removes the child and unregisters the generic PHY.

State and persistence: stores child `ci` platform device and generic PHY platform device in PCI driver data. PCI resource state is managed by PCI core helpers.

Dependencies and integration: integrates with PCI core, generic USB PHY, ChipIdea platform add/remove, and static platform data describing cap offsets and power budget.

Risks: EHCI PCI driver may bind first unless IDs are bypassed there, as noted in the source. Generic PHY registration must be unwound on child-add failure. Platform data is static and shared, so it must not be mutated in instance-specific ways by consumers.

Test signals: PCI probe/remove, BAR/IRQ resource validation, generic PHY registration, Intel Langwell/Penwell cap-offset behavior, and coexistence with EHCI PCI driver binding rules.
