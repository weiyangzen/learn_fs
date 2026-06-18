# sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/pciback.h

## Purpose
`pciback.h` is the private contract for the Xen PCI backend. It defines the shared backend device structure, per-PCI-device state, backend topology abstraction, and cross-file APIs used by pcistub, Xenbus setup, vpci/passthrough mapping, config-space emulation, interrupt/event handling, and AER.

## Important APIs, Types, And Functions
`struct xen_pcibk_device` binds a `xenbus_device` to backend-specific PCI mapping data, a device mutex, backend watch, event-channel IRQ, mapped `xen_pci_sharedinfo`, operation flags, work item, and current `xen_pci_op`. `struct xen_pcibk_dev_data` is attached to each physical `pci_dev` and tracks emulated config fields, saved PCI state, permissive/interrupt-control bits, fake INTx state, IRQ count, and IRQ name. `struct xen_pcibk_backend` abstracts BDF presentation with `init`, `free`, `find`, `publish`, `release`, `add`, and `get` callbacks. Inline wrappers dispatch to the selected backend.

## Control Flow
The header encodes the module split: pcistub owns captured hardware and exports `pcistub_get_pci_dev_by_slot()`/`pcistub_put_pci_dev()`, Xenbus calls `xen_pcibk_init_devices()`, `xen_pcibk_add_pci_dev()`, `xen_pcibk_publish_pci_roots()`, and `xen_pcibk_release_devices()`, while event handlers call `xen_pcibk_do_op()` and `xen_pcibk_handle_event()`. `xen_pcibk_lateeoi()` centralizes late EOI release for the shared event-channel IRQ.

## State And Persistence
State is all in-kernel and per backend instance or per captured PCI device. The flag bits (`PDEVF_op_active`, `PCIB_op_pending`, `EOI_pending`) coordinate request processing, AER acknowledgements, and late EOI. The externally declared `xen_pcibk_aer_wait_queue` and `xen_pcibk_quirks` couple AER waiters and config quirks across source files.

## Dependencies And Integration Points
It depends on Linux PCI, interrupt, list, mutex/spinlock/workqueue, Xen events, Xenbus, and `xen/interface/io/pciif.h`. It also declares the two topology backends, `xen_pcibk_vpci_backend` and `xen_pcibk_passthrough_backend`; this group includes the vpci backend and the Xenbus selector.

## Risks
Because most helpers silently return `-1` or `NULL` if `xen_pcibk_backend` is unset, initialization ordering matters. Flag bits are shared between interrupt and process context, so call sites must preserve barriers and late-EOI behavior. Any extension of `xen_pcibk_dev_data` must respect allocation of the flexible `irq_name[]`.

## Test Signals
Compile coverage under `CONFIG_XEN_PCIDEV_BACKEND`, successful backend selection logs, correct callback dispatch for vpci/passthrough modes, and interrupt/request processing without EOI warnings validate this contract.
