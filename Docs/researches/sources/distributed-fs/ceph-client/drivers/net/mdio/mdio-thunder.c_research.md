# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-thunder.c

## Purpose
This file implements the PCI wrapper for Cavium ThunderX MDIO controllers. It discovers up to four child MDIO bus nodes below the PCI device firmware node, maps each child resource into BAR0, enables the corresponding SMI block, and registers each bus with PHYLIB through `of_mdiobus_register()`. The driver is a hardware integration layer over the shared Cavium MDIO register-access helpers in `mdio-cavium.h`.

## Important APIs, Types, and Functions
`struct thunder_mdiobus_nexus` stores the BAR0 mapping and an array of `struct cavium_mdiobus *` entries so remove can unregister and disable each SMI bus. `thunder_mdiobus_pci_probe()` is the main setup path: it uses `pcim_enable_device()`, `pcim_request_all_regions()`, `pcim_iomap()`, `device_for_each_child_node_scoped()`, `of_address_to_resource()`, `devm_mdiobus_alloc_size()`, and `of_mdiobus_register()`. The registered `mii_bus` callbacks are `cavium_mdiobus_read_c22()`, `cavium_mdiobus_write_c22()`, `cavium_mdiobus_read_c45()`, and `cavium_mdiobus_write_c45()`. `thunder_mdiobus_pci_remove()` calls `mdiobus_unregister()` and writes zero to `SMI_EN`.

## Control Flow
Probe allocates nexus state, enables the PCI device, claims and maps BAR0, then iterates firmware children. Non-OF children stop discovery because this driver only handles OF-described child buses. For each OF child, it translates the child register address, allocates a managed `mii_bus` with private Cavium bus state, computes the SMI register base as `bar0 + child_resource_start - pci_bar_start`, enables SMI via `oct_mdio_writeq()`, initializes bus identity and MDIO operation callbacks, and asks OF MDIO helpers to register child PHYs/devices. Discovery stops after four buses or on translation/allocation failure. Remove walks the stored bus pointers and performs the inverse bus unregister and SMI disable steps.

## State and Persistence
Persistent runtime state is limited to managed allocations and PCI driver data. `bar0` is managed by PCIM, `mii_bus` objects are device-managed, and bus pointers are retained in `nexus->buses[]` for teardown. Hardware state changes are the SMI enable bit per child bus and the side effects of registering MDIO/PHY devices. There is no on-disk persistence or userspace configuration in this file.

## Dependencies and Integration Points
The file depends on PCI core, OF address translation, OF MDIO registration, PHYLIB/MDIO core, and the Cavium shared MDIO helpers. The PCI ID table matches Cavium vendor device `0xa02b`; module registration is through `module_pci_driver()`. Firmware must provide child OF nodes with address resources under the PCI device, and those child nodes become MDIO bus roots for PHY discovery.

## Risks and Edge Cases
Probe currently returns success even if a child registration fails after logging `of_mdiobus_register failed`; only early PCI/BAR failures unwind with an error. The bus array has a fixed size of four and discovery silently stops at that limit. A non-OF firmware child causes the loop to break rather than skip, so mixed firmware descriptions can prevent later OF children from being processed. Since a bus pointer is stored before registration, remove may call `mdiobus_unregister()` on buses whose registration failed, which relies on core tolerance for unregistering an unregistered or partially registered bus. Address arithmetic assumes child resources lie inside BAR0.

## Test Signals
Useful signals include successful probe logs `Added bus at ...`, visible MDIO buses under sysfs, PHY devices registered from child nodes, successful Clause 22 and Clause 45 transactions, and SMI enable bits being cleared on device removal. Negative tests should cover missing/invalid child resources, more than four children, `of_mdiobus_register()` failures, and PCI unbind/rebind cycles.
