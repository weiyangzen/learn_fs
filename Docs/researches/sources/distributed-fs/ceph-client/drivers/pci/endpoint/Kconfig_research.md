# sources/distributed-fs/ceph-client/drivers/pci/endpoint/Kconfig

## Purpose
Defines the top-level PCI endpoint configuration menu and core endpoint feature switches. It controls whether endpoint controller/function libraries, configfs management, MSI doorbell support, and endpoint function drivers are exposed to the kernel build.

## Important APIs, Types, And Functions
Kconfig symbols are `PCI_ENDPOINT`, `PCI_ENDPOINT_CONFIGFS`, and `PCI_ENDPOINT_MSI_DOORBELL`. The file also sources `drivers/pci/endpoint/functions/Kconfig` to make endpoint function drivers visible inside the same menu.

## Control Flow
There is no runtime execution. Build-time flow starts with `menu "PCI Endpoint"`, allows enabling endpoint core when `HAVE_PCI` is present, optionally selects `CONFIGFS_FS` for configfs endpoint binding, optionally enables MSI doorbell support when `GENERIC_MSI_IRQ` exists, then enters the endpoint functions submenu.

## State And Persistence
State is kernel configuration. Enabling `PCI_ENDPOINT` changes which object files are built by the endpoint Makefile and whether endpoint controller/function frameworks are available to platform drivers.

## Dependencies And Integration Points
Integrates with the top-level PCI Kconfig, endpoint Makefile, configfs, generic MSI infrastructure, and endpoint function drivers such as test, NTB, VNTB, and MHI.

## Risks
Missing dependencies can expose build options that do not link on a platform. Because `PCI_ENDPOINT_CONFIGFS` selects configfs, enabling it changes userspace ABI availability. Endpoint function Kconfig inclusion under this menu means function symbols depend on the top-level endpoint core being sensible.

## Test Signals
Run Kconfig builds with endpoint disabled, endpoint core only, configfs enabled, MSI doorbell enabled, and individual endpoint functions. Confirm expected object inclusion and absence of unresolved configfs/MSI references.
