# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-iproc.h

## Purpose

`pcie-iproc.h` defines the shared contract between Broadcom iProc PCIe wrappers, the common host-controller core, and the optional internal MSI implementation. It exposes controller type enumeration, mapping descriptors, the main `struct iproc_pcie`, and setup/remove/shutdown/MSI entry points.

## Important APIs, Types, And Functions

- `enum iproc_pcie_type` distinguishes BCMA PAXB, platform PAXB, PAXB v2, PAXC, and PAXC v2 wrappers.
- `struct iproc_pcie_ob` describes outbound mapping requirements: AXI offset and supported window count.
- `struct iproc_pcie_ib` describes inbound mapping region count.
- `struct iproc_pcie` is the shared mutable state for wrappers and core logic: device, type, register offsets, MMIO base, physical base, memory resource, optional PHY, IRQ mapping callback, endpoint/config quirks, outbound/inbound mapping state, MSI steering flag, and MSI pointer.
- `iproc_pcie_setup()`, `iproc_pcie_remove()`, and `iproc_pcie_shutdown()` are the common host lifecycle entry points.
- `iproc_msi_init()` and `iproc_msi_exit()` are declared when `CONFIG_PCIE_IPROC_MSI` is enabled and stubbed to `-ENODEV`/no-op otherwise.

## Control Flow

Wrappers allocate `struct iproc_pcie` as PCI host bridge private data, fill fields such as `dev`, `type`, `base`, `base_addr`, resources, optional PHY, and mapping flags, then call `iproc_pcie_setup()`. The common core fills `reg_offsets`, mapping tables, and runtime flags. MSI setup calls the header-provided `iproc_msi_init()` symbol, which either links to the MSI implementation or returns `-ENODEV` when the internal MSI driver is not configured.

## State And Persistence

The header itself has no state, but it defines which state is shared across files. The most important persistent fields are `reg_offsets`, `base/base_addr`, mapping flags/tables, quirk booleans, and `msi`. These fields remain valid from setup until remove/shutdown.

## Dependencies And Integration Points

It depends on kernel declarations for `struct device`, `struct resource`, `struct phy`, `struct pci_dev`, `struct list_head`, and device tree nodes through included users. It is included by `pcie-iproc.c`, `pcie-iproc-msi.c`, `pcie-iproc-platform.c`, and `pcie-iproc-bcma.c`.

## Risks And Edge Cases

- Many fields are initialized by wrappers and later assumed valid by the common core; missing `base`, wrong `type`, or inconsistent mapping flags cause setup failures or invalid MMIO.
- The MSI stubs mean callers must treat `-ENODEV` as an acceptable "not using internal MSI" outcome.
- Boolean quirk fields encode hardware behavior tightly; adding a new SoC requires careful field initialization in `iproc_pcie_rev_init()` and wrappers.

## Test Signals

Compile coverage with `CONFIG_PCIE_IPROC_MSI=y` and disabled, wrapper builds for BCMA and OF platform paths, setup calls with each enum value, static analysis for uninitialized shared fields, and runtime probe verifying wrappers populate the fields consumed by common setup.
