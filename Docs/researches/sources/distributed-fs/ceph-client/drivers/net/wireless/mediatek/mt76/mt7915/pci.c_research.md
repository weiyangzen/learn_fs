# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/pci.c

## Purpose

`pci.c` is the PCI probe/remove layer for MT7915/MT7916 primary devices and auxiliary HIF devices. It matches PCI IDs, enables and maps BAR0, configures DMA and IRQ resources, discovers/links the optional second HIF, initializes the MMIO device, optionally attaches WED, requests primary and secondary interrupts, enables PCIe interrupt master switches, and calls `mt7915_register_device()`.

## Important APIs, Types, and Functions

- `mt7915_pci_device_table` matches primary devices `0x7915` and `0x7906`.
- `mt7915_hif_device_table` matches auxiliary HIF devices `0x7916` and `0x790a`.
- Static globals `hif_list`, `hif_lock`, and `hif_idx` coordinate discovery of a second PCI function/device used as HIF2.
- `mt7915_pci_get_hif2()` scans registered HIF devices for a recognition ID, takes a device reference, and returns the matching `struct mt7915_hif`.
- `mt7915_pci_init_hif2()` increments a global recognition index, writes it to the primary BAR recognition register with semaphore bit, and tries to find the matching auxiliary HIF.
- `mt7915_pci_hif2_probe()` creates and registers a lightweight `mt7915_hif` object for auxiliary devices.
- `mt7915_pci_probe()` handles both auxiliary and primary probe paths.
- `mt7915_hif_remove()` removes auxiliary HIF objects from the global list.
- `mt7915_pci_remove()` releases HIF2 and unregisters the primary device.
- `mt7915_hif_driver` and `mt7915_pci_driver` are exported to `mmio.c` module init.

## Control Flow

Both PCI drivers use `mt7915_pci_probe()`. The function first enables the PCI device with managed helpers, maps BAR0, sets bus mastering, enforces a 32-bit DMA mask, and disables ASPM through mt76. If the matched ID is an auxiliary HIF ID, it stops there and calls `mt7915_pci_hif2_probe()` to allocate a list entry, record BAR0 and IRQ, and set drvdata.

For primary IDs, the probe calls `mt7915_mmio_probe()` to allocate and initialize the mt76/mt7915 device, resets WFSYS, and tries to initialize HIF2. It then calls `mt7915_mmio_wed_init()`. A positive return means WED attached and supplied an IRQ/DMA device. A zero return means normal PCI IRQ vectors are allocated and HIF2 detection is retried. The primary IRQ is requested with `mt7915_irq_handler`, PCIe MAC interrupts are enabled, and if HIF2 exists, `dev->hif2` is set, secondary interrupt masks are cleared, the correct secondary PCIe interrupt master switch is enabled, and a secondary IRQ is requested.

The final step is `mt7915_register_device(dev)`, which performs the broader driver registration outside this file. Error paths unwind in reverse: secondary IRQ/device reference, primary IRQ, WED detach or PCI vector free, and mt76 device free.

Remove is shorter. Auxiliary remove deletes the HIF list node. Primary remove drops the HIF2 device reference and calls `mt7915_unregister_device()`.

## State and Persistence Behavior

Persistent runtime state includes the global auxiliary HIF list and recognition index, `struct mt7915_hif` objects stored in managed PCI device memory, primary `dev->hif2` references, PCI drvdata, IRQ registrations, and WED/IRQ-vector state. None of this is stored across module unload or device removal.

`mt7915_pci_get_hif2()` uses `get_device()` to hold the auxiliary device while associated with a primary device; `mt7915_put_hif2()` releases it. The recognition ID written into primary BAR0 is a hardware coordination mechanism for matching the primary and auxiliary functions.

## Dependencies and Integration Points

`pci.c` integrates with Linux PCI core, DMA API, IRQ management, and module firmware declarations. It depends on `mmio.c` for `mt7915_mmio_probe()`, `mt7915_mmio_wed_init()`, and `mt7915_irq_handler()`, on reset/register helpers for `mt7915_wfsys_reset()`, on registration code for `mt7915_register_device()`/`mt7915_unregister_device()`, and on mt76 PCI helpers such as `mt76_pci_disable_aspm()`.

The file declares firmware dependencies for MT7915 and MT7916 primary devices through `MODULE_FIRMWARE()`. MT798x firmware declarations are handled outside this PCI-specific file.

## Risks and Edge Cases

- HIF2 pairing relies on a global incrementing `hif_idx` and recognition register value. Concurrent probes and stale auxiliary entries require correct locking and device references.
- `mt7915_hif_remove()` removes from `hif_list` without an explicit lock in this file, while lookup uses `hif_lock`; this deserves care if removal can race lookup.
- WED initialization changes the cleanup branch. If WED attaches, PCI IRQ vectors may not have been allocated and cleanup must call `mtk_wed_device_detach()`.
- HIF2 is attempted before and after WED initialization in the non-WED path; behavior depends on auxiliary device probe timing.
- Error labels must distinguish `dev->hif2` from local `hif2`; a local HIF reference that has not been assigned to `dev->hif2` can be leaked if future changes add failures between lookup and assignment.
- Interrupt master switch writes are chip-specific for secondary PCIe; using the wrong register on MT7916-class devices would break HIF2 interrupts.

## Test Signals

Validation should include primary-only probe, dual-HIF probe with auxiliary devices appearing before and after primary, WED-enabled and WED-disabled probe, IRQ delivery on primary and secondary HIF, clean failure injection at BAR map, DMA mask, WED init, IRQ request, and register-device stages, module unload/reload, and remove while associated stations/traffic exist. Expected signals are proper firmware requests, one registered mac80211 device per primary, no leaked HIF device references, no stale HIF list entries, traffic on both bands when HIF2 is present, and clean WED detach or PCI vector free on failure/remove.
