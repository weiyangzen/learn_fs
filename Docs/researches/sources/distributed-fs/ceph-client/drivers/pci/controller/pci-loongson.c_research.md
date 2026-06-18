# sources/distributed-fs/ceph-client/drivers/pci/controller/pci-loongson.c

## Purpose
`pci-loongson.c` provides Loongson PCI host controller support for OF platforms and ACPI ECAM systems. It maps Loongson-specific CFG0/CFG1 config windows into generic PCI config operations and carries several PCI fixups for Loongson bridge/device quirks: bridge class correction, always-on/non-compliant system bus BARs, MRRS limits, interrupt pin correction, and an MSI enable quirk.

## Important APIs, types, and functions
`struct loongson_pci_data` describes controller capabilities with flags and `pci_ops`; `struct loongson_pci` stores CFG0/CFG1 bases and match data. `FLAG_CFG0`, `FLAG_CFG1`, `FLAG_DEV_FIX`, and `FLAG_DEV_HIDDEN` drive config window selection and device filtering. `cfg0_map()` and `cfg1_map()` build MMIO addresses for standard and extended config space; CFG1 supports extended config by folding high offset bits into the window address. `pci_loongson_map_bus()` enforces root/child visibility quirks and selects CFG0 for standard config or CFG1 for extended config.

The file registers many PCI fixups with `DECLARE_PCI_FIXUP_*`. `bridge_class_quirk()` changes Loongson PCIe ports to normal PCI bridge class. `system_bus_quirk()` marks selected internal devices with `mmio_always_on` and `non_compliant_bars`. `loongson_mrrs_quirk()` sets `pci_host_bridge.no_inc_mrrs`; on MIPS, `loongson_set_min_mrrs_quirk()` walks upstream bridges and clamps endpoint MRRS to 256 bytes under affected ports. `loongson_pci_pin_quirk()` derives interrupt pins from the function number, and `loongson_pci_msi_quirk()` explicitly enables MSI on a host bridge class device.

## Control flow
For OF builds, `loongson_pci_probe()` allocates a host bridge, loads match data, maps CFG0 and/or CFG1 resources according to flags, sets `bridge->sysdata`, installs the selected ops, sets `bridge->map_irq` to `loongson_map_irq()`, and calls `pci_host_probe()`. The OF match table supports `loongson,ls2k-pci`, `loongson,ls7a-pci`, and `loongson,rs780e-pci`; LS2K/LS7A use CFG1 and generic 8/16/32-bit config operations, while RS780E uses CFG0 and 32-bit-only config operations.

For ACPI builds, `loongson_pci_ecam_init()` allocates private data behind `struct pci_config_window`, marks CFG1 plus hidden-device filtering, and derives `cfg1_base` from the ECAM window and bus start. `loongson_pci_ecam_ops` then exposes `pci_loongson_map_bus()` through the standard ECAM interface.

## State and persistence behavior
The driver stores only mapped config-window bases and per-controller flags. PCI fixups mutate in-memory PCI core device state such as class, BAR compliance flags, MRRS policy, pin, and MSI capability flags. There is no disk persistence and no explicit remove path for the builtin platform driver.

## Dependencies and integration points
The file integrates with OF host bridge probing, ACPI ECAM, generic PCI config accessors, Loongson PCI IDs, IRQ mapping through `of_irq_parse_and_map_pci()`, legacy i8259 interrupt-line fallback, and the PCI fixup framework. It also depends on arch behavior: the MRRS clamp is compiled only for MIPS, while ACPI ECAM support is separately guarded.

## Risks and edge cases
Visibility filtering is important: `FLAG_DEV_FIX` suppresses extra devices behind non-root buses, and `FLAG_DEV_HIDDEN` avoids root functions that should not exist. A wrong flag set can make devices disappear or make invalid config cycles. CFG1 mapping is optional on OF probe; if absent, standard CFG0 may still be unavailable depending on the compatible data. `loongson_pci_msi_quirk()` assumes the target host bridge path has a valid MSI capability offset. MRRS behavior differs between firmware quality levels and architectures.

## Test signals
Test coverage should include OF boot on LS2K/LS7A/RS780E, ACPI ECAM boot, standard and extended config-space access, hidden-device filtering on root bus slots/functions, child-bus single-device filtering, bridge class fixups, internal system-bus BAR behavior, i8259 fallback IRQ mapping, MRRS clamp on MIPS, and MSI behavior on LS7A port 5.
