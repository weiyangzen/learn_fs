# sources/distributed-fs/ceph-client/include/xen/platform_pci.h

## Purpose
`platform_pci.h` defines Xen platform PCI I/O port offsets, magic/product/version values, unplug command bits for emulated disks/NICs, and config-dependent helpers for deciding whether PV devices require unplugging legacy emulation.

## Important APIs, Types, and Functions
Constants include `XEN_IOPORT_MAGIC_VAL`, `XEN_IOPORT_LINUX_PRODNUM`, `XEN_IOPORT_LINUX_DRVVER`, `XEN_IOPORT_*` offsets, `XEN_UNPLUG_ALL_IDE_DISKS`, `XEN_UNPLUG_ALL_NICS`, `XEN_UNPLUG_AUX_IDE_DISKS`, `XEN_UNPLUG_ALL`, `XEN_UNPLUG_UNNECESSARY`, and `XEN_UNPLUG_NEVER`. Inline helpers include `xen_must_unplug_nics()`, `xen_must_unplug_disks()`, and PV-device presence stubs/externs.

## Control Flow
PVHVM platform PCI code probes the magic port, writes driver/product version data, and may write unplug bits to remove emulated IDE/NIC devices when Xen PV frontends are available. Inline helpers compile the unplug policy from frontend and PVHVM config options.

## State and Persistence Behavior
I/O port writes change Xen platform-device emulation state during boot. Presence queries report runtime detection of PV and legacy devices; this header itself holds no state.

## Dependencies and Integration Points
It integrates Xen PVHVM boot, platform PCI driver code, blkfront/netfront availability, and legacy device unplug sequencing.

## Risks and Test Signals
Risks include unplugging legacy devices before PV frontends are usable, duplicate disks/NICs if unplug fails, config-dependent helpers returning unexpected defaults, and I/O width mistakes on shared offsets. Test signals include PVHVM boots with block/net frontends built-in and modular, mixed legacy/PV disk detection, and platform PCI magic/version probe.
