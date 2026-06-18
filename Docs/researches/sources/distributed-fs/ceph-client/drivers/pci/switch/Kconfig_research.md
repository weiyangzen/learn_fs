# sources/distributed-fs/ceph-client/drivers/pci/switch/Kconfig

## Purpose
This Kconfig fragment defines the PCI switch controller driver menu and the `PCI_SW_SWITCHTEC` option for the MicroSemi Switchtec PCIe switch management driver.

## Important APIs, types, and functions
There are no C APIs. The important symbol is `CONFIG_PCI_SW_SWITCHTEC`, declared as a tristate and gated by `depends on PCI`.

## Control flow and behavior
When enabled built-in or as a module, the option causes `switchtec.o` to be built by the local Makefile. The help text documents that the driver exposes userspace MRPC command submission through `/dev/switchtecX` and points to `Documentation/driver-api/switchtec.rst`.

## State and persistence
The persistent effect is build configuration: `.config` records whether Switchtec support is disabled, built in, or modular.

## Dependencies and integration points
The symbol integrates with the PCI menu hierarchy and `drivers/pci/switch/Makefile`. It indirectly selects the runtime code in `switchtec.c`.

## Risks
Because this option exposes a userspace management device for PCIe switches, enabling it can add a privileged hardware-management ABI. Missing `PCI` dependency would break builds, but this fragment correctly gates it.

## Test signals
Check `olddefconfig` visibility under PCI, module and built-in builds, and that `CONFIG_PCI_SW_SWITCHTEC=m/y` produces the expected `switchtec` driver.
