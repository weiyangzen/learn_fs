<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci_sriov.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci_sriov.c

## Purpose

`xe_pci_sriov.c` implements the Xe PCI SR-IOV configure callback for PF devices. It provisions or unprovisions virtual functions, keeps the PF awake while VFs exist, sizes VF local-memory BARs, links PF/VF devices for resume ordering, and toggles GuC engine-activity accounting for PF/VF functions.

## Important APIs and Functions

The public entry point is `xe_pci_sriov_configure(struct pci_dev *pdev, int num_vfs)`, installed in `struct pci_driver.sriov_configure`. `xe_pci_sriov_get_vf_pdev()` resolves a 1-based VF ID to a referenced VF `pci_dev`. Private helpers reset VFs, create device links, enable engine activity function stats, choose VF LMEM BAR size, arm/disarm the PF guard, and perform `pf_enable_vfs()`/`pf_disable_vfs()`.

## Control Flow and State

`xe_pci_sriov_configure()` validates PF mode, bounds, and existing VFs, then takes a scoped runtime PM reference. Enabling waits for PF readiness, arms a guard against conflicting VF enabling, takes a noresume PM reference that persists for the VF lifetime, provisions VFs, optionally sizes VF LMEM BAR for dGFX, calls `pci_enable_sriov()`, links devices for resume order, creates sysfs links, and enables per-function engine activity stats. Failure unprovisions and drops the PM reference. Disabling reverses stats, sysfs links, PCI SR-IOV, VF reset, provisioning, PM reference, and guard.

## Dependencies and Integration Points

It depends on Linux PCI IOV APIs, Xe SR-IOV PF provisioning/control/sysfs helpers, GuC engine activity, runtime PM guards, BAR constants, and Xe SR-IOV logging/assertion helpers. PCI probe/remove calls this path indirectly through the PCI driver and explicitly disables VFs during PF remove.

## Risks and Test Signals

The persistent runtime PM reference is critical: missing a put on disable or failure leaks a wakeref; missing a get lets the PF enter D3 while VFs exist. Device-link creation is best-effort, so resume-order bugs may appear only on systems with both PF and VF drivers bound. Tests should cover invalid VF counts, non-PF rejection, enabling while VFs already exist, provisioning failure unwinds, LMEM BAR sizing failure non-fatal logging, sysfs link creation/removal, engine stats toggling, PF remove disabling VFs, and `pci_dev_put()` ownership for VF lookups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci_sriov.c -->
