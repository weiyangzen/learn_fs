# sources/distributed-fs/ceph-client/drivers/firmware/efi/apple-properties.c

Purpose: imports Apple Mac EFI device properties passed through x86 setup data and attaches them to Linux devices as software nodes, enabling drivers to consume firmware-provided properties such as GPU or Thunderbolt metadata.

Important APIs/types/functions: private wire formats are `struct properties_header` and `struct dev_header`. Main helpers are `map_properties()`, `unmarshal_devices()`, `unmarshal_key_value_pairs()`, and the `dump_apple_properties` boot option handler.

Control flow: `fs_initcall(map_properties)` runs only on `x86_apple_machine`. It walks the `setup_data` chain for `SETUP_APPLE_PROPERTIES`, maps the header and payload, validates version and length, parses each EFI device path with `efi_get_device_by_path()`, allocates `property_entry` arrays, converts UCS-2 property names to UTF-8, and calls `device_create_managed_software_node()`. After processing, it clears payload length and frees the payload memory via memblock while preserving the setup-data chain header.

State and persistence behavior: parsed properties become managed software nodes owned by each device. The original setup payload is freed after import. Optional dump mode emits property names and hex data to the log.

Dependencies and integration points: depends on x86 boot params, Apple platform detection, EFI device path parser, Linux device property API, UCS-2 conversion, memblock, and devices being instantiated by fs initcall time.

Risks and test signals: malformed lengths, unsupported device-path nodes, and missing devices cause property loss for that entry. Key names are heap-allocated and freed after software-node creation, so managed-node copy semantics are essential. Test signals include `dump_apple_properties` logs, successful software node creation on Mac hardware, and driver-visible properties through `device_property_read_*()`.
