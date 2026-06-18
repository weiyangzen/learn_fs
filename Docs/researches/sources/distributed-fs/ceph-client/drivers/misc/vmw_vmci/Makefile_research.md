# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/Makefile

## Purpose
`vmw_vmci/Makefile` defines how the VMware VMCI driver is built and which implementation objects compose the `vmw_vmci` module or built-in object.

## Important APIs, Types, and Functions
The Makefile selects `vmw_vmci.o` with `obj-$(CONFIG_VMWARE_VMCI)` and composes it from `vmci_context.o`, `vmci_datagram.o`, `vmci_doorbell.o`, `vmci_driver.o`, `vmci_event.o`, `vmci_guest.o`, `vmci_handle_array.o`, `vmci_host.o`, `vmci_queue_pair.o`, `vmci_resource.o`, and `vmci_route.o`.

## Control Flow
There is no runtime control flow. Kbuild links the listed objects into the VMCI driver when `CONFIG_VMWARE_VMCI` is enabled.

## State and Persistence
No runtime state is defined here. State resides in the listed VMCI implementation files.

## Dependencies and Integration Points
The file integrates the VMCI subdirectory with Kbuild and the `CONFIG_VMWARE_VMCI` symbol from the adjacent Kconfig.

## Risks and Edge Cases
All VMCI subcomponents are always included when the symbol is enabled; partial feature builds are not represented. Adding new VMCI implementation files requires updating this composite object list.

## Test Signals
Verify built-in and module builds include all listed VMCI objects, disabled builds omit the composite object, and dependency changes in Kconfig remain aligned with this Makefile.
