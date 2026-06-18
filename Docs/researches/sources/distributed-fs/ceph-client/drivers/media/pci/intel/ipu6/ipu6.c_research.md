# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6.c

## Purpose
`ipu6.c` is the PCI parent driver for Intel IPU6 hardware. It identifies the hardware generation, loads and authenticates firmware, initializes buttress power/security state, creates ISYS and PSYS auxiliary devices, instantiates their MMUs and platform data, configures SPC firmware boot data, handles PCI/runtime PM, and cleans up all child devices on removal.

## Important APIs, Types, And Functions
The file defines generation-specific `isys_ipdata` and `psys_ipdata`, buttress control descriptors, `struct ipu6_cell_program`, exported `ipu6_configure_spc()`, and the PCI driver callbacks. Major functions include `ipu6_internal_pdata_init()`, `ipu6_isys_init()`, `ipu6_psys_init()`, `ipu6_pci_config_setup()`, `ipu6_configure_vc_mechanism()`, `ipu6_pci_probe()`, `ipu6_pci_remove()`, reset prepare/done handlers, and PM callbacks.

## Control Flow
Probe enables the PCI device, maps BAR0, sets the DMA mask, selects firmware and hardware version from PCI ID, fills internal platform data for the generation, initializes buttress, requests and validates CPD firmware, creates ISYS and PSYS auxiliary devices plus MMUs, powers PSYS enough to initialize its MMU, maps firmware and creates package directory, requests the shared IRQ, authenticates firmware, powers PSYS back down, configures VC arbitration, logs SKU/version, enables runtime PM, and finally marks the bus ready for auxiliary probes.

`ipu6_configure_spc()` invalidates SPC icache and either writes the secure-mode package directory IMR offset or parses the CPD package directory/cell program to configure icache base, master, start PC, and DMEM package directory pointer.

## State And Persistence
`struct ipu6_device` persists for the PCI device lifetime. It stores child bus devices, firmware pointer/name, BAR mapping, secure mode flags, hardware version, and `bus_ready_to_probe`. Runtime PM restore paths reapply buttress state and IPC reset when needed.

## Dependencies And Integration Points
The driver integrates PCI IDs from `ipu6-pci-table`, IPU bridge ACPI sensor setup, CPD firmware parsing, buttress authentication/IPC/IRQ code, auxiliary-bus child devices, IPU6 MMU, and ISYS/PSYS platform data.

## Risks And Test Signals
Probe error unwinding spans many resources; failures after child creation must clean MMUs, package directories, firmware mappings, IRQs, and firmware references in the right order. MSI behavior differs for IPU6EP/MTL. Secure versus non-secure SPC setup changes firmware address handling. Test signals include probe on every PCI ID, missing/invalid firmware, secure and non-secure boot, suspend/resume with IPC reset, PCI reset recovery, IRQ sharing, and child auxiliary probe deferral until `bus_ready_to_probe` is true.
