# sources/distributed-fs/ceph-client/drivers/pci/setup-cardbus.c

## Purpose
`setup-cardbus.c` handles CardBus bridge resource sizing, config-space programming, kernel-parameter overrides, and two-pass bus-number assignment for CardBus bridges.

## Important APIs, types, and functions
It defines CardBus defaults (`DEFAULT_CARDBUS_IO_SIZE`, `DEFAULT_CARDBUS_MEM_SIZE`), mutable boot-parameter sizes `pci_cardbus_io_size` and `pci_cardbus_mem_size`, and the reserve count `CARDBUS_RESERVE_BUSNR`. Main functions are `pci_cardbus_resource_alignment()`, `pci_bus_size_cardbus_bridge()`, `pci_setup_cardbus_bridge()`, `pci_setup_cardbus()`, and `pci_cardbus_scan_bridge_extend()`.

## Control flow and behavior
Sizing reserves two I/O windows and one or two memory windows on the bridge. It clears `PCI_CB_BRIDGE_CTL_PREFETCH_MEM1`, probes and enables prefetch support for MEM0, and marks bridge resources with `IORESOURCE_STARTALIGN` for later assignment. If a realloc list is provided, it records optional future growth.

`pci_setup_cardbus_bridge()` translates assigned resources into bus-relative addresses and writes the CardBus I/O and memory base/limit registers. `pci_setup_cardbus()` parses `pci=cbiosize=` and `pci=cbmemsize=` options via `memparse()`. Scanning is two-pass: pass 0 disables forwarding with a temporary `PCI_PRIMARY_BUS` write; pass 1 clears status errors, honors Enhanced Allocation fixed bus numbers if present, creates or reuses a child bus, writes primary/secondary/subordinate numbers in one dword, reserves up to three additional bus numbers for future cards, updates the child bus resource, and validates the bus-number range.

## State and persistence
The persistent state is bridge config space, `bus->resource[]`, child `busn_res`, child name, and the global CardBus size tunables set by boot parameters. No private heap state is retained.

## Dependencies and integration points
It is called from `setup-bus.c` during bridge sizing and assignment. It depends on PCI bus-number helpers, resource translation, Enhanced Allocation bus-number discovery, and CardBus config register definitions.

## Risks
Wrong prefetch handling can misroute CardBus memory windows. Bus-number reservation must avoid existing bus numbers and firmware-assigned parent ranges. The fixed resource sizing is conservative but can waste scarce I/O or memory address space.

## Test signals
Test with CardBus bridges that support and do not support prefetchable memory, bridges with EA fixed bus numbers, hotplug scans where target bus numbers already exist, boot overrides for `cbiosize`/`cbmemsize`, and logs showing CardBus window programming.
