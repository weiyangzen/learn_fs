# sources/distributed-fs/ceph-client/drivers/pci/msi/msi.c

## Purpose
Owns the core PCI MSI/MSI-X lifecycle: support checks, descriptor construction, message programming, masking, enable/disable, restore, shutdown, IRQ vector freeing, TPH tag updates, and global MSI disable. It is the main implementation behind public PCI IRQ vector APIs.

## APIs, Types, And Functions
Exports `pci_msi_mask_irq()`, `pci_msi_unmask_irq()`, `pci_write_msi_msg()`, `pci_msi_vec_count()`, `msi_desc_to_pci_dev()`, and many GPL/common internal entry points declared in `msi.h`: `__pci_enable_msi_range()`, `__pci_enable_msix_range()`, `pci_msi_shutdown()`, `pci_msix_shutdown()`, `pci_free_msi_irqs()`, restore helpers, and `msix_prepare_msi_desc()`. Important helpers include `pci_msi_supported()`, `pci_setup_msi_context()`, `msi_setup_msi_desc()`, `__msi_capability_init()`, `msix_map_region()`, `msix_setup_msi_descs()`, and `msi_verify_entries()`.

## Control Flow
MSI enablement validates global/device/bus support, D0 power state, existing MSI-X state, vector ranges, irqdomain feature support, and available vector count. It installs MSI device data/devres cleanup, creates the device MSI domain, then loops reducing requested vectors when setup reports a smaller supported count. MSI setup builds one descriptor, masks all MSI bits, allocates IRQs, verifies assigned message addresses against the device address mask, disables INTx, enables MSI, frees the legacy INTx IRQ, and replaces `dev->irq`. MSI-X setup enables and masks MSI-X globally, maps the table, creates one descriptor per requested entry, allocates IRQs, updates user entries, masks stale table entries, clears global mask-all, and disables INTx. Restore paths rewrite saved messages and masks after resume; shutdown paths disable MSI/MSI-X, restore INTx, and reallocate legacy IRQs.

## State And Persistence
State lives in `pci_dev` flags (`msi_enabled`, `msix_enabled`, `msix_base`, `msi_cap`, `msix_cap`, `msi_addr_mask`, `is_msi_managed`), `msi_desc` PCI attributes, cached MSI masks/MSI-X vector control, saved `msi_msg`, and global `pci_msi_enable`. There is no disk persistence. Devres cleanup automatically frees vectors for managed PCI devices.

## Dependencies And Integration
Depends on config-space accessors, `irqdomain`, generic MSI core, PCI core IRQ allocation, `ioremap` for MSI-X tables, irq affinity helpers, and arch hooks such as `arch_restore_msi_irqs()`. It integrates with `irqdomain.c` for allocation/teardown and with `pcidev_msi.c` capability discovery performed during enumeration.

## Risks And Test Signals
High-risk areas are ordering of hardware enable bits versus descriptor allocation, masking/unmasking while editing MSI-X table entries, multi-MSI count encoding, partial allocation retry semantics, D0/disconnected-device checks, resource cleanup after failed MSI-X setup, and restore after suspend/kexec. Test signals include MSI/MSI-X vector allocation with affinity, multi-MSI, invalid duplicate MSI-X entries, virtual MSI-X entries, devices with 32-bit MSI address masks, hot unplug, runtime/system suspend-resume, `pci_no_msi`, and fault injection around `ioremap`, descriptor insertion, and IRQ allocation.
