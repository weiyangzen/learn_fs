# sources/distributed-fs/ceph-client/include/linux/soc/brcmstb/brcmstb.h

Purpose: This Broadcom STB header provides helpers for decoding SoC ID registers and optional APIs for retrieving SoC family/product identifiers from the Broadcom STB SoC driver.

Important APIs/types/functions: `BRCM_ID(reg)` extracts the family/product ID using the register format, and `BRCM_REV(reg)` extracts the low 8-bit revision. When `CONFIG_SOC_BRCMSTB` is enabled, `brcmstb_get_family_id` and `brcmstb_get_product_id` are declared; otherwise stub behavior is provided by the remainder of the header.

Control flow: Drivers call the ID helpers or SoC query APIs during probe to gate quirks, compatible behavior, or revision-specific setup.

State and persistence: No state is stored here. The underlying SoC driver owns the cached or hardware-read identifiers.

Dependencies and integration: Includes `linux/kconfig.h` for `IS_ENABLED`. Integrates with Broadcom STB platform drivers, clocks, reset, PM, and peripheral quirks.

Risks and test signals: Mis-decoding IDs can select wrong hardware quirks. Test on old and new register formats, disabled `CONFIG_SOC_BRCMSTB` builds, and drivers that branch on family/product values.
