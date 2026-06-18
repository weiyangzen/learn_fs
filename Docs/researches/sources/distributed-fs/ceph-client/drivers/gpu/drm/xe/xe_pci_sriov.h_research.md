<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci_sriov.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci_sriov.h

## Purpose

`xe_pci_sriov.h` declares the PCI SR-IOV integration hooks used by the Xe PCI driver and PF/VF helper code.

## Important APIs

When `CONFIG_PCI_IOV` is enabled, `xe_pci_sriov_configure()` enables or disables VFs for a PF and `xe_pci_sriov_get_vf_pdev()` returns a referenced VF `pci_dev` for a 1-based VF ID. Without PCI IOV, `xe_pci_sriov_configure()` is an inline no-op returning 0.

## Control Flow and State

The header is stateless, but the enabled implementation changes PCI SR-IOV state, PF provisioning state, runtime PM references, and PF/VF sysfs/device-link relationships.

## Dependencies and Integration Points

It forward-declares `struct pci_dev` and is consumed by `xe_pci.c` and SR-IOV PF logic.

## Risks and Test Signals

The `CONFIG_PCI_IOV` fallback means callers must tolerate no-op configuration on kernels without IOV support. Compile coverage should include both enabled and disabled builds. Runtime tests should validate VF pdev reference ownership and correct error propagation from `sriov_configure`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci_sriov.h -->
