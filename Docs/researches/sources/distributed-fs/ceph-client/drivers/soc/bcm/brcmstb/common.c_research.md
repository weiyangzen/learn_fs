# sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/common.c

Purpose: common Broadcom STB SoC identification support. It reads family and product IDs from the SUN_TOP control block very early, exports those IDs, and registers a `soc_device` with family, SoC ID, and revision strings.

Important APIs and functions: `brcmstb_get_family_id()` and `brcmstb_get_product_id()` are exported symbols consumed by other Broadcom STB code such as BIU tuning. `brcmstb_soc_device_early_init()` is an `early_initcall` that maps the first SUN_TOP compatible node and reads offsets 0 and 4. `brcmstb_soc_device_init()` is an `arch_initcall` that allocates `struct soc_device_attribute`, formats `family`, `soc_id`, and `revision`, and calls `soc_device_register()`.

Control flow: both init paths are non-fatal on multi-platform kernels. If no matching SUN_TOP node exists, they return success without registering anything. The early path only reads and caches IDs; the arch path creates user-visible SoC metadata in sysfs.

State and persistence: persistent state is limited to static `family_id` and `product_id` globals plus the registered `soc_device`. There is no cleanup path because this is built-in early platform metadata.

Dependencies and integration: requires OF matching against several Broadcom SUN_TOP compatible strings, `of_iomap()`, `soc_device_register()`, and exported Linux SoC bus metadata. It is an integration point for later drivers that need hardware-family conditionals before normal device probing.

Risks and test signals: risk centers on ID format interpretation because the code shifts differently depending on high nibble presence. Allocation failure can return `-ENOMEM`, but strings allocated before a failed register are freed. Test signals include `/sys/devices/soc0` family/soc_id/revision contents, exported ID users taking the intended family branches, and clean boot on non-Broadcom multi-platform kernels.
