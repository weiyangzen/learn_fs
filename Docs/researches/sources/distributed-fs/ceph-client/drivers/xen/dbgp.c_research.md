# sources/distributed-fs/ceph-client/drivers/xen/dbgp.c

## Purpose
`dbgp.c` provides Xen Dom0 hooks around USB EHCI debug port reset/startup so the hypervisor can coordinate debug-port ownership during controller reset.

## Important APIs, types, and functions
The internal helper is `xen_dbgp_op`. Exported functions are `xen_dbgp_reset_prep` and `xen_dbgp_external_startup`, except when early DBGP printk owns the symbols.

## Control flow
Callers pass a USB HCD. Outside the Xen initial domain the helpers return success without hypercalls. In Dom0, the helper fills `physdev_dbgp_op` with operation code and, for PCI controllers, segment/bus/devfn and PCI bus type. It then calls `HYPERVISOR_physdev_op(PHYSDEVOP_dbgp_op, ...)`.

## State and persistence
No driver state is stored. The effects are transient hypervisor coordination around debug-port reset phases.

## Dependencies and integration points
It depends on USB HCD/EHCI headers, optional PCI identification, Xen physdev hypercalls, and Xen initial-domain detection. It integrates with USB debug-port reset paths.

## Risks and test signals
Risks include unknown bus fallback for non-PCI controllers, hypercall failures disrupting USB reset, symbol availability under `CONFIG_EARLY_PRINTK_DBGP`, and Dom0-only behavior hiding issues in guests. Test signals include PCI EHCI debug-port reset in Dom0, non-PCI controller calls, non-Xen no-op paths, and hypervisor error propagation.
