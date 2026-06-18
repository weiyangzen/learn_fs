## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/acpi.c

Purpose: ACPI integration for rtw89 regulatory and SAR policy. It evaluates Realtek DSM functions and ACPI methods, validates binary policy signatures, flattens ACPI packages/buffers into driver data, recognizes HP/Realtek SAR table formats, applies geographic SAR deltas, and exposes static/dynamic SAR configuration to the rtw89 regulatory/SAR layer.

Important APIs/functions: `rtw89_acpi_evaluate_dsm()` handles DSM functions including 6 GHz baseline policy, standard-power support, VLP support, TAS, regulatory rules, and integer values. `rtw89_acpi_evaluate_rtag()` reads antenna gain. `rtw89_acpi_sar_get_subband()` and `rtw89_acpi_sar_subband_to_band()` map frequencies/subbands. SAR loaders normalize HP and RT formats, load legacy/6 GHz standard and small tables, apply geo-SAR, and `rtw89_acpi_evaluate_sar()` coordinates static/dynamic SAR recognition and indicator setup. `rtw89_acpi_evaluate_dynamic_sar_indicator()` polls table selection changes.

Control flow: ACPI evaluation first finds a device-root method or DSM object, flattens nested integers/buffers/packages, validates expected type/length/signature, then copies policy buffers. SAR evaluation prefers static SAR, falls back to dynamic SAR, recognizes CID/revision/table length, loads tables into all regulatory domains, optionally applies GEO SAR per regulatory type, initializes 2TX downgrade and indicator fields, then fetches dynamic table selection if needed.

State and persistence: allocates temporary ACPI data/policy copies for callers; fills caller-owned `rtw89_sar_cfg_acpi` tables, valid count, downgrade value, and indicator fields. No global mutable state beyond the Realtek GUID.

Dependencies and integration: depends on Linux ACPI/UUID APIs and rtw89 ACPI/debug/type definitions. It feeds rtw89 SAR, regulatory, TAS, 6 GHz policy, and antenna-gain logic.

Risks and test signals: risks include malformed firmware ACPI objects, divide-by-zero if table count were zero, signature/length mismatch, regulatory mapping gaps, and stale dynamic SAR indicators. Test with systems exposing HP and Realtek SAR variants, ACPI fuzz/malformed methods, 6 GHz policy DSMs, geo regulatory changes, and dynamic SAR polling.
