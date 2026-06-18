# sources/distributed-fs/ceph-client/include/xen/interface/nmi.h

## Purpose
`nmi.h` defines Xen's x86-oriented NMI reason bits and the small `nmi_op` ABI for registering or unregistering an NMI callback.

## Important APIs, Types, and Functions
Important constants are `XEN_NMIREASON_io_error`, `XEN_NMIREASON_pci_serr`, `XEN_NMIREASON_unknown`, `XENNMI_register_callback`, and `XENNMI_unregister_callback`. `struct xennmi_callback` carries the callback handler address.

## Control Flow
A privileged caller, currently meaningful for dom0 VCPU0, registers a handler address through `nmi_op`. Xen records the callback and later invokes it for NMI events with reason bits exposed via architecture shared info. Unregister clears the callback.

## State and Persistence Behavior
Registered callback state lives in Xen for the calling VCPU until unregistered or domain teardown. NMI reason bits are transient diagnostic state in shared info.

## Dependencies and Integration Points
It includes `xen/interface/xen.h` for handle definitions and integrates with x86 Xen low-level trap/NMI handling, dom0 machine-check and hardware-error reporting, and platform interrupt diagnostics.

## Risks and Test Signals
Risks include invalid handler addresses, non-dom0 callers receiving `EINVAL`, architecture-specific reason interpretation, and callback lifetime across CPU hotplug or suspend. Test signals include register/unregister hypercall return paths, injected/observed NMI reason bits, and dom0-only permission checks.
