<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_pci.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_pci.c

## Purpose
Discovers IPMI system interfaces exposed on PCI, chooses the correct KCS/SMIC/BT state machine, determines I/O versus memory access, probes KCS register spacing, and registers the interface with the generic IPMI SI core.

## Important APIs, Types, and Functions
- `ipmi_si_pci_init()` and `ipmi_si_pci_shutdown()` register/unregister the PCI driver under the `trypci` module parameter.
- `ipmi_pci_probe()` is the main PCI probe path.
- `ipmi_pci_probe_regspacing()` tests KCS spacing of 1, 4, and 16 bytes by temporarily setting up I/O, writing an invalid command, and reading status.
- `ipmi_pci_remove()` delegates to `ipmi_si_remove_by_dev()`.
- `ipmi_pci_devices` matches HP MMC and PCI serial IPMI classes; `ipmi_pci_blacklist` excludes a Realtek virtual device.

## Control Flow
Probe rejects blacklisted devices, selects `si_info` from PCI class, enables the device, selects `ipmi_si_port_setup()` for I/O BARs or `ipmi_si_mem_setup()` for memory BARs, derives BAR start, probes spacing, attaches the PCI IRQ if present, logs resource metadata, and calls `ipmi_si_add_smi()`.

## State and Persistence
`pci_registered` records whether the PCI driver was registered. `si_trypci` persists as module configuration. Runtime interface state is owned by the SI core.

## Dependencies and Integration Points
Integrates with PCI core, IPMI SI state machines, port/memory setup helpers, and standard IRQ setup. It is one of several SI discovery lanes alongside platform, ACPI, OF, DMI, hardcoded, and PA-RISC paths.

## Risks
Register spacing probing performs live writes to the KCS command register, so it must only happen after correct resource setup and cleanup. The default branch for unknown IPMI class returns `-ENOMEM`, which is semantically odd. Systems without `CONFIG_HAS_IOPORT` reject I/O BAR devices with `-ENXIO`.

## Test Signals
Probe KCS, SMIC, and BT class devices; validate spacing detection on 1, 4, and 16 byte KCS mappings; confirm blacklist behavior; exercise removal while IRQ setup is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_pci.c -->
