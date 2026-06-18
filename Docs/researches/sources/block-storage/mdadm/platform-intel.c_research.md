# File Research: sources/block-storage/mdadm/platform-intel.c

## Role

`platform-intel.c` discovers Intel storage controllers and IMSM/VROC/RST capabilities from sysfs, PCI option ROMs, EFI variables, ACPI UEFI tables, NVMe/VMD compatibility data, and controller registers. Metadata handlers use this to validate IMSM arrays against hardware/firmware support.

## Controller Discovery

- `find_driver_devices()` scans `/sys/bus/<bus>/drivers/<driver>` for Intel devices, supports `isci`, `ahci`, `nvme`, and `vmd`, and classifies devices as SAS, SATA, NVMe, VMD, or SATA-behind-VMD.
- VMD domains are resolved with `vmd_find_pci_bus()` and `vmd_domain_to_controller()`.
- NVMe devices behind VMD are skipped in plain NVMe discovery, while VMD controllers are included separately.
- `find_intel_devices()` caches the discovered list for 10 seconds.
- `device_by_id()` and `device_by_id_and_path()` search the cached controller list.

## OROM and Capability Discovery

- `scan()` inspects option ROM memory for Intel PCI expansion data and IMSM `$VER` capability blocks.
- `find_imsm_hba_orom()` scans legacy option ROMs unless EFI boot is detected or test modes are active.
- `imsm_platform_test()` synthesizes capabilities for test environments.
- OROM entries are stored in the global `orom_entries` list with associated device IDs.
- `find_imsm_capability()` first checks cached OROMs, then NVMe synthetic caps, EFI caps, VMD caps, and legacy OROM caps.

## EFI and ACPI Discovery

- EFI variable access supports both efivarfs and old sysfs EFI variable layouts.
- ACPI UEFI table scanning reads `/sys/firmware/acpi/tables/UEFI*`, matches controller identifiers by name and GUID, verifies table length, and extracts embedded `struct imsm_orom`.
- SATA, sSATA, tSATA, VROC VMD, and RST VMD identifiers are represented by `imsm_orom_id_t`.

## NVMe and VMD Support

- `find_imsm_nvme()` provides synthetic IMSM-compatible NVMe capabilities.
- `read_vmd_register()` reads VMD PCI config space, and `add_vmd_orom()` builds VMD capabilities from SKU/version bits.
- `find_imsm_vmd()` provides VMD compatibility capabilities.
- `get_nvme_multipath_dev_hw_path()` resolves virtual NVMe subsystem paths to hardware controller paths.
- `devt_to_devpath()` and `diskfd_to_devpath()` map block devices to sysfs device paths at requested `/device` depth.
- `imsm_is_nvme_namespace_supported()` accepts only the lowest NVMe namespace for IMSM.
- `is_multipath_nvme()` detects namespace exposure through `/sys/devices/virtual/nvme-subsystem/`.

## Attachment Helpers

- `devpath_to_vendor()`, `devpath_to_char()`, and internal `devpath_to_ll()` read sysfs controller attributes.
- `is_path_attached_to_hba()`, `devt_attached_to_hba()`, and `disk_attached_to_hba()` test whether disks are under a controller path.

## Invariants and Risks

- Intel vendor ID `0x8086` gates controller discovery.
- EFI/ACPI/OROM capability discovery is intentionally best-effort and supports environment-variable test overrides.
- VMD and NVMe paths need realpath normalization because sysfs may expose virtual layers or still-enumerating devices.
- OROM data is cached globally by device ID; callers should treat returned pointers as process-lifetime capability records.
