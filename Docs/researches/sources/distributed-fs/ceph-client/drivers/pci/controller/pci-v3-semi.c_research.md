# sources/distributed-fs/ceph-client/drivers/pci/controller/pci-v3-semi.c

## Purpose
`pci-v3-semi.c` drives the V3 Semiconductor V360EPC PCI local-bus-to-PCI bridge, notably on ARM Integrator/AP systems. It programs local-bus windows for PCI memory, I/O, config cycles, inbound DMA ranges, error interrupts, FIFO policy, and reset sequencing for a legacy non-ECAM host bridge.

## Important APIs, Types, And Functions
`struct v3_pci` stores device/MMIO state, config window base, non-prefetchable and prefetchable local memory windows, bus addresses, and optional Integrator syscon regmap. `v3_pci_ops` provides `v3_map_bus()`, `v3_pci_read_config()`, and `v3_pci_write_config()`. `v3_pci_probe()` allocates the host bridge, enables the clock, maps controller/config resources, installs the error IRQ, programs bridge windows, parses `dma-ranges`, handles Integrator-specific reset/syscon setup, and calls `pci_host_probe()`.

## Control Flow, State, And Persistence
Config access temporarily repurposes local-bus window 1 for PCI config cycles. `v3_map_bus()` expands non-prefetchable memory window 0 to 512 MiB, maps window 1 to config space, returns the config address, and then read/write wrappers call `v3_unmap_bus()` to restore window 1 as prefetchable memory and shrink window 0 back to 256 MiB. Probe disables PCI slave access, asserts reset, enables retry, configures endianness/byte-enable mode, programs outbound windows from host bridge resources, programs up to two inbound DMA windows, enables interrupts, deasserts reset, and locks the system register. Hardware state is volatile and reprogrammed only on probe; the driver has no PM hooks.

## Dependencies, Integration Points, Risks, And Test Signals
The driver depends on OF PCI host resources, `dma-ranges`, host bridge allocation, clocks, platform IRQs, syscon/regmap for `"arm,integrator-ap-syscon"`, and generic PCI config helpers. It expects exact 256 MiB prefetchable/non-prefetchable windows, a 16 MiB config resource, and at most two inbound DMA mappings. Risks include temporary window remapping, strict resource geometry, and invalid DMA range encodings. Test subordinate-bus config cycles, normal memory traffic after config reads, I/O and memory window decoding, interrupt logs for abort/parity cases, and Integrator reset/mailbox initialization.
