# sources/distributed-fs/ceph-client/drivers/pci/devres.c

## Purpose
Provides device-managed PCI resource helpers for config-space remapping, IO-space remapping, device enable/disable, INTx state restore, memory-write-invalidate, BAR region requests, BAR mappings, ranged mappings, and legacy `pcim_iomap_table()` compatibility.

## Important APIs, Types, And Functions
Exports include `devm_pci_remap_iospace()`, `devm_pci_remap_cfgspace()`, `devm_pci_remap_cfg_resource()`, `pcim_set_mwi()`, `pcim_intx()`, `pcim_enable_device()`, `pcim_pin_device()`, `pcim_iomap_table()`, `pcim_iomap()`, `pcim_iounmap()`, `pcim_iomap_region()`, `pcim_iounmap_region()`, `pcim_iomap_regions()`, `pcim_request_region()`, `pcim_request_all_regions()`, and `pcim_iomap_range()`. Key internal records are `pcim_iomap_devres`, `pcim_intx_devres`, and `pcim_addr_devres`.

## Control Flow
Managed helpers allocate devres records before requesting resources or creating mappings. Release callbacks later unmap IO, release BAR regions, restore INTx, clear MWI, or disable devices. Modern APIs track each request/mapping in `pcim_addr_devres`; deprecated whole-BAR APIs also update the legacy iomap table so old callers can retrieve BAR mappings.

## State And Persistence
State is attached to `struct device` devres stacks. `pcim_enable_device()` sets `pdev->is_managed` and restore action, while `pcim_pin_device()` prevents automatic disable. Region/mapping records persist until detach or explicit release. The legacy iomap table persists as a devres object for compatibility.

## Dependencies And Integration Points
Depends on PCI core resource APIs, generic devres, ioremap helpers, `pci_iomap*`, `pci_request_region*`, `pci_enable_device()`, and PCI command-register INTx behavior. Used broadly by PCI drivers for failure-safe probe cleanup.

## Risks
Mixing deprecated whole-BAR table APIs with ranged mappings can confuse callers if they expect all mappings in the table. `pcim_iomap()` returns NULL while newer helpers return `IOMEM_ERR_PTR`, so callers must match conventions. Manual release must use the matching pcim helper or devres records remain inconsistent.

## Test Signals
Probe-error injection should release requested BARs and mappings. Driver detach should restore INTx, clear MWI, and disable unpinned devices. Validate `pcim_iomap_table()` compatibility, invalid BAR rejection, ranged mapping release, and repeated request/unmap cycles.
