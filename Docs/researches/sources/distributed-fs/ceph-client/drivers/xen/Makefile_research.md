# sources/distributed-fs/ceph-client/drivers/xen/Makefile

## Purpose
This Makefile maps Xen Kconfig symbols and architecture conditions to built objects and subdirectories.

## Important APIs, types, and functions
It uses kbuild variables such as `obj-y`, `obj-$(CONFIG_...)`, composite object lists, and architecture-conditioned `dom0-*` lists. Always-built Xen core objects include grant table, features, balloon, manage, time, mem reservation, events, and xenbus. Conditional objects cover CPU hotplug, Dom0 platform helpers, block bio merge, event-channel device, grant devices, xenfs, sys-hypervisor, platform PCI, SWIOTLB, mcelog, pciback, privcmd, ACPI processor, EFI, scsiback, pv calls, xlate MMU, front shared buffers, unpopulated alloc, and grant DMA.

## Control flow
Kbuild evaluates configuration variables and descends into `events/`, `xenbus/`, `xenfs/`, and `xen-pciback/` as appropriate. Composite variables map module names such as `xen-evtchn`, `xen-gntdev`, `xen-gntalloc`, and `xen-privcmd` to their constituent objects.

## State and persistence
The Makefile has no runtime state; it creates build graph state from `.config`.

## Dependencies and integration points
It links the Kconfig menu to the actual Xen driver implementation files and architecture-specific Dom0 helpers.

## Risks and test signals
Risks include stale object names, architecture conditional mismatches, unconditional core objects lacking dependencies, and module composition drift. Test signals include Xen disabled/enabled builds, Dom0 ARM64 and x86 builds, `CONFIG_BLOCK=n`, modular grant/privcmd/xenfs options, and `make W=1` for orphaned objects.
