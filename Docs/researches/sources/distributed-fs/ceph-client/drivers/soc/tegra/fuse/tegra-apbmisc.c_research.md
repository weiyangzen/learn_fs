# sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/tegra-apbmisc.c

## Purpose

`tegra-apbmisc.c` initializes and exposes Tegra APBMISC and strapping registers used for chip ID, revision, platform type, RAM code, and selected error-response control. It supports early device-tree initialization, legacy ARM hardcoded addresses, and ACPI initialization for newer systems.

## Important APIs, Types, and Functions

Exported/global APIs include `tegra_read_chipid()`, `tegra_get_chip_id()`, `tegra_get_major_rev()`, `tegra_get_minor_rev()`, `tegra_get_platform()`, `tegra_is_silicon()`, `tegra_read_straps()`, `tegra_read_ram_code()`, `tegra194_miscreg_mask_serror()`, `tegra_init_revision()`, `tegra_init_apbmisc()`, and `tegra_acpi_init_apbmisc()`.

Static state includes `apbmisc_base`, `long_ram_code`, `strapping`, and `chipid`. `apbmisc_match` covers Tegra20 APBMISC and Tegra186/194/234/264 misc compatibles.

## Control Flow

`tegra_init_apbmisc()` locates a matching DT node or legacy Tegra ARM addresses, extracts APBMISC and strap resources, maps APBMISC long-term, reads chip ID from offset 4, maps straps briefly, reads strap value, and records whether DT requested a long RAM code mask. `tegra_acpi_init_apbmisc()` finds ACPI HID `NVDA2010`, reads memory resources, and initializes the same cached state.

`tegra_init_revision()` derives `tegra_sku_info.revision` from the APBMISC minor revision, handles Tegra20 A03 prime detection via spare fuses 18/19, reads SKU from fuse offset 0x10, and stores platform.

## State and Persistence Behavior

`chipid`, `strapping`, and `long_ram_code` are boot-lifetime cached hardware values. `apbmisc_base` remains mapped for exported register writes such as `tegra194_miscreg_mask_serror()`. No file-backed persistence exists. `tegra194_miscreg_mask_serror()` writes the ERD config register to mask inband errors on Tegra194 only.

## Dependencies and Integration Points

This file integrates with OF/ACPI resource discovery, Tegra common SoC helpers, public fuse APIs, and users of chip/revision/platform/RAM-code data throughout the Tegra SoC code. The fuse driver calls APBMISC init before revision and speedo binning.

## Risks and Edge Cases

`tegra_init_apbmisc()` calls `of_property_read_bool(np, ...)` after the legacy path where `np` may be NULL; current OF helper behavior tolerates NULL on many kernels, but it is a fragile pattern. Accessors warn if `chipid` is zero but still return cached zero-derived fields. `tegra194_miscreg_mask_serror()` is guarded by machine compatibility and base availability; callers must handle `-EPROBE_DEFER` and `-EOPNOTSUPP`.

## Test Signals

Validate DT and ACPI init, legacy ARM fallback, chip ID/revision/platform decoding, RAM code short and long masks, Tegra20 A03 prime detection, and `tegra194_miscreg_mask_serror()` success/failure on Tegra194 versus other SoCs.
