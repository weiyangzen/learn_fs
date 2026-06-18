<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci.h

## Purpose

`xe_pci.h` declares the minimal PCI-driver interface exported outside `xe_pci.c`. It lets module init/exit register or unregister the Xe PCI driver and lets VF-side code resolve the parent PF Xe device.

## Important APIs

`xe_register_pci_driver()` wraps `pci_register_driver()` for the static Xe PCI driver. `xe_unregister_pci_driver()` unregisters it. `xe_pci_to_pf_device(struct pci_dev *pdev)` uses PCI IOV PF drvdata lookup to return the PF `struct xe_device` associated with a VF `pci_dev`, or `NULL` if no matching PF driver data is available.

## Control Flow and State

The header stores no state. The registration functions affect global PCI-driver state in the kernel. PF lookup depends on the PF probe path having stored DRM drvdata on the PCI device and on the PCI core's SR-IOV relationship tracking.

## Dependencies and Integration Points

It forward-declares `struct pci_dev` and `struct xe_device` for use by module setup, SR-IOV, and any helper code that needs to cross from a VF PCI device to the PF driver instance.

## Risks and Test Signals

The API is intentionally tiny, so the main risks are lifecycle misuse and stale PF references. Test signals include module load/unload registering exactly once, VF lookup returning `NULL` when PF driver data is absent or wrong, and correct PF resolution after VFs are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci.h -->
