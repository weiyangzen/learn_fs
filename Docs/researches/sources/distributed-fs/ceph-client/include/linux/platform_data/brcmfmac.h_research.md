# sources/distributed-fs/ceph-client/include/linux/platform_data/brcmfmac.h

Purpose: defines platform-specific configuration for Broadcom/Cypress `brcmfmac` wireless devices, including power hooks, firmware path override, per-device bus settings, country-code translation, and SDIO quirks.

Important APIs and types: `BRCMFMAC_PDATA_NAME` names the platform-data provider and `BRCMFMAC_COUNTRY_BUF_SZ` sizes country strings. `enum brcmf_bus_type` selects SDIO, USB, or PCIE. `struct brcmfmac_sdio_pd` configures SDIO txglom size, drive strength, OOB IRQ support/number/flags, broken scatter-gather alignment constraints, and reset callback. `struct brcmfmac_pd_cc_entry` and flexible-array `struct brcmfmac_pd_cc` translate ISO3166 country codes to firmware country/revision codes. `struct brcmfmac_pd_device` matches device ID/revision/bus type and carries feature-disable flags, country-code table, and bus-specific settings. `struct brcmfmac_platform_data` provides power-on/off callbacks, alternate firmware path, device count, and a flexible array of device entries.

Control flow: a platform data provider must be initialized before brcmfmac's device initcall if built-in. On driver load, brcmfmac looks up platform data by name, calls `power_on()`, matches the probed device against `devices[]`, applies bus quirks/features/country tables, and calls `power_off()` on unload or reset-style teardown.

State and persistence: platform data is static board/device policy. Runtime wireless state includes firmware, regulatory settings, bus state, IRQs, and power state in brcmfmac and hardware. Flexible arrays require the provider allocation to remain valid for the driver's lifetime.

Dependencies and integration points: integrates platform data providers, brcmfmac SDIO/USB/PCIe bus layers, firmware loading, regulatory country-code translation, OOB interrupt setup, SDIO host quirks, and platform power control.

Risks and test signals: risks include provider initcall ordering, silent fallback when pdata is missing, malformed flexible-array allocation, country-code table bounds, invalid OOB IRQ flags, broken SG alignment values, and power/reset callback races. Test built-in and module load ordering, power cycle, SDIO OOB IRQ operation, country-code translation, firmware alternate path, feature-disable masks, suspend/resume, and reset after bus communication failure.
