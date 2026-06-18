# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_ids.h

## Purpose

`lpfc_ids.h` defines the LPFC driver's PCI device ID table, `lpfc_id_table`. This table is the match list used by the Linux PCI core to bind the LPFC driver to supported Emulex/Broadcom, ServerEngines, and ATTO Fibre Channel adapters. It is intentionally data-only: the file includes `<linux/pci.h>` and initializes an array of `const struct pci_device_id` entries terminated by `{ 0 }`.

The table is included by `lpfc_init.c`, where it is exported through `MODULE_DEVICE_TABLE(pci, lpfc_id_table)` and assigned to the driver's `struct pci_driver` `.id_table`. This makes the table both a runtime probe contract and a module autoload alias source.

## Important APIs, Types, and Constants

The only exported object in this header is:

- `const struct pci_device_id lpfc_id_table[]`

Each entry contains vendor ID, device ID, subsystem vendor ID, and subsystem device ID fields. Most Emulex/Broadcom and ServerEngines entries use `PCI_ANY_ID` for subsystem fields, allowing the driver to bind across board variants. ATTO entries are more specific: they use ATTO vendor/device pairs with specific subsystem IDs to distinguish Celerity and ThunderLink models.

The table covers older Emulex adapters such as Viper, Firefly, Thor, Pegasus, Centaur, Dragonfly, Superfly, RFLY, PFLY, Neptune variants, Helios variants, BMID/BSMB, Zephyr variants, TFLY, LP101/LP10000S/LP11000S/LPE11000S, Saturn variants, Proteus variants, Falcon, Balius, Lancer FC/FCoE physical and VF devices, Lancer G6/G7/G7P/G8 FC, and Skyhawk physical/VF devices. It also includes ServerEngines Tigershark and Tomcat IDs and ATTO Celerity/ThunderLink combinations.

The numeric `PCI_VENDOR_ID_*` and `PCI_DEVICE_ID_*` constants are not defined here. In this source tree they are available from LPFC hardware definitions such as `lpfc_hw.h` and standard kernel PCI headers.

## Control Flow and Integration

The control flow enabled by this file is Linux PCI driver binding:

1. The PCI core enumerates a device and compares vendor/device/subsystem IDs against `lpfc_id_table`.
2. If an entry matches, the LPFC `pci_driver` in `lpfc_init.c` can probe the device.
3. `MODULE_DEVICE_TABLE` causes module alias metadata to be generated so supported devices can autoload the module.
4. Once probe runs, later LPFC initialization code uses the matched PCI IDs and additional hardware discovery to select generation-specific behavior, ATTO labeling, SLI mode, FC/FCoE handling, VF/PF handling, and feature support.

Cross references show `lpfc_init.c` includes this header and registers the table at the bottom of the driver definition. Other initialization code switches on several IDs listed here, especially ATTO subsystem IDs and modern Lancer/Skyhawk/Proteus IDs, to adjust adapter type naming and behavior.

## State and Persistence Behavior

The table is static const module data. It has no runtime mutation and no persistence side effects. Its persistent impact is in kernel module metadata and boot-time device binding: adding or removing an entry changes which PCI devices can autoload and bind to the LPFC driver across reboots.

Because several entries use `PCI_ANY_ID` for subsystem matching, their binding scope is broad. The ATTO entries use subsystem-specific matches, which makes their binding behavior more constrained and dependent on exact subsystem IDs.

## Dependencies and External Contracts

The file depends on `<linux/pci.h>` for `struct pci_device_id` and `PCI_ANY_ID`. It depends on the LPFC build including definitions for all `PCI_VENDOR_ID_*` and `PCI_DEVICE_ID_*` symbols before or around inclusion. Its primary integration points are:

- `lpfc_init.c` include of `lpfc_ids.h`.
- `MODULE_DEVICE_TABLE(pci, lpfc_id_table)` module alias generation.
- `struct pci_driver` registration with `.id_table = lpfc_id_table`.
- Device-specific probe logic in `lpfc_init.c`, `lpfc_attr.c`, and related code paths that switch on IDs from the table.

## Risks

Incorrect entries have immediate hardware support consequences. A missing ID prevents supported adapters from probing or autoloading. A too-broad ID can bind LPFC to an unsupported or vendor-customized device. A wrong subsystem tuple can break ATTO-specific matching or cause a generic path to claim a branded adapter that needs special naming or behavior.

Because the file defines a non-`static` const object in a header, it must be included in exactly the intended translation unit. Including it from multiple C files would create duplicate definitions at link time. The current tree uses it from `lpfc_init.c`, which matches that pattern.

Ordering can matter for human maintenance and for overlapping ATTO device/subsystem combinations. The terminator `{ 0 }` is required; omitting or moving it would allow the PCI core to read beyond the table.

## Test Signals

Useful validation signals for changes touching this file include:

- Successful LPFC module build and link, confirming the table is defined once and all PCI ID constants resolve.
- `modinfo` or generated module alias checks showing expected PCI aliases for new or changed devices.
- Probe tests, or at least PCI modalias matching tests, for Emulex/Broadcom, ServerEngines, and ATTO IDs.
- Negative matching tests for nearby unsupported subsystem IDs, especially ATTO variants.
- Runtime probe smoke tests that confirm `lpfc_init.c` still maps matched IDs to the correct adapter type, generation, VF/PF handling, and FC/FCoE behavior.
