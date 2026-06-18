# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_acpi_sar.c

## Purpose
This file parses MediaTek ACPI SAR and country-list tables for MT792x devices. It reads ACPI methods, validates dynamic/geographic SAR tables, initializes per-frequency power limits, exposes firmware flag bits, and converts MTCL country lists into 5.9 GHz, 6 GHz, and 11be policy configuration.

## Important APIs, Types, And Functions
Exports are `mt792x_init_acpi_sar()`, `mt792x_init_acpi_sar_power()`, `mt792x_acpi_get_flags()`, and `mt792x_acpi_get_mtcl_conf()`. Internal readers handle ACPI methods `MTCL`, `MTDS`, `MTGS`, and `MTFG`. Power helpers include `mt792x_asar_get_geo_pwr()` and `mt792x_asar_range_pwr()`. Country-list parsing uses static all/EU/BE country tables and version-specific MTCL map helpers.

## Control Flow
Initialization allocates `mt792x_acpi_sar`, then tries MTCL, MTDS, optional MTGS, and optional MTFG reads. Each ACPI read evaluates a package method, validates integer elements, and stores byte tables in devm memory. Dynamic and geographic tables are validated against version-specific record sizes and min/max counts. SAR power initialization walks cfg80211 SAR ranges, assigns default ranges when requested, and clamps existing or default power by ACPI dynamic plus geographic limits. MTCL lookup first parses v3 BE policy, then older 6 GHz/5.9 GHz policy, and returns an aggregate config or invalid.

## State And Persistence
Parsed ACPI data persists in `phy->acpisar` for device lifetime. SAR limits are materialized into `phy->mt76->frp[]`. Geographic power depends on `phy->mt76->dev->region`. MTCL config is queried later by MT7925 regulatory code to disable channels or EHT.

## Dependencies And Integration Points
The file integrates Linux ACPI evaluation, cfg80211 SAR capabilities, mt76 frequency-range power storage, MT7925 regulatory CLC handling, and firmware feature flags. It is compiled only under `CONFIG_ACPI`, with stubs in `mt792x.h` otherwise.

## Risks
ACPI package validation is strict but byte-sized; malformed platform tables can disable SAR/CLC features silently after freeing the table. Versioned unions require `asar->ver` to match the populated pointer type. Country table mappings are hard-coded and must track platform firmware definitions. Power clamping assumes SAR capability ranges align with ACPI FRP indices.

## Test Signals
Systems with and without MTCL/MTDS/MTGS/MTFG, versions 1/2/3, all/FCC/ETSI/world regions, cfg80211 SAR user specs, 6 GHz/5.9 GHz country changes, and `mt7925_regd_channel_update()` effects validate the parser.
