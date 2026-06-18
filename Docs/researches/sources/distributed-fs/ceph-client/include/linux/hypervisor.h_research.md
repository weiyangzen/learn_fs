# sources/distributed-fs/ceph-client/include/linux/hypervisor.h

## Purpose
Provides tiny generic hypervisor helpers for pinning vCPUs and detecting isolated PCI-function environments.

## APIs, Control Flow, and State
On x86, `hypervisor_pin_vcpu()` dispatches to `x86_platform.hyper.pin_vcpu()`. On non-x86, it is a no-op and `jailhouse_paravirt()` checks the device tree for a `jailhouse,cell` compatible node. `hypervisor_isolated_pci_functions()` returns true for s390, loongarch, or Jailhouse paravirtual cells. There is no local persistent state.

## Dependencies, Integration, Risks, and Tests
Depends on x86 platform hypervisor hooks or OF device-tree helpers. Integrates with scheduler/CPU placement and PCI isolation policy. Risks include the include guard typo spelling `HYPEVISOR`, non-x86 `of_find_compatible_node()` reference lifetime expectations, and architecture-specific assumptions hidden behind `IS_ENABLED`. Test signals include x86 hypervisor hook calls, OF Jailhouse detection, and config builds for x86, s390, loongarch, and generic non-x86.
