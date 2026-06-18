<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/quirks.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/quirks.c

Purpose: PnP device fixups for firmware/resource descriptions known to be incomplete or harmful.

Important APIs/types/functions: quirk functions adjust SoundBlaster/AWE32/CMI8330/AD1815 options, clone dependent sets with optional IRQs, disable PnP resources overlapping PCI BARs, add AMD MMCONFIG reservations, and extend Intel MCH PNP0C02 resources. `pnp_fixups[]` maps PnP IDs to fixup functions; `pnp_fixup_device()` runs matching quirks during device add.

Control flow: after a backend parses a device, core calls `pnp_fixup_device()`. The function compares IDs and invokes all matching quirks. Quirks mutate option lists or current resources in place, sometimes allocating cloned options and adding resources.

State/persistence: mutates `dev->options` and `dev->resources` before driver binding/resource assignment. Added resources/options persist with the device until freed by normal PnP release.

Dependencies/integration: PnP option/resource helpers, PCI enumeration/resource APIs, AMD northbridge helper when enabled, and ID matching with wildcard support.

Risks: quirks are hardware-specific and can overfit old firmware behavior. PCI overlap quirk disables only partial overlaps, preserving bridge-enclosing resources. Cloning dependent sets can partially succeed on allocation failure and leave earlier clones. Intel MCH quirk depends on host bridge IDs and config registers.

Test signals: devices matching each fixup ID, PCI overlap scenarios, AMD MMCONFIG partial coverage, Intel MCH 16 KiB-to-32 KiB extension, allocation failure in clone paths, and nonmatching devices remaining unchanged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/quirks.c -->
