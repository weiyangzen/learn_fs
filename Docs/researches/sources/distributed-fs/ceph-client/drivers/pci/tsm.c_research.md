# sources/distributed-fs/ceph-client/drivers/pci/tsm.c

## Purpose
`tsm.c` connects PCI devices to platform TEE Security Manager devices for PCIe TDISP and related link/device-security operations. It manages DSM discovery, sysfs connection controls, TDI bind/unbind for confidential guest assignment flows, guest request forwarding, DOE mailbox transfers, and teardown when PCI devices or TSM providers disappear.

## Important APIs, types, and functions
The file uses global `pci_tsm_rwsem`, counts link and device-security TSM providers, and relies on `struct pci_tsm`, `struct pci_tsm_pf0`, `struct pci_tdi`, `struct tsm_dev`, and `struct pci_tsm_ops`. Exported functions include `pci_tsm_unbind()`, `pci_tsm_bind()`, `pci_tsm_guest_req()`, `pci_tsm_tdi_constructor()`, `pci_tsm_link_constructor()`, `pci_tsm_pf0_constructor()`, `pci_tsm_pf0_destructor()`, `pci_tsm_register()`, `pci_tsm_unregister()`, and `pci_tsm_doe_transfer()`. PCI core lifecycle hooks are `pci_tsm_init()` and `pci_tsm_destroy()`.

## Control flow and behavior
A link TSM provider registers with `pci_tsm_register()`, which increments provider counts and exposes sysfs groups for eligible PF0 devices. Users connect a PF0 DSM by writing a `tsmN` device name to `tsm/connect`; `pci_tsm_connect()` probes provider state, takes the PF0 lock, calls provider `connect()`, then probes dependent functions and VFs with `probe_fn()`. `find_dsm_dev()` resolves the DSM for a device from PF0 or an upstream port. `pci_tsm_init()` later probes newly appearing dependent functions when a DSM already exists.

Binding uses `pci_tsm_bind()` under the read semaphore and PF0 mutex to create a `struct pci_tdi` for a KVM private-memory context. `pci_tsm_guest_req()` validates request scope, verifies a bound TDI, and forwards guest payloads to provider `guest_req()`. Unbind and disconnect walk functions in reverse order, unbind TDIs, remove per-function contexts, call provider disconnect, and hide sysfs when the last provider unregisters. DOE transfer requires a PF0 TSM with a CMA DOE mailbox.

## State and persistence
Persistent state includes `pdev->tsm`, DSM pointers, PF0 locks, TDI pointers, provider counts, sysfs group visibility, and DOE mailbox references. The read/write semaphore serializes provider registration, connect/disconnect, per-device init/destroy, and guest operations.

## Dependencies and integration points
It depends on PCIe TEE capability bits, SR-IOV enumeration helpers, PCI DOE, TSM core device lookup, sysfs visible groups, KVM contexts, xarray-including headers for provider internals, and PCI search helpers for PF/VF walking.

## Risks
This is security-sensitive orchestration. Races between provider unregister, PCI removal, sysfs connect/disconnect, VF creation, and guest requests are mitigated by `pci_tsm_rwsem` and PF0 mutexes but remain the key risk. Provider callbacks are trusted to implement correct security transitions. Scope filtering in `pci_tsm_guest_req()` prevents unrelated guest commands from being proxied.

## Test signals
Test provider register/unregister, PF0 connect/disconnect, sysfs visibility, VF and multifunction probing, bind idempotence and conflicting KVM contexts, guest request scope rejection, teardown while bound, DOE mailbox absence, and reverse-order unbind during PCI removal.
