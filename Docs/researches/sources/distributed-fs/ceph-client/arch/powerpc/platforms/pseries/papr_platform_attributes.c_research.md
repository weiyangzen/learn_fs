# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr_platform_attributes.c

Purpose: Creates `/sys/firmware/papr/energy_scale_info/` entries that expose platform energy and frequency attributes retrieved via `H_GET_ENERGY_SCALE_INFO`.

Important APIs/types/functions: Defines `struct energy_scale_attribute`, `struct h_energy_scale_info_hdr`, `struct papr_attr`, `struct papr_group`, `papr_get_attr()`, sysfs show functions for `desc`, `value`, `value_desc`, `add_attr_group()`, and init function `papr_init()`.

Control flow: Init checks LPAR and energy-scale firmware features, allocates a hcall buffer, retries with larger buffers when firmware reports partial/too-small results, validates header offsets and attribute count, creates the `papr/energy_scale_info` kobjects, and creates one sysfs group per firmware attribute id. Each sysfs read performs a fresh single-attribute hcall because values can change dynamically.

State and persistence: Keeps global kobjects and an array of `papr_group` objects containing sysfs attributes and group names. Attribute values are not cached; firmware is queried on every read.

Dependencies and integration points: Depends on PAPR hypercall wrappers, `firmware_kobj`, pseries initcalls, sysfs/kobject APIs, and firmware feature bits `FW_FEATURE_LPAR` and `FW_FEATURE_ENERGY_SCALE_INFO`.

Risks: Buffer growth arithmetic and returned `array_offset/num_attrs` validation protect against firmware overrun. Cleanup paths must free partially allocated names and attrs. Current allocation growth uses `ESI_HDR_SIZE + (CURR_MAX_ESI_ATTRS * max_esi_attrs)`, which scales in chunks but deserves review because `max_esi_attrs` already begins as an attribute count.

Test signals: Boot on systems with and without energy-scale support, read all sysfs attributes, simulate partial-buffer hcall responses, attributes with empty `value_desc`, invalid firmware offsets, and init failure injection for kobject/sysfs allocation cleanup.

Source read size: 363 lines, 10214 bytes.
