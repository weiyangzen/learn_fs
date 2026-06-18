# Research: sources/distributed-fs/ceph-client/include/linux/pci-tsm.h

Purpose: `pci-tsm.h` defines PCI TEE Security Manager abstractions for confidential PCIe links and function security, including TSM registration, SPDM/IDE/TDISP coordination, TDI binding, DOE transfer, and guest request forwarding.

Important APIs/types/functions: `struct pci_tsm_ops` contains mutually exclusive link and device-security operation groups. Link ops cover probe/remove, connect/disconnect, bind/unbind, and guest requests; devsec ops cover lock/unlock. Context types include `struct pci_tdi`, `struct pci_tsm`, and `struct pci_tsm_pf0` with DSM lock and DOE mailbox. `is_pci_tsm_pf0()` identifies eligible function 0 devices. `enum pci_tsm_req_scope` classifies guest requests as info, state change, debug read, or debug write. Enabled APIs register/unregister TSM devices, construct/destruct link/PF0 contexts, perform DOE transfer, bind/unbind TDI, construct TDI state, and process guest requests.

Control flow and state: a TSM driver registers, probes/locks PCI devices, establishes secure links through connect, optionally binds a TDI to a KVM/TVM, marshals scoped guest requests, and disconnects/unbinds during teardown. Locking context is part of the contract: operations run under `pci_tsm_rwsem` and, for link operations, a DSM mutex. State ties PCI devices to TSM devices, DSM devices, DOE mailboxes, and optional TDI/KVM contexts.

Dependencies and integration points: depends on mutexes, PCI core, socket pointers, KVM, TSM device core, DOE mailboxes, PCIe IDE/TEE capabilities, and TDISP security policy. It integrates with `pci-doe.h`, `pci-ide.h`, confidential-computing guests, and VF assignment flows.

Risks and test signals: risks include security-scope violations for guest requests, debug write authorization mistakes, lock inversions, stale TDI bindings across VM teardown, DOE transfer failure handling, and incorrect PF0 eligibility. Tests should cover registration lifecycle, PF0 detection matrix, connect/disconnect serialization, bind/unbind with KVM teardown, guest request scope enforcement, DOE errors, and disabled-config stubs returning `-ENXIO`.
