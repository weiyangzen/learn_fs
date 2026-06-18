# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/acpi.h

Purpose: Defines Intel Wi-Fi ACPI method names, package sizing constants, DSM constants, feature masks, product-reset structures, and CONFIG_ACPI-dependent prototypes/stubs for firmware runtime ACPI policy loading.

Important APIs and types: Method constants include `WRDS`, `EWRD`, `WGDS`, `WRDD`, `SPLC`, `ECKV`, `PPAG`, `WTAS`, `WPFC`, `GLAI`, `WBEM`, and `DSBR`. Size macros describe SAR, geo, PPAG, TAS, PHY-filter, lock-status, WBEM, and DSBR package layouts by revision. Prototypes expose all `iwl_acpi_get_*()` readers; no-ACPI inline stubs return `-ENOENT`, default power limit zero, or WGDS `1` as appropriate.

Control flow: Header-only flow is compile-time selection between real ACPI implementations and stubs. Callers can use the same API surface regardless of kernel ACPI support.

State and persistence: No direct storage; it defines constants used to fill `struct iwl_fw_runtime` fields in `acpi.c`. Platform policy persists in BIOS/ACPI, not in this header.

Dependencies and integration points: Includes Linux ACPI, firmware regulatory/image headers, and transport declarations. It is shared by iwlwifi firmware runtime, regulatory, MVM/MLD feature setup, and platform reset/control code.

Risks: Package-size macros must match BIOS specifications and the parser's fixed indexing. The no-ACPI return conventions are part of caller behavior and inconsistent returns can change feature defaults. `struct iwl_dsm_internal_product_reset_cmd` is packed and must match DSM payload expectations.

Test signals: Compile with and without `CONFIG_ACPI`, validate all package-size macros against parser loops, exercise caller handling of no-ACPI stubs, and test DSM product-reset payload packing.
