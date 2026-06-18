# sources/distributed-fs/ceph-client/drivers/xen/pci.c

Purpose: notifies Xen about PCI device add/remove/reset events in dom0, reserves MMCONFIG regions with Xen, and tracks optional device-domain ownership metadata.

Important APIs/functions: exports `xen_reset_device`, and under dom0 support exports `xen_find_device_domain_owner`, `xen_register_device_domain_owner`, and `xen_unregister_device_domain_owner`. Internal notifier paths use `xen_add_device`, `xen_remove_device`, `xen_pci_notifier`, and `xen_mcfg_late`.

Control flow: an arch initcall registers a PCI bus notifier only in the initial domain. On device add, the driver first reserves MCFG regions once, validates the PCI segment fits Xen's 16-bit hypercall ABI, then prefers `PHYSDEVOP_pci_device_add` with segment/bus/devfn, SR-IOV, ARI, and optional ACPI proximity data. If unsupported, it falls back to legacy manage-pci hypercalls for segment zero. Remove mirrors this with `PHYSDEVOP_pci_device_remove` or legacy removal. Reset sends `PHYSDEVOP_pci_device_reset` with FLR.

State and persistence: `pci_seg_supported` tracks whether the modern segment-aware hypercall is available. A dom0-only spinlocked list maps PCI devices to owning domains when registered by other code.

Dependencies and integration: depends on Linux PCI/ACPI notifier infrastructure, Xen physdev hypercalls, SR-IOV/ARI support, x86 MMCONFIG state, and Xen passthrough/MSI setup.

Risks: unsupported or oversized segments cannot be represented to Xen; failed add/remove can break passthrough or MSI/MSI-X; fallback paths lose nonzero segment support; domain owner list lifetime depends on callers unregistering before PCI device teardown.

Test signals: hot-add/remove PCI devices in dom0, SR-IOV virtual functions, ARI devices, nonzero segments, MMCONFIG reservation reporting, FLR reset notification, and owner register/find/unregister concurrency.
