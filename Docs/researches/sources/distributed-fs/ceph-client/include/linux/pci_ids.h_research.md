<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci_ids.h -->
# sources/distributed-fs/ceph-client/include/linux/pci_ids.h

## Purpose
`include/linux/pci_ids.h` is a shared PCI class/vendor/device/subsystem ID registry for kernel code. It supplies symbolic constants for PCI class codes and selected vendor/device IDs that are used by multiple drivers or core code. The file explicitly instructs maintainers to keep IDs numerically sorted and to avoid adding entries unless definitions are shared between multiple drivers.

## Important APIs, Types, and Functions
This header contains no functions or types. Its API is macro constants. The first block defines PCI base classes, subclasses, and selected programming interfaces, including storage, network, display, multimedia, memory/CXL, bridge, communication, system, input, docking, processor, serial bus, wireless, intelligent, satellite, crypto, signal processing, accelerator, and catch-all classes.

The remainder defines `PCI_VENDOR_ID_*`, `PCI_DEVICE_ID_*`, `PCI_SUBVENDOR_ID_*`, `PCI_SUBDEVICE_ID_*`, and a small number of subsystem IDs. In this snapshot the registry contains roughly 121 class/base-class constants, 286 vendor IDs, 2367 device IDs, 11 subvendor IDs, and 96 subdevice IDs. It includes common vendors used elsewhere in this subset, such as `PCI_VENDOR_ID_ALIBABA`, `PCI_VENDOR_ID_AMPERE`, `PCI_VENDOR_ID_QCOM`, `PCI_VENDOR_ID_ROCKCHIP`, and `PCI_VENDOR_ID_SAMSUNG`, which are consumed by the DesignWare PCIe VSEC header.

## Control Flow
There is no runtime control flow. The constants are consumed at compile time in driver ID tables, PCI fixups, class checks, quirk matching, feature allowlists, and vendor-specific capability handling. Typical control flow happens in users such as `pci_match_id()`, driver `id_table` matching, or quirk dispatch that compares `struct pci_dev` fields against these constants.

## State and Persistence Behavior
The header holds no mutable state and creates no objects. Its persistence is source-level ABI within the kernel tree: renaming, removing, or changing a numeric value breaks code that uses the symbolic constant to match hardware. Sorting and sharing rules are the maintainability constraints that keep the registry stable.

## Dependencies and Integration Points
The file is standalone except for include guards and is included by `include/linux/pci.h` and many drivers. It integrates with `struct pci_device_id` tables, `MODULE_DEVICE_TABLE(pci, ...)`, quirk declarations, class checks such as `pci_is_vga()` and `pci_is_display()`, PCIe vendor-specific logic, and subsystem-specific drivers that need shared symbolic IDs rather than local definitions.

## Risks
Incorrect numeric IDs cause drivers or quirks to bind to the wrong hardware or fail to bind to intended hardware. Adding single-use IDs here increases global churn and creates a false impression of shared semantics. Duplicate vendor aliases, legacy IDs, mixed case names, and comments recording vendor quirks require careful preservation because external hardware documentation is inconsistent. Sorting violations make future maintenance and review harder.

## Test Signals
Build coverage is the primary signal because all users compile these constants into match tables. Additional signals include `modinfo` alias checks for affected drivers, PCI device match tests on known hardware or emulated devices, quirk activation logs, `lspci -n` comparisons against expected vendor/device pairs, and simple scripts that verify numeric sort order and duplicate definitions when editing the file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci_ids.h -->
