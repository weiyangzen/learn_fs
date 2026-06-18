# sources/distributed-fs/ceph-client/drivers/pci/ecam.c

## Purpose
Provides generic PCI ECAM config-window allocation, mapping, freeing, bus add/remove hooks, and `map_bus` implementation for host controllers and ACPI/DT PCI roots using enhanced configuration access mechanism.

## Important APIs, Types, And Functions
Exports `pci_ecam_create()`, `pci_ecam_free()`, `pci_ecam_map_bus()`, and `pci_generic_ecam_ops`. With ACPI quirks enabled it also defines `pci_32b_ops` and `pci_32b_read_ops`. Internal helpers are `pci_ecam_add_bus()` and `pci_ecam_remove_bus()` for 32-bit per-bus mapping.

## Control Flow
`pci_ecam_create()` validates the bus range, allocates `struct pci_config_window`, clamps the desired bus range to available ECAM resource size, claims the physical ECAM region, maps the full window on 64-bit systems or allocates per-bus mapping storage on 32-bit systems, runs optional platform `ops->init()`, and returns the config window. PCI config accesses call `pci_ecam_map_bus()` through `pci_ops` to compute a bus/device/function/register address.

## State And Persistence
`pci_config_window` stores parent device, config resource, bus resource, bus shift, ops, and either one `win` mapping or an array of per-bus `winp` mappings. The ECAM iomem resource remains reserved and mappings remain active until `pci_ecam_free()`.

## Dependencies And Integration Points
Depends on PCI core config-read/write helpers, `pci_remap_cfgspace()`, iomem resource reservation, `struct pci_ecam_ops`, and host-controller drivers such as Microchip PLDA through `pci_host_common_probe()`.

## Risks
Bus-range clamping can silently reduce discoverable buses after a warning. Nonstandard `bus_shift` affects address calculations and must match hardware. On 32-bit, config access before `.add_bus` maps the bus would fail. `ops->init()` errors must unwind mappings and resource reservations correctly.

## Test Signals
Validate ECAM resource conflict handling, full-window mapping on 64-bit, per-bus map/unmap on 32-bit, standard and nonstandard bus shifts, generic read/write config access, 32-bit-only quirk ops, and cleanup after host probe failure.
