# sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/vpci.c

## Purpose
`vpci.c` implements the default Xen PCI backend topology mode: hide host PCI topology and present exported devices on a synthetic guest bus `0000:00:*.*`. It assigns captured devices to virtual slots, keeps related multifunction devices together, publishes a single root, and maps guest BDFs back to physical `pci_dev` objects.

## Important APIs, Types, And Functions
`struct vpci_dev_data` stores 32 virtual slot lists guarded by a mutex. The `xen_pcibk_vpci_backend` callback table provides `__xen_pcibk_init_devices()`, `__xen_pcibk_release_devices()`, `__xen_pcibk_add_pci_dev()`, `__xen_pcibk_release_pci_dev()`, `__xen_pcibk_get_pci_dev()`, `__xen_pcibk_publish_pci_roots()`, and `__xen_pcibk_get_pcifront_dev()`.

## Control Flow
When a backend instance is allocated, `init` creates empty per-slot lists. Adding a physical device rejects bridges, allocates a `pci_dev_entry`, and searches for an existing virtual slot with a matching physical domain/bus/slot so multifunction devices remain adjacent. SR-IOV virtual functions at function zero are deliberately not treated as multifunction anchors. If no compatible slot exists, the first empty virtual slot is used. The selected virtual BDF is published through the Xenbus callback. Removal finds the entry by physical device, deletes it, and calls `pcistub_put_pci_dev()` under optional `device_lock()`.

## State And Persistence
The only persistent state is the in-memory slot-to-device list in `pdev->pci_dev_data`. It is rebuilt per backend instance and freed on Xenbus device removal. Guest-visible BDFs are persisted to Xenstore by the caller via the publish callback.

## Dependencies And Integration Points
The file depends on Linux PCI helpers for slot/function extraction and on pciback's backend abstraction. `xenbus.c` calls `add`, `release`, `publish`, and `get`; `pci_stub.c` receives returned devices on release; AER uses `find` to translate a physical device back to a pcifront BDF.

## Risks
The fixed 32-slot root bus can exhaust when many devices are exported. Bridge rejection prevents hierarchical topology. Guest drivers that require host BDFs need passthrough mode rather than vpci. Slot grouping for multifunction devices must avoid misleading guests around SR-IOV VFs.

## Test Signals
Attach devices with single-function, multifunction, and SR-IOV layouts; verify Xenstore `vdev-*` paths show expected `0000:00:slot.func` mappings; hot-remove devices and confirm pcistub release; confirm AER reports the same virtual BDF visible to the frontend.
