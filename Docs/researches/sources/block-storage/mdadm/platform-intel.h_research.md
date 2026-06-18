# File Research: sources/block-storage/mdadm/platform-intel.h

## Role

`platform-intel.h` declares Intel IMSM platform capability structures, constants, inline capability tests, controller/device list types, and discovery helper prototypes.

## Key Structures

- `struct imsm_orom` models IMSM AHCI/SCU/NVMe/VMD capability data, including signature, version, RAID level capability, supported strip sizes, disk/volume limits, attributes, capabilities, and driver features.
- `struct imsm_level_ops` maps RAID levels to capability and disk-count validators.
- `enum sys_dev_type` classifies discovered controllers as unknown, SAS, SATA, NVMe, VMD, SATA VMD, or max.
- `struct sys_dev` records controller type, sysfs path, PCI ID, device ID, class, and list link.
- `struct efi_guid`, `struct devid_list`, and `struct orom_entry` support EFI/OROM matching and cached capability records.

## Inline Helpers

- `imsm_rlc_has_bit()` tests RAID-level capability bits.
- `imsm_orom_has_chunk()` validates power-of-two chunk sizes against OROM strip-size bits.
- `fls()` provides a local most-significant-bit helper.
- `imsm_orom_is_enterprise()`, `imsm_orom_is_nvme()`, `imsm_orom_is_vmd_without_efi()`, and `imsm_orom_has_tpv_support()` test capability signatures/features.
- `guid_str()` formats EFI GUIDs.

## Exported Interfaces

The header declares controller discovery, capability lookup, sysfs path conversion, HBA attachment tests, OROM lookup by device ID, NVMe multipath/namespace checks, and VMD domain mapping.

## Invariants

The OROM structures are packed firmware-layout definitions. Constants encode Intel IMSM/RST/VROC capability semantics and must match firmware metadata formats expected by IMSM handlers.
