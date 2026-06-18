# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_fru_eeprom.c

## Purpose
`amdgpu_fru_eeprom.c` detects supported server GPUs with Field Replaceable Unit EEPROM data, reads IPMI FRU Product Info Area records through the common EEPROM helper, stores product identity fields in `adev->fru_info`, and exposes those fields through read-only sysfs files.

## Important APIs, types, and functions
Public functions are `amdgpu_fru_get_product_info()`, `amdgpu_fru_sysfs_init()`, and `amdgpu_fru_sysfs_fini()`. The detection helper is `is_fru_eeprom_supported()`. Sysfs show handlers export `product_name`, `product_number`, `serial_number`, `fru_id`, and `manufacturer`.

## Control flow
Detection rejects SR-IOV VFs and APUs, then switches on MP1 IP version, ASIC type, and VBIOS part-number substrings to decide whether FRU EEPROM is available and which EEPROM memory address to use. Product-info reading allocates `adev->fru_info` when needed, seeds the serial field from `adev->unique_id`, verifies the FRU I2C adapter exists, reads and validates the IPMI common header version and checksum, locates the Product Info Area, reads and validates its header and checksum, then walks type/length fields to copy manufacturer, product name, product number, serial, and optional FRU ID into bounded strings. Sysfs init creates attributes only for supported devices with populated FRU info.

## State and persistence behavior
The persistent source of truth is the external FRU EEPROM. Runtime state is copied into `struct amdgpu_fru_info` attached to `adev`. Sysfs attributes expose that cached runtime copy; the driver does not write FRU data in this file.

## Dependencies and integration points
It depends on PCI/device data, ATOM VBIOS context, PM FRU I2C adapter initialization, SMU I2C support, `amdgpu_eeprom_read()`, AMDGPU IP-version helpers, and sysfs device attributes. It integrates with device initialization and teardown paths that call the product-info and sysfs helpers.

## Risks and edge cases
SKU detection is partly string-based and can miss new server cards or misclassify VBIOS part numbers. Some supported IP versions return `FRU_EEPROM_MADDR_INV`, meaning FRU data is supported but not directly readable. The parser assumes IPMI FRU type/length fields fit inside the validated Product Info Area; it bounds string copies but advances offsets manually. Sysfs show handlers assume `adev->fru_info` remains valid while attributes exist.

## Test signals
Signals include supported and unsupported SKU detection, VF/APU rejection, I2C adapter absence returning `-ENODEV`, common-header and Product Info Area checksum failures, exact-length EEPROM reads, populated sysfs attributes, serial fallback from unique ID, and teardown removing sysfs files.
