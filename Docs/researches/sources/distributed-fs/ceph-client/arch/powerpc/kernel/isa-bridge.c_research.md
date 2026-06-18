# sources/distributed-fs/ceph-client/arch/powerpc/kernel/isa-bridge.c

## Purpose
Tracks and maps the legacy ISA I/O bridge on PowerPC systems, supporting early PHB discovery, non-PCI ISA bridges, late PCI bus notification, and removal.

## Important APIs, Types, And Functions
Exports `isa_io_base` and `isa_bridge_pcidev`. Public setup functions are `isa_bridge_find_early` and `isa_bridge_init_non_pci`. Internal helpers include `remap_isa_base`, `process_ISA_OF_ranges`, `isa_bridge_find_late`, `isa_bridge_remove`, `isa_bridge_notify`, and `isa_bridge_init`.

## Control Flow
Early discovery scans OF nodes of type `isa` under a PCI host bridge, parses I/O ranges, remaps the ISA I/O window at `ISA_IO_BASE`, and marks `isa_io_base` valid. Non-PCI setup does the same directly from a device node. Late PCI notifications attach a discovered PCI device to an existing early node or detect a newly added ISA bridge. Removal clears cached references and unmaps the fixed 64K ISA area.

## State And Persistence
State is global `isa_io_base`, cached `isa_bridge_devnode`, and `isa_bridge_pcidev`. The virtual mapping at `ISA_IO_BASE` persists while the bridge is registered. Device node and PCI references are runtime-only.

## Dependencies And Integration Points
Depends on Open Firmware range parsing, PCI host bridge data, early ioremap/vmap APIs, PCI bus notifiers, ISA bridge helpers used by `iomap.c`, and platform code that calls early discovery while adding PHBs.

## Risks And Edge Cases
Risks include non-page-aligned OF ranges, missing or malformed `ranges`, multiple ISA bridges where only one global bridge is tracked, hot removal of a bridge used by legacy drivers, and the suspicious removal path leaving `isa_io_base` set to `ISA_IO_BASE` rather than clearing to zero. Fallback mapping of 64K from PHB base is only a compatibility path.

## Test Signals
Signals include boot on systems with legacy ISA devices, OF range parsing logs, successful port I/O through `ioport_map`, PCI hotplug notifier behavior, bridge removal/unmap tests where hardware supports it, and malformed device-tree range tests.
