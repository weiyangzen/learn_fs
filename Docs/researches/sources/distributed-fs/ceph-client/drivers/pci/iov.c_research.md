# sources/distributed-fs/ceph-client/drivers/pci/iov.c

## Purpose
Implements PCI SR-IOV support: capability initialization, VF BAR sizing/resource management, enabling/disabling VFs, creating/removing VF `pci_dev` objects, sysfs controls, VF MSI-X count hooks, state restore, and exported PF/VF helper APIs.

## Important APIs, Types, and Functions
Exported helpers include `pci_iov_virtfn_bus()`, `pci_iov_virtfn_devfn()`, `pci_iov_vf_id()`, `pci_iov_get_pf_drvdata()`, `pci_enable_sriov()`, `pci_disable_sriov()`, `pci_num_vf()`, `pci_vfs_assigned()`, `pci_sriov_set_totalvfs()`, `pci_sriov_get_totalvfs()`, `pci_sriov_configure_simple()`, `pci_iov_vf_bar_set_size()`, and `pci_iov_vf_bar_get_sizes()`. Core internal helpers are `sriov_init()`, `sriov_enable()`, `sriov_disable()`, `pci_iov_add_virtfn()`, `pci_iov_remove_virtfn()`, `pci_iov_update_resource()`, and restore helpers.

## Control Flow
Initialization finds the SR-IOV extended capability, disables any firmware-left VF Enable, sets ARI if needed, validates total VFs and page size, sizes VF BARs with VF Enable clear, scales PF VF BAR resources by total VFs, records offsets/stride/capabilities/link/VF ReBAR, marks the device as a PF, and computes maximum bus range. Enabling validates requested VF count/resources/bus range, enables VF BAR resources, creates dependency links when needed, calls arch enable hook, writes NumVFs and SR-IOV Control VF Enable/MSE, waits, creates VF devices and sysfs links, and records `num_VFs`. Disabling removes VFs, clears control bits, waits, calls arch disable hook, removes links, and resets NumVFs. Sysfs `sriov_numvfs` delegates to the PF driver's `sriov_configure()` under device and rescan/remove locks.

## State and Persistence Behavior
`struct pci_sriov` persists capability position, control word, total/driver-max/initial/current VF counts, offset/stride, VF BAR sizes, page size, VF device ID, dependency link, VF ReBAR capability, resource count, and autoprobe flag. VF `pci_dev`s hold `is_virtfn`, `physfn`, inherited resource slices, and sysfs `physfn`/`virtfnN` links. Hardware state includes SR-IOV control, NumVFs, system page size, VF BARs, and VF ReBAR size fields.

## Dependencies and Integration Points
Depends on PCI extended capability/resource sizing, bus creation/removal, sysfs attribute groups, MSI-related VF vector hooks, PCI driver callbacks (`sriov_configure`, `sriov_get_vf_total_msix`, `sriov_set_msix_vec_count`), arch hooks `pcibios_sriov_enable/disable`, ReBAR helpers, IOMMU assignment checks, and global PCI rescan/remove locking.

## Risks
SR-IOV enablement is resource- and topology-sensitive: VF BAR resources must be assigned for every implemented VF BAR and bus numbers must cover the highest VF. Partial VF creation must unwind already-created VFs. Sysfs vector count changes are blocked when a VF driver is bound, but PF driver callbacks still need strong validation. Restore order matters: ARI must be restored before NumVFs because offset/stride can depend on it. Drivers that remove with VFs still enabled are warned but can leave cleanup to later paths.

## Test Signals
Initialize PFs with varied total VFs, ARI, VF BAR sizes, page sizes, VF ReBAR; enable/disable via driver API and sysfs; resource/bus exhaustion failures; no-VF-scan mode; VF sysfs link creation/removal; VF driver autoprobe toggling; assigned VF refusal in `pci_sriov_configure_simple()`; suspend/resume restore; PF remove with VFs enabled; VF MSI-X count attributes.
